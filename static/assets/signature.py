from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a white background
width, height = 500, 150
image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
draw = ImageDraw.Draw(image)

# Draw a signature
points = [(50, 80), (80, 50), (120, 100), (160, 40), (200, 70), (240, 50), 
          (280, 80), (320, 60), (350, 90), (380, 70), (430, 80)]

for i in range(len(points) - 1):
    draw.line([points[i], points[i+1]], fill=(0, 0, 150), width=3)

# Add text
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 20)
except:
    font = ImageFont.load_default()

draw.text((250, 100), "Authorized Signature", fill=(0, 0, 0), font=font)

# Save the image
image.save("signature.png", "PNG")

# Create company stamp
stamp_width, stamp_height = 300, 300
stamp = Image.new('RGBA', (stamp_width, stamp_height), (255, 255, 255, 0))
stamp_draw = ImageDraw.Draw(stamp)

# Draw outer circle
stamp_draw.ellipse((10, 10, stamp_width-10, stamp_height-10), outline=(135, 20, 20), width=3)
# Draw inner circle
stamp_draw.ellipse((30, 30, stamp_width-30, stamp_height-30), outline=(135, 20, 20), width=2)

# Add text to the stamp
try:
    stamp_font_large = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
    stamp_font_medium = ImageFont.truetype("DejaVuSans.ttf", 20)
    stamp_font_small = ImageFont.truetype("DejaVuSans.ttf", 16)
except:
    stamp_font_large = ImageFont.load_default()
    stamp_font_medium = ImageFont.load_default()
    stamp_font_small = ImageFont.load_default()

stamp_draw.text((stamp_width//2, 120), "PC ASSEMBLER", fill=(135, 20, 20), 
                font=stamp_font_large, anchor="mm")
stamp_draw.text((stamp_width//2, 160), "OFFICIAL", fill=(135, 20, 20), 
                font=stamp_font_medium, anchor="mm")
stamp_draw.text((stamp_width//2, 200), "est. 2023", fill=(135, 20, 20), 
                font=stamp_font_small, anchor="mm")

# Save the stamp
stamp.save("stamp.png", "PNG")

print("Signature and stamp images created successfully.")