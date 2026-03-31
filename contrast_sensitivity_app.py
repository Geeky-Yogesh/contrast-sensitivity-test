"""
Professional Contrast Sensitivity Test Application
Complete, production-ready implementation
"""

import streamlit as st
import cv2
import numpy as np
import random
from PIL import Image
from datetime import datetime
import os

class ContrastSensitivityTest:
    """Main contrast sensitivity testing engine"""
    
    def __init__(self):
        # Professional contrast levels (Weber contrast)
        self.contrast_levels = [0.20, 0.10, 0.05, 0.025, 0.0125, 0.01, 0.0075, 0.005]
        self.pattern_size = 200
        
    def start_test(self, test_eye="Both"):
        """Initialize test session"""
        st.session_state.contrast_test_started = True
        st.session_state.contrast_current_level = 0
        st.session_state.contrast_test_eye = test_eye
        st.session_state.contrast_responses = []
        st.session_state.current_contrast_pattern = self.generate_contrast_pattern()
        
    def generate_contrast_pattern(self, contrast=None):
        """Generate letter pattern with specified contrast"""
        if contrast is None:
            idx = st.session_state.contrast_current_level
            contrast = self.contrast_levels[idx]
        
        # Generate random letters
        letters = random.sample('ABCDEFGHJKLMNOPRSTUVXYZ', 3)
        bg_val = 240 
        text_val = int(bg_val * (1.0 - contrast))  # Weber contrast calculation
        
        letter_images = []
        for letter in letters:
            img = np.ones((self.pattern_size, self.pattern_size, 3), dtype=np.uint8) * bg_val
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.0
            thickness = 5
            
            (w, h), _ = cv2.getTextSize(letter, font, font_scale, thickness)
            cv2.putText(img, letter, ((self.pattern_size-w)//2, (self.pattern_size+h)//2), 
                        font, font_scale, (text_val, text_val, text_val), thickness)
            
            # Convert to RGB PIL for Streamlit
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            letter_images.append(Image.fromarray(img_rgb))
        
        return {
            'images': letter_images,
            'letters': letters,
            'contrast_percent': round(contrast * 100, 2)
        }
    
    def get_current_pattern(self):
        """Get current pattern from session state"""
        return st.session_state.get('current_contrast_pattern')
    
    def next_level(self):
        """Advance to next level or end test"""
        st.session_state.contrast_current_level += 1
        if st.session_state.contrast_current_level < len(self.contrast_levels):
            st.session_state.current_contrast_pattern = self.generate_contrast_pattern()
        else:
            st.session_state.contrast_test_started = False
    
    def generate_pelli_robson_chart(self):
        """Generate clinical Pelli-Robson chart"""
        chart_width, chart_height = 900, 600
        img = np.ones((chart_height, chart_width, 3), dtype=np.uint8) * 240
        
        # Standard clinical LogCS steps
        log_cs_steps = [0.00, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90, 1.05, 1.20, 1.35, 1.50, 1.65]
        chart_data = []
        
        for i, log_val in enumerate(log_cs_steps):
            contrast = 1 / (10**log_val)
            text_val = int(240 * (1.0 - contrast))
            letter = random.choice('NHRSDKV')
            row, col = i // 3, i % 3
            x, y = col * 300 + 150, row * 150 + 100
            cv2.putText(img, letter, (x-40, y+40), cv2.FONT_HERSHEY_SIMPLEX, 3, 
                        (text_val, text_val, text_val), 8)
            chart_data.append({'letter': letter, 'log_cs': log_val})
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return {'image': Image.fromarray(img_rgb), 'data': chart_data}
    
    def get_clinical_category(self, log_cs):
        """Get clinical interpretation based on LogCS value"""
        if log_cs >= 1.65:
            return "Normal", "🟢 Excellent contrast sensitivity."
        elif log_cs >= 1.35:
            return "Fair", "🟡 Slightly reduced. Consider checkup."
        else:
            return "Abnormal", "🔴 Significant contrast loss. Consult a doctor."
    
    def calculate_distance_from_face(self, frame):
        """Calculate distance from face detection"""
        try:
            xml_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(xml_path)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda r: r[2]*r[3])
                # Simple distance estimation
                dist_ft = (15 * 500) / (w * 30.48) 
                return {'detected': True, 'distance_feet': dist_ft}
        except:
            pass
        return {'detected': False}

class WebcamHandler:
    """Handle webcam operations"""
    
    def initialize_webcam(self):
        """Initialize webcam for distance monitoring"""
        if st.session_state.get('webcam_cap') is None:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                st.session_state.webcam_cap = cap
                st.session_state.webcam_active = True
                return True
        return False
    
    def release_webcam(self):
        """Release webcam resources"""
        if st.session_state.get('webcam_cap'):
            st.session_state.webcam_cap.release()
            st.session_state.webcam_cap = None
            st.session_state.webcam_active = False
    
    def get_frame(self, test_engine):
        """Get frame with distance estimation"""
        cap = st.session_state.get('webcam_cap')
        if not cap:
            return None, None
        
        ret, frame = cap.read()
        if not ret:
            return None, None
        
        frame = cv2.flip(frame, 1)
        dist = test_engine.calculate_distance_from_face(frame)
        return frame, dist

class StandardContrastTest:
    """Standard contrast sensitivity test implementation"""
    
    def __init__(self, test_engine):
        self.test = test_engine
    
    def render_standard_test(self, test_eye="Both", test_distance=10):
        """Render standard test interface"""
        st.subheader(f"Level {st.session_state.contrast_current_level + 1} - {test_eye} Eye")
        pattern = self.test.get_current_pattern()
        
        if not pattern:
            st.error("Error loading pattern.")
            return
        
        # Display letter patterns
        cols = st.columns(3)
        for i, img in enumerate(pattern['images']):
            cols[i].image(img, width='stretch')
        
        # User input
        user_input = st.text_input(
            "Enter the 3 letters you see:", 
            key=f"inp_{st.session_state.contrast_current_level}"
        ).upper().strip()
        
        # Submit button
        if st.button("Submit Answer", type="primary"):
            if len(user_input) == 3:
                actual = "".join(pattern['letters'])
                correct = sum(1 for u, a in zip(user_input, actual) if u == a)
                
                # Store response
                st.session_state.contrast_responses.append({
                    'contrast': pattern['contrast_percent'],
                    'passed': correct >= 2,
                    'correct': correct,
                    'total': 3,
                    'user_input': user_input,
                    'actual': actual
                })
                
                if correct >= 2:
                    st.success(f"✅ Correct! {correct}/3 letters right.")
                    st.info(f"Passed {pattern['contrast_percent']}% contrast level!")
                    self.test.next_level()
                    st.rerun()
                else:
                    st.error(f"❌ Only {correct}/3 letters correct. Test ended.")
                    st.session_state.contrast_test_started = False
                    st.rerun()
            else:
                st.warning("Please enter exactly 3 letters.")

class PelliRobsonTest:
    """Pelli-Robson clinical test implementation"""
    
    def __init__(self, test_engine):
        self.test = test_engine
    
    def render_pelli_robson_section(self):
        """Render Pelli-Robson test interface"""
        st.header("📊 Pelli-Robson Clinical Chart")
        st.markdown("""
        **Standard Clinical Test for Contrast Sensitivity**
        - **Viewing Distance**: 1 meter (3.3 feet)
        - **Test Protocol**: Identify the last letter you can clearly read
        """)
        
        # Generate chart once per session
        if 'pr_chart' not in st.session_state:
            st.session_state.pr_chart = self.test.generate_pelli_robson_chart()
        
        # Display chart
        st.image(st.session_state.pr_chart['image'], 
                caption="View from 1 meter (approx 3.3 ft)", 
                width='stretch')
        
        st.write("### Click the button corresponding to the last letter you can clearly read:")
        
        # Create interactive buttons
        data = st.session_state.pr_chart['data']
        cols = st.columns(4)
        
        for i, item in enumerate(data):
            col_idx = i % 4
            with cols[col_idx]:
                if st.button(f"Point {i+1} (LogCS {item['log_cs']})", key=f"pr_btn_{i}"):
                    log_score = item['log_cs']
                    category, guidance = self.test.get_clinical_category(log_score)
                    
                    # Store result
                    if 'pelli_robson_result' not in st.session_state:
                        st.session_state.pelli_robson_result = {}
                    st.session_state.pelli_robson_result = {
                        'log_cs': log_score,
                        'category': category,
                        'guidance': guidance
                    }
                    
                    # Display results
                    st.divider()
                    st.metric("Your Log Contrast Sensitivity (LogCS)", log_score)
                    st.subheader(f"Result: {category}")
                    st.info(guidance)
                    
                    # End test
                    st.session_state.contrast_test_started = False

def render_results_evaluation():
    """Render comprehensive results and evaluation"""
    if not st.session_state.contrast_responses:
        return
    
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
        best_contrast = None
        for response in st.session_state.contrast_responses:
            if response.get('passed', False):
                best_contrast = response.get('contrast', 0)
        st.metric("Best Contrast", f"{best_contrast}%" if best_contrast else "None")
    
    # Detailed results table
    st.markdown("#### 📊 Detailed Performance")
    results_data = []
    for i, response in enumerate(st.session_state.contrast_responses):
        status = "✅ PASS" if response.get('passed', False) else "❌ FAIL"
        results_data.append({
            "Level": i + 1,
            "Contrast %": f"{response.get('contrast', 'N/A')}%",
            "Your Answer": response.get('user_input', 'N/A'),
            "Correct": response.get('actual', 'N/A'),
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
        report_text = generate_test_report(pass_rate, total_levels, passed_levels)
        st.download_button(
            label="💾 Download Report",
            data=report_text,
            file_name=f"contrast_sensitivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def generate_test_report(pass_rate, total_levels, passed_levels):
    """Generate comprehensive test report"""
    report_text = f"""
CONTRAST SENSITIVITY TEST REPORT
================================

Test Date: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
Test Type: Contrast Sensitivity Assessment
Total Levels: {total_levels}
Levels Passed: {passed_levels}
Pass Rate: {pass_rate:.1f}%

DETAILED RESULTS:
----------------
"""
    
    for i, response in enumerate(st.session_state.contrast_responses):
        status = "PASS" if response.get('passed', False) else "FAIL"
        report_text += f"Level {i+1}: {response.get('contrast', 'N/A')}% contrast - {status}\n"
        report_text += f"  Your Answer: {response.get('user_input', 'N/A')}\n"
        report_text += f"  Correct Answer: {response.get('actual', 'N/A')}\n\n"
    
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
    
    report_text += f"""
RECOMMENDATIONS:
---------------
"""
    
    if pass_rate >= 60:
        report_text += """
- Continue regular eye examinations
- Protect eyes from UV exposure
- Maintain good lighting for reading
- Monitor for any changes over time
"""
    else:
        report_text += """
- Schedule comprehensive eye exam
- Discuss contrast sensitivity issues with your doctor
- Improve lighting in your environment
- Use high-contrast settings on digital devices
"""
    
    report_text += """

NOTES:
------
This test measures your ability to detect letters at different contrast levels.
Results should be discussed with an eye care professional for proper interpretation.
"""
    
    return report_text

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Professional Contrast Sensitivity Test",
        page_icon="👁️",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    test = st.session_state.test_engine
    handler = st.session_state.webcam_handler
    
    st.title("👁️ Professional Contrast Sensitivity Test")
    st.markdown("---")
    
    # Sidebar configuration
    render_sidebar(handler)
    
    # Main content area
    if not st.session_state.contrast_test_started:
        render_welcome_screen(test)
    else:
        render_active_test(test)
    
    # Results evaluation
    if not st.session_state.contrast_test_started and st.session_state.contrast_responses:
        render_results_evaluation()
        render_reset_button()

def initialize_session_state():
    """Initialize all session state variables"""
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

def render_sidebar(handler):
    """Render sidebar controls"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Test mode selection
        test_mode = st.radio(
            "Test Mode", 
            ["Standard (10ft)", "Pelli-Robson (1m)"],
            key="test_mode"
        )
        
        st.markdown("---")
        st.header("📷 Webcam Controls")
        
        # Webcam controls
        web_container = st.empty()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📹 Start Webcam"):
                if handler.initialize_webcam():
                    st.success("Webcam started!")
                else:
                    st.warning("Camera not available")
                st.rerun()
        
        with col2:
            if st.button("⏹️ Stop Webcam"):
                handler.release_webcam()
                st.rerun()
        
        # Display webcam feed
        if st.session_state.webcam_active:
            frame, dist = handler.get_frame(st.session_state.test_engine)
            if frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                web_container.image(rgb, caption="Distance Tracker", width='stretch')
                if dist and dist['detected']:
                    st.metric("Distance", f"{dist['distance_feet']:.1f} ft")

def render_welcome_screen(test):
    """Render welcome screen and instructions"""
    st.markdown("### 🎯 Welcome to Contrast Sensitivity Test")
    st.markdown("""
    This test measures your ability to distinguish between different levels of contrast using letters.
    
    **📋 How the Test Works:**
    1. **Position yourself** at the specified distance from your screen
    2. **Enable webcam** (optional) for distance monitoring
    3. **Cover one eye** if testing individually
    4. **View letters** that appear with different contrast levels
    5. **Identify letters** (type the 3 letters you see)
    6. **Progress through levels** from easy to difficult contrast
    7. **Get results** with clinical interpretation
    
    **🎯 Pattern Type:**
    - **Letter Patterns**: Read 3 letters with varying contrast
    
    **📊 Contrast Levels:** 20% (easiest) → 0.5% (most difficult)
    """)
    
    # Test setup checklist
    st.markdown("### ✅ Test Setup Checklist")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📍 Positioning**
        - Standard: 10 feet away
        - Pelli-Robson: 1 meter away
        - Eye level with screen
        """)
    
    with col2:
        st.markdown("""
        **💡 Lighting**
        - Bright, even lighting
        - No glare on screen
        - Consistent illumination
        """)
    
    with col3:
        st.markdown("""
        **👁️ Eye Care**
        - Remove glasses if needed
        - Cover one eye individually
        - Focus on center of screen
        """)
    
    # Start test button
    st.markdown("---")
    if st.button("🚀 Start Test", type="primary", use_container_width=True):
        test.start_test("Both")
        st.rerun()

def render_active_test(test):
    """Render active test interface"""
    test_mode = st.session_state.get('test_mode', 'Standard (10ft)')
    
    if test_mode == "Standard (10ft)":
        standard_test = StandardContrastTest(test)
        standard_test.render_standard_test("Both", 10)
    else:
        pelli_test = PelliRobsonTest(test)
        pelli_test.render_pelli_robson_section()

def render_reset_button():
    """Render reset button for new test"""
    st.markdown("---")
    st.markdown("### 🔄 Start New Test")
    if st.button("Start New Test", type="primary", use_container_width=True):
        # Reset all session state
        st.session_state.contrast_test_started = False
        st.session_state.contrast_current_level = 0
        st.session_state.contrast_responses = []
        st.session_state.current_contrast_pattern = None
        
        # Clear Pelli-Robson results if present
        if 'pelli_robson_result' in st.session_state:
            del st.session_state.pelli_robson_result
        
        st.rerun()

if __name__ == "__main__":
    main()
