#coding=utf-8
import pymysql

#打开数据库连接
db = pymysql.connect("localhost","root","11111111","stock_db" )
 
# 使用cursor()方法获取操作游标 
cursor = db.cursor()
 
# SQL 查询语句
sql = "select * from daily_tbl"
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    print(results)
    for row in results:
        print(row)
except:
    print ("Error: unable to fetch data")
 
# 关闭数据库连接
db.close()

