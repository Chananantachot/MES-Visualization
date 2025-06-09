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
    def getCurrentUsers():
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, fullname, email, active, created_at, updated_at FROM users')
         
        return cursor.fetchall()

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
        cursor.execute('''SELECT id,fullname,email,password,salt 
                        FROM users 
                        WHERE email = ?
                        AND active = 1''',(email,))
        user = cursor.fetchone()
        roles = authDb.getUserRoles(user['id'])
        
        user = dict(user)
        _roles = [dict(r) for r in roles]
        user['roles'] = [r['roleName'] for r in _roles]
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
    def UpdateUser(userId,fullname,email,active):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE users SET 
                            fullname = ?,
                            email = ?, 
                            active = ?
                            WHERE id = ?'''
                            , (fullname,email,active,userId,))
        db.commit()
        return True

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
    def getAssignedUserRoles(roleId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute(f''' 
                       SELECT u.id, u.fullname, u.email,
                            CASE WHEN ur.roleId IS NOT NULL THEN 1 ELSE 0 END AS assigned
                        FROM users u
                        LEFT JOIN userInRoles ur ON u.id = ur.userId AND u.active = 1 AND ur.roleId = ?
                        ''', (roleId,))
        roles = cursor.fetchall()
        return roles

    @staticmethod
    def getUserRoles(userId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute(f''' 
                        SELECT r.id,r.roleName 
                        FROM roles r
                        JOIN userInRoles ur ON r.id = ur.roleId
                        WHERE (ur.userId = ?)
                        AND r.active = 1
                        ''', (userId,))
        roles = cursor.fetchall()
        return roles
    
    @staticmethod
    def getRoles(id = None):
        db = authDb.get_db()
        cursor = db.cursor()
        if id:
            cursor.execute(f''' SELECT id,roleName,
                            description,active,
                            created_at,updated_at
                            FROM roles 
                            WHERE id = ?
                        ''', (id,))
            roles = cursor.fetchone()
        else:    
            cursor.execute(f''' SELECT id,roleName,
                                description,active,
                                created_at,updated_at
                                FROM roles 
                            ''')
            roles = cursor.fetchall()
        return roles

    @staticmethod
    def createRole(roleName,description,active):
        db = authDb.get_db()
        cursor = db.cursor()
        id = str(uuid.uuid4())
        cursor.execute('INSERT INTO roles (id,roleName,description,active) VALUES (?,?,?,?)', (id,roleName,description,active,))
        db.commit()
        return id
    
    @staticmethod
    def UpdateRole(id,roleName,description,active):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('''UPDATE users SET 
                            roleName = ?,
                            description = ?, 
                            active = ?
                            WHERE id = ?'''
                            , (roleName,description,active,id,))
        db.commit()
        return True
    
    @staticmethod
    def addUserInRoles(roleId,userId):
        _id = str(uuid.uuid4())
        db = authDb.get_db()
        cursor = db.cursor()
        
        cursor.execute('INSERT INTO userInRoles (id, roleId, userId) VALUES (?,?,?)', (_id,roleId,userId,))
        db.commit()
        return True

    @staticmethod
    def deleteUserRoles(roleid, userId):
        db = authDb.get_db()
        cursor = db.cursor()
        cursor.execute('DELETE FROM userInRoles WHERE roleId = ? AND userId = ?', (roleid,userId,))
        db.commit()
        return True