"""Scan stats header row to find precise column centers."""
from PIL import Image
img = Image.open('templates/edited_front.png').convert('L')

# Find stats header row (the row with M WS BS S T W I A Dex Ld Int Cl WP Fel)
# This is just above the STARTER PROFILE row
# First find the row y position
print('Stats header region scan at x=500:')
for y in range(660, 720):
    p = img.getpixel((500, y))
    if p < 120:
        print('  y=%d: %d' % (y, p))

# Scan the actual column header text positions at y=706 (stats header row)
# Dark regions = text characters of M, WS, BS etc.
print()
print('Dark clusters in stats header at y=706 (stat column headers):')
divs = []
for x in range(280, 1700):
    p = img.getpixel((x, 706))
    if p < 80:
        divs.append(x)

bands = []
i = 0
while i < len(divs):
    start = divs[i]
    while i+1 < len(divs) and divs[i+1] - divs[i] <= 5:
        i += 1
    end = divs[i]
    bands.append((start, end, (start+end)//2))
    i += 1
print('Bands:')
for s,e,c in bands:
    print('  x=%d-%d center=%d' % (s, e, c))

# Also scan at y=695 for border of header row
print()
print('Column dividers at y=695 (between header and stats):')
divs2 = []
for x in range(280, 1700):
    p = img.getpixel((x, 695))
    if p < 80:
        divs2.append(x)
bands2 = []
i = 0
while i < len(divs2):
    start = divs2[i]
    while i+1 < len(divs2) and divs2[i+1] - divs2[i] <= 3:
        i += 1
    end = divs2[i]
    bands2.append((start, end, (start+end)//2))
    i += 1
print('Bands at y=695:')
for s,e,c in bands2:
    print('  x=%d-%d center=%d' % (s, e, c))
