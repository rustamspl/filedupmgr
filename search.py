# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import sqlite3,os,time
from datetime import datetime
import hashlib
import ctypes



kdll = ctypes.windll.LoadLibrary("kernel32.dll")

dbfile="data.db3"
try:
    os.remove(dbfile)
except:
    pass
con = sqlite3.connect(dbfile)
#con.text_factory = str
con.row_factory = sqlite3.Row
con.isolation_level = None
cur = con.cursor()
sql='''CREATE table file(
    id integer  PRIMARY KEY  autoincrement,
    path string ,
    dir string , 
    name string ,
    ext string ,
    ctime timestamp ,
    mtime timestamp ,
    size int,
    md5 string 
)'''
cur.execute(sql)
cur.execute('CREATE unique INDEX ind_file_path ON file(PATH )')
#cur.execute('CREATE INDEX ind_file_name ON file(name)')
cur.execute('CREATE INDEX ind_file_size_md5 ON file(size,md5)')

def fileIterator(rootpath):
    for fdir, subdirs, files in os.walk(rootpath):
   
        for fname in files:       
            path=os.path.join(fdir,fname)
            try:
                st=os.stat(path) 
            except Exception as e:
                print e.winerror
                raise e 
            if(st.st_size>0):                  
                fn, ext = os.path.splitext(fname)

                with open(path, 'rb') as f:
                    data = f.read()
                    md5=hashlib.md5(data).hexdigest()
                yield path,fdir,fname,ext,st.st_size,datetime.fromtimestamp(st.st_ctime),datetime.fromtimestamp(st.st_mtime),md5


rootpath= u'D:\\music'
cur.execute('begin')
cur.executemany("INSERT INTO file(path,dir,name,ext,size,ctime,mtime,md5) VALUES (?,?,?,?,?,?,?,?)", fileIterator(rootpath))
cur.execute('commit')

sql='''select size,md5,ctime,count(1) from file a
group by size,md5,ctime
having count(1)>1'''
cur.execute(sql)
for rec in cur:
    raise Exception('duplicate size,md5: %s ,ctime: %s'%(rec['md5'],rec['ctime']))

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
    #os.unlink(rec['path'])
    #r=kdll.CreateSymbolicLinkW(rec['path'],rec['path1'],0)   
    print rec['path'], rec['path1']
  