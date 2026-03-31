import streamlit as st

class StandardContrastTest:
    def __init__(self, test_engine):
        self.test = test_engine

    def render_standard_test(self, test_eye="Both", test_distance=10):
        st.subheader(f"Level {st.session_state.contrast_current_level + 1} - {test_eye} Eye")
        pattern = self.test.get_current_pattern()
        
        if not pattern:
            st.error("Error loading pattern.")
            return

        cols = st.columns(3)
        for i, img in enumerate(pattern['images']):
            cols[i].image(img, use_container_width=True)

        user_input = st.text_input("Enter the 3 letters:", key=f"inp_{st.session_state.contrast_current_level}").upper().strip()

        if st.button("Submit Answer"):
            if len(user_input) == 3:
                actual = "".join(pattern['letters'])
                correct = sum(1 for u, a in zip(user_input, actual) if u == a)
                
                st.session_state.contrast_responses.append({
                    'contrast': pattern['contrast_percent'],
                    'passed': correct >= 2
                })

                if correct >= 2:
                    st.success(f"Passed {pattern['contrast_percent']}% contrast!")
                    self.test.next_level()
                    st.rerun()
                else:
                    st.error("Test ended due to incorrect response.")
                    st.session_state.contrast_test_started = False
                    st.rerun()
            else:
                st.warning("Please enter 3 letters.")