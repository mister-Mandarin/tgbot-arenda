import sqlite3
from pathlib import Path

DB_PATH = Path("data.sqlite3")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        '''
        Таблица пользователей
        role по плану будет user/admin/manager
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                first_name  TEXT NOT NULL,
                last_name   TEXT,
                phone       TEXT NOT NULL DEFAULT '',
                username    TEXT,
                role        TEXT NOT NULL DEFAULT 'user',
                created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_update TIMESTAMP NULL,
                active      BOOLEAN NOT NULL DEFAULT TRUE
            );
        """)

        '''
        Таблица залов
        alias - уникальное название зала        
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS halls (
                name VARCHAR(100) NOT NULL UNIQUE,
                alias VARCHAR(50) PRIMARY KEY,
                price_per_hour INTEGER NOT NULL,
                description TEXT,
                capacity SMALLINT,
                noise_level VARCHAR(20), -- low/medium/high
                syncToken TEXT NULL,
                last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                
                     
            );
        """)

        '''Индексы для быстрого поиска'''
        conn.executescript("""
            CREATE INDEX IF NOT EXISTS idx_halls_alias ON halls(alias);
            CREATE INDEX IF NOT EXISTS idx_halls_price ON halls(price_per_hour);
        """)

        halls_data = [
            ("Зал 120/Классика", 'big120', 4400, "Светлый просторный зал  в 4 минутах от метро Достоевская для тренингов, семинаров, телесно-ориентированных практик, вместимость 40-60 человек. Свежий ремонт, полы — ламинат, 4 больших окна с возможностью затемнения. Две большие музыкальные колонки Samsung (проводное , проектор, флипчарт, коврики, пуфы, термопот входят в стоимость. Кулер с горячей, холодной и газированной водой в зоне ожидания, возможность организовать чайную зону в углу зала.", 60, 'medium'),
            ('Зал 90/Эзотерика', 'big90', 3300, "Зал в эзотерическом стиле со статуей медитируюшего Будды и возможностью цветного освещения.", 40, 'low'),
            ("Зал 60/Романтика", 'medium60', 2200, "Прямоугольный зал с фантазийными элементами в оформлении.", 15, 'low'),
            ('Малый зал 30/Практика', 'small30', 1100, "Небольшой зал для мини-групп и индивидуальных сессий.", 25, 'high'),
            ('Кабинет 16/Массаж', 'small16', 2000, "С кушеткой и местом для беседы с клиентом.", 18, 'low')
        ]

        for hall in halls_data:
            try:
                conn.execute(
                    "INSERT INTO halls (name, alias, price_per_hour, description, capacity, noise_level) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    hall
                )
            except sqlite3.IntegrityError:
                # Если запись уже существует - пропускаем
                continue

        '''
        Записи залов
        ON DELETE CASCADE означает, что если зал удаляется из halls, 
        все связанные с ним события удаляются автоматически.
        '''
        conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id TEXT PRIMARY KEY,
                hall_alias VARCHAR(50) NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                FOREIGN KEY (hall_alias) REFERENCES halls(alias) ON DELETE CASCADE
            );
        """)