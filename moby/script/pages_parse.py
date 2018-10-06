import sys
import os
import json
import glob
import re
#---------------------------------
#from lxml import html
#import bs4
#from pyquery import PyQuery
#---------------------------------

g_verbose = True

def try_print(*data):
    result = True
    try:
        print(data)
    except:
        result = False
        print("--fail to print data")
    return result

def is_valid_data(data):
    return (data != None) and ('Title' in data) and ('Released' in data) and ('Genre' in data) and ('Url' in data)

#---------------------------------
from html.parser import HTMLParser
import sqlite3

#---output handle---------------
#maybe implement as class

class Output:
    def __init__(self, output_path):
        print('opening {0}'.format(output_path))    
        if os. path. isfile(output_path):
            os.remove(output_path)
        self.conn = sqlite3.connect(output_path)
        self.cursor = self.conn.cursor()
        
        conn = self.conn    
        cursor = self.cursor
    
        print('--opened--')

        print('preparing tables...', cursor.execute('CREATE TABLE IF NOT EXISTS moby_games(id INTEGER PRIMARY KEY,title VARCHAR(256), url VARCHAR(1024), publisher VARCHAR(128),year INTEGER,platforms VARCHAR(256),genre VARCHAR(128),perspective VARCHAR(128),visual VARCHAR(128),pacing VARCHAR(128),interface VARCHAR(128),setting TEXT, images TEXT)') )
#        print( cursor.execute('DELETE FROM boby_games') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_title_index ON moby_games(title)') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_publisher_index ON moby_games(publisher)') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_year_index ON moby_games(year)') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_platforms_index ON moby_games(platforms)') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_genre_index ON moby_games(genre)') )
        conn.commit()
        
    def __del__(self):
        self.conn.commit()
        self.conn.close()
        print('--closed--')
        
    def add_entry(self,data):
        result = False
        if len(data) > 0:
            if is_valid_data(data):
                conn = self.conn
                cursor = self.cursor
                
                title = data['Title']
                url = data['Url']
                publisher = ""
                year = ",".join( data['Released'] )
                platform = ""
                genre = ",".join( data['Genre'] )
                prespective = ""
                visual = ""
                pacing = ""
                interface = ""
                setting = ""
                images = ""
                
                if 'Published by' in data:
                    publisher = ",".join( data['Published by'] )
                if 'Platforms' in data:
                    platform = ",".join( data['Platforms'] )
                if 'Platform' in data:
                    platform = ",".join( data['Platform'] )
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
                    images = ",".join( data['Images'] )
                params = (title,url,publisher,year,platform,genre,prespective,visual,pacing,interface,setting,images,)
                if g_verbose:
                    print(len( params ) )
                    try_print(params)
                    
                if cursor.executemany('INSERT INTO moby_games(title,url,publisher,year,platforms,genre,perspective,visual,pacing,interface,setting,images)'+ \
                                                 'VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', (params,) ):
                    conn.commit()
                    result = True
                    print("--added to db--")
                else:
                    print("--fail to add to db--")
            else:
                print("--bad data--",data)
        else:
            print("--bad data empty--")
        return result
        
#tag - title - game name Akalabeth: World of Doom Apple II
#tag h1 class niceHeaderTitle tag a - short game name Akalabeth: World of Doom
#tag div id = coreGameCover tag img attr src /images/covers/s/23640-akalabeth-world-of-doom-apple-ii-front-cover.jpg
#div Published by netx div -> a data California Pacific Computer Co.
#div Released netx div -> a data 1980
#div Platforms netx div -> a data AppleII a data iPhone etc
#tag div id = coreGameGenre
#div Genre netx div -> a data Role-Playing (RPG)
#div Perspective netx div -> a data 1st-person / Top-down
#div Visual netx div -> a data
#div Pacing netx div -> a data
#div Interface netx div -> a data
#div Setting netx div -> a data
#div id floatholder coreGameInfo

#TODO: check Perspective
base_url = 'https://www.mobygames.com'
g_controled_data = ['Published by','Released','Platforms','Platform','Genre','Perspective','Visual','Pacing','Interface','Setting']
re_cover = re.compile('front-cover.*\.(jpg|jpeg|png|bmp)')
re_screenshot = re.compile('screenshot.*\.(jpg|jpeg|png|bmp)')

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagId = ""
        self.output_data = {}
        self.key = ""
        self.value = ""
        self.futher_pattern = ""
        self.errors = []

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
        try_print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        try_print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        try_print("Num ent  :", c)

    def handle_decl(self, data):
        try_print("Decl     :", data)

def append_to_file(data, file_path):
    f = open(file_path,"a+")
    f.write(data+"\n")
    f.close()

#make parser class
def parse_moby_page(page_path):
    print(file_name)
    output_data = None
    
    vf = open(file_name,"r")
    parser = MyHTMLParser()
#    parser.feed(vf.read())
    try:
        parser.feed(vf.read())
    except:
        print("--skip--page--")
        
    output_data = parser.output_data
    if( is_valid_data( output_data ) ):
        print("output_data ok")
    else:
        print("bad output_data")
        
    return output_data
    

if __name__ == "__main__":
    '''print(len(sys.argv),sys.argv)'''
    parameters = {"source_dir"  :"./pages",
                  "output_path" :".",
                  "output_name" :"thumb.db",
                  "verbose" : "False"
                 } 
    '''parameters by index'''             
    pp =  {1:"source_dir",
           2:"output_path",
           3:"output_name"
          }
          
    '''parameters by string'''      
    ps =  {"-i" :"source_dir",
           "-op":"output_path",
           "-on":"output_name",
           "-v" :"False"
          }      
        
    argit = iter( range(1,len(sys.argv)) )         
    for argi in argit:
        arg = sys.argv[argi]
        if arg in ps:
            pname = ps[arg]
            parameters[pname] = sys.argv[argi+1]
            next(argit)
        else:
            pname = pp[argi]
            parameters[pname] = arg
    
    source_path = parameters["source_dir"]
    out_path = os.path.join(parameters["output_path"],parameters["output_name"])
    output = Output(out_path)
    
    search_pattern = os.path.join(source_path,"*.htm*")
    '''print(source_path, search_pattern)'''
    for file_name in glob.glob(search_pattern):
        data = parse_moby_page(file_name)
        if is_valid_data( data ):
            if output.add_entry(data) == False:
                append_to_file(file_name,"bad_pages.txt")
        else:
            append_to_file(file_name,"bad_pages.txt")
                
            
     
'''
You can use glob:

import glob, os
os.chdir("/mydir")
for file in glob.glob("*.txt"):
    print(file)
or simply os.listdir:

import os
for file in os.listdir("/mydir"):
    if file.endswith(".txt"):
        print(os.path.join("/mydir", file))
or if you want to traverse directory, use os.walk:

import os
for root, dirs, files in os.walk("/mydir"):
    for file in files:
        if file.endswith(".txt"):
             print(os.path.join(root, file))
             
>>> import os
>>> path = '/usr/share/cups/charmaps'
>>> text_files = [f for f in os.listdir(path) if f.endswith('.txt')]
>>> text_files
['euc-cn.txt', 'euc-jp.txt', 'euc-kr.txt', 'euc-tw.txt', ... 'windows-950.txt']

import os

path = 'mypath/path' 
files = os.listdir(path)

files_txt = [i for i in files if i.endswith('.txt')]

I like os.walk():

import os, os.path

for root, dirs, files in os.walk(dir):
    for f in files:
        fullpath = os.path.join(root, f)
        if os.path.splitext(fullpath)[1] == '.txt':
            print fullpath
Or with generators:

import os, os.path

fileiter = (os.path.join(root, f)
    for root, _, files in os.walk(dir)
    for f in files)
txtfileiter = (f for f in fileiter if os.path.splitext(f)[1] == '.txt')
for txt in txtfileiter:
    print txt
share

Here's more versions of the same that produce slightly different results:

glob.iglob()
import glob
for f in glob.iglob("/mydir/*/*.txt"): # generator, search immediate subdirectories 
    print f
glob.glob1()
print glob.glob1("/mydir", "*.tx?")  # literal_directory, basename_pattern
fnmatch.filter()
import fnmatch, os
print fnmatch.filter(os.listdir("/mydir"), "*.tx?") # include dot-files

path.py is another alternative: https://github.com/jaraco/path.py

from path import path
p = path('/path/to/the/directory')
for f in p.files(pattern='*.txt'):
    print f
    
import os
import sys 

if len(sys.argv)==2:
    print('no params')
    sys.exit(1)

dir = sys.argv[1]
mask= sys.argv[2]

files = os.listdir(dir); 

res = filter(lambda x: x.endswith(mask), files); 

print res


You can simply use pathlibs glob 1:

import pathlib

list(pathlib.Path('your_directory').glob('*.txt'))
or in a loop:

for txt_file in pathlib.Path('your_directory').glob('*.txt'):
    # do something with "txt_file"
If you want it recursive you can use .glob('**/*.txt)

import os
fnames = ([file for root, dirs, files in os.walk(dir)
    for file in files
    if file.endswith('.txt') #or file.endswith('.png') or file.endswith('.pdf')
    ])
for fname in fnames: print(fname)

import glob
import os
filenames_without_extension = [os.path.basename(c).split('.')[0:1][0] for c in glob.glob('your/files/dir/*.txt')]
filenames_with_extension = [os.path.basename(c) for c in glob.glob('your/files/dir/*.txt')]

import glob
import os
filenames_without_extension = [os.path.basename(c).split('.')[0:1][0] for c in glob.glob('your/files/dir/*.txt')]
filenames_with_extension = [os.path.basename(c) for c in glob.glob('your/files/dir/*.txt')]             
'''
