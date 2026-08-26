# Registers "Bench Log - Activity Posting Automation".
# Already registered live on 2026-07-27 by running this content directly via
# PowerShell (see Projects/Local AI Bench Log/STATE.md for the handoff note).
# This file exists so the live task definition is reproducible from source.
#
# Trigger time (10am, every 3 days) matches PC 2's YoutubeAudioWatch task,
# which also fires at 10am and also uses pc2 -- both were aligned deliberately.
#
# To reproduce or re-register after a change:
#   Unregister-ScheduledTask -TaskName "Bench Log - Activity Posting Automation" -Confirm:$false
#   (then run the block below)

# NOTE 2026-08-26: this was `-Execute "claude.exe"` (bare name). Task Scheduler
# does not resolve PATH the way an interactive shell does, so every run since
# registration failed with 0x80070002 ERROR_FILE_NOT_FOUND -- the task never
# launched at all, and nothing surfaced that. Absolute path only.
$Action = New-ScheduledTaskAction -Execute "C:\Users\Nipoon Kalam\.local\bin\claude.exe" `
    -Argument "--print --dangerously-skip-permissions `"$(Get-Content 'E:\CLAUDE\AFFILATE MARKETTING\scripts\run_pipeline_prompt.md' -Raw)`"" `
    -WorkingDirectory "E:\CLAUDE\AFFILATE MARKETTING"

$Trigger = New-ScheduledTaskTrigger -Daily -DaysInterval 3 -At 10am

Register-ScheduledTask -TaskName "Bench Log - Activity Posting Automation" `
    -Action $Action -Trigger $Trigger `
    -Description "Every 3 days at 10am (alongside YoutubeAudioWatch): scans Main Brain activity, drafts bench-log posts, generates pc2 hero images, feeds ADHD Data profiler. Never auto-publishes." `
    -RunLevel Limited
