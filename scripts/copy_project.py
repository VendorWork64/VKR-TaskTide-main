#!/usr/bin/env python3
import shutil
import os

# Пути
source = '/Users/vendor/Desktop/Программирование/TaskTide'
dest = '/Users/vendor/Desktop/Программирование/курсор 2'

try:
    # Проверяем существование исходной папки
    if os.path.exists(source):
        # Удаляем папку назначения если она существует
        if os.path.exists(dest):
            shutil.rmtree(dest)
        
        # Копируем папку
        shutil.copytree(source, dest)
        print(f'✅ Копия проекта создана успешно!')
        print(f'📁 Исходная папка: {source}')
        print(f'📁 Копия: {dest}')
    else:
        print(f'❌ Исходная папка не найдена: {source}')
except Exception as e:
    print(f'❌ Ошибка при копировании: {e}')
