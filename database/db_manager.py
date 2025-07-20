import sqlite3
import datetime
from typing import List, Dict, Any, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.init_db()
    
    def connect(self):
        """Установка соединения с базой данных"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def disconnect(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        self.connect()
        
        # Создание таблицы фильмов с добавлением столбца usage_count
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        )
        ''')
        
        # Проверка наличия столбца usage_count и добавление его, если отсутствует
        try:
            self.cursor.execute("SELECT usage_count FROM movies LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE movies ADD COLUMN usage_count INTEGER DEFAULT 0")
        
        # Создание таблицы пользователей с добавлением столбца click_count
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0,
            click_count INTEGER DEFAULT 0
        )
        ''')
        
        # Проверка наличия столбца click_count и добавление его, если отсутствует
        try:
            self.cursor.execute("SELECT click_count FROM users LIMIT 1")
        except sqlite3.OperationalError:
            self.cursor.execute("ALTER TABLE users ADD COLUMN click_count INTEGER DEFAULT 0")
        
        self.conn.commit()
        self.disconnect()
    
    # Методы для работы с фильмами
    
    def add_movie(self, code: str, title: str) -> bool:
        """Добавление нового фильма"""
        try:
            self.connect()
            self.cursor.execute(
                "INSERT INTO movies (code, title, usage_count) VALUES (?, ?, 0)",
                (code, title)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Код уже существует
            return False
        finally:
            self.disconnect()
    
    def get_movie_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Получение фильма по коду"""
        self.connect()
        self.cursor.execute("SELECT * FROM movies WHERE code = ?", (code,))
        movie = self.cursor.fetchone()
        self.disconnect()
        
        if movie:
            return dict(movie)
        return None
    
    def increment_movie_usage(self, code: str) -> bool:
        """Увеличение счетчика использования фильма"""
        self.connect()
        self.cursor.execute(
            "UPDATE movies SET usage_count = usage_count + 1 WHERE code = ?",
            (code,)
        )
        updated = self.cursor.rowcount > 0
        self.conn.commit()
        self.disconnect()
        return updated
    
    def get_all_movies(self) -> List[Dict[str, Any]]:
        """Получение всех фильмов"""
        self.connect()
        self.cursor.execute("SELECT * FROM movies ORDER BY created_at DESC")
        movies = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return movies
    
    def delete_movie(self, code: str) -> bool:
        """Удаление фильма по коду"""
        self.connect()
        self.cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
        deleted = self.cursor.rowcount > 0
        self.conn.commit()
        self.disconnect()
        return deleted
    
    # Методы для работы с пользователями
    
    def add_or_update_user(self, user_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> None:
        """Добавление или обновление пользователя"""
        self.connect()
        self.cursor.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name, click_count)
            VALUES (?, ?, ?, ?, 0)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(excluded.username, username),
                first_name = COALESCE(excluded.first_name, first_name),
                last_name = COALESCE(excluded.last_name, last_name)
            """,
            (user_id, username, first_name, last_name)
        )
        self.conn.commit()
        self.disconnect()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение пользователя по ID"""
        self.connect()
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = self.cursor.fetchone()
        self.disconnect()
        
        if user:
            return dict(user)
        return None
    
    def increment_click_count(self, user_id: int) -> int:
        """Увеличение счетчика кликов пользователя и возврат нового значения"""
        self.connect()
        self.cursor.execute(
            """
            UPDATE users SET click_count = click_count + 1 WHERE user_id = ?
            RETURNING click_count
            """,
            (user_id,)
        )
        result = self.cursor.fetchone()
        self.conn.commit()
        self.disconnect()
        
        if result:
            return result[0]
        return 0
    
    def reset_click_count(self, user_id: int) -> None:
        """Сброс счетчика кликов пользователя"""
        self.connect()
        self.cursor.execute(
            "UPDATE users SET click_count = 0 WHERE user_id = ?",
            (user_id,)
        )
        self.conn.commit()
        self.disconnect()
    
    def set_admin_status(self, user_id: int, is_admin: bool) -> None:
        """Установка статуса администратора для пользователя"""
        self.connect()
        self.cursor.execute(
            "UPDATE users SET is_admin = ? WHERE user_id = ?",
            (1 if is_admin else 0, user_id)
        )
        self.conn.commit()
        self.disconnect()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение всех пользователей"""
        self.connect()
        self.cursor.execute("SELECT * FROM users")
        users = [dict(row) for row in self.cursor.fetchall()]
        self.disconnect()
        return users
