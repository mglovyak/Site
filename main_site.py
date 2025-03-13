#импортирование библиотек
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect
import hashlib


#создаем шаблон фласк , указываем адресс базы данных 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Eco_site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#создаем базу данных и хэшируем данные пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_hash = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_email(self, email):
        self.email_hash = hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"ID: {self.id}, Email Hash: {self.email_hash}"


#создание логина и проверкина на првильность ввода данных
@app.route('/', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_email = request.form['email']
        form_password = request.form['password']
        
        email_hash = hashlib.sha256(form_email.lower().encode('utf-8')).hexdigest()
        user = User.query.filter_by(email_hash=email_hash).first()
        if user and user.check_password(form_password):
            return redirect('/site')
        else:
            error = 'Неправильно указан e-mail или пароль. Повторите попытку.'
    return render_template('login.html', error=error)
    
 #создание авторизации данных пользователя и проверка на уникальность данных       
@app.route('/regist', methods=['GET', 'POST'])
def regist():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        email_hash = hashlib.sha256(email.lower().encode('utf-8')).hexdigest()
        if User.query.filter_by(email_hash=email_hash).first():
            error = 'Пользователь с таким e-mail или паролем уже существует.'
            return render_template('registration.html', error=error)
        
        user = User()
        user.set_email(email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('registration.html')

#просто сайт о экологии
@app.route('/site', methods=['GET', 'POST'])
def eco_site():
    comments =[]
    if request.method == 'POST':
        comment = request.form['comment']
        if comment:
            comments.append(comment)
    return render_template('site.html',comments=comments)

def create_db():
    with app.app_context():
        db.create_all()
 
if __name__ == "__main__":
    create_db()
    app.run(debug=True)