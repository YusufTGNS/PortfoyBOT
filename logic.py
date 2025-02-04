import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database  

    def create_tables(self):
        baglanti = sqlite3.connect(self.database)
        with baglanti:
            cursor = baglanti.cursor()  
            
            # users tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            ''')

            # status tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS status (
                status_id INTEGER PRIMARY KEY AUTOINCREMENT,
                status_name TEXT NOT NULL
            )
            ''')

            # projects tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_name TEXT NOT NULL,
                description TEXT,
                url TEXT,
                status_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
                FOREIGN KEY (status_id) REFERENCES status (status_id)
            )
            ''')

            # skills tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS skills (
                skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL
            )
            ''')

            # project_skills tablosu
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_skills (
                project_id INTEGER,
                skill_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills (skill_id),
                PRIMARY KEY (project_id, skill_id)
            )
            ''')

        baglanti.commit()


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()