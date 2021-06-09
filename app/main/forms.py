from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import PasswordField, SubmitField, SelectField, StringField, IntegerField
from flask_wtf import FlaskForm
from flask_wtf.file import DataRequired
from flask_ckeditor import CKEditorField
from flask_codemirror.fields import CodeMirrorField
from wtforms.validators import InputRequired, EqualTo


extend_existing = True


class loginform(FlaskForm):
    class_name = SelectField(label="请选择班级", validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,

        )
    stuname = SelectField(label="请选择学生名", validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,
        )
    password = PasswordField("请输入密码", validators=[InputRequired("请输入密码")])
    submit = SubmitField("登录")


class userlogin(FlaskForm):
    username = StringField(label="用户名", validators=[DataRequired('请输入账号')])
    password = PasswordField("密码", validators=[InputRequired("请输入密码")])
    submit = SubmitField("登录")


class reset_pwd_form(FlaskForm):
    pwd1 = PasswordField("输入新密码", validators=[InputRequired("必须输入数据")])
    pwd2 = PasswordField("再次输入新密码", validators=[InputRequired("必须输入数据"), EqualTo("pwd1", "输入不一致")])
    submit = SubmitField("确认")


class upload_xlsx(FlaskForm):
    file = FileField("请选择文件", validators=[
        FileRequired(),
        FileAllowed(['xlsx'], 'xlsx only!')])
    submit = SubmitField("提交")


class multitext(FlaskForm):  # 出题form
    question_name = StringField('标题', validators=[InputRequired("必须输入数据")])
    describe = CKEditorField('题目描述', validators=[InputRequired("必须输入数据")])
    select = SelectField(label="水平层次", validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,
        coerce=int)
    algorithm = StringField('算法标签', validators=[InputRequired("必须输入数据")])
    timelimit = IntegerField("时间限制", validators=[InputRequired("必须输入数据")])
    memorylimit = IntegerField('内存限制')
    file = FileField("请选择测评数据文件", validators=[
        FileRequired(),
        FileAllowed(['zip', 'rar'], 'rar,zip only!')])
    submit = SubmitField('提交')


class selectform(FlaskForm):
    select = SelectField(label="请选择要操作班级", validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,)
    submit = SubmitField("上课")
    submit1 = SubmitField("下课")


class submitcode(FlaskForm):  # 代码提交form
    select = SelectField(label="选择编程语言", validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,
        coerce=int)
    c = CodeMirrorField(language='python', config={'autofocus': True})
    submit = SubmitField('提交代码')


class sift(FlaskForm):  # 筛选框
    submitter = StringField("提交者")
    question_name = StringField("题目名称")
    language = SelectField(label='语言', validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,
        coerce=int)
    status = SelectField(label='状态', validators=[DataRequired('请选择标签')],
        render_kw={'class': 'form-control'},
        default=3,
        coerce=int)
    submit = SubmitField('确定')
