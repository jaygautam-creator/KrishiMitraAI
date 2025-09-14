#!/usr/bin/env python3
"""
Simple Streamlit test app to demonstrate pincode-based crop recommendations
Run with: streamlit run pincode_test.py
"""

import streamlit as st
import sys
import os

# Add app directory to path
sys.path.append('app')

from recommendation import get_crop_recommendations

# Page configuration
st.set_page_config(
    page_title="Pincode Test - KrishiMitra AI",
    page_icon="🌾",
    layout="wide"
)

st.title("🌾 Pincode-Based Crop Recommendation Test")
st.markdown("**This is a test page to verify that different pincodes give different crop recommendations**")

# Create columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Test Parameters")
    pincode = st.text_input("Enter Pincode:", value="110001", max_chars=6)
    land_area = st.number_input("Land Area (acres):", value=1.0, min_value=0.1, max_value=100.0, step=0.1)
    budget = st.number_input("Budget (₹):", value=50000, min_value=1000, max_value=1000000, step=1000)

with col2:
    st.subheader("🧪 Quick Test Buttons")
    test_cols = st.columns(2)
    
    with test_cols[0]:
        if st.button("🏛️ Test Delhi (110001)", key="delhi"):
            pincode = "110001"
            st.rerun()
            
        if st.button("🏭 Test Mumbai (400001)", key="mumbai"):  
            pincode = "400001"
            st.rerun()
            
    with test_cols[1]:
        if st.button("🌆 Test Bangalore (560001)", key="bangalore"):
            pincode = "560001" 
            st.rerun()
            
        if st.button("🌉 Test Kolkata (700001)", key="kolkata"):
            pincode = "700001"
            st.rerun()

# Process button
if st.button("🌱 Get Recommendations", type="primary"):
    if pincode and len(pincode) == 6 and pincode.isdigit():
        
        st.markdown("---")
        
        # Clear any caching
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
            
        with st.spinner(f"Getting recommendations for PIN {pincode}..."):
            
            try:
                # Get recommendations using PINCODE_BASED mode
                recommendations = get_crop_recommendations(
                    model_prediction="PINCODE_BASED",  # Pure pincode mode
                    land_area=land_area,
                    budget=budget,
                    pincode=pincode,
                    api_key=None  # Use estimated weather
                )
                
                if recommendations:
                    # Show results
                    st.success(f"✅ Found {len(recommendations)} recommendations for PIN {pincode}")
                    
                    # Show top 5 in a nice format
                    st.subheader(f"🎯 Top Recommendations for PIN {pincode}")
                    
                    for i, rec in enumerate(recommendations[:5], 1):
                        crop_name = rec.get('name', 'Unknown')
                        score = rec.get('debug_score', 'N/A')
                        roi = rec.get('roi', 0)
                        
                        with st.expander(f"{i}. {crop_name} (Score: {score:.2f})", expanded=(i<=3)):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.metric("Crop Name", crop_name)
                                st.metric("Suitability Score", f"{score:.2f}")
                                
                            with col_b:
                                st.metric("Expected ROI", f"₹{roi:,.0f}")
                                st.metric("For Pincode", pincode)
                                
                            # Weather impact
                            weather_impact = rec.get('weather_impact', {})
                            if weather_impact:
                                st.write("**🌤️ Weather Suitability:**")
                                for factor, value in weather_impact.items():
                                    st.write(f"• **{factor}:** {value}")
                    
                    # Show quick comparison
                    st.subheader("📊 Quick Summary")
                    top_5_names = [rec['name'] for rec in recommendations[:5]]
                    st.info(f"**PIN {pincode} Top 5:** {', '.join(top_5_names)}")
                    
                else:
                    st.error(f"❌ No recommendations found for PIN {pincode}")
                    
            except Exception as e:
                st.error(f"❌ Error getting recommendations: {e}")
                st.exception(e)
    else:
        st.error("❌ Please enter a valid 6-digit PIN code")

# Instructions
st.markdown("---")
st.subheader("📋 How to Test")
st.markdown("""
1. **Try different pincodes** using the buttons above or enter manually
2. **Look for different crop names** in the results
3. **Compare suitability scores** - different pincodes should show different scores
4. **Expected results:**
   - **110001 (Delhi):** Should show Maize, Lentil, Cotton
   - **400001 (Mumbai):** Should show Cotton, Rice, Mungbean  
   - **560001 (Bangalore):** Should show Coffee, Banana, Coconut
   - **700001 (Kolkata):** Should show Rice, Jute, Lentil
""")

# Footer
st.markdown("---")
st.caption("🌾 This is a test interface for KrishiMitra AI pincode-based crop recommendations")
