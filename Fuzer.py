#! /usr/bin/env python

import os
import sys

import click
from mutagen.easyid3 import EasyID3

## Functions ##
def get_out(msg = ""):
    if msg:
        print("")
        print(msg)
    print("")
    print("Usage: Fuzer.py <list of mp3 files> newFileName")
    print("   OR: Fuzer.py --help")
    print("")
    sys.exit(0)
    ## get_out ##

def split_tags_from_sound(mp3):
    """
    # split_tags_from_sound(mp3)
    #
    # Takes an mp3 file (read into a String via an 'rb' open) and figures out
    # where the ID3 tags are and separates it from the mp3 portion of the mp3
    # file.
    #
    # Arguments:
    #  mp3 - the whole mp3 file
    #
    # Returns: (tag_type, id3, mp3) where tag type is 'v1' or 'v2', id3 is the
    #          tag portion of the file, and mp3 is the sound portion of the
    #          file.
    """
    tags = None
    music = None
    if mp3.find(b'TAG') == 0:
        tag_type = 'v1'
        tags = mp3[ : 128]
        music = mp3[128 : ]
    elif mp3.find(b'ID3') == 0:
        tag_type = 'v2'
        # The tags are at the start of the file
        # v1 tags, 128 bytes long. Assuming extended v1 tags are not used
        tagSize = header_size(mp3[6:10])
        tags = mp3[ : tagSize]
        music = mp3[tagSize : ]
    else:
        print("tags not at the start")
    return tag_type, tags, music
    ## split_tags_from_sound ##


def header_size(size_bytes):
    """
    # header_size(size_bytes)
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
    #  size_bytes - the contents of bytes 6-10 of the tag portion of the file
    #
    # Returns: an int, the size of the tag region of the file
    """
    size = 0
    sizeList = list(size_bytes)
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
    ## header_size ##


@click.command()
@click.argument('out_name', type=click.File('wb'))
@click.argument('in_names', type=click.File('rb'), nargs=-1)
def fuzer(out_name, in_names):
    """
    This script takes a list of mp3 files on the command line, strips the ID3
    tags concatenates the sound portions, adds the ID3 tags from the first file
    to the beginning (if they're v2 tags) or the end (if they're v1 tags) and
    saves the file in the file name specified on the command line.

    The input files are combined in the order specified by disk and track info
    in ID3 tags

    Arguments:

        out_name: the name of the file into which the input mp3 files are
        concatenated.

        in_names: the individual mp3 files that are going to be combined.
    """
    problems = []
    if os.path.isfile(out_name.name):
        # Don't overwrite an existing file
        get_out(f"{out_name.name} already exists")
    
    print("Checking tags for file ordering...")
    sound_parts = []
    track_map = {}
    for i, in_file in enumerate(in_names):
        file_name = os.path.basename(in_file.name)
        tag_info = EasyID3(in_file.name)

        total_discs = 0

        try:
            disc_index, disc_count = [int(x) for x in tag_info["discnumber"][0].split("/")]
        except:
            problems.append(f"{file_name} missing disc info")
            continue

        total_discs = max(disc_count, total_discs)
        if disc_index not in track_map:
            track_map[disc_index] = {}

        try:
            track_index, track_count = [int(x) for x in tag_info["tracknumber"][0].split("/")]
        except:
            problems.append(f"{file_name} missing track info")
            continue
        
        track_map[disc_index][track_index] = in_file

    if len(track_map) != total_discs:
        problems.append(f"Expected {total_discs} only found {len(track_map)}")

    if problems:
        get_out("\n".join(problems))
    
    for disc_index in track_map:
        max_track = max(track_map[disc_index].keys())
        if len(track_map[disc_index]) != max_track:
            problems.append(f"Disc {disc_index} expected {max_track} tracks only found {len(track_map[disc_index])}")
    if problems:
        get_out("\n".join(problems))

    is_first = True
    first_file_tags = None
    for disc_number in sorted(track_map):
        for track_number in sorted(track_map[disc_number]):
            in_file = track_map[disc_number][track_number]
            data = in_file.read()
            tag_type, tags, sound = split_tags_from_sound(data)
            if is_first:
                first_file_tags = tags
                is_first = False
            if tag_type == 'v2':
                out_name.write(first_file_tags)
            out_name.write(sound)
    if tag_type == "v1":
        out_name.write(first_file_tags)
            

## Main ##
if __name__ == '__main__':
    fuzer()