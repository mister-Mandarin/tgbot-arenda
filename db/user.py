from db.database import get_connection

def get_user(user_id: int):
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()

def create_user(user_id: int, first_name: str, last_name: str | None, username: str | None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (user_id, first_name, last_name, username, phone)
            VALUES (?, ?, ?, ?, '')
        """, (user_id, first_name, last_name, username,))

def update_user(user_id: int, first_name: str | None = None, last_name: str | None = None,
                username: str | None = None, phone: str | None = None):
    fields = []
    values = []

    if first_name is not None:
        fields.append("first_name = ?")
        values.append(first_name)
    if last_name is not None:
        fields.append("last_name = ?")
        values.append(last_name)
    if username is not None:
        fields.append("username = ?")
        values.append(username)
    if phone is not None:
        fields.append("phone = ?")
        values.append(phone)

    if not fields:
        raise ValueError("Нет данных для обновления")

    fields.append("last_update = CURRENT_TIMESTAMP")

    sql = f"""
        UPDATE users
        SET {', '.join(fields)}
        WHERE user_id = ?
    """

    values.append(user_id)

    with get_connection() as conn:
        conn.execute(sql, values)

