### The Lost Vikings
##   Python procedures to extract worlds and scenes

## Note: Required library: PIL


### Included procedures:
## Chunks:
##   getChunk                    .
##   getChunkOffset              .
##   decompressChunk             .
## Data:
##   readByte                    .
##   readInt16                   .
##   srcByteToHex                .
## Dictionary:
##   rle_table_read              .
##   rle_table_write             .
## Decompress chunk:
##   decompress                  .
## Build scene:
##   buildPalette                .
##   buildSpecialLevelScene      .
##   buildTileImage              .
##   buildLevelScene             .
##   buildLevelSceneTiles        .
## Read data from level:
##   readLevelHeader             .
##   readLevelObjects            .
##   readLevelPalettes           .
##   readLevelPaletteAnimations  .
##   readLevelUnpackedSpriteSets .
##   readLevelSprite32Sets       .
## Print procedures:
##   printArrayWithDescriptor    .Format level data for printout
##   printLevelData              .Format level data for printout
## Main procedures:
##   readLevel                   .
##   readWorlds                  .

##  Graphic procedures
## Build Scene:
##   buildScene                  .
##   buildSceneTiles             .



## Note: The Python code (this file) is presumed located in a sub-folder from the preceding files:
#   tlv/                      Root folder
#     DATA.DAT                 The Lost Vikings application binary library
#     data_dat.txt             Chunk descriptions
#     data_object_types.txt    Object descriptions
#    py/                      Program folder
#     tlv.py                   This file

	# Global
import os
from   array            import array
from   PIL              import Image, ImageOps


### The Lost Vikings Worlds
worlds = [
           ['Spaceship',  # Part 1 (Part 2 concludes game)
            449,
            [
             ['Level  1', 198, 'STRT'],
             ['Level  2', 200, 'GR8T'],
             ['Level  3', 202, 'TLPT'],
             ['Level  4', 204, 'GRND']
            ]
           ], # End of 'Spaceship'
           ['Caves',
            450,
            [
             ['Level  5',  40, 'LLM0'],
             ['Level  6',  42, 'FL0T'],
             ['Level  7',  44, 'TRSS'],
             ['Level  8',  46, 'PRHS'],
             ['Level  9',  48, 'CVRN'],
             ['Level 10',  50, 'BBLS'],
             ['Level 11',  52, 'VLCN']
            ]
           ], # End of 'Caves'
           ['Egypt',
            451,
            [
             ['Level 12',  75, 'QCKS'],
             ['Level 13',  77, 'PRH0'],
             ['Level 14',  79, 'C1R0'],
             ['Level 15',  81, 'SPKS'],
             ['Level 16',  83, 'JMNN'],
             ['Level 17',  85, 'TTRS']
            ]
           ], # End of 'Egypt'
           ['Construction',
            452,
            [
             ['Level 18', 114, 'JLLY'],
             ['Level 19', 116, 'PLNG'],
             ['Level 20', 118, 'BTRY'],
             ['Level 21', 120, 'JNKR'],
             ['Level 22', 122, 'CBLT'],
             ['Level 23', 124, 'H0PP'],
             ['Level 24', 126, 'SMRT'],
             ['Level 25', 128, 'V8TR']
            ]
           ], # End of 'Construction' (aka 'Factory')
           ['Candy' ,
            453,
            [
             ['Level 26', 156, 'NFL8'],
             ['Level 27', 158, 'WKKY'],
             ['Level 28', 160, 'CMB0'],
             ['Level 29', 162, '8BLL'],
             ['Level 30', 164, 'TRDR'],
             ['Level 31', 166, 'FNTM'],
             ['Level 32', 168, 'WRLR'],
             ['Level 33', 170, 'TRPD']
            ]
           ], # End of 'Candy' (aka 'Wacky')
           ['Spaceship',  # Part 2
            449,
            [
             ['Level 34', 206, 'TFFF'],
             ['Level 35', 208, 'FRGT'],
             ['Level 36', 210, '4RN4'],
             ['Level 37', 212, 'MSTR']
            ]
           ] # End of 'Spaceship' part 2
          ] # End of 'worlds'
            
specialWorlds = ['Special Worlds',
             454,
             [
              ['Special level?',         369, None],
              ['Special ',               381, None],
              ['Special ',               390, None],
              ['Silicon & Synapse logo', 396, None],
              ['Timewarp',               402, None],
              ['Special ',               382, None],
              ['Vikings home (intro)',   431, None],
              ['Vikings home (demo)',    432, None],
              ['Special ',               433, None],
              ['Vikings home (ending?)', 434, None],
              ['Viking ship ending',     218, None]
             ]
            ]
        
imagesPath                                   = '../images/'
pngExtension                                 = '.png'


# **********************************************************************************

### Immediate execution:
##   Note: Read and Load database: DATA.DAT (binary file)
##  File structure:
##   Table of offsets to chunks
##   Chunks
#     Variables:
dataOffsetBytesCount                         = 4    # offsets use 4 bytes
dataSrcFilePath                              = '../DATA.DAT'
dataSrcLength                                = os.path.getsize(dataSrcFilePath)
dataSrc                                      = array('B')
with open(dataSrcFilePath, 'rb') as f:
    dataSrc.fromfile(f, dataSrcLength)
dataChunksCount                              = int.from_bytes(dataSrc[0: dataOffsetBytesCount], byteorder='little', signed=False) >> 2


###   Data chunk procedures
def getChunk(chunkNo):
        # Start index
    chunkStartIndex                          = getChunkOffset(chunkNo)
        # End index
    chunkEndIndex                            = len(dataSrc)
    if (chunkNo < (dataChunksCount - 1)):
        chunkEndIndex                        = getChunkOffset(chunkNo + 1)
    chunkSrc                                 = dataSrc[chunkStartIndex: chunkEndIndex]
    return decompressChunk(chunkSrc)

def getChunkOffset(chunkNo):
    chunkStartIndexOffset                    = (chunkNo * dataOffsetBytesCount)
    return int.from_bytes(dataSrc[chunkStartIndexOffset: chunkStartIndexOffset + dataOffsetBytesCount], byteorder='little', signed=False)

def decompressChunk(chunkSrc):
        # Get and remove the length descriptor (first two(2) bytes)
    byte0                                    = chunkSrc.pop(0)
    byte1                                    = chunkSrc.pop(0)
    dataLength                               = ((byte1 << 8) + byte0)
    if (dataLength == len(chunkSrc)):
        return chunkSrc
    else:
        src                                  = decompress(chunkSrc)
        if (src == None):
            return chunkSrc
        else:
            return src


# ----------------------------------------------------------------------------------
### Immediate execution:
## Read chunk descriptors: data_dat.txt (text file)
# Expected structure example: '389(x0185)(  768): Palette (256 colors) used in world 7, level D'
#     Variables:
dataLinesSrc                                 = []
with open('../data_dat.txt', 'r') as f:
    dataLinesSrc                             = f.read()
dataLinesBulk                                = dataLinesSrc.split('\n')
    # Filter
chunkDescriptors                             = [''] * dataChunksCount
#     1: 
for dataLine in dataLinesBulk:
    if (dataLine[0:3].isnumeric()):
        chunkNo                              = int(dataLine[0:3])
        # Remove chunk No(int and hex) and location in 'DATA.DAT'
        index                                = dataLine.find(':')
        # Remove 'same as' data
        indexEqual                           = dataLine.find('=')
        if (indexEqual > -1):
            chunkDescriptors[chunkNo]        = dataLine[index + 1:indexEqual]
        else:
            chunkDescriptors[chunkNo]        = dataLine[index + 1:]


# ----------------------------------------------------------------------------------
### Immediate execution:
## Read object descriptors: data_object_types.txt (text file)
#   Expected structure example: 'Hx: Chk :..x..: Description'
#     Variables:
objectLinesSrc                               = []
#     1: 
with open('../data_object_types.txt', 'r') as f:
    objectLinesSrc                           = f.read()
#     2: 
objectLinesBulk                              = objectLinesSrc.split('\n')
objectDescriptors                            = ['...'] * 256
for objectLine in objectLinesBulk:
    s                                        = objectLine.split(':')
    if (len(s) > 1):
        sNo                                      = s[0].strip()
        no                                       = int(sNo, 16)
        objectDescriptors[no]                    = s[3]


# **********************************************************************************
# Utilities (when reading data)
def readByte(src, index):
    value                                    = src[index]
    index                                   += 1
    return index, value

def readInt16(src, index):
    value                                    = int.from_bytes(src[index: index + 2], byteorder='little', signed=False)
    index                                   += 2
    return index, value


# Utilities (when building description)
def srcByteToHex(byteValue):
    hexString                                = hex(byteValue)
    hexString                                = hexString[2:]
    hexString                                = hexString.upper()
    hexString                                = hexString.rjust(2,'0')
    return hexString


# **********************************************************************************
### ----- DECOMPRESSOR -----
##  Note: Except for chunks 0(first) and 536(last), all chunks are compressed
#     Catalog Variables:
RLE_MIN_LENGTH                               =    3
RLE_MAX_LENGTH                               =   18

table                                        = bytearray()
table_index                                  = 0
tableLength                                  = 0x1000    # 4096:
tableIndexLimit                              = 0x0fff    # 4095:

##   Catalog procedures
def rle_table_read(table, rle_index):
    byte                                     = table[rle_index]
    rle_index                               += 1
    rle_index                               &= tableIndexLimit
    return rle_index, byte

def rle_table_write(table, table_index, byte):
    table[table_index]                       = byte
    table_index                             += 1
    table_index                             &= tableIndexLimit
    return table, table_index


## Note: No need for a 'compressor' procedure in this context

def decompress(src):
    try:
        # Initialize dictionary.
        table                                = bytearray(tableLength)
        table_index                          = 0
        rle_index                            = 0
        dst                                  = array('B')
        # Initialize source offset
        src_offset                           = 0
        while (src_offset < len(src)):
            ctrl_byte                        = src[src_offset]
            src_offset                      += 1
            for bit in range(8):
                if (src_offset >= len(src)):
                    break
                #Read bits from right
                if (ctrl_byte & (1 << bit)):
                    # Get the next byte
                    byte                     = src[src_offset]
                    # (increment source index)
                    src_offset              += 1
                    dst.append(byte)
                    # Add to dictionary
                    table, table_index       = rle_table_write(table, table_index, byte)
                else:
                    # Get the next word
                    word                     = (src[src_offset + 1] << 8) | src[src_offset + 0]
                    #  (increment source index by 2)
                    src_offset              += 2
                    count                    = ((word & 0xf000) >> 12) + RLE_MIN_LENGTH
                    rle_index                = word & tableIndexLimit

                    for i in range(count):
                        rle_index, byte      = rle_table_read(table, rle_index)
                        table, table_index   = rle_table_write(table, table_index, byte)
                        dst.append(byte)
        return dst
    except:
        return None


# ##################################################################################
# Build (256-color) Palette
#  Incoming data example:
#    [Descriptor string, [paletteChunkNo, paletteOffset], ...]
#    ['Palettes           ', [172, 0], [3, 0], [3, 128], [291, 144], [292, 160], [229, 176], [282, 192], [276, 208], [279, 224], [220, 240]]
#  Note: paletteData values shifted right 2 bits to get actual color
def buildPalette(palettesData):
    palette                                  = [(0,0,0)] * 256
        # Remove header
    palettesData.pop(0)
        # Process data
    for paletteData in palettesData:
        paletteChunkNo                       = paletteData[0]
        paletteOffset                        = paletteData[1]
        paletteSrc                           = getChunk(paletteChunkNo)
        for i in range(0, len(paletteSrc), 3):
            r                                = paletteSrc[i + 0] << 2
            g                                = paletteSrc[i + 1] << 2
            b                                = paletteSrc[i + 2] << 2
            palette[paletteOffset]           = (r, g, b)
            paletteOffset                   += 1
    return palette


# ##################################################################################
# SCENE

# Special levels
def buildSpecialLevelScene(mapNo, paletteId, imageWidth):
    src                                      = getChunk(mapNo)
        # Image size
    imageHeight                              = round(len(src) / imageWidth)  #  Height may be 176 or 64
        # Build image colors
    paletteColors                            = loadPalette(paletteId)
    new_image_colors                         = []
    for index in range(len(src)):
        new_image_colors.append(paletteColors[src[index]])
        # Set new image
    img                                      = Image.new( mode = "RGB", size = (imageWidth, imageHeight))
    img.putdata(new_image_colors)
    return img


# Worlds levels
TILE_WIDTH                                   = 16
TILE_HEIGHT                                  = 16
TILE_PART_SIZE                               = 64

def buildTileImage(tilePartData, tileFlipHorizontal, tileFlipVertival, palette):
    processArray                             = [0] * len(tilePartData)
    tilePartDataIndex                        = -1
    for block in range(4):
        for row in range(8):
            for column in range(2):
                tilePartDataIndex           += 1
                processIndex                 = (row * 8) + (column * 4) + block
                processArray[processIndex]   = tilePartData[tilePartDataIndex]
        # Set tile part image
    tilePart_colors                          = []
    for index in range(len(processArray)):
        tilePart_colors.append(palette[processArray[index]])
    tilePartImage                            = Image.new( mode = "RGB", size = (8, 8))
    tilePartImage.putdata(tilePart_colors)
        # Mirror:
    if (tileFlipHorizontal > 0):
        tilePartImage                        = ImageOps.mirror(tilePartImage)
        # Flip:
    if (tileFlipVertival > 0):
        tilePartImage                        = ImageOps.flip(tilePartImage)
    return tilePartImage

# Build level scene image
def buildLevelScene(levelHeader, palette):
    columnsCount                             = levelHeader[5]
    rowsCount                                = levelHeader[6]
    mapNo                                    = levelHeader[7]
    tilesPartsNo                             = levelHeader[8]
    tilesOffsetsNo                           = levelHeader[9]

    sceneWidth                               = (columnsCount * TILE_WIDTH)
    sceneHeight                              = (rowsCount    * TILE_HEIGHT)
    
    mapSrc                                   = getChunk(mapNo)
    tilesOffsetsSrc                          = getChunk(tilesOffsetsNo)
    tilesPartsSrc                            = getChunk(tilesPartsNo)

    sceneImage                               = Image.new( mode = "RGB", size = (sceneWidth, sceneHeight))
    for row in range(rowsCount):
        for column in range(columnsCount):
            tileMapOffset                    = (((row * columnsCount) + column) * 2)
            tileIndex                        = mapSrc[tileMapOffset + 0]
            tileMode                         = mapSrc[tileMapOffset + 1]
            tileIndex                       += ((tileMode % 4) * 256)
            
            tilesOffsetsIndex                = (tileIndex * 8)
            tilesOffsetsArray                = tilesOffsetsSrc[tilesOffsetsIndex: tilesOffsetsIndex + 8]

            tileImage                        = Image.new( mode = "RGB", size = (16, 16))
            for tilePartRow in range(2):
                for tilePartColumn in range(2):
                    index                    = ((tilePartRow * 2) + tilePartColumn) * 2
                    tileDeclaredStartIndex   = int.from_bytes(tilesOffsetsArray[index: index + 2], "little")
                    tileParameters           = (tileDeclaredStartIndex % TILE_PART_SIZE)
                    tileSetStartIndex        = (tileDeclaredStartIndex - tileParameters)
                    tileFlipHorizontal       = tileParameters & 16
                    tileFlipVertival         = tileParameters & 32
                    tilePartData             = tilesPartsSrc[tileSetStartIndex: tileSetStartIndex + TILE_PART_SIZE]

                    tilePartImage            = buildTileImage(tilePartData, tileFlipHorizontal, tileFlipVertival, palette)
                    
                        # Paste tile part into tile
                    offset                   = ((tilePartColumn * 8), (tilePartRow * 8))
                    tileImage.paste(tilePartImage, offset)
                        # Paste tile part into tile
                    offset                   = ((tilePartColumn * 8), (tilePartRow * 8))
                    tileImage.paste(tilePartImage, offset)
            pixelY                           = (row    * TILE_HEIGHT)
            pixelX                           = (column * TILE_WIDTH)
            offset                           = (pixelX, pixelY)
            sceneImage.paste(tileImage, offset)
    return sceneImage

# Analyze/document tiles used in the scene
def buildLevelSceneTiles(levelHeader, palette, columnsCount, tilesSpacing):
    tilesPartsNo                             = levelHeader[8]
    tilesOffsetsNo                           = levelHeader[9]
    
    tilesOffsetsSrc                          = getChunk(tilesOffsetsNo)
    tilesPartsSrc                            = getChunk(tilesPartsNo)

    tilesCount                               = len(tilesOffsetsSrc) >> 3
    rowsCount                                = round(tilesCount / columnsCount)
    if ((rowsCount * columnsCount) < tilesCount):
        rowsCount                           += 1

    sceneWidth                               = (columnsCount * TILE_WIDTH)  + ((columnsCount - 1) * tilesSpacing)
    sceneHeight                              = (rowsCount    * TILE_HEIGHT) + ((rowsCount - 1)    * tilesSpacing)

    sceneImage                               = Image.new( mode = "RGB", size = (sceneWidth, sceneHeight))
    for tileIndex in range(tilesCount):
            # Locate tile in final image
        tileColumnIndex                      = (tileIndex % columnsCount)
        tileRowIndex                         = round((tileIndex - tileColumnIndex) / columnsCount)

        tilesOffsetsIndex                    = (tileIndex * 8)
        tilesOffsetsArray                    = tilesOffsetsSrc[tilesOffsetsIndex: tilesOffsetsIndex + 8]
        tileImage                            = Image.new( mode = "RGB", size = (16, 16))
            # Build tile from its four parts
        for tilePartRow in range(2):
            for tilePartColumn in range(2):
                index                        = ((tilePartRow * 2) + tilePartColumn) * 2
                tileDeclaredStartIndex       = int.from_bytes(tilesOffsetsArray[index: index + 2], "little")
                tileParameters               = (tileDeclaredStartIndex % TILE_PART_SIZE)
                tileSetStartIndex            = (tileDeclaredStartIndex - tileParameters)
                tileFlipHorizontal           = tileParameters & 16
                tileFlipVertival             = tileParameters & 32
                tilePartData                 = tilesPartsSrc[tileSetStartIndex: tileSetStartIndex + TILE_PART_SIZE]

                tilePartImage                = buildTileImage(tilePartData, tileFlipHorizontal, tileFlipVertival, palette)
                    # Paste tile part into tile
                offset                       = ((tilePartColumn * 8), (tilePartRow * 8))
                tileImage.paste(tilePartImage, offset)
        pixelY                               = (tileRowIndex    * (TILE_HEIGHT + tilesSpacing)) 
        pixelX                               = (tileColumnIndex * (TILE_WIDTH  + tilesSpacing))
        offset                               = (pixelX, pixelY)
        sceneImage.paste(tileImage, offset)
    return sceneImage


# ##################################################################################
# LEVEL
# 'readLevelHeader': called from 'readLevel' Procedure
def readLevelHeader(levelSrc):
    global levelHeader
    worldNo                                  = levelSrc[5]
    LevelNo                                  = levelSrc[22]
        # First part: Vikings positions
    levelIndex                               = 7    #  *** Skip to Vikings positions
    levelIndex, vikingsPositionFlag          = readByte(levelSrc, levelIndex)
    levelIndex, vikingsXoffset               = readInt16(levelSrc, levelIndex)
        # Vikings y offset processing: check for absolute or relative location
    levelIndex, vikingsYoffset               = readByte(levelSrc, levelIndex)
    levelIndex, flag                         = readByte(levelSrc, levelIndex)
    if (flag == 255):
        vikingsYoffset                       = -vikingsYoffset
    else:
        vikingsYoffset                      += (flag * 256)
    levelIndex                              += 2    # Skip 2 bytes
    levelIndex, vikingsFlags                 = readInt16(levelSrc, levelIndex)
        # Second part: Scene descriptor
    levelIndex                               = 41   #  *** Skip to scene descriptor offset
    levelIndex, tileColumnsCount             = readInt16(levelSrc, levelIndex)
    levelIndex, tileRowsCount                = readInt16(levelSrc, levelIndex)
    levelIndex                              += 1    # Skip 1 byte
    levelIndex, mapId                        = readInt16(levelSrc, levelIndex)
    levelIndex, tileOffsetsId                = readInt16(levelSrc, levelIndex)
    levelIndex, tileMapsId                   = readInt16(levelSrc, levelIndex)
        # Build header array
    levelHeader                              = ['World: ' + str(worldNo) + ', Level: ' + str(LevelNo).rjust(2, '0')]
    levelHeader.append(vikingsPositionFlag)
    levelHeader.append(vikingsXoffset)
    levelHeader.append(vikingsYoffset)
    levelHeader.append(vikingsFlags)
    levelHeader.append(tileColumnsCount)
    levelHeader.append(tileRowsCount)
    levelHeader.append(mapId)
    levelHeader.append(tileOffsetsId)
    levelHeader.append(tileMapsId)

# ----------------------------------------------------------------------------------
# 'readLevelObjects': called from 'readLevel' Procedure
# Object entries (14 bytes):
#   [00] u16: xoffset - 0xffff ends
#   [02] u16: yoffset
#   [04] u16: width / 2
#   [06] u16: height / 2
#   [08] u16: type (in object database)
#   [0a] u16: flags
#   [0c] u16: argument
objectsDatabase                              = [None] * 256

def readLevelObjects(levelSrc):
    global levelObjects
    levelIndex                               = 67   #  *** Skip to level Object Offset
    levelObjects                             = ['Objects            ']
    # Read first offset
    levelIndex, xoffset                      = readInt16(levelSrc, levelIndex)
    while (xoffset != 65535):
        levelIndex, yoffset                  = readInt16(levelSrc, levelIndex)
        levelIndex, halfWidth                = readInt16(levelSrc, levelIndex)
        levelIndex, halfHeight               = readInt16(levelSrc, levelIndex)
        levelIndex, objectType               = readInt16(levelSrc, levelIndex)
        levelIndex, objectFlags              = readInt16(levelSrc, levelIndex)
        levelIndex, objectArgument           = readInt16(levelSrc, levelIndex)

        objectTypeHex                        = 'x' + srcByteToHex(objectType)

        if (objectsDatabase[objectType] == None):
            objectsDatabase[objectType]      = [objectTypeHex, objectDescriptors[objectType], [[halfWidth, halfHeight]]]
        
        objectData                           = [xoffset, yoffset, halfWidth, halfHeight, objectTypeHex, objectFlags, objectArgument]
        objectData.append(' -->' + str(objectType).rjust(3) + ': ' + objectDescriptors[objectType])
        levelObjects.append(objectData)
        # Read next offset
        levelIndex, xoffset                  = readInt16(levelSrc, levelIndex)
    return levelIndex

# ----------------------------------------------------------------------------------
# 'readLevelPalettes': called from 'readLevel' Procedure
# Palette: Entries are 3 bytes:
#   [00]: u16: Chunk index - 0xffff ends
#   [02]:  u8:  Start index
def readLevelPalettes(levelSrc, levelIndex):
    global levelPalettes
    levelPalettes                            = ['Palettes           ']
    # Read first id
    levelIndex, paletteId                    = readInt16(levelSrc, levelIndex)
    while (paletteId != 65535):
        levelIndex, paletteOffset            = readByte(levelSrc, levelIndex)
        levelPalettes.append([paletteId, paletteOffset])
        # Read next id
        levelIndex, paletteId                = readInt16(levelSrc, levelIndex)
    return levelIndex

# ----------------------------------------------------------------------------------
# 'readLevelPaletteAnimations': called from 'readLevel' Procedure
# Palette Animations: Entries are 3 byte header, plus n u16 values:
#   [00]:     u8: Count down start - 0x00 ends
#   [01]:     u8: First color index
#   [02]:     u8: Second color index
#   [03]: u16[n]: Animation values - 0xffff ends
def readLevelPaletteAnimations(levelSrc, levelIndex):
    global levelAnimations
    # Skip 2 bytes
    levelIndex                              += 2
    levelAnimations                          = ['Palette Animations ']
    # Read first count down
    levelIndex, countDownStart           = readByte(levelSrc, levelIndex)
    while (countDownStart != 0):
        levelIndex, firstColorIndex          = readByte(levelSrc, levelIndex)
        levelIndex, secondColorIndex         = readByte(levelSrc, levelIndex)
        # Read animation values
        animationValues                      = []
        while (True):
            levelIndex, animationValue       = readInt16(levelSrc, levelIndex)
            if (animationValue == 65535):
                break
            else:
                animationValues.append(animationValue)
        levelAnimations.append([countDownStart, firstColorIndex, secondColorIndex])
        if (animationValues != []):
            levelAnimations.append(animationValues)
        # Read next count down
        levelIndex, countDownStart           = readByte(levelSrc, levelIndex)

    return levelIndex

# ----------------------------------------------------------------------------------
# 'readLevelUnpackedSpriteSets': called from 'readLevel' Procedure
# Unpacked Sprites: Entries are 6 bytes
#   [00] u16: Chunk index - 0xffff ends
#   [02] u16:
#   [04] u16:
def readLevelUnpackedSpriteSets(levelSrc, levelIndex):
    global levelUnpackedSprites
    levelUnpackedSprites                     = ['Unpacked Sprites   ']
    levelIndex, chunkIndex                   = readInt16(levelSrc, levelIndex)
    while (chunkIndex != 65535):
        levelIndex, chunkFirst               = readInt16(levelSrc, levelIndex)
        levelIndex, chunkSecond              = readInt16(levelSrc, levelIndex)
        levelUnpackedSprites.append([chunkIndex, chunkFirst, chunkSecond])
        levelIndex, chunkIndex               = readInt16(levelSrc, levelIndex)
    return levelIndex

# ----------------------------------------------------------------------------------
# 'readLevelSprite32Sets': called from 'readLevel' Procedure
# Sprites 32: Entries are 5 bytes:
#   [00] u16: Chunk index - 0xffff ends
#   [02]  u8: Unknown
#   [03]  u8: Unknown
#   [04]  u8: Unknown
def readLevelSprite32Sets(levelSrc, levelIndex):
    global levelSprites32
    levelSprites32                           = ['Sprite32           ']
    levelIndex, chunkIndex                   = readInt16(levelSrc, levelIndex)
    while (chunkIndex != 65535):
        levelIndex, chunkFirst               = readByte(levelSrc, levelIndex)
        levelIndex, chunkSecond              = readByte(levelSrc, levelIndex)
        levelIndex, chunkThird               = readByte(levelSrc, levelIndex)
        levelSprites32.append([chunkIndex, chunkFirst, chunkSecond, chunkThird])
        levelIndex, chunkIndex               = readInt16(levelSrc, levelIndex)

# ----------------------------------------------------------------------------------
# LEVEL Top Procedure
#  Variables
levelHeader                                  = []
levelObjects                                 = []
levelPalettes                                = []
levelAnimations                              = []
levelUnpackedSprites                         = []
levelSprites32                               = []



def printArrayWithDescriptor(thisArray, isUsingDescriptor, index):
    s                                        = '['
    s                                       += ' '.join(str(e).rjust(4,' ') for e in thisArray)
    s                                       += ']'
    if (isUsingDescriptor):
        theIndex                             = thisArray[index]
        if (index == 0):
            s                               += ' ' + chunkDescriptors[theIndex]
        else:
            s                               += ' ' + objectDescriptors[theIndex]
    print(s)
    
# Called from procedure 'buildLevel' below
def printLevelData(thisLevelData, isDescriptor, index):
    print(thisLevelData.pop(0))
    for thisData in thisLevelData:
        printArrayWithDescriptor(thisData, isDescriptor, index)


# Procedure
def readLevel(levelId, isDebug):
    levelSrc                                 = getChunk(levelId)
        # Process
    readLevelHeader(levelSrc)
    levelIndex                               = readLevelObjects(levelSrc)
    levelIndex                               = readLevelPalettes(levelSrc, levelIndex)
    levelIndex                               = readLevelPaletteAnimations(levelSrc, levelIndex)
    levelIndex                               = readLevelUnpackedSpriteSets(levelSrc, levelIndex)
    readLevelSprite32Sets(levelSrc, levelIndex)
    
    if (isDebug):
        print('DEBUG:')
        print(levelHeader)
        printLevelData(levelObjects,         False, 4)
        printLevelData(levelPalettes,        True,  0)
        printLevelData(levelAnimations,      False, 0)
        printLevelData(levelUnpackedSprites, True,  0)
        printLevelData(levelSprites32,       True,  0)

# ***** Test Call *****:
#readLevel(198, True)


# ##################################################################################
#          ----- WORLD -----
# Used to gather data from all levels

def readWorlds():
    global objectsDatabase
    objectsDatabase                          = [None] * 256
    for worldData in worlds:
        worldName                            = worldData[0]
        levels                               = worldData[2]
        for level in levels:
            levelName                        = level[0]
            levelNo                          = level[1]
            readLevel(levelNo, False)
            print(levelHeader[0] + ', chunk ' + str(levelNo))
   
    print()
    print()
    print('objectsDatabase:')
    for index in range(len(objectsDatabase)):
        objectData                           = objectsDatabase[index]
        if objectData == None:
            print('[' + format(index, '#04x') + ']')
        else:
            print(objectData)

    print()
    print('Done:')

# ***** Test Call *****:
#readWorlds()


# ##################################################################################
#          ----- SCENE -----

def buildScene(levelId):
    readLevel(levelId, None)

        # Build palette
    palette                                  = buildPalette(levelPalettes)
    tilesOffsetsNo                           = levelHeader[8]
    if (tilesOffsetsNo == 65535):
        mapNo                                = levelHeader[7]
        sceneImage                           = buildSpecialLevelScene(mapNo, palette)
    else:
        sceneImage                           = buildLevelScene(levelHeader, palette)
    # TEMPORARY: Save level image in test directory
    sceneImage.save(imagesPath + str(levelId) + pngExtension)
    print('buildScene is done:')
    
## ***** Test Call *****:
# buildScene(198)



def buildSceneTiles(levelId, columnsCount, tilesSpacing):
    readLevel(levelId, None)
    tilesOffsetsNo                           = levelHeader[8]
    if (tilesOffsetsNo < 65535):
        palette                              = buildPalette(levelPalettes)
        sceneImage                           = buildLevelSceneTiles(levelHeader, palette, columnsCount, tilesSpacing)
        # TEMPORARY: Save level image in test directory
        sceneImage.save(imagesPath + str(levelId) + '_tiles' + pngExtension)
    print('buildSceneTiles is done')

## ***** Test Call *****:
# buildSceneTiles(198, 10, 4)

# ##################################################################################

# -\\-

