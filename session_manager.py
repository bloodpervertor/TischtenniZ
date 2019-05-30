class User(object):
    def __init__(self):
        self.usr_name = []
        # user or admin
        self.type = []

    def get_user(self):
        return self.usr_name

    def __login__(self, conn, usr_name, password):
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM users WHERE player_name ='%s'"
                           % usr_name)
            if cursor.fetchone()[0] == password:
                print('Welcome home', usr_name)
                self.usr_name = usr_name
                self.type = 'user'
            else:
                print('Non existing user or password incorrect')
        except:
            print('Non existing user or password incorrect')

    def __logout__(self):
        self.usr_name = []
        self.type = []


