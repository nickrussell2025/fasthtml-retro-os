# fix_whitespace.py
import os


def fix_trailing_whitespace(filepath):
    """Remove trailing whitespace from a file."""
    with open(filepath, encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = [
        line.rstrip() + '\n' if line.endswith('\n') else line.rstrip() for line in lines
    ]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)


# Fix specific files
files_to_fix = [
    'programs/game_of_life/components.py',
]

for file in files_to_fix:
    if os.path.exists(file):
        fix_trailing_whitespace(file)
        print(f'Fixed: {file}')
