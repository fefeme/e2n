# Basic Evernote to Notebooksapp exporter

There's still a lot to do, but it fit's my needs.

Html notes can be converted to either html or txt notebooksapp notes (use -to_text command line switch)

For media notes only PDF and Images are supported.

This is in no way complete, it just worked for my initial conversion from evernote to notebooksapp.


# Installation

I recommend to create a virtualenv. 
 
 __Python 3 is required__
 
 
Then install the requirements

 ```pip install -r requirements.txt```



# Examples

Convert all notes from Misc.enex to html / pdf / images and save the result to ./test

```./export.py --out test```


Convert all notes to text (this doesn't work for en-media notes)

```./export.py --to_text --out test```


