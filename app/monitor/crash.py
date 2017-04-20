# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from mmysql import MysqlBase
import time
from monitor_crash_config import conn_data_crash

app = Flask(__name__)


def get_data_mysql(conn, sql):
    m = MysqlBase(**conn)
    data = m.query(sql)
    return data


def return_time():
    base_time = time.time()
    end = base_time + 60
    base_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(base_time))
    end_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(end))
    return base_time, end_time


def write_file(files, data):
    with open(files, 'w')as f:
        f.write(str(data))


@app.route('/monitor_loginfo/')
def monitor_loginfo():
    times_base, time_end = return_time()
    before = "%s:00" % times_base
    end = "%s:00" % time_end
    sql = "select count(1) from loginfo where  datetime  between '%s' and '%s';" % (before, end)
    m = MysqlBase(**conn_data_crash)
    data = m.query(sql)
    files = "/tmp/loginfo.log"
    write_file(files, data[0][0])
    return '<h1>数据获取</h1>'


def get_data_crash(argv):
    times_base, time_end = return_time()
    before = "%s 00:00:00" % times_base[0:-6]
    end = "%s 00:00:00" % time_end[0:-6]
    sql_productModel = "select  %s,count(1) as num from loginfo \
    where datetime between '%s' and '%s' group by  %s \
    order by count(1) desc limit 10;" % (argv, before, end, argv)
    m = MysqlBase(**conn_data_crash)
    data = m.query(sql_productModel)
    return data


@app.route('/get_loginfo/', methods=['POST', 'GET'])
def get_loginfo():
    if request.method == 'POST':
        argv = request.form['argv']
    else:
        argv = request.args.get(['argv'])

    base_time, _ = return_time()
    data = get_data_crash(argv)
    return render_template('crash_show.html', data=data, argv=argv, times=base_time)

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001, debug=False)
