from PIL import Image

ASCII_CHARS = "@%#*+=-:. "

BRAILLE_BASE = 0x2800
DOTS = [
    (0, 0),  # dot 1
    (1, 0),  # dot 2
    (2, 0),  # dot 3
    (0, 1),  # dot 4
    (1, 1),  # dot 5
    (2, 1),  # dot 6
    (3, 0),  # dot 7
    (3, 1),  # dot 8
]

def resize_image(image, new_width=100):
    width, height = image.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio * 0.55)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayscale(image):
    return image.convert("L")

def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ""
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
    return ascii_str

def pixels_to_braille_block(pixels):
    """pixels is a 4x2 matrix of 0/1 (row-major)
    Returns a single braille character"""
    value = 0
    for i, (row, col) in enumerate(DOTS):
        if pixels[row][col]:
            value |= 1 << i
    return chr(BRAILLE_BASE + value)

def image_to_braille(image, threshold=128):
    """Convert PIL Image (grayscale) to braille ASCII string."""
    # Make sure image height is multiple of 4 and width multiple of 2 for perfect blocks
    w, h = image.size
    new_w = w - (w % 2)
    new_h = h - (h % 4)
    image = image.crop((0, 0, new_w, new_h))

    pixels = image.load()

    lines = []
    for y in range(0, new_h, 4):
        line_chars = []
        for x in range(0, new_w, 2):
            # Create 4x2 pixel block (rows x cols)
            block = [[0,0],[0,0],[0,0],[0,0]]
            for row in range(4):
                for col in range(2):
                    val = pixels[x+col, y+row]
                    block[row][col] = 1 if val < threshold else 0
            braille_char = pixels_to_braille_block(block)
            line_chars.append(braille_char)
        lines.append("".join(line_chars))
    return "\n".join(lines)

def main(image_path, new_width=100, mode='ascii'):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(f"Unable to open image file {image_path}.")
        print(e)
        return

    if mode == 'ascii':
        image = resize_image(image, new_width)
        image = grayscale(image)
        ascii_str = pixels_to_ascii(image)
        img_width = image.width
        ascii_img = "\n".join([ascii_str[i:(i+img_width)] for i in range(0, len(ascii_str), img_width)])
        print(ascii_img)
    elif mode == 'braille':
        # For braille, new_width refers to the number of braille chars per line
        # Each braille char = 2 pixels wide, so resize image width accordingly
        target_width_px = new_width * 2
        image = resize_image(image, target_width_px)
        image = grayscale(image)
        braille_img = image_to_braille(image)
        print(braille_img)
    else:
        print(f"Unknown mode '{mode}'. Use 'ascii' or 'braille'.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ascii_generator.py <image_path> [width] [mode]")
        print("mode: ascii (default) or braille")
    else:
        path = sys.argv[1]
        width = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        mode = sys.argv[3].lower() if len(sys.argv) > 3 else 'ascii'
        main(path, width, mode)
