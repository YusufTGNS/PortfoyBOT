import sqlite3
from config import DATABASE

# Örnek beceriler ve durumlar
skills = [ (_,) for _ in (['Python', 'SQL', 'API', 'Discord'])]
statuses = [ (_,) for _ in (['Prototip Oluşturma', 'Geliştirme Aşamasında', 'Tamamlandı, kullanıma hazır', 'Güncellendi', 'Tamamlandı, ancak bakımı yapılmadı'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS projects (
                            project_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            project_name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(status_id),
                            UNIQUE(user_id, project_name)  -- Aynı kullanıcı için aynı proje adı tekrar eklenemez
                        )''') 
            conn.execute('''CREATE TABLE IF NOT EXISTS skills (
                            skill_id INTEGER PRIMARY KEY,
                            skill_name TEXT UNIQUE  -- Beceri adı benzersiz olmalı
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skills (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES projects(project_id),
                            FOREIGN KEY(skill_id) REFERENCES skills(skill_id),
                            UNIQUE(project_id, skill_id)  -- Aynı projeye aynı beceri tekrar eklenemez
                        )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS status (
                            status_id INTEGER PRIMARY KEY,
                            status_name TEXT UNIQUE  -- Durum adı benzersiz olmalı
                        )''')
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def is_table_empty(self, table_name):
        """Belirtilen tablonun boş olup olmadığını kontrol eder."""
        sql = f"SELECT COUNT(*) FROM {table_name}"
        result = self.__select_data(sql)
        return result[0][0] == 0  # Eğer tablo boşsa True döner

    def default_insert(self):
        """Varsayılan becerileri ve durumları ekler (sadece tablo boşsa)."""
        if self.is_table_empty("skills"):
            sql = 'INSERT OR IGNORE INTO skills (skill_name) VALUES (?)'
            self.__executemany(sql, skills)
        
        if self.is_table_empty("status"):
            sql = 'INSERT OR IGNORE INTO status (status_name) VALUES (?)'
            self.__executemany(sql, statuses)

    def insert_project(self, data):
        """Yeni proje ekler."""
        sql = """INSERT OR IGNORE INTO projects 
                  (user_id, project_name, description, url, status_id) 
                  VALUES (?, ?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        """Projeye yeni beceri ekler."""
        # Proje ID'sini al
        sql = 'SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?'
        result = self.__select_data(sql, (project_name, user_id))
        
        if not result:
            print(f"Proje {project_name} bulunamadı veya kullanıcıya ait değil.")
            return  # Eğer proje yoksa, beceri eklemeyi yapma.
        
        project_id = result[0][0]
        
        # Beceri ID'sini al
        sql = 'SELECT skill_id FROM skills WHERE skill_name = ?'
        skill_result = self.__select_data(sql, (skill,))
        if not skill_result:
            print(f"Beceri {skill} bulunamadı.")
            return  # Eğer beceri yoksa, beceri eklemeyi yapma.
        
        skill_id = skill_result[0][0]
        
        # Beceri ve proje ilişkisini ekle
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skills VALUES(?, ?)'
        self.__executemany(sql, data)

    def get_statuses(self):
        """Tüm durumları getirir."""
        sql = "SELECT status_name FROM status"
        return self.__select_data(sql)
        
    def get_status_id(self, status_name):
        """Belirtilen durum adının ID'sini getirir."""
        sql = 'SELECT status_id FROM status WHERE status_name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        """Belirtilen kullanıcının tüm projelerini getirir."""
        sql = "SELECT * FROM projects WHERE user_id = ?"
        return self.__select_data(sql, data=(user_id,))
        
    def get_project_id(self, project_name, user_id):
        """Belirtilen proje adı ve kullanıcı ID'sine göre proje ID'sini getirir."""
        return self.__select_data(sql='SELECT project_id FROM projects WHERE project_name = ? AND user_id = ?', data=(project_name, user_id,))[0][0]
        
    def get_skills(self):
        """Tüm becerileri getirir."""
        return self.__select_data(sql='SELECT * FROM skills')
    
    def get_project_skills(self, project_name):
        """Belirtilen projenin becerilerini getirir."""
        res = self.__select_data(sql='''SELECT skill_name FROM projects 
                                        JOIN project_skills ON projects.project_id = project_skills.project_id 
                                        JOIN skills ON skills.skill_id = project_skills.skill_id 
                                        WHERE project_name = ?''', data=(project_name,))
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        """Belirtilen projenin detaylarını getirir."""
        sql = """
        SELECT project_name, description, url, status_name 
        FROM projects 
        JOIN status ON status.status_id = projects.status_id
        WHERE project_name = ? AND user_id = ?
        """
        return self.__select_data(sql=sql, data=(project_name, user_id))

    def update_projects(self, param, data):
        """Proje bilgilerini günceller."""
        sql = f"""UPDATE projects SET {param} = ? 
                  WHERE project_name = ? AND user_id = ?"""
        self.__executemany(sql, [data])

    def delete_project(self, user_id, project_id):
        """Projeyi siler."""
        sql = """DELETE FROM projects 
                  WHERE user_id = ? AND project_id = ? """
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        """Projeden beceriyi siler."""
        sql = """DELETE FROM project_skills 
                  WHERE project_id = ? AND skill_id = ? """
        self.__executemany(sql, [(project_id, skill_id)])


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()  
    
    # Varsayılan verileri ekle (sadece tablolar boşsa)
    manager.default_insert()
    
    # Örnek proje ekleme
    data = [
        (1, "Portföy", "BETA", "https://github.com/YusufTGNS/PortfoyBOT", 1),
        (2, "Proje B", "Başka bir açıklama", "https://ornek2.com", 2)
    ]
    manager.insert_project(data)
    
    # Projeye beceri ekleme
    manager.insert_skill(1, "Portföy", "Python")
    manager.insert_skill(1, "Portföy", "SQL")
    
    # Proje bilgilerini getirme
    print(manager.get_project_info(1, "Portföy"))
