from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:GoodPassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gsr345456gfdfgdfGDFGHDF'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(256))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_display', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():

    if request.args != {}:
        if request.args['id']:
            post_id = request.args.get('id', '')
            post = Blog.query.filter_by(id=post_id).first()
            title = post.title
            body = post.body
            return render_template('solo.html',title=title,body=body)
        if request.args['user']:
            username = request.args.get('user', '')
            user = User.query.filter_by(username=username).first()
            posts = user.posts
            return render_template('singleUser.html', posts=posts)
    else:
        posts = Blog.query.all()
        return render_template('blog.html',posts=posts)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            if not user:
                flash("Username does not exist", "username_error")
            if user.password != password:
                flash("Incorrect password", "password_error")
    
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ''
    errors = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        #verify input
        if len(username) < 3:
            flash("Username must be longer than 3 characters", "username_error")
            username = ''
            errors = True
        if len(password) < 3:
            flash("Password must be longer than 3 characters", "password_error")
            username = username
            errors = True
        if password != verify:
            flash("Passwords do not match", "verify_error")
            username = username
            errors = True
        if existing_user:
            flash("Username already exists", "existing_error")
            username = ''
            errors = True
        if errors:
            return render_template('signup.html', username=username)
        else:
        #ensure username does not already exist
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')


    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.args != {}:
        username = request.args.get('user', '')
        user = User.query.filter_by(username=username).first()
        posts = user.posts
        return redirect(url_for('.blog_display', user=username))
    else:
        users = User.query.all()
        return render_template('index.html',users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title = ''
    body = ''
    errors = False
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == '':
            flash("Please enter a title", "title_error")
            title = ''
            errors = True
        else:
            title = title
        if body == '':
            flash("Please enter the body of your post", "body_error")
            body = ''
            errors = True
        else:
            body = body
        if errors:
            return render_template('newpost.html',title=title,body=body)
        else:
            new_post = Blog(title,body,owner)
            db.session.add(new_post)
            db.session.commit()
            post = Blog.query.filter_by(id=new_post.id).first()
            post_id = post.id
            return redirect(url_for('.blog_display', id=post_id))
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()