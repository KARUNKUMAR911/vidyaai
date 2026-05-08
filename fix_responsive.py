"""
Responsive Scaling Injector for VidyaAI HTML files.
Scans each HTML file for known CSS class names and injects the corresponding
clamp()-based responsive rules right before </style>.
Does NOT change colors, text, or any existing styles — only ADDS responsive overrides.
"""
import os, re, glob

# Master mapping: CSS selector -> clamp() responsive override
# These are based on the Class 3 reference files
RESPONSIVE_RULES = {
    # TOPBAR / NAVBAR
    '.topbar': 'padding:clamp(10px,1.5vw,20px) clamp(16px,3vw,48px);',
    '.topbar-title': 'font-size:clamp(15px,2vw,28px);',
    '.stars-pill': 'font-size:clamp(14px,1.6vw,22px);padding:clamp(5px,0.8vw,10px) clamp(12px,1.5vw,22px);',
    '.navbar': 'padding:clamp(10px,1.5vw,20px) clamp(16px,3vw,48px);',

    # HERO
    '.hero-emoji': 'font-size:clamp(56px,7vw,120px);',
    '.hero-icon': 'font-size:clamp(56px,7vw,120px);',
    '.hero h1': 'font-size:clamp(22px,3.5vw,52px);',
    '.hero h2': 'font-size:clamp(22px,3.5vw,52px);',
    '.hero p': 'font-size:clamp(13px,1.6vw,22px);',
    '.hero': 'padding:clamp(18px,3vw,48px) clamp(20px,5vw,80px) clamp(44px,6vw,80px);',

    # HEADER (alternate name used in some files)
    '.header h1': 'font-size:clamp(22px,3.5vw,52px);',
    '.header p': 'font-size:clamp(13px,1.6vw,22px);',
    '.header': 'padding:clamp(18px,3vw,48px) clamp(20px,5vw,80px) clamp(44px,6vw,80px);',

    # PROGRESS
    '.prog-wrap': 'margin:clamp(-22px,-2vw,-16px) clamp(12px,3vw,48px) clamp(12px,2vw,24px);padding:clamp(12px,1.8vw,22px) clamp(16px,2.5vw,36px);',
    '.prog-label': 'font-size:clamp(13px,1.4vw,20px);',
    '.prog-bar': 'height:clamp(12px,1.4vw,20px);',
    '.progress-card': 'margin:clamp(-18px,-2vw,-14px) clamp(12px,3vw,48px) clamp(12px,2vw,24px);padding:clamp(12px,1.8vw,22px) clamp(16px,2.5vw,36px);border-radius:clamp(14px,2vw,24px);',
    '.progress-circle': 'width:clamp(44px,6vw,72px);height:clamp(44px,6vw,72px);font-size:clamp(15px,2vw,26px);',
    '.progress-info h4': 'font-size:clamp(13px,1.5vw,20px);',
    '.progress-info p': 'font-size:clamp(11px,1.3vw,17px);',
    '.progress-bar-wrap': 'height:clamp(6px,1vw,12px);',

    # TABS / STEPS
    '.steps-bar': 'padding:clamp(10px,1.5vw,20px) clamp(12px,3vw,48px) 4px;gap:clamp(6px,1vw,16px);',
    '.step-tab': 'font-size:clamp(12px,1.3vw,18px);padding:clamp(8px,1vw,14px) clamp(12px,1.5vw,22px);',

    # CONTENT AREA
    '.content': 'padding:clamp(6px,1vw,16px) clamp(12px,3.5vw,60px) clamp(80px,10vw,140px);',

    # LESSON BANNER
    '.lesson-banner': 'padding:clamp(12px,1.8vw,24px) clamp(14px,2vw,28px);gap:clamp(10px,1.5vw,20px);border-radius:clamp(16px,2vw,28px);',
    '.banner-emoji': 'font-size:clamp(36px,5vw,72px);',
    '.banner-title': 'font-size:clamp(17px,2.2vw,32px);',
    '.banner-sub': 'font-size:clamp(11px,1.3vw,18px);',

    # TEACH CARD
    '.teach-card': 'padding:clamp(14px,2vw,28px);border-radius:clamp(16px,2vw,28px);',
    '.teach-card h3': 'font-size:clamp(15px,1.8vw,26px);',
    '.teach-card p': 'font-size:clamp(13px,1.5vw,22px);line-height:1.9;',
    '.hl': 'font-size:clamp(13px,1.6vw,22px);',

    # RHYME CARD
    '.rhyme-card': 'padding:clamp(14px,2vw,32px);border-radius:clamp(16px,2vw,28px);',
    '.rhyme-title': 'font-size:clamp(17px,2.2vw,32px);',
    '.rhyme-line': 'font-size:clamp(14px,1.8vw,28px);line-height:2.2;',

    # SCENARIO CARDS
    '.scenario-card': 'border-radius:clamp(18px,2vw,28px);',
    '.scene-top': 'padding:clamp(14px,1.8vw,24px) clamp(14px,2vw,28px) clamp(8px,1vw,14px);',
    '.scene-label': 'font-size:clamp(10px,1.1vw,15px);',
    '.scene-sentence': 'font-size:clamp(15px,1.9vw,28px);',
    '.scene-sentence .kw': 'font-size:clamp(17px,2.1vw,30px);',
    '.scene-bottom': 'padding:clamp(10px,1.4vw,20px) clamp(14px,2vw,28px);',

    # CHOICE BUTTONS
    '.choice-btn': 'padding:clamp(12px,1.5vw,22px) clamp(6px,1vw,14px);border-radius:clamp(14px,1.5vw,22px);font-size:clamp(13px,1.5vw,20px);',
    '.choice-btn .cb-emoji': 'font-size:clamp(24px,3.5vw,52px);',
    '.choice-btn .cb-word': 'font-size:clamp(11px,1.2vw,17px);',
    '.fb-box': 'font-size:clamp(13px,1.5vw,20px);padding:clamp(8px,1vw,14px);',

    # BIG BUTTONS
    '.big-btn': 'font-size:clamp(16px,2vw,28px);padding:clamp(14px,1.8vw,24px);border-radius:clamp(14px,1.8vw,24px);',

    # INFO STRIP
    '.info-strip': 'padding:clamp(10px,1.4vw,20px) clamp(14px,2vw,28px);border-radius:clamp(12px,1.5vw,22px);',
    '.info-strip p': 'font-size:clamp(13px,1.5vw,20px);',

    # QUIZ
    '.quiz-box-wrap': 'padding:clamp(14px,2vw,28px);border-radius:clamp(18px,2vw,28px);',
    '.quiz-num': 'font-size:clamp(11px,1.2vw,17px);',
    '.quiz-question': 'font-size:clamp(16px,2vw,30px);',
    '.quiz-opts': 'gap:clamp(8px,1.2vw,18px);',
    '.quiz-opt': 'font-size:clamp(14px,1.7vw,24px);padding:clamp(13px,1.7vw,24px) clamp(8px,1vw,16px);border-radius:clamp(13px,1.5vw,22px);',
    '.quiz-fb': 'font-size:clamp(13px,1.5vw,20px);',

    # MATCH GAME
    '.match-item': 'font-size:clamp(12px,1.5vw,21px);padding:clamp(12px,1.5vw,20px) clamp(8px,1vw,14px);border-radius:clamp(12px,1.5vw,20px);',
    '.match-col-title': 'font-size:clamp(12px,1.4vw,20px);',

    # ODD ONE OUT
    '.odd-group': 'padding:clamp(12px,1.6vw,24px);border-radius:clamp(16px,2vw,28px);',
    '.odd-group-title': 'font-size:clamp(12px,1.4vw,20px);',
    '.odd-item': 'font-size:clamp(12px,1.4vw,20px);padding:clamp(9px,1.1vw,16px) clamp(12px,1.5vw,22px);border-radius:clamp(12px,1.4vw,20px);',

    # WORD CHIPS / PILLS
    '.word-chip': 'font-size:clamp(12px,1.4vw,20px);padding:clamp(7px,0.9vw,14px) clamp(12px,1.5vw,22px);',
    '.word-pill': 'font-size:clamp(12px,1.4vw,20px);padding:clamp(7px,0.9vw,14px) clamp(12px,1.5vw,22px);',

    # BODY CARDS
    '.body-card': 'padding:clamp(12px,1.5vw,24px);border-radius:clamp(16px,2vw,28px);',
    '.body-emoji': 'font-size:clamp(40px,5.5vw,80px);',
    '.body-name': 'font-size:clamp(14px,1.8vw,26px);',
    '.body-fact': 'font-size:clamp(11px,1.3vw,19px);',

    # CELEBRATION
    '.celeb-emoji': 'font-size:clamp(70px,10vw,140px);',
    '.celeb-title': 'font-size:clamp(24px,3.5vw,54px);',
    '.celeb-sub': 'font-size:clamp(14px,1.8vw,26px);',
    '.celeb-stars': 'font-size:clamp(36px,5vw,72px);',
    '.celeb-btn': 'font-size:clamp(16px,2vw,28px);padding:clamp(14px,1.8vw,22px) clamp(36px,4vw,60px);border-radius:clamp(40px,5vw,60px);',

    # TOAST
    '.lock-toast': 'font-size:clamp(13px,1.5vw,20px);padding:clamp(10px,1.4vw,18px) clamp(18px,2.5vw,32px);',

    # SECTION DIVIDER
    '.section-divider': 'font-size:clamp(12px,1.4vw,20px);',

    # OPPOSITES
    '.opp-card': 'padding:clamp(10px,1.5vw,22px);border-radius:clamp(14px,2vw,24px);',
    '.opp-word': 'font-size:clamp(13px,1.6vw,22px);padding:clamp(6px,1vw,14px) clamp(10px,1.5vw,20px);',

    # WORD GROUP
    '.word-group': 'padding:clamp(10px,1.5vw,22px);border-radius:clamp(14px,2vw,24px);',
    '.word-group-title': 'font-size:clamp(13px,1.5vw,22px);',

    # GENERAL CARDS (common in lesson files)
    '.card': 'border-radius:clamp(16px,2vw,28px);',
    '.card-title': 'font-size:clamp(14px,1.7vw,24px);',

    # CHAPTER CARDS (index pages)
    '.chapter-card': 'padding:clamp(12px,1.5vw,22px) clamp(14px,2vw,28px);border-radius:clamp(14px,2vw,24px);',
    '.chapter-num': 'width:clamp(36px,5vw,60px);height:clamp(36px,5vw,60px);border-radius:clamp(10px,1.2vw,18px);font-size:clamp(16px,2.2vw,30px);',
    '.chapter-title': 'font-size:clamp(13px,1.6vw,22px);',
    '.chapter-meta': 'font-size:clamp(11px,1.2vw,17px);',
    '.chapter-status': 'font-size:clamp(15px,2vw,26px);',

    # SECTION LABEL
    '.section-label': 'font-size:clamp(11px,1.2vw,17px);padding:clamp(6px,1vw,12px) clamp(12px,2vw,24px);',

    # SUBJECT CARDS (dashboards)
    '.subject-card': 'border-radius:clamp(16px,2vw,28px);padding:clamp(14px,2vw,28px);',
    '.card-icon': 'font-size:clamp(36px,5vw,72px);',
    '.card-badge': 'font-size:clamp(10px,1.1vw,15px);padding:clamp(3px,0.5vw,8px) clamp(8px,1vw,16px);',
    '.card-sub': 'font-size:clamp(11px,1.3vw,18px);',
    '.card-en': 'font-size:clamp(10px,1.1vw,15px);',

    # SECTIONS (dashboards)
    '.section-title': 'font-size:clamp(14px,1.7vw,24px);padding:clamp(10px,1.5vw,20px) clamp(14px,2vw,28px);',
    '.progress-section': 'padding:clamp(10px,1.5vw,20px) clamp(14px,2vw,28px);',
    '.progress-title': 'font-size:clamp(13px,1.5vw,20px);',
    '.progress-count': 'font-size:clamp(11px,1.3vw,17px);',

    # CHALLENGE CARD
    '.challenge-card': 'padding:clamp(12px,1.5vw,22px) clamp(14px,2vw,28px);border-radius:clamp(16px,2vw,28px);',
    '.challenge-text h3': 'font-size:clamp(14px,1.7vw,24px);',
    '.challenge-text p': 'font-size:clamp(11px,1.3vw,18px);',
    '.challenge-icon': 'font-size:clamp(28px,4vw,56px);',
    '.challenge-arrow': 'font-size:clamp(18px,2.5vw,36px);',

    # WELCOME SECTION
    '.welcome-section': 'padding:clamp(16px,2.5vw,40px) clamp(14px,3vw,48px);border-radius:clamp(20px,3vw,40px);',
    '.welcome-name': 'font-size:clamp(20px,3vw,44px);',
    '.welcome-grade': 'font-size:clamp(12px,1.4vw,20px);',

    # BOTTOM NAV
    '.bottom-nav': 'padding:clamp(6px,1vw,14px) 0 clamp(8px,1.2vw,16px);',
    '.nav-icon': 'font-size:clamp(18px,2.5vw,32px);',
    '.nav-label': 'font-size:clamp(10px,1.1vw,15px);',

    # GENERIC TYPOGRAPHY
    '.stats-container': 'padding:0 clamp(14px,2.5vw,36px);gap:clamp(10px,1.5vw,22px);',
    '.stat-card': 'padding:clamp(12px,1.5vw,22px);border-radius:clamp(16px,2.5vw,28px);',
    '.stat-info h3': 'font-size:clamp(14px,1.6vw,24px);',
    '.stat-info p': 'font-size:clamp(11px,1.3vw,17px);',

    # FORM ELEMENTS (login/signup)
    '.auth-container': 'padding:clamp(20px,3vw,48px);border-radius:clamp(16px,2.5vw,32px);',
    '.form-group label': 'font-size:clamp(13px,1.5vw,20px);',
    '.form-group input': 'padding:clamp(10px,1.3vw,18px);font-size:clamp(14px,1.5vw,20px);border-radius:clamp(10px,1.3vw,18px);',
    '.auth-title': 'font-size:clamp(22px,3vw,44px);',
    '.auth-btn': 'padding:clamp(12px,1.5vw,22px);font-size:clamp(15px,1.8vw,26px);border-radius:clamp(12px,1.5vw,22px);',

    # BACK BUTTON
    '.back-btn': 'padding:clamp(5px,0.8vw,12px) clamp(10px,1.3vw,20px);font-size:clamp(12px,1.3vw,18px);',

    # LKG/UKG specific
    '.activity-card': 'padding:clamp(14px,2vw,28px);border-radius:clamp(16px,2vw,28px);',
    '.activity-title': 'font-size:clamp(16px,2vw,28px);',
    '.grid-item': 'padding:clamp(10px,1.3vw,20px);border-radius:clamp(12px,1.5vw,22px);font-size:clamp(13px,1.5vw,20px);',
    '.emoji-big': 'font-size:clamp(40px,5.5vw,80px);',
    '.item-label': 'font-size:clamp(12px,1.4vw,20px);',
    '.letter-card': 'padding:clamp(12px,1.5vw,24px);border-radius:clamp(14px,2vw,24px);',
    '.letter-big': 'font-size:clamp(48px,7vw,100px);',
    '.number-card': 'padding:clamp(12px,1.5vw,24px);border-radius:clamp(14px,2vw,24px);',
    '.number-big': 'font-size:clamp(48px,7vw,100px);',
    '.color-card': 'padding:clamp(12px,1.5vw,24px);border-radius:clamp(14px,2vw,24px);',
    '.shape-card': 'padding:clamp(12px,1.5vw,24px);border-radius:clamp(14px,2vw,24px);',

    # PAGE TITLE
    '.page-title': 'font-size:clamp(20px,3vw,44px);',
    '.sub-title': 'font-size:clamp(13px,1.6vw,22px);',
}

def get_class_name(selector):
    """Extract the base class name from a CSS selector for searching."""
    # e.g. '.teach-card h3' -> 'teach-card'
    match = re.match(r'\.([a-zA-Z0-9_-]+)', selector)
    return match.group(1) if match else None

def file_has_class(content, class_name):
    """Check if a file's CSS or HTML contains a reference to this class."""
    # Check in CSS rules or HTML class attributes
    return class_name in content

def strip_old_responsive(content):
    """Remove any existing RESPONSIVE SCALING block from the CSS."""
    # Pattern 1: Remove our injected block (between comment markers)
    pattern1 = r'/\*\s*=+\s*RESPONSIVE SCALING[^*]*\*/(.*?)(?=/\*|</style>)'
    content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Pattern 2: Remove inline clamp() from individual CSS rules
    # We need to find all CSS rules that contain clamp() and remove the clamp-based properties
    # but keep the rest of the rule intact. This is complex, so instead we'll
    # remove entire lines that contain clamp() within <style> blocks.
    lines = content.split('\n')
    new_lines = []
    in_responsive_section = False
    for line in lines:
        # Detect start of responsive section
        if 'RESPONSIVE SCALING' in line:
            in_responsive_section = True
            continue
        # Detect end of responsive section (next non-clamp, non-empty line or </style>)
        if in_responsive_section:
            stripped = line.strip()
            if stripped == '' or 'clamp(' in stripped:
                continue  # skip these lines
            else:
                in_responsive_section = False
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def process_file(filepath, force=False):
    """Process a single HTML file - inject responsive clamp() rules."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return False, "Could not read file"

    # Skip if no <style> tag
    if '</style>' not in content:
        return False, "No </style> tag"

    had_clamp = 'clamp(' in content
    
    # If file already has clamp, strip old responsive rules first
    if had_clamp:
        content = strip_old_responsive(content)

    # Find which responsive rules apply to this file
    applicable_rules = []
    for selector, rule in RESPONSIVE_RULES.items():
        class_name = get_class_name(selector)
        if class_name and file_has_class(content, class_name):
            applicable_rules.append(f'{selector}{{{rule}}}')

    if not applicable_rules:
        return False, "No matching classes found"

    # Build the responsive CSS block
    responsive_block = "\n/* ===== RESPONSIVE SCALING - FULL WIDTH ===== */\n"
    responsive_block += "\n".join(applicable_rules)
    responsive_block += "\n"

    # Inject before the LAST </style> tag
    last_style_pos = content.rfind('</style>')
    if last_style_pos == -1:
        return False, "No </style> found"

    new_content = content[:last_style_pos] + responsive_block + content[last_style_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    action = "Replaced old + injected" if had_clamp else "Injected"
    return True, f"{action} {len(applicable_rules)} responsive rules"


def main():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    html_files = []
    for root, dirs, files in os.walk(templates_dir):
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))

    html_files.sort()
    
    processed = 0
    skipped = 0
    errors = 0

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
    print(f"DONE! Processed: {processed} | Skipped: {skipped} | Total: {len(html_files)}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
