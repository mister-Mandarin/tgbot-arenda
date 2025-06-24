from db.database import get_connection

def get_all_halls_syncToken():
    with get_connection() as conn: 
        cur = conn.execute("SELECT alias, syncToken FROM halls")
        return {alias: syncToken for alias, syncToken in cur.fetchall()}

def write_syncToken(alias, token: str):
    with get_connection() as conn:
        conn.execute("UPDATE halls SET syncToken = ? WHERE alias = ?", (token, alias))

def write_hall_data(alias, data: dict):
    pass
# Нужно заполнить данными бд.
# чтобы заполнить данными бд нужно получить данные из файла по алиасу.
