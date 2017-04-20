#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
date: 2016/07/11
role: mysql的增删改查类
usage: m = mysqlBase(host='xxx',db='xxx',user='xxx',pwd='xxx')    实例化
       m.insert('core',{'host_name':'ccc','process_name':'ddd','ip_addr':'192.168.136.41','status':'4'})
       m.update('table',{'field1':'value1','field2':'value2'},'id=1')  更新表名  字段名：值  条件
       m.delete('core','status=5 and id=12')
       m.change("update core set a='aaa' where id=1")   可以多条插入
       m.query("select * from core")
"""
from common import logMsg

import warnings

try:
    import MySQLdb
except ImportError, e:
    logMsg('error', 'MySQLdb import error', 2)
    raise ImportError('No module named MySQLdb')


###mysql操作类
class MysqlBase:
    ###连接数据库
    def __init__(self, **args):

        ###获取参数
        self.host = args.get('host', 'localhost')
        self.user = args.get('user')
        self.pswd = args.get('pswd')
        self.db = args.get('db', 'mysql')
        self.port = args.get('port', '3306')
        self.charset = args.get('charset', 'utf8')

        try:
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.pswd, db=self.db,
                                        port=int(self.port), charset=self.charset)

            self.curs = self.conn.cursor()

            self.curs.execute('SET NAMES utf8')
        except:
            logMsg('error', '%s mysql connect error' % self.host, 2)
            raise ValueError('mysql connect error %s' % self.host)

    ###释放资源
    def __del__(self):
        self.curs.close()
        self.conn.close()

        ###插入

    def insert(self, table, data):
        _field = ','.join(['`%s`' % (k_insert) for k_insert in data.keys()])
        _value = ','.join(["'%s'" % (str(v_insert).replace("'", "\'")) for v_insert in data.values()])
        ###拼接成sql语句
        _sql = 'INSERT INTO `%s`(%s) VALUES(%s)' % (table, _field, _value)

        ###执行
        self.curs.lastrowid = 0
        try:
            self.curs.execute(_sql)
            ###提交
            self.conn.commit()
            logMsg('insert', '%s insert ' % _sql, 1)
        except:
            self.conn.rollback()
            logMsg('error', '%s insert error' % _sql, 2)
            raise ValueError('112,insert error %s' % _sql)

        return self.curs.lastrowid

    ###更新
    def update(self, table, data, condition):
        _field = ','.join(["`%s`='%s'" % (k_update, str(data[k_update]).replace("'", "\'")) for k_update in data])

        _sql = 'UPDATE `%s` SET %s WHERE %s' % (table, _field, condition)

        ###执行
        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            ###提交
            self.conn.commit()
            logMsg('update', '%s update ' % _sql, 1)
        except:
            self.conn.rollback()
            logMsg('error', '%s update error' % _sql, 2)
            raise ValueError('update error %s' % _sql)

        return resNum

    ###删除
    def delete(self, table, condition):
        _sql = 'DELETE FROM `%s` WHERE %s' % (table, condition)

        ###执行
        resNum = 0
        try:
            resNum = self.curs.execute(_sql)
            ###提交
            self.conn.commit()
            logMsg('delete', '%s delete ' % _sql, 1)
        except:
            self.conn.rollback()
            logMsg('error', '%s delete error' % _sql, 2)
            raise ValueError('112,delete error %s' % _sql)

        return resNum

    ###直接给修改语句执行
    def change(self, sql, many=False):
        ###过滤unknow table的warning
        warnings.filterwarnings('ignore')
        resNum = 0
        if many:
            try:
                ###多条同时插入
                resNum = self.curs.executemany(sql, many)
                self.conn.commit()
                logMsg('success', '%s exec ' % sql, 1)
            except:
                self.conn.rollback()
                logMsg('error', '%s exec error' % sql, 2)
                raise ValueError('exec error %s' % sql)
        else:
            try:
                resNum = self.curs.execute(sql)
                ###提交
                self.conn.commit()
                logMsg('change', '%s exec ' % sql, 1)
            except:
                self.conn.rollback()
                logMsg('error', '%s exec error' % sql, 2)
                raise ValueError('112,exec error %s' % sql)

        return resNum

    ###查询
    def query(self, sql):
        res = ''
        try:
            self.curs.execute(sql)
            res = self.curs.fetchall()
            logMsg('select', '%s query ' % sql, 1)
        except:
            logMsg('error', '%s query error' % sql, 2)
        # raise ValueError('query error %s'% sql)

        return res


if __name__ == "__main__":
    args = dict()
    args['host'] = '172.16.17.164'
    args['user'] = 'miles'
    args['pswd'] = 'aspect'
    args['db'] = 'test'
    sql_sel = "select * from bigdata_host limit 5"
    m = MysqlBase(**args)
    data = m.query(sql=sql_sel)
    m.insert('bigdata_host', {'hostname': 'ccc', 'remark': 'ddd', 'up_addr_p': '192.168.136.41', 'states': '4',
                              'enter_time': '2017-03-13'})
    m.delete('bigdata_host', 'hostname="ccc"')
