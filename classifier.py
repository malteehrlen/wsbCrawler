#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Malte Ehrlen, malte@ehrlen.com, 2018

import sqlite3
import sys
import csv
import msvcrt
import pickle
import os
from colorama import Fore, Back, Style, init
init()
    
db = sqlite3.connect('Tickers.db')
db.row_factory = sqlite3.Row
c = db.cursor()

with open('analyzed.p', 'rb') as f:
    analyzed = pickle.load(f)
# analyzed = []
c.execute("select * from redditID")
inpMsg = 'sentiment? (p=positive, n=negative, u=neutral)'
for id in c.fetchall():
    if id[0] not in analyzed:
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for tablerow in c.fetchall():
            table = tablerow[0]
            c.execute("SELECT * from {t}".format(t = table))
            for row in c:
                if (id[0] == row['id']):
                    if 'context' in row.keys():
                        message = row['context'].encode('utf-8')
                        titlename = table.encode('utf-8').split('_')[0]
                        print Fore.MAGENTA+titlename+Style.RESET_ALL+': ',
                        print Fore.CYAN+message+Style.RESET_ALL
                        sentiment = 'u'
                        print Style.DIM+inpMsg+Style.RESET_ALL
                        while True:
                            sentiment = msvcrt.getch()
                            if sentiment == 'p':  
                                break
                            elif sentiment == 'n':
                                break
                            elif sentiment == 'u':
                                break
                            else:
                                with open('analyzed.p', 'wb') as f:
                                    pickle.dump(analyzed, f)
                                sys.exit()
                        analyzed.append(id[0])
                        with open('sentiment.csv', 'ab') as f:
                            w = csv.writer(f, delimiter=',')
                            w.writerow([titlename, sentiment, message])
                        os.system('cls' if os.name == 'nt' else 'clear')

with open('analyzed.p', 'wb') as f:
    pickle.dump(analyzed, f)