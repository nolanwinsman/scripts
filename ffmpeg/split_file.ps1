<#
.SYNOPSIS
    Splits an MKV video file using ffmpeg without re-encoding.

.DESCRIPTION
    This script uses ffmpeg to cut a segment from an existing .mkv file
    while preserving the original video, audio, subtitle, and attachment
    streams exactly as-is (stream copy, no quality loss).

    The output file is written to the same directory as the input file
    and appends "_cut" to the filename.

.PARAMETER InputFile
    Absolute path to the input .mkv file.

.PARAMETER StartTime
    Start time for the cut.
    Use a timestamp (e.g. 00:24:10.000) or the keyword "start" to begin
    at the start of the file.

.PARAMETER EndTime
    End time for the cut.
    Use a timestamp (e.g. 00:30:11.000) or the keyword "end" to cut
    until the end of the file.

.TIME FORMAT
    Accepted ffmpeg time formats include:
        HH:MM:SS
        HH:MM:SS.mmm
        MM:SS
        Seconds (e.g. 1811 or 1811.5)

    NOTE: Use colons (:) between time units.
          "00:30:11.000" is valid
          "00.30:11.000" is NOT valid

.EXAMPLES
    Cut from start to 24 minutes 10 seconds:
        .\split-mkv.ps1 "C:\Videos\episode.mkv" start "00:24:10.000"

    Cut from 30 minutes 11 seconds to the end:
        .\split-mkv.ps1 "C:\Videos\episode.mkv" "00:30:11.000" end

    Cut a middle segment:
        .\split-mkv.ps1 "C:\Videos\episode.mkv" "00:12:00" "00:24:10"

.REQUIREMENTS
    - ffmpeg must be installed and available in PATH

.NOTES
    - This script uses stream copy (-c copy), so there is NO re-encoding.
    - Cuts are keyframe-accurate, not frame-accurate.
    - Very fast and ideal for anime episode splitting (Plex / Sonarr safe).
#>


param (
    [Parameter(Mandatory = $true)]
    [string]$InputFile,

    [Parameter(Mandatory = $true)]
    [string]$StartTime,

    [Parameter(Mandatory = $true)]
    [string]$EndTime
)

# Ensure ffmpeg is available
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Error "ffmpeg not found in PATH"
    exit 1
}

# Resolve absolute path
$InputFile = (Resolve-Path $InputFile).Path

# Extract path parts
$directory = [System.IO.Path]::GetDirectoryName($InputFile)
$baseName  = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
$extension = [System.IO.Path]::GetExtension($InputFile)

# Output file in same directory
$outputFile = Join-Path $directory "${baseName}_cut${extension}"

# Normalize start time
if ($StartTime.ToLower() -eq "start") {
    $StartTime = "00:00:00"
}

# Build ffmpeg arguments
$ffmpegArgs = @(
    "-hide_banner",
    "-loglevel", "error",
    "-ss", $StartTime,
    "-i", $InputFile,
    "-map", "0",
    "-c", "copy"
)

# Handle end time
if ($EndTime.ToLower() -ne "end") {
    $ffmpegArgs += @("-to", $EndTime)
}

# Add output file
$ffmpegArgs += $outputFile

# Run ffmpeg
& ffmpeg @ffmpegArgs

Write-Host "Created: $outputFile"

