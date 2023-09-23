from flask import Flask,render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_required,login_user,logout_user,current_user
import hashlib
from bardapi import Bard
import os

os.environ["_BARD_API_KEY"] = "bQh-1wA0VAEug6jP-2b4tBkfJSdoxweeXBUzvhfTTrm3NyFiKjbtgpvJxqXPPU7Wwcd9MA."

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
app.secret_key = 'suiiiiiiiiiiiii'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
LoginManager.login_view = 'login'

class User(db.Model,UserMixin):
      id = db.Column(db.Integer, primary_key=True)
      user_name = db.Column(db.String(10), nullable=False)
      email = db.Column(db.String(50), nullable=False, unique=True)
      password = db.Column(db.String(80), nullable=False)
      profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
      
      def __init__(self,user_name, email, password):
            self.email = email
            self.user_name = user_name
            self.password = hashlib.sha256(password.encode()).hexdigest()
      
      def check_password(self, password):
            hashed_psw = hashlib.sha256(password.encode()).hexdigest()
            return self.password == hashed_psw


@login_manager.user_loader
def loader(user_id):
      return User.query.get(int(user_id))
      

@app.route('/')
def home():
      if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
      bg = url_for('static',filename='pics/bg.png')     
      return render_template('index.html',bg=bg)
      
@app.route('/register', methods=['GET','POST'])
def register():
      if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
      if request.method == 'POST':
            userName = request.form['name']
            email = request.form['email']
            password = request.form['password']
            c_password = request.form['c_password']
            v_name = User.query.filter_by(user_name=userName).all()
            if v_name:
                  error= 'UserName already used try another UserName!'
                  return render_template('register.html',error=error)
            v_email = User.query.filter_by(email=email).all()
            if v_email:
                  error= 'Email already used try another email!'
                  return render_template('register.html',error=error)
            if len(password) > 7:
                  if password == c_password:
                        new_usr = User(user_name=userName,email=email,password=password)
                        db.session.add(new_usr)
                        db.session.commit()
                        return redirect(url_for('login'))
                  else:
                        a = {'email':email,'name':userName}
                        error = 'Password did not matched !!'
                        return render_template('register.html',error=error,a=a)
            else:
                  a = {'email':email,'name':userName}
                  error='Password must  contain 8 characters !'
                  return  render_template('register.html',error=error,a = a)
      return render_template('register.html', title='Register')
      return render_template('register.html')
      
@app.route('/login', methods=['GET','POST'])
def login ():
      if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
      if request.method == 'POST':
            email = request.form['email']
            password= request.form['password']
            user = User.query.filter_by(email=email).first()
     
            if user and user.check_password(password):
                  login_user(user)
                  return redirect(url_for('dashboard'))
            else:
                  a = {'email':email}
                  error='Invalid Email or Password!'
                  return render_template('login.html',a=a,error=error)
      return  render_template('login.html',title='Login')
      
      return render_template('login.html')
 
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
      pic = url_for('static',filename='pics/'+current_user.profile_pic)
     
      if request.method == 'POST':
            query = request.form['input']
            response = Bard().get_answer(query)['content']
            return render_template('dashboard.html',query=query, response=response,pic=pic)
      return render_template('dashboard.html')
      
@app.route('/account', methods=['GET','POST'])
@login_required
def account():
      
      pic = url_for('static',filename='pics/'+current_user.profile_pic)
      
      if request.method == "POST":
                        name = request.form['name']
                        email = request.form['email']
                        password = request.form['password']
                        v_email = User.query.filter_by(email=email).first()
                        v_name = User.query.filter_by(user_name=name).first()
                        
                        if v_name and v_name != current_user:
                              error = 'User name already taken !!'
                              return render_template('account.html', error=error, pic=pic)
                              
                        
                        if v_email and v_email != current_user:
                              error = 'Email already in use !!'
                              return render_template('account.html', error=error, pic=pic)
                              
                        
                        if len(password) > 7:
                                     
                              current_user.user_name = name
                              current_user.email = email
                              current_user.password = hashlib.sha256(password.encode()).hexdigest()
                              db.session.commit()
                              return redirect(url_for('account'))
                        
                        
     
      return render_template('account.html',pic=pic)

      
@app.route('/logout')
@login_required
def logout():
      logout_user()
      return redirect(url_for('home'))
@app.route('/delete/<int:id>')
@login_required
def delete(id):
      user = User.query.filter_by(id=id).first()
      db.session.delete(user)
      db.session.commit()
      
      logout_user()
      return redirect(url_for('home'))
      
if __name__ == '__main__':
      with app.app_context():
            db.create_all()
      app.run(debug=True,port=6969)