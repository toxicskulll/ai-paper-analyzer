import os
import shutil
import logging
import requests
from pathlib import Path

def ensure_unicode_font():
    """Ensure a Unicode-compatible font is available for PDF generation."""
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    os.makedirs(fonts_dir, exist_ok=True)
    
    # List of potential font files and their download URLs
    font_options = [
        {
            'name': 'DejaVuSans.ttf',
            'url': 'https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf'
        },
        {
            'name': 'NotoSans-Regular.ttf',
            'url': 'https://github.com/googlefonts/noto-fonts/raw/master/hinted/ttf/NotoSans/NotoSans-Regular.ttf'
        }
    ]
    
    for font in font_options:
        font_path = os.path.join(fonts_dir, font['name'])
        
        # Check if font already exists
        if os.path.exists(font_path):
            logging.info(f"Font {font['name']} already exists")
            return font_path
        
        # Try to download the font
        try:
            logging.info(f"Downloading {font['name']}...")
            response = requests.get(font['url'], stream=True)
            response.raise_for_status()
            
            with open(font_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            
            logging.info(f"Successfully downloaded {font['name']}")
            return font_path
            
        except Exception as e:
            logging.warning(f"Failed to download {font['name']}: {str(e)}")
            continue
    
    logging.warning("Could not download any Unicode fonts. Falling back to built-in fonts.")
    return None

# Get the font path when the module is imported
UNICODE_FONT_PATH = ensure_unicode_font()
