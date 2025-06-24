import json
from pathlib import Path
from db.halls import get_all_halls_syncToken, write_syncToken

list_alias = ['big120', 'big90', 'medium60', 'small30', 'small16']
list_tokens = []
folder = Path('data')

def get_tokens_from_files():
    tokens_from_files = {}

    for alias in list_alias:
        for file in folder.glob(f'{alias}_*.json'):

            with open(file, 'r') as json_file:
                data = json.load(json_file)
                tokens_from_files[alias] = data['syncToken']
    return tokens_from_files

def compare():
    tokens_from_files = get_tokens_from_files()
    tokens_from_db = get_all_halls_syncToken()

    for alias in list_alias:
        file_token = tokens_from_files.get(alias)
        db_token = tokens_from_db.get(alias)

        if file_token != db_token:
            write_syncToken(alias, str(file_token))

if __name__ == "__main__":
    compare()
    print('Done!')