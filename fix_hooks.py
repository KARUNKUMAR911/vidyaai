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
    
    # Hook strategy 1: showCelebration
    content = re.sub(r'(function\s+showCelebration\s*\(\)\s*\{)', r'\1\n    saveLessonCompletion();', content, count=1)
    if content != original:
        return write_if_changed(fp, content, 'Hooked into showCelebration')

    # Hook strategy 2: finishChapter
    content = re.sub(r'(function\s+finishChapter\s*\(\)\s*\{)', r'\1\n    saveLessonCompletion();', content, count=1)
    if content != original:
        return write_if_changed(fp, content, 'Hooked into finishChapter')
        
    # Hook strategy 3: showCompletion
    content = re.sub(r'(function\s+showCompletion\s*\(\)\s*\{)', r'\1\n    saveLessonCompletion();', content, count=1)
    if content != original:
        return write_if_changed(fp, content, 'Hooked into showCompletion')

    # Hook strategy 4: classList.add('show') on celeb
    # A bit risky, but we can look for celebScreen.classList.add('show')
    content = re.sub(r'(celebScreen\.classList\.add\([\'"]show[\'"]\);?)', r'\1\n    saveLessonCompletion();', content, count=1)
    if content != original:
        return write_if_changed(fp, content, 'Hooked near celebScreen show')

    # Hook strategy 5: 100% width
    content = re.sub(r'(\.style\.width\s*=\s*[\'"]100%[\'"];?)', r'\1\n    saveLessonCompletion();', content, count=1)
    if content != original:
        return write_if_changed(fp, content, 'Hooked near 100% progress')

    # Hook strategy 6: function checkAnswer returning true or celebrating
    # (This is harder to target safely)

    return False, 'Could not find hook point'

def write_if_changed(fp, content, msg):
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    return True, msg

def main():
    fixed = 0
    failed = 0
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if not f.endswith('.html'): continue
            fp = os.path.join(root, f)
            ok, msg = fix_file(fp)
            rel = os.path.relpath(fp, 'templates')
            if ok:
                print(f"[OK] {rel}: {msg}")
                fixed += 1
            elif msg == 'Could not find hook point':
                print(f"[WARN] {rel}: {msg}")
                failed += 1
    
    print(f"Fixed: {fixed}, Unhooked: {failed}")

if __name__ == '__main__':
    main()
