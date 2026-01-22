from db.database import get_connection


class HallsSync:
    def __init__(self):
        self.conn = get_connection()
        self.conn.isolation_level = "EXCLUSIVE"
        self.conn.execute("BEGIN EXCLUSIVE")

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def get_all_halls_syncToken(self):
        cur = self.conn.execute("SELECT alias, syncToken FROM halls")
        return {alias: syncToken for alias, syncToken in cur.fetchall()}

    def write_halls_syncToken(self, alias: str, token: str):
        self.conn.execute(
            """
            UPDATE halls
            SET syncToken = ?, last_update = datetime('now', '+3 hours')
            WHERE alias = ?
            """,
            (token, alias),
        )

    def write_records_data(self, alias: str, items):
        records = [(item["id"], alias, item["start"], item["end"]) for item in items]
        self.conn.executemany(
            """
            INSERT INTO records (id, hall_alias, start_time, end_time)
            VALUES (?, ?, ?, ?)
            """,
            records,
        )

    def delete_records_data(self, alias: str):
        self.conn.execute("DELETE FROM records WHERE hall_alias = ?", (alias,))


def get_halls_time(alias: str, date: str):
    with get_connection() as conn:
        cur = conn.execute(
            "SELECT hall_alias, start_time, end_time FROM records WHERE hall_alias = ? AND start_time LIKE ?",
            (
                alias,
                date + "%",
            ),
        )
        return cur.fetchall()
