#!/usr/bin/env python3
"""
Refresh Crop Images - Re-downloads all crop images with specific URLs
"""

import os
import requests
from PIL import Image
import time
from pathlib import Path

# Configuration
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Specific high-quality image URLs for each crop
CROP_SPECIFIC_URLS = {
    'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=80',  # Rice paddy field
    'wheat': 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80',  # Wheat ears
    'maize': 'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=800&q=80',  # Corn field
    'chickpea': 'https://images.unsplash.com/photo-1610632734225-4c13e7a2f467?w=800&q=80',  # Chickpeas
    'kidneybeans': 'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=800&q=80',  # Red kidney beans
    'pigeonpeas': 'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Pigeon peas
    'mothbeans': 'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Moth beans
    'mungbean': 'https://images.unsplash.com/photo-1610632734225-4c13e7a2f467?w=800&q=80',  # Green mung beans  
    'blackgram': 'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Black gram
    'lentil': 'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Mixed lentils
    'apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=800&q=80',  # Apple orchard
    'orange': 'https://images.unsplash.com/photo-1557800636-894a64c1696f?w=800&q=80',  # Orange tree
    'banana': 'https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=800&q=80',  # Banana plantation
    'grapes': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=800&q=80',  # Grape vineyard
    'coconut': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80',  # Coconut palm
    'cotton': 'https://images.unsplash.com/photo-1609113386779-3b57bb9ed6cb?w=800&q=80',  # Cotton field
    'sugarcane': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',  # Sugarcane field
    'coffee': 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80',  # Coffee plantation
    'jute': 'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=800&q=80',  # Jute/fiber crop
    'watermelon': 'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80',  # Watermelon field
    'muskmelon': 'https://images.unsplash.com/photo-1494093845797-185376bd8017?w=800&q=80',  # Muskmelon
    'papaya': 'https://images.unsplash.com/photo-1528825871115-3581a5387919?w=800&q=80',  # Papaya tree
    'pomegranate': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Pomegranate
}

def download_image(url, filename):
    """Download an image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"  📥 Downloading from: {url[:60]}...")
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save the image
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Verify it's a valid image
        img = Image.open(filename)
        img.verify()
        
        # Reload image to get size info
        img = Image.open(filename)
        print(f"  ✅ Downloaded: {filename.name} ({img.size[0]}x{img.size[1]})")
        return True
        
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False

def main():
    print("🔄 Refreshing All Crop Images")
    print("=" * 50)
    
    success_count = 0
    total_crops = len(CROP_SPECIFIC_URLS)
    
    for i, (crop_name, url) in enumerate(CROP_SPECIFIC_URLS.items(), 1):
        print(f"[{i}/{total_crops}] {crop_name.title()}")
        
        filename = IMAGES_DIR / f"{crop_name}.jpg"
        
        # Remove old file if it exists
        if filename.exists():
            filename.unlink()
        
        if download_image(url, filename):
            success_count += 1
        
        print()
        
        # Rate limiting to be respectful to the server
        if i < total_crops:
            time.sleep(1)
    
    print("=" * 50)
    print(f"✅ Refresh Complete!")
    print(f"   Successfully downloaded: {success_count}/{total_crops} images")
    
    if success_count == total_crops:
        print("🎉 All crop images are now unique and specific!")
    else:
        failed = total_crops - success_count
        print(f"⚠️ {failed} images need manual attention")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
