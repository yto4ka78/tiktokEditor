import os
import json

def checkName(directoryToExport):
    number = 1
    while True:
        name = f"outFile{number}.mp4"
        full_path = os.path.join(directoryToExport, name)
        if not os.path.exists(full_path):
            return full_path  # Возвращаем полный путь к несуществующему файлу
        number += 1


SETTINGS_FILE = "videoeditor/settings.json"

def save_outh_video_path(path):
    data = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    
    data["last_video_path"] = path
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def load_last_outh_path():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_video_path", "")
    return ""

def save_loop_video_path(path):
    data = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    
    data["last_loop_path"] = path
    
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def load_last_loop_path():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_loop_path", "")
    return ""
