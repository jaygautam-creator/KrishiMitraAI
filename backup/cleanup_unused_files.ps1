# KrishiMitra AI - Cleanup Unused Files
# This script removes redundant, duplicate, and unused files

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
            Write-Host "❌ Failed to move: $file - $($_.Exception.Message)" -ForegroundColor Red
            $skippedCount++
        }
    }
    else {
        Write-Host "⚠️  File not found (already removed?): $file" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host ""
Write-Host "📊 Cleanup Summary:" -ForegroundColor Cyan
Write-Host "   Files moved to backup: $removedCount" -ForegroundColor Green
Write-Host "   Files skipped: $skippedCount" -ForegroundColor Yellow
Write-Host "   Backup location: $backupDir" -ForegroundColor Cyan

# Show remaining project structure
Write-Host ""
Write-Host "📁 Current Project Structure:" -ForegroundColor Cyan
Write-Host "========================================"

# Core files that should remain
$coreFiles = @(
    "app\app.py",
    "app\fresh_recommendations.py", 
    "app\recommendation.py",
    "app\export_pdf.py",
    "app\crop_data.py",
    "app\data_preprocessing.py",
    "refresh_crop_images.py",
    "train_model.py",
    "model_loader.py", 
    "convert_model.py",
    "requirements.txt",
    "README.md",
    "Crop_recommendation.csv",
    ".gitignore"
)

Write-Host "✅ Essential Files:" -ForegroundColor Green
foreach ($file in $coreFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ MISSING: $file" -ForegroundColor Red
    }
}

# Count image files
$imageCount = (Get-ChildItem "images" -Filter "*.jpg" -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host ""
Write-Host "🖼️  Images folder: $imageCount crop images" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Cleanup completed! Your project is now leaner and cleaner." -ForegroundColor Green
Write-Host "💡 Tip: You can delete the backup folder '$backupDir' if everything works fine." -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Test your app: streamlit run app\app.py" 
Write-Host "   2. If everything works, delete: $backupDir"
Write-Host "   3. Commit your changes to git"
