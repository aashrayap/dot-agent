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
  red: "#ffe3e3",
  redStroke: "#b42318",
  gray: "#eef2f7",
  grayStroke: "#64748b",
  violet: "#eee7ff",
  violetStroke: "#6d4aff",
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
  let remaining = line.trim();
  while (remaining.length > maxChars) {
    let cut = remaining.lastIndexOf(" ", maxChars);
    if (cut < Math.floor(maxChars * 0.55)) {
      cut = maxChars;
    }
    parts.push(remaining.slice(0, cut).trim());
    remaining = remaining.slice(cut).trim();
  }
  if (remaining) {
    parts.push(remaining);
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

function text(x, y, width, body, opts = {}) {
  const fontSize = opts.fontSize ?? 20;
  const lineHeight = opts.lineHeight ?? 1.45;
  const maxChars = opts.wrapAt ?? Math.max(8, Math.floor(width / (fontSize * 0.62)));
  const renderedBody = opts.wrap === false ? String(body) : wrapBody(body, maxChars);
  const lines = renderedBody.split("\n").length;
  const computedHeight = Math.ceil(fontSize * lineHeight * lines + 22);
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
    startArrowhead: null,
    endArrowhead: opts.endArrowhead ?? "arrow",
  };
}

function panel(elements, x, y, width, height, title, subtitle) {
  elements.push(rect(x, y, width, height, {
    strokeColor: colors.panelStroke,
    backgroundColor: colors.panel,
  }));
  elements.push(text(x + 24, y + 22, width - 48, title, {
    fontSize: 24,
    color: colors.ink,
    height: 58,
  }));
  if (subtitle) {
    elements.push(text(x + 24, y + 68, width - 48, subtitle, {
      fontSize: 15,
      color: colors.muted,
      height: 52,
    }));
  }
}

function skill(elements, x, y, width, height, label, opts = {}) {
  const fill = opts.fill ?? colors.blue;
  const stroke = opts.stroke ?? colors.blueStroke;
  elements.push(rect(x, y, width, height, {
    strokeColor: stroke,
    backgroundColor: fill,
    strokeWidth: opts.strokeWidth ?? 2,
  }));
  elements.push(text(x + 12, y + 13, width - 24, label, {
    fontSize: opts.fontSize ?? 18,
    color: opts.color ?? "#0b3954",
    align: opts.align ?? "center",
    height: opts.textHeight ?? height - 14,
    wrap: false,
  }));
}

function pill(elements, x, y, label, opts = {}) {
  const width = opts.width ?? Math.max(150, label.length * 10 + 36);
  skill(elements, x, y, width, 48, label, {
    fill: opts.fill ?? colors.green,
    stroke: opts.stroke ?? colors.greenStroke,
    fontSize: opts.fontSize ?? 16,
    color: opts.color ?? colors.ink,
    textHeight: 36,
  });
  return width;
}

function legend(elements, x, y) {
  pill(elements, x, y, "keep", { width: 92, fill: colors.green, stroke: colors.greenStroke });
  pill(elements, x + 112, y, "reroute", { width: 118, fill: colors.amber, stroke: colors.amberStroke });
  pill(elements, x + 252, y, "cut", { width: 78, fill: colors.red, stroke: colors.redStroke });
}

function doc(elements, width, height) {
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

function header(elements, title, subtitle, width = 1920) {
  elements.push(text(70, 42, width - 140, title, {
    fontSize: 36,
    color: colors.ink,
    height: 70,
  }));
  elements.push(text(72, 102, width - 144, subtitle, {
    fontSize: 18,
    color: colors.muted,
    height: 64,
  }));
}

function pruneMap() {
  counter = 1;
  const e = [];
  header(
    e,
    "dot-agent skill workflow prune map",
    "Old projects-centered workflow compared with the current roadmap-centered target. The roster below covers every source skill.",
    1980,
  );
  legend(e, 1550, 54);

  panel(e, 70, 155, 870, 470, "Old published workflow", "The existing README diagram makes projects the durable hub.");
  skill(e, 120, 280, 180, 76, "morning-sync\nfocus", { fill: colors.blue, stroke: colors.blueStroke });
  arrow(305, 318, 378, 318);
  skill(e, 380, 270, 210, 96, "projects", { fill: colors.red, stroke: colors.redStroke, color: "#7a1f16", fontSize: 24 });
  arrow(595, 318, 668, 318);
  skill(e, 670, 280, 200, 76, "spec-new-feature\nreview", { fill: colors.blue, stroke: colors.blueStroke });
  skill(e, 220, 405, 180, 76, "idea\ninit-epic", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  arrow(402, 430, 470, 365);
  skill(e, 575, 405, 230, 76, "execution-review\nclosure blended", { fill: colors.amber, stroke: colors.amberStroke, color: colors.ink, fontSize: 16 });
  arrow(620, 403, 545, 366);
  e.push(text(120, 525, 740, "Old risk: project files, session IDs, and closure duties become a hidden service layer.", {
    fontSize: 18,
    color: colors.muted,
    height: 86,
  }));

  panel(e, 1010, 155, 900, 470, "Current target workflow", "Human closure sits on roadmap.md; forensics and build work stay composable.");
  skill(e, 1345, 280, 230, 88, "state/collab/\nroadmap.md", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink, fontSize: 18 });
  skill(e, 1070, 250, 180, 70, "morning-sync", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(1254, 286, 1340, 304, { strokeColor: colors.greenStroke });
  skill(e, 1070, 350, 180, 70, "focus", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(1254, 386, 1340, 340, { strokeColor: colors.greenStroke });
  skill(e, 1660, 300, 180, 70, "daily-review", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(1580, 326, 1655, 326, { strokeColor: colors.greenStroke });
  skill(e, 1065, 480, 185, 70, "idea\ninit-epic", { fill: colors.amber, stroke: colors.amberStroke, color: colors.ink, fontSize: 17 });
  arrow(1255, 515, 1350, 515, { strokeColor: colors.amberStroke });
  skill(e, 1355, 480, 220, 70, "spec-new-feature", { fill: colors.blue, stroke: colors.blueStroke, color: colors.ink });
  arrow(1580, 515, 1660, 515, { strokeColor: colors.blueStroke });
  skill(e, 1665, 480, 175, 70, "review", { fill: colors.blue, stroke: colors.blueStroke, color: colors.ink });
  skill(e, 1395, 400, 220, 58, "execution-review", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink, fontSize: 16 });
  arrow(1618, 427, 1660, 353, { strokeColor: colors.violetStroke });
  e.push(text(1070, 565, 760, "Target rule: no normal-path reads from projects/* and no preserved session-ID layer.", {
    fontSize: 18,
    color: colors.muted,
    height: 74,
  }));

  panel(e, 70, 675, 1840, 650, "Skill disposition", "Keep the composable capabilities; cut the stale project-state architecture.");

  e.push(text(110, 775, 390, "Daily human loop", { fontSize: 22, color: colors.greenStroke, height: 52 }));
  pill(e, 110, 835, "morning-sync", { width: 180 });
  pill(e, 305, 835, "focus", { width: 110 });
  pill(e, 430, 835, "daily-review", { width: 170 });
  e.push(text(110, 905, 510, "Owns attention, row edits, and end-of-day closure on roadmap.md.", {
    fontSize: 16,
    color: colors.muted,
    height: 90,
  }));

  e.push(text(690, 775, 420, "Planning and delivery", { fontSize: 22, color: colors.blueStroke, height: 52 }));
  pill(e, 690, 835, "idea", { width: 95, fill: colors.amber, stroke: colors.amberStroke });
  pill(e, 805, 835, "init-epic", { width: 140, fill: colors.amber, stroke: colors.amberStroke });
  pill(e, 965, 835, "spec-new-feature", { width: 230, fill: colors.blue, stroke: colors.blueStroke });
  pill(e, 1215, 835, "review", { width: 115, fill: colors.blue, stroke: colors.blueStroke });
  e.push(text(690, 905, 650, "Keep these skills. Remove project handoffs and route durable execution back to roadmap rows, specs, PRs, and handoff docs.", {
    fontSize: 16,
    color: colors.muted,
    height: 100,
  }));

  e.push(text(110, 1040, 460, "Forensics and comparison", { fontSize: 22, color: colors.violetStroke, height: 52 }));
  pill(e, 110, 1100, "execution-review", { width: 230, fill: colors.violet, stroke: colors.violetStroke });
  pill(e, 360, 1100, "compare", { width: 130, fill: colors.violet, stroke: colors.violetStroke });
  e.push(text(110, 1170, 510, "Keep. execution-review investigates runtime behavior and can recommend daily-review, but it should not close the day itself.", {
    fontSize: 16,
    color: colors.muted,
    height: 110,
  }));

  e.push(text(690, 1040, 480, "Docs, knowledge, visuals", { fontSize: 22, color: colors.grayStroke, height: 52 }));
  pill(e, 690, 1100, "wiki", { width: 88, fill: colors.gray, stroke: colors.grayStroke });
  pill(e, 795, 1100, "create-agents-md", { width: 230, fill: colors.gray, stroke: colors.grayStroke });
  pill(e, 1045, 1100, "explain", { width: 130, fill: colors.gray, stroke: colors.grayStroke });
  pill(e, 1195, 1100, "excalidraw-diagram", { width: 265, fill: colors.gray, stroke: colors.grayStroke });
  e.push(text(690, 1170, 760, "Keep. These produce reusable docs, diagrams, and queryable knowledge without owning project state.", {
    fontSize: 16,
    color: colors.muted,
    height: 94,
  }));

  e.push(rect(1510, 770, 340, 485, {
    strokeColor: colors.redStroke,
    backgroundColor: "#fff8f8",
    strokeWidth: 3,
  }));
  e.push(text(1535, 800, 290, "Cut or retire", { fontSize: 24, color: colors.redStroke, height: 56 }));
  skill(e, 1535, 865, 285, 72, "projects", { fill: colors.red, stroke: colors.redStroke, color: "#7a1f16", fontSize: 24 });
  skill(e, 1535, 955, 285, 72, "improve-agent-md", { fill: colors.red, stroke: colors.redStroke, color: "#7a1f16", fontSize: 20 });
  e.push(text(1535, 1050, 290, "Also remove project helper surfaces:\n- state/projects setup\n- focus-promote.py path\n- projects-setup.sh calls\n- complete-session.py / update-execution.py", {
    fontSize: 15,
    color: colors.ink,
    height: 160,
  }));

  e.push(text(110, 1285, 1690, "Recommendation: split daily-review helper work from projects teardown. Teardown should remove source/runtime install, setup state creation, helper calls, and doc routing together.", {
    fontSize: 18,
    color: colors.ink,
    height: 68,
  }));

  return doc(e, 1980, 1390);
}

function drilldowns() {
  counter = 1;
  const e = [];
  header(
    e,
    "current high-level composable workflows",
    "A deeper view of the live workflows after removing the projects hub.",
    2000,
  );

  panel(e, 70, 155, 900, 560, "1. Human daily loop", "Default operating loop for what Ash should see, change, and close.");
  skill(e, 120, 285, 190, 72, "morning-sync", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(315, 321, 410, 321, { strokeColor: colors.greenStroke });
  skill(e, 415, 270, 215, 102, "roadmap.md\nhuman rows", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(635, 321, 730, 321, { strokeColor: colors.greenStroke });
  skill(e, 735, 285, 180, 72, "focus", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(825, 365, 825, 455, { strokeColor: colors.greenStroke });
  skill(e, 690, 460, 240, 78, "daily-review\nrecap + drain", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(688, 500, 535, 500, { strokeColor: colors.greenStroke });
  skill(e, 290, 460, 235, 78, "dated recap\nroadmap update", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  e.push(text(120, 585, 760, "Normal path: read and mutate state/collab/roadmap.md only. Ask the human on ambiguous closure. Do not inspect project files.", {
    fontSize: 17,
    color: colors.muted,
    height: 96,
  }));

  panel(e, 1030, 155, 900, 560, "2. Planning and delivery", "Execution planning remains durable, but the durable artifact is no longer projects/*.");
  skill(e, 1085, 270, 165, 72, "idea", { fill: colors.amber, stroke: colors.amberStroke, color: colors.ink });
  arrow(1255, 306, 1340, 306, { strokeColor: colors.amberStroke });
  skill(e, 1345, 270, 245, 72, "spec-new-feature", { fill: colors.blue, stroke: colors.blueStroke, color: colors.ink });
  arrow(1595, 306, 1690, 306, { strokeColor: colors.blueStroke });
  skill(e, 1695, 270, 165, 72, "review", { fill: colors.blue, stroke: colors.blueStroke, color: colors.ink });
  skill(e, 1085, 420, 190, 78, "init-epic\nmulti-repo", { fill: colors.amber, stroke: colors.amberStroke, color: colors.ink });
  arrow(1280, 458, 1345, 342, { strokeColor: colors.amberStroke });
  skill(e, 1395, 420, 245, 78, "handoff docs\nPR context", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  arrow(1645, 458, 1710, 342, { strokeColor: colors.grayStroke });
  skill(e, 1085, 565, 310, 74, "remove: project promotion", { fill: colors.red, stroke: colors.redStroke, color: "#7a1f16" });
  e.push(text(1425, 560, 410, "Keep idea, init-epic, spec-new-feature, and review. Reroute references that say \"promote to projects\".", {
    fontSize: 17,
    color: colors.muted,
    height: 116,
  }));

  panel(e, 70, 765, 900, 560, "3. Forensics and comparison", "Used when the question is what actually happened, not what to close.");
  skill(e, 120, 880, 225, 76, "runtime logs\ntranscripts", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  arrow(350, 918, 445, 918, { strokeColor: colors.violetStroke });
  skill(e, 450, 880, 245, 76, "execution-review", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink });
  arrow(700, 918, 790, 918, { strokeColor: colors.violetStroke });
  skill(e, 795, 880, 125, 76, "report", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink });
  skill(e, 120, 1035, 170, 72, "compare", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink });
  skill(e, 330, 1035, 170, 72, "review", { fill: colors.blue, stroke: colors.blueStroke, color: colors.ink });
  skill(e, 540, 1035, 275, 72, "optional handoff:\ndaily-review", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink, fontSize: 17 });
  arrow(697, 958, 660, 1030, { strokeColor: colors.greenStroke });
  e.push(text(120, 1155, 750, "Boundary: execution-review writes findings and recommendations. It does not drain roadmap rows or write the daily recap.", {
    fontSize: 17,
    color: colors.muted,
    height: 96,
  }));

  panel(e, 1030, 765, 900, 560, "4. Knowledge, docs, and visual reasoning", "Reusable support skills that should remain independent of daily closure.");
  skill(e, 1085, 880, 150, 70, "wiki", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  arrow(1240, 915, 1330, 915, { strokeColor: colors.grayStroke });
  skill(e, 1335, 880, 240, 70, "queryable\nknowledge", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  skill(e, 1615, 880, 220, 70, "create-agents-md", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink, fontSize: 17 });
  skill(e, 1085, 1035, 160, 72, "explain", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink });
  arrow(1250, 1070, 1350, 1070, { strokeColor: colors.grayStroke });
  skill(e, 1355, 1035, 260, 72, "excalidraw-diagram", { fill: colors.gray, stroke: colors.grayStroke, color: colors.ink, fontSize: 17 });
  skill(e, 1645, 1035, 185, 72, "compare", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink });
  e.push(text(1085, 1155, 745, "These skills can feed specs, handoffs, or reviews. None should become a hidden project-state owner.", {
    fontSize: 17,
    color: colors.muted,
    height: 96,
  }));

  return doc(e, 2000, 1390);
}

function dailyVsExecution() {
  counter = 1;
  const e = [];
  header(
    e,
    "daily-review vs execution-review",
    "Keep both skills. The obsolete part is the old blend between human closure and forensic investigation.",
    1720,
  );

  panel(e, 70, 165, 720, 780, "daily-review", "Human day-end closure.");
  panel(e, 930, 165, 720, 780, "execution-review", "Runtime and delivery forensics.");

  const leftRows = [
    ["Question", "What changed today, and what can be closed?"],
    ["Reads", "state/collab/roadmap.md in normal path"],
    ["Writes", "dated recap and roadmap row drain"],
    ["Authority", "human closure and next-day continuity"],
    ["When stuck", "ask the human before closing ambiguous rows"],
    ["Must not", "score sessions or sweep logs as a default"],
  ];
  const rightRows = [
    ["Question", "What actually happened in an agent session or PR?"],
    ["Reads", "Codex/Claude logs, transcripts, PRs, diffs, evidence"],
    ["Writes", "forensic report, review history, recommendations"],
    ["Authority", "behavioral evidence and delivery risk"],
    ["When stuck", "state evidence gaps and residual risk"],
    ["Must not", "mutate roadmap rows or write daily recaps"],
  ];

  function rows(x, y, rows, accent) {
    rows.forEach(([label, body], index) => {
      const top = y + index * 104;
      e.push(rect(x, top, 620, 82, {
        strokeColor: accent,
        backgroundColor: index % 2 === 0 ? "#ffffff" : "#f8fafc",
        strokeWidth: 1,
      }));
      e.push(text(x + 18, top + 15, 150, label, {
        fontSize: 18,
        color: accent,
        height: 52,
      }));
      e.push(text(x + 180, top + 13, 410, body, {
        fontSize: 17,
        color: colors.ink,
        height: 60,
      }));
    });
  }

  rows(120, 295, leftRows, colors.greenStroke);
  rows(980, 295, rightRows, colors.violetStroke);

  e.push(rect(430, 990, 860, 140, {
    strokeColor: colors.amberStroke,
    backgroundColor: colors.amber,
    strokeWidth: 3,
  }));
  e.push(text(460, 1018, 800, "Allowed bridge", {
    fontSize: 24,
    color: colors.amberStroke,
    height: 50,
  }));
  e.push(text(460, 1060, 800, "execution-review may recommend a daily-review closure pass. daily-review may cite a forensic report when the user asks for that evidence.", {
    fontSize: 18,
    color: colors.ink,
    height: 62,
  }));

  skill(e, 225, 1215, 210, 70, "daily-review", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  arrow(440, 1250, 700, 1250, { strokeColor: colors.greenStroke });
  skill(e, 705, 1215, 300, 70, "roadmap.md + recap", { fill: colors.green, stroke: colors.greenStroke, color: colors.ink });
  skill(e, 1105, 1215, 260, 70, "execution-review", { fill: colors.violet, stroke: colors.violetStroke, color: colors.ink });
  arrow(1265, 1210, 1160, 1138, { strokeColor: colors.amberStroke });
  e.push(text(230, 1315, 1260, "Cut target: the projects-era assumption that a session/project service layer should coordinate both closure and forensics.", {
    fontSize: 18,
    color: colors.muted,
    height: 70,
  }));

  return doc(e, 1720, 1410);
}

const outputs = {
  "skill-workflow-prune-map.excalidraw": pruneMap(),
  "skill-workflow-drilldowns.excalidraw": drilldowns(),
  "daily-vs-execution-review.excalidraw": dailyVsExecution(),
};

for (const [name, data] of Object.entries(outputs)) {
  const fullPath = path.join(outDir, name);
  fs.writeFileSync(fullPath, `${JSON.stringify(data, null, 2)}\n`);
  console.log(fullPath);
}
