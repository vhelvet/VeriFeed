import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_default_profile_picture():
    """Create a default profile picture if it doesn't exist"""
    
    # Get the media directory
    media_dir = Path(__file__).parent / 'media' / 'profile_pics'
    media_dir.mkdir(parents=True, exist_ok=True)
    
    default_pic_path = media_dir / 'default.jpg'
    
    if not default_pic_path.exists():
        # default profile picture
        size = (200, 200)
        img = Image.new('RGB', size, color='#e0e0e0')
        draw = ImageDraw.Draw(img)
        
        # Head circle
        head_center = (100, 70)
        head_radius = 30
        draw.ellipse([
            head_center[0] - head_radius,
            head_center[1] - head_radius,
            head_center[0] + head_radius,
            head_center[1] + head_radius
        ], fill='#a0a0a0')
        
        # Body semi-circle
        body_center = (100, 140)
        body_radius = 50
        draw.ellipse([
            body_center[0] - body_radius,
            body_center[1] - body_radius,
            body_center[0] + body_radius,
            body_center[1] + body_radius
        ], fill='#a0a0a0')
        
        # Save the image
        img.save(default_pic_path, 'JPEG', quality=95)
        print(f"Default profile picture created at: {default_pic_path}")
    else:
        print(f"Default profile picture already exists at: {default_pic_path}")

def create_placeholder_frontend():
    """Create a placeholder image for the frontend public folder"""
    
    public_dir = Path(__file__).parent.parent / 'public' 
    public_dir.mkdir(parents=True, exist_ok=True)
    
    placeholder_path = public_dir / 'profile_placeholder.png'
    
    if not placeholder_path.exists():
        size = (200, 200)
        img = Image.new('RGBA', size, color=(240, 240, 240, 255))
        draw = ImageDraw.Draw(img)
        
        # Head circle
        head_center = (100, 70)
        head_radius = 25
        draw.ellipse([
            head_center[0] - head_radius,
            head_center[1] - head_radius,
            head_center[0] + head_radius,
            head_center[1] + head_radius
        ], fill=(160, 160, 160, 255))
        
        # Body semi-circle
        body_center = (100, 140)
        body_radius = 45
        draw.ellipse([
            body_center[0] - body_radius,
            body_center[1] - body_radius,
            body_center[0] + body_radius,
            body_center[1] + body_radius
        ], fill=(160, 160, 160, 255))
        
        img.save(placeholder_path, 'PNG')
        print(f"Frontend placeholder created at: {placeholder_path}")
    else:
        print(f"Frontend placeholder already exists at: {placeholder_path}")

if __name__ == "__main__":
    print("Setting up profile pictures...")
    create_default_profile_picture()
    create_placeholder_frontend()
    print("Profile picture setup complete!")