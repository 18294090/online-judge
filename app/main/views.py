from . import main
from .forms import loginform,  reset_pwd_form, multitext, submitcode, userlogin, upload_xlsx, selectform, sift
from flask import render_template, abort, session, redirect, url_for, request, send_from_directory, jsonify, flash
from ..models import problem, user, questions, question_level, language, submitting, result, class_info, students, class_info
import os
from .. import db
from datetime import datetime
from flask_ckeditor import upload_success, upload_fail
import zipfile
from sqlalchemy import or_, distinct
#import pandas as pd
from flask_login import current_user
from flask_paginate import Pagination, get_page_parameter
import phpserialize


color = ["info", "danger", "success", "warning"]


"""@main.route("/", methods=["POST", 'GET'])
def login():  # 处理登录逻辑,下拉列表选择用户
    classes = class_info.query.filter_by(status=True).all()
    form = loginform()
    form1 = userlogin()
    if classes:
        form.class_name.choices = [v.name for v in classes]
        form.stuname.choices = [(v.school_num, v.name) for v in classes[0].students]
    if form.validate_on_submit():
        stuname = form.stuname.data
        password = form.password.data
        login_check = students.query.filter_by(school_num=stuname).first().username
        if login_check.id and login_check.password == password:
            session["userid"] = login_check.id
            return(redirect(url_for("main.index")))
        else:
            return(render_template("test.html", x=session["userid"]))
    if form1.validate_on_submit():
        username = form1.username.data
        password = form1.password.data
        login_check = user.query.filter_by(username=username).first()
        if login_check and login_check.password == password:
            session["userid"] = login_check.id
            return(redirect(url_for("main.index")))
        else:
            return(render_template("test.html", x=session["userid"]))
    return(render_template("login.html", form=form, form1=form1))"""

@main.route("/")
def root():
    return(redirect("/auth/"))

@main.route("/select/", methods=["POST", "GET"])  # 根据网页发来的下列列表选择，返回相应的二级下拉列表选项
def stu_match_class():
    if request.method == 'POST':
        data = request.get_json()
        class_name = data['class_name']
        stu = students.query.filter_by(class_name=class_name).all()
        d = [(i.school_num, i.name) for i in stu]
        return jsonify(d)


@main.route("/index/", methods=["POST", 'GET'])
def index():  # 首页
    w=[]
    try:
        p = problem.query.all()
        for i in p:
            j = (phpserialize.loads(str.encode(i.sample_input,'utf-8')))
            w.append(j)
    except Exception:
        db.session.rollback()
    form = upload_xlsx()  # 电子表格提交表单
    class_select = selectform()
    classes = class_info.query.filter_by(teacher = current_user.id).all()
    class_select.select.choices = [v.name for v in classes]
    cla = class_info.query.filter_by(status=True).all()
    if form.validate_on_submit():
        try:
            file = request.files["file"].read()  # 获取前端提交的文件对象，并读取为二进制流
            sheet = pd.read_excel(file,usecols=[0, 1, 2])  # pandas读取excel文件
            for index, i in sheet.iterrows():  # 遍历入数据库
                add = user()
                stu = students()
                add.username = i["学号"]
                add.roleId = 3
                add.password = "111"
                add.rank = 0
                stu.school_num = i["学号"]
                stu.name = i["姓名"]
                stu.class_name = i["班级"]
                db.session.add(add)
                db.session.flush()
                db.session.add(stu)
                db.session.flush()
            db.session.commit()
            flash("文件导入成功")
        except IOError:
            flash("文件导入失败")
            db.session.rollback()
    if class_select.validate_on_submit():
        s = class_select.select.data
        c = class_info.query.filter_by(name=s).first()
        if class_select.submit.data:
            c.status = True
        elif class_select.submit1.data:
            c.status = False
        db.session.commit()
        return(redirect(url_for("main.index")))
    return(render_template("index.html", u=current_user, w=w,form=form, form1=class_select, cla=cla))


@main.route("/download/<filepath>", methods=["GET"])  # 下载excel文件
def download_excel(filepath):
    return(main.send_static_file("excel/download/" + filepath))


@main.route("/index/reset/", methods=["POST", 'GET'])
def reset_pwd():  # 重置密码
    form = reset_pwd_form()
    u = user.query.filter_by(id=session["userid"]).first()
    if form.validate_on_submit():
        u.password = request.form["pwd2"]
        db.session.commit()
        return("重置成功")
    else:
        pass
    return(render_template("reset_password.html", form=form, u=u))


@main.route("/index/set_questions/", methods=["POST", "GET"])
def set_questions():  # 出题逻辑
    form = multitext()
    level = question_level.query.all()
    form.select.choices = [(s.id, s.level_name) for s in level]
    add = questions()
    if request.method == 'POST':
        add.question_name = request.form["question_name"]
        add.describe = request.form["describe"]
        add.algorithm = request.form["algorithm"]
        add.timelimit = request.form["timelimit"]
        add.memorylimit = request.form["memorylimit"]
        add.level_id = form.select.data
        add.author_id = current_user.id
        add.question_time = datetime.now()
        add.submit_num = 0
        add.passed_num = 0
        file = request.files.get("file")
        r = zipfile.is_zipfile(file)
        db.session.add(add)
        db.session.flush()
        path = "app/static/testdata/"+str(add.id)
        os.mkdir(path)  # 新建题目测试数据文件夹
        if r:
            fz = zipfile.ZipFile(file, "r")
            fz.extractall(path)
        else:
            return("文件格式错误，请选择正确的压缩包文件")
        add.total_data = len(fz.namelist())//2
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        return(redirect(url_for("main.index")))
    return(render_template("set_questions.html", form=form))


@main.route("/questions/<arg>", methods=["POST", "GET"])
def question_list(arg):  # 题库列表
    search = False  # 分页切片，flask_paginate模块实现
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)
    start = (page-1)*20
    end =page*20
    if arg == "all":
        que = problem.query.slice(start,end)
    else:
        que = problem.query.filter(or_(problem.id == arg, problem.title.like(arg), problem.tags.like(arg))).slice(start,end)
    pagination = Pagination(page=page, per_page=20, total=len(problem.query.all()), bs_version=4, search=search, record_name='que')
    return(render_template("questions_list.html", questions=que, id=arg,pagination = pagination))


@main.route("/question/<id>", methods=["POST", "GET"])
def question(id):  # 显示题目内容,提交代码
    s = submitting()
    u = user.query.filter_by(id=session["userid"]).first()
    que = questions.query.filter_by(id=id).first()
    form = submitcode()
    q = language.query.all()
    form.select.choices = [(s.id, s.language) for s in q]
    try:
        path = "test/submited/%s" % session["userid"]
        if not os.path.exists(path):
            os.mkdir(path)
        if request.form.get(form.select.data) == 2:
            path = path + "/%s.c" % (id)
        else:
            path = path + "/%s.py" % (id)
        fd = open(path, "r", encoding='utf-8')
        code = fd.read()
        fd.close()
    except IOError:
        code = ""
    form.c.data = code
    if request.method == 'POST':
        code = request.form.get("c")
        byte = len(code)
        if form.select.data == 1:
            fd = open("test/submited/%s/%s.py" % (session["userid"], id), "w", encoding='utf-8')
        else:
            fd = open("test/submited/%s/%s.c" % (session["userid"], id), "w", encoding='utf-8')
        fd.write(code)
        fd.close()
        s.submit_time = datetime.now()
        s.user_id = session["userid"]
        s.question_id = id
        s.language_id = form.select.data
        s.status_id = 1
        s.rank = 0
        s.byte = byte
        que.submit_num += 1
        db.session.add(s)
        db.session.flush()
        db.session.commit()
        return(redirect("/recorder/%d" % s.id))
    return(render_template("question_detail.html", q=que, u=u, form=form))


'''
@main.route("/question/<id>/submit", methods=["POST", "GET"])
def submit(id):  # 代码提交
    s = submitting()
    u = user.query.filter_by(id=session["userid"]).first()
    select_form = selectform()
    q = language.query.all()
    select_form.select1.choices = [(s.id, s.language) for s in q]
    try:
        path = "test/submited/"
        if request.form.get(select_form.select1.data) == 2:
            path = path+"/%s/%s.c" % (session["userid"], id)
        else:
            path = path+"/%s/%s.py" % (session["userid"], id)
        fd = open(path, "r", encoding='utf-8')
        code = fd.read()
        fd.close()
    except IOError:
        code = ""
    if request.method == 'POST':
        code = request.form.get("c")
        byte = len(code)
        if select_form.select1.data == 1:
            fd = open("test/submited/%s/%s.py" % (session["userid"], id), "w", encoding='utf-8')
        else:
            fd = open("test/submited/%s/%s.c" % (session["userid"], id), "w", encoding='utf-8')
        fd.write(code)
        fd.close()
        s.submit_time = datetime.now()
        s.user_id = session["userid"]
        s.question_id = id
        s.language_id = select_form.select1.data
        s.status_id = 1
        s.byte = byte
        que = questions.query.filter_by(id=id).first()
        que.submit_num += 1
        db.session.add(s)
        db.session.flush()
        db.session.commit()
        return(redirect("/recorder/%d" % s.id))
    return(render_template("submit.html", id=id, form=select_form, code=code, u=u, s=s))
'''


@main.route("/test_monitor/", methods=["POST", "GET"])
def monitor():
    if request.method == "POST":
        os.system("python3 test/oj.py")

    r = result()
    r = r.query.all()
    return(render_template('monitor.html', r=r))


@main.route("/recorder/<id>", methods=["POST", "GET"])
def recorder(id):
    u = user.query.filter_by(id=session["userid"]).first()
    db.session.commit()
    s = submitting.query.filter_by(id=id).first()
    t = 0
    m = 0
    print(s.result)
    try:
        path = "test/submited/"
        if s.language_id == 2:
            path = path+"/%s/%s.c" % (session["userid"], s.question_id)
        elif s.language_id == 1:
            path = path+"/%s/%s.py" % (session["userid"], s.question_id)
        fd = open(path, "r", encoding='utf-8')
        code = fd.read()
        fd.close()
    except IOError:
        code = ""
    if s.status_id == 3:
        for i in s.result:
            t = max(t, i.time_used)
            m = max(m, i.memory_used)
    return(render_template("recorder_detail.html", submit=s, time=t, memory=m, code=code, u=u, color=color))


@main.route('/files/<path:filename>', methods=['GET'])
def uploaded_files(filename):
    path = '/home/zh/web/app/static/upload'  # 必须是绝对路径
    return(send_from_directory(path, filename))


@main.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')  # 获取上传图片文件对象
    # Add more validations here
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:  # 验证文件类型示例
        return upload_fail(message='Image only!')  # 返回upload_fail调用
    f.save(os.path.join('app/static/upload', f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url=url)  # 返回upload_success调用


@main.route("/recorders/<u>/<v>", methods=["POST", "GET"])
def recorders(u, v):
    s = submitting()
    us = user()
    si = sift()
    
    if u == "question":
        table = s.query.order_by(submitting.submit_time.desc()).filter_by(question_id=v).all()
    elif u == "user":
        table = s.query.order_by(submitting.submit_time.desc()).filter_by(user_id=v).all()
    elif u == "all":
        table = s.query.order_by(submitting.submit_time.desc()).all()
    else:
        return(abort(404))
    return(render_template("recorders.html", table=table, sg=u, sift=si, color=color))


@main.route('/login_out', methods=['GET', 'POST'])
def login_out():
    session.clear()
    return redirect(url_for('main.login'))


@main.route("/rank", methods=['GET', 'POST'])
def rank_list():
    u = user.query.order_by(user.rank.desc()).all()
    
    return(render_template("rank_list.html",  table=u))


@main.route("/class_off/<class_name>", methods=['GET', 'POST'])
def class_off(class_name):
    return(class_name)
    return(redirect("/index"))


@main.route("/personal_info/<id>", methods=['GET', 'POST'])
def personal_info(id):
    
    u1 = user.query.filter_by(id=id).first()
    s = submitting.query.filter(submitting.user_id == id)
    s1 = s.filter_by(status_id=3)
    s2 = db.session.query(distinct(submitting.question_id)).filter(submitting.user_id == id)
    s3 = db.session.query(distinct(submitting.question_id)).filter(submitting.user_id == id).filter(submitting.status_id ==3)
    table = s.order_by(submitting.submit_time.desc()).limit(5)
    return(render_template("personal_info.html", u1=u1, s=s1.all(), s2=s2, s3=s3,table=table,color=color))
