
## Setup.bat

```batch
@echo off
chcp 65001 >nul
title Image Text Adder - Настройка среды

echo.
echo ========================================
echo    Image Text Adder - Настройка среды
echo ========================================
echo.

echo Создаем структуру папок...
if not exist "photos" (
    mkdir "photos"
    echo [Создано] Папка 'photos' для ваших изображений
) else (
    echo [Уже существует] Папка 'photos'
)

if not exist "output" (
    mkdir "output"
    echo [Создано] Папка 'output' для результатов
) else (
    echo [Уже существует] Папка 'output'
)

if not exist "examples" (
    mkdir "examples"
    echo [Создано] Папка 'examples' с примерами
) else (
    echo [Уже существует] Папка 'examples'
)

echo.
echo Создаем пример файла заголовков...
if not exist "titles.txt" (
    (
        echo Отдых на море в летний день
        echo Поход в горы с друзьями
        echo Закат над озером
        echo Семейный праздник
        echo Городская архитектура
        echo Природа и животные
        echo Спортивные мероприятия
        echo Культурные события
    ) > "titles.txt"
    echo [Создано] Файл 'titles.txt' с примерами заголовков
) else (
    echo [Уже существует] Файл 'titles.txt'
)

echo.
echo Создаем инструкцию для примеров...
if not exist "examples\README.txt" (
    (
        echo Примеры использования Image Text Adder
        echo =====================================
        echo.
        echo 1. ПРОСТАЯ ОБРАБОТКА:
        echo    - Поместите изображения в папку 'photos'
        echo    - Отредактируйте файл 'titles.txt'
        echo    - Запустите ImageTextAdder.exe
        echo.
        echo 2. ИСПОЛЬЗОВАНИЕ ИМЕН ФАЙЛОВ:
        echo    - Переименуйте файлы в нужные заголовки
        echo    - Пример: "Мой отпуск.jpg", "Семейный ужин.png"
        echo    - Запустите: ImageTextAdder.exe --use-filename
        echo.
        echo 3. РАСШИРЕННЫЕ ВОЗМОЖНОСТИ:
        echo    - Сортировка по дате: --sort-by date
        echo    - Текст сверху: --position top
        echo    - Жирный шрифт: --bold
        echo    - Авторасширение: --auto-extend
        echo.
        echo Полезные команды:
        echo ImageTextAdder.exe --interactive
        echo.
    ) > "examples\README.txt"
    echo [Создано] Файл с инструкциями в папке 'examples'
) else (
    echo [Уже существует] Файл с инструкциями
)

echo.
echo ========================================
echo        Настройка завершена!
echo ========================================
echo.
echo ЧТО ДЕЛАТЬ ДАЛЬШЕ:
echo 1. Поместите ваши изображения в папку 'photos'
echo 2. Отредактируйте файл 'titles.txt' если нужно
echo 3. Запустите 'ImageTextAdder.exe'
echo.
echo ДОПОЛНИТЕЛЬНО:
echo - Запустите 'ImageTextAdder.exe --interactive' для пошаговой настройки
echo - Прочтите 'README.md' для полной инструкции
echo.

set /p choice="Запустить программу сейчас? (y/n): "
if /i "%choice%"=="y" (
    echo Запускаем Image Text Adder...
    timeout /t 2 /nobreak >nul
    start "" "ImageTextAdder.exe"
) else (
    echo.
    echo Вы можете запустить программу вручную, дважды кликнув на 'ImageTextAdder.exe'
)

echo.
pause