from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required
from app.yandexAPI import YandexDiskAPI
from app import db, yandexClient
from app.models import User
from app.forms import LoginForm, RegisterForm
from aiohttp import ClientError
from yadisk_async.exceptions import YaDiskError


routes_bp = Blueprint('routes_bp', __name__)

@routes_bp.route('/')
async def index():
    return render_template('index.html', title="Главная страница")

@routes_bp.route('/login', methods=['GET', 'POST'])
async def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('routes_bp.index'))
        flash('Неверные email или пароль!', 'danger')
    return render_template('auth/login.html', form=form)

@routes_bp.route('/register', methods=['GET', 'POST'])
async def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Войдите в систему.', 'success')
        return redirect(url_for('routes_bp.login'))
    return render_template('auth/register.html', form=form)

@routes_bp.route('/logout')
@login_required
async def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('routes_bp.index'))

@routes_bp.route('/files', methods=['GET'])
@login_required
async def files():
    public_key = request.args.get('public_key')
    path = request.args.get('path')

    if not public_key:
        flash("Публичный ключ не предоставлен.", "warning")
        return redirect(url_for('routes_bp.index'))

    try:
        meta = await yandexClient.get_public_meta(public_key, path=path or "/")

        return render_template(
            'files.html',
            title="Список файлов",
            files=files_list,
            public_key=public_key,
            path=path
        )

    except YaDiskError as e:
        flash(f"Ошибка при работе с Яндекс.Диском: {str(e)}", "danger")
        return redirect(url_for('routes_bp.index'))
    except Exception as e:
        flash(f"Неизвестная ошибка: {str(e)}", "danger")
        return redirect(url_for('routes_bp.index'))

@routes_bp.route('/disk_info', methods=['GET'])
@login_required
async def disk_info():
    try:
        disk_info = await yandexClient.get_disk_info()
        return str(disk_info)
    except YaDiskError as e:
        flash(f"Ошибка при получении данных о диске: {str(e)}", "danger")
        return redirect(url_for('routes_bp.index'))