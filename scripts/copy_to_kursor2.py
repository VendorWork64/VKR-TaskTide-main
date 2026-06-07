#!/usr/bin/env python3
import shutil
import os

def create_copy():
    # Пути
    source = '/Users/vendor/Desktop/Программирование/TaskTide'
    dest = '/Users/vendor/Desktop/Программирование/курсор 2'
    
    try:
        print(f"📁 Исходная папка: {source}")
        print(f"📁 Папка назначения: {dest}")
        
        # Проверяем существование исходной папки
        if os.path.exists(source):
            print("✅ Исходная папка найдена")
            
            # Удаляем папку назначения если она существует
            if os.path.exists(dest):
                print("🗑️ Удаляем существующую папку назначения")
                shutil.rmtree(dest)
            
            # Копируем папку
            print("📋 Копируем проект...")
            shutil.copytree(source, dest)
            print("✅ Копия проекта создана успешно!")
            
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
