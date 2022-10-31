from pathlib import Path
import shutil
import sys
import re

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

JPEG_IMAGES = []
JPG_IMAGES = []
PNG_IMAGES = []
SVG_IMAGES = []
MP3_AUDIO = []
MY_OTHER = []
ARCHIVES = []

REGISTER_EXTENSIONS = {
    'JPEG': JPEG_IMAGES,
    'PNG': PNG_IMAGES,
    'JPG': JPG_IMAGES,
    'SVG': SVG_IMAGES,
    'MP3': MP3_AUDIO,
    'ZIP': ARCHIVES
}

FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()

TRANS = {}
def normalize(name: str) -> str:
    print(name)
    t_name = name.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    return t_name

def get_extension(filename: str) -> str:
    # перетворюємо розширення файлу на назву папки .jpg -> JPG
    return Path(filename).suffix[1:].upper()


def handle_media(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / (normalize(filename.name.replace(filename.suffix, '')) + '.' + filename.suffix))


def handle_other(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / (normalize(filename.name.replace(filename.suffix, '')) + '.' + filename.suffix))


def handle_archive(filename: Path, target_folder: Path):
    # Створюємо папку для архіву
    target_folder.mkdir(exist_ok=True, parents=True)
    # Створюємо папку куди розпакуємо архів
    # Беремо суфікс у файла і удаляємо replace(filename.suffix, '')
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))

    # Створюємо папку для архіву з іменем файлу
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()),
                              str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f'Це не архів {filename}!')
        folder_for_file.rmdir()
        return None
    filename.unlink()


def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f'Помилка видалення папки {folder}')

def scan(folder: Path) -> None:
    for item in folder.iterdir():
        # Якщо це папка то додаємо її зі списку FOLDERS і переходимо до наступного елемента папки
        if item.is_dir():
            # перевіряємо, щоб папка не була тією, в яку ми складаємо вже файли.
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'MY_OTHER'):
                FOLDERS.append(item)
                # скануємо цю вкладену папку - рекурсія
                scan(item)
            # перейти до наступного елемента в сканованій папці
            continue

        # Робота з файлом
        ext = get_extension(item.name)  # взяти розширення
        fullname = folder / item.name  # взяти повний шлях до файлу
        if not ext:  # якщо файл не має розширення додати до невідомих
            MY_OTHER.append(fullname)
        else:
            try:
                # взяти список куди покласти повний шлях до файлу
                container = REGISTER_EXTENSIONS[ext]
                EXTENSIONS.add(ext)
                container.append(fullname)
            except KeyError:
                # Якщо ми не реєстрували розширення у REGISTER_EXTENSIONS, то додати до іншого
                UNKNOWN.add(ext)
                MY_OTHER.append(fullname)

def sort_files_by_folders(folder: Path):
    for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        TRANS[ord(c)] = l
        TRANS[ord(c.upper())] = l.upper()
    scan(folder)
    for file in JPEG_IMAGES:
        handle_media(file, folder / 'images' / 'JPEG')
    for file in JPG_IMAGES:
        handle_media(file, folder / 'images' / 'JPG')
    for file in PNG_IMAGES:
        handle_media(file, folder / 'images' / 'PNG')
    for file in SVG_IMAGES:
        handle_media(file, folder / 'images' / 'SVG')
    for file in MP3_AUDIO:
        handle_media(file, folder / 'audio' / 'MP3')

    for file in MY_OTHER:
        handle_other(file, folder / 'MY_OTHER')
    for file in ARCHIVES:
        handle_archive(file, folder / 'archives')

    # Виконуємо реверс списку для того щоб видалити всі папки
    for folder in FOLDERS[::-1]:
        handle_folder(folder)

def start_proc_by_command_line():
    if len(sys.argv) < 2:
        print('Потрібно вказати шлях до папки')
    else:
        folder_for_scan = Path(sys.argv[1])
        print(f'Start in folder {folder_for_scan.resolve()}')
        sort_files_by_folders(folder_for_scan.resolve())

if __name__ == '__main__':
    start_proc_by_command_line()

# TODO: запускаємо:  python3 main.py `назва_папки_для_сортування`