#! /usr/bin/env python

"""
Standalone and callable routine that combines multiple mp3 files into one big
file. It can either use the disk and track number info to order the files or
use the order the files were presented on the command line. Optionally a cover
image can be added and the name of the final file specified. See the doc-string
for the fuzer function below for more details.
"""

from io import BufferedReader
import os
import re
import sys

import click
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3


class TrackError(Exception):
    def __init__(self, problems):
        sys.tracebacklimit = 0  # Don't show traceback for this exception
        self.problems = problems
        self.problem_string = "\n".join(problems)
        self.message = self.problem_string
        super().__init__(self.message)


class AlreadyExistsError(Exception):
    def __init__(self, file_name):
        sys.tracebacklimit = 0  # Don't show traceback for this exception
        self.file_name = file_name
        self.message = f"{self.file_name} already exists. Delete or move it"
        super().__init__(self.message)


## Functions ##
def split_tags_from_sound(mp3:BufferedReader) -> tuple[str, bytes, bytes]:
    """
    # split_tags_from_sound(mp3)
    #
    # Takes an mp3 file (read into a String via an "rb" open) and figures out
    # where the ID3 tags are and separates it from the mp3 portion of the mp3
    # file.
    #
    # Arguments:
    #  mp3 - the whole mp3 file
    #
    # Returns: (tag_type, id3, mp3) where tag type is "v1" or "v2", id3 is the
    #          tag portion of the file, and mp3 is the sound portion of the
    #          file.
    """
    tags = None
    music = None
    #mp3_contents = mp3.read()
    #if mp3_contents.find(b"TAG") == 0:
    if mp3.find(b"TAG") == 0:
        tag_type = "v1"
        #tags = mp3_contents[:128]
        #music = mp3_contents[128:]
        tags = mp3[:128]
        music = mp3[128:]
    #elif mp3_contents.find(b"ID3") == 0:
    elif mp3.find(b"ID3") == 0:
        tag_type = "v2"
        # The tags are at the start of the file
        # v1 tags, 128 bytes long. Assuming extended v1 tags are not used
        #tagSize = header_size(mp3_contents[6:10])
        #tags = mp3_contents[:tagSize]
        #music = mp3_contents[tagSize:]
        tagSize = header_size(mp3[6:10])
        tags = mp3[:tagSize]
        music = mp3[tagSize:]
    else:
        print("tags not at the start")
    return tag_type, tags, music
    ## split_tags_from_sound ##


def header_size(size_bytes:bytes) -> int:
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
            # size += pow(128, i) * ord(c)
            size += pow(128, i) * c
        except:
            print(f"type(c) = {type(c)}")
            print(f"c = {c}")
            print(f"ord(c) = {ord(c)}")
            raise
    return size
    ## header_size ##


def sort_tracks(source_files:list[click.File], in_file_order:bool) -> list[click.File]:
    """
    Constructs a dictionary of dictionaries where the outer keys the disc
    numbers and the keys of the inner dictionaries are the track numbers.
    The values are the click-File ("rb") files passed in the command line.
    Generally, the disc and track numbers will be read from the ID3 tags in the
    files and error checking to ensure that there are no gaps in the disc or
    track numbers. The User, though is allowed to specify that the tracks
    should be combined in the order in which they were presented on the command
    line. In this case, the outer dictionary has a single disc key of 1 and the
    inner dictionary keys are the index of the file as passed in by the
    Given the list of click.File ("rb") input mp3 files, reads the ID3 tags to
    determine the order of the tracks and saves a dictionary keyed on disc
    number, with sub-dictionaries keyed on track number with values that are
    individual mp3 files.

    Arguments:
        source_files: a list of click.File instances that are the mp3 files that
        are being combined
        in_file_order: Boolean, if True return the source_files in the order they
        appeared on the command line, if False sort the source_files by disc and
        track order in the ID3 tags

    Returns: a list of the source files in the order in which they should be
    concatenated

    Side Effects: If any problmes are encountered, missing track numbers, disc
    numbers, etc, the program exits after printing the list of problems encountered
    """
    if in_file_order:
        print("Using the command line order...")
        return source_files

    print("Checking tags for file ordering...")
    problems = []
    track_map = {}
    tracks_per_disc = {}
    track_list = []
    for in_file in source_files:
        file_name = os.path.basename(in_file)
        tag_info = EasyID3(in_file)

        total_discs = None

        try:
            disc_index, disc_count = [
                int(x) for x in tag_info["discnumber"][0].split("/")
            ]
        except (TrackError, KeyError):
            problems.append(f"{file_name} missing disc info")
            continue

        if not total_discs:
            total_discs = disc_count
        elif total_discs != disc_count:
            raise TrackError([f"Disc count mismatch {total_discs} != {disc_count}"])
        if disc_index not in track_map:
            track_map[disc_index] = {}

        try:
            track_index, track_count = [
                int(x) for x in tag_info["tracknumber"][0].split("/")
            ]
        except (TrackError, KeyError):
            problems.append(f"{file_name} missing track info")
            continue

        if disc_index not in tracks_per_disc:
            tracks_per_disc[disc_index] = track_count
        elif tracks_per_disc[disc_index] != track_count:
            raise TrackError(
                [
                    f"Disc {disc_index} has mutliple total tracks values {tracks_per_disc[disc_index]}, {track_count}"
                ]
            )

        track_map[disc_index][track_index] = in_file

    if len(track_map) != total_discs:
        problems.append(f"Expected {total_discs} discs only found {len(track_map)}")

    for d in sorted(tracks_per_disc):
        if tracks_per_disc[d] != len(track_map[d]):
            problems.append(
                f"Tag Error: Disc {d} should have {tracks_per_disc[d]} tracks only {len(track_map[d])} found"
            )

    if problems:
        raise TrackError(problems)

    for disc_index in track_map:
        max_track = max(track_map[disc_index].keys())
        if len(track_map[disc_index]) != max_track:
            problems.append(
                f"Disc {disc_index} expected {max_track} tracks only found {len(track_map[disc_index])}"
            )
    if problems:
        raise TrackError(problems)

    for d in sorted(track_map):
        for t in sorted(track_map[d]):
            track_list.append(track_map[d][t])

    return track_list
    ## sort_tracks ##


def get_output_file_name(a_file:click.File) -> str:
    """
    Reads the album tag from an input mp3 file and generates a safe output file
    name

    Arguments:
        a_file - one of the input mp3 files

    Returns: a string, that should be a safe name that is based on the album tag
    in the file
    """
    source_tags = EasyID3(a_file)
    album = source_tags["album"][0]
    album = re.sub("[^0-9a-zA-Z]+", "_", album)
    return album + ".mp3"


def write_file(tracks:list[click.File], out_name:str) -> None:
    """
    Given the list of tracks, combines all the individual mp3 files into
    one big file.

    Arguments:
        tracks: the list containing all the tracks to be combined
        out_name: the click.File opened in "wb" mode into which the mp3 files
        from the tracks dictionary are combined.
    """
    print(f"Writing tracks to {out_name}...")
    for in_file in tracks:
        with open(in_file, "rb") as inf:
            data = inf.read()
        _, _, sound = split_tags_from_sound(data)
        out_name.write(sound)
    ## write_file ##


def add_tags(first_file:str, output_file:str) -> None:
    """
    Copies the tags from the first input file to the output file and sets title tag
    to the album tag as well as the the tracknumber and discnumber tags to 1/1.

    Arguments:
        first_file: the path to the first input file, from which the tags are
        obtained.
        output_file: the name of the mp3 file.
    """
    print("Adding basic tags...")
    destination_tags = mutagen.File(output_file, easy=True)
    source_tags = EasyID3(first_file)
    for tag in source_tags:
        destination_tags[tag] = source_tags[tag]
    destination_tags["title"] = destination_tags["album"]
    destination_tags["tracknumber"] = ["1/1"]
    destination_tags["discnumber"] = ["1/1"]
    destination_tags.save(v2_version=4)
    ## add_tags ##


def add_cover_art(output_file:str, cover_file:click.File) -> None:
    """
    Adds a cover image to the mp3 that was created

    Arguments:
        output_file: the name of the output file (not a click.File)
        cover_file: a jpeg image file that is a click.File in "rb" mode
    """
    print("Adding cover art...")
    album_art = cover_file.read()
    audio = MP3(output_file, ID3=ID3)
    audio.tags.add(
        APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=album_art)
    )
    audio.save(v2_version=4)
    ## add_cover_art ##


def run_fuzer(
    source_files,
    cover=None,
    title=None,
    dest_dir=None,
    file_order=False,
    raise_exceptions=True,
) -> str|None:
    """
    This function actually does the work described in fuzer.

    Arguments:
        source_files: the individual mp3 files that are going to be combined.
        cover: optional, jpeg file containing a cover image for the combined files
        title: optional, if set it is the name of the output file, otherwise the file
        name is generated from the title tag of the first file
        dest_dir: optional, if set the directory where the new file should be written
        file_order: a flag, if set the files are concatenated in the order they are
        specificed on the command line
        raise_exceptions: optional, defaults to True, if False it returns a list of
        stings if problems were encountered. When running from the command line,
        exceptions are the way to go, but when called from winFuzer, strings are better
        since we want to display helpful messages in the UI
    """
    try:
        track_list = sort_tracks(source_files, file_order)
    except TrackError as te:
        if raise_exceptions:
            raise
        else:
            print(f"--->te.message = {te.message}")
            print(f"--->type(te.message) = {type(te.message)}")
            return te.message

    if title:
        out_name = title
    else:
        out_name = get_output_file_name(track_list[0])

    if dest_dir:
        if dest_dir[-1] != os.path.sep:
            dest_dir += os.path.sep
        out_name = dest_dir + out_name

    if os.path.isfile(out_name):
        # Don't overwrite an existing file
        if raise_exceptions:
            raise AlreadyExistsError(out_name)
        else:
            return f"{out_name} already exists. Delete or move it"

    with open(out_name, "wb") as out_file:
        write_file(track_list, out_file)

    add_tags(track_list[0], out_name)

    if cover:
        add_cover_art(out_name, cover)
    
    return f"All done: {out_name}"


@click.command()
@click.option(
    "--cover", "-c", type=click.File("rb"), default=None, help="JPEG cover art file"
)
@click.option(
    "--title", "-t", type=click.STRING, default=None, help="The name of the output file"
)
@click.option(
    "--dest_dir",
    "-dd",
    type=click.Path(exists=True),
    help="The directory where the file should be written",
)
@click.option("--file-order", "-fo", is_flag=True)
@click.argument("source_files", type=click.Path(exists=True), nargs=-1)
def fuzer(cover, title, dest_dir, file_order, source_files):
    """
    This script takes a list of mp3 files on the command line, strips the ID3 tags
    concatenates the sound portions, adds the ID3 tags from the first input file to the
    output file and save it to the file name specified on the command line.

    The input files are combined in the order specified by disk and track info
    in ID3 tags unless the User has said to do combine them in the order they are on
    the command line

    Arguments:
        cover: optional, jpeg file containing a cover image for the combined files
        title: optional, if set it is the name of the output file, otherwise the file
        name is generated from the title tag of the first file
        dest_dir: optional, if set the directory where the new file should be written
        file_order: a flag, if set the files are concatenated in the order they are
        specificed on the command line
        concatenated.
        source_files: the individual mp3 files that are going to be combined.
    """
    run_fuzer(source_files, cover, title, dest_dir, file_order)
    print("All done.")


## Main ##
if __name__ == "__main__":
    fuzer()
