#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat May 23 11:18:13 2020

@author: Bob Buckley

Create usable HTML from ABC file
Based on a template file Simple.htm or Simple2.htm
These templates use the svgweb1-1.js and svgweb2-1.js modules to display scores.
"""

import os
import re
import sys
import argparse

import bs4

def main():
    """
    Commandline argument is an ABC file to be "converted"
    
    Output for X.abc is X.htm

    Returns
    -------
    None.

    """
    
    prog = sys.argv[0]
    progdir = os.path.dirname(prog)
    
    deftmpl = "Simple.htm"
    px = argparse.ArgumentParser(description='Embed ABC in a template.')
    px.add_argument("abc", nargs=1, help="the name of the ABC file to be embedded")
    px.add_argument("-t", "--template", default=deftmpl, help="template file(default={})".format(deftmpl))
    px.add_argument("-o", "--output", default=None, help="output file (default=ABC.abc=>ABC.htm)")
    px.add_argument("-x", "--header", default=None, help="page header (default=ABC file name)")
    px.add_argument("-l", "--local", action="store_false", help="use locally - don't embed local javascript code")
    args= px.parse_args()
    
    tmplrep = { '2': 'Simple2.htm'} # allow known shortcuts
    tx = tmplrep.get(args.template, args.template)
    template = tx if os.path.isfile(tx) else os.path.join(progdir, tx)
    print("Template file =", template)
    htm = bs4.BeautifulSoup(open(template), "html.parser")
    
    
    fn = args.abc[0] #nargs makes this a list
    assert fn.endswith(".abc"), fn+" is not recognised as an ABC file."
#    with open(fn, encoding="utf-16") as src:
    with open(fn) as src:
        # fix odd newlinesq
        abc = src.read().strip().replace("\r\n", "\n").replace("\r", "\n")
    # abc2svg needs %%newpage in a tune to flag <div class=newpage> in the output
    abc = re.sub(r'\n\n+%%\s*newpage\s*(%.*)?$', '\n%%newpage\n', abc, flags=re.MULTILINE)
    
    if args.local:
        # replace local files (as they are not available generally)
        dsts = htm.findAll("script", src=True)
        for sx in dsts:
            sxsrc = sx.attrs['src']
            # if not sxsrc.startswith("file://" ):
            if any(sxsrc.startswith(x) for x in ["http://", "https://"]):
                continue
            if sxsrc.startswith("file://"):
                sxsrc = sxsrc[7:] # drop "file://" from src
            # replace with file content and delete src attribute, minimise the code
            # it would be better to use minimised code
            with open(sxsrc) as src:
                insert = [x for x in src]
            # the following is for javascript - should check
            if sx.attrs['type']=="text/javascript":
                insert = [re.sub("\s*//.*\n", '', x).strip() for x in insert]
            sx.string = "\n"+"".join(x+'\n' for x in insert if x)
            del sx.attrs["src"]
        
    code = htm.head.find(name="script", id="code")
    if code:
        code.clear()
        code.append("\n  ")
        hdrstr = (args.header if args.header else (fn+' tunes.')).replace("'", "''")
        code.append("  var list_head='{}';\n".format(hdrstr))
        code.append("  var list_tail='Show all.';\n  ")
        htm.head.append("  ")
    
    if args.header:
        h1 = htm.body.find(name="h1", class_="replace")
        if h1:
            h1[0].string = args.header
        else:
            print("-x/--header but no <h1 class='replace'> in Template")
    
    if abc.startswith('\xef\xbb\xbf'): # UTF-8 header?
        abc = abc[3:]
    if not abc.startswith('%abc'):
        print("ABC? file starts with", repr(abc[:10]), ''.join('\\x%02x'%ord(c) for c in abc[:6]))
    assert abc.startswith('%abc'), 'argument {} is not an ABC file.'.format(fn)

    dst = htm.body.findAll(name="script", class_="abc", attrs={'type': "text/vnd.abc"})
    if len(dst)==1:
        dst=dst[0]
        dst.clear()
        dst.append("\n  ")
        abcelem = bs4.CData(''.join(['\n\n',abc, '\n\n']))
        dst.append(abcelem)
        dst.append("\n")
    elif code:
       dst=htm.body
       x = abc.find('\n')
       dst.clear()
       dst.string = '\n\n'+abc[:x]+'%'
       dst.append(bs4.Comment(abc[x:]+'\n% '))
       dst.append('\n\n')
    else:
       print("Mystery template!")
       sys.exit(0)
   
    htm.head.title.string = fn+' file.' # set the title
    
    #fix some BS4 oddities
    htmstr = htm.encode(formatter="html5")
    for x in [b'async', b'defer']:
        fixstr = b'<script '+x
        htmstr = htmstr.replace(fixstr+b'="" ', fixstr+b' ')
    
    with open(args.output if args.output else fn[:-4]+".htm", "wb") as dst:
        dst.write(htmstr)
        
    return

if __name__=="__main__":
    main()  


