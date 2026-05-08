import os, re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def fix_file(fp):
    try:
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return False, str(e)
    
    if 'function saveLessonCompletion' not in content:
        return False, 'No save function present'
        
    calls = len(re.findall(r'saveLessonCompletion\(\)', content))
    if calls > 1:
        return False, 'Already hooked'
        
    original = content
    
    # Try different hook points
    hook_points = [
        (r'(function\s+endLesson\s*\(\)\s*\{)', 'endLesson'),
        (r'(function\s+finishLesson\s*\(\)\s*\{)', 'finishLesson'),
        (r'(function\s+showResults\s*\(\)\s*\{)', 'showResults'),
        (r'(function\s+showResult\s*\(\)\s*\{)', 'showResult'),
        (r'(function\s+celebrate\s*\(\)\s*\{)', 'celebrate'),
        (r'(document\.getElementById\([\'"]celebScreen[\'"]\)\.classList\.add\([\'"]show[\'"]\);?)', 'celebScreen show'),
        (r'(celebScreen\.classList\.add\([\'"]show[\'"]\);?)', 'celebScreen show 2'),
        (r'(function\s+completeLesson\s*\(\)\s*\{)', 'completeLesson'),
        # Fallback to check if a progress bar is set to 100%
        (r'(progFill\.style\.width\s*=\s*[\'"]100%[\'"];?)', 'progFill 100%')
    ]

    for pattern, name in hook_points:
        content = re.sub(pattern, r'\1\n    saveLessonCompletion();', content, count=1)
        if content != original:
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f'Hooked into {name}'

    return False, 'Could not find hook point'

def main():
    fixed = 0
    failed = 0
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if not f.endswith('.html'): continue
            fp = os.path.join(root, f)
            ok, msg = fix_file(fp)
            if ok:
                fixed += 1
            elif msg == 'Could not find hook point':
                failed += 1
    
    print(f"Fixed: {fixed}, Remaining Unhooked: {failed}")

if __name__ == '__main__':
    main()
