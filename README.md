# Fuzer
Python code that merges multiple mp3 files into one

## Background
Let's say you have a (legally acquired) book on CD that you want to listen to on your phone. You've ripped into iTunes/Music/whatever.
You could put all the little 3 minute files on your phone and listen to them in order, but it would be so much nicer if the audiobook 
was one file. That's where Fuzer comes in; it combines all the little mp3 files from the CDs into one mp3 file for your listening
convenience. It also tries to be intelligent about handling ID3 tags.

## Usage
The basic usage for Fuzer is 

`Fuzer.py destination_name.mp3 <all the input mp3 files>`

By default Fuzer reads the discnumber and tracknumber ID3 tags to determine the order of the files when combining them. It copies
the ID3 tags from the first file into the ID3 tags of the destination file. Finally, it sets both the tracknumber and discnumber tags of
the destination file to 1/1 and the title tag to be the same as the album tag. It can also add a cover image of the --cover option is used.

There are a few command line options as well:
- `--help`: prints a helpful message
- `--cover` (or `-c`): takes a path to a jpeg file that you'd like to have added as the cover image for the output file.
- `--file-order` (or `-fo`): a flag, that if set combines the input files in the order they were entered on the command line, rather than reading ID3 tags for the order

## Caveats
- Fuzer only handles mp3 files
- When adding a cover image, Fuzer assumes it is a jpeg
- When playing the otuput file with Quicktime Player on Mac OS, it only plays the first track that was added to the file. When playing it with iTunes/Music, Fission, VLC, all the combined tracks are played
