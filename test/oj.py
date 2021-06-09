from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import time
from pytest import judge
import os
# 创建数据库引擎，连接数据库
engine = create_engine('mysql+mysqldb://root:123@localhost:3306/ojdb')


# 用automap_base创建反射对象，从数据库当中获取相应数据表的orm对象
# models中定义的外键无效

Base = automap_base()
Base.prepare(engine, reflect=True)
submitting = Base.classes.submitting
result = Base.classes.result
questions = Base.classes.questions
language = Base.classes.language
user = Base.classes.user
question_level = Base.classes.question_level

# 创建session
DbSession = sessionmaker(bind=engine)
session = DbSession()

complier = {
            "python": "pyflakes %s",
            "C": 'gcc %s -o m'
            }

path = {
        "python": "/home/zh/web/test/submited/%s/%s.py",
        "C": "/home/zh/web/test/submited/%s/%s.c"
        }

while True:
    session.commit()
    print(time.time())
    tasklist = session.query(submitting).filter_by(status_id=1).all()
    for i in tasklist:
        td_path = "/home/zh/web/app/static/testdata/%s" % i.question_id
        q = session.query(questions).filter_by(id=i.question_id).first()
        question_rank = session.query(question_level).filter_by(id=questions.level_id).first()
        u = session.query(user).filter_by(id=i.user_id).first()
        memory = q.memorylimit
        timelimit = q.timelimit
        print("提交记录id:%s，提交者:%s，题目：%s" % (i.id, u.username,q.question_name))
        td_total = q.total_data
        lg = session.query(language).filter_by(id=i.language_id).first()
        src_path = path[lg.language] % (i.user_id, i.question_id)
        com = os.system(complier[lg.language] % src_path)
        if com:  # 编译测试，如若未通过，返回"编译错误"结果，跳往下一个测试目标
            i.status_id = 2
            session.commit()
            continue
        r = judge(src_path, td_path, td_total, timelimit, memory)
        n = 0
        flag = True
        for j in r:
            n += 1
            add = result()
            add.submitting_id = i.id
            add.question_id = i.question_id
            add.user_id = i.user_id
            add.language_id = i.language_id
            add.submit_time = i.submit_time
            add.test_point = n
            add.result = j['result']
            if j["result"] != '测试通过':
                flag = False
                add.rank = 0
            else:
                add.rank = question_rank.rank/q.total_data
            if j['result'] not in ['编译错误', '答案错误', '系统错误', '运行错误']:
                add.time_used = j["timeused"]
                add.memory_used = j["memoryused"]
            i.rank += add.rank
            session.add(add)
        if flag:
            q.passed_num = q.passed_num+1
            i.status_id = 3
        else:
            i.status_id = 4
        session.flush()
        if len(session.query(submitting).filter(submitting.question_id == i.question_id).filter(submitting.user_id == i.user_id).all()) ==1:
            u.rank += i.rank
        session.commit()
    time.sleep(1)