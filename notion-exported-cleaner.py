import os
import re
from unidecode import unidecode
from datetime import date
from bs4 import BeautifulSoup
from urllib.parse import unquote

def decode_url(url):
    return unidecode(unquote(url))

def remove_uuid(s):
    pattern = re.compile(r'\s*\b[a-z0-9]{32}\b\s*')
    return pattern.sub('', s)

def is_root(s):
    pattern = re.compile(r'\bExport-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\b')
    return bool(pattern.search(s))

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
                print(f'* Renamed file: {name} => {new_name}')
                cnt_files += 1
        paths.append(path)
    print("> Done")

    print("> Renaming folders...")
    paths.reverse()
    paths.pop()
    for path in paths:
        path_split = path.split("\\")
        path_split[-1] = unidecode(remove_uuid(path_split[-1]))
        new_path = '\\'.join(path_split)
        if new_path != path:
            os.rename(path, new_path)
            print(f'* Renamed folder: {path} => {new_path}')
            cnt_folders += 1
    print("> Done")

    print(f'> Renamed {cnt_files} files and {cnt_folders} folders')

def rename_root(root):
    os.rename(root, str(date.today()))

    print(f'* Renamed exported folder: {root} => {str(date.today())}')
    

def rebuild_index_html(root):
    print("> Rebuilding index.html")

    filename = f'.\\{root}\\index.html'

    with open(filename, 'r', encoding="utf8") as file:
        data = file.read()

    data = unidecode(data)
    guid_regex = r'\s*\b[a-z0-9]{32}\b\s*'
    data = re.sub(guid_regex, '', data)

    with open(filename, 'w') as file:
        file.write(data)

    print("> Done")

def replace_all_href():
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
                    print("* Replaced href: " + a['href'] + " => " + new_url)
                    a['href'] = new_url
                    for img in a.find_all('img'):
                        new_src = remove_uuid(decode_url(img['src']))
                        print("* Replaced img src: " + img['src'] + " => " + new_src)
                        img['src'] = new_src

            with open(os.path.join(path, name), 'w', encoding="utf8") as file:
                file.write(str(soup))
    
    print("> Done")

root = ""
for dir in os.listdir(os.getcwd()):
    if os.path.isdir(dir) and is_root(dir):
        root = dir
        break

if root != "":
    rename_files_and_folders(root)
    rebuild_index_html(root)
    replace_all_href()
    rename_root(root)
else:
    print("> Exported folder not found!")