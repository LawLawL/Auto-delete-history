# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:01:36 2017

@author: Nouey
"""

import sqlite3
import sys
import os
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-b", "--browser", help="Which browser you want to set the rules for")
parser.add_argument("-k", "--keywords", help="Which keywords you want to forbid in your history")

args = parser.parse_args()

keywords = args.keywords.split(',')

if args.browser.lower() == "chrome":
    path = os.getenv('APPDATA') + "\\..\\Local\\Google\\Chrome\\User Data\\Default\\"
elif args.browser.lower() == "vivaldi":
    path = os.getenv('APPDATA') + "\\..\\Local\\Vivaldi\\User Data\\Default\\"
    
def check_availability(cursor, tablename):
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #lists all tables
    except Exception as e:
        if "database is locked" == str(e):
            print("You need to close your browser first, can't access the database")
            sys.exit(0)
        else:
            print(e)
        
    result = cursor.fetchall() 

    for var_tuple in result: #looks for "urls" in the list of tables, because that's where the urls are stored 
    #print(var_tuple)
        if tablename in var_tuple:
            return True
            
    return False

def save_parameters(path, tablename, check=False): #tested
    conn = sqlite3.connect(path)
    c = conn.cursor()
    schema = get_schema(c,tablename)
    if check:
        if os.path.isfile("backup_create_table_" + tablename) :
            print("There is already a backup for " + tablename)
            return
 
    file = open("backup_create_table_" + tablename, "w")
    file.write(schema)
    file.close() 
    
    conn.commit()
    conn.close()
    
def clean_table(path, tablename): #tested
    conn = sqlite3.connect(path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT name FROM sqlite_master WHERE type='table';") #lists all tables
    except Exception as e:
        if "database is locked" == str(e):
            print("You need to close your browser first, can't access the database")
            sys.exit(0)
        else:
            print(e)
        
    result = c.fetchall() 
    
    for var_tuple in result: #looks for the table we want
    #print(var_tuple)
        if tablename in var_tuple:
            found = True
            break
    
    if not found:
        print("Can't find the good table in the database")
        sys.exit(0)
        
    try: #on vérifie que la backup soit là avant de tout jeter
        file = open("backup_create_table_" + tablename, "r")
    except:
        print("Cannot find the backup file of the format backup_create_table_" + tablename)
        sys.exit(0)

    c.execute("drop table "+tablename+";")
    
    
    c.execute(file.readline())
    
    conn.commit()
    conn.close()
    
def get_schema(cursor, tablename): #tested
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #lists all tables
    except Exception as e:
        if "database is locked" == str(e):
            print("You need to close your browser first, can't access the database")
            sys.exit(0)
        else:
            print(e)
        
    result = cursor.fetchall() 
    found = False
    for var_tuple in result: #looks for "urls" in the list of tables, because that's where the urls are stored 
    #print(var_tuple)
        if tablename in var_tuple:
            found = True
            break
    if not found:
        print("Can't find the good table in the database")
        sys.exit(0)

    cursor.execute("select sql from sqlite_master where type = \'table\' and name = \'"+tablename+"\';") #gets the create table
    result = cursor.fetchone()[0]
    return result

def wrapper_get_schema(filename, tablename):
    
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    return get_schema(c,tablename)

def get_content_table(cursor,tablename):
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") #lists all tables
    except Exception as e:
        if "database is locked" == str(e):
            print("You need to close your browser first, can't access the database")
            sys.exit(0)
        else:
            print(e)
        
    result = cursor.fetchall() 
    found = False
    for var_tuple in result: 
        
        if tablename in var_tuple:
            found = True
            break
    if not found:
        print("Can't find the good table in the database")
        sys.exit(0)
    
    cursor.execute("select * from " + tablename + ";") #gets the content
    result = cursor.fetchall()
    return result
    
def wrapper_get_content_table(filename, tablename):
    
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    return get_content_table(c,tablename)
    

"""def set_rules_history(path, keywords): #tested

    conn = sqlite3.connect(path)
    
    c = conn.cursor()

    schema = get_schema(c, "urls")
#mettre une exeception pour "database is locked"
 #renvoie un array, gets the first element
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL, CONSTRAINT check_url CHECK (url NOT LIKE \'%reddit%\'and (url not like \'%mcgill%\'and (url not like \'%raddit%\'and (url not like \'%lol%\'and (url not like \'%maco%\'))))));"
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL)"
    print("The current table looks like that:\n")
    print(schema+"\n---------------------------------------")
    preschema = schema[:-1] #serves to take out the last parenthesis, so that if there is no constraint, everything else runs smoothly
    preschema_split = preschema.split(',')

#remplacement du nom "url", pour qu'on crée une table différent et qu'il n'y ait pas de conflit
#on prend chaque partie de la liste de chaque coté d' "urls"
    preschema_split_url = preschema_split[0].split("urls")
    preschema_split[0] = preschema_split_url[0] + "test" + preschema_split_url[1] # on met test à la place d'url

    save = ""
    
    for index, i in enumerate(preschema_split): #verifier s'il y a déjà une contrainte
        if "constraint" in i.lower():
            if "check_url" in i.lower():
                save = preschema_split.pop(index)
            
    if save:
        load = save[:-1].split(')')[0] + ' and (url not like'

    else:
        load = ' CONSTRAINT check_url CHECK (url not like'

    for index,i in enumerate(keywords): #organiser les keywords et les conditions

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

    c.execute(postschema)
    c.execute("insert into test select * from urls")
    c.execute("drop table urls")
    c.execute("alter table test rename to urls")

#checking everything went fine
    c.execute("select sql from sqlite_master where type = \'table\' and name = \'urls\';") #gets the create table
    newschema = c.fetchone()[0]
    
    print("The new tables looks like:\n",newschema,"\n--------------------------------------")
    
    conn.commit()
    conn.close()"""

def set_rules(path, keywords, table, valuename):#to test 

    conn = sqlite3.connect(path)

    c = conn.cursor()
   #mettre une exeception pour "database is locked"
    schema = get_schema(c,table) #renvoie un array, gets the first element
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL, CONSTRAINT check_url CHECK (url NOT LIKE \'%reddit%\'and (url not like \'%mcgill%\'and (url not like \'%raddit%\'and (url not like \'%lol%\'and (url not like \'%maco%\'))))));"
#schema = "CREATE TABLE \"urls\"(id INTEGER PRIMARY KEY AUTOINCREMENT,url LONGVARCHAR,title LONGVARCHAR,visit_count INTEGER DEFAULT 0 NOT NULL,typed_count INTEGER DEFAULT 0 NOT NULL,last_visit_time INTEGER NOT NULL,hidden INTEGER DEFAULT 0 NOT NULL)"
    #print("The current table looks like that:\n")
    #print(schema+"\n---------------------------------------")
    preschema = schema[:-1] #serves to take out the last parenthesis, so that if there is no constraint, everything else runs smoothly
    preschema_split = preschema.split(',')

#remplacement du nom "url", pour qu'on crée une table différent et qu'il n'y ait pas de conflit
#on prend chaque partie de la liste de chaque coté d' "urls"
    preschema_split_url = preschema_split[0].split(table)
    preschema_split[0] = preschema_split_url[0] + "test" + preschema_split_url[1] # on met test à la place d'url

    save = ""
    
    for index, i in enumerate(preschema_split): #verifier s'il y a déjà une contrainte
        if "constraint" in i.lower():
            if "check_"+valuename in i.lower():
                save = preschema_split.pop(index)
                break
    save_split = save.split('%')
    print(save_split[i] for i in range(len(save_split)) if i & 1)
            
    if save:
        load = save[:-1].split(')')[0] + ' and (' + valuename + ' not like'

    else:
        load = ' CONSTRAINT check_'+valuename+' CHECK (' + valuename + ' not like'

    for index,i in enumerate(keywords): #organiser les keywords et les conditions

        c.execute("delete from " + table + " where " + valuename + " like ?", ('%' + i + '%',)) #we delete the entries that don't match with the condition we're setting

        if index == 0:
            load = load + ' \'%' + i + '%\''
        else:
            load = load + 'and (' + valuename + ' not like \'%' + i + '%\''

    load = load + ")"*(load.count('(')+1) +';' # on ferme toutes les parenthèses + celle du tout début

    #print("This load will be added/modified:"+load+"\n-------------------------")

    postschema = ''
    for i in preschema_split:
        postschema = postschema + i + ','

    postschema = postschema + load

    """c.execute(postschema)
    c.execute("insert into test select * from " + table)
    c.execute("drop table " + table)
    c.execute("alter table test rename to " + table)"""

#checking everything went fine
    c.execute("select sql from sqlite_master where type = \'table\' and name = \'" + table + "\';") #gets the create table
    newschema = c.fetchone()[0]
    
    print("The new create_table for " + table + " looks like:\n",newschema,"\n--------------------------------")
    
    conn.commit()
    conn.close()

def autodelete(path, keywords):
    save_parameters(path+'Cookies','cookies', True)
    save_parameters(path+'History','urls', True)
    save_parameters(path+'History','keyword_search_terms', True)
    save_parameters(path+'History','segments', True)
    save_parameters(path+'Network Action Predictor','network_action_predictor', True)
    
    set_rules(path + "Cookies", keywords, "cookies", "host_key")
    set_rules(path + 'History', keywords, "urls", "url") 
    set_rules(path + 'History', keywords, "keyword_search_terms", "lower_term")
    set_rules(path + 'History', keywords, "segments", "name")
    set_rules(path + 'Network Action Predictor', keywords, "network_action_predictor", "url")
    
if __name__ == "__main__":
    autodelete(path, keywords)
    #save_parameters(path+'Cookies','cookies')
    
    #set_rules(path + "Cookies", keywords, "cookies", "host_key")
    #clean_table(path + 'Network Action Predictor','network_action_predictor')

    #print(wrapper_get_schema(path + 'Network Action Predictor','network_action_predictor'))