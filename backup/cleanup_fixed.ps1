# KrishiMitra AI - Cleanup Unused Files
Write-Host "🧹 KrishiMitra AI - Cleaning up unused files..." -ForegroundColor Green
Write-Host "========================================"

# Create backup directory first
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "📦 Created backup directory: $backupDir" -ForegroundColor Yellow

# Files to remove
$filesToRemove = @(
    "download_crop_images.py",
    "download_specific_crop_images.py", 
    "debug_pincode.py",
    "pincode_test.py",
    "test_pincode_recommendations.py",
    "Untitled.ipynb",
    "images\rice.jpg.webp",
    "app\recommendation-v.py"
)

$removedCount = 0
$skippedCount = 0

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        # Move to backup first
        $backupPath = Join-Path $backupDir (Split-Path $file -Leaf)
        try {
            Move-Item $file $backupPath -Force
            Write-Host "✅ Moved to backup: $file" -ForegroundColor Green
            $removedCount++
        }
        catch {
            Write-Host "❌ Failed to move: $file" -ForegroundColor Red
            $skippedCount++
        }
    }
    else {
        Write-Host "⚠️ File not found: $file" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host ""
Write-Host "📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "   Files moved to backup: $removedCount" -ForegroundColor Green  
Write-Host "   Files skipped: $skippedCount" -ForegroundColor Yellow
Write-Host "   Backup location: $backupDir" -ForegroundColor Cyan

# Count remaining files
$imageCount = (Get-ChildItem "images" -Filter "*.jpg" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host ""
Write-Host "🖼️ Images folder: $imageCount crop images" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Cleanup completed!" -ForegroundColor Green
Write-Host "💡 Test your app: streamlit run app\app.py" -ForegroundColor Cyan
