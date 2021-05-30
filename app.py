import mysql.connector
import os
import hashlib
from flask import Flask, url_for, render_template, redirect, request, session
from flask_bootstrap import Bootstrap

db = mysql.connector.connect(
    host = "hostname",
    user = "username",
    password = "password",
    database = "databasename"
)
if True:
    db.reconnect()

cr = db.cursor(dictionary=True)

app = Flask(__name__)
Bootstrap(app)

app.secret_key = b'SecretKey'

@app.route("/")
def home():
    db.reconnect()
    sqlc = "SELECT * FROM posts ORDER BY post_date DESC LIMIT 3"
    cr.execute(sqlc)
    posts = cr.fetchall()
    db.reconnect()
    return render_template("index.html", posts = posts)


@app.route("/post")
def posted():
    db.reconnect()
    sqlc = "SELECT * FROM posts ORDER BY post_date DESC"
    cr.execute(sqlc)
    posts = cr.fetchall()
    db.reconnect()
    return render_template("post.html", posts = posts)


@app.route("/post/<url>")
def post(url):
    db.reconnect()
    sqlc = "SELECT * FROM posts WHERE posts.post_url='"+str(url)+"'"
    cr.execute(sqlc)
    post = cr.fetchall()
    db.reconnect()
    return render_template("content.html",url=url,post = post)


@app.route("/admin", methods=["GET","POST"])
def admin():
    db.reconnect()
    sqlc = "SELECT * FROM users WHERE user_id = 1"
    cr.execute(sqlc)
    pswrd = cr.fetchall()
    db.reconnect()
    error = ""
    if request.method == "POST":
        if request.form["username"] != pswrd[0]['user_name']:
            error = "Lütfen doğru giriş yapın"
        elif hashlib.md5(request.form["password"].encode()).hexdigest() != pswrd[0]['passwords']:
            error = "Lütfen doğru giriş yapın"
        else:
            session['username'] = request.form['username']
            return redirect(url_for("panel"))
    
    db.reconnect()
    return render_template("admin.html", error=error)


@app.route("/panel", methods=["GET","POST"])
def panel():
    db.reconnect()
    sqlc = "SELECT max(post_id) FROM posts"
    cr.execute(sqlc)
    postid = cr.fetchall()
    lastid = postid[0]["max(post_id)"]
    db.reconnect()
    sqld = "SELECT * FROM users WHERE user_id = 1"
    cr.execute(sqld)
    user = cr.fetchall()
    db.reconnect()
    if user[0]['user_name'] == session['username']:
        if request.method == "POST":
            insrt = "INSERT INTO `posts`(`post_id`, `post_title`, `post_url`, `post_preview`, `post_content`, `post_user_id`, `post_category_id`, `post_date`) VALUES (%s, %s, %s, %s, %s, %s, %s, 'current_timestamp()')"
            data = (request.form['post_id'], request.form['post_title'], request.form['post_url'], request.form['post_preview'], request.form['post_content'],
                    request.form['post_user_id'], request.form['post_category'])
            cr.execute(insrt,data)
            db.commit()
            db.reconnect()
        db.reconnect()
        return render_template("panel.html",lastid=lastid)
    else:
        db.reconnect()
        return render_template("not_found.html")   
    


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.errorhandler(404)
def not_found(error):
    db.reconnect()
    return render_template("not_found.html")


if __name__ == "__main__":
    db.reconnect()
    app.run(debug=True,port=5000)
    db.reconnect()

if True:
    db.reconnect()