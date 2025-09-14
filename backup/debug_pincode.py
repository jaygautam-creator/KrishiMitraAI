#!/usr/bin/env python3
"""
Debug script to test pincode-based recommendations
Run this to verify what crops are actually returned for different pincodes
"""

import sys
import os
sys.path.append('app')

def test_pincode_recommendations():
    """Test different pincodes and show exactly what's returned"""
    
    # Import fresh each time
    from recommendation import get_crop_recommendations
    
    test_pincodes = {
        "560001": "Bangalore (should show: coffee, banana, coconut)",
        "110001": "Delhi (should show: maize, lentil, cotton)",
        "400001": "Mumbai (should show: cotton, rice, mungbean)",
    }
    
    print("=" * 80)
    print("🐛 DEBUG: Testing Pincode-Based Recommendations")
    print("=" * 80)
    
    for pincode, expected in test_pincodes.items():
        print(f"\n📍 Testing PIN {pincode} - {expected}")
        print("-" * 60)
        
        try:
            # Get fresh recommendations
            recommendations = get_crop_recommendations(
                model_prediction="PINCODE_BASED",
                land_area=1.0,
                budget=50000,
                pincode=pincode,
                api_key=None
            )
            
            if recommendations:
                print(f"✅ SUCCESS: Got {len(recommendations)} recommendations")
                print("🎯 TOP 5 RESULTS:")
                for i, rec in enumerate(recommendations[:5], 1):
                    name = rec.get('name', 'Unknown')
                    score = rec.get('debug_score', 'N/A')
                    print(f"  {i}. {name} (Score: {score:.2f})")
                
                # Check if results match expectations
                top_3 = [rec['name'] for rec in recommendations[:3]]
                print(f"📋 Top 3: {', '.join(top_3)}")
                
            else:
                print("❌ FAILED: No recommendations returned")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 80)
    print("🔍 ANALYSIS:")
    print("If you see the same crops for different pincodes, there's a caching issue.")
    print("If you see different crops, the backend is working correctly.")
    print("=" * 80)

if __name__ == "__main__":
    test_pincode_recommendations()
