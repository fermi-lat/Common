
import sys
import pUtils

## @var ACD_CROWN_TILES
## @brief Information from Alex: 0-4, 16-20, 32-36, 48-52 (crown tiles)

## @var ACD_SIDE_ROW_2_TILES
## @brief Information from Alex: 5-9, 21-25, 37-41, 53-57 (sides, 2-nd row)
## @todo I guess 53-57 is really 58-62. Double check that with Alex.

## @var ACD_SIDE_ROW_3_TILES
## @brief Information from Alex: 10-14, 26-30, 42-46, 53-57 (sides, 3-rd row)

## @var ACD_LONG_TILES
## @brief Information from Alex: 15, 31, 47, 63 (long tiles)

## @var ACD_TOP_BENT_TILES
## @brief Information from Alex: 64-68, 84-88 (top bent tiles)

## @var ACD_TOP_MIDDLE_TILES
## @brief Information from Alex: 69-83 (top 3 middle rows)

## @var ACD_RIBBONS
## @brief 96-103

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

## @var ACD_CROWN_TILES
## @brief Information from Alex: 34 x 38cm = 1,292 cm2

## @var ACD_SIDE_ROW_2_TILES
## @brief Information from Alex: 34 x 22 cm = 748 cm2

## @var ACD_SIDE_ROW_3_TILES
## @brief Information from Alex: 34 x 17 cm = 578 cm2

## @var ACD_LONG_TILES
## @brief Information from Alex: 170 x 17 cm = 2,890 cm2

## @var ACD_TOP_BENT_TILES
## @brief Information from Alex: 40 x 34 cm = 1,360 cm2

## @var ACD_TOP_MIDDLE_TILES
## @brief Information from Alex: 34 x 34 cm = 1,156 cm2

## @var ACD_RIBBONS
## @brief ~600 cm2 is an educated guess taken from the rates as they appear
#  in the data quality monitoring products (after all we need it for
#  normalizing things, so a reasonable "effective area" should be file).
## @todo Double check area with Alex.

## @var ACD_UNPHYSICAL_TILES
## @brief The unphysical tile ids showing up in the data monitoring quantities.

ACD_CROWN_TILES_AREA      = 1292.0
ACD_SIDE_ROW_2_TILES_AREA = 748.0
ACD_SIDE_ROW_3_TILES_AREA = 578.0
ACD_LONG_TILES_AREA       = 2890.0
ACD_TOP_BENT_TILES_AREA   = 1360.0
ACD_TOP_MIDDLE_TILES_AREA = 1156.0
ACD_RIBBONS_AREA          = 600.0
ACD_UNPHYSICAL_TILES_AREA = 0.0

## @var ACD_NORM_AREA
## @brief The area the tiles surface is normalized to.
#  In principle we could have choosen whatever area as a normalization
#  (including the average tile area). We choose the @ref ACD_CROWN_TILES_AREA
#  variable as tile 0 corresponds to that group and it may be handy, while
#  setting alarm limits, just look at the first tile amd normalize all the
#  others accordingly.

ACD_NORM_AREA = ACD_CROWN_TILES_AREA

## @var ACD_CROWN_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_CROWN_TILES group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_SIDE_ROW_2_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_ACD_SIDE_ROW_2_TILES group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_SIDE_ROW_3_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_SIDE_ROW_3_TILES group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_LONG_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_LONG_TILES group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_TOP_BENT_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_TOP_BENT_TILES group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_TOP_MIDDLE_TILE_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_TOP_MIDDLE_TILE group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_RIBBONS_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_RIBBONS group.
#  Used as a multiplicative factor for the alarm limits.

## @var ACD_UNPHYSICAL_TILES_NORM_FACTOR
## @brief Normalization factor for the @ref ACD_UNPHYSICAL_TILES group.
#  Used as a multiplicative factor for the alarm limits.

ACD_CROWN_TILES_NORM_FACTOR      = ACD_CROWN_TILES_AREA/ACD_NORM_AREA
ACD_SIDE_ROW_2_TILES_NORM_FACTOR = ACD_SIDE_ROW_2_TILES_AREA/ACD_NORM_AREA
ACD_SIDE_ROW_3_TILES_NORM_FACTOR = ACD_SIDE_ROW_3_TILES_AREA/ACD_NORM_AREA
ACD_LONG_TILES_NORM_FACTOR       = ACD_LONG_TILES_AREA/ACD_NORM_AREA
ACD_TOP_BENT_TILES_NORM_FACTOR   = ACD_TOP_BENT_TILES_AREA/ACD_NORM_AREA
ACD_TOP_MIDDLE_TILES_NORM_FACTOR = ACD_TOP_MIDDLE_TILES_AREA/ACD_NORM_AREA
ACD_RIBBONS_NORM_FACTOR          = ACD_RIBBONS_AREA/ACD_NORM_AREA
ACD_UNPHYSICAL_TILES_NORM_FACTOR = ACD_UNPHYSICAL_TILES_AREA/ACD_NORM_AREA

## @brief Return the area of the tile corresponding to a given tile number.
## @param tileNumber
## The tile number.

def getAcdTileArea(tileNumber):
    if tileNumber in ACD_CROWN_TILES:
        return ACD_CROWN_TILES_AREA
    elif tileNumber in ACD_SIDE_ROW_2_TILES:
        return ACD_SIDE_ROW_2_TILES_AREA
    elif tileNumber in ACD_SIDE_ROW_3_TILES:
        return ACD_SIDE_ROW_3_TILES_AREA
    elif tileNumber in ACD_LONG_TILES:
        return ACD_LONG_TILES_AREA
    elif tileNumber in ACD_TOP_BENT_TILES:
        return ACD_TOP_BENT_TILES_AREA
    elif tileNumber in ACD_TOP_MIDDLE_TILES:
        return ACD_TOP_MIDDLE_TILES_AREA
    elif tileNumber in ACD_RIBBONS:
        return ACD_RIBBONS_AREA
    elif tileNumber in ACD_UNPHYSICAL_TILES:
        return ACD_UNPHYSICAL_TILES_AREA
    else:
        sys.exit('Tile number %d out of range. Abort.' % tileNumber)



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
    print 'ACD_CROWN_TILES_NORM_FACTOR:'     , ACD_CROWN_TILES_NORM_FACTOR
    print 'ACD_SIDE_ROW_2_TILES_NORM_FACTOR:', ACD_SIDE_ROW_2_TILES_NORM_FACTOR
    print 'ACD_SIDE_ROW_3_TILES_NORM_FACTOR:', ACD_SIDE_ROW_3_TILES_NORM_FACTOR
    print 'ACD_LONG_TILES_NORM_FACTOR:'      , ACD_LONG_TILES_NORM_FACTOR
    print 'ACD_TOP_BENT_TILES_NORM_FACTOR:'  , ACD_TOP_BENT_TILES_NORM_FACTOR
    print 'ACD_TOP_MIDDLE_TILES_NORM_FACTOR:', ACD_TOP_MIDDLE_TILES_NORM_FACTOR
    print 'ACD_RIBBONS_NORM_FACTOR:'         , ACD_RIBBONS_NORM_FACTOR
    print 'ACD_UNPHYSICAL_TILES_NORM_FACTOR:', ACD_UNPHYSICAL_TILES_NORM_FACTOR
    
