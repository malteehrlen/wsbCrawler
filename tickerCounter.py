#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Malte Ehrlen, malte@ehrlen.com, 2018

import praw
import re
import csv
import pickle
import time
from praw.models import MoreComments

class Ticker:
    def __init__(self, name):
        self.name = name
        self.titleMentions = {"time":[],\
                             "context":[],\
                             "score":[]}
        self.bodyMentions = {"time":[],\
                             "context":[],\
                             "score":[]}
        self.replyMentions = {"time":[],\
                             "context":[],\
                             "score":[]}
                     
tckrRe = re.compile(r'\$[A-Z]+')       
    
reddit = praw.Reddit(client_id='your-id', 
                     client_secret='your-secret',
                     user_agent='your-agent')
                     
wsb = reddit.subreddit('wallstreetbets')
crawledSubmissions = []
crawledReplies = []
tckrList = []

def countTickers(submission):
    if submission.id not in crawledSubmissions:
        crawledSubmissions.append(submission.id)
        #first do title
        tckrMentions = tckrRe.findall(submission.title)
        if tckrMentions:
            for tckrMention in tckrMentions:
                tckrFound = False
                for tckr in tckrList:
                    if tckr.name == tckrMention:
                        tckr.titleMentions['time'].append(
                            submission.created)
                        tckr.titleMentions['context'].append(
                            submission.title)
                        tckr.titleMentions['score'].append(
                            submission.score)
                        tckrFound = True
                        break
                if not tckrFound:
                    tckrList.append(Ticker(tckrMention))
                    tckrList[-1].titleMentions['time'].append(
                        submission.created)
                    tckrList[-1].titleMentions['context'].append(
                        submission.title)
                    tckrList[-1].titleMentions['score'].append(
                        submission.score)
        #body
        tckrMentions = tckrRe.findall(submission.selftext)
        if tckrMentions:
            for tckrMention in tckrMentions:
                tckrFound = False
                for tckr in tckrList:
                    if tckr.name == tckrMention:
                        tckr.bodyMentions['time'].append(
                            submission.created)
                        tckr.bodyMentions['context'].append(
                            submission.selftext)
                        tckr.bodyMentions['score'].append(
                            submission.score)
                        tckrFound = True
                        break
                if not tckrFound:
                    tckrList.append(Ticker(tckrMention))
                    tckrList[-1].bodyMentions['time'].append(
                        submission.created)
                    tckrList[-1].bodyMentions['context'].append(
                        submission.selftext)
                    tckrList[-1].bodyMentions['score'].append(
                        submission.score)
    
    #comments
    submission.comments.replace_more(limit=None)
    commentQueue = submission.comments[:]
    for comment in submission.comments.list():
        if comment.id not in crawledReplies:
            crawledReplies.append(comment.id)
            tckrMentions = tckrRe.findall(comment.body)
            if tckrMentions:
                for tckrMention in tckrMentions:
                    tckrFound = False
                    for tckr in tckrList:
                        if tckr.name == tckrMention:
                            tckr.replyMentions['time'].append(
                                comment.created)
                            tckr.replyMentions['context'].append(
                                comment.body)
                            tckr.replyMentions['score'].append(
                                comment.score)
                            tckrFound = True
                            break
                    if not tckrFound:
                        tckrList.append(Ticker(tckrMention))
                        tckrList[-1].replyMentions['time'].append(
                            comment.created)
                        tckrList[-1].replyMentions['context'].append(
                            comment.body)
                        tckrList[-1].replyMentions['score'].append(
                            comment.score)

def main():                        
    while True:
        submissions = wsb.hot(limit=100)
        for submission in submissions:
            countTickers(submission)
        with open('output.csv', 'wb') as output:
            writer = csv.writer(output)
            writer.writerow(['ticker name', 
                             'number of mentions (title):', 
                             'number of mentions (replies):',
                             'most upvoted comment (score)'])
            for tckr in tckrList:
                try:
                    maxpost = tckr.replyMentions['context']\
                    [tckr.replyMentions['score'].index(
                        max(tckr.replyMentions['score'])
                        )].encode('utf-8')
                    maxscore = max(tckr.replyMentions['score'])
                except: 
                    maxpost = u'--'
                    maxscore = u'--'
                writer.writerow([tckr.name, 
                                 len(tckr.titleMentions['time']),
                                 len(tckr.replyMentions['time']),
                                 maxpost, 
                                 maxscore])
        with open('tickerMyPickle', 'wb') as output:
            pickle.dump(tckrList, output)
        
        time.sleep(1800)
if __name__ == '__main__':
    main()