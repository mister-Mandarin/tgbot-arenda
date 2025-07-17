# Телеграм бот школы Альфа-зет по аренде залов

Плохой пример идей https://github.com/alexkarden/telegram-bot-NBRB.BY-sqlite-aiogram3/tree/main

## Команды
```bash
uv run ./bot.py # запуск бота
python3 -m services.sync # синхронизация данных с бд локально на пк
uv run python -m services.sync # синхронизация на сервере
chmod +x ftp_update.sh # выдать права на файл всем пользователям

# crontab
crontab -e # открыть crontab
15 6-23 * * * /home/mandarin/tgbot-arenda/ftp_update.sh
```

## Идеи на развитие
- Команда /clear
- Раздел помощи
- Раздел контактов
- Роль - менеджер