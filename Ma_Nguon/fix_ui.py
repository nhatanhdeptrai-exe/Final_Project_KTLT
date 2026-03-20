import os
import glob
import re

print("Starting fix script...")

# Fix all .ui files
ui_files = glob.glob('D:/Documents/Do_AN/ui/**/*.ui', recursive=True)
for f in ui_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if '<property name="class">' in content:
        content = content.replace('<property name="class">', '<property name="class" stdset="0">')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Fixed {f}")

# Fix all generated .py files
py_files = glob.glob('D:/Documents/Do_AN/Ma_Nguon/ui/**/*.py', recursive=True)
for f in py_files:
    if 'generated' in f:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        if '.setClass(' in content:
            # Replace .setClass(args) with .setProperty("class", args)
            content = re.sub(r'\.setClass\((.*?)\)', r'.setProperty("class", \1)', content)
            with open(f, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed {f}")

print("Fix completed.")
