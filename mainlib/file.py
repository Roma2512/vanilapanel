import os, datetime

def f_size(size_bytes):
    if size_bytes == 0: return "0 Б"
    size_names = ("Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "ЭБ", "ЗБ", "ЙБ")
    i = 0
    size = float(size_bytes)

    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1

    precision = 2
    rounded_size = round(size, precision)
    if rounded_size == int(rounded_size):
        precision = 0

    return f"{rounded_size:.{precision}f} {size_names[i]}"

def get_file(path):
    filename = os.path.basename(path)
    if os.path.isfile(path):
        stat = os.stat(path)
        date = datetime.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return {"isdir": False, "name": path.split("/")[-1], "size": f_size(os.path.getsize(path)), "date": date, "ext": filename.split(".")[-1]}
    else:
        return {"isdir": True, "name": path.split("/")[-1], "ext": "folder"}


def get_files(path):
    files = []
    for file in os.listdir(path):
        files.append(get_file(f"{path}/{file}"))

    files.sort(key=lambda x: (not x['isdir'], x['name'].lower()))

    return files

def get_folder_size(path, follow_symlinks=False):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            fp = os.path.join(dirpath, filename)
            if not follow_symlinks and os.path.islink(fp):
                continue
            total_size += os.path.getsize(fp)
    return total_size