# image_text_adder.py
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
import argparse
import sys

def get_resource_path(relative_path):
    """Получает абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Добавление текста к изображениям')
    parser.add_argument('--input', '-i', default='photos', 
                       help='Папка с исходными изображениями (по умолчанию: photos)')
    parser.add_argument('--output', '-o', default='output', 
                       help='Папка для обработанных изображений (по умолчанию: output)')
    parser.add_argument('--titles', '-t', default='titles.txt', 
                       help='Файл с названиями (по умолчанию: titles.txt)')
    parser.add_argument('--position', '-p', choices=['top', 'bottom'], default='bottom',
                       help='Позиция текста: top (сверху) или bottom (снизу) (по умолчанию: bottom)')
    parser.add_argument('--bold', '-b', action='store_true',
                       help='Сделать текст жирным')
    parser.add_argument('--auto-extend', '-a', action='store_true',
                       help='Автоматически расширять последний заголовок без подтверждения')
    parser.add_argument('--interactive', '-I', action='store_true',
                       help='Запустить в интерактивном режиме')
    parser.add_argument('--sort-by', '-s', choices=['name', 'date'], default='name',
                       help='Сортировка изображений: name (по имени) или date (по дате создания)')
    parser.add_argument('--use-filename', '-u', action='store_true',
                       help='Использовать имена файлов как заголовки вместо файла titles.txt')
    return parser.parse_args()

def ask_confirmation(question):
    """Запрос подтверждения от пользователя"""
    while True:
        response = input(f"{question} (y/n): ").strip().lower()
        if response in ['y', 'yes', 'д', 'да']:
            return True
        elif response in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Пожалуйста, введите 'y' (да) или 'n' (нет)")

def get_input_path(prompt, default, path_type="folder"):
    """Получение пути с подсказками"""
    examples = {
        "folder": "Пример: C:\\Users\\Имя\\Pictures\\photos  или  ./photos",
        "file": "Пример: C:\\Users\\Имя\\Documents\\titles.txt  или  ./titles.txt",
        "font": "Пример: C:\\Windows\\Fonts\\arial.ttf  или  ./myfont.ttf"
    }
    
    print(f"\n{prompt}")
    print(examples[path_type])
    
    while True:
        path = input(f"[по умолчанию: {default}]: ").strip()
        if not path:
            path = default
            
        # Заменяем прямые слеши на обратные для Windows
        path = path.replace('/', '\\')
        
        # Проверяем существование
        if path_type == "folder" and not os.path.exists(path):
            print(f"Ошибка: Папка '{path}' не существует!")
            if not ask_confirmation("Создать папку?"):
                continue
            os.makedirs(path, exist_ok=True)
            return path
        
        elif path_type == "file" and not os.path.exists(path):
            print(f"Ошибка: Файл '{path}' не существует!")
            if ask_confirmation("Попробовать другой путь?"):
                continue
            else:
                return None
        
        elif path_type == "font":
            if not os.path.exists(path):
                print(f"Ошибка: Файл шрифта '{path}' не существует!")
                if ask_confirmation("Попробовать другой путь?"):
                    continue
                else:
                    return None
            if not path.lower().endswith('.ttf'):
                print("Ошибка: Файл должен иметь расширение .ttf")
                if ask_confirmation("Попробовать другой путь?"):
                    continue
                else:
                    return None
        
        return path

def select_percentage(prompt, default=3, options=[3,4,5,6,7,8,9]):
    """Выбор процентного значения с предустановленными опциями"""
    print(f"\n{prompt}")
    print("Предустановленные значения:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}%")
    print(f"  {len(options)+1}. Свое значение")
    
    while True:
        try:
            choice = input(f"Выберите вариант (1-{len(options)+1}) [по умолчанию {default}%]: ").strip()
            if not choice:
                return default / 100.0
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return options[choice_num-1] / 100.0
            elif choice_num == len(options)+1:
                custom_val = input("Введите свое значение в %: ").strip()
                if custom_val:
                    custom_percent = int(custom_val)
                    if 1 <= custom_percent <= 100:
                        return custom_percent / 100.0
                    else:
                        print("Ошибка: значение должно быть от 1 до 100%")
                else:
                    print("Используется значение по умолчанию")
                    return default / 100.0
            else:
                print(f"Пожалуйста, выберите вариант от 1 до {len(options)+1}")
        except ValueError:
            print("Пожалуйста, введите число")

def select_color(prompt, default_color, color_type="текста"):
    """Выбор цвета из предустановленных вариантов"""
    colors = {
        'черный': (0, 0, 0),
        'белый': (255, 255, 255),
        'красный': (255, 0, 0),
        'оранжевый': (255, 165, 0),
        'желтый': (255, 255, 0),
        'зеленый': (0, 128, 0),
        'голубой': (0, 255, 255),
        'синий': (0, 0, 255),
        'фиолетовый': (128, 0, 128)
    }
    
    color_names = list(colors.keys())
    default_name = 'черный' if default_color == (0,0,0) else 'белый'
    
    print(f"\n{prompt}")
    print("Доступные цвета:")
    for i, color_name in enumerate(color_names, 1):
        print(f"  {i}. {color_name}")
    
    while True:
        try:
            choice = input(f"Выберите цвет {color_type} (1-{len(color_names)}) [по умолчанию {default_name}]: ").strip()
            if not choice:
                return colors[default_name]
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(color_names):
                return colors[color_names[choice_num-1]]
            else:
                print(f"Пожалуйста, выберите вариант от 1 до {len(color_names)}")
        except ValueError:
            print("Пожалуйста, введите число")

def select_yes_no(prompt, default=False):
    """Выбор да/нет"""
    default_text = "да" if default else "нет"
    while True:
        response = input(f"{prompt} (y/n) [по умолчанию {default_text}]: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes', 'д', 'да']:
            return True
        elif response in ['n', 'no', 'н', 'нет']:
            return False
        else:
            print("Пожалуйста, введите 'y' (да) или 'n' (нет)")

def select_position(prompt, default='bottom'):
    """Выбор позиции текста"""
    positions = ['верх', 'низ']
    default_text = 'низ' if default == 'bottom' else 'верх'
    
    print(f"\n{prompt}")
    print("Доступные позиции:")
    print("  1. верх")
    print("  2. низ")
    
    while True:
        try:
            choice = input(f"Выберите позицию (1-2) [по умолчанию {default_text}]: ").strip()
            if not choice:
                return default
            
            choice_num = int(choice)
            if choice_num == 1:
                return 'top'
            elif choice_num == 2:
                return 'bottom'
            else:
                print("Пожалуйста, выберите 1 или 2")
        except ValueError:
            print("Пожалуйста, введите число")

def select_sort_method(prompt, default='name'):
    """Выбор метода сортировки"""
    methods = ['по имени', 'по дате создания']
    default_text = 'по имени' if default == 'name' else 'по дате создания'
    
    print(f"\n{prompt}")
    print("Методы сортировки изображений:")
    print("  1. по имени")
    print("  2. по дате создания")
    
    while True:
        try:
            choice = input(f"Выберите метод сортировки (1-2) [по умолчанию {default_text}]: ").strip()
            if not choice:
                return default
            
            choice_num = int(choice)
            if choice_num == 1:
                return 'name'
            elif choice_num == 2:
                return 'date'
            else:
                print("Пожалуйста, выберите 1 или 2")
        except ValueError:
            print("Пожалуйста, введите число")

def select_title_source(prompt, default='file'):
    """Выбор источника заголовков"""
    sources = ['из файла', 'из имени файла']
    default_text = 'из файла' if default == 'file' else 'из имени файла'
    
    print(f"\n{prompt}")
    print("Источник заголовков:")
    print("  1. из файла titles.txt")
    print("  2. из имени файла изображения")
    
    while True:
        try:
            choice = input(f"Выберите источник заголовков (1-2) [по умолчанию {default_text}]: ").strip()
            if not choice:
                return default
            
            choice_num = int(choice)
            if choice_num == 1:
                return 'file'
            elif choice_num == 2:
                return 'filename'
            else:
                print("Пожалуйста, выберите 1 или 2")
        except ValueError:
            print("Пожалуйста, введите число")

def select_font():
    """Выбор шрифта"""
    print("\nНастройка шрифта:")
    print("  1. Использовать стандартный шрифт Times New Roman")
    print("  2. Указать свой файл шрифта (.ttf)")
    
    while True:
        try:
            choice = input("Выберите вариант (1-2) [по умолчанию 1]: ").strip()
            if not choice:
                return None, "times.ttf"  # Стандартный шрифт
            
            choice_num = int(choice)
            if choice_num == 1:
                return None, "times.ttf"
            elif choice_num == 2:
                font_path = get_input_path("Введите путь к файлу шрифта (.ttf):", "", "font")
                if font_path:
                    # Проверяем, что файл можно загрузить
                    try:
                        test_font = ImageFont.truetype(font_path, 20)
                        return font_path, os.path.basename(font_path)
                    except Exception as e:
                        print(f"Ошибка загрузки шрифта: {e}")
                        if ask_confirmation("Попробовать другой шрифт?"):
                            continue
                        else:
                            return None, "times.ttf"
                else:
                    print("Используется стандартный шрифт")
                    return None, "times.ttf"
            else:
                print("Пожалуйста, выберите 1 или 2")
        except ValueError:
            print("Пожалуйста, введите число")

def get_image_files_sorted(folder_path, sort_method='name'):
    """Получение списка изображений с сортировкой (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp')
    image_files = []
    
    # Получаем все файлы в папке
    all_files = os.listdir(folder_path)
    
    for filename in all_files:
        # Проверяем расширение файла (без учета регистра)
        if filename.lower().endswith(image_extensions):
            image_files.append(filename)
    
    if sort_method == 'name':
        # Сортировка по имени файла
        image_files.sort()
    elif sort_method == 'date':
        # Сортировка по дате создания (сначала старые)
        image_files.sort(key=lambda x: os.path.getctime(os.path.join(folder_path, x)))
    
    return image_files

def get_titles_from_filenames(image_files):
    """Создание заголовков из имен файлов"""
    titles = []
    for filename in image_files:
        # Убираем расширение файла
        name_without_ext = os.path.splitext(filename)[0]
        # Заменяем подчеркивания и дефисы на пробелы для лучшей читаемости
        clean_name = name_without_ext.replace('_', ' ').replace('-', ' ')
        titles.append(clean_name)
    return titles

def interactive_mode():
    """Интерактивный режим настройки параметров"""
    print("=" * 60)
    print("        РЕЖИМ НАСТРОЙКИ ПАРАМЕТРОВ")
    print("=" * 60)
    
    # Создаем объект для хранения настроек
    class Config:
        pass
    
    config = Config()
    
    # Настройка путей к файлам
    print("\nШАГ 1: Настройка путей к файлам")
    config.input = get_input_path("Папка с изображениями:", "photos", "folder")
    config.output = get_input_path("Папка для результатов:", "output", "folder")
    
    # Настройка источника заголовков
    config.title_source = select_title_source("Источник заголовков для изображений:")
    
    if config.title_source == 'file':
        config.titles = get_input_path("Файл с заголовками:", "titles.txt", "file")
        # Проверяем, что файл с заголовками существует
        if config.titles and not os.path.exists(config.titles):
            print("Файл с заголовками не существует. Создайте его или укажите правильный путь.")
            return None
    else:
        config.titles = None
    
    # Настройка метода сортировки
    config.sort_by = select_sort_method("Сортировка изображений")
    
    # Настройка шрифта
    config.custom_font_path, config.font_name = select_font()
    
    # Настройка размера текста
    config.text_size_ratio = select_percentage(
        "Размер текста относительно высоты изображения:",
        default=3
    )
    
    # Настройка цвета текста
    config.text_color = select_color(
        "Цвет текста:",
        default_color=(0, 0, 0),
        color_type="текста"
    )
    
    # Настройка жирности текста
    config.bold = select_yes_no("Жирный текст?", default=False)
    
    # Настройка позиции текста
    config.position = select_position("Позиция текста:")
    
    # Настройка цвета фона
    config.background_color = select_color(
        "Цвет фона текстовой области:",
        default_color=(255, 255, 255),
        color_type="фона"
    )
    
    # Настройка автоматического расширения (только для файловых заголовков)
    if config.title_source == 'file':
        config.auto_extend = select_yes_no("Автоматически расширять последний заголовок?", default=False)
    else:
        config.auto_extend = False
    
    return config

def main():
    # Получаем аргументы командной строки
    args = parse_arguments()

    # Если запрошен интерактивный режим, запускаем его
    if args.interactive or len(sys.argv) == 1:
        config = interactive_mode()
        
        if config is None:
            print("Настройка отменена.")
            return
        
        # Показываем сводку настроек
        print("\n" + "=" * 60)
        print("        СВОДКА НАСТРОЕК")
        print("=" * 60)
        print(f"Папка с изображениями: {config.input}")
        print(f"Папка для результатов: {config.output}")
        print(f"Источник заголовков: {'из файла' if config.title_source == 'file' else 'из имени файла'}")
        if config.title_source == 'file':
            print(f"Файл с заголовками: {config.titles}")
        print(f"Сортировка: {'по имени' if config.sort_by == 'name' else 'по дате создания'}")
        print(f"Шрифт: {'Стандартный Times' if config.custom_font_path is None else 'Пользовательский: ' + config.font_name}")
        print(f"Размер текста: {config.text_size_ratio * 100}% от высоты изображения")
        print(f"Цвет текста: {config.text_color}")
        print(f"Жирный текст: {'Да' if config.bold else 'Нет'}")
        print(f"Позиция текста: {'верх' if config.position == 'top' else 'низ'}")
        print(f"Цвет фона: {config.background_color}")
        if config.title_source == 'file':
            print(f"Авторасширение: {'Да' if config.auto_extend else 'Нет'}")
        print("=" * 60)
        
        if not ask_confirmation("Начать обработку с этими настройками?"):
            print("Обработка отменена.")
            return
    else:
        # Используем настройки из аргументов командной строки
        config = args
        # Устанавливаем значения по умолчанию для параметров, не заданных через аргументы
        config.text_size_ratio = 0.03  # 3%
        config.text_color = (0, 0, 0)  # черный
        config.background_color = (255, 255, 255)  # белый
        config.custom_font_path = None
        config.font_name = "times.ttf"
        config.title_source = 'filename' if args.use_filename else 'file'

    # Константы, которые не настраиваются
    PADDING_RATIO = 0.02
    LINE_SPACING_RATIO = 0.3
    MAX_TEXT_HEIGHT_RATIO = 0.2
    MIN_FONT_SIZE = 20
    MAX_FONT_SIZE = 150

    # Проверяем существование необходимых папок
    if not os.path.exists(config.input):
        print(f"Ошибка: Папка '{config.input}' не существует!")
        input("Нажмите Enter для выхода...")
        return

    # Создаем выходную папку
    os.makedirs(config.output, exist_ok=True)

    # Получаем список изображений с сортировкой
    image_files = get_image_files_sorted(config.input, config.sort_by)
    
    if not image_files:
        print(f"В папке '{config.input}' не найдено изображений!")
        input("Нажмите Enter для выхода...")
        return

    # Получаем заголовки в зависимости от выбранного источника
    if config.title_source == 'file':
        # Загружаем названия из файла
        if not os.path.exists(config.titles):
            print(f"Ошибка: Файл '{config.titles}' не существует!")
            input("Нажмите Enter для выхода...")
            return
            
        try:
            with open(config.titles, "r", encoding="utf-8") as f:
                titles = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print(f"Ошибка при чтении файла '{config.titles}': {e}")
            input("Нажмите Enter для выхода...")
            return

        # Проверяем, что есть хотя бы один заголовок
        if not titles:
            print(f"Ошибка: Файл '{config.titles}' не содержит заголовков!")
            input("Нажмите Enter для выхода...")
            return

        # Проверяем, достаточно ли заголовков
        if len(titles) < len(image_files):
            missing_count = len(image_files) - len(titles)
            last_title = titles[-1]
            
            print(f"ВНИМАНИЕ: Заголовков ({len(titles)}) меньше, чем изображений ({len(image_files)})!")
            print(f"Не хватает {missing_count} заголовков.")
            print(f"Для оставшихся {missing_count} изображений будет использован последний заголовок:")
            print(f"'{last_title}'")
            print()
            
            if not config.auto_extend:
                if not ask_confirmation("Продолжить с этими настройками?"):
                    print("Обработка отменена пользователем.")
                    return
            else:
                print("Автоматическое расширение заголовков включено. Продолжаем...")
            
            # Расширяем список заголовков, повторяя последний заголовок
            titles.extend([last_title] * missing_count)
            print(f"Список заголовков расширен до {len(titles)} записей")
            print("-" * 50)
    else:
        # Создаем заголовки из имен файлов
        titles = get_titles_from_filenames(image_files)
        print(f"Создано {len(titles)} заголовков из имен файлов")

    print(f"\nНайдено {len(image_files)} изображений")
    print(f"Сортировка: {'по имени' if config.sort_by == 'name' else 'по дате создания'}")
    print(f"Источник заголовков: {'из файла' if config.title_source == 'file' else 'из имени файла'}")
    print(f"Используемый шрифт: {config.font_name}")
    print("-" * 50)

    # Обрабатываем изображения
    processed_count = 0
    
    for i, filename in enumerate(image_files):
        try:
            # Открываем и конвертируем изображение
            img_path = os.path.join(config.input, filename)
            img = Image.open(img_path).convert('RGB')
            
            # Получаем размеры изображения
            img_width, img_height = img.size
            
            # Вычисляем адаптивные параметры на основе размера изображения
            base_font_size = int(img_height * config.text_size_ratio)
            font_size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, base_font_size))
            
            padding = int(img_height * PADDING_RATIO)
            line_spacing = int(font_size * LINE_SPACING_RATIO)
            max_text_height = int(img_height * MAX_TEXT_HEIGHT_RATIO)
            
            # Загружаем шрифт
            font = None
            
            # Если указан пользовательский шрифт
            if config.custom_font_path:
                try:
                    font = ImageFont.truetype(config.custom_font_path, font_size)
                except Exception as e:
                    print(f"Ошибка загрузки пользовательского шрифта: {e}")
                    print("Используется стандартный шрифт")
                    config.custom_font_path = None
            
            # Если пользовательский шрифт не загружен, используем стандартные пути
            if font is None:
                font_paths = [
                    "times.ttf",
                    "times new roman.ttf", 
                    "Times New Roman.ttf",
                    "Times.ttf",
                    get_resource_path("times.ttf")
                ]
                
                # Если нужен жирный шрифт, пробуем сначала жирные версии
                if config.bold:
                    bold_paths = [
                        "timesbd.ttf", "timesb.ttf", "TIMESBD.TTF",
                        "times new roman bold.ttf", "Times New Roman Bold.ttf",
                        get_resource_path("timesbd.ttf")
                    ]
                    font_paths = bold_paths + font_paths
                
                for font_path in font_paths:
                    try:
                        if os.path.exists(font_path):
                            font = ImageFont.truetype(font_path, font_size)
                            break
                    except:
                        continue
            
            # Если шрифт все еще не найден, используем стандартный
            if font is None:
                print(f"Шрифт не найден, используется стандартный шрифт")
                font = ImageFont.load_default()
            
            # Создаем временный объект для рисования для расчета размеров текста
            temp_draw = ImageDraw.Draw(img)
            
            # Подготавливаем текст с переносами
            text = titles[i]
            
            # Определяем максимальную ширину для текста (с отступами)
            max_text_width = img_width - 2 * padding
            
            # Разбиваем текст на строки с учетом переноса
            avg_char_width = font_size * 0.6
            approx_chars_per_line = max(10, int(max_text_width / avg_char_width))
            
            wrapper = textwrap.TextWrapper(width=approx_chars_per_line)
            wrapped_lines = wrapper.wrap(text)
            
            # Если текст не помещается по ширине, разбиваем по символам
            if not wrapped_lines:
                def split_text_by_width(text, font, max_width):
                    lines = []
                    current_line = ""
                    
                    for char in text:
                        test_line = current_line + char
                        bbox = temp_draw.textbbox((0, 0), test_line, font=font)
                        test_width = bbox[2] - bbox[0]
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = char
                    
                    if current_line:
                        lines.append(current_line)
                    
                    return lines
                
                wrapped_lines = split_text_by_width(text, font, max_text_width)
            
            # Вычисляем высоту текстового блока
            bbox = temp_draw.textbbox((0, 0), "Test", font=font)
            line_height = bbox[3] - bbox[1] + line_spacing
            text_block_height = len(wrapped_lines) * line_height + 2 * padding
            
            # Ограничиваем максимальную высоту текстового блока
            text_block_height = min(text_block_height, max_text_height)
            
            # Создаем новое изображение с увеличенной высотой
            new_img_height = img_height + text_block_height
            new_img = Image.new('RGB', (img_width, new_img_height), color=config.background_color)
            
            # Вставляем оригинальное изображение в нужную позицию
            if config.position == 'bottom':
                new_img.paste(img, (0, 0))
                text_y_start = img_height
            else:
                new_img.paste(img, (0, text_block_height))
                text_y_start = 0
            
            # Создаем объект для рисования на новом изображении
            draw_new = ImageDraw.Draw(new_img)
            
            # Рисуем текст в нужной позиции
            y_position = text_y_start + padding
            
            for line in wrapped_lines:
                bbox = draw_new.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (img_width - text_width) / 2
                
                draw_new.text((x_position, y_position), line, fill=config.text_color, font=font)
                y_position += line_height
            
            # Сохраняем
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_labeled{ext}"
            output_path = os.path.join(config.output, output_filename)
            new_img.save(output_path)
            
            processed_count += 1
            
            # Показываем, какой заголовок использован
            if config.title_source == 'file':
                title_source = "расширенный" if i >= (len(titles) - (len(image_files) - len(titles))) and len(titles) < len(image_files) else "оригинальный"
                print(f"Обработано: {filename} -> {output_filename} ({len(wrapped_lines)} стр., {title_source} заголовок)")
            else:
                print(f"Обработано: {filename} -> {output_filename} ({len(wrapped_lines)} стр., из имени файла)")
            
        except Exception as e:
            print(f"Ошибка при обработке {filename}: {e}")
            continue

    print("-" * 50)
    print(f"Обработка завершена! Успешно обработано: {processed_count}/{len(image_files)} изображений")
    
    # Показываем статистику по использованию заголовков
    if config.title_source == 'file' and len(titles) > len(image_files):
        print(f"Использовано {len(image_files)} из {len(titles)} заголовков")
    elif config.title_source == 'file' and len(titles) < len(image_files) and processed_count == len(image_files):
        extended_count = len(image_files) - (len(titles) - (len(image_files) - len(titles)))
        print(f"Использовано {len(titles) - extended_count} оригинальных и {extended_count} расширенных заголовков")
    
    # Для Windows: оставляем консоль открытой
    if os.name == 'nt':
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()