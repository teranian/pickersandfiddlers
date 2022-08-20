# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 11:26:27 2017

@author: bobbuckley

A library of code for ABC files.
The ABC files can be augmented for Paverty
A line that is "%p: v BB" means BB is the vocalist
"""
#import itertools
import re
import sys
            
def abcdict(ssx):
    "convert a list of songs to a header and a dictionary of songs lines"
    assert ssx, "expects at least one song"       
    hdr, ss = (["%abc"], ssx) if ssx[0][0].startswith('X:') else (ssx[0], ssx[1:])
        
    assert all(s[0].startswith('X:') for s in ss), "malformed song - first line is not X:"

    sdict = dict((s[0][2:].strip(), s[1:]) for s in ss)
    return hdr, sdict
    
def songdict(ssx):
    "convert a list of songs to a header and a dictionary of Songs"
    assert ssx, "expects at least one song"       
    hdr, ss = ([], ssx) if ssx[0][0].startswith('X:') else (ssx[0], ssx[1:])
    
    badsongs = [n for n, s in enumerate(ss) if not s[0].startswith('X:')]
    
    if badsongs:
        print("badsongs=", badsongs)
        for n in badsongs[:4]:
            print(ss[n-1][:3])
            print(ss[n][:3])
        
    assert all(s[0].startswith('X:') for s in ss), "malformed song - first line is not X:"
    
    sdict = dict((s[0][2:].strip(), ABCsong(s[1:])) for s in ss)
    return hdr, sdict
    
def sorttitle(title):
    "tranform a title for sorting"
    tx = re.sub('^(a|an|the|l[ae]|en) ', '', title.lower())
    return re.sub(', (a|an|the|l[ae]|en)$', '', tx)
    
def fixtitle(title):
    return re.sub(r'^(.*), (an?|the|l[ae]|en)$', r'\2 \1', title, flags=re.IGNORECASE)

class Song:
    pass

oldplines =[]
class ABCsong(Song):
    """
    class for storing and accessing ABC song/tune notation
    Note: the X: lines was trimmed from the front.
    No blank line at the end. 
    """
    def __init__(self, plines, attrs=None):
        global oldplines
        # song/tunes must start with an X: line
        if not plines[0].startswith('X:'):
            print('bad ABC song/tune ...')
            print('plines =', ''.join(x+'\n' for x in plines))
            print()
            assert False
            if oldplines:
                print("previous ...")
                print(''.join(x+'\n' for x in oldplines))
            sys.exit(1)
        # dispose of any initial blank words lines ... they break things
        oldplines = plines
        wpos = 0
        for i, l in enumerate(plines):
            if l.startswith('W:'):
                wpos = i
                wend = wpos
                while wend<len(plines) and plines[wend]=='W:':
                    wend+=1
                break
        lines = [x for x in (plines[:wpos]+plines[wend:] if wpos else plines)]
        self.xid = lines[0][2:].strip()
        self.lines = lines[1:] if lines[0].startswith('X:') else lines 
        self.attr = attrs
        return
        
    def clean(self):
        self.lines = [l for l in self.lines if not l.startswith('%%newpage')]
        return self
        
    def taglines(self, tag):
        "all the lines that start with tag"
        return (l[len(tag)+1:].strip() for l in self.lines if l.startswith(tag+':'))
    
    def titles(self):
        "title lines - lines that start with T: up to first K: line"
        for line in self.lines:
            if line.startswith('T:'):
                yield line[2:].strip()
            if line.startswith('K:'):
                break
        return
    def alltitles(self):
        "title lines - lines that start with T: up to first K: line"
        for line in self.lines:
            if line.startswith('T:'):
                yield line[2:].strip()
        return
    
    def title(self):
        "main title of song/tune - the first title line"
        for ts in self.titles():
            return ts
        return None
        
    def sorttitles(self):
        "titles used for sorting - all lowercase and remove leading article"
        return map(sorttitle, self.titles())
        
    def words(self):
        "words or lyrics - lines starting with W:"
        # maybe should include w: as well
        return self.taglines('W')
    
    def key(self):
        "get the first key - first K: tag"
        trim = (('maj', ''), ('major', ''), ('minor', 'm'), ('min', 'm'), ('dorian', 'dor'))
        for ll in self.taglines('K'):
            if not ll:
                return ll
            l = ll.split()[0] # strip off any extra stuff like clef= ...
            for x, z in trim:
                if l.endswith(x):
                    l = l[:-len(x)]+z
            return l
        return None
    
    def mbody(self):
        "True if anything follows K: ... this is more than a place holder"
        kno = next(i for i, lx in enumerate(self.lines) if lx.startswith('K:'))
        return kno+1<len(self.lines)
    
    def linesstr(self):
        "the lines of the song - as a string"
        return ''.join(map(lambda x:x+"\n", self.lines))
        
    def vocalist(self):
        "%p: v BB style lines in Paverty ABC files"
        for l in self.taglines('%p'):
            if l.startswith('v '):
                return l[2:].lstrip().lower()
        return '-'

class Songsets:

    def __init__(self, fn):
        """
        Read an ABC file whose name is fn
        
        Split file into songs/tunesets. These are separated by "\n%%newpage\n"
        Return the file header (if any) and lists of abclines
        """
        print()
        print('reading file', fn)
        
        with open(fn, 'rt') as src:
            # use the following with open mode 'rb' above
            #mystr = src.read()
            #txt = ''.join(chr(c) for c in mystr)
            #inp = [z for z in map(lambda x: x.strip(), txt.split("\n%%newpage\n")) if z]
            # inp = [z for z in map(lambda x: x.strip(), src.read().split("\n%%newpage\n")) if z]
            # inp = [z for z in map(lambda x: x.strip(), re.split(src.read(),r'\n%%\s*(newpage|sep)\s*\n', flags=re.IGNORECASE|re.UNICODE|re.MULTILINE)) if z]
            setpat = re.compile(r'\n%%\s*(newpage|sep)\s*\n', flags=re.IGNORECASE|re.UNICODE|re.MULTILINE)
            settmp = setpat.split(src.read())[0::2]
            inp = [z for z in map(lambda x: x.strip(), settmp) if z]
        self.hdr = None
        if inp and inp[0].startswith("%abc"):
            hdr, inp[0] = inp[0].split("\n\n", 1)
            self.hdr = [x for x in hdr.split('\n')]
        sss = [[x.strip().split('\n') for x in xs.strip().split('\n\n')] for xs in inp if xs]
        # fails with multiple blank lines between songs - should use groupby()
        self.sets = tuple(tuple(ABCsong(x) for x in ss if x) for ss in sss)
        
        return
