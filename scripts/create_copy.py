#!/usr/bin/env python3
import shutil
import os
import sys

def create_copy():
    # Пути
    source = '/Users/vendor/Desktop/Программирование/TaskTide'
    dest = '/Users/vendor/Desktop/Программирование/курсор 2'
    
    try:
        # Проверяем существование исходной папки
        if os.path.exists(source):
            print(f"📁 Исходная папка найдена: {source}")
            
            # Удаляем папку назначения если она существует
            if os.path.exists(dest):
                print(f"🗑️ Удаляем существующую папку: {dest}")
                shutil.rmtree(dest)
            
            # Копируем папку
            print(f"📋 Копируем проект...")
            shutil.copytree(source, dest)
            print(f"✅ Копия проекта создана успешно!")
            print(f"📁 Исходная папка: {source}")
            print(f"📁 Копия: {dest}")
            
            # Проверяем что копия создалась
            if os.path.exists(dest):
                files = os.listdir(dest)
                print(f"📄 Файлов в копии: {len(files)}")
                for file in files:
                    print(f"  - {file}")
            else:
                print("❌ Копия не была создана")
                
        else:
            print(f"❌ Исходная папка не найдена: {source}")
            
    except Exception as e:
        print(f"❌ Ошибка при копировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_copy()
