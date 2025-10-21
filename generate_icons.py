#!/usr/bin/env python3
"""
Generate PWA icons for Section 1983 App
Creates 192x192 and 512x512 PNG icons
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, output_path):
    """Create a simple, professional icon for the app"""

    # Create image with blue background
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)

    # Calculate font size based on icon size
    font_size = int(size * 0.25)  # 25% of icon size

    try:
        # Try to use a nice font if available
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Draw white text "1983" in the center
    text = "1983"

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position to center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - int(size * 0.05)  # Slightly above center

    # Draw text
    draw.text((x, y), text, fill='white', font=font)

    # Draw a subtle gavel emoji representation (simple hammer shape)
    # Drawing a simple legal scale/balance icon
    scale_size = int(size * 0.15)
    scale_y = int(size * 0.65)
    scale_x = size // 2

    # Draw balance beam
    beam_width = int(size * 0.4)
    draw.rectangle(
        [scale_x - beam_width//2, scale_y, scale_x + beam_width//2, scale_y + int(size * 0.02)],
        fill='white'
    )

    # Draw center pillar
    pillar_width = int(size * 0.03)
    draw.rectangle(
        [scale_x - pillar_width//2, scale_y, scale_x + pillar_width//2, scale_y + int(size * 0.1)],
        fill='white'
    )

    # Save the icon
    img.save(output_path, 'PNG')
    print(f"✅ Created {size}x{size} icon at {output_path}")

def main():
    """Generate all required icons"""

    # Ensure output directory exists
    output_dir = 'static/images'
    os.makedirs(output_dir, exist_ok=True)

    # Generate 192x192 icon
    create_icon(192, os.path.join(output_dir, 'icon-192.png'))

    # Generate 512x512 icon
    create_icon(512, os.path.join(output_dir, 'icon-512.png'))

    print("\n🎉 All icons created successfully!")
    print("Icons are located in: static/images/")
    print("- icon-192.png (192x192)")
    print("- icon-512.png (512x512)")

if __name__ == '__main__':
    main()
