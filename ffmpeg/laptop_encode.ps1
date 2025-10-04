$dir = Read-Host "Enter the directory to encode"

if (!(Test-Path $dir -PathType Container)) {
    Write-Host "Directory does not exist!"
    exit
}

Write-Host "WARNING: This will re-encode all .mkv and .mp4 files in '$dir' (recursively)."
Write-Host "Original files will be DELETED after encoding."
$confirm = Read-Host "Are you sure? (y/N)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "Aborted."
    exit
}

# Track total encoding time
$totalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Get-ChildItem -Path $dir -Recurse -Include *.mkv, *.mp4 | ForEach-Object {
    $file = $_.FullName
    $outfile = [System.IO.Path]::ChangeExtension($file, $null) + "[ENCODED].mp4"

    Write-Host "`n----------------------------------------"
    Write-Host "Encoding: $file -> $outfile"

    # Track per-file time
    $fileStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

    & ffmpeg -i "$file" `
        -c:v libx264 -preset slow -crf 20 `
        -vf "scale='min(1920,iw)':'min(1080,ih)':force_original_aspect_ratio=decrease" `
        -c:a aac -b:a 192k `
        "$outfile"

    $fileStopwatch.Stop()

    if ($LASTEXITCODE -eq 0) {
        Remove-Item "$file"
        Write-Host "✅ Finished and deleted: $file"
        Write-Host "⏱️ File time: $($fileStopwatch.Elapsed.ToString())"
    } else {
        Write-Host "❌ Failed: $file (original kept)"
    }

    Write-Host "⏱️ Total elapsed so far: $($totalStopwatch.Elapsed.ToString())"
    Write-Host "----------------------------------------`n"
}

# Final total
$totalStopwatch.Stop()
Write-Host "🎉 All encoding finished in $($totalStopwatch.Elapsed.ToString())."

