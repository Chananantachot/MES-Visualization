import sqlite3
import uuid

from flask import g

class authDb:
    DATABASE = "auth.db"

    @staticmethod
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(authDb.DATABASE)
            db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def init_db():
        db = authDb.get_db()
        _cursor = db.cursor()

        # Create users tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                fullname TEXT NOT NULL,        
                email TEXT NOT NULL,
                salt TEXT NOT NULL,
                password TEXT NOT NULL,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP            
            )
        ''')

        # Create roles tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                roleName TEXT NOT NULL,        
                description TEXT,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              
            )
        ''')
        
        # Create userInRoles tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS userInRoles (
                id TEXT PRIMARY KEY,        
                userId TEXT NOT NULL,
                roleId TEXT NOT NULL          
            )
        ''')

        # Create menus tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS menus (
                id TEXT PRIMARY KEY,        
                menu TEXT NOT NULL,
                active INTEGER DEFAULT 1, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            )
        ''')

        # Create menuInRoles tables 
        _cursor.execute('''
            CREATE TABLE IF NOT EXISTS menuInRoles (
                id TEXT PRIMARY KEY,        
                menuId TEXT NOT NULL,
                roleId TEXT NOT NULL        
            )
        ''')

        db.commit()

    @staticmethod
    def getCurrentUser(id):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT fullname, email FROM users WHERE id = ?', (id,))
        return cursor.fetchone()

    @staticmethod
    def getCurrentActiveUser(email):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('''SELECT fullname,email,password,salt 
                        FROM users 
                        WHERE email = ?
                        AND active = 1''',(email,))
        user = cursor.fetchone()
        return user

    @staticmethod
    def createUser(fullname,email,salt,password):
        db = authDb.get_db()
        cursor = db.cursor()
        userid = str(uuid.uuid4())
        cursor.execute('INSERT INTO users (id,fullname,email,salt,password) VALUES (?,?,?,?,?)', (userid,fullname,email,salt,password,))
        db.commit()
        return userid

    @staticmethod
    def activeUser(userId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET active = 1 WHERE id = ?', (userId,))
        db.commit()
        return True

    @staticmethod
    def inactiveUser(userId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE users SET active = 0 WHERE id = ?', (userId,))
        db.commit()
        return True

    @staticmethod
    def getUserRoles(userId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute(f''' 
                        SELECT roleId,roleName 
                        FROM userInRoles 
                        WHERE (userId = "{userId}" AND {userId} is not null)
                        AND active = 1
                        ''')
        roles = cursor.fetchall()
        return roles
