"""Find stat column centers by scanning white text in dark header band."""
from PIL import Image
img = Image.open('templates/edited_front.png').convert('L')

# Dark band (stats header) is y=659-706. Scan for LIGHT pixels (>180) within it
# to find column separators/centers
print('Light pixels in stats header band y=659-706 at each x:')
col_light = {}
for x in range(280, 1700):
    lights = sum(1 for y in range(659, 706) if img.getpixel((x, y)) > 180)
    col_light[x] = lights

# Light columns = separators between stat cells (the vertical dividers in the dark header)
# A "separator" would be a narrow light column within the dark band
# Actually in a dark header, the TEXT letters are lighter and the background is dark
# Vertical rule lines between columns would also be lighter (grid lines)
# Let's find narrow light-column spikes (vertical separator lines)
# and wider light regions (stat name letter clusters)

# Find all x positions where most of the y pixels are light
threshold = 15  # out of 47 pixels being light
light_xs = [x for x, l in col_light.items() if l >= threshold]

# Group into bands
bands = []
i = 0
while i < len(light_xs):
    start = light_xs[i]
    while i+1 < len(light_xs) and light_xs[i+1] - light_xs[i] <= 3:
        i += 1
    end = light_xs[i]
    width = end - start + 1
    bands.append((start, end, (start+end)//2, width))
    i += 1

print('Light bands in header (potential stat name areas or dividers):')
for s,e,c,w in bands:
    print('  x=%d-%d center=%d width=%d' % (s, e, c, w))

# Identify which are narrow dividers vs wider name areas
print()
print('Wide light bands (stat name cells or column content areas):')
for s,e,c,w in bands:
    if w > 20:
        print('  x=%d-%d center=%d width=%d' % (s, e, c, w))
