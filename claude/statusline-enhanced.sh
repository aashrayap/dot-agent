#!/bin/bash
# Claude Code Statusline — minimal: Model | Project | Context %

input=$(cat)

# Colors
C_RESET="\033[0m"
C_PURPLE="\033[35m"
C_GREEN="\033[32m"
C_BLUE="\033[34m"
C_CYAN="\033[36m"
C_YELLOW="\033[33m"
C_RED="\033[31m"
C_DIM="\033[2m"

# Extract values
MODEL_ID=$(echo "$input" | jq -r '.model.id // ""')
MODEL_NAME=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
CURRENT_DIR=$(echo "$input" | jq -r '.workspace.current_dir // ""')

# Model short name + color
MODEL_COLOR=$C_CYAN
if [[ "$MODEL_ID" == *"opus"* ]]; then
    MODEL_COLOR=$C_PURPLE; MODEL_SHORT="OPS"
elif [[ "$MODEL_ID" == *"sonnet"* ]]; then
    MODEL_COLOR=$C_GREEN; MODEL_SHORT="SNT"
elif [[ "$MODEL_ID" == *"haiku"* ]]; then
    MODEL_COLOR=$C_BLUE; MODEL_SHORT="HAI"
else
    MODEL_SHORT=$(echo "$MODEL_NAME" | head -c 3 | tr '[:lower:]' '[:upper:]')
fi

# Project directory name (truncate if long)
if [ -n "$CURRENT_DIR" ]; then
    DIR_NAME=$(basename "$CURRENT_DIR")
    [ ${#DIR_NAME} -gt 20 ] && DIR_NAME="${DIR_NAME:0:17}..."
else
    DIR_NAME="~"
fi

# Context usage percentage (from pre-calculated field in statusline input)
CTX_DISPLAY=""
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
if [[ "$PCT" =~ ^[0-9]+$ ]] && [ "$PCT" -gt 0 ]; then
    if [ "$PCT" -ge 90 ]; then
        CTX_DISPLAY="${C_RED}${PCT}%${C_RESET}"
    elif [ "$PCT" -ge 75 ]; then
        CTX_DISPLAY="${C_YELLOW}${PCT}%${C_RESET}"
    elif [ "$PCT" -ge 50 ]; then
        CTX_DISPLAY="${C_CYAN}${PCT}%${C_RESET}"
    else
        CTX_DISPLAY="${C_DIM}${PCT}%${C_RESET}"
    fi
fi

# Harness update check against the canonical dot-agent repo.
HARNESS_DISPLAY=""
DOT_AGENT_REPO="${DOT_AGENT_HOME:-$HOME/.dot-agent}"
if [ -d "$DOT_AGENT_REPO/.git" ]; then
    BEHIND=$(cd "$DOT_AGENT_REPO" && git rev-list HEAD..origin/main --count 2>/dev/null)
    if [ -n "$BEHIND" ] && [ "$BEHIND" -gt 0 ]; then
        HARNESS_DISPLAY="${C_YELLOW}⬆ ${BEHIND}${C_RESET}"
    fi
fi

# Build output: Model | Project | Context% | Harness updates
OUTPUT="${MODEL_COLOR}${MODEL_SHORT}${C_RESET} ${C_DIM}│${C_RESET} ${DIR_NAME}"
[ -n "$CTX_DISPLAY" ] && OUTPUT="${OUTPUT} ${C_DIM}│${C_RESET} ${CTX_DISPLAY}"
[ -n "$HARNESS_DISPLAY" ] && OUTPUT="${OUTPUT} ${C_DIM}│${C_RESET} ${HARNESS_DISPLAY}"

echo -e "$OUTPUT"
