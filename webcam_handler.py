import cv2
import streamlit as st

class WebcamHandler:
    def initialize_webcam(self):
        if st.session_state.get('webcam_cap') is None:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                st.session_state.webcam_cap = cap
                st.session_state.webcam_active = True
                return True
        return False

    def release_webcam(self):
        if st.session_state.get('webcam_cap'):
            st.session_state.webcam_cap.release()
            st.session_state.webcam_cap = None
            st.session_state.webcam_active = False

    def get_frame(self, test_engine):
        cap = st.session_state.get('webcam_cap')
        if not cap: return None, None
        ret, frame = cap.read()
        if not ret: return None, None
        frame = cv2.flip(frame, 1)
        dist = test_engine.calculate_distance_from_face(frame)
        return frame, dist