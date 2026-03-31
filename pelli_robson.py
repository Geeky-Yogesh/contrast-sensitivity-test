"""
Pelli-Robson chart functionality for contrast sensitivity testing
"""

import streamlit as st
import numpy as np
from datetime import datetime


class PelliRobsonTest:
    def __init__(self, contrast_test):
        self.contrast_test = contrast_test
        self.responses = []
    
    def render_pelli_robson_section(self):
        """Render Pelli-Robson chart test section"""
        st.markdown("### 📊 Pelli-Robson Chart Test")
        st.markdown("""
        **Standard Clinical Test for Contrast Sensitivity**
        - **Viewing Distance**: Exactly 1 meter (3.3 feet)
        - **Chart Size**: 8 rows × 6 columns (48 letters total)
        - **Spatial Frequencies**: 0.5 to 22 cycles/degree
        - **Contrast Levels**: Logarithmic scale (100% to 3.125%)
        
        **Instructions:**
        1. Position yourself exactly 1 meter from screen
        2. Read letters from left to right, top to bottom
        3. Identify the darkest contrast level where you can read letters
        4. Click on letters to record your responses
        """)
        
        # Generate and display Pelli-Robson chart
        chart = self.contrast_test.generate_pelli_robson_chart(1.0)  # Full contrast for visibility
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(chart['image'], width=800, caption="Pelli-Robson Chart - View from 1 meter")
            self.render_interactive_chart(chart)
        
        with col2:
            self.render_responses_panel()
    
    def render_interactive_chart(self, chart):
        """Render interactive chart for letter selection"""
        st.markdown("### 🎯 Click on Letters You Can See")
        
        # Create grid for letter selection
        chart_grid = []
        for row_idx, row in enumerate(chart['chart_data']):
            grid_row = []
            for col_idx, cell in enumerate(row):
                # Make each cell clickable
                cell_key = f"cell_{row_idx}_{col_idx}"
                
                # Determine if this cell should be clickable (based on contrast)
                is_visible = cell['contrast'] >= 0.125  # Only show reasonably visible letters
                
                if is_visible:
                    if st.button(cell['letter'], key=cell_key, help=f"Row {row_idx+1}, Col {col_idx+1}, Contrast: {cell['contrast']:.2f}"):
                        # Store response
                        if 'pelli_responses' not in st.session_state:
                            st.session_state.pelli_responses = []
                        
                        st.session_state.pelli_responses.append({
                            'row': row_idx,
                            'col': col_idx,
                            'letter': cell['letter'],
                            'contrast': cell['contrast'],
                            'correct': True  # Assume correct when clicked
                        })
                        
                        st.success(f"Recorded: {cell['letter']} at position ({row_idx+1}, {col_idx+1})")
                else:
                    # Show very low contrast cells as disabled
                    st.button(cell['letter'], key=f"disabled_{cell_key}", disabled=True, 
                             help=f"Too low contrast to see")
            
                chart_grid.append(grid_row)
    
    def render_responses_panel(self):
        """Render responses panel with results"""
        st.markdown("### 📋 Your Responses")
        
        if 'pelli_responses' in st.session_state and st.session_state.pelli_responses:
            st.write(f"Letters identified: {len(st.session_state.pelli_responses)}")
            
            # Show responses in a table
            response_data = []
            for resp in st.session_state.pelli_responses:
                response_data.append({
                    'Position': f"({resp['row']+1}, {resp['col']+1})",
                    'Letter': resp['letter'],
                    'Contrast': f"{resp['contrast']:.2f}"
                })
            
            if response_data:
                st.dataframe(response_data)
            
            # Calculate sensitivity
            sensitivity = self.contrast_test.calculate_pelli_robson_sensitivity(st.session_state.pelli_responses)
            category, guidance = self.contrast_test.get_pelli_robson_category(sensitivity)
            
            st.markdown(f"### 🎯 Your Contrast Sensitivity: **{sensitivity}**")
            st.markdown(f"**Category: {category}**")
            st.info(guidance)
            
            # Results button
            if st.button("📊 View Detailed Pelli-Robson Results", type="secondary"):
                self.render_detailed_results(sensitivity, category, guidance)
            
            # Reset button
            if st.button("🔄 Reset Pelli-Robson Test", type="secondary"):
                if 'pelli_responses' in st.session_state:
                    del st.session_state.pelli_responses
                st.rerun()
        else:
            st.info("Click on letters in chart to record your responses")
    
    def render_detailed_results(self, sensitivity, category, guidance):
        """Render detailed Pelli-Robson results"""
        st.markdown("### 📈 Pelli-Robson Test Results")
        
        # Create comprehensive results display
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Contrast Sensitivity", sensitivity)
            st.metric("Letters Identified", len(st.session_state.pelli_responses))
            st.metric("Best Position", f"Row {min([r['row'] for r in st.session_state.pelli_responses])+1}")
        
        with col2:
            # Show contrast sensitivity scale
            st.markdown("""
            **Contrast Sensitivity Scale:**
            - 50%+: Excellent (Outstanding)
            - 25-50%: Very Good (Above average)
            - 12.5-25%: Good (Normal)
            - 6.25-12.5%: Fair (Below average)
            - 3.125-6.25%: Poor (Consult doctor)
            - <3.125%: Very Poor (Immediate exam)
            """)
        
        st.markdown(f"**Clinical Interpretation:** {guidance}")
        
        # Export option
        if st.button("📄 Download Pelli-Robson Results"):
            self.generate_download_report(sensitivity, category, guidance)
    
    def generate_download_report(self, sensitivity, category, guidance):
        """Generate downloadable text report"""
        report_text = f"""
PELLI-ROBSON CONTRAST SENSITIVITY TEST REPORT
=============================================

Test Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Test Type: Pelli-Robson Chart
Viewing Distance: 1 meter (standard)

RESULTS:
--------
Contrast Sensitivity: {sensitivity}
Category: {category}
Letters Identified: {len(st.session_state.pelli_responses)} out of 48
Best Position: Row {min([r['row'] for r in st.session_state.pelli_responses])+1}

DETAILED RESPONSES:
------------------
"""
        
        for resp in st.session_state.pelli_responses:
            report_text += f"""
Position ({resp['row']+1}, {resp['col']+1}): Letter {resp['letter']}
Contrast Level: {resp['contrast']:.2f}%
"""
        
        report_text += f"""

CLINICAL NOTES:
--------------
{guidance}

This test follows standard Pelli-Robson protocol for contrast sensitivity assessment.
Results should be discussed with an eye care professional for proper interpretation.
"""
        
        st.download_button(
            label="💾 Download Pelli-Robson Report",
            data=report_text,
            file_name=f"pelli_robson_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
