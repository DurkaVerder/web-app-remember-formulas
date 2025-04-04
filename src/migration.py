from sqlite3 import connect

def migrate_database():
    conn = connect('instance/db_sqlite.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE tests ADD COLUMN start_time DATETIME')
    except Exception as e:
        print("Поле start_time уже существует, пропускаем")
    

    cursor.execute('UPDATE tests SET start_time = CURRENT_TIMESTAMP WHERE start_time IS NULL')
    
 
    try:
        cursor.execute('ALTER TABLE tests ADD COLUMN end_time DATETIME')
    except Exception as e:
        print("Поле end_time уже существует, пропускаем")
    

    cursor.execute('UPDATE tests SET end_time = CURRENT_TIMESTAMP WHERE end_time IS NULL')

    try:
        cursor.execute('ALTER TABLE achievements ADD COLUMN image_path VARCHAR(255)')
    except Exception as e:
        print("Поле image_path уже существует, пропускаем")
   
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_name VARCHAR(255) NOT NULL,
            achievement_description TEXT NOT NULL,
            date_achieved DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()