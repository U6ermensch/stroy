import sys
import os

# Добавляем путь к текущей директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем бота
from bot import main

if __name__ == '__main__':
    main() 