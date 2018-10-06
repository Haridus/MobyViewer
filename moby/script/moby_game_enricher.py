import sys
import os
import json
import glob
import re
import sqlite3
from urllib.request import Request, urlopen
from html.parser import HTMLParser

g_verbose = False

def try_print(*data):
    result = True
    try:
        print(data)
    except:
        result = False
        print("--fail to print data")
    return result
    
def append_to_file(data, file_path):
    f = open(file_path,"a+")
    f.write(data+"\n")
    f.close()
    
class Enricher:
    def __init__(self, output_path):
        print('opening {0}'.format(output_path))    
        self.conn = sqlite3.connect(output_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        print('--opened--')
        
    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print('--closed--')
        
    def get_bounds(self):
        conn   = self.conn
        cursor = self.cursor 
        result = None
        
        if cursor.execute('SELECT min(id) as minId, max(id) as maxId,COUNT(*) as count FROM moby_games WHERE ( images = "") and ( approved > 0 )'):
            result = cursor.fetchone()
        return result
        
    def get_entry_data(self, eid):
        conn   = self.conn
        cursor = self.cursor 
        result = None
        if cursor.execute('SELECT id,approved,title,url,publisher,year,platforms,genre, images FROM moby_games WHERE (id = ?)',(eid,)):
            result = cursor.fetchone()
        return result
                
    def update_entry(self,eid,data):
        result = False
        if len(data) > 0:
            perspective = ""
            visual = ""
            pacing = ""
            interface = ""
            setting = ""
            images = ""
            
            if 'Perspective' in data:
                perspective = ",".join( data['Perspective'] )
            if 'Visual' in data:
                visual = ",".join( data['Visual'] )
            if 'Pacing' in data:
                pacing = ",".join( data['Pacing'] )
            if 'Interface' in data:
                interface = ",".join( data['Interface'] )
            if 'Setting' in data:
                setting = ",".join( data['Setting'] )
            if 'Images' in data:
                if( len( data['Images'] ) > 0 ):
                    images = ",".join( data['Images'] )
                    images = images.strip()
                    if len(images) == 0:
                        images = "NO_IMAGE"
                else:
                    images = "NO_IMAGE"
            
            params = (perspective,visual,pacing,interface,setting,images,)
            if g_verbose:
                print(len( params ) )
                try_print(params)
            
            conn = self.conn
            cursor = self.cursor     
            try_print('--params--',params)   
            if cursor.execute('UPDATE moby_games SET perspective = ?,visual = ?,pacing = ?,interface=?,setting=?,images=? '+ \
                                                 'WHERE id = {_eid_}'.format(_eid_ = eid), params ):
                conn.commit()
                result = True
                print("--entry updated--")
            else:
                append_to_file("|".join(params)+"\n","doubt.txt")
                print("--fail to update entry--")
        else:
            print("--bad data empty--")
        return result

base_url = 'https://www.mobygames.com'
g_controled_data = ['Published by','Released','Platforms','Platform','Genre','Perspective','Visual','Pacing','Interface','Setting']
re_cover = re.compile('front-cover.*\.(jpg|jpeg|png|bmp)')
re_screenshot = re.compile('screenshot.*\.(jpg|jpeg|png|bmp)')

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.clear()
                
    def clear(self):
        self.tagId = ""
        self.output_data = {}
        self.key = ""
        self.value = ""
        self.futher_pattern = ""
        self.errors = []    
        HTMLParser.close(self)
        HTMLParser.reset(self)
        
    def handle_starttag(self, tag, attrs):
        self.tagId = tag
        if g_verbose:
            try_print("Start tag:", tag)
        for attr in attrs:
            if g_verbose:
                try_print("     attr:", attr)
            if tag == "img":
                if attr[0]=="src":
                    if re_cover.search( attr[1] ):
                        if "Images" not in self.output_data:
                            self.output_data["Images"] = []
                        self.output_data["Cover"] = base_url+attr[1]
                        self.output_data["Images"].append(self.output_data["Cover"])
                    elif re_screenshot.search( attr[1] ):
                        if "Images" not in self.output_data:
                            self.output_data["Images"] = []
                        self.output_data["Images"].append(base_url+attr[1])
                    else:
                        if g_verbose:
                            print("--image-infit--")
            if tag == "h1":
                if attr[0] == "class":
                    if attr[1] == "niceHeaderTitle":
                        self.futher_pattern = "niceHeaderTitle"
            if (tag == "a") and (self.futher_pattern == "niceHeaderTitle"):
                if attr[0] == "href":
                    self.output_data["Url"] = attr[1]
                    self.futher_pattern = ""
                        
        if len(self.key) > 0:
            self.futher_pattern = self.futher_pattern+tag
            if g_verbose:
                print("self.futher_pattern",self.futher_pattern)    
               
    def handle_endtag(self, tag):
        if g_verbose:
            try_print("End tag  :", tag)
        self.tagId = ""
        if len(self.key) != 0 and len(self.futher_pattern) > len(tag):
            self.futher_pattern = self.futher_pattern[:-(len(tag))]
            if g_verbose:
                try_print("self.futher_pattern",self.futher_pattern)
        if tag == "div" and len(self.key) > 0 and len(self.value) > 0:
            self.key=""
            self.value=""
            self.futher_pattern=""
            
    def handle_data(self, data):
        if self.tagId == "title":
            self.output_data["Title"] = data
        elif self.tagId == "div":            
            if data in g_controled_data:
                self.key = data
                if g_verbose:
                    try_print("--key "+data+"found--")
        elif self.tagId == "a":
            if self.futher_pattern == "diva":
                self.value = data
                if self.key not in self.output_data:
                    self.output_data[self.key]=[]
                self.output_data[self.key].append(data)
        if g_verbose:
            if try_print("Data     :", data) == False:       
                self.errors.append( (1,1,'unknown print data --skip--data--') )
                print("Data     :","--skip--data--") 
                  
    def handle_comment(self, data):
        if g_verbose:
            try_print("Comment  :", data)

    def handle_entityref(self, name):
        if g_verbose:
            c = chr(name2codepoint[name])
            try_print("Named ent:", c)

    def handle_charref(self, name):
        if g_verbose:
            if name.startswith('x'):
                c = chr(int(name[1:], 16))
            else:
                c = chr(int(name))
            try_print("Num ent  :", c)

    def handle_decl(self, data):
        if g_verbose:
            try_print("Decl     :", data)
    
if __name__ == "__main__":
    parser = MyHTMLParser()
    enricher = Enricher('./thumb_full.db')
    bounds = enricher.get_bounds()
#    bounds = (1,20,1)
    print("({minId},{maxId},{count})".format(minId = bounds[0], maxId = bounds[1], count = bounds[2]) )
    for eid in range(bounds[0], bounds[1]+1):
        edata = enricher.get_entry_data(eid)
        approved = edata['approved']
        page_url = edata['url']
        if (approved > 0 ) and ( len(page_url) > 0 ) and ( len( edata['images'] ) == 0 ):
            print("--start page ["+page_url+"] download--")
            req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
            output_data = None
            try:
                resp = urlopen(req)    
                html = resp.read().decode('utf-8')
                parser.clear()       
                parser.feed(html)
                output_data = parser.output_data
            except: 
                output_data = {"Images":["NO_PAGE"]}
            enricher.update_entry(eid,output_data)
        else:
            print("--page [{_page_url_}({_approved_}{_img_data_len_})] unfit--".format(_page_url_ = page_url, _approved_ = approved, _img_data_len_ = len( edata['images'] ) == 0 ) )
    
'''    for offset in range(0,90000,25):
        page_url = "https://www.mobygames.com/browse/games/offset,{_offset_}/so,0a/list-games/".format(_offset_=offset)
        print("--start page ["+page_url+"] download--")
        req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read().decode('utf-8')
        parser.output_data = []        
        parser.feed(html)
        output_data = parser.output_data
        for data in output_data:
            output.add_entry(data)
'''

