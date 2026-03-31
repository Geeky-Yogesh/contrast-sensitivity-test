import streamlit as st

class PelliRobsonTest:
    def __init__(self, test_engine):
        self.contrast_test = test_engine

    def render_pelli_robson_section(self):
        st.header("Pelli-Robson Digital Chart")
        
        # Ensure chart is generated once and stored in session state
        if 'pr_chart' not in st.session_state:
            # FIX: Removed (1.0) from the function call below
            st.session_state.pr_chart = self.contrast_test.generate_pelli_robson_chart()
        
        st.image(st.session_state.pr_chart['image'], caption="View from 1 meter (approx 3.3 ft)")
        
        data = st.session_state.pr_chart['data']
        st.write("Click the button corresponding to the last letter you can clearly read:")
        
        # Create a grid of buttons for scoring
        cols = st.columns(4)
        for i, item in enumerate(data):
            col_idx = i % 4
            # Each button represents a letter on the chart with its specific LogCS value
            if cols[col_idx].button(f"Point {i+1} (LogCS {item['log_cs']})", key=f"pr_btn_{i}"):
                log_score = item['log_cs']
                category, guidance = self.contrast_test.get_clinical_category(log_score)
                
                st.divider()
                st.metric("Your Log Contrast Sensitivity (LogCS)", log_score)
                st.subheader(f"Result: {category}")
                st.info(guidance)