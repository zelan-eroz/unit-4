from flask import Flask, request, render_template, redirect, url_for, make_response
from my_lib import database_worker, encrypt_password, check_password
import time
from datetime import datetime

app = Flask(__name__)

@app.route('/signup', methods=['GET','POST'])
def signup():
    message=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        message = f"sent to server"
        print(username, password,email)
        db = database_worker('woof.db')
        existing_user = db.search(f"SELECT * from users where email = '{email}' or username='{username}'")
        print(existing_user)
        if existing_user:
            #check existing email
            if email == existing_user[0][1]:
                message = "User with that email already exists. Try again."
            elif username == existing_user[0][2]:
                message = "User with that username already exists. Try again."
            elif email== existing_user[0][1] and username==existing_user[0][2]:
                message = "User with that username & email already exists. Perhaps log in instead?"
        else:
            new_user = f"INSERT into users (email,username, password) values ('{email}','{username}','{encrypt_password(password)}')"
            db.run_save(new_user)
            db.close()
            print("Successful")
            return redirect("/home")
    else:
        return render_template("signup.html", message=message)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        uname = request.form['uname']
        password = request.form['password']
        db=database_worker("woof.db")
        existing_user = db.search(f"SELECT * from users where username='{uname}' or email='{uname}'")
        print(check_password(password,existing_user[0][3]))
        if existing_user:
            if check_password(password, existing_user[0][3]):
                print("Successfully logged in.")
                #resp = make_response(render_template('profile.html'))
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('user_id',f'{existing_user[0][2]}')
                print('Password is correct')
                return resp
            else:
                error = "Incorrect password. Try again."
                print(error)
                return render_template('login.html', error=error)
        else:
            print("User does not exist. Try again.")
        db.close()
    else:
        return render_template("login.html")

@app.route('/terms')
def terms():
    return render_template("terms.html")

@app.route('/home', methods=['GET','POST'])
def home():
    print("Now in home")
    id=request.cookies.get('user_id')
    print("id: ",id)
    if id:
        db = database_worker('woof.db')
        print("Home database open")
        uname = db.search(f"SELECT * from users where username='{id}'")
        print("uname open")
        uname = uname[0][2]
        print(uname)
        posts = db.search(f"SELECT * from posts")
        print(posts)
        db.close()
        return render_template('home.html', posts=posts)
    else:
        return redirect("/login")

@app.route("/profile", methods=['GET','POST'])
def profile2():
    print("Now in profile")
    id = request.cookies.get('user_id')
    print("id: ", id)
    if id:
        db = database_worker('woof.db')
        print("Home database open")
        posts = db.search(f"SELECT * from posts where uid='{id}'")
        print(posts)
        db.close()
        return render_template('profile.html', posts=posts)
    else:
        return redirect("/home")

@app.route("/profile/<user_id>", methods=['GET','POST'])
def profile(user_id:int):
    user_id = request.cookies.get('user_id')
    if user_id:
        db=database_worker('woof.db')
        username=db.search(f"SELECT * from users where username='{user_id}'")
        username=username[0][2]
        db.close()
        return render_template('profile.html',name=username)
    else:
        return redirect(url_for(login))


@app.route('/new_post', methods=['GET','POST'])
def post():
    if request.method=='POST':
        title = request.form['title']
        content = request.form['content']
        flair=request.form['options']
        date_time = datetime.fromtimestamp(time.time())
        str_date = date_time.strftime("%b %d, %Y")
        print(title, content,flair, str_date)
        if request.cookies.get('user_id'):
            print("The cookie was found in creating posts")
            user_id=request.cookies.get('user_id')
            print('cookie requested, ', user_id)
        #DO SOMETHING WITH THE POSTS
        db = database_worker("woof.db")
        new_post = f"INSERT into posts (uid,title, post, flair, date) values ('{user_id}','{title}','{content}','{flair}','{str_date}')"
        db.run_save(new_post)
        db.close()
        return redirect('/home')
    return render_template('new_post.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    resp = make_response(render_template('login.html'))
    resp.set_cookie('user_id', "", expires=0) #delete cookie
    return render_template('login.html')
if __name__ == '__main__':
    app.run()
