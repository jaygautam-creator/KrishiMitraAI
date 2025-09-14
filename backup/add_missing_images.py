#!/usr/bin/env python3
"""
Add Missing Crop Images to KrishiMitra AI
This script helps you add the remaining crop images needed by the app.
"""

import os
import shutil
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Missing crop images that are needed
MISSING_CROPS = [
    'blackgram',
    'chickpea', 
    'mothbeans',
    'mungbean',
    'pigeonpeas'
]

# High-quality image URLs for missing crops
CROP_IMAGE_URLS = {
    'blackgram': [
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',
        'https://source.unsplash.com/800x600/?black,lentils,pulse,agriculture',
    ],
    'chickpea': [
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',
        'https://source.unsplash.com/800x600/?chickpea,gram,legume,agriculture',
    ],
    'mothbeans': [
        'https://source.unsplash.com/800x600/?small,beans,legume,agriculture',
        'https://source.unsplash.com/800x600/?pulse,beans,crop,field',
    ],
    'mungbean': [
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',
        'https://source.unsplash.com/800x600/?mung,green,beans,agriculture',
    ],
    'pigeonpeas': [
        'https://source.unsplash.com/800x600/?pigeon,peas,pulse,agriculture',
        'https://source.unsplash.com/800x600/?field,peas,crop,plant',
    ]
}

def download_image_from_url(url, filename):
    """Download an image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  📥 Downloading from: {url[:60]}...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Verify it's a valid image
        img = Image.open(filename)
        img.verify()
        
        # Reload to get size
        img = Image.open(filename)
        print(f"  ✅ Downloaded: {filename.name} ({img.size[0]}x{img.size[1]})")
        return True
        
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        if os.path.exists(filename):
            os.remove(filename)
        return False

def create_high_quality_placeholder(crop_name, filename):
    """Create a high-quality placeholder image"""
    try:
        # Crop-specific styling
        themes = {
            'blackgram': {'bg': '#2F2F2F', 'primary': '#FFFFFF', 'secondary': '#D3D3D3', 'emoji': '⚫'},
            'chickpea': {'bg': '#F5F5DC', 'primary': '#8B4513', 'secondary': '#DAA520', 'emoji': '🟡'},
            'mothbeans': {'bg': '#FFF8DC', 'primary': '#6B4423', 'secondary': '#CD853F', 'emoji': '🟤'},
            'mungbean': {'bg': '#F0FFF0', 'primary': '#006400', 'secondary': '#32CD32', 'emoji': '🟢'},
            'pigeonpeas': {'bg': '#F0F8FF', 'primary': '#4682B4', 'secondary': '#87CEEB', 'emoji': '🔵'},
        }
        
        theme = themes.get(crop_name, {'bg': '#F0F8FF', 'primary': '#2E8B57', 'secondary': '#98FB98', 'emoji': '🌱'})
        
        # Create high-resolution image (800x600)
        img = Image.new('RGB', (800, 600), theme['bg'])
        draw = ImageDraw.Draw(img)
        
        # Try to load system fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 64)
            subtitle_font = ImageFont.truetype("arial.ttf", 36)
            desc_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        
        # Draw decorative background pattern
        for i in range(0, 800, 100):
            for j in range(0, 600, 100):
                if (i + j) % 200 == 0:
                    draw.ellipse([(i, j), (i+40, j+40)], outline=theme['secondary'], width=2)
        
        # Draw main crop name
        crop_display = crop_name.replace('_', ' ').title()
        bbox = draw.textbbox((0, 0), crop_display, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (800 - text_width) // 2
        text_y = 200
        
        # Text shadow
        draw.text((text_x + 3, text_y + 3), crop_display, fill='#00000040', font=title_font)
        draw.text((text_x, text_y), crop_display, fill=theme['primary'], font=title_font)
        
        # Subtitle
        subtitle = f"🌾 {crop_name.title()} Crop"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (800 - sub_width) // 2
        sub_y = text_y + 80
        draw.text((sub_x, sub_y), subtitle, fill=theme['secondary'], font=subtitle_font)
        
        # Description
        descriptions = {
            'blackgram': 'High-protein pulse crop',
            'chickpea': 'Nutritious legume variety',
            'mothbeans': 'Drought-resistant pulse',
            'mungbean': 'Green gram for health',
            'pigeonpeas': 'Traditional protein source',
        }
        
        desc_text = descriptions.get(crop_name, 'Agricultural crop variety')
        bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
        desc_width = bbox[2] - bbox[0]
        desc_x = (800 - desc_width) // 2
        desc_y = sub_y + 60
        draw.text((desc_x, desc_y), desc_text, fill=theme['primary'], font=desc_font)
        
        # Border
        draw.rectangle([(10, 10), (790, 590)], outline=theme['primary'], width=6)
        draw.rectangle([(20, 20), (780, 580)], outline=theme['secondary'], width=2)
        
        # Save high-quality image
        img.save(filename, 'JPEG', quality=95, optimize=True)
        print(f"  🎨 Created high-quality placeholder: {filename.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Placeholder creation failed: {e}")
        return False

def copy_user_image(crop_name):
    """Help user copy an image from their computer"""
    print(f"\n📂 To add {crop_name}.jpg manually:")
    print(f"   1. Find your downloaded {crop_name} image")
    print(f"   2. Copy it to: {IMAGES_DIR.absolute()}")
    print(f"   3. Rename it to: {crop_name}.jpg")
    print(f"   4. Press Enter when done, or 's' to skip")
    
    user_input = input("   Ready? (Enter/s): ").strip().lower()
    
    if user_input == 's':
        print(f"   ⏭️ Skipped {crop_name}")
        return False
    
    # Check if user added the file
    crop_path = IMAGES_DIR / f"{crop_name}.jpg"
    if crop_path.exists():
        try:
            # Verify it's a valid image
            img = Image.open(crop_path)
            img.verify()
            print(f"   ✅ {crop_name}.jpg added successfully!")
            return True
        except Exception as e:
            print(f"   ❌ Invalid image file: {e}")
            return False
    else:
        print(f"   ❌ {crop_name}.jpg not found in images folder")
        return False

def main():
    print("🌾 KrishiMitra AI - Add Missing Crop Images")
    print("=" * 50)
    
    print(f"📋 Missing crops: {', '.join(MISSING_CROPS)}")
    print(f"📁 Images will be saved to: {IMAGES_DIR.absolute()}")
    print()
    
    # Ask user preference
    print("How would you like to add the missing images?")
    print("1. 🔄 Download automatically from web")
    print("2. 📂 Copy from files I already have")
    print("3. 🎨 Create high-quality placeholders")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    success_count = 0
    
    for crop in MISSING_CROPS:
        print(f"\n[{MISSING_CROPS.index(crop) + 1}/{len(MISSING_CROPS)}] Processing: {crop}")
        filename = IMAGES_DIR / f"{crop}.jpg"
        
        if filename.exists():
            print(f"  ✅ {crop}.jpg already exists, skipping")
            success_count += 1
            continue
        
        success = False
        
        if choice == '1':
            # Try to download
            if crop in CROP_IMAGE_URLS:
                for url in CROP_IMAGE_URLS[crop]:
                    if download_image_from_url(url, filename):
                        success = True
                        break
            
            # Create placeholder if download failed
            if not success:
                print(f"  🎨 Download failed, creating placeholder...")
                success = create_high_quality_placeholder(crop, filename)
                
        elif choice == '2':
            # Manual copy
            success = copy_user_image(crop)
            
            # Create placeholder if user skipped
            if not success:
                print(f"  🎨 Creating placeholder instead...")
                success = create_high_quality_placeholder(crop, filename)
                
        elif choice == '3':
            # Create placeholder
            success = create_high_quality_placeholder(crop, filename)
        
        if success:
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Process Complete!")
    print(f"   Successfully added: {success_count}/{len(MISSING_CROPS)} images")
    
    if success_count == len(MISSING_CROPS):
        print("🎉 All missing crop images are now available!")
    else:
        remaining = len(MISSING_CROPS) - success_count
        print(f"⚠️ {remaining} images still need to be added")
    
    # Final status check
    total_images = len(list(IMAGES_DIR.glob('*.jpg')))
    print(f"📊 Total crop images: {total_images}")
    print(f"🚀 Run your app: streamlit run app\\app.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Process cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
