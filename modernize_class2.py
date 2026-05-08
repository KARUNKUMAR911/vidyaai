import os
import re
import glob

# Unified PREMIUM Lesson CSS
premium_lesson_css = '''    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&family=Noto+Sans+Kannada:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body { font-family: 'Noto Sans Kannada', 'Outfit', sans-serif; background: #f8fafc; min-height: 100vh; overflow-x: hidden; color: #1e293b; position: relative; }

        /* DYNAMIC BACKGROUND */
        .bg-blob {
            position: fixed; width: 300px; height: 300px; border-radius: 50%;
            filter: blur(80px); z-index: -1; opacity: 0.15; animation: float 15s infinite alternate;
        }
        .blob-1 { top: -100px; right: -100px; background: var(--accent, #6366f1); }
        .blob-2 { bottom: -100px; left: -100px; background: #22d3ee; }
        @keyframes float { from { transform: translate(0,0); } to { transform: translate(50px, 100px); } }

        /* PREMIUM TOPBAR */
        .topbar {
            background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            padding: clamp(10px, 1.5vw, 20px) clamp(16px, 3vw, 48px);
            display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 500;
            box-shadow: 0 4px 30px rgba(0,0,0,0.03); border-bottom: 1px solid rgba(255,255,255,0.8);
        }
        .topbar-title { font-weight: 900; font-size: clamp(14px, 2vw, 22px); color: #334155; }
        .topbar-right { display: flex; align-items: center; gap: 12px; }
        .stars-pill { 
            background: var(--theme-gradient, #334155); color: white; 
            padding: clamp(4px, 0.8vw, 8px) clamp(10px, 1.5vw, 18px);
            border-radius: 50px; font-size: clamp(13px, 1.5vw, 18px); font-weight: 900;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); font-family: 'Outfit', sans-serif;
        }
        .reset-btn {
            background: white; border: 1px solid rgba(0,0,0,0.05); color: #ef4444;
            padding: 6px 12px; border-radius: 12px; font-size: 11px; font-weight: 900;
            cursor: pointer; transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        }

        /* PREMIUM HERO */
        .hero {
            background: var(--theme-gradient, #334155);
            padding: clamp(30px, 5vw, 60px) clamp(20px, 4vw, 40px) clamp(60px, 8vw, 90px);
            text-align: center; color: white; position: relative; overflow: hidden;
            border-bottom-left-radius: 50px; border-bottom-right-radius: 50px;
        }
        .hero-emoji { font-size: clamp(50px, 8vw, 90px); display: block; margin-bottom: 12px; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.2)); }
        .hero h1 { font-size: clamp(22px, 3.5vw, 42px); font-weight: 900; margin-bottom: 4px; }
        .hero p { font-size: clamp(13px, 1.6vw, 18px); opacity: 0.9; font-weight: 600; }

        /* PROGRESS OVERLAY */
        .prog-wrap {
            margin: clamp(-35px, -5vw, -45px) clamp(16px, 3vw, 48px) 20px;
            background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(20px);
            border-radius: 30px; padding: clamp(14px, 2.5vw, 24px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,1);
            position: relative; z-index: 100;
        }
        .prog-label { font-size: clamp(12px, 1.5vw, 16px); font-weight: 900; color: #475569; margin-bottom: 8px; }
        .prog-bar { background: #f1f5f9; border-radius: 50px; height: 14px; overflow: hidden; }
        .prog-fill { background: var(--theme-gradient, #334155); height: 100%; border-radius: 50px; transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1); width: 0%; }

        /* TABS SCROLLER */
        .steps-bar { display: flex; gap: 10px; padding: 10px clamp(16px, 3vw, 48px); overflow-x: auto; scrollbar-width: none; }
        .step-tab {
            flex-shrink: 0; padding: 10px 20px; border-radius: 50px; font-size: 14px; font-weight: 800;
            background: white; color: #64748b; border: 1px solid rgba(0,0,0,0.03);
            cursor: pointer; transition: all 0.3s; white-space: nowrap; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        }
        .step-tab.active { background: var(--theme-gradient, #334155); color: white; box-shadow: 0 8px 20px rgba(0,0,0,0.1); border: none; }

        /* CONTENT CARDS */
        .content { padding: 10px clamp(16px, 3vw, 48px) 120px; }
        .teach-card {
            background: white; border-radius: 35px; padding: 28px;
            margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.04);
            border-left: 8px solid var(--accent, #475569);
        }
        .teach-card h3 { font-size: 22px; font-weight: 900; color: var(--accent); margin-bottom: 12px; }
        .teach-card p { font-size: 17px; font-weight: 600; color: #475569; line-height: 1.7; }

        .scenario-card {
            background: white; border-radius: 35px; margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.04); overflow: hidden;
            border: 2px solid transparent; transition: all 0.3s;
        }
        .scenario-card.done { border-color: #10b981; background: #f0fdf4; }
        .scene-sentence { font-size: 22px; font-weight: 900; color: #1e293b; line-height: 1.4; }

        .choice-btn {
            flex: 1; min-width: 120px; padding: 18px; border-radius: 20px;
            border: 2px solid #f1f5f9; background: white; font-size: 17px; font-weight: 800;
            color: #334155; cursor: pointer; transition: all 0.2s;
        }
        .choice-btn:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: var(--accent); }
        .choice-btn.correct { background: #10b981; color: white; border-color: #10b981; }
        .choice-btn.wrong { background: #ef4444; color: white; border-color: #ef4444; }

        .big-btn {
            width: 100%; padding: 22px; border: none; border-radius: 24px;
            font-size: 20px; font-weight: 900; cursor: pointer; transition: all 0.3s;
            background: var(--theme-gradient, #475569); color: white;
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }

        .celeb-screen {
            position: fixed; inset: 0; background: var(--theme-gradient, #475569);
            z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;
            opacity: 0; pointer-events: none; transition: all 0.6s cubic-bezier(0.19, 1, 0.22, 1);
        }
        .celeb-screen.show { opacity: 1; pointer-events: all; }
    </style>'''

def modernize_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Subject specific colors
    accent = "#475569"
    grad = "linear-gradient(135deg, #475569, #334155)"
    if 'maths' in filepath:
        accent, grad = "#3b82f6", "linear-gradient(135deg, #3b82f6, #2563eb)"
    elif 'eng' in filepath:
        accent, grad = "#ec4899", "linear-gradient(135deg, #ec4899, #db2777)"
    elif 'evs' in filepath:
        accent, grad = "#10b981", "linear-gradient(135deg, #10b981, #059669)"
    elif 'kan' in filepath:
        accent, grad = "#f59e0b", "linear-gradient(135deg, #f59e0b, #d97706)"

    # Inject variables into CSS
    css = premium_lesson_css.replace('var(--accent, #475569)', accent).replace('var(--theme-gradient, #334155)', grad)

    # 1. Update Style
    content = re.sub(r'<style>.*?</style>', css, content, flags=re.DOTALL)
    
    # 2. Add blobs and style
    if 'bg-blob' not in content:
        content = content.replace('<body', f'<body style="--accent:{accent}; --theme-gradient:{grad};"><div class="bg-blob blob-1"></div><div class="bg-blob blob-2"></div><body')
        content = content.replace('<body<body', '<body')

    # 3. Ensure student_id injection
    if 'window.student_id =' not in content:
        content = content.replace('<script>', '<script>\nwindow.student_id = "{{ student.id if student else \'\' }}";')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

# Search in all Class 2 folders
search_dirs = ['templates/class2/english', 'templates/class2/maths', 'templates/class2/evs', 'templates/class2/kannada', 'templates/class2/maths_kn', 'templates/class2/evs_kn']
count = 0
for d in search_dirs:
    files = glob.glob(os.path.join(d, '*.html'))
    for f in files:
        if 'index.html' in f: continue
        modernize_file(f)
        count += 1
print(f"Modernized {count} lesson files across all Class 2 subjects.")
