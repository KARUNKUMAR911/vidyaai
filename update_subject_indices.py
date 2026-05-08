import re
import os

unified_subject_css = '''    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }

        body {
            background: var(--bg-gradient, linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%));
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            padding-bottom: 80px;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            padding: clamp(12px, 2vw, 20px) clamp(16px, 4vw, 40px);
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border-bottom: 1px solid rgba(255,255,255,0.8);
            position: sticky; top: 0; z-index: 100;
        }
        .navbar-left { display: flex; align-items: center; gap: clamp(8px, 2vw, 15px); }
        .navbar-logo { font-size: clamp(18px, 3vw, 24px); font-weight: 900; background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .navbar-subject { background: rgba(255,255,255,0.8); color: #334155; padding: 4px 12px; border-radius: 20px; font-size: clamp(11px, 1.5vw, 14px); font-weight: 700; border: 1px solid rgba(0,0,0,0.05); }
        .back-btn { background: white; color: #334155; padding: 7px 16px; border-radius: 20px; font-size: clamp(12px, 1.5vw, 14px); font-weight: 700; text-decoration: none; border: 1px solid rgba(0,0,0,0.1); transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .back-btn:hover { transform: translateX(-3px); }

        .hero {
            background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155));
            padding: clamp(30px, 6vw, 60px) 20px clamp(50px, 8vw, 80px);
            text-align: center; color: white;
            border-bottom-left-radius: 40px; border-bottom-right-radius: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0, 0.1); margin-bottom: 30px;
        }
        .hero-icon { font-size: clamp(50px, 8vw, 90px); margin-bottom: 15px; filter: drop-shadow(0 4px 15px rgba(0,0,0,0.2)); }
        .hero h2 { font-size: clamp(26px, 4vw, 42px); font-weight: 900; margin-bottom: 6px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .hero p  { font-size: clamp(14px, 1.8vw, 18px); opacity: 0.9; font-weight: 600; max-width: 600px; margin: 0 auto; }

        .progress-card {
            background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            margin: -45px 20px 25px; border-radius: 28px; padding: clamp(16px, 3vw, 24px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.9);
            display: flex; align-items: center; gap: clamp(15px, 3vw, 25px);
            position: relative; z-index: 10;
        }
        .progress-circle {
            width: clamp(50px, 8vw, 70px); height: clamp(50px, 8vw, 70px); border-radius: 50%;
            background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155));
            display: flex; align-items: center; justify-content: center;
            color: white; font-size: clamp(16px, 2.5vw, 22px); font-weight: 900; flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .progress-info h4 { font-size: clamp(15px, 2vw, 19px); font-weight: 800; color: #1f2937; }
        .progress-info p  { font-size: clamp(12px, 1.5vw, 15px); color: #6b7280; margin-top: 2px; font-weight: 600; }
        .progress-bar-wrap { flex: 1; background: rgba(0,0,0,0.05); border-radius: 12px; height: 10px; overflow: hidden; margin-top: 8px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
        .progress-bar-inner { height: 100%; background: var(--theme-gradient, #475569); border-radius: 12px; width: 0%; transition: width 0.8s cubic-bezier(0.34, 1.56, 0.64, 1); }

        .section-label { padding: 15px 24px 15px; font-size: clamp(18px, 3vw, 24px); font-weight: 900; color: #111827; display: flex; align-items: center; gap: 10px; }

        .chapters-list { padding: 0 20px 40px; display: grid; grid-template-columns: 1fr; gap: 16px; }

        .chapter-card {
            background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
            border-radius: 24px; padding: clamp(16px, 2.5vw, 22px);
            display: flex; align-items: center; gap: clamp(14px, 2.5vw, 20px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.04);
            cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none; position: relative; overflow: hidden;
            border: 1px solid rgba(255,255,255,0.7);
        }
        .chapter-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.08); background: rgba(255,255,255,0.95); }
        .chapter-card:active { transform: scale(0.97); }
        
        .chapter-card.completed { border-left: 6px solid #10b981; }
        .chapter-card.inprogress { border-left: 6px solid #f59e0b; }
        .chapter-card.notstarted { border-left: 6px solid #e5e7eb; }

        .chapter-num {
            width: clamp(45px, 6vw, 60px); height: clamp(45px, 6vw, 60px); border-radius: 18px;
            display: flex; align-items: center; justify-content: center;
            font-size: clamp(24px, 3.5vw, 32px); flex-shrink: 0; font-weight: 900;
            background: #f1f5f9; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .chapter-info { flex: 1; min-width: 0; }
        .chapter-title { font-size: clamp(16px, 2vw, 20px); font-weight: 800; color: #1f2937; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .chapter-meta  { font-size: clamp(12px, 1.5vw, 15px); color: #6b7280; font-weight: 600; }
        .chapter-status { font-size: clamp(20px, 3vw, 26px); flex-shrink: 0; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.1)); }

        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
            border-top: 1px solid rgba(0,0,0,0.05); display: flex; padding: 8px 0 clamp(10px, 2vw, 16px);
            box-shadow: 0 -4px 20px rgba(0,0,0,0.05); z-index: 100;
        }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 6px; text-decoration: none; transition: all 0.2s; }
        .nav-icon { font-size: clamp(20px, 3vw, 26px); transition: transform 0.2s; }
        .nav-label { font-size: clamp(10px, 1.2vw, 13px); font-weight: 700; color: #94a3b8; }
        .nav-item.active .nav-label { color: #334155; }
        .nav-item.active .nav-icon { transform: translateY(-2px); }

        @media(min-width: 768px) {
            .chapters-list { grid-template-columns: repeat(2, 1fr); max-width: 1000px; margin: 0 auto; }
            .hero { padding: 60px 20px 80px; }
            .progress-card { max-width: 800px; margin: -60px auto 30px; }
            .section-label { max-width: 1000px; margin: 0 auto; padding-left: 20px; }
        }
    </style>'''

subject_configs = {
    'templates/class2/english/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #4f46e5, #7c3aed)'
    },
    'templates/class2/maths/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #16a34a, #22c55e)'
    },
    'templates/class2/evs/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #0ea5e9, #2563eb)'
    },
    'templates/class2/kannada/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #f97316, #ea580c)'
    },
    'templates/class2/maths_kn/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #16a34a, #22c55e)'
    },
    'templates/class2/evs_kn/index.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #0ea5e9, #2563eb)'
    }
}

for filepath, vars_dict in subject_configs.items():
    if not os.path.exists(filepath):
        print(f"File {filepath} not found, skipping...")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace style block and any existing link tags that might be duplicate
    content = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Baloo\+Tamma\+2.*?>', '', content, flags=re.DOTALL)
    content = re.sub(r'<link href="https://fonts.googleapis.com/css2\?family=Outfit.*?>', '', content, flags=re.DOTALL)
    new_content = re.sub(r'<style>.*?</style>', unified_subject_css, content, flags=re.DOTALL)
    
    # Inject CSS variables into body
    style_str = f" style='--bg-gradient:{vars_dict['--bg-gradient']}; --theme-gradient:{vars_dict['--theme-gradient']};'"
    if "style='--bg-gradient" in new_content:
        new_content = re.sub(r'style=\'--bg-gradient:.*?;\'', style_str, new_content)
    else:
        new_content = re.sub(r'<body([^>]*)>', r'<body\1' + style_str + '>', new_content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {filepath}')
