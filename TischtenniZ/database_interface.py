import datetime
import mysql.connector
from mysql.connector import Error
import elo


class Player(object):
    def __init__(self, rank, name, elo_rank):
        self.rank = rank
        self.name = name
        self.elo = elo_rank


class game_history(object):
    def __init__(self, opponent, score, elo_rank, date):
        self.opponent = opponent
        self.score = score
        self.elo = elo_rank
        self.date = date


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = mysql.connector.connect(user='root', database=db_file, password='easy')
        if conn.is_connected():
            print('Connected to MySQL database')
        return conn

    except Error as e:
        print(e)

    return None


def add_new_user(conn, userNameIn, passwordIn):
    cur = conn.cursor()

    # check if user name is not taken
    cur.execute("SELECT player_name FROM users \
                WHERE player_name='%s'" % userNameIn)
    is_user_name_already_in_db = cur.fetchone()
    if is_user_name_already_in_db:
        print('User name: ', userNameIn, 'already existing, select another one')
    else:
        try:
            cur.execute("INSERT INTO users \
                SET player_name='%s', password='%s'" % (userNameIn, passwordIn))
            conn.commit()
        except Error as error:
            print(error)


def display_user_list(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    print('Total Row(s):', cursor.rowcount)
    for row in rows:
        print(row)


def update_elo(conn, user_id, opponent_name, did_the_user_win):
    cursor = conn.cursor()
    cursor.execute("SELECT elo FROM users WHERE \
                    player_name = '%s'" % opponent_name)
    opponent_elo = cursor.fetchone()
    cursor.execute("SELECT elo FROM users WHERE \
                    id_usr = '%d'" % user_id)
    user_elo = cursor.fetchone()

    expected_score = elo.expected(int(user_elo[0]), int(opponent_elo[0]))

    if did_the_user_win == 1:
        score = 1
        score_opponent = 0
    else:
        score = 0
        score_opponent = 1

    # update user elo
    updated_user_elo = round(elo.elo(int(user_elo[0]), expected_score, score, k=32))
    # update opponent elo, his expected score is 1 - expected_score
    updated_opponent_elo = round(elo.elo(int(opponent_elo[0]), 1 - expected_score, score_opponent, k=32))

    return updated_user_elo, updated_opponent_elo


def game_result_input(conn, user_id, opponent_name, did_the_user_win):
    cursor = conn.cursor()

    # update elo of the user and opponent
    updated_elo = update_elo(conn, user_id, opponent_name, did_the_user_win)

    if did_the_user_win == 1:
        score = 'W'
        score_opponent = 'L'
    else:
        score = 'L'
        score_opponent = 'W'

    now = datetime.datetime.now()
    # Add a row in user game_history
    cursor.execute("INSERT INTO game_history \
                SET opponent='%s', id_usr='%d', score='%s', elo='%d', date='%s'"
                   % (opponent_name, user_id, score, updated_elo[0], now))
    # update user profile
    cursor.execute("Update users \
                    SET elo='%d' WHERE id_usr='%d'"
                   % (updated_elo[0], user_id))

    # Add a row in opponent game_history
    cursor.execute("INSERT INTO game_history \
                SET opponent='%s', id_usr='%d', score='%s', elo='%d', date='%s'"
                   % (get_player_name_from_usr_id(conn, user_id), get_id_usr_from_player_name(conn, opponent_name),
                      score_opponent, updated_elo[1], now))
    # update elo of the opponent
    cursor.execute("Update users \
                    SET elo='%d' WHERE player_name='%s'"
                   % (updated_elo[1], opponent_name))
    conn.commit()


def display_user_game_history(conn, user_id):
    cursor = conn.cursor()

    cursor.execute("SELECT opponent FROM game_history WHERE id_usr='%d' ORDER by date DESC"
                   % user_id)
    opponent = cursor.fetchall()
    cursor.execute("SELECT score FROM game_history WHERE id_usr='%d' ORDER by date DESC"
                   % user_id)
    score = cursor.fetchall()
    cursor.execute("SELECT elo FROM game_history WHERE id_usr='%d' ORDER by date DESC"
                   % user_id)
    elo_rank = cursor.fetchall()
    cursor.execute("SELECT date FROM game_history WHERE id_usr='%d' ORDER by date DESC"
                   % user_id)
    date = cursor.fetchall()

    cursor.execute("SELECT COUNT(id) FROM game_history WHERE id_usr='%d'" % user_id)
    number_of_game = cursor.fetchone()[0]

    game_history_list = []
    for idx_game in range(number_of_game):
        game_history_list.append(game_history(opponent[idx_game][0], score[idx_game][0],
                                              elo_rank[idx_game][0], date[idx_game][0]))
    return game_history_list


def get_player_name_from_usr_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT player_name FROM users WHERE id_usr='%d'"
                   % user_id)
    user_name = cursor.fetchone()
    return user_name[0]


def get_id_usr_from_player_name(conn, player_name):
    cursor = conn.cursor()
    cursor.execute("SELECT id_usr FROM users WHERE player_name ='%s'"
                   % player_name)
    opponent_id_usr = cursor.fetchone()
    return opponent_id_usr[0]


def get_all_users_and_elo(conn, logged_in_user_name):

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(player_name) from users")
    number_of_users = cursor.fetchone()[0]

    cursor.execute("SELECT player_name FROM users ORDER BY elo DESC")
    Player_name = cursor.fetchall()
    cursor.execute("SELECT elo FROM users ORDER BY elo DESC")
    Player_elo = cursor.fetchall()


    Player_list = []
    for nb_users in range(number_of_users):
        Player_list.append(Player(nb_users+1, Player_name[nb_users][0], Player_elo[nb_users][0]))

    return Player_list


def get_all_users_alph_order(conn, logged_in_user_name):

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(player_name) from users \
                    WHERE player_name not like '%s'" % logged_in_user_name)
    number_of_users = cursor.fetchone()[0]

    cursor.execute("select player_name from users WHERE\
                     player_name NOT LIKE '%s' ORDER BY player_name ASC" % logged_in_user_name)
    Player_name = cursor.fetchall()
    cursor.execute("select player_name from users WHERE\
                     player_name NOT LIKE '%s' ORDER BY player_name ASC" % logged_in_user_name)
    Player_elo = cursor.fetchall()


    Player_list = []
    for nb_users in range(number_of_users):
        Player_list.append(Player(nb_users + 1, Player_name[nb_users][0], Player_elo[nb_users][0]))

    return Player_list


def main():
    database = 'tischtenniz'

    testNewUser = 'Shinji'
    testNewPass = 'iLoveCheeseNaN'
    testNewUser1 = 'a'
    testNewPass1 = 'iLoveCheeseNaN'
    opponent_name = 'Shinji'
    did_the_user_win = 1
    user_id = 1

    # create a database connection
    conn = create_connection(database)
    Player_list = get_all_users(conn)
    display_user_game_history(conn, 12)
    return Player_list
    '''
    # input a new user
    add_new_user(conn, testNewUser, testNewPass)
    add_new_user(conn, testNewUser1, testNewPass1)

    # display full user list
    display_user_list(conn)

    ############################ ENTER GAME SCORE SECTION ###############################

    # input a new game resut
    game_result_input(conn, user_id, opponent_name, did_the_user_win)

    # display user history
    display_user_game_history(conn, user_id)
'''


if __name__ == '__main__':
    main()
