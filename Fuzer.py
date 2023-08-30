#! /usr/bin/env python

"""
Fuzer.py

This script takes a list of mp3 files on the command line, strips the ID3 tags
from them, concatenates them adds the ID3 tags from the first file to the
beginning (if they're v2 tags) or the end (if they're v1 tags) and saves the
file in the file name specified on the command line.

The files are combined in the order they appear on the command line.

Craig Amundsen
August 11, 2013
"""

import os
import sys

from mutagen.easyid3 import EasyID3

## Functions ##
def getOut(msg = ""):
    if msg:
        print("")
        print(msg)
    print("")
    print("Usage: Fuzer.py <list of mp3 files> newFileName")
    print("   OR: Fuzer.py --help")
    print("")
    sys.exit(0)
    ## getOut ##

def splitTagsFromMusic(mp3):
    """
    # splitTagsFromMusic(mp3)
    #
    # Takes an mp3 file (read into a String via an 'rb' open) and figures out
    # where the ID3 tags are and separates it from the mp3 portion of the mp3
    # file.
    #
    # Arguments:
    #  mp3 - the whole mp3 file
    #
    # Returns: (tagType, id3, mp3) where tag type is 'v1' or 'v2', id3 is the
    #          tag portion of the file, and mp3 is the sound portion of the
    #          file.
    """
    tags = None
    music = None
    if mp3.find(b'TAG') == 0:
        tagType = 'v1'
        tags = mp3[ : 128]
        music = mp3[128 : ]
    elif mp3.find(b'ID3') == 0:
        tagType = 'v2'
        # The tags are at the start of the file
        # v1 tags, 128 bytes long. Assuming extended v1 tags are not used
        tagSize = headerSize(mp3[6:10])
        tags = mp3[ : tagSize]
        music = mp3[tagSize : ]
    else:
        print("tags not at the start")
    return tagType, tags, music
    ## splitTagsFromMusic ##


def headerSize(sizeBytes):
    """
    # headerSize(sizeBytes)
    #
    # Takes bytes 6-10 of the tag section and calculates the size of the tag
    # portion.
    # 
    # Cut from spec:
    # The ID3 tag size is encoded with four bytes where the first bit (bit 7)
    # is set to zero in every byte, making a total of 28 bits. The zeroed bits
    # are ignored, so a 257 bytes long tag is represented as $00 00 02 01.
    #
    # Arguments:
    #  sizeBytes - the contents of bytes 6-10 of the tag portion of the file
    #
    # Returns: an int, the size of the tag region of the file
    """
    size = 0
    sizeList = list(sizeBytes)
    sizeList.reverse()
    for i, c in enumerate(sizeList):
        try:
            #size += pow(128, i) * ord(c)
            size += pow(128, i) * c
        except:
            print(f"type(c) = {type(c)}")
            print(f"c = {c}")
            print(f"ord(c) = {ord(c)}")
            raise
    return size
    ## headerSize ##


## Main ##
if __name__ == '__main__':
    if len(sys.argv) in (1, 3):
        getOut()
    if len(sys.argv) == 2:
        if sys.argv[1] in ('--help', '-h'):
            getOut(__doc__)
        else:
            getOut()

    outName = sys.argv[-1]
    inNames = sys.argv[1 : -1]

    problems = []
    problems += ['%s is not a file' % x for x in inNames if not os.path.isfile(x)]

    if os.path.isfile(outName):
        problems.append("%s already exists" % outName)

    if problems:
        getOut("\n".join(problems))

    print(f'{len(inNames)} files will be combined in this order:')
    for name in inNames:
        print(f'  {name}')
    print(f'{len(inNames)} files will be combined')
    answer = input("Continue?: [y]")
    if not answer:
        # Default to 'y'
        answer = 'y'
    if answer not in ('Y', 'y'):
        getOut("No file writen")

    soundParts = []
    trackMap = {}
    print('Reading files...')
    for i, name in enumerate(inNames):
        tagInfo = EasyID3(name)
        try:
            trackIndex, trackCount = [int(x) for x in tagInfo["tracknumber"][0].split("/")]
        except:
            print(tagInfo.keys())
            print("")
            raise
        try:
            discIndex, discCount = [int(x) for x in tagInfo["discnumber"][0].split("/")]
        except:
            print(sorted(tagInfo.keys()))
            print("")
            print(tagInfo["discnumber"][0])
            print("")
            raise

        discMax = None
        if trackMap:
            if discCount > max(trackMap.keys()):
                discMax = discCount
        else:
            discMax = discCount

        if discMax:
            for j in range(1, discMax + 1):
                if j not in trackMap:
                    trackMap[j] = {}

        trackMax = None
        if trackMap[discIndex]:
            if trackCount > max(trackMap[discIndex].keys()):
                trackMax = trackCount
        else:
            trackMax = trackCount

        if trackMax:
            for j in range(1, trackMax + 1):
                trackMap[discIndex][j] = None

        inf = open(name, 'rb')
        data = inf.read()
        if i == 0:
            tagType, tags, sound = splitTagsFromMusic(data)
        else:
            d1, d2, sound = splitTagsFromMusic(data)

        if trackMap[discIndex][trackIndex]:
            # We've already seen this track 
            problems.append("Disc %d, Track %d - more than one file" % (discIndex, trackIndex))

        trackMap[discIndex][trackIndex] = sound

        sys.stdout.write("*")
        if ((i + 1) % 100) == 0:
            sys.stdout.write("\n")
        sys.stdout.flush()
            
    for d in sorted(trackMap.keys()):
        for t in sorted(trackMap[d].keys()):
            if not trackMap[d][t]:
                problems.append("Disc %d, Track %d - no sound found" % (d, t))

    if problems:
        getOut("\n".join(problems))

    print(f"\n{tagType}  tags")

    print(f'Writing {outName}...')
    sys.stdout.flush()
    outf = open(outName, 'wb')
    if tagType == 'v2':
        outf.write(tags)
    i = 0
    for d in sorted(trackMap.keys()):
        for t in sorted(trackMap[d].keys()):
            outf.write(trackMap[d][t])

            sys.stdout.write("#")
            i += 1
            if (i % 100) == 0:
                sys.stdout.write("\n")
            sys.stdout.flush()
    if tagType == 'v1':
        outf.write(tags)
    outf.close()
    print('\nDone')
