"""
UI components for contrast sensitivity test application
"""

import streamlit as st
import time
from datetime import datetime
from webcam_handler import WebcamHandler


class UIComponents:
    @staticmethod
    def render_sidebar(test):
        """Render sidebar with test configuration"""
        st.sidebar.header("Test Configuration")
        
        # Eye selection
        test_eye = st.sidebar.radio(
            "Select Eye to Test:",
            ["Left Eye", "Right Eye", "Both Eyes"]
        )
        
        if test_eye == "Left Eye":
            test_eye_value = "left"
        elif test_eye == "Right Eye":
            test_eye_value = "right"
        else:
            test_eye_value = "both"
        
        # Test distance
        test_distance = st.sidebar.slider(
            "Test Distance (feet):",
            min_value=10,
            max_value=20,
            value=20
        )
        
        # Distance measurement toggle
        use_distance_detection = st.sidebar.checkbox("📏 Enable Distance Detection", value=True)
        
        # Pattern type selection
        test_type = st.sidebar.selectbox(
            "Test Type:",
            ["Standard Contrast Test", "Pelli-Robson Chart (1 Meter)", "Both Tests"]
        )
        
        pattern_preference = st.sidebar.selectbox(
            "Pattern Preference:",
            ["Mixed", "Grating Only", "Letters Only"]
        )
        
        return test_eye_value, test_distance, use_distance_detection, test_type, pattern_preference
    
    @staticmethod
    def render_welcome_screen(test):
        """Render welcome screen with setup checklist"""
        st.markdown("### Welcome to Contrast Sensitivity Test!")
        st.markdown("""
        This test will measure your ability to distinguish between different levels of contrast using letters.
        
        **📋 How the Test Works:**
        1. **Position yourself** at the specified distance from your camera
        2. **Enable webcam** for distance monitoring (optional but recommended)
        3. **Cover one eye** if testing individually
        4. **View letters** that appear with different contrast levels
        5. **Identify letters** (type the 3 letters you see)
        6. **Progress through levels** from low to high contrast
        7. **Get results** showing your contrast sensitivity
        
        **🎯 Pattern Type:**
        - **Letter Patterns**: Read 3 letters with varying contrast
        
        **📊 Contrast Levels:** 0.25% (hardest) → 20% (easiest)
        """)
        
        # Test setup checklist
        st.markdown("### ✅ Test Setup Checklist")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**👁️ Eye Preparation:**")
            st.checkbox("Remove glasses if causing glare", key="glasses_check")
            st.checkbox("Cover left eye (if testing right)", key="left_cover")
            st.checkbox("Cover right eye (if testing left)", key="right_cover")
        
        with col2:
            st.markdown("**📏 Distance Setup:**")
            st.checkbox("Position at target distance", key="distance_check")
            st.checkbox("Face clearly visible in camera", key="face_check")
            st.checkbox("Good lighting on face", key="lighting_check")
        
        with col3:
            st.markdown("**🖥️ Screen Setup:**")
            st.checkbox("Screen at eye level", key="screen_check")
            st.checkbox("No glare on screen", key="glare_check")
            st.checkbox("Comfortable viewing distance", key="comfort_check")
        
        # Sample patterns preview
        UIComponents.render_sample_patterns(test)
        
        # Test difficulty progression
        st.markdown("### 📈 Test Progression")
        st.markdown("""
        **The test starts with HIGH contrast (easy) and progresses to LOW contrast (hard):**
        
        | Level | Contrast | Difficulty | What You'll See |
        |--------|-----------|-------------|-----------------|
        | 1 | 20% | Very Easy | Clearly visible patterns |
        | 3 | 5% | Easy | Good visibility |
        | 5 | 2% | Medium | Challenging but doable |
        | 7 | 1% | Hard | Subtle contrast differences |
        | 9 | 0.25% | Very Hard | Barely visible patterns |
        
        **🏆 Goal:** Find the LOWEST contrast level you can accurately detect!
        """)
    
    @staticmethod
    def render_sample_patterns(test):
        """Render sample pattern previews (letters only)"""
        st.markdown("### 📋 Sample Patterns")
        st.markdown("**Here's what you'll see during the test:**")
        
        st.markdown("**🔤 Letter Patterns**")
        st.info("You'll see letters with varying contrast:")
        # Generate sample letters
        sample_letters = test.generate_contrast_letters(5.0)  # 5% contrast
        cols = st.columns(3)
        for i, img in enumerate(sample_letters['images']):
            with cols[i]:
                st.image(img, width=100, caption=f"Letter {i+1}")
        st.markdown("*Your task: Type the 3 letters you see*")
    
    @staticmethod
    def render_progress_section(test, current_contrast):
        """Render progress section with metrics"""
        st.markdown("### 📊 Your Progress")
        
        # Progress bar with level info
        progress = st.session_state.contrast_current_level / len(test.contrast_levels)
        st.progress(progress)
        
        # Level information
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Level", f"{st.session_state.contrast_current_level + 1}/{len(test.contrast_levels)}")
        with col2:
            st.metric("Contrast", f"{current_contrast}%")
        with col3:
            # Calculate difficulty based on contrast
            if current_contrast >= 5:
                difficulty = "Easy"
                color = "🟢"
            elif current_contrast >= 2:
                difficulty = "Medium"
                color = "🟡"
            elif current_contrast >= 1:
                difficulty = "Hard"
                color = "🟠"
            else:
                difficulty = "Very Hard"
                color = "🔴"
            st.metric("Difficulty", f"{color} {difficulty}")
    
    @staticmethod
    def render_start_button(test_eye_value, use_distance_detection, webcam_handler, test):
        """Render start test button with validation"""
        st.markdown("---")
        ready_to_start = (
            st.session_state.glasses_check or True  # Optional
        )
        
        if st.button("🚀 Start Contrast Sensitivity Test", type="primary", use_container_width=True, disabled=not ready_to_start):
            if use_distance_detection and webcam_handler.active:
                # Check if distance is good before starting
                frame, distance_data = webcam_handler.get_frame_with_distance(test)
                if distance_data and distance_data['detected']:
                    if distance_data['category'] == "Optimal":
                        test.start_test(test_eye_value)
                        st.rerun()
                    else:
                        st.warning(f"⚠️ Please adjust your position. Current status: {distance_data['category']}")
                        st.info(distance_data['guidance'])
                else:
                    st.warning("⚠️ No face detected. Please position yourself in front of the camera.")
            else:
                test.start_test(test_eye_value)
                st.rerun()
    
    @staticmethod
    def render_distance_monitoring(current_distance, target_distance, use_distance_detection, webcam_handler, test):
        """Render real-time distance monitoring"""
        current_distance = target_distance  # Default to slider value
        if use_distance_detection and webcam_handler.active:
            st.markdown("### 📏 Real-time Distance Monitoring")
            # Get current frame and distance
            frame, distance_data = webcam_handler.get_frame_with_distance(test)
            
            if distance_data and distance_data['detected']:
                current_distance = distance_data['distance_feet']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Distance", f"{current_distance:.1f} ft")
                with col2:
                    st.metric("Target Distance", f"{target_distance} ft")
                with col3:
                    diff = abs(current_distance - target_distance)
                    if diff <= 2:
                        st.success("✅ Good position!")
                    else:
                        st.warning(f"⚠️ Move {diff:.1f} ft {'closer' if current_distance > target_distance else 'further'}")
                
                st.info(f"📊 {distance_data['category']}: {distance_data['guidance']}")
            else:
                st.warning("⚠️ No face detected for distance measurement")
                current_distance = target_distance
        elif use_distance_detection:
            st.info("📹 Webcam not active - distance monitoring disabled")
        
        return current_distance
    
    @staticmethod
    def render_webcam_controls(webcam_handler, test):
        """Render webcam controls in sidebar"""
        st.sidebar.markdown("### 📷 Webcam Feed")
        webcam_placeholder = st.sidebar.empty()
        
        # Initialize webcam in session state
        if 'webcam_active' not in st.session_state:
            st.session_state.webcam_active = False
        if 'webcam_cap' not in st.session_state:
            st.session_state.webcam_cap = None
        
        # Webcam control buttons
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📹 Start Webcam", key="start_webcam"):
                if not st.session_state.webcam_active:
                    st.sidebar.info("🔄 Attempting to open camera...")
                    cap = webcam_handler.initialize_webcam()
                    if cap:
                        st.session_state.webcam_cap = cap
                        st.session_state.webcam_active = True
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Failed to open any camera")
                        st.sidebar.warning("📋 Test will continue without webcam")
        with col2:
            if st.button("⏹️ Stop Webcam", key="stop_webcam"):
                if st.session_state.webcam_active and st.session_state.webcam_cap:
                    webcam_handler.release_webcam()
                    st.session_state.webcam_active = False
                    st.session_state.webcam_cap = None
                    st.rerun()
        
        # Display webcam feed or status
        if st.session_state.webcam_active and st.session_state.webcam_cap:
            webcam_handler.display_webcam_feed(webcam_placeholder, test)
        else:
            webcam_placeholder.info("""
            📹 **Webcam Status**: Inactive
            
            **Click 'Start Webcam' to begin distance monitoring**
            
            **If webcam doesn't work:**
            - Test will continue without distance monitoring
            - You can still complete the contrast sensitivity test
            - Results will be based on your manual distance setting
            """)
