#!/bin/bash

# Копируем .env.example в .env, если .env не существует
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env создан из .env.example"
fi

# Создаем виртуальное окружение, если не существует
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Виртуальное окружение создано."
fi

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Запускаем приложение
python -m src.main 