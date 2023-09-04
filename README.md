# Fuzer
Python code that merges multiple mp3 files into one

## Background
Let's say you have a (legally acquired) book on CD that you want to listen to on your phone. You've ripped into iTunes/Music/whatever.
You could put all the little 3 minute files on your phone and listen to them in order, but it would be so much nicer if the audiobook 
was one file. That's where Fuzer comes in; it combines all the little mp3 files from the CDs into one mp3 file for your listening
convenience. It also tries to be intelligent about handling ID3 tags.

## Usage
The basic usage for Fuzer is `Fuzery.py destination_name.mp3 <all the input mp3 files>`

There are a few command line options as well:
- `--help`: prints a helpful message
- `--cover` (or `-c`): takes a path to a jpeg file that you'd like to have added as the cover image for the output file.
- `--file-order` (or `-fo`): a flag, that if set combines the input files in the order they were entered on the command line, rather than reading ID3 tags for the order
