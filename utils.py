"""
Utility functions for contrast sensitivity test application
"""

def get_contrast_explanation(contrast):
    """Get explanation of what contrast level means"""
    if contrast >= 10:
        return "Very high contrast - easily visible patterns"
    elif contrast >= 5:
        return "High contrast - clear visibility"
    elif contrast >= 2:
        return "Medium contrast - challenging but manageable"
    elif contrast >= 1:
        return "Low contrast - subtle differences"
    else:
        return "Very low contrast - barely visible"
    
def get_visibility_expectation(contrast):
    """Get expected visibility at this contrast level"""
    if contrast >= 10:
        return "You should see this very clearly"
    elif contrast >= 5:
        return "Most people can see this easily"
    elif contrast >= 2:
        return "This may be challenging for some people"
    elif contrast >= 1:
        return "This is difficult for many people"
    else:
        return "This is very difficult - normal vision may struggle"
