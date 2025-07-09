@echo off
REM Копируем .env.example в .env, если .env не существует
if not exist .env copy .env.example .env

REM Создаем виртуальное окружение, если не существует
if not exist venv (
    python -m venv venv
    echo Виртуальное окружение создано.
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
pip install -r requirements.txt

REM Запускаем приложение
python -m src.main 