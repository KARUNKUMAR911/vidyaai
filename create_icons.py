# Save as C:\vidyaai\create_icons.py
from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('C:/vidyaai/static/icons', exist_ok=True)

def create_icon(size):
    img = Image.new('RGB', (size, size), color='#7c3aed')
    draw = ImageDraw.Draw(img)
    
    # Draw circle background
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='#6d28d9')
    
    # Draw text
    font_size = size // 3
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    text = "V"
    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) // 2
    y = (size - text_h) // 2
    draw.text((x, y), text, fill='white', font=font)
    
    return img

# Generate icons
create_icon(192).save('C:/vidyaai/static/icons/icon-192.png')
create_icon(512).save('C:/vidyaai/static/icons/icon-512.png')
print("Icons created!")
