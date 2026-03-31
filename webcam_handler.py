import cv2
import streamlit as st

class WebcamHandler:
    def __init__(self):
        if 'webcam_cap' not in st.session_state:
            st.session_state.webcam_cap = None
        self.active = st.session_state.get('webcam_active', False)

    def initialize_webcam(self):
        """Initialize webcam for distance monitoring"""
        if st.session_state.webcam_cap is None:
            try:
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    st.session_state.webcam_cap = cap
                    st.session_state.webcam_active = True
                    return cap
                else:
                    st.warning("Camera not available. Test will continue without distance monitoring.")
                    return None
            except Exception as e:
                st.warning(f"Camera initialization failed: {e}")
                return None
        return st.session_state.webcam_cap

    def release_webcam(self):
        if st.session_state.webcam_cap:
            st.session_state.webcam_cap.release()
            st.session_state.webcam_cap = None
            st.session_state.webcam_active = False

    def get_frame(self, test_engine):
        cap = st.session_state.webcam_cap
        if not cap: return None, None
        
        ret, frame = cap.read()
        if not ret: return None, None
        
        frame = cv2.flip(frame, 1)
        distance_data = test_engine.calculate_distance_from_face(frame)
        return frame, distance_data