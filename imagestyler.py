from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
 
 
def watermark_text(user_id, text, color, pos):
    with Image.open(f'{user_id}/in.jpg').convert("RGBA") as base:
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

    # make the image editable
        drawing = ImageDraw.Draw(txt)
        font = ImageFont.truetype("Molot.otf", 40)
        drawing.text(pos, text, fill=color, font=font)
        out = Image.alpha_composite(base, txt)
        out.save(f'{user_id}/out.png')
        return