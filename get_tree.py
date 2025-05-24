import os
from pathlib import Path

def print_directory_tree(tree, level=0):
    for key, value in tree.items():
        prefix = '|   ' * level + '|-- '
        if isinstance(value, dict):
            print(prefix + key)
            print_directory_tree(value, level + 1)
        else:
            print(prefix + key)

def get_project_tree(root_dir, exclude_dirs=[]):
    tree = {}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Исключаем указанные директории
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        
        # Преобразуем путь относительно корневой директории
        relative_path = os.path.relpath(dirpath, root_dir)
        
        if relative_path == '.':
            current_node = tree
        else:
            parts = relative_path.split(os.sep)
            current_node = tree
            
            for part in parts:
                current_node = current_node.setdefault(part, {})
                
        for dirname in dirnames:
            current_node[dirname] = {}
            
        for filename in filenames:
            current_node[filename] = 'file'
    
    return tree

# Определяем текущую рабочую директорию
current_dir = Path(__file__).parent.resolve()

# Устанавливаем корень проекта как текущую директорию
root_dir = str(current_dir)

# Список исключаемых директорий
exclude_dirs = ['.git', '.venv']

# Получаем и выводим дерево проекта
project_tree = get_project_tree(root_dir, exclude_dirs=exclude_dirs)
print("Структура проекта:")
print_directory_tree(project_tree)