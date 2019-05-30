from flask import Flask
from flask import render_template, request, url_for, redirect
from session_manager import User
import database_interface

# creates a Flask application, named app
app = Flask(__name__)

current_user = User()

# global variable
database = 'tischtenniz'
conn = database_interface.create_connection(database)


@app.route("/")
def default():
    with_current_user = True
    logged_in_user_name = current_user.__getattribute__('usr_name')

    if len(logged_in_user_name) == 0:
        logged_in_user_name = 'no one'

    all_users = database_interface.get_all_users_and_elo(conn, logged_in_user_name)
    idx = range(len(all_users))
    request.args.get('page')

    return render_template('index.html', all_users=all_users,
                           logged_in_user_nickname=logged_in_user_name,
                           idx=idx)


@app.route("/my_game_history")
def my_game_history():

    if current_user.__getattribute__('usr_name'):
        user_id = database_interface.get_id_usr_from_player_name(conn,
                                                                 current_user.__getattribute__('usr_name'))
        game_history_list = database_interface.display_user_game_history(conn, user_id)

        return render_template('my_game_history.html', game_history_list=game_history_list,
                               logged_in_user_nickname=current_user.__getattribute__('usr_name'))
    else:
        print('log in you nobody')
        return login_page()


@app.route('/logout')
def logout():
    current_user.__logout__()
    return default()


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/login_database', methods=['POST'])
def login():
    password = request.form['password']
    nickname = request.form['nickname']

    current_user.__login__(conn, nickname, password)
    return default()


@app.route("/enter_score", methods=['GET'])
def enter_score():
    if current_user.__getattribute__('usr_name'):
        user_won = (request.args.get('user_won') == 'on')
        opponent_player_name = request.args.get('opponent')
        user_id = database_interface.get_id_usr_from_player_name(conn,
                                                                 current_user.__getattribute__('usr_name'))

        # write to database
        database_interface.game_result_input(conn, user_id,
                                             opponent_player_name, user_won)
        return default()
    else:
        return login_page()


@app.route("/create_account")
def create_account():
    return render_template('create_account.html')


@app.route("/new_user", methods=['POST'])
def new_user():
    # TO DO: secure password transfer and defensive mechanism when password entered (matching )
    new_email = request.form['Email']
    new_nickname = request.form['nickname']
    new_password = request.form['password']
    confirm_password = request.form['confirm_password']

    if new_nickname and new_email and new_password and confirm_password and confirm_password == new_password:
        database_interface.add_new_user(conn, new_nickname, new_password)
    else:
        print('missing parameter or both password do not match')
    return default()


@app.route("/enter_game")
def enter_game():
    logged_in_user_name = current_user.__getattribute__('usr_name')
    if logged_in_user_name:
        with_current_user = False
        existing_user = database_interface.get_all_users_alph_order(conn, logged_in_user_name)
        return render_template('enter_game.html', existing_user=existing_user,
                               logged_in_user_nickname=logged_in_user_name)
    else:
        return login_page()


# run the application
if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host='0.0.0.0')
