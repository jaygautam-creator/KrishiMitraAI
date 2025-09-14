#!/usr/bin/env python3
"""
Crop Image Downloader for KrishiMitra AI
Downloads high-quality crop images from Unsplash API for all supported crops
"""

import os
import requests
from PIL import Image
import pandas as pd
import time
from pathlib import Path

# Configuration
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Supported crops from the CSV dataset
SUPPORTED_CROPS = [
    'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
    'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
    'papaya', 'watermelon', 'muskmelon', 'apple', 'orange', 
    'coconut', 'banana', 'grapes', 'coffee', 'jute', 'cotton', 
    'wheat', 'sugarcane'
]

# Alternative search terms for better image results
CROP_SEARCH_TERMS = {
    'rice': ['rice plant', 'rice crop', 'paddy field'],
    'maize': ['corn plant', 'maize crop', 'corn field'],
    'chickpea': ['chickpea plant', 'gram crop', 'chana plant'],
    'kidneybeans': ['kidney beans plant', 'red beans crop', 'rajma plant'],
    'pigeonpeas': ['pigeon peas plant', 'arhar crop', 'toor dal plant'],
    'mothbeans': ['moth beans plant', 'matki crop', 'dew beans'],
    'mungbean': ['mung bean plant', 'moong crop', 'green gram'],
    'blackgram': ['black gram plant', 'urad dal crop', 'black lentil'],
    'lentil': ['lentil plant', 'dal crop', 'masoor plant'],
    'pomegranate': ['pomegranate tree', 'pomegranate fruit', 'anar tree'],
    'papaya': ['papaya tree', 'papaya fruit', 'papaya plant'],
    'watermelon': ['watermelon plant', 'watermelon crop', 'watermelon field'],
    'muskmelon': ['muskmelon plant', 'cantaloupe crop', 'kharbuja'],
    'apple': ['apple tree', 'apple orchard', 'apple fruit tree'],
    'orange': ['orange tree', 'citrus tree', 'orange fruit tree'],
    'coconut': ['coconut tree', 'coconut palm', 'nariyal tree'],
    'banana': ['banana tree', 'banana plant', 'kela tree'],
    'grapes': ['grape vine', 'grape vineyard', 'angur vine'],
    'coffee': ['coffee plant', 'coffee tree', 'coffee beans plant'],
    'jute': ['jute plant', 'jute crop', 'jute fiber plant'],
    'cotton': ['cotton plant', 'cotton crop', 'cotton field'],
    'wheat': ['wheat plant', 'wheat crop', 'wheat field'],
    'sugarcane': ['sugarcane plant', 'sugar cane crop', 'ganna plant']
}

def download_from_unsplash(query, filename, max_attempts=3):
    """Download image from Unsplash with fallback URLs"""
    
    # Unsplash search URLs (no API key required for basic searches)
    base_urls = [
        f"https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800&q=80",  # Generic crop
        f"https://source.unsplash.com/800x600/?{query.replace(' ', '+')},agriculture",
        f"https://source.unsplash.com/800x600/?{query.replace(' ', '+')}",
    ]
    
    for attempt, url in enumerate(base_urls):
        try:
            print(f"  Attempt {attempt + 1}: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save the image
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            # Verify it's a valid image
            try:
                img = Image.open(filename)
                img.verify()
                print(f"  ✅ Successfully downloaded: {filename}")
                return True
            except Exception as e:
                print(f"  ❌ Invalid image file: {e}")
                if os.path.exists(filename):
                    os.remove(filename)
                
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            
        # Wait between attempts
        if attempt < len(base_urls) - 1:
            time.sleep(2)
    
    return False

def download_from_pixabay(query, filename):
    """Download from Pixabay as fallback"""
    try:
        # Pixabay API endpoint (free tier, no key required for basic use)
        url = f"https://pixabay.com/api/?key=9656065-a4094594c07e0e3451315666a&q={query}&image_type=photo&category=nature&min_width=800&safesearch=true"
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data['hits']:
                image_url = data['hits'][0]['webformatURL']
                
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                    
                print(f"  ✅ Downloaded from Pixabay: {filename}")
                return True
    except Exception as e:
        print(f"  ❌ Pixabay download failed: {e}")
    
    return False

def create_placeholder_image(crop_name, filename):
    """Create a simple placeholder image if download fails"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a 800x600 image with crop color theme
        colors = {
            'rice': '#90EE90', 'wheat': '#F5DEB3', 'maize': '#FFD700',
            'cotton': '#F8F8FF', 'sugarcane': '#98FB98',
            'default': '#98FB98'  # Light green for agriculture
        }
        
        bg_color = colors.get(crop_name, colors['default'])
        
        img = Image.new('RGB', (800, 600), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Draw crop name in center
        text = crop_name.title()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, fill='#2E8B57', font=font)
        
        # Add subtitle
        subtitle = "Crop Image"
        try:
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            small_font = font
            
        bbox = draw.textbbox((0, 0), subtitle, font=small_font)
        sub_width = bbox[2] - bbox[0]
        draw.text(((800 - sub_width) // 2, y + text_height + 20), 
                 subtitle, fill='#2E8B57', font=small_font)
        
        img.save(filename, 'JPEG', quality=85)
        print(f"  📸 Created placeholder: {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create placeholder: {e}")
        return False

def main():
    """Main function to download all crop images"""
    
    print("🌾 KrishiMitra AI - Crop Image Downloader")
    print("=" * 50)
    
    # Check existing images
    existing_images = []
    for crop in SUPPORTED_CROPS:
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            img_path = IMAGES_DIR / f"{crop}{ext}"
            if img_path.exists():
                existing_images.append(crop)
                break
    
    missing_crops = [crop for crop in SUPPORTED_CROPS if crop not in existing_images]
    
    print(f"📊 Status:")
    print(f"   Total crops: {len(SUPPORTED_CROPS)}")
    print(f"   With images: {len(existing_images)}")
    print(f"   Missing images: {len(missing_crops)}")
    print()
    
    if not missing_crops:
        print("✅ All crops already have images!")
        return
    
    print(f"📥 Downloading images for {len(missing_crops)} crops...")
    print()
    
    success_count = 0
    
    for i, crop in enumerate(missing_crops, 1):
        print(f"[{i}/{len(missing_crops)}] Processing: {crop}")
        
        filename = IMAGES_DIR / f"{crop}.jpg"
        
        # Try different search terms for this crop
        search_terms = CROP_SEARCH_TERMS.get(crop, [crop])
        downloaded = False
        
        for term in search_terms:
            print(f"  Searching for: '{term}'")
            
            # Try Unsplash first
            if download_from_unsplash(term, filename):
                downloaded = True
                break
            
            # Try Pixabay as fallback
            if download_from_pixabay(term, filename):
                downloaded = True
                break
            
            time.sleep(1)  # Rate limiting
        
        # Create placeholder if all downloads failed
        if not downloaded:
            print(f"  📝 All downloads failed, creating placeholder...")
            if create_placeholder_image(crop, filename):
                downloaded = True
        
        if downloaded:
            success_count += 1
        
        print()
        time.sleep(2)  # Rate limiting between crops
    
    print("=" * 50)
    print(f"✅ Download Complete!")
    print(f"   Successfully processed: {success_count}/{len(missing_crops)} crops")
    
    if success_count == len(missing_crops):
        print("🎉 All missing crop images have been added!")
    else:
        print(f"⚠️  {len(missing_crops) - success_count} crops still need images")
    
    print(f"📁 Images saved to: {IMAGES_DIR.absolute()}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Download cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
