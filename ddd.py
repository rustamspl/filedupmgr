# -*- coding: utf-8 -*-
import sqlite3,os,time
from datetime import datetime
import hashlib
import ctypes



kdll = ctypes.windll.LoadLibrary("kernel32.dll")

dbfile="data.db3"

con = sqlite3.connect(dbfile)
#con.text_factory = str
con.row_factory = sqlite3.Row
con.isolation_level = None
cur = con.cursor()

sql='''select b.path,c.path path1 from file b
join
(
select size,md5,min(ctime) ctime,count(1) from file a
group by size,md5
having count(1)>1
) g on g.size=b.size and g.md5=b.md5 and b.ctime>g.ctime
join file c on c.size=g.size and c.md5=g.md5 and c.ctime=g.ctime
'''
cur.execute(sql)
for rec in cur:
    try:
        #os.unlink(rec['path'])
        #r=kdll.CreateSymbolicLinkW(rec['path'],rec['path1'],0)   
        print rec['path'], rec['path1']
    except:
        print "err:%s"%(rec['path1'])