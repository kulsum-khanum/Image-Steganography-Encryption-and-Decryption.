from PIL import Image

def to_bin(data):
    return ''.join(format(ord(i), '08b') for i in data)

def from_bin(binary):
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    return ''.join(chr(int(b, 2)) for b in chars)

def embed_data(image_path, data, output_path):
    img = Image.open(image_path)
    bin_data = to_bin(data) + '1111111111111110'
    pixels = img.getdata()
    new_pixels = []

    data_index = 0
    for pixel in pixels:
        if data_index < len(bin_data):
            r = (pixel[0] & ~1) | int(bin_data[data_index])
            data_index += 1
        else:
            r = pixel[0]
        new_pixels.append((r, *pixel[1:]))

    img.putdata(new_pixels)
    img.save(output_path)

def extract_data(image_path):
    img = Image.open(image_path)
    pixels = img.getdata()
    binary = ''
    for pixel in pixels:
        binary += str(pixel[0] & 1)
        if binary[-16:] == '1111111111111110':
            break
    return from_bin(binary[:-16])
