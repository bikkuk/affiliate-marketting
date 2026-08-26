# Registers "Bench Log - Publish AI Server Part 2".
#
# One-time task: fires 2026-08-29 at 10am and runs scripts/publish_part2.py,
# which moves the staged part-2 files out of scheduled/2026_08_29/ into the
# site, updates index.astro + sitemap.xml, builds, commits and pushes.
# Netlify deploys from the push.
#
# 10am matches the existing "Bench Log - Activity Posting Automation" task and
# PC 2's YoutubeAudioWatch, which both also fire at 10am.
#
# Publication was pre-approved by Nipoon on 2026-08-26 for both parts of the
# series, so this task publishes without a review step. The script is
# idempotent -- if scheduled/2026_08_29/ is already gone it exits clean.
#
# To re-register after a change:
#   Unregister-ScheduledTask -TaskName "Bench Log - Publish AI Server Part 2" -Confirm:$false
#   (then run the block below)

$Action = New-ScheduledTaskAction -Execute "E:\Python311\python.exe" `
    -Argument "`"E:\CLAUDE\AFFILATE MARKETTING\scripts\publish_part2.py`"" `
    -WorkingDirectory "E:\CLAUDE\AFFILATE MARKETTING"

$Trigger = New-ScheduledTaskTrigger -Once -At "2026-08-29T10:00:00"

# StartWhenAvailable: if the PC is off or asleep at 10am the run is not lost,
# it fires at the next opportunity instead.
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 20) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName "Bench Log - Publish AI Server Part 2" `
    -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "One-time, 2026-08-29 10am: publishes part 2 of the AI server series (staged in scheduled/2026_08_29/), commits and pushes so Netlify deploys. Pre-approved 2026-08-26. Idempotent." `
    -RunLevel Limited
