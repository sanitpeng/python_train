#coding=utf-8

from __future__ import print_function
#需要安装 mysql-python
#macOS 安装方法
#sudo brew install mysql-connector-c
#pip install mysql-python

import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import (INTEGER, CHAR, FLOAT, BIGINT)
from sqlalchemy import Column, Table, MetaData

host = 'localhost'
db = 'stock_db'
user = 'root'
password = '11111111'

engine = create_engine(str(r"mysql+mysqldb://%s:" + '%s' + "@%s/%s?charset=utf8") 
    % (user, password, host, db))

def read_sql(engine):
    try:
        df = pd.read_sql(sql=r'select * from daily_tbl', con=engine)
    except Exception as e:
        print(e.message)

def csv2sql(fn, table, engine):

    try:
        df = pd.read_csv(fn)
        df.to_sql(table, con=engine, if_exists='replace', index=False)
    except Exception as e:
        print(e.message)   



def file_list(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            fn, ext = os.path.splitext(file)
            if ext == '.csv':
                L.append((os.path.join(root, file), fn))
    return L

#废弃，使用pd.to_sql
def create_table(tbl_name, engine):

    try:
        meta = MetaData()
        table = Table(tbl_name, meta,
            Column('id', INTEGER, primary_key=True),
            Column('date', INTEGER),
            Column('open', FLOAT),
            Column('high', FLOAT),
            Column('low', FLOAT),
            Column('close', FLOAT),
            Column('volume', BIGINT),
            Column('count', FLOAT)
        )
        table.create(bind=engine)    
    except Exception as e:
        print(e.message)   


if __name__ == "__main__":


    fl = file_list('/Users/sanit/abu/data/tdx_csv/Volumes/export')

    """
    csv2sql('/Users/sanit/abu/data/tdx_csv/Volumes/export/SZ#300579.csv', 
        'SZ#300579', engine)
    """

    len = len(fl)
    for i, l in enumerate(fl):
        csv2sql(l[0], l[1], engine)
        print("处理%s, 完成进度百分之%d" %( l[0], (float(i+1)/len)*100 ), end="\r" )
    
    print("\n")

