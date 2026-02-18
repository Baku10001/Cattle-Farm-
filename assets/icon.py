"""
Application icon generator for Cattle Farm Management System
Creates both SVG and ICO format icons for cross-platform compatibility
"""

import os
from pathlib import Path

def create_app_icon():
    """Create SVG and ICO icons for the application"""
    
    # Create assets directory if it doesn't exist
    assets_dir = Path(__file__).parent
    assets_dir.mkdir(exist_ok=True)
    
    # SVG icon content - cow silhouette with farm elements
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <!-- Background circle -->
  <circle cx="128" cy="128" r="120" fill="#2c5530" stroke="#1a3d1f" stroke-width="4"/>
  
  <!-- Grass base -->
  <ellipse cx="128" cy="220" rx="100" ry="20" fill="#4a7c59"/>
  
  <!-- Cow body -->
  <ellipse cx="128" cy="160" rx="45" ry="25" fill="#f8f8f8"/>
  
  <!-- Cow head -->
  <ellipse cx="128" cy="120" rx="25" ry="20" fill="#f8f8f8"/>
  
  <!-- Cow spots -->
  <ellipse cx="115" cy="155" rx="8" ry="6" fill="#2c2c2c"/>
  <ellipse cx="140" cy="165" rx="6" ry="4" fill="#2c2c2c"/>
  <ellipse cx="125" cy="170" rx="5" ry="3" fill="#2c2c2c"/>
  
  <!-- Cow ears -->
  <ellipse cx="115" cy="110" rx="4" ry="8" fill="#f0f0f0"/>
  <ellipse cx="141" cy="110" rx="4" ry="8" fill="#f0f0f0"/>
  
  <!-- Cow eyes -->
  <circle cx="122" cy="118" r="2" fill="#2c2c2c"/>
  <circle cx="134" cy="118" r="2" fill="#2c2c2c"/>
  
  <!-- Cow nose -->
  <ellipse cx="128" cy="125" rx="3" ry="2" fill="#ffb6c1"/>
  
  <!-- Legs -->
  <rect x="110" y="180" width="4" height="15" fill="#2c2c2c"/>
  <rect x="120" y="180" width="4" height="15" fill="#2c2c2c"/>
  <rect x="132" y="180" width="4" height="15" fill="#2c2c2c"/>
  <rect x="142" y="180" width="4" height="15" fill="#2c2c2c"/>
  
  <!-- Tail -->
  <path d="M 173 160 Q 185 155 180 170" stroke="#2c2c2c" stroke-width="3" fill="none"/>
  
  <!-- Farm elements - barn in background -->
  <rect x="60" y="80" width="30" height="25" fill="#8b4513"/>
  <polygon points="60,80 75,65 90,80" fill="#654321"/>
  
  <!-- Fence -->
  <rect x="40" y="140" width="2" height="15" fill="#8b4513"/>
  <rect x="50" y="140" width="2" height="15" fill="#8b4513"/>
  <rect x="40" y="145" width="14" height="2" fill="#8b4513"/>
  <rect x="40" y="150" width="14" height="2" fill="#8b4513"/>
  
  <!-- Sun -->
  <circle cx="200" cy="60" r="12" fill="#ffd700"/>
  <path d="M 200 40 L 200 35 M 220 60 L 225 60 M 215 45 L 218 42 M 185 45 L 182 42 M 200 80 L 200 85 M 180 60 L 175 60 M 185 75 L 182 78 M 215 75 L 218 78" stroke="#ffd700" stroke-width="2"/>
  
  <!-- Title text -->
  <text x="128" y="240" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#ffffff">Farm Manager</text>
</svg>'''
    
    # Write SVG file
    svg_path = assets_dir / "app_icon.svg"
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"SVG icon created at: {svg_path}")
    
    # Try to create ICO file using PIL
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple 32x32 ICO icon
        ico_size = (32, 32)
        img = Image.new('RGBA', ico_size, (44, 85, 48, 255))  # Green background
        draw = ImageDraw.Draw(img)
        
        # Draw simple cow shape
        # Body (ellipse)
        draw.ellipse([8, 16, 24, 26], fill=(248, 248, 248, 255))  # White body
        
        # Head (circle)
        draw.ellipse([12, 8, 20, 16], fill=(248, 248, 248, 255))  # White head
        
        # Spots
        draw.ellipse([10, 18, 13, 21], fill=(44, 44, 44, 255))  # Black spot
        draw.ellipse([18, 20, 21, 23], fill=(44, 44, 44, 255))  # Black spot
        
        # Eyes
        draw.ellipse([14, 10, 15, 11], fill=(44, 44, 44, 255))  # Left eye
        draw.ellipse([17, 10, 18, 11], fill=(44, 44, 44, 255))  # Right eye
        
        # Legs
        draw.rectangle([11, 24, 12, 28], fill=(44, 44, 44, 255))  # Leg 1
        draw.rectangle([13, 24, 14, 28], fill=(44, 44, 44, 255))  # Leg 2
        draw.rectangle([18, 24, 19, 28], fill=(44, 44, 44, 255))  # Leg 3
        draw.rectangle([20, 24, 21, 28], fill=(44, 44, 44, 255))  # Leg 4
        
        # Save as ICO
        ico_path = assets_dir / "app_icon.ico"
        img.save(ico_path, format='ICO', sizes=[(32, 32)])
        print(f"ICO icon created at: {ico_path}")
        
    except ImportError:
        print("PIL not available - ICO creation skipped")
    except Exception as e:
        print(f"ICO creation failed: {e}")
    
    return svg_path

if __name__ == "__main__":
    create_app_icon()
