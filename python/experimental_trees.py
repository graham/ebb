from trees import *

START=len(TYPES)

EXTRA = {
    'geo':START+1,
    'set':START+2,
    'zset':START+3,
    'log':START+4,
    'url':START+5,
}

class GeoNode(
