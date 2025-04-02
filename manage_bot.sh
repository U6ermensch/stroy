#!/bin/bash

# Путь к файлу службы
SERVICE_FILE="telegram_bot.service"
SERVICE_NAME="telegram_bot"

# Функция для проверки статуса службы
check_status() {
    if pgrep -f "python3 bot.py" > /dev/null; then
        echo "Бот запущен и работает"
    else
        echo "Бот не запущен"
    fi
}

# Функция для запуска бота
start_bot() {
    if pgrep -f "python3 bot.py" > /dev/null; then
        echo "Бот уже запущен"
    else
        echo "Запускаем бота..."
        nohup python3 bot.py > bot.log 2>&1 &
        echo "Бот запущен в фоновом режиме"
    fi
}

# Функция для остановки бота
stop_bot() {
    if pgrep -f "python3 bot.py" > /dev/null; then
        echo "Останавливаем бота..."
        pkill -f "python3 bot.py"
        echo "Бот остановлен"
    else
        echo "Бот не был запущен"
    fi
}

# Функция для перезапуска бота
restart_bot() {
    stop_bot
    sleep 2
    start_bot
}

# Обработка аргументов командной строки
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        check_status
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0 