import os
import re
from unidecode import unidecode
from datetime import date

def remove_char(s, index):
    return s[:index] + s[index + 1:]
def remove_end_space(s):
    while s[0]==' ':
        s = remove_char(s, 0)
    while s[-1]==' ':
        s = remove_char(s, len(s)-1)
    return s

def rename_files(root):
    cnt=0
    for path, subdirs, files in os.walk(root):
        for name in files:
            file_name, file_ext = os.path.splitext(name)
            guid = file_name.split(' ')[-1]
            if len(guid)==32:
                file_name = remove_end_space(unidecode(file_name[:-33])) + file_ext
                os.rename(os.path.join(path, name), os.path.join(path, file_name))
                print(f'Renamed: {name} => {file_name}')
                cnt+=1
            if path not in paths:
                paths.append(path)
    return cnt

def rename_directories():
    cnt=0
    paths.reverse()
    paths.pop()
    for path in paths:
        split_path = path.split('\\')
        dirname = split_path[-1]
        guid = dirname.split(' ')[-1]
        if len(guid)==32:
            dirname = remove_end_space(unidecode(dirname[:-33]))
            split_path.pop()
            split_path.append(dirname)
            newpath = '\\'.join(split_path)
            os.rename(path, newpath)
            print(f'Renamed: {path} => {newpath}')
            cnt+=1
    return cnt

def remove_guids(filename):
    with open(filename, 'r', encoding="utf8") as file:
        data = file.read()

    data = unidecode(data)
    guid_regex = r'\s*\b[a-z0-9]{32}\b\s*'
    data = re.sub(guid_regex, '', data)

    with open(filename, 'w') as file:
        file.write(data)

def contains_uuid(s):
    # UUIDs are in the form of 8-4-4-4-12 hexadecimal characters
    uuid_regex = r'\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b'
    match = re.search(uuid_regex, s)
    return match is not None

paths = []

current_folder = os.getcwd()
exported_dir = ""
for dir in os.listdir(current_folder):
    if os.path.isdir(dir) and contains_uuid(dir):
        exported_dir = dir

remove_guids(f'.\\{exported_dir}\\index.html')

f = rename_files(exported_dir)
d = rename_directories()
os.rename(f'{current_folder}\\{exported_dir}', f'{current_folder}\\{exported_dir[:-36]}{str(date.today())}')

print(f'Renamed {f} files and {d+1} directories')
