#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Malte Ehrlen, malte@ehrlen.com, 2018
from datetime import datetime
import sqlite3


db = sqlite3.connect('Tickers.db')
c = db.cursor()

c.execute("create table if not exists redditID(ID text primary key)")
db.commit()

def addRedditID(redditID):
    c.execute("select * from redditID where ID=?", (redditID,))
    if c.fetchall():
        return
    else:
        c.execute("insert into redditID values (?)", (redditID,))
        db.commit()

def isCrawled(redditID):
    c.execute("select * from redditID where ID=?", (redditID,))
    if c.fetchall():
        return True
    else:
        return False

def addTickerInfo(tckr, redditID, time, context, score, type):
    #remove the dolla sign
    name = scrub(tckr.replace('$', ''))
    
    #check if ticker allready exists and create if needed
    ensureTickerExists(name, redditID)
    
    date = datetime.utcfromtimestamp(time)
    datestring = date.strftime("%Y-%m-%d %H:%M:%S")
    
    if type=='title':
        tableName = name+'_title_mentions'
    elif type=='body':
        tableName = name+'_body_mentions'
    elif type=='reply':
        tableName = name+'_reply_mentions'
    else:
        print 'unknown type:'+type
        return 1
    c.execute("insert into "+tableName+" values (?, ?, ?, ?)", (
                 redditID,
                 datestring,
                 context,
                 score
                 ))
                 
def getTickerInfo(tckr):
    name = scrub(tckr.replace('$', ''))
    tableName = name+'_title_mentions'
    c.execute("select * from "+tableName)
    tm = c.fetchall()
    tableName = name+'_body_mentions'
    c.execute("select * from "+tableName)
    bm = c.fetchall()
    tableName = name+'_reply_mentions'
    c.execute("select * from "+tableName)
    cm = c.fetchall()
    return (tm, bm, cm)
    
def ensureTickerExists(name, id):
    
    c.execute("""create table if not exists {} (
                 id text primary key,
                 time text,
                 context text,
                 score integer)""".format(name+'_title_mentions'))
    c.execute("""create table if not exists {} (
                 id text primary key,
                 time text,
                 context text,
                 score integer)""".format(name+'_body_mentions'))
    c.execute("""create table if not exists {} (
                 id text primary key,
                 time text,
                 context text,
                 score integer)""".format(name+'_reply_mentions'))
    db.commit()
    
def scrub(table_name):
    return ''.join( chr for chr in table_name if chr.isalnum() )

def dbClose():
    db.close()