"""
Progress Fix for VidyaAI HTML lesson files.
1. Adds saveLessonCompletion() function that calls the server API
2. Adds a "Play Again" button (location.reload()) to the celebration screen
3. Hooks saveLessonCompletion() into the celebration/finish trigger
"""
import os, re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def infer_grade_subject_lesson(filepath):
    """Infer grade, subject, and lesson key from the file path."""
    rel = os.path.relpath(filepath, TEMPLATES_DIR).replace('\\', '/')
    basename = os.path.basename(filepath).replace('.html', '')

    # Class 2 files: class2/<subject>/<filename>.html
    m = re.match(r'class2/(english|maths|evs|kannada|maths_kn|evs_kn)/(.+?)\.html', rel)
    if m:
        return '2', m.group(1), m.group(2)

    # Class 1 english: class1/english/<filename>.html
    m = re.match(r'class1/english/(.+?)\.html', rel)
    if m:
        return '1', 'english', m.group(1)

    # Class 1 maths: class1/maths/<filename>.html
    m = re.match(r'class1/maths/(.+?)\.html', rel)
    if m:
        return '1', 'maths', m.group(1)

    # Class 1 EVS: class1/evs/<filename>.html
    m = re.match(r'class1/evs/(.+?)\.html', rel)
    if m:
        return '1', 'evs', m.group(1)

    # Class 1 Kannada: class1/kannada/<filename>.html (not in subfolder)
    m = re.match(r'class1/kannada/([^/]+?)\.html', rel)
    if m:
        return '1', 'kannada', m.group(1)

    # Class 1 Kannada EVS: class1/kannada/evs/<filename>.html
    m = re.match(r'class1/kannada/evs/(.+?)\.html', rel)
    if m:
        return '1', 'kannada_evs', m.group(1)

    # Class 1 Kannada Maths: class1/kannada/maths/<filename>.html
    m = re.match(r'class1/kannada/maths/(.+?)\.html', rel)
    if m:
        return '1', 'kannada_maths', m.group(1)

    # LKG
    m = re.match(r'lkg_(.+?)\.html', rel)
    if m:
        lesson = m.group(1)
        if 'kannada' in lesson:
            return 'lkg', 'kannada', lesson.replace('kannada_', '')
        return 'lkg', 'english', lesson

    # UKG
    m = re.match(r'ukg_(.+?)\.html', rel)
    if m:
        lesson = m.group(1)
        if 'kannada' in lesson:
            return 'ukg', 'kannada', lesson.replace('kannada_', '')
        return 'ukg', 'english', lesson

    # Stories
    if 'stories' in rel:
        return 'misc', 'stories', basename

    return None, None, None


def build_save_function(grade, subject, lesson):
    """Build the saveLessonCompletion JS function string."""
    return f"""
// === AUTO-INJECTED: Server progress save ===
async function saveLessonCompletion(){{
  try{{
    await fetch('/api/lesson_progress/save', {{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body: JSON.stringify({{grade:'{grade}', subject:'{subject}', lesson:'{lesson}', completed:true, stars: typeof stars !== 'undefined' ? stars : 0}})
    }});
  }}catch(e){{console.log('Progress save failed',e);}}
}}
// === END AUTO-INJECTED ==="""


def add_save_hook(content):
    """Try to hook saveLessonCompletion() into the right place."""
    if 'saveLessonCompletion' in content:
        return content, False  # already hooked

    # Strategy 1: Hook into showCelebration
    patterns = [
        ("function showCelebration() {", "function showCelebration() {\n  saveLessonCompletion();"),
        ("function showCelebration(){", "function showCelebration(){\n  saveLessonCompletion();"),
        ("function showCelebration () {", "function showCelebration () {\n  saveLessonCompletion();"),
    ]
    for old, new in patterns:
        if old in content:
            content = content.replace(old, new, 1)
            return content, True

    # Strategy 2: Hook into finishChapter
    patterns = [
        ("function finishChapter() {", "function finishChapter() {\n  saveLessonCompletion();"),
        ("function finishChapter(){", "function finishChapter(){\n  saveLessonCompletion();"),
    ]
    for old, new in patterns:
        if old in content:
            content = content.replace(old, new, 1)
            return content, True

    # Strategy 3: Hook into the 100% progress point
    if ".style.width = '100%'" in content:
        content = content.replace(
            ".style.width = '100%'",
            ".style.width = '100%';\n        saveLessonCompletion()",
            1
        )
        return content, True

    # Strategy 4: Hook into celeb screen show
    if "celebScreen" in content and "classList.add('show')" in content:
        # Find the celebration show line and add save after it
        idx = content.find("celebScreen")
        if idx > 0:
            show_idx = content.find("classList.add('show')", idx)
            if show_idx > 0:
                semi = content.find(';', show_idx)
                if semi > 0:
                    content = content[:semi+1] + '\n  saveLessonCompletion();' + content[semi+1:]
                    return content, True

    # Strategy 5: Hook into celeb overlay show
    if "celebOverlay" in content and "classList.add('show')" in content:
        idx = content.find("celebOverlay")
        if idx > 0:
            show_idx = content.find("classList.add('show')", idx)
            if show_idx > 0:
                semi = content.find(';', show_idx)
                if semi > 0:
                    content = content[:semi+1] + '\n  saveLessonCompletion();' + content[semi+1:]
                    return content, True

    return content, False


def add_play_again(content):
    """Add Play Again button to celebration screen if missing."""
    if 'Play Again' in content or 'location.reload()' in content:
        return content, False

    # Find celebration buttons and add Play Again after
    search_patterns = [
        'Keep Learning',
        'Back to Lessons', 
        'Back',
    ]
    
    for pattern in search_patterns:
        if pattern in content:
            idx = content.find(pattern)
            if idx > 0:
                btn_end = content.find('</button>', idx)
                if btn_end > 0:
                    btn_end += len('</button>')
                    play_btn = '\n  <button class="celeb-btn" onclick="location.reload()" style="margin-top:10px;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.5);color:#fff;">&#x1f504; Play Again</button>'
                    content = content[:btn_end] + play_btn + content[btn_end:]
                    return content, True

    # Try generic celeb-btn
    if 'celeb-btn' in content:
        # Find last celeb-btn closing tag
        last_idx = content.rfind('celeb-btn')
        if last_idx > 0:
            btn_end = content.find('</button>', last_idx)
            if btn_end > 0:
                btn_end += len('</button>')
                play_btn = '\n  <button class="celeb-btn" onclick="location.reload()" style="margin-top:10px;background:rgba(255,255,255,.2);border:2px solid rgba(255,255,255,.5);color:#fff;">&#x1f504; Play Again</button>'
                content = content[:btn_end] + play_btn + content[btn_end:]
                return content, True

    return content, False


def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False, "Could not read"

    basename = os.path.basename(filepath)
    if basename == 'index.html' or 'dashboard' in basename:
        return False, "Dashboard/index - skip"
    if basename in ('login.html', 'signup.html', 'profile.html', 'tutor.html'):
        return False, "Auth/utility page - skip"
    if '</script>' not in content:
        return False, "No script tag"

    grade, subject, lesson = infer_grade_subject_lesson(filepath)
    if not grade:
        return False, "Could not infer grade/subject/lesson"

    changes = []
    original = content

    # 1. Add saveLessonCompletion function if missing
    if 'saveLessonCompletion' not in content:
        save_fn = build_save_function(grade, subject, lesson)
        last_script = content.rfind('</script>')
        if last_script > 0:
            content = content[:last_script] + save_fn + '\n' + content[last_script:]
            changes.append(f"Added save({grade}/{subject}/{lesson})")

    # 2. Hook the save into celebration/finish
    content, hooked = add_save_hook(content)
    if hooked:
        changes.append("Hooked into completion trigger")

    # 3. Add Play Again button
    content, added = add_play_again(content)
    if added:
        changes.append("Added Play Again button")

    if not changes:
        return False, "No changes needed"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, " | ".join(changes)


def main():
    html_files = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    html_files.sort()

    processed = 0
    skipped = 0

    for fp in html_files:
        rel = os.path.relpath(fp, os.path.dirname(__file__))
        success, msg = process_file(fp)
        if success:
            processed += 1
            print(f"  [OK] {rel} - {msg}")
        else:
            skipped += 1
            print(f"  [SKIP] {rel} - {msg}")

    print(f"\n{'='*60}")
    print(f"DONE! Fixed: {processed} | Skipped: {skipped} | Total: {len(html_files)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
