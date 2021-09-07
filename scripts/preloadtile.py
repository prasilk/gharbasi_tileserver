import math
import requests
import sys
import time

base_url = '127.0.0.1:8080/osm_tiles'

if '--help' in sys.argv or len(sys.argv) > 2:
    print """Preload tiles by making rest calls.

Syntax: preloadtile.py (url)

Tiles are fetched from http://(url)/{z}/{x}/{y}.jpg for regions defined in this
program.
"""
    sys.exit(0)
if len(sys.argv) > 1:
    base_url = sys.argv[1]

retries = 10

# The zones list contains an inclusive range of tiles [x0-x1][y0-y1] for a
# specific z level.  These are fetches for a given range of z levels [z0-z1].
# The tile numbers are scaled appropriately.  z, x0, x1, y0, y1 are used to
# determine the area of the world to fetch.  z0, z1 are used to determine the
# levels to fetch.  z0 and z1 do not need to include z.
#
# Zones may overlap.
zones = [{
    # California for levels 0-8
    'z': 7, 'x0': 18, 'x1': 24, 'y0': 47, 'y1': 51, 'z0': 0, 'z1': 8,
}, {
    # Los Angeles region for levels 0-16
    'z': 10, 'x0': 172, 'x1': 177, 'y0': 406, 'y1': 409, 'z0': 0, 'z1': 16,
}]

tiles = {}

for zone in zones:
    for z in range(zone['z0'], zone['z1'] + 1):
        Z = zone['z']
        x0 = int(zone['x0'] * 2 ** (z - Z))
        x1 = int(math.ceil(float(zone['x1'] + 1) * 2 ** (z - Z)))
        y0 = int(zone['y0'] * 2 ** (z - Z))
        y1 = int(math.ceil(float(zone['y1'] + 1) * 2 ** (z - Z)))
        for x in range(x0, x1):
            for y in range(y0, y1):
                tiles[(z, x, y)] = True
tiles = sorted(tiles.keys())
print 'z/x/y len req elapsed done'
done = 0
starttime = time.time()
lastlog = 0
for (z, x, y) in tiles:
    url = 'http://%s/%d/%d/%d.png' % (base_url, z, x, y)
    reqtime = time.time()
    for retry in xrange(retries):
        try:
            data = requests.get(url, timeout=10).text
        except Exception:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
            continue
        else:
            break
    done += 1
    curtime = time.time()
    if curtime - lastlog > 1:
        print '%d/%d/%d %d %3.1f %3.1f %4.2f (%d/%d)' % (
            z, x, y, len(data), curtime - reqtime, curtime - starttime,
            100.0 * done / len(tiles), done, len(tiles))
        lastlog = curtime
