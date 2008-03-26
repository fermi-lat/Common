

## Acd tiles area, from Alex.
##
## 0-4, 16-20, 32-36, 48-52 (crown tiles) : 34 x 38cm = 1,292 cm2
## 5-9, 21-25, 37-41, 53-57 (sides, 2-nd row): 34 x 22 cm = 748 cm2
## 10-14, 26-30, 42-46, 53-57 (sides, 3-rd row) : 34 x 17 cm = 578 cm2
## 15, 31, 47, 63 (long tiles): 170 x 17 cm = 2,890 cm2
## 64-68, 84-88 (top bent tiles) : 40 x 34 cm = 1,360 cm2
## 69-83 (top 3 middle rows): 34 x 34 cm = 1,156 cm2 

def getAcdTileArea(tileNumber):
    if tileNumber in [0, 1, 2, 3, 4, 16, 17, 18, 19, 20, 32, 33, 34, 35, 36,
                      48, 49, 50, 51, 52]:
        return 1292.0
    elif tileNumber in [5, 6, 7, 8, 9, 21, 22, 23, 24, 25, 37, 38, 39, 40, 41,
                        53, 54, 55, 56, 57]:
        return 748.0
    elif tileNumber in [10, 11, 12, 13, 14, 26, 27, 28, 29, 30, 42, 43, 44, 45,
                        46, 53, 54, 55, 56, 57]:
        return 578.0
    elif tileNumber in [15, 31, 47, 63]:
        return 2890.0
    elif tileNumber in [64, 65, 66, 67, 68, 84, 85, 86, 87, 88]:
        return 1360.0
    elif tileNumber in range(69, 84):
        return 1156.0
    else:
        return 0

ACD_TILES_AREA = [getAcdTileArea(i) for i in range(128)]


if __name__ == '__main__':
    for (tileNumber, area) in  enumerate(ACD_TILES_AREA):
        print tileNumber, area


