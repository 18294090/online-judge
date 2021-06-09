from app import db
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return (user.query.get(int(user_id)))


class role(db.Model):  # 角色表
    __table_args__ = {'extend_existing': True}
    __tablename__ = "role"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    role = db.Column(db.String(16), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    def has_permission(self, perm):
        return(self.permissions & perm == perm)

class Permission:
    practice = 1  # 练习
    problem = 2  # 出题
    check_code = 4  # 查看他人代码
    teacher = 8  # 课堂管理
    admin = 16  # 用户管理


class user(UserMixin, db.Model):  # 用户表
    __table_args__ = {'extend_existing': True}
    __tablename__ = "user"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    realname = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, ForeignKey("role.id"))
    role = db.relationship("role",backref=db.backref("user", lazy="dynamic"))
    gender = db.Column(db.String(1))
    login_time = db.Column(db.DateTime)
    login_ip = db.Column(db.String(64))
    status = db.Column(db.String(64))
    rank = db.Column(db.Integer)
    # 禁止读密码
    @property
    def password(self):
        return ("密码字段不可读")  # 当调用密码字段时，返回错误信息

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return(check_password_hash(self.password_hash, password))


class students(db.Model):
    __tablename__ = "students"
    __table_args__ = {'extend_existing': True}
    school_num = db.Column(db.String(32), ForeignKey("user.username"), primary_key=True)
    username = db.relationship('user', backref=db.backref('students'), uselist=False)
    name = db.Column(db.String(32))
    class_name = db.Column(db.String(32), ForeignKey("class_info.name", ondelete='CASCADE'))


class class_info(db.Model):
    __tablename__ = "class_info"
    __table_args__ = {'extend_existing': True}
    name = db.Column(db.String(32), primary_key=True)
    teacher = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    teacher_name = db.relationship("user", backref=db.backref("class_info"))
    status = db.Column(db.Boolean())
    students = db.relationship('students', backref=db.backref('class_info'), cascade='all, delete-orphan', passive_deletes=True)


class course(db.Model):
    __tablename__ = "class_info"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    class_name = db.Column(db.String(32), ForeignKey("class_info.name", ondelete='cascade'))
    start_time = db.Column(db.DateTime)
    over_time = db.Column(db.DateTime)
    sheet_id = db.Column(db.Integer,ForeignKey("sheet.id", ondelete='cascade'))

class question_level(db.Model):  # 定义题目等级
    __tablename__ = "question_level"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    level_name = db.Column(db.String(10))
    rank = db.Column(db.Integer)


class questions(db.Model):  # 建立题库模型
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question_name = db.Column(db.String(32))
    describe = db.Column(db.Text(4294967295))
    total_data = db.Column(db.Integer)
    author_id = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    author = db.relationship('user', backref=db.backref('questions'), cascade='all, delete',
    passive_deletes=True, foreign_keys=[author_id])
    level_id = db.Column(db.Integer, ForeignKey("question_level.id", ondelete='cascade'))
    level = db.relationship('question_level', backref=db.backref('questions'), cascade='all, delete',
    passive_deletes=True, foreign_keys=[level_id])
    submit_num = db.Column(db.Integer)
    passed_num = db.Column(db.Integer)
    algorithm = db.Column(db.String(32))
    question_time = db.Column(db.DateTime)
    timelimit = db.Column(db.Integer)
    memorylimit = db.Column(db.Integer)
    audited = db.Column(db.Boolean(0))
    checker_id = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    checker = db.relationship('user', backref=db.backref('checked_questions'), cascade='all, delete', passive_deletes=True, foreign_keys=[checker_id])
    check_time = db.Column(db.DateTime)

class problem(db.Model):
    __tablename__ = "problem"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    hint = db.Column(db.Text)
    source = db.Column(db.String(255))
    time_limit = db.Column(db.Integer)
    memory_limit = db.Column(db.Integer)
    status = db.Column(db.Integer)
    submit = db.Column(db.Integer)
    accepted = db.Column(db.Integer)
    solved = db.Column(db.Integer)
    tags = db.Column(db.Text)
    solution = db.Column(db.Text)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer,ForeignKey("user.id"))
    updated_at = db.Column(db.DateTime)
    polygon_problem_id = db.Column(db.Integer)

    


class sheet(db.Model):  # 题单信息
    __tablename__ = "sheet"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sheet_name = db.Column(db.String(32))
    describe = db.Column(db.String(32))
    owner_id = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    owner = db.relationship('user', backref=db.backref('sheets'), cascade='all, delete', passive_deletes=True,foreign_keys=[owner_id])


class question_belongs_to_sheet(db.Model):  # 题单与题目关系
    __tablename__ = "question_belongs_to_sheet"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    problem_id = db.Column(db.Integer, ForeignKey("problem.id", ondelete='cascade'))
    problem = db.relationship('problem', backref=db.backref('sheets'))
    sheet_id = db.Column(db.Integer, ForeignKey("sheet.id", ondelete='cascade'))
    sheet = db.relationship('sheet', backref=db.backref('problem'), cascade='all, delete',
    passive_deletes=True)


class language(db.Model):  # 编程语言
    __tablename__ = "language"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    language = db.Column(db.String(10))


class status(db.Model):
    __tablename__ = "status"
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(32))


class submitting(db.Model):  # 判题队列
    __tablename__ = "submitting"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    submit_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    user = db.relationship('user', backref=db.backref('submitted'), cascade='all, delete', 
    passive_deletes=True)
    question_id = db.Column(db.Integer, ForeignKey("problem.id", ondelete='cascade'))
    question = db.relationship('problem', backref=db.backref('submitted'), cascade='all, delete', 
    passive_deletes=True)
    language_id = db.Column(db.Integer, ForeignKey("language.id", ondelete='cascade'))
    language = db.relationship('language', backref=db.backref('submitted'), cascade='all, delete',
    passive_deletes=True)
    status_id = db.Column(db.Integer, ForeignKey("status.id", ondelete='cascade'))
    status = db.relationship('status', backref=db.backref('submitted'), cascade='all, delete', 
    passive_deletes=True)
    byte = db.Column(db.Integer)
    rank = db.Column(db.Integer)  # 本次提交得分
    result = db.relationship('result', backref=db.backref('submit'), cascade='all, delete',
    passive_deletes=True)


class result(db.Model):  # 测试结果
    __tablename__ = "result"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey("questions.id", ondelete='cascade'))
    question = db.relationship('questions', backref=db.backref('result'))
    user_id = db.Column(db.Integer, ForeignKey("user.id", ondelete='cascade'))
    user = db.relationship('user', backref=db.backref('result'), cascade='all, delete',
    passive_deletes=True)
    test_point = db.Column(db.Integer)
    result = db.Column(db.String(22))
    memory_used = db.Column(db.Integer)
    time_used = db.Column(db.Integer)
    submit_time = db.Column(db.DateTime)
    language_id = db.Column(db.Integer, ForeignKey("language.id", ondelete='cascade'))
    language = db.relationship('language', backref=db.backref('result'), cascade='all, delete',
    passive_deletes=True)
    submitting_id = db.Column(db.Integer, ForeignKey("submitting.id"))
    rank = db.Column(db.Integer)
