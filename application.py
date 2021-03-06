from flask import Flask, render_template,request #追加
from flask import Flask
from flask import Flask,flash,redirect,render_template,request,session,abort
import flask ,flask_login
from api.views.user import user_router
from flask import Blueprint, request, make_response, jsonify
from flask_bcrypt import Bcrypt
import json
import datetime
from api.__init__ import api_app
from config import SECRET_KET_FLASK
from code_def import calender_sort,search_class,hash_password
from sql import insert_user,getpassword,get_Taking_class,getuserlist,GetTodo,get_classname_from_index,COS5SQL,get_class_all,make_class


app = Flask(__name__)
bcrypt = Bcrypt() #ハッシュのやつ
#Login処理の試しを作ってみる
app.secret_key = SECRET_KET_FLASK

class User(flask_login.UserMixin):
    pass

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#SQL実装前の仮データベース
#password = password_data = bcrypt.generate_password_hash('password').decode('utf-8')
#users = {'example@com': {'password': password}} #パスワード

#password = "$2b$12$q.n/uI24z9zStg8tritvU.u4Vn6UkYkHDxwpz8Xt3OvMajIuvSBKi"
#users = {'example@com': {'password': password}} #パスワード (@tom:取っている授業情報を入れるべきかもしれない by kuri)

#classlist_user = ['class1','機械学習','情報論理学','go'] #本当はusersの中にSQLで格納してほしい(これを入れ込む感じリンク構造でもいい)


# 取っている授業のToDoリストの全ての一覧をデータ型としてプログラムに持ってくる
#ToDoList = '[{"id": "class1","date":"2020-8-13","info":"期末課題"},{"id": "情報論理学","date":"2020-8-16","info":"猿でもわかる"},{"id": "情報論理学","date":"2020-8-16","info":"猿でもわかるっていうけど誰がわかるねんって感じでめっちゃ怒っているなうなので、なんとかしてほしい。"},{"id": "機械学習","date":"2020-7-30","info":"未踏ジュニア"}]'
#ToDoList_json = json.loads(ToDoList) #Json読み込み
# 全体のクラスの一覧（検索とかで使う）


#classlist = '[{"class": "go","info":"期末課題"},{"class": "class1","info":"期末課題"},{"class": "情報論理学","info":"猿でもわかる"},{"class": "機械学習","info":"猿でもわかる"}]'
#classlist_json = json.loads(classlist) #Json読み込み


#----ここからページへのリンクの実装---------
global error_flag
error_flag = False
global users
users = getuserlist()
@login_manager.user_loader
def user_loader(email):
    if email not in users:
        print("idが違います") #ここでエラーが起きている（何だろう）
        return

    user = User()
    user.id = email
    return user
"""
@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user
"""
# ------------------------------------------------------------------
@app.route('/') #はじめに表示！！
def home():
   if not session.get('logged_in'): #ログインしていなかったら表示
       print("最初のログイン")
       error_flag = False
       return render_template('index.html')
   else:
        print("ログインなう")
        with COS5SQL() as cos5sql:
            classlist=cos5sql.get_Taking_class(database_user_index)
        #取っているクラスの情報を取得
        taking_class_index = get_Taking_class(database_user_index)
        #print("ユーザーindex",database_user_index)
        #print("取っているインデックス",taking_class_index)
        #インデックスからクラスのToDoを取得

        ToDoList_json = GetTodo(classlist) #データの取得をここで行なっている。
        print("履修している科目",ToDoList_json)
        #予定データのソート
        sort_cut_data = calender_sort(ToDoList_json) # ソートはcode_def.py内にて定義
        print("sort_cut_data",sort_cut_data)
        return render_template('home_ver2.html',id_name=database_user_id, ToDo = sort_cut_data,classlist_user = classlist)

# ------------------------------------------------------------------
@app.route('/login')
def showloginpage():
    if error_flag == True:
        message = "ユーザー名がすでに使われているかパスワードが違います"
    else:
        message = ""

    return render_template('login_ver2.html',error_message = message)

@app.route('/new')
def newuserpage():
    if error_flag == True:
        message = "ユーザー名がすでに使われているかパスワードが違います"
    else:
        message = ""
    return render_template('new.html',error_message = message)

@app.route('/newpost', methods=['POST']) #ここでユーザ登録のPOSTを行う # ユーザの登録をする。ポスト
def newuserpage_post():
    #id_name_join = flask.request.form['password']
    email_join = flask.request.form['email']
    password_1st = flask.request.form['password']
    #ハッシュ化する
    password_hash_1st = bcrypt.generate_password_hash(password_1st).decode('utf-8')
    password_2nd = flask.request.form['re-password']

    if password_1st != password_2nd:
        message ="パスワードが同じではありません"
        print("パスワードが同じではありません")
        return render_template('new.html',error_message = message)
    elif error_flag == True:
        message = "ユーザー名がすでに使われているかパスワードが違います"
        return render_template('new.html',error_message = message)
    else:
        try:
            insert_user(email_join,email_join,password_hash_1st) #ユーザ登録
            print("ユーザ登録の完了")
            message = "ユーザ登録の完了"
            print(email_join,email_join,password_hash_1st)
            #ここでもう一回ユーザ一覧を読み込まないといけない（めんど！！）
            users = getuserlist()
            return render_template('login_ver2.html',error_message = message)

        except:
            message ="エラーが発生しました。やり直してください"
            print("exceptでエラー")
            return render_template('new.html',error_message = message)


#database
@app.route('/loginpost', methods=['POST']) #ここでログインのPOSTを行う
def do_admin_login():
    id_name = flask.request.form['email'] #ユーザーネームの取り出し
    try:
        #ここでDBからパスワードとユーザー情報をゲットする！
        global database_user_index,database_user_id,database_hash_pass,database_user_email
        database_user_index, database_user_id,database_hash_pass,database_user_email = getpassword(id_name)

        if hash_password(flask.request.form['password'],database_hash_pass,bcrypt) == 1:
        #if flask.request.form['password'] == users[id_name]['password']:
            session['logged_in'] = True
            user = User()
            user.id = id_name
            flask_login.login_user(user)
            print("ログインしました。")
            error_flag = False
            #return home()
            return flask.redirect(flask.url_for('home'))
        else:
            flash('パスワードまたは、ユーザー名が違います。')
            error_flag=True
            return showloginpage()
    except:
        flash('パスワードまたは、ユーザー名が違います。')
        error_flag=True
        return showloginpage()

@app.route('/protected')
@flask_login.login_required #ログインが必要だよ
def protected():
    #print(flask_login.current_user.id)
    return render_template('home_ver2.html',id_name=flask_login.current_user.id,username = database_user_id)
    #return 'Logged in as: ' + flask_login.current_user.id

# -----個々のページの処理コード-----------------------------------------
# 授業検索のページ
@app.route('/register_class')
def register_class():
    with COS5SQL() as cos5sql:
        classlist = cos5sql.GetAllClasses()
    return render_template('register_class.html',classlist = classlist,username = database_user_id)

#サーチの時の機能を追加
@app.route('/searchtext', methods=['POST']) #ここでログインのPOSTを行う
@flask_login.login_required
def searching():
    with COS5SQL() as cos5sql:
        classlist = cos5sql.GetAllClasses()
    search_text = flask.request.form['searching'] #searchボックスの中身を取得
    #print(search_text)
    search_json = search_class(search_text,classlist) #code_def内の関数でサーチ機能を実装
    return render_template('register_class.html',classlist = search_json,username = database_user_id)


# classページの動的作成
@app.route('/class/<classname>')
@flask_login.login_required
def classpage(classname):
    isSearch = int(request.args.get('search')) if request.args.get('search') != None else 0
    classId = int(request.args.get('id'))
    with COS5SQL() as cos5sql:
        isTakeClass = cos5sql.IsTakeClass(database_user_index,classId)
        classInfo = cos5sql.GetClassInfo(classId)
        todos = cos5sql.GetTodoList(classId)
        ProblemSets = cos5sql.GetProblemSetInfo(classId)
    return render_template("class.html",classInfo = classInfo,Todos=todos,ProblemSets = ProblemSets,search=isSearch,classId = classId,isTake = isTakeClass,username = database_user_id)
@app.route('/class/<classname>/register')
@flask_login.login_required
def class_register(classname):
    classId = int(request.args.get('id'))
    with COS5SQL() as cos5sql:
        cos5sql.AddClass2User(database_user_index,classId)
    return flask.redirect(flask.url_for('classpage',classname=classname,username = database_user_id))

@app.route('/class/<classname>/release')
@flask_login.login_required
def class_release(classname):
    classId = int(request.args.get('id'))
    with COS5SQL() as cos5sql:
        cos5sql.RemoveClassFUser(database_user_index,classId)
    return flask.redirect(flask.url_for('home'))

# edit
@app.route('/edit_user_info')
@flask_login.login_required
def edit_user():
    return render_template("edit_user_info.html",username = database_user_id)

@app.route('/edit_user_info/passwordchange', methods=['POST']) #ここで、データベースの変更のポストを送る
@flask_login.login_required
def edit_userpassword():
    try:
        print("ここでデータベース操作")
        flash("パスワードの変更が完了しました。")
        return render_template("home.html",username = database_user_id)
    except:
        flash("エラーが発生しました。もう一度やり直してくだいさい")
        return render_template("class.html",username = database_user_id)



# 予定追加
@app.route('/add_event')
@flask_login.login_required
def add_event():
    #取っているクラスを一覧表示する

    with COS5SQL() as cos5sql:
        classlist=cos5sql.get_Taking_class(database_user_index)
    return render_template("register_schedule.html",classlist=classlist,username = database_user_id)


@app.route('/add_event_post', methods=['POST']) #ここで、データベースの変更のポストを送る
@flask_login.login_required
def add_event_post():
        classId = flask.request.form['select_class']
        print("class\n")
        name = flask.request.form['eventname']
        print("name\n")
        date = flask.request.form['eventdate']
        print("date\n")
        info = flask.request.form['eventinfo']
        print("eventinfo\n")
        with COS5SQL() as  cos5sql:
            cos5sql.ToDo_insert(classId,name,date,info)
        return render_template("feedback.html",username = database_user_id)


# making_class(クラスの作成)
@app.route('/make_class')
@flask_login.login_required
def make_class_page():
    #新しいクラスを作成する
    return render_template("make_class.html",username = database_user_id)


@app.route('/make_class_post', methods=['POST']) #ここで、データベースの変更のポストを送る
@flask_login.login_required
def make_class_post():
    make_class_name = flask.request.form['class_name'] #クラスネームの取り出し
    make_class_info = flask.request.form['class_info'] #クラスネームの取り出し
    make_class(make_class_name,make_class_info)
    return render_template("feedback.html",username = database_user_id)


#question
@app.route('/class/<classname>/register_question',methods=['GET'])
@flask_login.login_required
def register_question_get(classname):
    classId = int(request.args.get('id'))
    return render_template("register_question.html",class_name = classname,classId=classId,username = database_user_id)


@app.route('/class/<classname>/register_question_post',methods=['POST'])
@flask_login.login_required
def register_question_post(classname):
    setId = request.args.get('set')
    if(setId == None): flask.abort(400,'Invalid Request')
    classId = int(request.args.get('id'))
    name = flask.request.form['name']
    question = flask.request.form['question']
    selection = [flask.request.form['selection1'],flask.request.form['selection2'],flask.request.form['selection3'],flask.request.form['selection4']]
    answer = flask.request.form['answer']
    solution = flask.request.form['solution']
    with COS5SQL() as cos5sql:
        problemId = cos5sql.InsertProblem(classId,name,question,selection,answer,solution)
        cos5sql.AddProblem2Set(setId,problemId)
    return flask.redirect(flask.url_for('classpage',classname=classname,id=classId,username = database_user_id))


@app.route('/class/<classname>/edit_question',methods=['GET'])
@flask_login.login_required
def edit_question(classname):
    setId = request.args.get('set')
    problemId = request.args.get('id')
    classId = int(request.args.get('cid'))
    if(setId == None or problemId ==None): flask.abort(400,'Invalid Request')
    with COS5SQL() as cos5sql:
        problem = cos5sql.GetProblem(problemId)
    return flask.render_template('edit_question.html',classname=classname,setId=setId,problem=problem,classId=classId,username = database_user_id)
  
@app.route('/class/<classname>/edit_question_post',methods=['POST'])
@flask_login.login_required
def edit_question_post(classname):
    setId = request.args.get('set')
    problemId = request.args.get('id')
    classId = int(request.args.get('cid'))
    if(setId == None or problemId ==None): flask.abort(400,'Invalid Request')
    name = flask.request.form['name']
    question = flask.request.form['question']
    selection = [flask.request.form['choice1'],flask.request.form['choice2'],flask.request.form['choice3'],flask.request.form['choice4']]
    answer = flask.request.form['answer']
    solution = flask.request.form['solution']
    with COS5SQL() as cos5sql:
        cos5sql.UpdateProblem(classId,problemId,name,question,selection,answer,solution)
    return flask.redirect(flask.url_for('question_list',classname=classname,set=setId,id=classId,username = database_user_id))
  
@app.route('/class/<classname>/delete_question',methods=['GET'])
@flask_login.login_required
def delete_question(classname):
    setId = request.args.get('set')
    problemId = request.args.get('id')
    classId = int(request.args.get('cid'))
    if(setId == None or problemId ==None): flask.abort(400,'Invalid Request')
    with COS5SQL() as cos5sql:
        cos5sql.RemoveProblemFSet(setId,problemId)
        cos5sql.DeleteProblem(problemId)
    return flask.redirect(flask.url_for('question_list',classname=classname,set=setId,id=classId,username = database_user_id))


@app.route('/class/<classname>/question_list',methods=['GET'])
@flask_login.login_required
def question_list(classname):
    setId = request.args.get('set')
    classId = int(request.args.get('id'))
    if(setId == None): flask.abort(400,'Invalid Request')
    with COS5SQL() as cos5sql:
        setTitle = cos5sql.GetProblemSetInfoByID(setId)[1]
        ProblemSet = cos5sql.GetProblemSet(setId)
    return render_template("question_list.html",classname=classname,setId = setId,setTitle = setTitle,ProblemSet=ProblemSet,classId=classId,username = database_user_id)



@app.route('/class/<classname>/question',methods=['GET'])
@flask_login.login_required
def question_get(classname):
    setId = request.args.get('set')
    n = int(request.args.get('n')) if request.args.get('n') != None else 1
    classId = int(request.args.get('id'))
    if(setId == None): flask.abort(400,'Invalid Request')
    with COS5SQL() as cos5sql:
        ProblemSet = cos5sql.GetProblemSet(setId)
    Problem = ProblemSet[n-1]
    if(n == None):

        return render_template("question.html",classname=classname,setId = setId,Problem=Problem,n=1,max=len(ProblemSet),classId=classId,username = database_user_id)
    elif(n != None):
        return render_template("question.html",classname=classname,setId = setId,Problem=Problem,n=n,max=len(ProblemSet),classId=classId,username = database_user_id)
@app.route('/class/<classname>/makeSet',methods=['POST'])
@flask_login.login_required
def make_problemSet(classname):
    SetName = flask.request.form['SetName']
    classId = int(request.args.get('id'))
    with COS5SQL() as cos5sql:
        setId = cos5sql.AddProblemSet(SetName,"")
        cos5sql.AddProblemSet2Class(classId,setId)
    return flask.redirect(flask.url_for('classpage',classname=classname,id=classId,username = database_user_id))

# ------------------------------------------------------------------
@app.route("/logout")
@flask_login.login_required
def logout():
   session['logged_in'] = False
   flask_login.logout_user()
   #print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
   return home()

# ------------------------------------------------------------------
@app.route('/api', methods=['GET'])
@flask_login.login_required
def doc():
    return "<H1>ここにドキュメント</H1>"

@app.route('/api/users', methods=['GET'])
def get_user_list():
  return make_response(jsonify({ #この値を返す予定
    'users': [
       {
         'id': 1,
         'name': 'John'
       }
     ]
  }))

## おまじない
if __name__ == "__main__":
    app.run(debug=True,threaded=True)
