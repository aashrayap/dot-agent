Launch OpenAI Codex CLI in a new Ghostty tab in yolo mode.

## Input
$ARGUMENTS

## Instructions

The entire argument string is the prompt to pass to Codex. Always use yolo mode.

### Build the command

```
codex --yolo -m gpt-5.3-codex "<prompt>"
```

### Launch in new Ghostty tab

1. Write the codex command to `/tmp/codex-run.sh`
2. Use `osascript` to send `Cmd+T` to Ghostty (opens a new tab), wait 0.8s, then type the run command + Enter

```bash
# Step 1: Write command
echo '#!/bin/bash' > /tmp/codex-run.sh
echo '<codex command here>' >> /tmp/codex-run.sh
chmod +x /tmp/codex-run.sh

# Step 2: Open new tab and run
osascript <<'APPLESCRIPT'
tell application "System Events"
    tell process "Ghostty"
        set frontmost to true
        keystroke "t" using {command down}
        delay 0.8
        keystroke "bash /tmp/codex-run.sh"
        key code 36
    end tell
end tell
APPLESCRIPT
```

### Confirm to user
After launching, tell the user:
- The prompt that was sent
- That Codex is running in yolo mode in a new Ghostty tab

### Error handling
- If no prompt is provided, ask the user what they want Codex to do
