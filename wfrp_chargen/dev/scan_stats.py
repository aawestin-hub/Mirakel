"""Scan stat column positions from the template."""
from PIL import Image
img = Image.open('templates/edited_front.png').convert('L')

print('Column dividers at y=730 (stats area):')
divs = []
for x in range(280, 1700):
    p = img.getpixel((x, 730))
    if p < 80:
        divs.append(x)

bands = []
i = 0
while i < len(divs):
    start = divs[i]
    while i+1 < len(divs) and divs[i+1] - divs[i] <= 3:
        i += 1
    end = divs[i]
    bands.append((start, end, (start+end)//2))
    i += 1

print('Dark bands (column dividers):')
for s,e,c in bands:
    print('  x=%d-%d center=%d' % (s, e, c))

print()
print('Column centers (between dividers):')
centers = [(bands[i][2]+bands[i+1][2])//2 for i in range(len(bands)-1)]
stat_names = ['M','WS','BS','S','T','W','I','A','Dex','Ld','Int','Cl','WP','Fel']
for i, c in enumerate(centers[:14]):
    name = stat_names[i] if i < len(stat_names) else '?'
    print('  %s: %d' % (name, c))

# Also check the y rows for STARTER/ADVANCE/CURRENT
print()
print('Row dividers at x=500 (within stats columns), y=700-900:')
for y in range(700, 900):
    p = img.getpixel((500, y))
    if p < 80:
        print('  y=%d: %d' % (y, p))
