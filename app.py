from flask import Flask, request, render_template, redirect, url_for, make_response, session
from my_lib import database_worker, encrypt_password, check_password
import time
from datetime import datetime

app = Flask(__name__)


from flask import Flask, render_template, request

app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def scratch3():
#     return render_template('scratch3.html', num=0, button_color='grey')
#
# @app.route('/update', methods=['POST'])
# def update():
#     num = int(request.form['num'])
#     button_color = request.form['button_color']
#     if button_color == 'grey':
#         num += 1
#         button_color = 'blue'
#     else:
#         num -= 1
#         button_color = 'grey'
#     return render_template('scratch3.html', num=num, button_color=button_color)




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
        posts = db.search(f"SELECT * from posts")
        print(posts)
        db.close()
        return render_template('home.html', posts=posts)
        print("Website submitted")
    else:
        return redirect("/login")

@app.route('/update', methods=['POST'])
def update():
    if request.method=='POST':
        post_id = request.form['post_id']
        id = request.cookies.get('user_id')
        db = database_worker('woof.db')
        if request.form['submit'] == 'like':
            print('like button clicked')
            num = request.form['num']
            # CHECK IF USER ALREADY LIKED
            liked = db.search(f"SELECT * FROM likes where uid='{id}' AND post_id={post_id}")

            # IF USER ALREADY LIKED, UNLIKE THE POST BY DECREASING NUM VALUE & DELETING ROW IN LIKES
            if liked:
                db.run_save(f"UPDATE posts set likes=likes-1 where id={post_id}")
                db.run_save(f"DELETE from likes where uid='{id}' AND post_id={post_id}")
            elif not liked:
                db.run_save(f"UPDATE posts set likes=likes+1 where id={post_id}")
                db.run_save(f"INSERT INTO likes(post_id,uid) VALUES({post_id},'{id}')")

            # UPDATE HTML POSTS
            posts = db.search(f"SELECT * from posts")
            db.close()
            return render_template('home.html', posts=posts)
        elif request.form['submit']=='save':
            print('save button clicked.')
            posts = db.search(f"SELECT * from posts")

            # CHECK IF USER ALREADY SAVED
            saved = db.search(f"SELECT * FROM saves where uid='{id}' AND post_id={post_id}")
            if saved:
                db.run_save(f"DELETE from likes where uid='{id}' AND post_id={post_id}")
                print("User already saved this.")
            elif not saved:
                print("Saving now")
                db.run_save(f"INSERT INTO saves(post_id, uid) VALUES({post_id},'{id}')")
            db.close()
            return render_template('home.html', posts=posts)
    else:
        return render_template('/home')



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

@app.route("/saves", methods=['GET'])
def saves():
    print("Now in saves")
    id = request.cookies.get('user_id')
    if id:
        db = database_worker('woof.db')
        posts = db.search(f"SELECT * FROM SAVES WHERE uid='{id}'")
        db.close()
        return render_template('saves.html',posts=posts)
    else:
        return redirect('/home')

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
        new_post = f"INSERT into posts (uid,title, post, flair, date,likes) values ('{user_id}','{title}','{content}','{flair}','{str_date}',0)"
        db.run_save(new_post)
        db.close()
        return redirect('/home')
    return render_template('new_post.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    resp = make_response(render_template('login.html'))
    resp.set_cookie('user_id', "", expires=0)  # delete cookie
    return resp


if __name__ == '__main__':
    app.run()
