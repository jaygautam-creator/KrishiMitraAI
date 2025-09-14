#!/usr/bin/env python3
"""
Fix Corrupted Images in KrishiMitra AI
This script identifies and fixes corrupted image files.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pandas as pd

IMAGES_DIR = Path("images")

def check_image_integrity(image_path):
    """Check if an image file is valid and can be opened"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        
        # Re-open to check it can be loaded properly
        with Image.open(image_path) as img:
            img.load()
        
        return True, None
    except Exception as e:
        return False, str(e)

def create_replacement_image(crop_name, filename):
    """Create a high-quality replacement image"""
    try:
        # Crop-specific styling
        themes = {
            'blackgram': {'bg': '#2F2F2F', 'primary': '#FFFFFF', 'secondary': '#D3D3D3', 'emoji': '🫘'},
            'chickpea': {'bg': '#F5F5DC', 'primary': '#8B4513', 'secondary': '#DAA520', 'emoji': '🌰'},
            'cotton': {'bg': '#FFFFFF', 'primary': '#4682B4', 'secondary': '#87CEEB', 'emoji': '☁️'},
            'lentil': {'bg': '#CD853F', 'primary': '#FFFFFF', 'secondary': '#F5DEB3', 'emoji': '🟤'},
            'mango': {'bg': '#FFD700', 'primary': '#FF6B35', 'secondary': '#FFA500', 'emoji': '🥭'},
            'mothbeans': {'bg': '#FFF8DC', 'primary': '#6B4423', 'secondary': '#CD853F', 'emoji': '🫛'},
            'mungbean': {'bg': '#F0FFF0', 'primary': '#006400', 'secondary': '#32CD32', 'emoji': '🟢'},
            'muskmelon': {'bg': '#FFFACD', 'primary': '#FFA500', 'secondary': '#FFD700', 'emoji': '🍈'},
            'pigeonpeas': {'bg': '#F0F8FF', 'primary': '#4682B4', 'secondary': '#87CEEB', 'emoji': '🟫'},
        }
        
        theme = themes.get(crop_name.lower(), {'bg': '#F0F8FF', 'primary': '#2E8B57', 'secondary': '#98FB98', 'emoji': '🌱'})
        
        # Create high-resolution image (800x600)
        img = Image.new('RGB', (800, 600), theme['bg'])
        draw = ImageDraw.Draw(img)
        
        # Try to load system fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 56)
            subtitle_font = ImageFont.truetype("arial.ttf", 32)
            desc_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        
        # Draw decorative elements
        for i in range(0, 800, 80):
            for j in range(0, 600, 80):
                if (i + j) % 160 == 0:
                    draw.ellipse([(i+10, j+10), (i+30, j+30)], outline=theme['secondary'], width=2)
        
        # Draw crop emoji at top
        emoji_y = 100
        emoji_text = theme['emoji']
        emoji_bbox = draw.textbbox((0, 0), emoji_text, font=title_font)
        emoji_width = emoji_bbox[2] - emoji_bbox[0]
        emoji_x = (800 - emoji_width) // 2
        draw.text((emoji_x, emoji_y), emoji_text, font=title_font)
        
        # Draw main crop name
        crop_display = crop_name.replace('_', ' ').title()
        bbox = draw.textbbox((0, 0), crop_display, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (800 - text_width) // 2
        text_y = 250
        
        # Text shadow
        draw.text((text_x + 2, text_y + 2), crop_display, fill='#00000030', font=title_font)
        draw.text((text_x, text_y), crop_display, fill=theme['primary'], font=title_font)
        
        # Subtitle
        subtitle = "🌾 Agricultural Crop"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        sub_x = (800 - sub_width) // 2
        sub_y = text_y + 80
        draw.text((sub_x, sub_y), subtitle, fill=theme['secondary'], font=subtitle_font)
        
        # Description
        descriptions = {
            'blackgram': 'High-protein black lentil',
            'chickpea': 'Nutritious chickpea variety',
            'cotton': 'White fiber cash crop',
            'lentil': 'Essential pulse crop',
            'mango': 'Tropical mango tree',
            'mothbeans': 'Drought-resistant beans',
            'mungbean': 'Green gram variety',
            'muskmelon': 'Sweet melon fruit',
            'pigeonpeas': 'Traditional pigeon peas',
        }
        
        desc_text = descriptions.get(crop_name.lower(), 'Agricultural crop variety')
        bbox = draw.textbbox((0, 0), desc_text, font=desc_font)
        desc_width = bbox[2] - bbox[0]
        desc_x = (800 - desc_width) // 2
        desc_y = sub_y + 50
        draw.text((desc_x, desc_y), desc_text, fill=theme['primary'], font=desc_font)
        
        # Footer text
        footer_text = "KrishiMitra AI • Crop Image"
        bbox = draw.textbbox((0, 0), footer_text, font=desc_font)
        footer_width = bbox[2] - bbox[0]
        footer_x = (800 - footer_width) // 2
        footer_y = 520
        draw.text((footer_x, footer_y), footer_text, fill=theme['secondary'], font=desc_font)
        
        # Border
        draw.rectangle([(15, 15), (785, 585)], outline=theme['primary'], width=4)
        
        # Save high-quality image
        img.save(filename, 'JPEG', quality=95, optimize=True)
        print(f"  ✅ Created replacement: {filename.name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create replacement: {e}")
        return False

def main():
    print("🔧 KrishiMitra AI - Fix Corrupted Images")
    print("=" * 50)
    
    if not IMAGES_DIR.exists():
        print("❌ Images directory not found!")
        return
    
    # Get required crops from dataset
    try:
        df = pd.read_csv('Crop_recommendation.csv')
        required_crops = set(df['label'].unique())
        print(f"📋 Dataset requires {len(required_crops)} crop images")
    except Exception as e:
        print(f"⚠️ Could not load dataset: {e}")
        required_crops = set()
    
    # Check all image files
    image_files = list(IMAGES_DIR.glob('*.jpg'))
    print(f"📁 Found {len(image_files)} image files")
    print()
    
    corrupted_files = []
    valid_files = []
    
    print("🔍 Checking image integrity...")
    for img_path in image_files:
        is_valid, error = check_image_integrity(img_path)
        
        if is_valid:
            print(f"  ✅ {img_path.name} - Valid")
            valid_files.append(img_path)
        else:
            print(f"  ❌ {img_path.name} - CORRUPTED: {error}")
            corrupted_files.append(img_path)
    
    print(f"\n📊 Results:")
    print(f"   Valid images: {len(valid_files)}")
    print(f"   Corrupted images: {len(corrupted_files)}")
    
    # Fix corrupted images
    if corrupted_files:
        print(f"\n🔧 Fixing {len(corrupted_files)} corrupted images...")
        
        for corrupt_file in corrupted_files:
            print(f"\n[Fix] Processing: {corrupt_file.name}")
            
            # Backup the corrupted file
            backup_name = f"corrupted_{corrupt_file.name}"
            backup_path = IMAGES_DIR / backup_name
            try:
                corrupt_file.rename(backup_path)
                print(f"  📦 Backed up as: {backup_name}")
            except Exception as e:
                print(f"  ⚠️ Could not backup: {e}")
            
            # Create replacement
            crop_name = corrupt_file.stem.lower()
            if create_replacement_image(crop_name, corrupt_file):
                print(f"  🎨 Replacement created successfully")
            else:
                print(f"  ❌ Failed to create replacement")
    
    # Check for missing required crops
    print(f"\n🎯 Checking coverage of required crops...")
    current_crops = set()
    for img_file in IMAGES_DIR.glob('*.jpg'):
        if not img_file.name.startswith('corrupted_'):
            current_crops.add(img_file.stem.lower())
    
    missing_crops = required_crops - current_crops
    
    if missing_crops:
        print(f"\n📝 Creating images for {len(missing_crops)} missing crops...")
        for crop in sorted(missing_crops):
            crop_path = IMAGES_DIR / f"{crop}.jpg"
            if create_replacement_image(crop, crop_path):
                print(f"  ✅ Created: {crop}.jpg")
    
    # Final status
    final_images = len([f for f in IMAGES_DIR.glob('*.jpg') if not f.name.startswith('corrupted_')])
    print(f"\n" + "=" * 50)
    print(f"✅ Image Fix Complete!")
    print(f"   Total valid images: {final_images}")
    print(f"   Required crops: {len(required_crops)}")
    
    if final_images >= len(required_crops):
        print(f"🎉 All required crop images are now available!")
    else:
        print(f"⚠️ Still missing {len(required_crops) - final_images} images")
    
    print(f"\n🚀 Your app should now work without image errors!")
    print(f"   Run: streamlit run app\\app.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Process cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
