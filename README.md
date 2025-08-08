# Fuzer
Python code that merges multiple mp3 files into one

## Background
Let's say you have a (legally acquired) book on CD that you want to listen to on your phone. You've ripped into iTunes/Music/whatever.
You could put all the little 3 minute files on your phone and listen to them in order, but it would be so much nicer if the audiobook 
was one file. That's where Fuzer comes in; it combines all the little mp3 files from the CDs into one mp3 file for your listening
convenience. It also tries to be intelligent about handling ID3 tags.

## Usage
The basic usage for Fuzer is 

`Fuzer.py <all the input mp3 files>`

By default Fuzer reads the discnumber and tracknumber ID3 tags to determine the order of the files when combining them. It copies
the ID3 tags from the first file into the ID3 tags of the destination file. Finally, it sets both the tracknumber and discnumber tags of
the destination file to 1/1 and the title tag to be the same as the album tag. If the --title option is not used it constructs a file name
from the album name where non-alphanumeric characters are replaced by _ (e.g., "The Return of the King" becomes The_Return_of_the_King.mp3. 
It can also add a cover image if the --cover option is used.

There are a few command line options as well:
- `--help`: prints a helpful message
- `--cover` (or `-c`): takes a path to a jpeg file that you'd like to have added as the cover image for the output file.
- `--title` (or `-t`): lets you specify the name of the output file. Otherwise Fuzer generates on from the album tag in the first file of the input set
- `--file-order` (or `-fo`): a flag, that if set combines the input files in the order they were entered on the command line, rather than reading ID3 tags for the order

For those of you who don't want to use the command line, there's also a GUI front end called winFuzer (based on the [winup](https://github.com/mebaadwaheed/winup) library.
To use, start up winFuzer. On the left side of the window you will see a directory tree with your current directory selected. To the right of it are two list boxes, one shows
all the .jpg and .jpeg files in the current directory. The other shows all the .mp3 files in the current directory. If you're not in the directory where your mp3 files are
located, click around in the directory tree until you're where you want to be. Then select the .mp3 files that comprise your book and click on "mp3 files --->" button to move
them into the list on the left side of the window that shows the files that will be used to construct the audiobook. If you've selected the wrong files, the "Clear mp3 files"
button will clear the list. If you're adding a cover image click on the .jpeg (or .jpg) file of the cover and click on the "cover image --->" button to select the image you're
using for the cover. The "Clear cover image" button will remove it and you can select the proper image file. Finally, click on the "Make book" button run the Fuzer code that
constructs the book from the input files. At the moment the file name for the output file is constructed from the album name of the first file. You can't specify a file name
when using winFuzer.py

## Caveats
- Fuzer only handles mp3 files
- When adding a cover image, Fuzer assumes it is a jpeg.

## Try it out
If you run 

`Fuzer.py --cover test_data/Fuzer.jpg -title test.mp3 test_data/*.mp3` 

You will generate an mp3 file called test.mp3 with a cover image and audio that says
> disc one track one disc one track two disc two track one disc two track two

Alternatively you can run

`Fuzer.py --cover test_data/Fuzer.jpg test_data/*.mp3`

And you will get an identical file, but this time called Fuzer_Test_Data.mp3.
