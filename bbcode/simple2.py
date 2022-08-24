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

#import bs4

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
    
    deftmpl = "Simple1.htm"
    px = argparse.ArgumentParser(description='Embed ABC in a template.')
    px.add_argument("abc", nargs=1, help="the name of the ABC file to be embedded")
    px.add_argument("-t", "--template", default=deftmpl, help="template file(default={})".format(deftmpl))
    px.add_argument("-o", "--output", default=None, help="output file (default=ABC.abc=>ABC.htm)")
    px.add_argument("-x", "--header", default=None, help="page header (default=ABC file name)")
    #px.add_argument("-l", "--local", action="store_false", help="use locally - don't embed local javascript code")
    args= px.parse_args()
    
    tmplrep = { '1': 'Simple1.htm', '2': 'Simple2.htm'} # allow known shortcuts
    tx = tmplrep.get(args.template, args.template)
    template = tx if os.path.isfile(tx) else os.path.join(progdir, tx)
    print("Template file =", template)
    #htm = bs4.BeautifulSoup(open(template), "html.parser")
    with open(template) as src:
        htmls = re.split(r"<script\s+class=['\"]abc['\"]\s+type=['\"]text/vnd.abc['\"]>\s*</script>\s*", src.read())
    assert len(htmls)==2
    
    fn = args.abc[0] #nargs makes this a list
    assert fn.endswith(".abc"), fn+" is not recognised as an ABC file."
    htmls[0] = re.sub('<title>.*</title>', '<title>'+fn[:-4]+'</title>', htmls[0])
    
    # replace header if requested
    if args.header:
        htmls[0] = re.sub('<h1(.*)>.*</h1>', '<h1\g<1>>'+args.header+'</h1>', htmls[0])
            
#    with open(fn, encoding="utf-16") as src:
    with open(fn) as src:
        # fix odd newlinesq
        abc = src.read().strip().replace("\r\n", "\n").replace("\r", "\n")
    if abc.startswith('\xef\xbb\xbf'): # UTF-8 header?
        abc = abc[3:]
    if not abc.startswith('%abc'):
        print("ABC? file starts with", repr(abc[:10]), ''.join('\\x%02x'%ord(c) for c in abc[:6]))
    assert abc.startswith('%abc'), 'argument {} is not an ABC file.'.format(fn)
    # abc2svg needs %%newpage in a tune to flag <div class=newpage> in the output
    #abc = re.sub(r'\n\n+%%\s*newpage\s*(%.*)?$', '\n%%newpage\n', abc, flags=re.MULTILINE)
    
    # if args.local:
    #     # replace local files (as they are not available generally)
    #     dsts = htm.findAll("script", src=True)
    #     for sx in dsts:
    #         sxsrc = sx.attrs['src']
    #         # if not sxsrc.startswith("file://" ):
    #         if any(sxsrc.startswith(x) for x in ["http://", "https://"]):
    #             continue
    #         if sxsrc.startswith("file://"):
    #             sxsrc = sxsrc[7:] # drop "file://" from src
    #         # replace with file content and delete src attribute, minimise the code
    #         # it would be better to use minimised code
    #         with open(sxsrc) as src:
    #             insert = [x for x in src]
    #         # the following is for javascript - should check
    #         if sx.attrs['type']=="text/javascript":
    #             insert = [re.sub("\s*//.*\n", '', x).strip() for x in insert]
    #         sx.string = "\n"+"".join(x+'\n' for x in insert if x)
    #         del sx.attrs["src"]
            
    #split the file contents into separate tunes
    tunes = re.split(r'^(X:\s*(\d+)).*\n|^(\s*%%\s*newpage).*\n', abc, flags=re.M)
    hdr = tunes.pop(0)
    gen   = (x.strip() if x else x for x in tunes)
    tunetup = [x for x in zip(gen, gen, gen, gen)]
    # for x in tunetup:
    #     print()
    #     print(x)
    
    class Tune:
        def __init__(self, tx):
            self.abc = '\n'.join((tx[0], tx[3]))
            self.id  = tx[1]
            kpos = self.abc.find('K:')
            self.hdrlen = self.abc.find('\n', kpos)
            self.key = self.abc[kpos+2:self.hdrlen].strip()
            return
            
        def divstr(self):
            return # should format for output
        
        def titles(self):
            # return the list of titles for a tune
            ts = [x[2:].strip() for x in self.abc[:self.hdrlen].split('\n') if x.startswith('T:')]
            return ts
        
        def tidx(self):
            "return a title index tuple generator"
            return ((self.id, t, self.key) for t in self.titles())
        
        def cidx(self):
            return self.id, self.titles()[0], self.key
            
    def mktidx(ss):
        "make a title index tuple from a list of tunes"
        return sorted((t for x in ss for t in x.tidx()), key=lambda x:(x[1], x[0], x[2]))
    
    def mkcidx(ss):
        "make a title index tuple from a list of tunes"
        return [x.cidx() for x in ss]
    
    # build indexing data
    ts = [Tune(x) for x in tunetup if not x[2]]
    
    cidxfmt = "    {0}. <a href='#xx{0}'>{1}</a> ({2})<br/>\n"        

    # process HTML from template
    # abcout = '\n'.join(mkseg(x) for x in tuneup)
    abcfmt = "<div id='xx{1}'><script class='abc' type='text/vnd.abc'>\n{0}\n{2}\n</script></div>\n"
    abchdr = "<script class='abc' type='text/vnd.abc'>\n{0}\n</script>\n"

    mx = mkcidx(ts)
    tx = mktidx(ts)
    tltrset = set(x[1][0] for x in tx)
    tltrs = ' '.join("<a href='#tx{0}'>{0}</a>".format(a) for a in sorted(x for x in tltrset))
    with open(args.output if args.output else fn[:-4]+".htm", "wt") as dst:
            dst.write(htmls[0])
            # output Contents
            dst.write("  <h1>Contents</h1>\n  <div id='cidx'>\n")
            dst.write("<p>\n")
            for x in mx:
                dst.write(cidxfmt.format(x[0], x[1], x[2]))
            dst.write("</p>\n</div><div class='pb'></div>\n")
            
            # output Title index
            # letter index list to start with. 
            dst.write("  <h1>Title Index</h1>\n  <p>{0}</p>\n  <div id='tidx'>\n".format(tltrs))
            lx = ''
            for x in tx: # we should use a python groupby here
                # letter headings
                if lx!=x[1][0]:
                    if lx:
                        dst.write('    </p>\n')
                    lx = x[1][0]
                    dst.write("    <h2 id='tx{0}'>".format(lx)+lx+"</h2><p>\n")
                dst.write(cidxfmt.format(x[0], x[1], x[2]))
            dst.write("    </p>\n</div><div class='pb'></div>\n")
            
            # now output all the ABC notation
            dst.write(abchdr.format(hdr))
            for x in tunetup:
                if x[2] and x[2].startswith('%%newpage'):
                    dst.write("<div class='pb'></div>\n")
                else:
                    dst.write(abcfmt.format(x[0], x[1], x[3]))
            dst.write(htmls[1])
    return

if __name__=="__main__":
    main()  


