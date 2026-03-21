"""Fix broken imports where custom_popup import was inserted inside from PyQt6.QtWidgets import ("""
import re
import glob
import os

UI_DIR = os.path.join(os.path.dirname(__file__), 'ui')
IMPORT_LINE = "from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger"

py_files = glob.glob(os.path.join(UI_DIR, '**', '*.py'), recursive=True)
for filepath in py_files:
    if 'generated' in filepath or '__pycache__' in filepath or 'custom_popup' in filepath:
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if IMPORT_LINE not in content:
        continue
    
    original = content
    
    # Fix: remove import line that's inside a from ... import ( block
    lines = content.split('\n')
    new_lines = []
    removed = False
    insert_after = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == IMPORT_LINE:
            # Check if previous non-empty line ends with ( — meaning we're inside a multi-line import
            prev_idx = i - 1
            while prev_idx >= 0 and not new_lines[prev_idx] if prev_idx < len(new_lines) else True:
                prev_idx -= 1
            
            # Simple check: is there an unclosed ( before this line?
            text_before = '\n'.join(new_lines)
            open_parens = text_before.count('(') - text_before.count(')')
            if open_parens > 0:
                # We're inside a ( block, remove this line
                removed = True
                continue
        new_lines.append(line)
    
    if removed:
        # Check if the import exists somewhere valid
        valid_content = '\n'.join(new_lines)
        if IMPORT_LINE not in valid_content:
            # Find the last top-level import and add after it
            final_lines = new_lines[:]
            last_import = 0
            in_from_block = False
            for i, line in enumerate(final_lines):
                stripped = line.strip()
                if stripped.startswith('from ') or stripped.startswith('import '):
                    if '(' in stripped and ')' not in stripped:
                        in_from_block = True
                    if not in_from_block:
                        last_import = i
                if in_from_block and ')' in stripped:
                    in_from_block = False
                    last_import = i
            
            final_lines.insert(last_import + 1, IMPORT_LINE)
            new_lines = final_lines
        
        content = '\n'.join(new_lines)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        rel = os.path.relpath(filepath, os.path.dirname(__file__))
        print(f"Fixed: {rel}")

print("Done!")
