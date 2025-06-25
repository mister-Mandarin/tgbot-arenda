from db.database import get_connection

class HallsSync:
    def __init__(self):
        self.conn = get_connection()
        self.conn.isolation_level = "EXCLUSIVE"
        self.conn.execute("BEGIN EXCLUSIVE")

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get_all_halls_syncToken(self):
        cur = self.conn.execute("SELECT alias, syncToken FROM halls")
        return {alias: syncToken for alias, syncToken in cur.fetchall()}

    def write_halls_syncToken(self, alias, token: str):
        self.conn.execute("UPDATE halls SET syncToken = ? WHERE alias = ?", (token, alias))

    def write_records_data(self, alias: str, items: list[dict]):
        records = [
            (item["id"], alias, item["start"], item["end"])
            for item in items
        ]
        self.conn.executemany(
            """
            INSERT INTO records (id, hall_alias, start_time, end_time)
            VALUES (?, ?, ?, ?)
            """, records
        )

    def delete_records_data(self, alias):
        self.conn.execute("DELETE FROM records WHERE hall_alias = ?", (alias,))
