#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Malte Ehrlen, malte@ehrlen.com, 2018

import praw
import re
import csv
import pickle
import time
import tickerDb
from praw.models import MoreComments
                     
tckrRe = re.compile(r'\$[A-Z]+')       
    
reddit = praw.Reddit(client_id='your-ID', 
                     client_secret='your-secret',
                     user_agent='your-agent')
                     
wsb = reddit.subreddit('wallstreetbets') #or any other subreddit ofc

def countTickers(submission):
    if not tickerDb.isCrawled(submission.id):
        tickerDb.addRedditID(submission.id)
        #first do title
        tckrMentions = list(set(tckrRe.findall(submission.title)))
        for tckr in tckrMentions:
            tickerDb.addTickerInfo(tckr,
                                   submission.id,
                                   submission.created,
                                   submission.title,
                                   submission.score,
                                   'title')
        #body
        tckrMentions = list(set(tckrRe.findall(submission.selftext)))
        for tckr in tckrMentions:
            tickerDb.addTickerInfo(tckr,
                                   submission.id,
                                   submission.created,
                                   submission.title,
                                   submission.score,
                                   'body')                
    
    #comments
    submission.comments.replace_more(limit=None)
    commentQueue = submission.comments[:]
    for comment in submission.comments.list():
        if not tickerDb.isCrawled(comment.id):
            tickerDb.addRedditID(comment.id)
            tckrMentions = list(set(tckrRe.findall(comment.body)))
            for tckr in tckrMentions:
                tickerDb.addTickerInfo(tckr,
                                       comment.id,
                                       comment.created,
                                       comment.body,
                                       comment.score,
                                       'reply')    

def main():                        
    while True:
        submissions = wsb.hot(limit=500)
        for submission in submissions:
            countTickers(submission)
        
        time.sleep(1800)
if __name__ == '__main__':
    main()
    tickerDb.dbClose()