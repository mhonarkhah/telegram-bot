# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 00:31:14 2017

@author: mhonarkhah
"""

import sqlite3
from datetime import datetime, timedelta
import time


class DBHelper:

    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS voices (unixstamp int, user text, year int, month int, day int, duration num)"
        itemidx = "CREATE INDEX IF NOT EXISTS timeIndex ON voices (unixstamp ASC)" 
        ownidx = "CREATE INDEX IF NOT EXISTS userIndex ON voices (user ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()

    def add_voice(self, message):
        user = message['from']['first_name']
        unixtime =  message['date']
        t = datetime.fromtimestamp(unixtime)
        d = message['voice']['duration']
        stmt = "INSERT INTO voices (unixstamp, user, year, month, day, duration) VALUES (?, ?, ?, ?, ?, ?)"
        args = (unixtime, user, t.year, t.month, t.day, d)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_old_messages(self):
        curr_time = datetime.today()
        curr_time = datetime(curr_time.year, curr_time.month, curr_time.day)
        unixtime = int(time.mktime(curr_time.timetuple()))
        stmt = "DELETE FROM voices WHERE unixstamp < (?)"
        args = (unixtime,)
        #self.conn.execute(stmt, args)
        #self.conn.commit()

    def get_date_tuple(self, numdays=1):
        curr_time = datetime.today()
        curr_time = curr_time - timedelta(days=numdays-1)
        return (curr_time.year, curr_time.month, curr_time.day)        
        
    def get_summaries(self, numdays=1):
        curr_time = datetime(*self.get_date_tuple(numdays))
        unixtime = int(time.mktime(curr_time.timetuple()))
        
        stmt = 'SELECT user, COUNT(*), SUM(duration) FROM voices WHERE unixstamp > (?) GROUP BY user'
        args = (unixtime,)
        return list(self.conn.execute(stmt, args))
        
        
    def get_total(self, hour):
        year, month, day = self.get_date_tuple()
        older_time = datetime(year, month, day, hour, 0, 0)
        unixtime   = int(time.mktime(older_time.timetuple()))
        
        stmt = 'SELECT SUM(duration) FROM voices WHERE unixstamp > (?)'
        args = (unixtime,)
        return list(self.conn.execute(stmt, args))[0][0]
        
    def delete_all(self):
        stmt = "DELETE FROM voices"
        #self.conn.execute(stmt)
        #self.conn.commit()
        
    def get_user_list(self):
        stmt = 'SELECT DISTINCT user FROM VOICES'
        return list(self.conn.execute(stmt))

    
            


