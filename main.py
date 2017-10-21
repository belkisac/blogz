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

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():

    if request.args != {}:
        post_id = request.args.get('id', '')
        post = Blog.query.get(post_id)
        title = post.title
        body = post.body
        return render_template('solo.html',title=title,body=body)
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
                flash("Username does not exist")
            if user.password != password:
                flash("Incorrect password")
    
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #verify input
        if len(username) < 3:
            flash("Username must be longer than 3 characters")
        if len(password) < 3:
            flash("Password must be longer than 3 characters")
        if password != verify:
            flash("Passwords do not match")
        else:
        #ensure username does not already exist
            existing_user = User.query.filter_by(username=username)

            if not existing_user:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash("Username already exists")

    return render_template('signup.html')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title = ''
    body = ''
    errors = False

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
            new_post = Blog(title,body)
            db.session.add(new_post)
            db.session.commit()
            post = Blog.query.filter_by(id=new_post.id).first()
            post_id = post.id
            return redirect(url_for('.blog_display', id=post_id))
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()