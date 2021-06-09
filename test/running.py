from ... import db
from ...models import submitting, result
from .pytest import judge
import time


def test():
    while True:
        t1 = time.time()
        tasklist = submitting.query.all()
        for i in tasklist:
            td_total = i.question.total_data
            td_path = "/home/zh/web/app/main/test/testdata/%s" % i.question_id
            if i.language_id == 1:
                src_path = "/home/zh/web/app/main/test/submited/%s/%s.py" % (i.user_id, i.question_id)
            elif i.language_id == 2:
                src_path = "/home/zh/web/app/main/test/submited/%s/%s.c" % (i.user_id, i.question_id)
            r = judge(src_path, td_path, td_total)
            n = 0
            for j in r:
                n += 1
                add = result()
                add.question_id = i.question_id
                add.user_id = i.user_id
                add.language_id = i.language_id
                add.submit_time = i.submit_time
                add.test_point = n
                add.result = j['result']
                if j["result"] == 'Accepted':
                    add.time_used = j["time_used"]
                    add.memory_used = j["memory_used"]
                db.session.add(add)
                db.session.flush()
                db.session.commit()
            db.session.delete(i)
            db.session.commit()
        t2 = time.time()
        if t2-t1 < 0.5:
            time.sleep(0.5+t1-t2)
    return()
