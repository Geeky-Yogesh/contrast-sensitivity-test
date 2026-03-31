import streamlit as st
from contrast_sensitivity_test import ContrastSensitivityTest
from webcam_handler import WebcamHandler
from pelli_robson import PelliRobsonTest
from standard_test import StandardContrastTest
import cv2
from datetime import datetime

def main():
    st.set_page_config(page_title="VisionTestPro", layout="wide")
    
    # INITIALIZATION
    if 'test_engine' not in st.session_state:
        st.session_state.test_engine = ContrastSensitivityTest()
    if 'webcam_handler' not in st.session_state:
        st.session_state.webcam_handler = WebcamHandler()
    if 'contrast_test_started' not in st.session_state:
        st.session_state.contrast_test_started = False
    if 'contrast_current_level' not in st.session_state:
        st.session_state.contrast_current_level = 0
    if 'contrast_responses' not in st.session_state:
        st.session_state.contrast_responses = []
    if 'current_contrast_pattern' not in st.session_state:
        st.session_state.current_contrast_pattern = None
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False

    test = st.session_state.test_engine
    handler = st.session_state.webcam_handler
    
    st.title("👁️ Professional Contrast Sensitivity Test")

    with st.sidebar:
        st.header("Settings")
        mode = st.radio("Test Mode", ["Standard (10ft)", "Pelli-Robson (1m)"])
        web_container = st.empty()
        
        if st.button("Start Webcam"):
            handler.initialize_webcam()
            st.rerun()
        if st.button("Stop Webcam"):
            handler.release_webcam()
            st.rerun()

    if st.session_state.webcam_active:
        frame, dist = handler.get_frame(test)
        if frame is not None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            web_container.image(rgb, use_container_width=True)
            if dist and dist['detected']:
                st.sidebar.metric("Distance", f"{dist['distance_feet']:.1f} ft")

    if not st.session_state.contrast_test_started:
        st.write("### Instructions")
        st.write("1. Set distance. 2. Ensure high brightness. 3. Cover one eye if needed.")
        if st.button("🚀 Start Test", type="primary"):
            test.start_test("Both")
            st.rerun()
    else:
        if mode == "Standard (10ft)":
            StandardContrastTest(test).render_standard_test("Both", 10)
        else:
            PelliRobsonTest(test).render_pelli_robson_section()
        
        # Show results if test is completed
        if not st.session_state.contrast_test_started and st.session_state.contrast_responses:
            st.markdown("---")
            st.markdown("### 🎯 Test Results & Evaluation")
            
            # Calculate performance metrics
            total_levels = len(st.session_state.contrast_responses)
            passed_levels = sum(1 for r in st.session_state.contrast_responses if r.get('passed', False))
            pass_rate = (passed_levels / total_levels) * 100 if total_levels > 0 else 0
            
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Levels", total_levels)
            with col2:
                st.metric("Levels Passed", passed_levels)
            with col3:
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
            with col4:
                # Calculate best contrast level achieved
                best_contrast = None
                for response in st.session_state.contrast_responses:
                    if response.get('passed', False):
                        best_contrast = response.get('contrast', 0)
                if best_contrast is not None:
                    st.metric("Best Contrast", f"{best_contrast}%")
                else:
                    st.metric("Best Contrast", "None")
            
            # Detailed results table
            st.markdown("#### 📊 Detailed Performance")
            results_data = []
            for i, response in enumerate(st.session_state.contrast_responses):
                status = "✅ PASS" if response.get('passed', False) else "❌ FAIL"
                results_data.append({
                    "Level": i + 1,
                    "Contrast %": f"{response.get('contrast', 'N/A')}%",
                    "Result": status
                })
            
            if results_data:
                st.dataframe(results_data, use_container_width=True)
            
            # Clinical interpretation
            st.markdown("#### 🏥 Clinical Interpretation")
            if pass_rate >= 80:
                st.success("🎉 **Excellent Contrast Sensitivity**")
                st.info("Your contrast sensitivity is well within normal range. Keep maintaining good eye health!")
            elif pass_rate >= 60:
                st.info("✅ **Good Contrast Sensitivity**")
                st.info("Your contrast sensitivity is within expected range for your age group.")
            elif pass_rate >= 40:
                st.warning("⚠️ **Fair Contrast Sensitivity**")
                st.warning("Your contrast sensitivity is slightly below average. Consider regular eye check-ups.")
            else:
                st.error("🚨 **Poor Contrast Sensitivity**")
                st.error("Your contrast sensitivity is below normal range. Consider consulting an eye care professional.")
            
            # Recommendations
            st.markdown("#### 💡 Recommendations")
            if pass_rate >= 60:
                st.markdown("""
                - Continue regular eye examinations
                - Protect eyes from UV exposure
                - Maintain good lighting for reading
                - Monitor for any changes over time
                """)
            else:
                st.markdown("""
                - Schedule comprehensive eye exam
                - Discuss contrast sensitivity issues with your doctor
                - Improve lighting in your environment
                - Use high-contrast settings on digital devices
                """)
            
            # Export results
            st.markdown("#### 📤 Export Results")
            if st.button("📄 Download Test Report"):
                report_text = f"""
CONTRAST SENSITIVITY TEST REPORT
================================

Test Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Test Mode: {mode}
Total Levels: {total_levels}
Levels Passed: {passed_levels}
Pass Rate: {pass_rate:.1f}%

DETAILED RESULTS:
----------------
"""
                for i, response in enumerate(st.session_state.contrast_responses):
                    status = "PASS" if response.get('passed', False) else "FAIL"
                    report_text += f"Level {i+1}: {response.get('contrast', 'N/A')}% contrast - {status}\n"
                
                report_text += f"""
CLINICAL INTERPRETATION:
------------------------
Pass Rate: {pass_rate:.1f}%
"""
                if pass_rate >= 80:
                    report_text += "Result: Excellent contrast sensitivity\n"
                elif pass_rate >= 60:
                    report_text += "Result: Good contrast sensitivity\n"
                elif pass_rate >= 40:
                    report_text += "Result: Fair contrast sensitivity\n"
                else:
                    report_text += "Result: Poor contrast sensitivity\n"
                
                st.download_button(
                    label="💾 Download Report",
                    data=report_text,
                    file_name=f"contrast_sensitivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
            # Reset button
            st.markdown("#### 🔄 Start New Test")
            if st.button("Start New Test", type="primary"):
                # Reset all session state
                st.session_state.contrast_test_started = False
                st.session_state.contrast_current_level = 0
                st.session_state.contrast_responses = []
                st.session_state.current_contrast_pattern = None
                st.rerun()

if __name__ == "__main__":
    main()