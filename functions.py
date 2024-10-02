# functions.py
FILEPATH = r"C:\Users\hp\Desktop\New folder\todos.txt"  # Your task file path

def get_tdos(filepath=FILEPATH):
    try:
        with open(filepath, 'r') as file_local:
            tdos_local = file_local.readlines()
        return tdos_local
    except FileNotFoundError:
        print(f"File not found: {filepath}. Please check the file path.")
        return []
    except PermissionError:
        print(f"Permission denied: {filepath}. Check your file permissions.")
        return []

def write_tdos(tdos_arg, filepath=FILEPATH):
    try:
        with open(filepath, 'w') as file:
            file.writelines(tdos_arg)
    except PermissionError:
        print(f"Permission denied: {filepath}. Check your file permissions.")
