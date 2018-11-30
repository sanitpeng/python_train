#coding=utf-8

#需要安装 mysql-python
#macOS 安装方法
#sudo brew install mysql-connector-c
#pip install mysql-python



from sqlalchemy import create_engine
import pandas as pd

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

def csv2sql(engine, fn):

    try:
        df = pd.read_csv(fn)
        print(df)
        df.to_sql('daily_tbl', con=engine, if_exists='append', index=False)
    except Exception as e:
        print(e.message)   


if __name__ == "__main__":

    csv2sql(engine, '~/abu/data/tdx_csv/SH#601398.csv')
