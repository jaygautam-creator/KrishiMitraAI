#!/usr/bin/env python3
"""
Enhanced Crop Image Downloader for KrishiMitra AI
Downloads specific, high-quality crop images from multiple sources
"""

import os
import requests
from PIL import Image
import time
from pathlib import Path
import random

# Configuration
IMAGES_DIR = Path("images")
IMAGES_DIR.mkdir(exist_ok=True)

# Specific image URLs for each crop from various sources
CROP_IMAGE_URLS = {
    'rice': [
        'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=80',  # Rice paddy field
        'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=800&q=80',  # Rice grains
        'https://images.unsplash.com/photo-1582718471317-6f1e7e43bd9e?w=800&q=80',  # Rice plant
    ],
    'wheat': [
        'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800&q=80',  # Wheat field
        'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=800&q=80',  # Wheat ears
        'https://images.unsplash.com/photo-1595569712398-d3d0bb1d2dda?w=800&q=80',  # Golden wheat
    ],
    'maize': [
        'https://images.unsplash.com/photo-1551754655-cd27e38d2076?w=800&q=80',  # Corn field
        'https://images.unsplash.com/photo-1586743536702-2c7fdf7c56a8?w=800&q=80',  # Corn cobs
        'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800&q=80',  # Corn plants
    ],
    'chickpea': [
        'https://images.unsplash.com/photo-1610632734225-4c13e7a2f467?w=800&q=80',  # Chickpeas
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Legumes
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Pulse crops
    ],
    'kidneybeans': [
        'https://images.unsplash.com/photo-1587593810167-a84920ea0781?w=800&q=80',  # Red kidney beans
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Bean varieties
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Beans
    ],
    'pigeonpeas': [
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Pigeon peas
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Pulse varieties
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Legumes
    ],
    'mothbeans': [
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Small beans
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Bean varieties
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Mixed beans
    ],
    'mungbean': [
        'https://images.unsplash.com/photo-1610632734225-4c13e7a2f467?w=800&q=80',  # Green mung beans
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Small green beans
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Mung varieties
    ],
    'blackgram': [
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Black lentils
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Dark beans
        'https://images.unsplash.com/photo-1580554530645-ca2822481d76?w=800&q=80',  # Black gram
    ],
    'lentil': [
        'https://images.unsplash.com/photo-1610632734225-4c13e7a2f467?w=800&q=80',  # Red lentils
        'https://images.unsplash.com/photo-1535398864574-3e46d825e6ad?w=800&q=80',  # Mixed lentils
        'https://images.unsplash.com/photo-1604966503019-9e1e9b1b2e2c?w=800&q=80',  # Lentil varieties
    ],
    'apple': [
        'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=800&q=80',  # Apple orchard
        'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?w=800&q=80',  # Red apples on tree
        'https://images.unsplash.com/photo-1576179635662-9d1983e97e1e?w=800&q=80',  # Apple tree
    ],
    'orange': [
        'https://images.unsplash.com/photo-1557800636-894a64c1696f?w=800&q=80',  # Orange tree
        'https://images.unsplash.com/photo-1511688878353-3a2f5be94cd7?w=800&q=80',  # Oranges on tree
        'https://images.unsplash.com/photo-1582979512210-99b6a53386f9?w=800&q=80',  # Orange grove
    ],
    'banana': [
        'https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=800&q=80',  # Banana plantation
        'https://images.unsplash.com/photo-1528825871115-3581a5387919?w=800&q=80',  # Banana tree
        'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=800&q=80',  # Banana bunch
    ],
    'grapes': [
        'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=800&q=80',  # Grape vineyard
        'https://images.unsplash.com/photo-1471296421402-fb1c9c074246?w=800&q=80',  # Grape vines
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Purple grapes
    ],
    'coconut': [
        'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80',  # Coconut palm
        'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&q=80',  # Coconut tree
        'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80',  # Coconut grove
    ],
    'cotton': [
        'https://images.unsplash.com/photo-1609113386779-3b57bb9ed6cb?w=800&q=80',  # Cotton field
        'https://images.unsplash.com/photo-1471970471044-2bdf4cb3cd31?w=800&q=80',  # Cotton plant
        'https://images.unsplash.com/photo-1516975080664-ed2fc6a32937?w=800&q=80',  # Cotton bolls
    ],
    'sugarcane': [
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',  # Sugarcane field
        'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=800&q=80',  # Sugarcane plants
        'https://images.unsplash.com/photo-1471970471044-2bdf4cb3cd31?w=800&q=80',  # Green sugarcane
    ],
    'coffee': [
        'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&q=80',  # Coffee plantation
        'https://images.unsplash.com/photo-1542843137-8791a6904d14?w=800&q=80',  # Coffee beans on plant
        'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=800&q=80',  # Coffee tree
    ],
    'jute': [
        'https://images.unsplash.com/photo-1471970471044-2bdf4cb3cd31?w=800&q=80',  # Jute field
        'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80',  # Fiber crop
        'https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=800&q=80',  # Green crop field
    ],
    'watermelon': [
        'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80',  # Watermelon field
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Watermelon vine
        'https://images.unsplash.com/photo-1494093845797-185376bd8017?w=800&q=80',  # Watermelon plant
    ],
    'muskmelon': [
        'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80',  # Melon field
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Melon vine
        'https://images.unsplash.com/photo-1494093845797-185376bd8017?w=800&q=80',  # Muskmelon plant
    ],
    'papaya': [
        'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80',  # Papaya tree
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Papaya fruit tree
        'https://images.unsplash.com/photo-1494093845797-185376bd8017?w=800&q=80',  # Papaya plant
    ],
    'pomegranate': [
        'https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&q=80',  # Pomegranate tree
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',  # Pomegranate orchard
        'https://images.unsplash.com/photo-1494093845797-185376bd8017?w=800&q=80',  # Pomegranate plant
    ]
}

# Fallback search terms for web search
WEB_SEARCH_URLS = {
    'rice': 'https://source.unsplash.com/800x600/?rice,paddy,field,agriculture',
    'wheat': 'https://source.unsplash.com/800x600/?wheat,grain,field,golden',
    'maize': 'https://source.unsplash.com/800x600/?corn,maize,field,agriculture',
    'chickpea': 'https://source.unsplash.com/800x600/?chickpea,gram,legume,pulse',
    'kidneybeans': 'https://source.unsplash.com/800x600/?kidney,beans,red,legume',
    'pigeonpeas': 'https://source.unsplash.com/800x600/?pigeon,peas,pulse,legume',
    'mothbeans': 'https://source.unsplash.com/800x600/?moth,beans,small,legume',
    'mungbean': 'https://source.unsplash.com/800x600/?mung,bean,green,gram',
    'blackgram': 'https://source.unsplash.com/800x600/?black,gram,lentil,urad',
    'lentil': 'https://source.unsplash.com/800x600/?lentil,dal,pulse,legume',
    'apple': 'https://source.unsplash.com/800x600/?apple,orchard,fruit,tree',
    'orange': 'https://source.unsplash.com/800x600/?orange,citrus,tree,fruit',
    'banana': 'https://source.unsplash.com/800x600/?banana,plantation,tree,tropical',
    'grapes': 'https://source.unsplash.com/800x600/?grapes,vineyard,vine,fruit',
    'coconut': 'https://source.unsplash.com/800x600/?coconut,palm,tree,tropical',
    'cotton': 'https://source.unsplash.com/800x600/?cotton,field,white,agriculture',
    'sugarcane': 'https://source.unsplash.com/800x600/?sugarcane,sugar,cane,field',
    'coffee': 'https://source.unsplash.com/800x600/?coffee,plantation,beans,agriculture',
    'jute': 'https://source.unsplash.com/800x600/?jute,fiber,plant,agriculture',
    'watermelon': 'https://source.unsplash.com/800x600/?watermelon,field,vine,agriculture',
    'muskmelon': 'https://source.unsplash.com/800x600/?muskmelon,cantaloupe,melon,field',
    'papaya': 'https://source.unsplash.com/800x600/?papaya,tree,tropical,fruit',
    'pomegranate': 'https://source.unsplash.com/800x600/?pomegranate,tree,fruit,orchard'
}

def download_image_from_url(url, filename, timeout=30):
    """Download image from a specific URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Save the image
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Verify it's a valid image
        try:
            img = Image.open(filename)
            img.verify()
            return True
        except Exception as e:
            print(f"  ❌ Invalid image file: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return False
            
    except Exception as e:
        print(f"  ❌ Download failed: {e}")
        return False

def download_crop_image(crop_name):
    """Download image for a specific crop"""
    filename = IMAGES_DIR / f"{crop_name}.jpg"
    
    print(f"📥 Downloading image for: {crop_name}")
    
    # Try specific URLs first
    if crop_name in CROP_IMAGE_URLS:
        for i, url in enumerate(CROP_IMAGE_URLS[crop_name]):
            print(f"  Attempt {i + 1}: Specific URL")
            if download_image_from_url(url, filename):
                print(f"  ✅ Successfully downloaded: {filename}")
                return True
            time.sleep(1)
    
    # Try web search URL as fallback
    if crop_name in WEB_SEARCH_URLS:
        print(f"  Fallback: Web search URL")
        if download_image_from_url(WEB_SEARCH_URLS[crop_name], filename):
            print(f"  ✅ Successfully downloaded: {filename}")
            return True
    
    # Create placeholder if all fails
    print(f"  📝 Creating placeholder image...")
    if create_placeholder_image(crop_name, filename):
        return True
    
    return False

def create_placeholder_image(crop_name, filename):
    """Create a placeholder image with crop-specific styling"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crop-specific colors and styling
        crop_themes = {
            'rice': {'bg': '#E8F5E8', 'text': '#2E7D32', 'accent': '#4CAF50'},
            'wheat': {'bg': '#FFF8E1', 'text': '#E65100', 'accent': '#FF9800'},
            'maize': {'bg': '#FFFDE7', 'text': '#F57F17', 'accent': '#FFEB3B'},
            'cotton': {'bg': '#FAFAFA', 'text': '#424242', 'accent': '#9E9E9E'},
            'sugarcane': {'bg': '#E8F5E8', 'text': '#388E3C', 'accent': '#4CAF50'},
            'coffee': {'bg': '#EFEBE9', 'text': '#3E2723', 'accent': '#795548'},
            'apple': {'bg': '#FFEBEE', 'text': '#C62828', 'accent': '#F44336'},
            'orange': {'bg': '#FFF3E0', 'text': '#E65100', 'accent': '#FF9800'},
            'banana': {'bg': '#FFFDE7', 'text': '#F57F17', 'accent': '#FFEB3B'},
            'grapes': {'bg': '#F3E5F5', 'text': '#6A1B9A', 'accent': '#9C27B0'},
            'coconut': {'bg': '#E0F2F1', 'text': '#00695C', 'accent': '#009688'},
            'default': {'bg': '#E8F5E8', 'text': '#2E7D32', 'accent': '#4CAF50'}
        }
        
        theme = crop_themes.get(crop_name, crop_themes['default'])
        
        # Create image
        img = Image.new('RGB', (800, 600), theme['bg'])
        draw = ImageDraw.Draw(img)
        
        # Try to load fonts
        try:
            title_font = ImageFont.truetype("arial.ttf", 56)
            subtitle_font = ImageFont.truetype("arial.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw title
        title_text = crop_name.replace('_', ' ').title()
        bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_height = bbox[3] - bbox[1]
        
        title_x = (800 - title_width) // 2
        title_y = (600 - title_height) // 2 - 40
        
        draw.text((title_x, title_y), title_text, fill=theme['text'], font=title_font)
        
        # Draw subtitle
        subtitle_text = "🌾 Crop Image"
        bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        sub_width = bbox[2] - bbox[0]
        
        subtitle_x = (800 - sub_width) // 2
        subtitle_y = title_y + title_height + 20
        
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill=theme['accent'], font=subtitle_font)
        
        # Draw decorative border
        draw.rectangle([(40, 40), (760, 560)], outline=theme['accent'], width=4)
        
        img.save(filename, 'JPEG', quality=90)
        print(f"  📸 Created themed placeholder: {filename}")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to create placeholder: {e}")
        return False

def main():
    """Main function to download crop images"""
    
    print("🌾 Enhanced KrishiMitra AI - Crop Image Downloader")
    print("=" * 60)
    
    # List of all supported crops
    SUPPORTED_CROPS = [
        'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
        'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
        'papaya', 'watermelon', 'muskmelon', 'apple', 'orange', 
        'coconut', 'banana', 'grapes', 'coffee', 'jute', 'cotton', 
        'wheat', 'sugarcane'
    ]
    
    # Check which images need to be downloaded
    crops_to_download = []
    existing_count = 0
    
    for crop in SUPPORTED_CROPS:
        has_image = False
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            if (IMAGES_DIR / f"{crop}{ext}").exists():
                has_image = True
                existing_count += 1
                break
        
        if not has_image:
            crops_to_download.append(crop)
    
    print(f"📊 Status:")
    print(f"   Total crops: {len(SUPPORTED_CROPS)}")
    print(f"   With images: {existing_count}")
    print(f"   Need download: {len(crops_to_download)}")
    print()
    
    if not crops_to_download:
        print("✅ All crops already have images!")
        user_input = input("🔄 Do you want to re-download ALL images for better quality? (y/N): ").lower()
        if user_input == 'y':
            crops_to_download = SUPPORTED_CROPS
            print(f"🔄 Will re-download all {len(SUPPORTED_CROPS)} crop images")
        else:
            print("No changes made.")
            return
    
    # Option to re-download existing images
    if existing_count > 0:
        user_input = input("🔄 Do you want to re-download ALL images for better quality? (y/N): ").lower()
        if user_input == 'y':
            crops_to_download = SUPPORTED_CROPS
            print(f"🔄 Will re-download all {len(SUPPORTED_CROPS)} crop images")
        else:
            print(f"📥 Will download {len(crops_to_download)} missing images only")
    
    print()
    
    success_count = 0
    
    for i, crop in enumerate(crops_to_download, 1):
        print(f"[{i}/{len(crops_to_download)}] Processing: {crop}")
        
        if download_crop_image(crop):
            success_count += 1
        
        print()
        
        # Rate limiting
        if i < len(crops_to_download):
            time.sleep(2)
    
    print("=" * 60)
    print(f"✅ Download Complete!")
    print(f"   Successfully processed: {success_count}/{len(crops_to_download)} crops")
    
    if success_count == len(crops_to_download):
        print("🎉 All crop images are now available!")
    else:
        print(f"⚠️  {len(crops_to_download) - success_count} crops may need manual attention")
    
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
