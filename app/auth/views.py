from . import auth
from .. import db
from ..models import Admin
from .forms import LoginForm, NewPasswordForm
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(phone_num=form.phone_num.data).first()
        if admin is not None and admin.verify_password(form.password.data):
            login_user(admin, form.remember_me.data)
            return redirect(url_for('main.index'))
        flash('手机号或密码输入错误。')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录。')
    return redirect(url_for('auth.login'))


@auth.route('/password', methods=['GET', 'POST'])
@login_required
def new_password():
    form = NewPasswordForm()
    if form.validate_on_submit():
        admin = Admin.query.get(current_user.id)
        if admin.verify_password(form.old_password.data) is not True:
            flash('旧密码输入不正确。')
            return render_template('auth/password.html', form=form)
        admin.password = form.password.data
        db.session.add(admin)
        db.session.commit()
        flash('更新密码成功，请重新登录。')
        return redirect(url_for('auth.login'))
    return render_template('auth/password.html', form=form)
