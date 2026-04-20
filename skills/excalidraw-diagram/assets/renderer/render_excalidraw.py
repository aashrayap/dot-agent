"""Render Excalidraw JSON to PNG using a local bundled Excalidraw export.

The browser page is intentionally offline-only. Any HTTP(S) request made during
render is treated as a renderer bug and fails the command.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate_excalidraw(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("type") != "excalidraw":
        errors.append(f"Expected type 'excalidraw', got '{data.get('type')}'")

    if "elements" not in data:
        errors.append("Missing 'elements' array")
    elif not isinstance(data["elements"], list):
        errors.append("'elements' must be an array")
    elif not data["elements"]:
        errors.append("'elements' array is empty; nothing to render")

    return errors


def compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]:
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for element in elements:
        if element.get("isDeleted"):
            continue
        x = element.get("x", 0)
        y = element.get("y", 0)
        width = element.get("width", 0)
        height = element.get("height", 0)

        if element.get("type") in {"arrow", "line"} and "points" in element:
            for point_x, point_y in element["points"]:
                min_x = min(min_x, x + point_x)
                min_y = min(min_y, y + point_y)
                max_x = max(max_x, x + point_x)
                max_y = max(max_y, y + point_y)
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + abs(width))
            max_y = max(max_y, y + abs(height))

    if min_x == float("inf"):
        return (0, 0, 800, 600)

    return (min_x, min_y, max_x, max_y)


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: int = 2,
    max_width: int = 1920,
) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run the skill wrapper so uv can install renderer deps.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(excalidraw_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"ERROR: Invalid JSON in {excalidraw_path}: {error}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print("ERROR: Invalid Excalidraw file:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    elements = [element for element in data["elements"] if not element.get("isDeleted")]
    min_x, min_y, max_x, max_y = compute_bounding_box(elements)
    padding = 80
    diagram_width = max_x - min_x + padding * 2
    diagram_height = max_y - min_y + padding * 2
    viewport_width = min(int(diagram_width), max_width)
    viewport_height = max(int(diagram_height), 600)

    if output_path is None:
        output_path = excalidraw_path.with_suffix(".png")

    renderer_dir = Path(__file__).parent
    template_path = renderer_dir / "render_template.html"
    bundle_path = renderer_dir / "dist" / "excalidraw-export.bundle.js"
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    if not bundle_path.exists():
        print(f"ERROR: Local Excalidraw bundle not found: {bundle_path}", file=sys.stderr)
        print("Run: skills/excalidraw-diagram/scripts/build-renderer-bundle.sh", file=sys.stderr)
        sys.exit(1)

    blocked_requests: list[str] = []
    page_errors: list[str] = []

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as error:
            if "Executable doesn't exist" in str(error) or "browserType.launch" in str(error):
                print("ERROR: Chromium not installed for Playwright. Run the skill wrapper once with network access.", file=sys.stderr)
                sys.exit(1)
            raise

        page = browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=scale,
        )

        def route_request(route, request):
            if request.url.startswith(("http://", "https://")):
                blocked_requests.append(request.url)
                route.abort()
                return
            route.continue_()

        page.route("**/*", route_request)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(template_path.as_uri(), wait_until="domcontentloaded", timeout=15000)

        if blocked_requests:
            browser.close()
            print("ERROR: Renderer attempted network access:", file=sys.stderr)
            for url in blocked_requests:
                print(f"  - {url}", file=sys.stderr)
            sys.exit(1)

        try:
            page.wait_for_function("window.__moduleReady === true", timeout=15000)
        except Exception:
            browser.close()
            if page_errors:
                print("ERROR: Renderer page failed before module ready:", file=sys.stderr)
                for error in page_errors:
                    print(f"  - {error}", file=sys.stderr)
            else:
                print("ERROR: Local Excalidraw bundle did not become ready.", file=sys.stderr)
            sys.exit(1)

        result = page.evaluate("jsonData => window.renderDiagram(jsonData)", data)
        if not result or not result.get("success"):
            browser.close()
            error_message = result.get("error", "Unknown render error") if result else "renderDiagram returned null"
            print(f"ERROR: Render failed: {error_message}", file=sys.stderr)
            sys.exit(1)

        page.wait_for_function("window.__renderComplete === true", timeout=15000)
        svg_element = page.query_selector("#root svg")
        if svg_element is None:
            browser.close()
            print("ERROR: No SVG element found after render.", file=sys.stderr)
            sys.exit(1)

        svg_element.screenshot(path=str(output_path))
        browser.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Excalidraw JSON to PNG")
    parser.add_argument("input", type=Path, help="Path to .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output PNG path")
    parser.add_argument("--scale", "-s", type=int, default=2, help="Device scale factor")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Max viewport width")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    png_path = render(args.input, args.output, args.scale, args.width)
    print(str(png_path))


if __name__ == "__main__":
    main()
