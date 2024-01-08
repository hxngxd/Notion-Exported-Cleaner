import os
import re
from unidecode import unidecode
from datetime import date
from bs4 import BeautifulSoup
from urllib.parse import unquote
import time
import shutil

def decode_url(url):
    return unidecode(unquote(url))

def remove_uuid(s):
    pattern = re.compile(r'\s*\b[a-z0-9]{32}\b\s*')
    return pattern.sub('', s)

def is_valid(s):
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_Export-[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.zip$'
    return True if re.match(pattern, s) else False

def get_name(s):
    match = re.search(r'_([^_]+)\.zip', s);
    return match.group(1) if match else None    

def get_part_num(s):
    match = re.search(r'-Part-(\d+)', s)
    return match.group(1) if match else None

def rename_files_and_folders(root):
    cnt_files = 0
    cnt_folders = 0
    paths = []

    print("> Renaming files...")
    for path, subdirs, files in os.walk(root):
        for name in files:
            new_name = unidecode(remove_uuid(name))
            if new_name != name:
                os.rename(os.path.join(path, name), os.path.join(path, new_name))
                print(f'* Renamed file: {name} => {new_name}.')
                cnt_files += 1
        paths.append(path)
    print("> Done.")

    print("> Renaming folders...")
    paths.reverse()
    paths.pop()
    for path in paths:
        path_split = path.split("\\")
        path_split[-1] = unidecode(remove_uuid(path_split[-1]))
        new_path = '\\'.join(path_split)
        if new_path != path:
            os.rename(path, new_path)
            print(f'* Renamed folder: {path} => {new_path}.')
            cnt_folders += 1
    print("> Done.")

    print(f'> Renamed {cnt_files} files and {cnt_folders} folders.')

def rebuild_index_html(root):
    print("> Rebuilding index.html.")

    filename = f'.\\{root}\\index.html'

    with open(filename, 'r', encoding="utf8") as file:
        data = file.read()

    data = unidecode(data)
    guid_regex = r'\s*\b[a-z0-9]{32}\b\s*'
    data = re.sub(guid_regex, '', data)

    with open(filename, 'w') as file:
        file.write(data)

    print("> Done.")

def replace_all_href(root):
    print("> Replacing hrefs in html files...")

    for path, subdirs, files in os.walk(root):
        for name in files:

            file_name, file_ext = os.path.splitext(name)
            if file_name == "index" or file_ext != ".html": continue

            with open(os.path.join(path, name), 'r', encoding="utf8") as file:
                html = file.read()

            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=True):
                if ".html" in a['href'] or ".png" in a['href']:
                    new_url = remove_uuid(decode_url(a['href']))
                    print("* Replaced href: " + a['href'] + " => " + new_url + ".")
                    a['href'] = new_url
                    for img in a.find_all('img'):
                        new_src = remove_uuid(decode_url(img['src']))
                        print("* Replaced img src: " + img['src'] + " => " + new_src + ".")
                        img['src'] = new_src

            with open(os.path.join(path, name), 'w', encoding="utf8") as file:
                file.write(str(soup))
    
    print("> Done.")

def rename_part(filename, part):
    zip_name = f'{str(date.today())}_{part}'
    os.rename(filename, zip_name)
    return zip_name

def zip_it(dirs):
    print("> Zipping...")
    name = str(date.today())
    os.makedirs(name, exist_ok=True)

    for dir in dirs:
        shutil.copytree(dir, f'{name}/{dir}')
        shutil.rmtree(dir)

    shutil.make_archive(name, 'zip', name)
    shutil.rmtree(name)
    print(f'{os.getcwd()}\{name}.zip')
    print("> Done.")
    
def unzip_it(filename):
    print(f'> Unzipping {filename}...')
    shutil.unpack_archive(filename, ".")
    time.sleep(1)
    print("> Done.")

def clean_it():
    filename = ""
    for dir in os.listdir(os.getcwd()):
        if is_valid(dir):
            filename = dir
            print(f'> Found {filename}')
            break

    if filename=="": return "> No exported was found!"

    unzip_it(filename)
    name = get_name(filename)
    dirs_to_zip = []

    for part in os.listdir(os.getcwd()):
        if part != filename and name in part and ".zip" in part:
            print(f'> Cleaning {part}...')
            unzip_it(part)
            time.sleep(1)
            rename_files_and_folders(name)
            rebuild_index_html(name)
            replace_all_href(name)
            dirs_to_zip.append(rename_part(name, get_part_num(part)))
            os.remove(part)
            print("")
            time.sleep(1)

    zip_it(dirs_to_zip)

    return "> All done. Enjoy!"

print(clean_it())