"""
Fix index/dashboard pages to show per-user progress from the server API.
Adds:
1. Progress card UI (if missing)
2. data-lesson attributes on lesson cards (if missing)
3. JavaScript to fetch /api/lesson_progress/load and update UI
"""
import os, re

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

# ── Files that need progress wired in ──
FILES_TO_FIX = {
    # path relative to templates -> (grade, subject, total_lessons)
    'class1/kannada/maths/index.html': ('1', 'kannada_maths', 19),
    'class1/kannada/evs/index.html':   ('1', 'kannada_evs', 16),
    'class1/hindi/index.html':         ('1', 'hindi', 0),  # may not have lessons yet
    'dashboard.html':                  (None, None, None),  # main dashboard, special
    'lkg_dashboard.html':              (None, None, None),  # special
}

def build_progress_css():
    """Progress card CSS styles."""
    return """
/* Progress Card */
.progress-card {
    background: white; margin: -18px 16px 20px;
    border-radius: 18px; padding: 14px 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    display: flex; align-items: center; gap: 14px;
}
.progress-circle {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #e64a19, #f57c00);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 18px; font-weight: 900; flex-shrink: 0;
}
.progress-info { flex: 1; }
.progress-info h4 { font-size: 14px; font-weight: 800; color: #333; }
.progress-info p  { font-size: 12px; color: #888; margin-top: 2px; }
.progress-bar-wrap {
    flex: 1; background: #f0f0f0;
    border-radius: 10px; height: 8px; overflow: hidden; margin-top: 6px;
}
.progress-bar-inner {
    height: 100%; background: linear-gradient(90deg, #e64a19, #ffab91);
    border-radius: 10px; width: 0%; transition: width 0.5s;
}
"""


def build_progress_html():
    """Progress card HTML."""
    return """
<div class="progress-card">
    <div class="progress-circle" id="progressNum">0%</div>
    <div class="progress-info" style="flex:1">
        <h4>My Progress</h4>
        <p id="progressText">Loading...</p>
        <div class="progress-bar-wrap">
            <div class="progress-bar-inner" id="progressBar"></div>
        </div>
    </div>
</div>
"""


def build_progress_js(grade, subject):
    """JavaScript to load and display progress."""
    return f"""
<script>
async function loadProgress() {{
    try {{
        const res = await fetch('/api/lesson_progress/load?grade={grade}&subject={subject}');
        const data = await res.json();
        const lessons = data.lessons || {{}};
        const total = data.totalLessons || document.querySelectorAll('.card[data-lesson], .chapter-card[data-lesson]').length || 1;
        const completed = Object.values(lessons).filter(x => x.completed).length;
        const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

        const numEl = document.getElementById('progressNum');
        const txtEl = document.getElementById('progressText');
        const barEl = document.getElementById('progressBar');
        if(numEl) numEl.textContent = pct + '%';
        if(txtEl) txtEl.textContent = completed + ' of ' + total + ' lessons completed';
        if(barEl) barEl.style.width = pct + '%';

        document.querySelectorAll('.card[data-lesson], .chapter-card[data-lesson], a[data-lesson]').forEach(card => {{
            const key = card.getAttribute('data-lesson');
            const p = lessons[key] || {{completed:false, stars:0}};
            card.classList.remove('completed','inprogress','notstarted');
            const statusEl = card.querySelector('.chapter-status, .card-arrow');

            if (p.completed) {{
                card.classList.add('completed');
                if(statusEl) statusEl.textContent = '\\u2705';
                card.style.borderLeft = '4px solid #059669';
            }} else if (p.stars > 0) {{
                card.classList.add('inprogress');
                if(statusEl) statusEl.textContent = '\\u23f3';
                card.style.borderLeft = '4px solid #f59e0b';
            }} else {{
                card.classList.add('notstarted');
                if(statusEl) statusEl.textContent = '\\u25b6\\ufe0f';
            }}
        }});
    }} catch(e) {{ console.log('Progress load failed', e); }}
}}
loadProgress();
</script>
"""


def add_data_lesson_attrs(content):
    """Add data-lesson attributes to card links that are missing them."""
    # Find <a href="/class/.../lessonX" class="card ..."> without data-lesson
    def add_attr(match):
        href = match.group(1)
        rest = match.group(2)
        # Extract lesson key from href
        parts = href.rstrip('/').split('/')
        lesson_key = parts[-1] if parts else ''
        if 'data-lesson' in rest:
            return match.group(0)  # already has it
        return f'<a href="{href}" data-lesson="{lesson_key}" {rest}'
    
    # Match <a href="..." class="card ..."> or <a href="..." class="chapter-card ...">
    pattern = r'<a href="([^"]*(?:lesson\d+|chapter\d+)[^"]*)"(\s+class="(?:card|chapter-card)[^"]*"[^>]*>)'
    content = re.sub(pattern, add_attr, content)
    return content


def process_index_file(filepath, grade, subject, total):
    """Process an index file to add progress tracking."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False, "Could not read"

    changes = []

    # 1. Add data-lesson attributes
    if 'data-lesson' not in content:
        content = add_data_lesson_attrs(content)
        if 'data-lesson' in content:
            changes.append("Added data-lesson attrs")

    # 2. Add progress card CSS if missing
    has_progress_card = 'progress-card' in content or 'progress-circle' in content
    if not has_progress_card:
        # Insert CSS before </style>
        css = build_progress_css()
        style_end = content.rfind('</style>')
        if style_end > 0:
            content = content[:style_end] + css + content[style_end:]
            changes.append("Added progress CSS")

    # 3. Add progress card HTML if missing
    has_progress_html = 'progressNum' in content or 'progressBar' in content or 'progressText' in content
    if not has_progress_html:
        # Insert after the header/hero section, before the chapters list
        # Try to find section-label or chapters-list
        insert_before = content.find('<div class="section-label"')
        if insert_before < 0:
            insert_before = content.find('<div class="chapters-list"')
        if insert_before > 0:
            html = build_progress_html()
            content = content[:insert_before] + html + '\n' + content[insert_before:]
            changes.append("Added progress card HTML")

    # 4. Add progress loading JS if missing
    has_progress_js = 'loadProgress' in content
    if not has_progress_js and grade and subject:
        js = build_progress_js(grade, subject)
        # Insert before </body>
        body_end = content.rfind('</body>')
        if body_end > 0:
            content = content[:body_end] + js + '\n' + content[body_end:]
            changes.append(f"Added progress JS ({grade}/{subject})")

    if not changes:
        return False, "No changes needed"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True, " | ".join(changes)


def main():
    processed = 0
    skipped = 0

    for rel_path, (grade, subject, total) in FILES_TO_FIX.items():
        fp = os.path.join(TEMPLATES_DIR, rel_path)
        if not os.path.exists(fp):
            print(f"  [SKIP] {rel_path} - File not found")
            skipped += 1
            continue

        if grade is None:
            # Special dashboards - skip for now, they use a different pattern
            print(f"  [SKIP] {rel_path} - Special dashboard (already has own pattern)")
            skipped += 1
            continue

        success, msg = process_index_file(fp, grade, subject, total)
        if success:
            processed += 1
            print(f"  [OK] {rel_path} - {msg}")
        else:
            skipped += 1
            print(f"  [SKIP] {rel_path} - {msg}")

    # Now also fix existing index files that have API but may have issues
    # Check class2/evs/index.html and class2/maths/index.html which have API but no progress UI
    extra_files = [
        ('class2/evs/index.html', '2', 'evs'),
        ('class2/maths/index.html', '2', 'maths'),
    ]
    for rel_path, grade, subject in extra_files:
        fp = os.path.join(TEMPLATES_DIR, rel_path)
        if not os.path.exists(fp):
            continue
        content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
        if 'progressNum' not in content and 'progressBar' not in content:
            success, msg = process_index_file(fp, grade, subject, 0)
            if success:
                processed += 1
                print(f"  [OK] {rel_path} - {msg}")
            else:
                skipped += 1
                print(f"  [SKIP] {rel_path} - {msg}")

    print(f"\n{'='*60}")
    print(f"DONE! Fixed: {processed} | Skipped: {skipped}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
