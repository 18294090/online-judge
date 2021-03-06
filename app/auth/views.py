from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask_login import login_user,logout_user,login_required
from ..models import user
from .forms import userlogin
from .. import db


@auth.route("/", methods=["POST", "GET"])
def login():
    if len(user.query.all()) == 0:  #如果用户数据库为空，添加admin用户
        u=user(username = "admin",password = "123",role_id =1)
        db.session.add(u)
        db.session.flush()
        db.session.commit()
    form1 = userlogin()
    if form1.validate_on_submit():
        u = user.query.filter_by(username=form1.username.data).first()
        if u and u.verify_password(form1.password.data):
            login_user(u, form1.remember_me.data)
            next = request.args.get('next')
            if not next or not next.startswith("/"):
                next = url_for('main.index')
            return(redirect(next))
        flash("错误的账号或密码")
    return(render_template("auth/login.html", form1=form1))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已成功退出系统")
    return(redirect(url_for('auth.login')))
