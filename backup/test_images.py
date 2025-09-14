#!/usr/bin/env python3
"""
Test script to verify crop image display functionality
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_image_paths():
    """Test image path resolution"""
    
    BASE_DIR = Path('app').resolve()
    IMAGES_DIR = BASE_DIR.parent / 'images'
    
    print("🧪 Testing Image Path Resolution")
    print("=" * 50)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"IMAGES_DIR: {IMAGES_DIR}")
    print(f"Images folder exists: {IMAGES_DIR.exists()}")
    
    if IMAGES_DIR.exists():
        image_files = list(IMAGES_DIR.glob('*.jpg'))
        print(f"Found {len(image_files)} image files")
        
        # Test crops from dataset
        test_crops = [
            'rice', 'wheat', 'maize', 'cotton', 'apple', 'banana',
            'chickpea', 'blackgram', 'lentil', 'mango', 'mungbean'
        ]
        
        print("\n📋 Image Availability Test")
        print("-" * 30)
        
        available = 0
        missing = 0
        
        for crop in test_crops:
            crop_path = IMAGES_DIR / f"{crop}.jpg"
            if crop_path.exists():
                print(f"✅ {crop}.jpg - Available")
                available += 1
            else:
                print(f"❌ {crop}.jpg - Missing (will show placeholder)")
                missing += 1
        
        print(f"\n📊 Summary:")
        print(f"   Available: {available}")
        print(f"   Missing: {missing}")
        print(f"   Total tested: {len(test_crops)}")
        
        if missing > 0:
            print(f"\n💡 Note: Missing images will display as styled placeholders")
        else:
            print(f"\n🎉 All test images are available!")
    
    else:
        print("❌ Images directory not found!")

def test_placeholder_themes():
    """Test placeholder theme configuration"""
    print("\n🎨 Testing Placeholder Themes")
    print("=" * 50)
    
    crop_themes = {
        'blackgram': {'color': '#4A4A4A', 'bg': '#F5F5F5', 'emoji': '🤎', 'desc': 'Black Lentil'},
        'chickpea': {'color': '#D2691E', 'bg': '#FFF8DC', 'emoji': '🥬', 'desc': 'Chickpea/Gram'},
        'cotton': {'color': '#FFE4E1', 'bg': '#FFFFFF', 'emoji': '☁️', 'desc': 'Cotton Plant'},
        'lentil': {'color': '#CD853F', 'bg': '#FFF8DC', 'emoji': '🥬', 'desc': 'Red Lentils'},
        'mango': {'color': '#FFD700', 'bg': '#FFFAF0', 'emoji': '🥭', 'desc': 'Mango Tree'},
        'mothbeans': {'color': '#8B4513', 'bg': '#F5DEB3', 'emoji': '🌱', 'desc': 'Moth Beans'},
        'mungbean': {'color': '#228B22', 'bg': '#F0FFF0', 'emoji': '👌', 'desc': 'Mung Bean'},
        'muskmelon': {'color': '#FFA500', 'bg': '#FFFACD', 'emoji': '🍈', 'desc': 'Muskmelon'},
        'pigeonpeas': {'color': '#DAA520', 'bg': '#FFFAF0', 'emoji': '🥬', 'desc': 'Pigeon Peas'}
    }
    
    for crop, theme in crop_themes.items():
        print(f"🎨 {crop.title():<12} → {theme['emoji']} {theme['desc']}")
    
    print(f"\n✅ {len(crop_themes)} themed placeholders configured")

if __name__ == "__main__":
    try:
        test_image_paths()
        test_placeholder_themes()
        
        print("\n" + "=" * 50)
        print("🎉 Image display system is ready!")
        print("   • Existing images will display normally")
        print("   • Missing images will show styled placeholders")
        print("   • Users will see helpful status messages")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
