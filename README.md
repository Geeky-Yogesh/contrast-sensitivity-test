# 👁️ Professional Contrast Sensitivity Test

A comprehensive, professional-grade contrast sensitivity testing application with clinical accuracy and medical evaluation capabilities.

## 🎯 Features

### **Dual Test Modes:**
- **Standard Test (10ft)** - Progressive letter recognition with Weber contrast calculation
- **Pelli-Robson Test (1m)** - Clinical chart assessment with LogCS scoring

### **Clinical Evaluation System:**
- **Performance Metrics** - Total levels, pass rate, best contrast achieved
- **Medical Interpretation** - Evidence-based clinical categorization
- **Detailed Results** - Level-by-level performance tracking
- **Professional Reports** - Exportable medical documentation

### **Technical Excellence:**
- **Robust Session Management** - Clean state handling and error recovery
- **Camera Integration** - Optional distance monitoring with graceful degradation
- **Responsive Design** - Works on all devices and screen sizes
- **Professional UI** - Medical-grade interface with clear instructions

## 🚀 Quick Start

### **Installation:**
```bash
# Clone the repository
git clone https://github.com/Geeky-Yogesh/contrast-sensitivity-test.git
cd contrast-sensitivity-test

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run contrast_sensitivity_app.py
```

### **Usage:**
1. **Open your browser** to the provided URL (usually http://localhost:8501)
2. **Select test mode** - Standard (10ft) or Pelli-Robson (1m)
3. **Position yourself** at the correct distance from screen
4. **Enable webcam** (optional) for distance monitoring
5. **Complete the test** by identifying letters at different contrast levels
6. **View results** with clinical interpretation
7. **Export reports** for medical consultation

## 📊 Test Modes

### **Standard Test (10 feet)**
- **Progressive difficulty** - 20% to 0.5% contrast levels
- **Letter recognition** - 3 letters per level
- **Pass criteria** - 2/3 letters correct
- **Automatic advancement** - Move to next level on success

### **Pelli-Robson Test (1 meter)**
- **Clinical protocol** - Standard medical implementation
- **LogCS scoring** - Logarithmic contrast sensitivity
- **Interactive chart** - Click-based response system
- **Clinical categorization** - Medical interpretation

## 🏥 Clinical Accuracy

### **Contrast Calculation:**
- **Weber Contrast** - Standard medical formula
- **Progressive Levels** - Evidence-based difficulty scaling
- **Clinical Thresholds** - Medical interpretation standards

### **Evaluation Categories:**
- **Excellent** (80%+ pass rate) - Well within normal range
- **Good** (60-79% pass rate) - Expected for age group
- **Fair** (40-59% pass rate) - Slightly below average
- **Poor** (<40% pass rate) - Below normal range

## 🔧 Technical Stack

- **Python** - Core application logic
- **Streamlit** - Interactive web interface
- **OpenCV** - Computer vision and image processing
- **NumPy** - Numerical computations
- **PIL** - Image manipulation and display

## 📱 Features

### **User Interface:**
- **Professional design** - Medical-grade interface
- **Responsive layout** - Works on all devices
- **Clear instructions** - Step-by-step guidance
- **Real-time feedback** - Immediate pass/fail notifications

### **Data Management:**
- **Session state** - Clean data handling
- **Export functionality** - Download medical reports
- **Error handling** - Graceful degradation
- **Camera integration** - Optional distance monitoring

## 📋 Requirements

```bash
streamlit>=1.28.0
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
```

## 🤝 Contributing

Contributions welcome! Please ensure:
- Clinical accuracy
- Medical standards compliance
- Professional code quality
- Comprehensive testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏥 Medical Disclaimer

This application is designed for contrast sensitivity screening and should not replace comprehensive eye examinations. Always consult with qualified healthcare professionals for medical diagnosis and treatment.

## 🔗 Links

- **Live Demo**: [Add deployment link here]
- **GitHub Repository**: https://github.com/Geeky-Yogesh/contrast-sensitivity-test
- **Issues**: Report bugs or request features

---

**Built with ❤️ for better vision health assessment**
