#!/usr/bin/env python3
from __future__ import annotations

from typing import Any


def _clamp(score: int) -> int:
    return max(1, min(5, score))


def _ratio(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return num / den


def _all_feedback(payload: dict[str, Any]) -> tuple[int, int]:
    total_feedback = 0
    followups = 0
    for session in payload.get("sessions") or []:
        fit = session.get("response_fit") or {}
        followups += int(fit.get("followup_user_messages") or 0)
        feedback = fit.get("feedback_signals") or {}
        total_feedback += sum(int(v or 0) for v in feedback.values())
    return total_feedback, followups


TACTICAL_TERMS = (
    ".dot-agent",
    "execution-review",
    "focus",
    "spec-new-feature",
    "skill",
    "skills",
    "workflow",
    "harness",
    "hermes",
    "agent",
    "agents",
)

DISPOSABLE_TERMS = (
    "config",
    "settings",
    "plugin",
    "auth",
    "install",
    "setup",
    "model",
    "gateway",
    "release",
    "runtime",
    "permission",
    "oauth",
    "token",
)


SOURCE_ARTIFACT_EXTS = (
    ".excalidraw",
    ".drawio",
    ".mmd",
    ".mermaid",
    ".plantuml",
    ".puml",
    ".dot",
    ".gv",
)

HUMAN_READABLE_ARTIFACT_EXTS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".pdf",
)


def artifact_contract_risk_sessions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for session in payload.get("sessions") or []:
        text = str(session.get("final_response_excerpt") or "").lower()
        source_exts = sorted({ext for ext in SOURCE_ARTIFACT_EXTS if ext in text})
        readable_exts = sorted({ext for ext in HUMAN_READABLE_ARTIFACT_EXTS if ext in text})
        if not source_exts or not readable_exts:
            continue

        risk = dict(session)
        risk["artifact_contract_risk"] = {
            "source_exts": source_exts,
            "readable_exts": readable_exts,
            "reason": "final response mentions editable/source and human-readable artifact extensions together",
        }
        risks.append(risk)
    return risks


def classify_session_layer(session: dict[str, Any]) -> tuple[str, str]:
    text = " ".join(
        str(value or "")
        for value in (
            session.get("cwd"),
            session.get("label"),
            session.get("first_user_message"),
            session.get("final_response_excerpt"),
        )
    ).lower()

    if any(term in text for term in TACTICAL_TERMS):
        return "tactical", "Harness/workflow/skill work that should accelerate domain work."
    if any(term in text for term in DISPOSABLE_TERMS):
        return "disposable", "Runtime/tool-specific work that may be replaced by upstream releases."
    return "strategic", "Domain/project work likely to compound via data, judgment, or decision loops."


def build_layer_allocation(payload: dict[str, Any]) -> dict[str, Any]:
    buckets: dict[str, dict[str, Any]] = {
        "strategic": {"sessions": 0, "wall_seconds": 0, "examples": []},
        "tactical": {"sessions": 0, "wall_seconds": 0, "examples": []},
        "disposable": {"sessions": 0, "wall_seconds": 0, "examples": []},
    }
    for session in payload.get("sessions") or []:
        layer, reason = classify_session_layer(session)
        bucket = buckets[layer]
        bucket["sessions"] += 1
        bucket["wall_seconds"] += int(session.get("wall_seconds") or 0)
        if len(bucket["examples"]) < 3:
            bucket["examples"].append(
                {
                    "runtime": session.get("runtime"),
                    "session_id": session.get("session_id"),
                    "label": session.get("label"),
                    "reason": reason,
                }
            )

    total_wall = sum(int(bucket["wall_seconds"]) for bucket in buckets.values())
    for bucket in buckets.values():
        bucket["wall_ratio"] = round((bucket["wall_seconds"] / total_wall), 3) if total_wall else 0
    return buckets


def score_review_payload(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    summary = payload.get("summary") or {}
    sessions = payload.get("sessions") or []
    session_count = int(summary.get("sessions") or 0)
    unique_cwds = int(summary.get("unique_cwds") or 0)
    context_switches = int(summary.get("context_switches") or 0)
    edits = int(summary.get("edits") or 0)
    verifications = int(summary.get("verifications") or 0)
    failures = int(summary.get("exec_failures") or 0)
    subagents = int(summary.get("subagent_count") or 0)
    total_feedback, followups = _all_feedback(payload)
    artifact_risks = artifact_contract_risk_sessions(payload)

    edit_sessions = [s for s in sessions if int(s.get("edits") or 0) > 0]
    grounded_edit_sessions = [
        s for s in edit_sessions if int(((s.get("tool_calls") or {}).get("read") or 0)) > 0
    ]
    verified_edit_sessions = [
        s for s in edit_sessions if int(s.get("verifications") or 0) > 0
    ]
    skill_sessions = [
        s
        for s in sessions
        if sum(int(v or 0) for v in (s.get("skill_mentions") or {}).values()) > 0
    ]
    workflow_tool_sessions = [
        s
        for s in sessions
        if any(
            key in (s.get("tool_counts") or {})
            for key in {"TaskCreate", "TaskUpdate", "ToolSearch", "update_plan", "spawn_agent", "Agent"}
        )
    ]
    low_progress_sessions = [
        s
        for s in sessions
        if int(s.get("edits") or 0) == 0
        and int(s.get("verifications") or 0) == 0
        and int(s.get("exec_failures") or 0) == 0
        and (
            int(((s.get("tool_calls") or {}).get("read") or 0))
            + int(((s.get("tool_calls") or {}).get("search") or 0))
            + int(((s.get("tool_calls") or {}).get("exec") or 0))
        ) >= 8
    ]

    # Focus
    focus = 5
    if unique_cwds >= 4:
        focus -= 1
    if context_switches >= max(4, session_count - 1):
        focus -= 2
    elif context_switches >= 3:
        focus -= 1
    if session_count >= 6 and unique_cwds >= 5:
        focus -= 1
    focus = _clamp(focus)

    # Grounding
    if not edit_sessions:
        grounding = 3 if session_count > 0 else 1
    else:
        ratio = _ratio(len(grounded_edit_sessions), len(edit_sessions))
        if ratio >= 0.9:
            grounding = 5
        elif ratio >= 0.7:
            grounding = 4
        elif ratio >= 0.4:
            grounding = 3
        elif ratio >= 0.2:
            grounding = 2
        else:
            grounding = 1

    # Verification
    if not edit_sessions:
        verification = 3 if session_count > 0 else 1
    else:
        ratio = _ratio(len(verified_edit_sessions), len(edit_sessions))
        if ratio >= 0.95:
            verification = 5
        elif ratio >= 0.75:
            verification = 4
        elif ratio >= 0.5:
            verification = 3
        elif ratio >= 0.25:
            verification = 2
        else:
            verification = 1

    # Response fit
    response_fit = 5
    if total_feedback >= 1:
        response_fit -= 1
    if total_feedback >= 3:
        response_fit -= 1
    if total_feedback >= 6:
        response_fit -= 1
    if artifact_risks:
        response_fit -= 1
    if session_count and _ratio(followups, session_count) > 2.5:
        response_fit -= 1
    response_fit = _clamp(response_fit)

    # Skill leverage
    skill_leverage = 3
    if skill_sessions or workflow_tool_sessions:
        skill_leverage += 1
    if len(skill_sessions) >= 2:
        skill_leverage += 1
    if not skill_sessions and not workflow_tool_sessions and session_count >= 4:
        skill_leverage -= 1
    if total_feedback >= 3 and not skill_sessions:
        skill_leverage -= 1
    skill_leverage = _clamp(skill_leverage)

    # Workflow efficiency
    efficiency = 4
    if failures >= 1:
        efficiency -= 1
    if failures >= 3:
        efficiency -= 1
    if total_feedback >= 3:
        efficiency -= 1
    if len(low_progress_sessions) >= max(2, session_count // 2 if session_count else 0):
        efficiency -= 1
    if subagents >= 5 and failures == 0 and total_feedback == 0:
        efficiency += 1
    efficiency = _clamp(efficiency)

    return {
        "focus": {
            "score": focus,
            "why": f"{context_switches} context switches across {session_count} sessions and {unique_cwds} cwd(s).",
        },
        "grounding": {
            "score": grounding,
            "why": (
                f"{len(grounded_edit_sessions)} of {len(edit_sessions)} edit sessions showed explicit read/explore activity "
                f"before or alongside change work."
                if edit_sessions
                else "No edit sessions in window, so grounding is neutral rather than strongly positive or negative."
            ),
        },
        "verification": {
            "score": verification,
            "why": (
                f"{len(verified_edit_sessions)} of {len(edit_sessions)} edit sessions included verification-like commands."
                if edit_sessions
                else "No edit sessions in window, so verification is neutral."
            ),
        },
        "response_fit": {
            "score": response_fit,
            "why": (
                f"{total_feedback} response-fit feedback signals, {followups} total follow-up user messages, "
                f"and {len(artifact_risks)} possible artifact-contract risk(s) were detected."
            ),
        },
        "skill_leverage": {
            "score": skill_leverage,
            "why": f"{len(skill_sessions)} sessions referenced explicit skills; {len(workflow_tool_sessions)} sessions used workflow/planning helper tools.",
        },
        "workflow_efficiency": {
            "score": efficiency,
            "why": f"{failures} execution failures, {len(low_progress_sessions)} high-churn low-progress sessions, and {subagents} subagent events were recorded.",
        },
    }


def recommendations_from_scores(scores: dict[str, dict[str, Any]]) -> list[str]:
    recs: list[str] = []
    if scores["focus"]["score"] <= 2:
        recs.append("Batch work by repo/workstream and reduce avoidable cross-project switching in the same review window.")
    if scores["grounding"]["score"] <= 3:
        recs.append("Front-load contract reading before edits and capture the expected invariants explicitly in the session.")
    if scores["verification"]["score"] <= 3:
        recs.append("Require a verification pass after every edit-bearing session and treat missing checks as an explicit risk.")
    if scores["response_fit"]["score"] <= 3:
        recs.append("Tighten response-shape discipline: match requested format early, and treat correction/redo prompts as a signal to simplify output.")
    if scores["skill_leverage"]["score"] <= 3:
        recs.append("Invoke existing skills or workflow helpers earlier instead of recreating process from scratch in-session.")
    if scores["workflow_efficiency"]["score"] <= 3:
        recs.append("Separate deep implementation work from coordination/research loops to reduce long shallow churn.")
    return recs[:3]


def recommendations_from_layer_allocation(layer_allocation: dict[str, Any]) -> list[str]:
    recs: list[str] = []
    strategic_ratio = float(layer_allocation.get("strategic", {}).get("wall_ratio") or 0)
    tactical_ratio = float(layer_allocation.get("tactical", {}).get("wall_ratio") or 0)
    disposable_ratio = float(layer_allocation.get("disposable", {}).get("wall_ratio") or 0)
    if strategic_ratio < 0.5 and (tactical_ratio + disposable_ratio) >= 0.5:
        recs.append("Rebalance toward strategic domain work: tactical harness work is useful only when it accelerates domain compounding.")
    if disposable_ratio >= 0.25:
        recs.append("Cap disposable runtime/tool-tuning work unless it unblocks a strategic or tactical bottleneck.")
    if tactical_ratio >= 0.5:
        recs.append("Convert repeated tactical harness work into deterministic helpers so agent attention returns to judgment and domain decisions.")
    return recs
