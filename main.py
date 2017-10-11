from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:MyPassword@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(256))

    def __init__(self,title,body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog_display():

    posts = Blog.query.all()
    return render_template('blog.html',posts=posts)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title = ''
    body = ''

    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']

        if post_title == '':
            flash("Please enter a title")
            title = ''
            return redirect('/newpost')
        else:
            title = post_title
        if post_body == '':
            flash("Please enter the body of your post")
            body = ''
            return redirect('/newpost')
        else:
            body = post_body

        if not title and not body:
            new_post = Blog(post_title,post_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog')
    
    return render_template('newpost.html')


if __name__ == '__main__':
    app.run()