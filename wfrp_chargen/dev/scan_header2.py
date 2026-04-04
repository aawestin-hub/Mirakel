"""Scan for white text (M WS BS...) in dark stats header."""
from PIL import Image
img = Image.open('templates/edited_front.png').convert('L')

# Stats header is dark background, white text
# Find the row y range first
print('Stats header: scanning for dark row at x=400, y=650-720:')
for y in range(650, 720):
    p = img.getpixel((400, y))
    print('  y=%d: %d' % (y, p))
