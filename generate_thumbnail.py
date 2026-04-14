"""
Generate professional thumbnail for Upwork gig
Run: pip install Pillow
Then: python generate_thumbnail.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_thumbnail():
    # Create image (1200x675 for YouTube/Upwork)
    width, height = 1200, 675
    img = Image.new('RGB', (width, height), '#1e3c72')
    draw = ImageDraw.Draw(img)

    # Create gradient background
    for y in range(height):
        r = int(30 + (74 - 30) * (y / height))
        g = int(60 + (114 - 60) * (y / height))
        b = int(114 + (152 - 114) * (y / height))
        for x in range(width):
            draw.point((x, y), (r, g, b))

    # Try to load fonts, fallback to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
        subtitle_font = ImageFont.truetype("arial.ttf", 30)
        code_font = ImageFont.truetype("cour.ttf", 24)
        tech_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
        tech_font = ImageFont.load_default()

    # Title
    title = "🚀 SQL AI Assistant"
    draw.text((width//2, 80), title, fill='white', font=title_font, anchor='mm')

    # Subtitle
    subtitle = "Convert Natural Language to SQL Queries Instantly"
    draw.text((width//2, 140), subtitle, fill='white', font=subtitle_font, anchor='mm')

    # Demo section
    # Left box - API call
    draw.rectangle([100, 200, 500, 400], fill=(0, 0, 0, 180), outline='#00d4ff', width=3)
    api_text = """POST /ask
{
  "question": "top 5 customers by spending"
}"""
    y_offset = 220
    for line in api_text.split('\n'):
        draw.text((120, y_offset), line, fill='#00ff88', font=code_font)
        y_offset += 30

    # Arrow
    draw.text((550, 300), "→", fill='#00d4ff', font=title_font, anchor='mm')

    # Right box - Response
    draw.rectangle([650, 200, 1100, 450], fill=(0, 0, 0, 180), outline='#ff6b6b', width=3)
    response_text = """{
  "sql_query": "SELECT customers.name...",
  "results": [
    {"name": "Ali", "total_spending": 300.0}
  ],
  "execution_time": 1.23
}"""
    y_offset = 220
    for line in response_text.split('\n'):
        draw.text((670, y_offset), line, fill='#ff6b6b', font=code_font)
        y_offset += 25

    # Tech stack badges
    tech_items = ["🤖 Ollama + Mistral", "🚀 FastAPI", "💾 SQLite", "🔒 Secure SELECT-only"]
    badge_width = 180
    start_x = (width - (len(tech_items) * badge_width + (len(tech_items)-1) * 20)) // 2

    for i, tech in enumerate(tech_items):
        x = start_x + i * (badge_width + 20)
        draw.rounded_rectangle([x, 520, x + badge_width, 560], radius=20, fill=(255, 255, 255, 50), outline=(255, 255, 255, 100), width=2)
        draw.text((x + badge_width//2, 540), tech, fill='white', font=tech_font, anchor='mm')

    # Footer
    footer = "Professional AI-Powered Data Solutions"
    draw.text((width//2, 620), footer, fill='white', font=subtitle_font, anchor='mm')

    # Save the image
    output_path = "sql_ai_assistant_thumbnail.png"
    img.save(output_path, 'PNG')
    print(f"✅ Thumbnail saved as: {output_path}")
    print(f"📐 Dimensions: {width}x{height} (perfect for Upwork)")
    print("🎨 Ready to upload to your Upwork gig!")

    return output_path

if __name__ == "__main__":
    try:
        create_thumbnail()
    except ImportError:
        print("❌ Please install Pillow: pip install Pillow")
    except Exception as e:
        print(f"❌ Error generating thumbnail: {e}")