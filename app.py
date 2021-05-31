import mysql.connector
import os
import hashlib
from flask import Flask, url_for, render_template, redirect, request, session
from flask_bootstrap import Bootstrap


## Connect to MySQL database
db = mysql.connector.connect(
    host = "hostname",
    user = "username",
    password = "password",
    database = "databasename"
)

## In my case I have conenction problem to heroku's clearDB so I reconnect to database in every chance :)
if True:
    db.reconnect()

## With dictionary=True statement I use database's data easily
cr = db.cursor(dictionary=True)

app = Flask(__name__)
Bootstrap(app)

## You should write your own secret key here you can use secrets.token.url_safe(16) or secrets.token_hex(16) 
## But you must have python 3.6 or more
app.secret_key = b'SecretKey'

@app.route("/")
def home():
    db.reconnect()
    sqlc = "SELECT * FROM posts ORDER BY post_date DESC LIMIT 3" ## With this query we take 3 latest post.
    cr.execute(sqlc)
    posts = cr.fetchall()
    db.reconnect()
    return render_template("index.html", posts = posts)


@app.route("/post")
def posted():
    db.reconnect()
    sqlc = "SELECT * FROM posts ORDER BY post_date DESC" ## With this query we take all posts latest to earliest
    cr.execute(sqlc)
    posts = cr.fetchall()
    db.reconnect()
    return render_template("post.html", posts = posts)


@app.route("/post/<url>")
def post(url):
    db.reconnect()
    ## I can use the %s method it's not that complicated so I left it simple.
    sqlc = "SELECT * FROM posts WHERE posts.post_url='"+str(url)+"'"    ## The query is for take the post that the user clicked with its url.
    cr.execute(sqlc)                                                    
    post = cr.fetchall()
    db.reconnect()
    return render_template("content.html",url=url,post = post)


@app.route("/admin", methods=["GET","POST"])
def admin():
    db.reconnect()
    ## I'm the only user so I make it for only me if I will change my mind it can be changed easily.
    sqlc = "SELECT * FROM users WHERE user_id = 1"   ## This query take the data of user that id's 1
    cr.execute(sqlc)
    pswrd = cr.fetchall()
    db.reconnect()
    
    ## I create a empty error string variable for change it later if there is an error case and then send it to page.
    error = ""
    if request.method == "POST":
        if request.form["username"] != pswrd[0]['user_name']:
            error = "Lütfen doğru giriş yapın"
            
        ## Password's hashed version is stored in the users table.
        elif hashlib.md5(request.form["password"].encode()).hexdigest() != pswrd[0]['passwords']:
            error = "Lütfen doğru giriş yapın"
        else:
            ## Start a session if everything is true and redirect the admin to content creation panel
            session['username'] = request.form['username']
            return redirect(url_for("panel"))
    
    db.reconnect()
    return render_template("admin.html", error=error)


@app.route("/panel", methods=["GET","POST"])
def panel():
    db.reconnect()
    sqlc = "SELECT max(post_id) FROM posts" ## This query take the last post's id for to be shown to admin.
    cr.execute(sqlc)
    postid = cr.fetchall()
    lastid = postid[0]["max(post_id)"]
    db.reconnect()
    sqld = "SELECT * FROM users WHERE user_id = 1"
    cr.execute(sqld)
    user = cr.fetchall()
    db.reconnect()
    
    ## Check the session and if everything is ok get the panel else get the not found error to user
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
    

## This part is for the changes in static files if this part will be removed changes will can not be seen.
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

## Reconnect issues again :) Have a good day !!
if True:
    db.reconnect()
