#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const outDir = path.resolve("docs/diagrams");
fs.mkdirSync(outDir, { recursive: true });

let n = 1;
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
  rose: "#ffe4e6",
  roseStroke: "#be123c",
  teal: "#dff7f3",
  tealStroke: "#0f766e",
};

function id(type) {
  return `${type}_${n++}`;
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
    seed: 1000 + n * 31,
    version: 1,
    versionNonce: 2000 + n * 89,
    isDeleted: false,
    groupIds: [],
    boundElements: null,
    link: null,
    locked: false,
  };
}

function wrapLine(line, maxChars) {
  if (line.length <= maxChars) return [line];
  const lines = [];
  let rest = line.trim();
  while (rest.length > maxChars) {
    let cut = rest.lastIndexOf(" ", maxChars);
    if (cut < maxChars * 0.55) cut = maxChars;
    lines.push(rest.slice(0, cut).trim());
    rest = rest.slice(cut).trim();
  }
  if (rest) lines.push(rest);
  return lines;
}

function wrap(text, maxChars) {
  return String(text)
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

function text(x, y, width, body, opts = {}) {
  const fontSize = opts.fontSize ?? 18;
  const lineHeight = opts.lineHeight ?? 1.32;
  const chars = opts.wrapAt ?? Math.max(8, Math.floor(width / (fontSize * 0.62)));
  const rendered = opts.wrap === false ? String(body) : wrap(body, chars);
  const lines = rendered.split("\n").length;
  return {
    ...base("text", x, y, width, opts.height ?? Math.ceil(fontSize * lineHeight * lines + 16), {
      strokeColor: opts.color ?? colors.ink,
      strokeWidth: 1,
    }),
    text: rendered,
    originalText: rendered,
    fontSize,
    fontFamily: opts.fontFamily ?? 3,
    textAlign: opts.align ?? "left",
    verticalAlign: "top",
    containerId: null,
    lineHeight,
  };
}

function arrow(x1, y1, x2, y2, opts = {}) {
  return {
    ...base("line", x1, y1, x2 - x1, y2 - y1, {
      strokeColor: opts.strokeColor ?? colors.line,
      strokeWidth: opts.strokeWidth ?? 2,
    }),
    points: [
      [0, 0],
      [x2 - x1, y2 - y1],
    ],
    startBinding: null,
    endBinding: null,
    startArrowhead: opts.startArrowhead ?? null,
    endArrowhead: opts.endArrowhead ?? "arrow",
  };
}

function panel(elements, x, y, width, height, title, subtitle = "") {
  elements.push(rect(x, y, width, height, {
    strokeColor: colors.panelStroke,
    backgroundColor: colors.panel,
  }));
  elements.push(text(x + 24, y + 20, width - 48, title, {
    fontSize: 26,
    height: 42,
    wrap: false,
  }));
  if (subtitle) {
    elements.push(text(x + 24, y + 64, width - 48, subtitle, {
      fontSize: 15,
      color: colors.muted,
      height: 46,
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
    align: opts.align ?? "center",
    height: height - 8,
    wrapAt: opts.wrapAt,
    color: opts.color ?? colors.ink,
  }));
}

function label(elements, x, y, body, opts = {}) {
  elements.push(text(x, y, opts.width ?? 220, body, {
    fontSize: opts.fontSize ?? 14,
    color: opts.color ?? colors.muted,
    height: opts.height,
    wrapAt: opts.wrapAt,
  }));
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

function write(name, elements) {
  fs.writeFileSync(
    path.join(outDir, `${name}.excalidraw`),
    `${JSON.stringify(doc(elements), null, 2)}\n`,
  );
}

function sourceRuntimeDiagram() {
  const e = [];
  panel(e, 20, 20, 1540, 760, "Harness Source And Runtime Ownership", ".dot-agent remains source; setup creates runtime consumers and deterministic checks.");

  node(e, 80, 150, 330, 410, ".dot-agent\nsource repo\n\nAGENTS.md\ncodex/\nclaude/\nskills/\ndocs/\nscripts/", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 20,
  });
  node(e, 560, 190, 270, 120, "setup.sh\ninstall + audit", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 21,
  });
  node(e, 560, 390, 270, 120, "validators\nskill drift\nrepo drift\nschema/context", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 18,
  });
  node(e, 980, 140, 250, 160, "~/.codex\nruntime consumer\n\nAGENTS/config/hooks symlink\nrules + skills copied", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
  node(e, 980, 395, 250, 145, "~/.claude\nruntime consumer\n\nCLAUDE/settings\nstatusline symlink\nskills symlinked", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 17,
  });
  node(e, 1270, 255, 240, 145, "Debug-only\nruntime edits\nnot durable source", {
    fill: colors.rose,
    stroke: colors.roseStroke,
    fontSize: 17,
  });

  e.push(arrow(410, 355, 560, 250));
  e.push(arrow(410, 355, 560, 450));
  e.push(arrow(830, 250, 980, 220));
  e.push(arrow(830, 450, 980, 465));
  e.push(arrow(1230, 220, 1290, 295, { strokeColor: colors.roseStroke }));
  e.push(arrow(1230, 465, 1290, 360, { strokeColor: colors.roseStroke }));

  label(e, 470, 315, "tracked source feeds setup", { width: 190 });
  label(e, 840, 285, "Codex symlink root/config/hooks; sync rules/skills", { width: 230 });
  label(e, 840, 535, "Claude mostly symlinks", { width: 190 });
  label(e, 1270, 430, "do not make runtime a second source", { width: 240 });
  return e;
}

function skillSchemaDiagram() {
  const e = [];
  panel(e, 20, 20, 1540, 850, "Skill Schema And Agent Routing", "Portable SKILL.md stays readable; skill.toml and generated SKILL_INDEX keep composition auditable.");

  node(e, 80, 150, 300, 190, "SKILL.md\n\nfrontmatter:\nname + description\n\nbody:\nworkflow + judgment", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 18,
  });
  node(e, 80, 410, 300, 180, "skill.toml\n\nschema_version = 1\ncomposition graph\ninputs / outputs\nstate + dependencies", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(e, 80, 625, 300, 120, "agents/openai.yaml\noptional UI, policy,\nand MCP/tool deps", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 15,
  });

  node(e, 525, 180, 300, 130, "Codex startup\nloads metadata only\nname, description, path,\noptional OpenAI metadata", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
  node(e, 525, 420, 300, 135, "Skill activation\nloads SKILL.md\nthen refs/scripts/assets\nas needed", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
  node(e, 525, 640, 300, 115, "Local validator\nchecks 20/20 manifests\nTOML + Markdown\nindex freshness", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
  });

  node(e, 970, 135, 250, 135, "references/\nshared contracts\noutput packet\nsubagent delegation\nroadmap ownership", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 16,
  });
  node(e, 970, 330, 250, 135, "scripts/\ndeterministic helpers\ncontext audit\nmanifest validation\nskill index generation", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 14,
  });
  node(e, 970, 525, 250, 135, "assets/\ntemplates\ndiagram sources\nstatic examples", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 16,
  });
  node(e, 1290, 325, 190, 160, "Result\nless drift\nrouting index\nsame semantics\ngrill gate\nmore checks", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
  });

  e.push(arrow(380, 245, 525, 245));
  e.push(arrow(380, 500, 525, 690));
  e.push(arrow(380, 685, 525, 245));
  e.push(arrow(825, 475, 970, 200));
  e.push(arrow(825, 490, 970, 395));
  e.push(arrow(825, 505, 970, 590));
  e.push(arrow(1220, 395, 1290, 405));
  label(e, 410, 165, "portable runtime contract", { width: 160 });
  label(e, 395, 600, "local machine-checkable harness contract", { width: 220 });
  return e;
}

function iterationLoopDiagram() {
  const e = [];
  panel(e, 20, 20, 1540, 760, "Bloat, Measure, Prune, Iterate", "Keep the best primitives, delete or archive the rest, then let the next experiment cycle happen.");

  node(e, 100, 250, 240, 120, "Experiment\nadd workflows\ntry prompts\nexpand skills", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 18,
  });
  node(e, 450, 160, 245, 120, "Measure\ncontext audit\nword counts\nduplicate anchors", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(e, 810, 250, 245, 120, "Keep best\nschema\nreferences\nscripts\npatterns", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 18,
  });
  node(e, 450, 460, 245, 150, "Prune\nlookup\ndelete\narchive meaningful", {
    fill: colors.rose,
    stroke: colors.roseStroke,
    fontSize: 17,
  });
  node(e, 1160, 250, 250, 120, "Verify\nsetup audit\nmanifest lint\ncontext audit\ndiff check", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 18,
  });

  node(e, 160, 575, 270, 95, "Reasoning stays in orchestrator\nonly for synthesis and tradeoffs", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 16,
  });
  node(e, 760, 575, 290, 95, "Deterministic work moves to\nscripts, validators, and narrow subagents", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 16,
  });

  e.push(arrow(340, 280, 450, 220));
  e.push(arrow(695, 220, 810, 280));
  e.push(arrow(1055, 310, 1160, 310));
  e.push(arrow(1185, 370, 695, 520));
  e.push(arrow(450, 520, 340, 330));
  e.push(arrow(1290, 250, 1290, 110));
  e.push(arrow(1290, 110, 190, 110));
  e.push(arrow(190, 110, 190, 250));

  label(e, 365, 188, "current reality", { width: 190 });
  label(e, 710, 255, "promote durable pieces", { width: 160 });
  label(e, 1080, 255, "prove no drift", { width: 130 });
  label(e, 725, 490, "remove leaks", { width: 120 });
  label(e, 1285, 75, "next bloat cycle is intentional", { width: 260 });
  return e;
}

function runtimeArchitectureDiagram() {
  const e = [];
  panel(e, 20, 20, 1760, 920, "dot-agent Harness Layers", "Tracked source, runtime installs, local state, and audits stay separate. Codex is preferred; Claude remains portable.");

  node(e, 80, 140, 295, 170, "Layer 1\nagent contract\n\nAGENTS.md\nREADME.md\nruntime docs", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 18,
  });
  node(e, 80, 350, 295, 170, "Layer 2\nskill source\n\nskills/*\nSKILL.md\nskill.toml", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 18,
  });
  node(e, 80, 570, 295, 170, "Layer 3\ndocs + helpers\n\ndocs/\nscripts/\nsetup.sh", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 18,
  });

  node(e, 495, 145, 305, 145, "agent skill choice\nruntime metadata first\nSKILL_INDEX fallback only", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(e, 495, 365, 305, 155, "setup.sh materializes\nClaude symlinks\nCodex copies + symlinks\nbacks up conflicts", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 18,
  });
  node(e, 495, 605, 305, 145, "tracked repo is source\nruntime homes are outputs\nstate is gitignored", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 17,
  });

  node(e, 920, 135, 305, 175, "Codex runtime\npreferred daily path\n\nAGENTS/config/hooks symlinked\nrules copied\nskills copied", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 17,
  });
  node(e, 920, 375, 305, 175, "Claude runtime\nportable second path\n\nCLAUDE/settings/statusline symlinked\nskills symlinked", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 17,
  });
  node(e, 920, 625, 305, 145, "Local state\nroadmap\nideas\nreviews\nbackups/tool caches", {
    fill: colors.gray,
    stroke: colors.grayStroke,
    fontSize: 17,
  });

  node(e, 1350, 135, 315, 150, "instruction drift audit\nsetup --check-instructions\ninstalled payloads\nrepo contracts", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 17,
  });
  node(e, 1350, 355, 315, 150, "manifest + index gates\nvalidate-skill-manifests\ngenerate-skill-index --check\n20 skill.toml entries", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
  });
  node(e, 1350, 575, 315, 150, "context-surface audit\nword counts\nduplicate anchors\nschema coverage\nruntime shape", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 16,
  });
  node(e, 1350, 785, 315, 90, "check failures\nfix source\nrerun setup/audits", {
    fill: "#ffffff",
    stroke: colors.violetStroke,
    fontSize: 16,
  });

  e.push(arrow(375, 225, 490, 217));
  e.push(arrow(375, 430, 490, 432));
  e.push(arrow(375, 655, 490, 678));
  e.push(arrow(800, 217, 915, 222));
  e.push(arrow(800, 442, 915, 462));
  e.push(arrow(800, 678, 915, 698));
  e.push(arrow(1225, 222, 1345, 210));
  e.push(arrow(1225, 462, 1345, 430));
  e.push(arrow(1225, 698, 1345, 650));
  e.push(arrow(1508, 728, 1508, 780));
  return e;
}

function skillsWorkflowDiagram() {
  const e = [];
  panel(e, 20, 20, 1540, 860, "Skill Workflow Map After Schema Reset", "Owner skills stay small; helper skills add checkpoints, language, diagrams, and verification.");

  node(e, 70, 150, 220, 120, "Daily loop\nmorning-sync", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
  });
  node(e, 350, 135, 220, 135, "focus\nroadmap control", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 14,
    wrapAt: 20,
  });
  node(e, 630, 135, 220, 135, "idea\nconcept shaping", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 14,
    wrapAt: 20,
  });
  node(e, 910, 135, 250, 135, "spec-new-feature\nplan + tasks", {
    fill: colors.green,
    stroke: colors.greenStroke,
    fontSize: 14,
    wrapAt: 22,
  });

  node(e, 965, 345, 230, 125, "grill-me\npressure test\nno owned artifacts", {
    fill: colors.amber,
    stroke: colors.amberStroke,
    fontSize: 15,
  });
  node(e, 1245, 160, 240, 130, "ubiquitous-language\nrepo terms", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 13,
    wrapAt: 22,
  });
  node(e, 1245, 380, 240, 120, "excalidraw-diagram\nvisual receipts", {
    fill: colors.teal,
    stroke: colors.tealStroke,
    fontSize: 14,
    wrapAt: 22,
  });

  node(e, 350, 610, 220, 120, "daily-review\nclosure + drainage", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
  });
  node(e, 630, 610, 220, 120, "review\nPR / branch risk", {
    fill: colors.blue,
    stroke: colors.blueStroke,
    fontSize: 16,
  });
  node(e, 910, 610, 250, 120, "context-surface-audit\nword counts\nschema coverage", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
  });
  node(e, 70, 610, 220, 120, "skill.toml schema v1\n20/20 manifests\nvalidator gate", {
    fill: colors.violet,
    stroke: colors.violetStroke,
    fontSize: 15,
  });

  e.push(arrow(290, 210, 350, 202));
  e.push(arrow(570, 202, 630, 202));
  e.push(arrow(850, 202, 910, 202));
  e.push(arrow(1035, 270, 1035, 345));
  e.push(arrow(1160, 200, 1245, 220));
  e.push(arrow(1160, 225, 1245, 430));
  e.push(arrow(1035, 470, 740, 610));
  e.push(arrow(1035, 470, 460, 610));
  e.push(arrow(180, 610, 350, 270));
  e.push(arrow(1035, 610, 1035, 470));

  return e;
}

write("harness-reduction-source-runtime", sourceRuntimeDiagram());
write("harness-reduction-skill-schema", skillSchemaDiagram());
write("harness-reduction-iteration-loop", iterationLoopDiagram());
// dot-agent-runtime-architecture is now maintained directly as an Excalidraw
// source under docs/diagrams after external diagram review. Do not regenerate it
// here unless that manual source is ported back into this generator.
// skills-current-state-workflows is owned by
// docs/artifacts/skills-readme-current-state-diagram/generate-diagram.mjs.
