from datetime import date
from typing import TypedDict

from db.database import get_connection
from services.helpers import run_in_thread


class User(TypedDict):
    user_id: int
    first_name: str
    last_name: str
    phone: str
    username: str
    role: str
    created_at: date
    last_update: date
    active: bool
    notifications: bool


@run_in_thread
def get_user(user_id: int) -> User | None:
    with get_connection() as conn:
        cur = conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()


@run_in_thread
def create_user(
    user_id: int, first_name: str, last_name: str | None, username: str | None
):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, first_name, last_name, username, phone)
            VALUES (?, ?, ?, ?, '')
        """,
            (
                user_id,
                first_name,
                last_name,
                username,
            ),
        )


@run_in_thread
def update_user(
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    username: str | None = None,
    phone: str | None = None,
    role: str | None = None,
):
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
    if role is not None:
        fields.append("role = ?")
        values.append(role)

    if not fields:
        raise ValueError("Нет данных для обновления")

    fields.append("last_update = datetime('now', '+3 hours')")

    sql = f"""
        UPDATE users
        SET {", ".join(fields)}
        WHERE user_id = ?
    """

    values.append(user_id)

    with get_connection() as conn:
        conn.execute(sql, values)


@run_in_thread
def get_statistics_users():
    with get_connection() as conn:
        cur = conn.execute(
            """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN notifications = 1 AND active = 1 THEN 1 ELSE 0 END) as notifications,
                    SUM(CASE WHEN active = 0 THEN 1 ELSE 0 END) as inactive,
                    SUM(CASE WHEN role = 'admin' THEN 1 ELSE 0 END) as admins
                FROM users
            """
        )

        row = cur.fetchone()
        return row["total"], row["notifications"], row["inactive"], row["admins"]


@run_in_thread
def get_users_for_broadcast():
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT user_id FROM users WHERE notifications = 1 AND active = 1"
        )
        rows = cur.fetchall()
        return [row[0] for row in rows]


@run_in_thread
def update_user_notifications(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET notifications = NOT notifications WHERE user_id = ?",
            (user_id,),
        )
    cur = conn.execute("SELECT notifications FROM users WHERE user_id = ?", (user_id,))
    return cur.fetchone()[0]


@run_in_thread
def set_user_active_false(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_update = datetime('now', '+3 hours'), active = 0 WHERE user_id = ?",
            (user_id,),
        )


@run_in_thread
def set_user_active_true(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_update = datetime('now', '+3 hours'), active = 1 WHERE user_id = ? AND active = 0",
            (user_id,),
        )
