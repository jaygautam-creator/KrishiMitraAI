#!/usr/bin/env python3
"""
Simple test to demonstrate pincode-based crop recommendations
Run this to verify that different pincodes give different crop recommendations
"""

import sys
import os
sys.path.append('app')

from recommendation import get_crop_recommendations

def test_pincode_recommendations():
    """Test different pincodes to show they give different recommendations"""
    
    # Test parameters
    model_prediction = "rice"
    land_area = 1.0
    budget = 50000
    
    # Test different pincodes
    test_pincodes = {
        "110001": "Delhi (North India)",
        "400001": "Mumbai (West India)", 
        "560001": "Bangalore (South India)",
        "700001": "Kolkata (East India)",
        "395007": "Random PIN (West India)",
        "600034": "Chennai (South India)"
    }
    
    print("=" * 60)
    print("🌾 PINCODE-BASED CROP RECOMMENDATION TEST")
    print("=" * 60)
    print()
    
    results = {}
    
    for pincode, location in test_pincodes.items():
        print(f"📍 Testing PIN {pincode} - {location}")
        print("-" * 50)
        
        try:
            recommendations = get_crop_recommendations(
                model_prediction, land_area, budget, 
                pincode=pincode, api_key=None
            )
            
            if recommendations:
                top_5_crops = [rec['name'] for rec in recommendations[:5]]
                results[pincode] = top_5_crops
                
                print(f"✅ Top 5 recommendations: {', '.join(top_5_crops)}")
                print(f"   Regional suitability scores shown in debug output above")
            else:
                print("❌ No recommendations generated")
                results[pincode] = []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results[pincode] = []
        
        print()
    
    # Summary comparison
    print("=" * 60)
    print("📊 SUMMARY COMPARISON")
    print("=" * 60)
    
    all_unique = True
    for pincode, crops in results.items():
        location = test_pincodes[pincode]
        if crops:
            print(f"{pincode} ({location}): {', '.join(crops[:3])}")
        else:
            print(f"{pincode} ({location}): No results")
    
    print()
    
    # Check if results are different
    crop_lists = [tuple(crops[:3]) for crops in results.values() if crops]
    unique_lists = set(crop_lists)
    
    if len(unique_lists) > 1:
        print("✅ SUCCESS: Different pincodes give DIFFERENT crop recommendations!")
        print(f"   Found {len(unique_lists)} unique recommendation patterns")
    else:
        print("❌ ISSUE: All pincodes giving same recommendations")
        print("   This suggests there might be a problem with pincode processing")
    
    print()
    print("=" * 60)
    print("To use this in your Streamlit app:")
    print("1. Run: streamlit run app/app.py")  
    print("2. Enter different pincodes and see different crops!")
    print("=" * 60)

if __name__ == "__main__":
    test_pincode_recommendations()
