#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve("docs/diagrams");
fs.mkdirSync(outDir, { recursive: true });

let counter = 1;

const colors = {
  ink: "#17324d",
  muted: "#475569",
  line: "#64748b",
  panel: "#ffffff",
  panelStroke: "#cbd5e1",
  blue: "#dff3ff",
  blueStroke: "#0b5a7a",
  green: "#e6f6ea",
  greenStroke: "#2f6f3e",
  amber: "#fff2cc",
  amberStroke: "#9a6700",
  violet: "#eee7ff",
  violetStroke: "#6d4aff",
  gray: "#eef2f7",
  grayStroke: "#64748b",
  teal: "#dff7f3",
  tealStroke: "#0f766e",
};

function id(prefix) {
  return `${prefix}_${counter++}`;
}

function base(type, x, y, width, height, opts = {}) {
  return {
    id: id(type),
    type,
    x,
    y,
    width,
    height,
    angle: 0,
    strokeColor: opts.strokeColor ?? colors.ink,
    backgroundColor: opts.backgroundColor ?? "transparent",
    fillStyle: "solid",
    strokeWidth: opts.strokeWidth ?? 2,
    strokeStyle: "solid",
    roughness: 0,
    opacity: 100,
    seed: 1000 + counter * 37,
    version: 1,
    versionNonce: 2000 + counter * 101,
    isDeleted: false,
    groupIds: [],
    boundElements: null,
    link: null,
    locked: false,
  };
}

function wrapLine(line, maxChars) {
  if (line.length <= maxChars) {
    return [line];
  }
  const parts = [];
  let rest = line.trim();
  while (rest.length > maxChars) {
    let cut = rest.lastIndexOf(" ", maxChars);
    if (cut < Math.floor(maxChars * 0.55)) {
      cut = maxChars;
    }
    parts.push(rest.slice(0, cut).trim());
    rest = rest.slice(cut).trim();
  }
  if (rest) {
    parts.push(rest);
  }
  return parts;
}

function wrapBody(body, maxChars) {
  return String(body)
    .split("\n")
    .flatMap((line) => wrapLine(line, maxChars))
    .join("\n");
}

function rect(x, y, width, height, opts = {}) {
  return {
    ...base("rectangle", x, y, width, height, opts),
    roundness: { type: 3 },
  };
}

function diamond(x, y, width, height, opts = {}) {
  return {
    ...base("diamond", x, y, width, height, opts),
    roundness: { type: 2 },
  };
}

function text(x, y, width, body, opts = {}) {
  const fontSize = opts.fontSize ?? 20;
  const lineHeight = opts.lineHeight ?? 1.35;
  const maxChars = opts.wrapAt ?? Math.max(8, Math.floor(width / (fontSize * 0.62)));
  const renderedBody = opts.wrap === false ? String(body) : wrapBody(body, maxChars);
  const lines = renderedBody.split("\n").length;
  const computedHeight = Math.ceil(fontSize * lineHeight * lines + 20);
  return {
    ...base("text", x, y, width, Math.max(opts.height ?? 0, computedHeight), {
      strokeColor: opts.color ?? colors.ink,
      strokeWidth: 1,
    }),
    text: renderedBody,
    originalText: renderedBody,
    fontSize,
    fontFamily: opts.fontFamily ?? 3,
    textAlign: opts.align ?? "left",
    verticalAlign: "top",
    containerId: null,
    lineHeight,
  };
}

function arrow(x1, y1, x2, y2, opts = {}) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  return {
    ...base("line", x1, y1, Math.abs(dx), Math.abs(dy), {
      strokeColor: opts.strokeColor ?? colors.line,
      strokeWidth: opts.strokeWidth ?? 2,
    }),
    points: [
      [0, 0],
      [dx, dy],
    ],
    startBinding: null,
    endBinding: null,
    startArrowhead: opts.startArrowhead ?? null,
    endArrowhead: opts.endArrowhead ?? "arrow",
  };
}

function panel(elements, x, y, width, height, title, subtitle) {
  elements.push(rect(x, y, width, height, {
    strokeColor: colors.panelStroke,
    backgroundColor: colors.panel,
  }));
  elements.push(text(x + 24, y + 20, width - 48, title, {
    fontSize: 25,
    color: colors.ink,
    height: 52,
  }));
  if (subtitle) {
    elements.push(text(x + 24, y + 64, width - 48, subtitle, {
      fontSize: 15,
      color: colors.muted,
      height: 50,
    }));
  }
}

function node(elements, x, y, width, height, label, opts = {}) {
  elements.push(rect(x, y, width, height, {
    strokeColor: opts.stroke ?? colors.blueStroke,
    backgroundColor: opts.fill ?? colors.blue,
    strokeWidth: opts.strokeWidth ?? 2,
  }));
  elements.push(text(x + 12, y + 12, width - 24, label, {
    fontSize: opts.fontSize ?? 17,
    color: opts.color ?? colors.ink,
    align: opts.align ?? "center",
    height: height - 8,
    wrap: opts.wrap ?? true,
    wrapAt: opts.wrapAt,
  }));
}

function lane(elements, x, y, width, height, title, body, opts = {}) {
  elements.push(rect(x, y, width, height, {
    strokeColor: opts.stroke ?? colors.grayStroke,
    backgroundColor: opts.fill ?? "#ffffff",
    strokeWidth: 2,
  }));
  elements.push(text(x + 18, y + 15, 265, title, {
    fontSize: 20,
    color: opts.stroke ?? colors.ink,
    height: 68,
  }));
  elements.push(text(x + 18, y + 86, 250, body, {
    fontSize: 14,
    color: colors.muted,
    height: height - 90,
  }));
}

function badge(elements, x, y, label, opts = {}) {
  const width = opts.width ?? Math.max(120, label.length * 9 + 32);
  node(elements, x, y, width, 42, label, {
    fill: opts.fill ?? colors.gray,
    stroke: opts.stroke ?? colors.grayStroke,
    fontSize: opts.fontSize ?? 14,
    wrap: false,
  });
  return width;
}

function doc(elements) {
  return {
    type: "excalidraw",
    version: 2,
    source: "https://excalidraw.com",
    elements,
    appState: {
      gridSize: null,
      viewBackgroundColor: "#f8fafc",
      currentItemFontFamily: 3,
      exportBackground: true,
    },
    files: {},
  };
}

function header(elements) {
  elements.push(text(70, 42, 1600, "dot-agent skills: current setup and workflows", {
    fontSize: 38,
    color: colors.ink,
    height: 70,
  }));
  elements.push(text(72, 104, 1540, "~/.dot-agent/skills is source of truth. setup.sh installs selected skill payloads into Claude and Codex. Workflows compose through explicit owners and handoffs.", {
    fontSize: 18,
    color: colors.muted,
    height: 58,
  }));
  badge(elements, 1760, 58, "current state", {
    width: 185,
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
}

function installPipeline(elements) {
  panel(
    elements,
    70,
    160,
    2060,
    325,
    "1. Runtime install path",
    "Tracked source stays in ~/.dot-agent. Runtime homes are outputs, not sources of truth.",
  );

  node(elements, 120, 295, 270, 92, "skills/<name>/\nSKILL.md + skill.toml", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 17,
    wrap: false,
  });
  node(elements, 460, 290, 280, 102, "skill.toml\nname, targets,\nentrypoints", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 16,
    wrap: false,
  });
  elements.push(arrow(394, 341, 455, 341, { strokeColor: colors.amberStroke }));

  elements.push(diamond(825, 285, 170, 115, {
    fill: colors.teal,
    stroke: colors.tealStroke,
  }));
  elements.push(text(848, 323, 122, "setup.sh", {
    fontSize: 21,
    color: colors.ink,
    align: "center",
    height: 48,
    wrap: false,
  }));
  elements.push(arrow(742, 341, 820, 341, { strokeColor: colors.tealStroke }));

  node(elements, 1090, 258, 320, 92, "~/.claude/skills/\nsymlink selected entrypoint\n+ shared dirs", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 1090, 372, 320, 60, "claude/ config symlinked", {
    fill: "#ffffff",
    stroke: colors.greenStroke,
    fontSize: 14,
  });
  elements.push(arrow(1000, 322, 1085, 304, { strokeColor: colors.greenStroke }));

  node(elements, 1510, 258, 330, 92, "~/.codex/skills/\ncopied payload\nrerun setup after edits", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 1510, 372, 330, 60, "AGENTS.md + codex/ config/rules", {
    fill: "#ffffff",
    stroke: colors.blueStroke,
    fontSize: 14,
  });
  elements.push(arrow(1000, 365, 1505, 304, { strokeColor: colors.blueStroke }));

  node(elements, 1880, 288, 200, 112, "state/\nlocal memory,\nbackups, caches", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
    wrap: false,
  });
  elements.push(arrow(995, 360, 1875, 344, { strokeColor: colors.violetStroke }));

  elements.push(text(120, 420, 850, "Installed shared dirs: scripts/ assets/ references/ shared/. Thin runtime wrappers are allowed; shared behavior stays at skill root.", {
    fontSize: 15,
    color: colors.muted,
    height: 44,
  }));
}

function authoringContract(elements) {
  panel(
    elements,
    70,
    525,
    580,
    600,
    "2. Authoring contract",
    "Every retained skill declares ownership and install shape.",
  );

  node(elements, 115, 650, 215, 72, "SKILL.md", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 22,
  });
  node(elements, 380, 650, 215, 72, "skill.toml", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 22,
  });
  elements.push(arrow(333, 686, 375, 686, { strokeColor: colors.amberStroke }));

  node(elements, 115, 780, 480, 86, "## Composes With\nParent / Children / Reads / Writes / Handoffs", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
    wrap: false,
  });
  elements.push(arrow(355, 725, 355, 775, { strokeColor: colors.greenStroke }));

  node(elements, 115, 925, 220, 78, "root workflow\nshared behavior", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 17,
    wrap: false,
  });
  node(elements, 375, 925, 220, 78, "thin runtime\nwrappers only", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 17,
    wrap: false,
  });
  elements.push(arrow(338, 964, 370, 964, { strokeColor: colors.blueStroke }));

  elements.push(text(115, 1038, 480, "Helpers and durable support live in scripts/, references/, assets/, and shared/. Generated state and caches stay out of tracked source.", {
    fontSize: 15,
    color: colors.muted,
    height: 70,
  }));
}

function workflows(elements) {
  panel(
    elements,
    700,
    525,
    1430,
    850,
    "3. High-level workflows",
    "One owner per surface; handoffs keep daily work, planning, delivery, forensics, docs, and visuals separate.",
  );

  lane(elements, 750, 650, 1325, 150, "Daily human loop", "Day-start, board edits, closure.", {
    fill: "#f7fff8",
    stroke: colors.greenStroke,
  });
  node(elements, 1040, 680, 165, 62, "morning-sync", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 16,
  });
  node(elements, 1265, 666, 220, 90, "state/collab/\nroadmap.md", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
    wrap: false,
  });
  node(elements, 1545, 680, 120, 62, "focus", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
  node(elements, 1725, 680, 165, 62, "daily-review", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 16,
  });
  node(elements, 1928, 670, 110, 82, "dated\nrecap", {
    fill: "#ffffff",
    stroke: colors.greenStroke,
    fontSize: 15,
    wrap: false,
  });
  elements.push(arrow(1210, 711, 1260, 711, { strokeColor: colors.greenStroke }));
  elements.push(arrow(1490, 711, 1540, 711, { strokeColor: colors.greenStroke, startArrowhead: "arrow" }));
  elements.push(arrow(1670, 711, 1720, 711, { strokeColor: colors.greenStroke }));
  elements.push(arrow(1895, 711, 1923, 711, { strokeColor: colors.greenStroke }));

  lane(elements, 750, 835, 1325, 150, "Idea to PR", "Incubate, bootstrap, plan, ship.", {
    fill: "#fffdf5",
    stroke: colors.amberStroke,
  });
  node(elements, 1040, 865, 115, 62, "idea", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(elements, 1210, 855, 150, 82, "init-epic\nif multi-repo", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 1420, 865, 215, 62, "spec-new-feature", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
  });
  node(elements, 1695, 865, 125, 62, "review", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 17,
  });
  node(elements, 1880, 855, 155, 82, "PR / focus /\nhandoff", {
    fill: "#ffffff",
    stroke: colors.blueStroke,
    fontSize: 15,
    wrap: false,
  });
  elements.push(arrow(1160, 896, 1205, 896, { strokeColor: colors.amberStroke }));
  elements.push(arrow(1365, 896, 1415, 896, { strokeColor: colors.blueStroke }));
  elements.push(arrow(1640, 896, 1690, 896, { strokeColor: colors.blueStroke }));
  elements.push(arrow(1825, 896, 1875, 896, { strokeColor: colors.blueStroke }));

  lane(elements, 750, 1020, 1325, 150, "Review and external gates", "Local diff checks, portable packets, and evidence loops.", {
    fill: "#fbf9ff",
    stroke: colors.violetStroke,
  });
  node(elements, 1010, 1048, 150, 66, "git diff\nPR context", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 1210, 1048, 125, 66, "review", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 17,
  });
  node(elements, 1385, 1038, 235, 86, "handoff-\nresearch-pro", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
    wrap: false,
  });
  node(elements, 1670, 1048, 150, 66, "external\nreviewer", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 1870, 1038, 170, 86, "findings\nintake", {
    fill: "#ffffff",
    stroke: colors.violetStroke,
    fontSize: 14,
    wrap: false,
  });
  elements.push(arrow(1165, 1081, 1205, 1081, { strokeColor: colors.blueStroke }));
  elements.push(arrow(1340, 1081, 1380, 1081, { strokeColor: colors.violetStroke }));
  elements.push(arrow(1625, 1081, 1665, 1081, { strokeColor: colors.violetStroke }));
  elements.push(arrow(1825, 1081, 1865, 1081, { strokeColor: colors.violetStroke }));

  lane(elements, 750, 1205, 1325, 150, "Docs, knowledge, visuals", "Reusable human-facing artifacts.", {
    fill: "#f8fbff",
    stroke: colors.grayStroke,
  });
  node(elements, 1040, 1235, 105, 62, "wiki", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 17,
  });
  node(elements, 1195, 1235, 205, 62, "create-agents-md", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 15,
  });
  node(elements, 1450, 1235, 115, 62, "explain", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 16,
  });
  node(elements, 1615, 1235, 125, 62, "compare", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
  });
  node(elements, 1790, 1225, 245, 82, "excalidraw-diagram\nPNG + source", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 15,
    wrap: false,
  });
  elements.push(arrow(1568, 1266, 1610, 1266, { strokeColor: colors.violetStroke }));
  elements.push(arrow(1745, 1266, 1785, 1266, { strokeColor: colors.tealStroke }));

  elements.push(text(760, 1335, 1250, "Boundary: normal daily output uses roadmap rows, not session IDs or hidden project state. Deep implementation uses docs/artifacts/<feature>/; external critique writes docs/handoffs/<slug>-research-pro-review.md.", {
    fontSize: 15,
    color: colors.muted,
    height: 40,
  }));
}

function researchProGate() {
  counter = 1;
  const elements = [];

  elements.push(text(70, 42, 1500, "Research Pro review gate", {
    fontSize: 34,
    color: colors.ink,
    height: 64,
  }));
  elements.push(text(72, 100, 1450, "Use a portable packet as a selective external critique gate around expensive-to-unwind decisions.", {
    fontSize: 16,
    color: colors.muted,
    height: 56,
  }));

  panel(
    elements,
    70,
    180,
    500,
    420,
    "1. Entry gates",
    "Run only when outside synthesis can change a decision.",
  );
  node(elements, 125, 335, 145, 62, "idea", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(elements, 330, 325, 165, 82, "spec-new-\nfeature", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
    wrap: false,
  });
  node(elements, 225, 460, 170, 82, "pre-merge\nrisk", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
    wrap: false,
  });

  panel(
    elements,
    650,
    180,
    560,
    420,
    "2. Packet contract",
    "The handoff is the product; strong review depends on strong packaging.",
  );
  node(elements, 700, 325, 190, 74, "target +\nmode", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
    wrap: false,
  });
  node(elements, 970, 325, 190, 74, "source +\naccess policy", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 700, 455, 190, 74, "assumptions\n+ blind spots", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
    wrap: false,
  });
  node(elements, 970, 455, 190, 74, "validation +\nknown gaps", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 15,
    wrap: false,
  });

  panel(
    elements,
    1290,
    180,
    520,
    420,
    "3. Findings loop",
    "External review returns findings that local work must triage.",
  );
  node(elements, 1340, 330, 190, 82, "ChatGPT\nResearch Pro", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 17,
    wrap: false,
  });
  node(elements, 1600, 330, 155, 82, "findings\nfirst", {
    fill: "#ffffff",
    stroke: colors.violetStroke,
    fontSize: 16,
    wrap: false,
  });
  node(elements, 1435, 460, 290, 74, "fix now / backlog /\nverify / reject", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 15,
    wrap: false,
  });

  elements.push(arrow(575, 390, 645, 390, { strokeColor: colors.amberStroke }));
  elements.push(arrow(1215, 390, 1285, 390, { strokeColor: colors.violetStroke }));
  elements.push(arrow(1535, 371, 1595, 371, { strokeColor: colors.violetStroke }));
  elements.push(arrow(1678, 415, 1590, 455, { strokeColor: colors.greenStroke }));

  elements.push(text(90, 650, 1580, "Thesis: use the highest-scrutiny surface where independent falsification matters. Local agents still own repo-grounded execution, tests, and accepted fixes.", {
    fontSize: 16,
    color: colors.ink,
    height: 56,
  }));

  return doc(elements);
}

function runtimeRoster(elements) {
  panel(
    elements,
    70,
    1420,
    2060,
    330,
    "4. Runtime targets today",
    "skill.toml decides whether a skill installs into Claude, Codex, or both.",
  );

  elements.push(text(120, 1532, 210, "Claude + Codex", {
    fontSize: 22,
    color: colors.blueStroke,
    height: 46,
  }));
  const dual = [
    "wiki",
    "idea",
    "init-epic",
    "spec-new-feature",
    "review",
    "execution-review",
    "compare",
    "explain",
    "create-agents-md",
    "excalidraw-diagram",
    "handoff-research-pro",
  ];
  let x = 360;
  let y = 1516;
  for (const item of dual) {
    const width = badge(elements, x, y, item, {
      fill: colors.blue,
      stroke: colors.blueStroke,
      fontSize: 13,
    });
    x += width + 14;
    if (x > 1880) {
      x = 360;
      y += 54;
    }
  }

  elements.push(text(120, 1665, 210, "Codex only", {
    fontSize: 22,
    color: colors.greenStroke,
    height: 46,
  }));
  x = 360;
  for (const item of ["morning-sync", "focus", "daily-review", "caveman"]) {
    const width = badge(elements, x, 1655, item, {
      fill: colors.green,
      stroke: colors.greenStroke,
      fontSize: 13,
    });
    x += width + 14;
  }
}

function render() {
  counter = 1;
  const elements = [];
  header(elements);
  installPipeline(elements);
  authoringContract(elements);
  workflows(elements);
  runtimeRoster(elements);
  return doc(elements);
}

const fullPath = path.join(outDir, "skills-current-state-workflows.excalidraw");
fs.writeFileSync(fullPath, `${JSON.stringify(render(), null, 2)}\n`);
console.log(fullPath);

const researchProPath = path.join(outDir, "research-pro-review-gate.excalidraw");
fs.writeFileSync(researchProPath, `${JSON.stringify(researchProGate(), null, 2)}\n`);
console.log(researchProPath);
