import cv2
import numpy as np
import streamlit as st
import random
import math
from PIL import Image

class ContrastSensitivityTest:
    def __init__(self):
        # Professional Contrast Levels (as decimals)
        self.contrast_levels = [0.20, 0.10, 0.05, 0.025, 0.0125, 0.01, 0.0075, 0.005]
        self.pattern_size = 200

    def start_test(self, test_eye):
        st.session_state.contrast_test_started = True
        st.session_state.contrast_current_level = 0
        st.session_state.contrast_test_eye = test_eye
        st.session_state.contrast_responses = []
        st.session_state.current_contrast_pattern = self.generate_contrast_pattern()

    def generate_contrast_pattern(self, contrast=None):
        if contrast is None:
            idx = st.session_state.contrast_current_level
            contrast = self.contrast_levels[idx]
        
        letters = random.sample('ABCDEFGHJKLMNOPRSTUVXYZ', 3)
        bg_val = 240 
        text_val = int(bg_val * (1.0 - contrast)) # Weber Contrast Math
        
        letter_images = []
        for letter in letters:
            img = np.ones((self.pattern_size, self.pattern_size, 3), dtype=np.uint8) * bg_val
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 2.0
            thickness = 5
            (w, h), _ = cv2.getTextSize(letter, font, font_scale, thickness)
            cv2.putText(img, letter, ((self.pattern_size-w)//2, (self.pattern_size+h)//2), 
                        font, font_scale, (text_val, text_val, text_val), thickness)
            
            # Convert to RGB PIL for Streamlit stability
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            letter_images.append(Image.fromarray(img_rgb))

        return {
            'images': letter_images,
            'letters': letters,
            'contrast_percent': round(contrast * 100, 2)
        }

    def generate_pelli_robson_chart(self):
        chart_width, chart_height = 900, 600
        img = np.ones((chart_height, chart_width, 3), dtype=np.uint8) * 240
        # Standard Clinical LogCS steps - each step repeats for 3 letters (groups)
        log_cs_steps = [0.00, 0.00, 0.00, 0.15, 0.15, 0.15, 0.30, 0.30, 0.30, 
                       0.45, 0.45, 0.45, 0.60, 0.60, 0.60, 0.75, 0.75, 0.75,
                       0.90, 0.90, 0.90, 1.05, 1.05, 1.05, 1.20, 1.20, 1.20,
                       1.35, 1.35, 1.35, 1.50, 1.50, 1.50, 1.65, 1.65, 1.65]
        chart_data = []
        
        # Generate letters for Pelli-Robson chart
        letters_sequence = []
        current_group = 0
        for log_val in log_cs_steps:
            letter = random.choice('NHRSDKV')
            letters_sequence.append({'letter': letter, 'log_cs': log_val, 'group': current_group})
            # Move to next group after 3 letters
            if len([l for l in letters_sequence if l['log_cs'] == log_val]) % 3 == 0 and log_val != letters_sequence[-1]['log_cs']:
                current_group += 1
        
        # Layout the chart in rows
        for i, item in enumerate(letters_sequence):
            contrast = 1 / (10**item['log_cs'])
            text_val = int(240 * (1.0 - contrast))
            row, col = i // 6, i % 6  # 6 letters per row
            x, y = col * 140 + 80, row * 120 + 80
            cv2.putText(img, item['letter'], (x-20, y+20), cv2.FONT_HERSHEY_SIMPLEX, 2, 
                       (text_val, text_val, text_val), 6)
            chart_data.append(item)
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return {'image': Image.fromarray(img_rgb), 'data': chart_data}

    def get_current_pattern(self):
        return st.session_state.get('current_contrast_pattern')

    def next_level(self):
        st.session_state.contrast_current_level += 1
        if st.session_state.contrast_current_level < len(self.contrast_levels):
            st.session_state.current_contrast_pattern = self.generate_contrast_pattern()
        else:
            st.session_state.contrast_test_started = False

    def get_clinical_category(self, log_cs):
        if log_cs >= 1.80: return "Excellent", "🟢 Superior contrast sensitivity. Well above average."
        if log_cs >= 1.50: return "Normal", "🟢 Normal contrast sensitivity for healthy eyes."
        if log_cs >= 1.20: return "Fair", "🟡 Slightly reduced. Monitor over time."
        if log_cs >= 0.90: return "Mild Loss", "🟠 Mild contrast sensitivity reduction."
        return "Significant Loss", "🔴 Significant contrast loss. Consult eye doctor."

    def calculate_distance_from_face(self, frame):
        try:
            xml_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(xml_path)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)
            if len(faces) > 0:
                x, y, w, h = max(faces, key=lambda r: r[2]*r[3])
                dist_ft = (15 * 500) / (w * 30.48) 
                return {'detected': True, 'distance_feet': dist_ft}
        except: pass
        return {'detected': False}