import os
import logging

from PIL import Image as ImageFile, ImageFont, ImageDraw


log = logging.getLogger(__name__)

# TODO: move to a fonts store
FONT = os.path.normpath(os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir,
    'data', 'fonts', 'Impact.ttf'
))


class Image:
    """Meme JPEG generated from a template."""

    def __init__(self, template, text, root=None):
        self.template = template
        self.text = text
        self.root = root

    @property
    def path(self):
        if self.root:
            return os.path.join(self.root, self.template.key,
                                self.text.path + '.jpg')
        else:
            return None

    def generate(self):
        directory = os.path.dirname(self.path)
        if not os.path.isdir(directory):
            os.makedirs(directory)
        make_meme(self.text.top, self.text.bottom,
                  self.template.path, self.path)

def split_sentance(phrase):
    ''' This function tries to split the phrase into two in as close to same size as possible'''
    result = [phrase]
    if len(phrase) >= 3 and ' ' in phrase[1:-1]: # can split this string
        spaceindx=[i for i in range(len(phrase)) if phrase[i]==' '] #indicies of spaces
        close = [abs(spacei-len(phrase)//2) for spacei in spaceindx] #space distance from center
        for i, j in zip(close, spaceindx):
            if i == min(close):
                result = [phrase[:j],phrase[j+1:]]
                break
    return result

def calc_largest_fontSize(phrase, max_size):
    '''Find biggest font size that works'''
    font_size = max_size
    font = ImageFont.truetype(FONT, font_size)
    text_size = font.getsize(phrase)
    while text_size[0] > max_size:
        font_size = font_size - 1
        font = ImageFont.truetype(FONT, font_size)
        text_size = font.getsize(phrase)
    return font_size

def calc_font_size(top, bottom, max_font_size, min_font_size, max_text_len):
    font_size = max_font_size

    # Check size when using smallest single line font size
    font = ImageFont.truetype(FONT, min_font_size)
    top_text_size = font.getsize(top)
    bottom_text_size = font.getsize(bottom)

    #calculate font size for top text, split if necessary
    if top_text_size[0] > max_text_len:
        top_phrases = split_sentance(top)
    else:
        top_phrases = [top]
    for phrase in top_phrases:
        font_size = min(calc_largest_fontSize(phrase, max_text_len), font_size)
    
    #calculate font size for bottom text, split if necessary
    if bottom_text_size[0] > max_text_len:
        bottom_phrases = split_sentance(bottom)
    else:
        bottom_phrases = [bottom]
    for phrase in bottom_phrases:
        font_size = min(calc_largest_fontSize(phrase, max_text_len), font_size)

    #rebuild text with new lines
    top = '\n'.join(top_phrases)
    bottom = '\n'.join(bottom_phrases)
    
    return font_size, top, bottom

# based on: https://github.com/danieldiekmeier/memegenerator
def make_meme(top, bottom, background, path):
    img = ImageFile.open(background)

    # Resize to a maximum height and width
    img.thumbnail((500, 500))
    image_size = img.size
        
    # Draw image
    draw = ImageDraw.Draw(img)

    max_font_size = int(image_size[1] / 5)
    min_font_size = int(image_size[1] / 10)
    max_text_len = image_size[0] - 20
    font_size, top, bottom = calc_font_size(top, bottom, max_font_size, min_font_size, max_text_len)
    font = ImageFont.truetype(FONT, font_size)

    top_text_size = draw.multiline_textsize(top, font)
    bottom_text_size = draw.multiline_textsize(bottom, font)

    # Find top centered position for top text
    top_text_position_x = (image_size[0] / 2) - (top_text_size[0] / 2)
    top_text_position_y = 0
    top_text_position = (top_text_position_x, top_text_position_y)

    # Find bottom centered position for bottom text
    bottom_text_size_x = (image_size[0] / 2) - (bottom_text_size[0] / 2)
    bottom_text_size_y = image_size[1] - bottom_text_size[1] * (7 / 6)
    bottom_text_position = (bottom_text_size_x, bottom_text_size_y)

    # Draw black text outlines
    outline_range = int(font_size / 15)
    for x in range(-outline_range, outline_range + 1):
        for y in range(-outline_range, outline_range + 1):
            pos = (top_text_position[0] + x, top_text_position[1] + y)
            draw.multiline_text(pos, top, (0, 0, 0), font=font, align='center')
            pos = (bottom_text_position[0] + x, bottom_text_position[1] + y)
            draw.multiline_text(pos, bottom, (0, 0, 0), font=font, align='center')

    # Draw inner white text
    draw.multiline_text(top_text_position, top, (255, 255, 255), font=font, align='center')
    draw.multiline_text(bottom_text_position, bottom, (255, 255, 255), font=font, align='center')

    log.info("generated: %s", path)
    return img.save(path)
