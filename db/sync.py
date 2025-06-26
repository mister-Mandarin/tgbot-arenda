import json
from pathlib import Path
from db.halls import HallsSync
from services.helpers import LIST_HALLS

folder = Path('data')

def compare(conn: HallsSync):
    tokens_from_db = conn.get_all_halls_syncToken()

    for alias in (hall['alias'] for hall in LIST_HALLS):
        for file in folder.glob(f'{alias}_*.json'):
            with file.open('r') as json_file:
                data = json.load(json_file)
                file_token = str(data.get('syncToken'))
                db_token = tokens_from_db.get(alias)

                if file_token != db_token:
                    conn.write_halls_syncToken(alias, file_token)
                    conn.delete_records_data(alias)
                    conn.write_records_data(alias, data['items'])
        

if __name__ == "__main__":
    connection = HallsSync()
    try:
        compare(connection)
    finally:
        connection.close()
    print('Done!')