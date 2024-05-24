from flask import Flask, send_from_directory, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import os

app = Flask(__name__)

# Assuming the 3rd partition is mounted at /mnt/p3
UPLOAD_FOLDER = '/mnt/p3'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)

# In-memory user store
users = {'user': {'password': 'password'}}

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    user = User()
    user.id = username
    return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    if (username in users and request.form['password'] == users[username]['password']):
        user = User()
        user.id = username
        login_user(user)
        return redirect(url_for('index'))

    return 'Bad login'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out'

@app.route('/')
@login_required
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return '<a href="/upload">Upload</a> <a href="/logout">Logout</a></br></br>' + '<br>'.join(['<a href="/uploads/{}">{}</a>'.format(f, f) for f in files])

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)