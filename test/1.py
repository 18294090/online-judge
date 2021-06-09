from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import time
from pytest import judge
import os
# 创建数据库引擎，连接数据库
engine = create_engine('mysql+mysqldb://root:123@localhost:3306/ojdb')

# 用automap_base创建反射对象，从数据库当中获取相应数据表的orm对象
Base = automap_base()
Base.prepare(engine, reflect=True)
submitting = Base.classes.submitting
result = Base.classes.result
questions = Base.classes.questions
language = Base.classes.language

# 创建session
DbSession = sessionmaker(bind=engine)
session = DbSession()

s = session.query(submitting).filter_by(id=24).first()
print(s.result)