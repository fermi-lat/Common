
import sys
import pUtils

## @var ACD_CROWN_TILES
## @brief Information from Alex:
#  0-4, 16-20, 32-36, 48-52 (crown tiles) : 34 x 38cm = 1,292 cm2

## @var ACD_SIDE_ROW_2_TILES
## @brief Information from Alex:
#  5-9, 21-25, 37-41, 53-57 (sides, 2-nd row): 34 x 22 cm = 748 cm2
## @todo I guess 53-57 is really 58-62. Double check that with Alex.

## @var ACD_SIDE_ROW_3_TILES
## @brief Information from Alex:
#  10-14, 26-30, 42-46, 53-57 (sides, 3-rd row) : 34 x 17 cm = 578 cm2

## @var ACD_LONG_TILES
## @brief Information from Alex:
#  15, 31, 47, 63 (long tiles): 170 x 17 cm = 2,890 cm2

## @var ACD_TOP_BENT_TILES
## @brief Information from Alex:
#  64-68, 84-88 (top bent tiles) : 40 x 34 cm = 1,360 cm2

## @var ACD_TOP_MIDDLE_TILES
## @brief Information from Alex:
#  69-83 (top 3 middle rows): 34 x 34 cm = 1,156 cm2

## @var ACD_RIBBONS
## @brief 96-103: ~600 cm2.
#  This is an educated guess taken from the rates as they appear in the
#  data quality monitoring products (after all we need it for normalizing
#  things, so a reasonable "effective area" should be file).
## @todo Double check area with Alex.

## @var ACD_UNPHYSICAL_TILES
## @brief The unphysical tile ids showing up in the data monitoring quantities.

ACD_CROWN_TILES      = pUtils.expandList('0-4, 16-20, 32-36, 48-52')
ACD_SIDE_ROW_2_TILES = pUtils.expandList('5-9, 21-25, 37-41, 58-62')
ACD_SIDE_ROW_3_TILES = pUtils.expandList('10-14, 26-30, 42-46, 53-57')
ACD_LONG_TILES       = pUtils.expandList('15, 31, 47, 63')
ACD_TOP_BENT_TILES   = pUtils.expandList('64-68, 84-88')
ACD_TOP_MIDDLE_TILES = pUtils.expandList('69-83')
ACD_RIBBONS          = pUtils.expandList('96-103')
ACD_UNPHYSICAL_TILES = pUtils.expandList('89-95, 104-127')

## @brief Return the area of the tile corresponding to a given tile number.
## @param tileNumber
## The tile number.

def getAcdTileArea(tileNumber):
    if tileNumber in ACD_CROWN_TILES:
        return 1292.0
    elif tileNumber in ACD_SIDE_ROW_2_TILES:
        return 748.0
    elif tileNumber in ACD_SIDE_ROW_3_TILES:
        return 578.0
    elif tileNumber in ACD_LONG_TILES:
        return 2890.0
    elif tileNumber in ACD_TOP_BENT_TILES:
        return 1360.0
    elif tileNumber in ACD_TOP_MIDDLE_TILES:
        return 1156.0
    elif tileNumber in ACD_RIBBONS:
        return 600.
    elif tileNumber in ACD_UNPHYSICAL_TILES:
        return 0
    else:
        sys.exit('Tile number %d out of range. Abort.' % tileNumber)

## @var ACD_TILES_AREA
## @brief List of the tiles area, by tile number.

## @var ACD_AVERAGE_TILE_AREA
## @brief The average (weighted with the number of tiles for each given area)
#  ACD tile area.

## @var ACD_TILE_NORM_FACTOR
## @brief The normalization factor (tile area/average area for each acd tile).

ACD_TILES_AREA = [getAcdTileArea(i) for i in range(128)]
ACD_AVERAGE_TILE_AREA = sum(ACD_TILES_AREA)/128
ACD_TILE_NORM_FACTOR = [ACD_TILES_AREA[i]/ACD_AVERAGE_TILE_AREA\
                        for i in range(128)]



if __name__ == '__main__':
    print 'ACD_CROWN_TILES:'     , ACD_CROWN_TILES
    print 'ACD_SIDE_ROW_2_TILES:', ACD_SIDE_ROW_2_TILES
    print 'ACD_SIDE_ROW_3_TILES:', ACD_SIDE_ROW_3_TILES
    print 'ACD_LONG_TILES:'      , ACD_LONG_TILES
    print 'ACD_TOP_BENT_TILES:'  , ACD_TOP_BENT_TILES
    print 'ACD_TOP_MIDDLE_TILES:', ACD_TOP_MIDDLE_TILES
    print 'ACD_RIBBONS:'         , ACD_RIBBONS
    print 'ACD_UNPHYSICAL_TILES:', ACD_UNPHYSICAL_TILES
    print 'Total number of defined tiles: %d' %\
          len(ACD_CROWN_TILES + ACD_SIDE_ROW_2_TILES + ACD_SIDE_ROW_3_TILES +\
              ACD_LONG_TILES + ACD_TOP_BENT_TILES + ACD_TOP_MIDDLE_TILES +\
              ACD_RIBBONS + ACD_UNPHYSICAL_TILES)
    print
    print 'ACD_AVERAGE_TILE_AREA: ', ACD_AVERAGE_TILE_AREA
    print 'ACD_TILE_NORM_FACTOR:', ACD_TILE_NORM_FACTOR
    print 'Tile\tArea\tnormalization'
    for (tileNumber, area) in  enumerate(ACD_TILES_AREA):
        print '%s\t%s\t%s' % (tileNumber, area,\
                              ACD_TILE_NORM_FACTOR[tileNumber])

