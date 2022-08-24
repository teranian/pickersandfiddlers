# Bob Buckley's tunebook code
The code in this folder/directory creates HTML tunebooks from an ABC notation file and a few template files.

There are several versions. The easiest to use and most basic is simple1.py This is a basic Python 3 script that creates a tune book from a ABC library file (e.g created by EasyABC). The file junk.abc in this package is an example.

To try it out create a folder and copy the following files into it.
    junk.abc
    simple1.py
    Simple1.htm

Now run the command: python3 simple1.py junk.abc

The result should be a junk.htm file that you can load into any proper browser (Chrome, Firefox, ...)
I create PDF versions by using Chrome's print function. That seems to preserve internal links. 
The HTML verion plays tunes if you click on them. To remove this feature, delete the loading of snd-1.js and follow-1.js in the header of the HTML file (you could create a template that does not include these).

Things still to be done:

    1. a fixed navigation menu at the bottom (or top) of the screen to get you back to the Contents & Title Index at the top
    2. static (build time) or dynamic (live option) choice of format - dots or chord charts or both 
    3. an index of tunes by key ... and maybe keys and tunings for old-time
    4. a HTML template with better headings and Preface for Canberra Old-timey session
    5. local abc2svg JS files so you don't need internet access - maybe wget the JS files at the time of build, load local files in HTML 
    6. preferred formatting options - maybe a separate CSS file

## Second (older) version

The second version of the code is addindex2.py It needs a working version of abcm2ps to create SVG files that it embeds in the HTML. I'm probably moving away from this model as it is far more complicated. 

The command is runtunes-oldtime.sh - a UNIX/Linux (or Windows WSL) style shell script. It expects the ABC file as it's argument.


