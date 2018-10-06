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
    
def is_valid_data(data):
    return (data != None) and ('Title' in data) and ('Released' in data) and ('Genre' in data) and ('Url' in data)
    
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

        print('preparing tables...', cursor.execute('CREATE TABLE IF NOT EXISTS moby_games(id INTEGER PRIMARY KEY, approved INTEGER, title VARCHAR(256), url VARCHAR(1024), publisher VARCHAR(128),year INTEGER,platforms VARCHAR(256),genre VARCHAR(128),perspective VARCHAR(128),visual VARCHAR(128),pacing VARCHAR(128),interface VARCHAR(128),setting TEXT, images TEXT)') )
#        print( cursor.execute('DELETE FROM boby_games') )
        print('preparing indexes...', cursor.execute('CREATE INDEX game_approved_index ON moby_games(approved)') )
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
        
    def is_valid_data(self,data):
        return (data != None) and ('Title' in data) and ('Released' in data) and ('Genre' in data) and ('Url' in data)
        
    def add_entry(self,data):
        result = False
        if len(data) > 0:
            approved = 0
            if is_valid_data(data):
                approved = 1
                            
            title = ""
            url = ""
            publisher = ""
            year = ""
            platform = ""
            genre = ""
            prespective = ""
            visual = ""
            pacing = ""
            interface = ""
            setting = ""
            images = ""
            
            if 'Title' in data:
                title = data['Title']
            if 'Url' in data:
                url = data['Url']
            if 'Released' in data:  
                year = ",".join( data['Released'] )
            if 'Genre' in data:
                genre = ",".join( data['Genre'] )
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
            
            params = (title,approved,url,publisher,year,platform,genre,prespective,visual,pacing,interface,setting,images,)
            if g_verbose:
                print(len( params ) )
                try_print(params)
            
            conn = self.conn
            cursor = self.cursor     
            try_print('--params--',params)   
            if cursor.executemany('INSERT INTO moby_games(title,approved,url,publisher,year,platforms,genre,perspective,visual,pacing,interface,setting,images)'+ \
                                                 'VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)', (params,) ):
                conn.commit()
                result = True
                print("--added to db--")
            else:
                append_to_file("|".join(params)+"\n","doubt.txt")
                print("--fail to add to db--")
        else:
            print("--bad data empty--")
        return result
        
base_url = 'https://www.mobygames.com'
g_controled_data = ['Published by','Released','Platforms','Platform','Genre','Perspective','Visual','Pacing','Interface','Setting']
g_tag_exeptions = ['link','meta','script']
re_cover = re.compile('front-cover.*\.(jpg|jpeg|png|bmp)')
re_screenshot = re.compile('screenshot.*\.(jpg|jpeg|png|bmp)')
g_patterns = ['html/body/div(wrapper)/div[container]/div[row](main)/div[col-md-12 col-lg-12]/div[lifesupport-header]/div/div/div[moBrowse]/div[mobList]/div[molist]/table[molist](mof_object_list)/tbody/tr/','html/body/div(wrapper)/div[container]/div[row](main)/div[col-md-12 col-lg-12]/div[lifesupport-header]/div/div/div[moBrowse]/div[mobList]/div[molist]/table[molist](mof_object_list)/tbody/tr/td/','html/body/div(wrapper)/div[container]/div[row](main)/div[col-md-12 col-lg-12]/div[lifesupport-header]/div/div/div[moBrowse]/div[mobList]/div[molist]/table[molist](mof_object_list)/tbody/tr/td/a/']
g_name_pos =['Title','Released','Published by','Genre','Platform']

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tagId = ""
        self.output_data = []
        self.data_pos = -1
        self.current_pattern = ""
        self.full_pattern = ""
        self.errors = []

    def handle_starttag(self, tag, attrs):
        self.tagId = tag
        node_class = ""
        node_id = ""
        href = ""
        if g_verbose:
            try_print("Start tag:", tag)
        try_print("Start tag:", tag)
        
#        if tag  not in g_tag_exeptions:
        if True:
            for attr in attrs:
                if g_verbose:
                    try_print("     attr:", attr)
                if attr[0] == "id":
                    node_id = attr[1]
                elif attr[0] == "class":
                    node_class = attr[1]
                elif tag == "a" and attr[0] == "href":
                    href = attr[1]
            node_format = "{ntag}"
            if node_class:
                node_format +="[{nclass}]"
            if node_id:
                node_format +="({nid})"
            node_format+="/"
            self.current_pattern = node_format.format(ntag=self.tagId, nclass= node_class, nid = node_id)
            self.full_pattern += self.current_pattern
            print("Current pattenr: ",self.current_pattern,len(self.current_pattern))
            print("Full pattenr: ",self.full_pattern,len(self.full_pattern))
        
        if self.full_pattern == g_patterns[0]:
            self.output_data.append({})
            self.data_pos = 0 
        if self.full_pattern == g_patterns[1]:
            ilast = len(self.output_data) - 1
            if self.data_pos > 0:
                self.output_data[ilast][g_name_pos[self.data_pos]]=[]
        if self.full_pattern == g_patterns[2] and len(href) > 0:
            ilast = len(self.output_data) - 1
            if "Url" not in self.output_data[ilast]:
                self.output_data[ilast]["Url"] = href
            
               
    def handle_endtag(self, tag):
        if g_verbose:
            try_print("End tag  :", tag)
        if self.full_pattern == g_patterns[1]:
            self.data_pos+=1
        if True:
            last_pos = self.full_pattern.rfind(tag)
            self.full_pattern = self.full_pattern[:last_pos]
            print("Current pattenr: ",self.current_pattern,len(self.current_pattern))
            print("Full pattenr: ",self.full_pattern,len(self.full_pattern))
            self.current_pattern = ""
         

    def handle_data(self, data):
# check for data patterns etc        
        if g_verbose:
            try_print("Data  :", data)
        if self.full_pattern == g_patterns[2]:
            ilast = len(self.output_data) - 1
            if self.data_pos == 0:
                self.output_data[ilast][ g_name_pos[self.data_pos] ] = data
            elif self.data_pos > 0:
                self.output_data[ilast][ g_name_pos[self.data_pos] ].append(data)
                
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

if __name__ == "__main__":
    parser = MyHTMLParser()
    output = Output('./thumb_full.db')
    for offset in range(0,90000,25):
        page_url = "https://www.mobygames.com/browse/games/offset,{_offset_}/so,0a/list-games/".format(_offset_=offset)
        print("--start page ["+page_url+"] download--")
        req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read().decode('utf-8')
        parser.output_data = []        
        parser.feed(html)
        output_data = parser.output_data
        for data in output_data:
            output.add_entry(data)
