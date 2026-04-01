import streamlit as st

class PelliRobsonTest:
    def __init__(self, test_engine):
        self.contrast_test = test_engine

    def render_pelli_robson_section(self):
        st.header("Pelli-Robson Digital Chart")
        
        # Ensure chart is generated once and stored in session state
        if 'pr_chart' not in st.session_state:
            st.session_state.pr_chart = self.contrast_test.generate_pelli_robson_chart()
        
        st.image(st.session_state.pr_chart['image'], caption="View from 1 meter (approx 3.3 ft)")
        
        # Add proper Pelli-Robson instructions
        st.markdown("### 📋 How to Take the Test")
        st.info("""
        **Pelli-Robson Test Instructions:**
        1. **Read the letters** from left to right, top to bottom
        2. **Letters are grouped** - each group of 3 letters has the same contrast
        3. **Find the last group** where you can read at least 2 out of 3 letters
        4. **Click the button** for that group to get your score
        
        **Scoring:** You need to read 2/3 letters in a group for it to count!
        """)
        
        data = st.session_state.pr_chart['data']
        
        # Group letters by LogCS value for scoring
        groups = {}
        for item in data:
            log_cs = item['log_cs']
            if log_cs not in groups:
                groups[log_cs] = []
            groups[log_cs].append(item['letter'])
        
        st.write("Click the button corresponding to the last group where you could read at least 2 letters:")
        
        # Create buttons for each LogCS group
        cols = st.columns(4)
        group_keys = sorted(groups.keys())
        
        for i, log_cs in enumerate(group_keys):
            col_idx = i % 4
            letters = groups[log_cs]
            letters_str = ' '.join(letters)
            
            if cols[col_idx].button(f"Group {i+1}: {letters_str} (LogCS {log_cs})", key=f"pr_btn_{i}"):
                category, guidance = self.contrast_test.get_clinical_category(log_cs)
                
                st.divider()
                st.metric("Your Log Contrast Sensitivity (LogCS)", log_cs)
                st.subheader(f"Result: {category}")
                st.info(guidance)
                
                # Show detailed results
                st.markdown("### 📊 Test Results")
                st.markdown(f"""
                **Your Score:** LogCS {log_cs}
                
                **Letters in Group:** {letters_str}
                
                **Clinical Interpretation:** {category}
                
                **Recommendation:** {guidance}
                """)