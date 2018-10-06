import sys
import os
import json
import glob
import re
import sqlite3

if __name__ == "__main__":
    '''print(len(sys.argv),sys.argv)'''
    parameters = {"source_dir"  :"./lst"
                 } 
    '''parameters by index'''             
    pp =  {1:"source_dir"
          }
          
    '''parameters by string'''      
    ps =  {"-i" :"source_dir"
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
    search_pattern = os.path.join(source_path,"*.mglist")
    
    in_conn = sqlite3.connect("./thumb_full.db")
    in_cursor = in_conn.cursor()
    
    '''print(source_path, search_pattern)'''
    for file_path in glob.glob(search_pattern):
        in_path = os.path.abspath(file_path)
        out_path = os.path.join(source_path,os.path.splitext( os.path.basename(file_path) )[0]+".db")
        
        in_  = open(in_path)
        if os. path. isfile(out_path):
            os.remove(out_path)

        out_conn = sqlite3.connect(out_path)
        out_cursor = out_conn.cursor()
        
        print('--opened--')

        print('preparing tables...', out_cursor.execute('CREATE TABLE IF NOT EXISTS moby_games(id INTEGER PRIMARY KEY, approved INTEGER, title VARCHAR(256), url VARCHAR(1024), publisher VARCHAR(128),year INTEGER,platforms VARCHAR(256),genre VARCHAR(128),perspective VARCHAR(128),visual VARCHAR(128),pacing VARCHAR(128),interface VARCHAR(128),setting TEXT, images TEXT,themes TEXT, sports TEXT,gameplay TEXT,vehicular TEXT,narrative TEXT,art TEXT,add_on TEXT,spec_ed TEXT,misc TEXT)') )
#        print( cursor.execute('DELETE FROM boby_games') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_approved_index ON moby_games(approved)') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_title_index ON moby_games(title)') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_publisher_index ON moby_games(publisher)') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_year_index ON moby_games(year)') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_platforms_index ON moby_games(platforms)') )
        print('preparing indexes...', out_cursor.execute('CREATE INDEX game_genre_index ON moby_games(genre)') )
        out_conn.commit()

        for url in in_:
            url = url.strip().replace("http","https")
            print(url)
            if ( in_cursor.execute("SELECT approved,title,url,publisher,year,platforms,genre,perspective,visual,pacing,interface,setting,images,themes,sports,gameplay,vehicular,narrative,art,add_on,spec_ed,misc " + \
                                   "FROM moby_games " + \
                                   "WHERE (url=?) LIMIT 1",(url,)
                                  ) ):
                data = in_cursor.fetchone()
#                print(data)
                if( out_cursor.execute("INSERT INTO moby_games(approved,title,url,publisher,year,platforms,genre,perspective,visual,pacing,interface,setting,images,themes,sports,gameplay,vehicular,narrative,art,add_on,spec_ed,misc) " + \
                                       "            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ",data)
                                      ):
                    print("--inserted--")
                
            
        out_conn.commit()
        out_conn.close()
        in_.close()
    in_conn.close()
     
