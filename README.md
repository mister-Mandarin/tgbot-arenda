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
15 6-23 * * * chmod +x /path/to/ftp_update.sh && /path/to/ftp_update.sh
```

## Запуск
```bash
# tmux
tmux new -s bot # запуск сессии в tmux
tmux attach -t bot # вход в сессию
tmux kill-session -t имя_сессии # удаление сессии
uv run bot.py >> ./session.log 2>&1 # >> ./session.log — добавляет стандартный вывод (stdout) в файл session.log;
                                    # 2>&1 — перенаправляет стандартный поток ошибок (stderr) в этот же файл;

# systemd
sudo cp /path/to/mybot.service /etc/systemd/system/ # копирование systemd-сервиса
sudo systemctl daemon-reload # перезагрузка демона systemd
sudo systemctl enable mybot.service # автозапуск сервиса при старте системы
sudo systemctl start mybot.service # запуск сервиса
```

## Идеи на развитие
- Команда /clear
- Раздел помощи
- Раздел контактов
- Роль - менеджер