"""
Script to replace all QMessageBox calls with custom_popup calls across the project.
This only modifies Python files in the ui/ directory.
"""
import re
import os
import glob

UI_DIR = os.path.join(os.path.dirname(__file__), 'ui')
IMPORT_LINE = "from ui.UI_Common.custom_popup import show_success, show_error, show_warning, show_info, ask_question, ask_danger"

# Patterns to replace
REPLACEMENTS = [
    # QMessageBox.information(self, "title", "msg") → show_success(self, "title", "msg")
    (r'QMessageBox\.information\(self,\s*"Thành công"', 'show_success(self, "Thành công"'),
    (r'QMessageBox\.information\(self,\s*"OK"', 'show_success(self, "Thành công"'),
    # Generic QMessageBox.information → show_info
    (r'QMessageBox\.information\(self,', 'show_info(self,'),

    # QMessageBox.warning → show_warning  
    (r'QMessageBox\.warning\(self,', 'show_warning(self,'),

    # QMessageBox.critical → show_error
    (r'QMessageBox\.critical\(self,', 'show_error(self,'),

    # QMessageBox.question patterns → ask_question
    # These are more complex, we'll handle them separately
]

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'QMessageBox' not in content:
        return False

    original = content

    # Apply simple replacements
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)

    # Handle QMessageBox.question patterns
    # Pattern: reply = QMessageBox.question(self, "title", "msg", QMessageBox.StandardButton.Yes | ...)
    #          if reply == QMessageBox.StandardButton.Yes:
    # Replace with: if ask_question(self, "title", "msg"):
    content = re.sub(
        r'reply\s*=\s*QMessageBox\.question\(\s*self,\s*(".*?"),\s*(".*?"(?:\s*\+\s*".*?")*),\s*\n\s*QMessageBox\.StandardButton\.Yes\s*\|\s*QMessageBox\.StandardButton\.No\)\s*\n(\s*)if reply == QMessageBox\.StandardButton\.Yes:',
        r'if ask_question(self, \1, \2):',
        content,
        flags=re.DOTALL
    )

    # Also handle single-line question patterns
    content = re.sub(
        r'reply\s*=\s*QMessageBox\.question\(self,\s*(".*?"),\s*(f?".*?"),\s*\n\s*QMessageBox\.StandardButton\.Yes\s*\|\s*QMessageBox\.StandardButton\.No\)\s*\n(\s*)if reply == QMessageBox\.StandardButton\.Yes:',
        r'if ask_question(self, \1, \2):',
        content,
        flags=re.DOTALL
    )

    if content == original:
        return False

    # Add import if not already present
    if 'custom_popup' not in content:
        # Find the last import line and add after it
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                last_import_idx = i
            elif line.strip() and not line.startswith('#') and not line.startswith('"""') and last_import_idx > 0:
                break
        lines.insert(last_import_idx + 1, IMPORT_LINE)
        content = '\n'.join(lines)

    # Remove or clean up QMessageBox from imports if no longer used
    # (Don't remove entirely since some files might still need it for other reasons)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

# Find all Python files in ui/
py_files = glob.glob(os.path.join(UI_DIR, '**', '*.py'), recursive=True)
modified = []
for f in py_files:
    # Skip generated files
    if 'generated' in f or '__pycache__' in f:
        continue
    if process_file(f):
        modified.append(os.path.relpath(f, os.path.dirname(__file__)))
        print(f"  Modified: {os.path.relpath(f, os.path.dirname(__file__))}")

print(f"\nTotal files modified: {len(modified)}")
