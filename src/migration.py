from sqlite3 import connect
from logger import log_info, log_error, log_debug 

def migrate_database():
    try:
        conn = connect('instance/db_sqlite.db')
        cursor = conn.cursor()
        log_info("Successfully connected to SQLite database 'instance/db_sqlite.db'")
    except Exception as e:
        log_error(f"Failed to connect to SQLite database: {str(e)}")
        return

    try:
        cursor.execute('ALTER TABLE tests ADD COLUMN start_time DATETIME')
        log_info("Added column 'start_time' to 'tests' table")
    except Exception as e:
        log_info(f"Column 'start_time' already exists in 'tests' table, skipping: {str(e)}")

    try:
        cursor.execute('UPDATE tests SET start_time = CURRENT_TIMESTAMP WHERE start_time IS NULL')
        log_info("Updated 'start_time' with CURRENT_TIMESTAMP where NULL")
    except Exception as e:
        log_error(f"Failed to update 'start_time' in 'tests' table: {str(e)}")

    try:
        cursor.execute('ALTER TABLE tests ADD COLUMN end_time DATETIME')
        log_info("Added column 'end_time' to 'tests' table")
    except Exception as e:
        log_info(f"Column 'end_time' already exists in 'tests' table, skipping: {str(e)}")

    try:
        cursor.execute('UPDATE tests SET end_time = CURRENT_TIMESTAMP WHERE end_time IS NULL')
        log_info("Updated 'end_time' with CURRENT_TIMESTAMP where NULL")
    except Exception as e:
        log_error(f"Failed to update 'end_time' in 'tests' table: {str(e)}")

    try:
        cursor.execute('ALTER TABLE achievements ADD COLUMN image_path VARCHAR(255)')
        log_info("Added column 'image_path' to 'achievements' table")
    except Exception as e:
        log_info(f"Column 'image_path' already exists in 'achievements' table, skipping: {str(e)}")

    try:
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
        log_info("Created or verified 'achievements' table")
    except Exception as e:
        log_error(f"Failed to create 'achievements' table: {str(e)}")

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                hashtag VARCHAR(255)
            )
        ''')
        log_info("Created or verified 'videos' table")
    except Exception as e:
        log_error(f"Failed to create 'videos' table: {str(e)}")

    try:
        conn.commit()
        log_info("Database changes committed successfully")
    except Exception as e:
        log_error(f"Failed to commit database changes: {str(e)}")
    
    try:
        conn.close()
        log_info("Database connection closed")
    except Exception as e:
        log_error(f"Failed to close database connection: {str(e)}")