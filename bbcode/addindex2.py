#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 28 10:03:37 2018

@author: bobbuckley
"""
import os
import re
import sys
import argparse
import datetime as dt

import bs4

import ABClib2

doc, body0, nblk = None, None, None
x2page, x2pl = {}, {}

# def fixtitle(t):
#     sep = re.compile(r',\s*')
#     return " ".join(reversed(sep.split(t, 1)))

def addindex(iname, items, sort=True, idxltr=False):
    """
    insert an index into the document
    iname might be "Dance Index"
    items = ((category, 'title1', 'xid1'), (category, 'title2', 'xid2'), ...
    xid's are strings that can be interpreted as integers
    this routine sorts the index items.
    We should probably send the link ID rather than using the global x2page
    """
    global doc, body0, nblk, x2page, x2pl
    bs = bs4.BeautifulSoup("""
            <div id="%s" class="section index">
              <h1>%s</h1>
              <div class="colidx">
              </div>
            </div>
            """, 'lxml')
    didiv = bs.div
    idxname = iname.replace(' ', '').lower()
    didiv["id"] = idxname
    didiv.h1.string = iname
    body0.insert_before(didiv)
    idxs = items
    if sort:
        idxs = sorted(items, key=lambda x:(x[0], x[1].lower() if type(x[1]) is str else x[1], int(x[2])))
    print(" ... adding "+iname+".", len(idxs), 'items.')
    pcat = None
    for cat, dn, xid in idxs:
        didiv.div.append('\t')
        idxitm = doc.new_tag('button', attrs={'class':'title'})
        if cat!=pcat and cat:
            # new category - add <h2> and div to keep with the next button
            dx = doc.new_tag('div', attrs={'class':'ncb'}) # class=ncb means no-column-break
            h2 = doc.new_tag('h2')
            h2.string = cat
            dx.append(h2)
            dx.append(idxitm)
            didiv.div.append(dx)
        else:
            didiv.div.append(idxitm)
            didiv.div.append(doc.new_tag('br'))
        didiv.div.append('\n')
        pcat = cat
        a = doc.new_tag("a", href='#'+x2page[xid])
        if type(dn) is str:
            xtag = doc.new_tag('div', attrs={'class': 'xid'})
            xtag.string = xid+'.'
            a.append(xtag)
            stag = doc.new_tag('span')
            stag.string = ABClib2.fixtitle(dn)
            a.append(stag)
        else:
            dnstr = '<b>'+dn[0]+"</b><br/>\n"+", ".join(ABClib2.fixtitle(t) for t in dn[1:])
            x = bs4.BeautifulSoup("<span>"+dnstr+"</span>", 'lxml')
            a.append(x.body.span)
        idxitm.append(a)
    if nblk:
        print(" ... adding", iname, "link to Nav Block.")
        bx = doc.new_tag("span")
        bx.append(doc.new_tag("a", href="#"+idxname))
        bx.a.string = iname
        #nblk.insert(1, bx) # insert after initial newline
        nblk.append(bx)
        bx.insert_after("\n")
        bx.insert_before("  ")

    return

def main():
    """
    input files x.abc and x.xhtml
    Add indices
    Output x.idx.xhtml
    """
    global doc, body0, nblk
    global x2page, x2pl
    def fnpage(s):
        fs = s.rsplit(' ', 2)
        return fs[0], ''.join(fs[1:])
    p = argparse.ArgumentParser(description="ABC XHTML indexer")
    p.add_argument("-c", '--contents', action='store_false', help="minus (minus) contents")
    p.add_argument("-C", '--simpcontents', action='store_true', help="simple contents (no group)")
    p.add_argument("-g", '--setindex', action='store_false', help="no grouping, omit 'set index'")
    p.add_argument("-a", '--alphasetindex', action='store_true', help="set index sorted by name of first tune")
    p.add_argument('--all', action='store_true', help="index all titles")
    # p.add_argument('--pavindex', action='store_true', help="index of singers (%p:v in ABC)")
    p.add_argument("-d", '--danceindex', action='store_false', help="no dance types, omit 'dance index'")
    p.add_argument("-s", '--style', type=argparse.FileType('r'), help="CSS file to be included")
    p.add_argument("-f", "--frontmatter", type=argparse.FileType('r'), help="HTML front matter for inclusion")
    p.add_argument('file', type=argparse.FileType('r'), help="name of an abcm2ps -X output file")
    args = p.parse_args(sys.argv[1:])
    
    # read an XHTML file created by abcm2ps -X 
    doc = bs4.BeautifulSoup(args.file.read(), 'lxml')
    
    if args.style:
#        # add Paverty's CSS
#        pavcss = doc.new_tag("link", rel="stylesheet", href=args.style.name)
#        doc.head.title.insert_before(pavcss)
#        pavcss.insert_after('\n') # on a new line
        
        # embed the CSS in the header
        sx = doc.head("style")[-1]  # the last <style> in the header
        sx.append(args.style.read())
           
    # changes to body
    body = doc.body
    fnsrc = doc.head.title.text
    if fnsrc.endswith(".abc"):
        doc.head.title.string = fnsrc[:-4] 
    body0 = body.contents[0]
    pages = body("svg") # each "page" is a single SVG element
    fnsrc, page1 = fnpage(pages[0].title.text)
    print("ABC file:", fnsrc)
    abcstat = os.stat(fnsrc)
    mydate =  dt.datetime.fromtimestamp(abcstat.st_mtime).strftime("%d-%b-%Y").upper()
    if mydate.startswith('0'):
        mydate = mydate[1:] # get rid of ugly leading zero
    print("Date:", mydate)
    
    # scrstr = """
    # <script>
    #     var prevpage = '';
    #     function showpage(ids) {
    #       // hide previously displayed pages
    #       var v = prevpage.split(' ')
    #       for (id in prevpage) {
    #         svg = document.getElementById(v[id]);
    #         if (svg) {
    #             svg.style.display = "none";
    #         }
    #       }
    #       v = ids.split(' ')
    #       for (id in v) {
    #         svg = document.getElementById(v[id]);
    #         if (svg) {
    #             svg.style.display = "block";
    #         }
    #         else {
    #             console.log("Element id=", v[id], "not found.");
    #         }
    #       }
    #       prevpage = ids;
    #     }
    # </script>
    # """
    # script = bs4.BeautifulSoup(scrstr, 'lxml')
    # doc.head.title.insert_after(script.script)
    # del script, scrstr

    ss = ABClib2.Songsets(fnsrc)
    # print(len(ss.sets), "sets found.")
    abcs = tuple(abc for x in ss.sets for abc in x)
    print(len(abcs), "songs/tunes in", len(ss.sets), "sets.")
    print()
    
    if args.frontmatter:
        # format the <div> a bit better
        fm = bs4.BeautifulSoup(args.frontmatter.read(), 'lxml')
        body0.insert_before('\n')
        for x in fm.body:
            body0.insert_before(x)
            body0.insert_before("\n\n")
        x = body.find("div", id="top")
        if not x:
            print("<div id='top'> not found!")
        x = x.find("p", id="abcdate")
        if x:
            x.string = mydate
        else:
            print("****** date not set ***********")
    nblk = body.find("div", id="nblist")
    if nblk:
        nblk.insert(1, "  ")
                
    setpage = {}
    
    print("Found", len(pages), "pages.")
    # step through pages adding id=svgid to svg tags
    for page in pages:
        svgid = ''.join(page.title.text.split()[-2:])
        page["id"] = svgid # give each svg tag it's own ID attribute
        gs = page("g")
        htxtidx = 0 #1 if len(gs)>1 else 0
        try:
            # get tune number
            tn = gs[htxtidx]("text")[0].text.strip().split('.  ',1)[0]
            # if svgid in ["page71", "page72", "page73"]:
            #     print("page", svgid)
            #     for x in page("g")[0]:
            #         print("\t", x)
            #     #print("  g[0][0] =", [0])
            #     print("  g[%d] ="%htxtidx, page("g")[htxtidx]("text")[0])
            #     print("  tn   =", tn)
            setpage[tn] = svgid
        except:
            print()
            print("************************* Fail ****************************")
            if gs:
                print(page("g")[0]("text"))
                print(page)
            else:
                print("g-less page:")
                print(page)
            # raise IndexError
                # note: c matches T: line, tt is a processed line ()
                # tn is the X: line
    # find all the pages for the set that each tunes is in
    # temporary fix for one multipage song
    # setpage['142'] += " page73"
    pz = None
    print("ss.sets[0][0].xid =", ss.sets[0][0].xid)
    print("setpage =", setpage)
    assert ss.sets[0][0].xid in setpage
    for sx in ss.sets:
        px = ' '.join(setpage[x.xid] for x in sx if x.xid in setpage)
        for x in sx:
            if x.xid in setpage:
                pz = setpage[x.xid]
            x2page[x.xid] = pz
            x2pl[x.xid] = px
    assert len(x2pl)==len(x2page)
    # print(len(x2pl), "values in x2pl.")
    # print("x2pl =", x2pl)
    # print(len(x2page), 'values in x2page.')
    # print("x2page =", x2page)
    nopage = [x[0].xid for x in ss.sets if x[0].xid not in x2page]
    if nopage:
        print('known pages:', sorted(x2page.keys()))
        print("The following ABCs don't have a page No.", nopage)
        
    def tunecategory(t):
        tt = {None:'???', 'c':'C - 2/4 or 4/4', "c|":'C - 2/4 or 4/4', '2/4':'C - 2/4 or 4/4', 
              '4/4':'C - 2/4 or 4/4', '2/2':'C - 2/4 or 4/4',
              'hornpipe':'C - 2/4 or 4/4', 'reel':'C - 2/4 or 4/4', 'polka':'C - 2/4 or 4/4', 'barndance':'C - 2/4 or 4/4', 
              'schottische':'C - 2/4 or 4/4', 'march':'C - 2/4 or 4/4', 
              '6/8':'6/8', 'jig':'6/8', 'single jig':'6/8', 'double jig':'6/8',
              '3/2':'3/2', '6/4':'3/2', 'triple hornpipe':'3/2', 'maggot':'3/2',
              'minuet':'3/2',
              '9/8':'9/8', 'slip jig':'9/8',
              'waltz':'3/4', '3/4':'3/4', 'varsoviana':'3/4'}
        r = list(t.taglines('R'))
        if not r:
            r = list(t.taglines('M'))+['']
        rx = r[0].lower()
        return tt.get(rx, rx)
                   
    # add tune index
    # omit titles with '-' at start
    if args.simpcontents:
        cx = [('', xt, x.xid) for x in abcs for xt in (x.title(),) if not xt.startswith('-')]
        if cx:
            addindex("Contents", cx, sort=False)
    elif not args.contents:
        cx = [(tunecategory(x), xt, x.xid) for x in abcs for xt in (x.title(),) if not xt.startswith('-')]
        if cx:
            addindex("Contents", cx, sort=False)
    tuneindex = [(t[0], t, x.xid) for x in abcs for t in (x.alltitles() if args.all else x.titles()) if t and not t.startswith('-')]
    if tuneindex:
        addindex("Titles", tuneindex)  
        
    if args.alphasetindex:
        # create a sorted list of sets
        sx = (s for s in sorted(ss.sets, key=lambda s:s[0].title().upper()) if len(s)>1)
        def setfmt(ts):
            return ts[0].title()[0].upper(), '; '.join("{0} ({1})".format(ABClib2.fixtitle(t.title()), t.key()) for t in ts), ts[0].xid
        addindex("Sets", [setfmt(x) for x in sx], sort=False)
                           
    
    # add set dance index
    #sditems = ((next(x.taglines('X')), tl.split(':',1)[-1]) for x in abcs for tl in x.taglines('N') if tl.strip().lower().startswith('set dance'))
    if args.danceindex:
        sditems = [('', z.strip(), x.xid) for x in abcs for tl in x.taglines('N') if tl.lower().strip().startswith('set dance:') for z in tl.split(':', 1)[-1].split(';')]
        if sditems:
            addindex("Dances", sditems)
    dts = ('polka', 'jig', 'slip jig', 'double jig', 'single jig', 'reel', 'waltz', 'hornpipe',
           'march', 'slide', 'schottische', 'maggot', 'song', 'other')
    
    # Paverty singer notation - for indexing
    # if args.pavindex:
    #     singer = {'bb':'Bob Buckley', 'gc':'Graham Chalker', 'sd':'Simone Dawson', 
    #               'br': 'Bryan Rae', 'rk':'Rick Kenyon', 'bp':'Bill Pitt', 
    #               'sd2':'Sarah Davies'}
    #     sditems = [(x.vocalist(), xt, x.xid) for x in abcs for xt in (x.title(),) if not xt.startswith('-')]
    #     sditems = [(singer[s] if s in singer else s, t, x) for s,t,x in sditems if s!='-']
    #     addindex("Singers", sditems, sort=True)
        
    tunecnts = dict((x, 0) for x in dts)
    def gettype(sx):
        # skip set dance sets
        for t in (x for abc in sx for x in abc.taglines('N')):
            if t.strip().lower().startswith('set dance:'):
                return None
        for t in (x.strip().lower() for abc in sx for x in abc.taglines('R')):
            tx = re.sub(r'\s*\d+[ -]bars*\s*', '', t)
            if tx in tunecnts:
                return tx
            else:
                print('type', t, 'becomes "other"')
        return 'other'
    
    def setname(sx):
        if len(sx)==1:
            return (sx[0].title(),)
        ts = tuple(abc.title() for abc in sx)
        t = gettype(sx)
        tunecnts[t] += 1
        return (" ".join((t, "set", "No.", str(tunecnts[t]))),)+ts
        
    # add set index   
    if args.setindex:    
        itemtypes = [(t, setname(s), s[0].xid) for s in ss.sets for t in (gettype(s),) if t]
        if itemtypes:
            addindex("Sets", itemtypes)

    d, fn = os.path.split(args.file.name)
    bn, ext = os.path.splitext(fn)
    target = os.path.join(d, bn+".idx"+ext)
    print("Output sent to", target)
    with open(target, "w") as dst:
        print(doc, file=dst)
    print("Done.")
    return

if __name__=="__main__":
    main()
