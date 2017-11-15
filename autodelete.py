# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:01:36 2017

@author: Nouey
"""

import sqlite3
import sys
import os

#pour chrome
keywords = ["demotivateur"]
conn = sqlite3.connect(os.getenv('APPDATA')+"\\..\\Local\\Google\\Chrome\\User Data\\Default\\History")

c = conn.cursor()
#mettre une exeception pour "database is locked"
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table';") #lists all tables
except Exception as e:
    if "database is locked" == str(e):
        print("You need to close your browser first, can't access the database")
        sys.exit(0)
    else:
        print(e)
        
result = c.fetchall() 

for var_tuple in result: #looks for "urls" in the list of tables, because that's where the urls are stored 
    #print(var_tuple)
    if "urls" in var_tuple:
        found = True
        break
    
if not found:
    print("Can't find the good table in the database")
    sys.exit(0)

c.execute("select sql from sqlite_master where type = \'table\' and name = \'urls\';") #gets the create table
schema = c.fetchone()[0]
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL, CONSTRAINT check_url CHECK (url NOT LIKE \'%reddit%\'and (url not like \'%mcgill%\'and (url not like \'%raddit%\'and (url not like \'%lol%\'and (url not like \'%maco%\'))))));"
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL)"

print(schema+"\n---------------------------------------")
preschema = schema[:-1] #serves to take out the last parenthesis, so that if there is no constraint, everything else runs smoothly
preschema_split = preschema.split(',')

#remplacement du nom "url", pour qu'on crée une table différent et qu'il n'y ait pas de conflit
#on prend chaque partie de la liste de chaque coté d' "urls"
preschema_split_url = preschema_split[0].split("urls")
preschema_split[0] = preschema_split_url[0] + "test" + preschema_split_url[1] # on met test à la place d'url

for index, i in enumerate(preschema_split): #verifier s'il y a déjà une contrainte
    if "constraint" in i.lower():
        if "check_url" in i.lower():
            save = preschema_split.pop(index)
            
save = ""
if save:
    load = save[:-1].split(')')[0] + ' and (url not like'
    """print(load)
    print("---------------------")"""
else:
    load = ' CONSTRAINT check_url CHECK (url not like'

for index,i in enumerate(keywords): #organiser les keywords et les conditions
    """t = (i,)
    print(type((i,)))"""
    c.execute("delete from urls where url like ?", ('%' + i + '%',)) #we delete the entries that don't match with the condition we're setting

    if index == 0:
        load = load + ' \'%' + i + '%\''
    else:
        load = load + 'and (url not like \'%' + i + '%\''

load = load + ")"*(load.count('(')+1) +';' # on ferme toutes les parenthèses + celle du tout début

print("This load will be added:"+load+"\n-------------------------")

postschema = ''
for i in preschema_split:
    postschema = postschema + i + ','

postschema = postschema + load

print(postschema)
c.execute(postschema)
c.execute("insert into test select * from urls")
c.execute("drop table urls")
c.execute("alter table test rename to urls")

conn.commit()
conn.close()