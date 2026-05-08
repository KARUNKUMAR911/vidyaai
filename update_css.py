import re
import os

unified_css = '''    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }

        body {
            background: var(--bg-gradient, linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%));
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            padding-bottom: 70px;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
            padding: 14px 20px; display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border-bottom: 1px solid rgba(255,255,255,0.8);
            position: sticky; top: 0; z-index: 100;
        }
        .navbar-left { display: flex; align-items: center; gap: 12px; }
        .navbar-logo { font-size: 22px; font-weight: 900; background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .navbar-grade { background: rgba(255,255,255,0.8); color: #334155; padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; border: 1px solid rgba(0,0,0,0.1); }
        .navbar-right { display: flex; align-items: center; gap: 10px; }
        .stars-badge { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: white; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 700; box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3); display: flex; align-items: center; gap: 5px; }
        .home-btn { background: white; color: #334155; padding: 7px 14px; border-radius: 20px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid rgba(0,0,0,0.1); transition: all 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }

        .hero {
            background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155));
            backdrop-filter: blur(8px); border-bottom-left-radius: 30px; border-bottom-right-radius: 30px;
            padding: 30px 20px 50px; text-align: center; color: white;
            box-shadow: 0 10px 30px rgba(0,0,0, 0.15); margin-bottom: 30px;
        }
        .hero-avatar { font-size: 70px; margin-bottom: 10px; filter: drop-shadow(0 4px 10px rgba(0,0,0,0.1)); }
        .hero h2 { font-size: 28px; font-weight: 900; margin-bottom: 4px; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .hero p  { font-size: 16px; opacity: 0.95; font-weight: 600; }

        .progress-section {
            background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            margin: -40px 16px 20px; border-radius: 24px; padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,0.9);
            position: relative; z-index: 10;
        }
        .progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .progress-title { font-size: 16px; font-weight: 800; color: #1f2937; }
        .progress-count { font-size: 14px; font-weight: 600; color: #fff; background: var(--theme-gradient, #475569); padding: 4px 12px; border-radius: 12px; }
        .progress-bar { background: rgba(0,0,0,0.05); border-radius: 12px; height: 14px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }
        .progress-fill { background: var(--theme-gradient, #475569); height: 100%; border-radius: 12px; width: 0%; transition: width 1s ease; }

        .challenge-card {
            margin: 0 16px 20px; background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155));
            border-radius: 24px; padding: 18px 20px; display: flex; align-items: center; gap: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15); cursor: pointer; transition: transform 0.2s; text-decoration: none;
        }
        .challenge-icon { font-size: 44px; flex-shrink: 0; }
        .challenge-text h3 { font-size: 16px; font-weight: 900; color: white; margin-bottom: 3px; }
        .challenge-text p  { font-size: 13px; color: rgba(255,255,255,0.85); font-weight: 600; }
        .challenge-arrow { margin-left: auto; font-size: 22px; color: white; flex-shrink: 0; }

        .section-title { padding: 10px 20px 15px; font-size: 22px; font-weight: 900; color: #111827; display: flex; align-items: center; gap: 10px; }

        .subjects-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding: 0 16px 40px; }

        .subject-card {
            border-radius: 28px; padding: 25px 16px; text-align: center; cursor: pointer;
            transition: all 0.3s ease; position: relative; overflow: hidden;
            text-decoration: none; display: block; box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        }
        .subject-card::before {
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%);
            pointer-events: none; z-index: 1;
        }
        .subject-card > * { position: relative; z-index: 2; }
        .card-icon { font-size: 60px; margin-bottom: 12px; display: block; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.2)); transition: transform 0.3s; }
        .card-title { font-size: 18px; font-weight: 900; color: white; text-shadow: 0 2px 8px rgba(0,0,0,0.3); margin-bottom: 4px; }
        .card-sub   { font-size: 13px; color: rgba(255,255,255,0.9); font-weight: 600; }

        .card-badge {
            position: absolute; top: 12px; left: 12px; background: rgba(255,255,255,0.9);
            color: #4b5563; font-size: 11px; font-weight: 800; padding: 4px 10px;
            border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 3;
        }

        .card-progress {
            position: absolute; top: 12px; right: 12px; background: rgba(0,0,0,0.2);
            color: white; font-size: 11px; font-weight: 800; padding: 4px 10px;
            border-radius: 12px; z-index: 3; backdrop-filter: blur(5px);
        }

        /* Lock overlay */
        .card-lock {
            position: absolute; inset: 0; background: rgba(0,0,0,0.35); border-radius: 28px;
            display: flex; align-items: center; justify-content: center; z-index: 10;
        }
        .card-lock-icon { font-size: 32px; filter: drop-shadow(0 2px 10px rgba(0,0,0,0.5)); }

        .card-1, .c1  { background: linear-gradient(135deg, #ff7eb3, #ff758c); }
        .card-2, .c2  { background: linear-gradient(135deg, #4facfe, #00f2fe); }
        .card-3, .c3  { background: linear-gradient(135deg, #f6d365, #fda085); }
        .card-4, .c4  { background: linear-gradient(135deg, #43e97b, #38f9d7); }
        .card-5, .c5  { background: linear-gradient(135deg, #a18cd1, #fbc2eb); }
        .card-6, .c6  { background: linear-gradient(135deg, #2af598, #009efd); }
        .card-7, .c7  { background: linear-gradient(135deg, #ff9a9e, #fecfef); }
        .card-8, .c8  { background: linear-gradient(135deg, #667eea, #764ba2); }
        .card-9, .c9  { background: linear-gradient(135deg, #f6d365, #ffb347); }
        .card-10, .c10 { background: linear-gradient(135deg, #89f7fe, #66a6ff); }
        .card-11, .c11 { background: linear-gradient(135deg, #ff0844, #ffb199); }
        .card-12, .c12 { background: linear-gradient(135deg, #4facfe, #00f2fe); }

        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(255, 255, 255, 0.95);
            border-top: 1px solid rgba(0,0,0,0.05); display: flex; padding: 8px 0 16px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.05); z-index: 50;
        }
        .nav-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 6px; text-decoration: none; transition: all 0.2s; }
        .nav-icon { font-size: 22px; transition: transform 0.2s; }
        .nav-label { font-size: 11px; font-weight: 700; color: #6b7280; }
        .nav-item.active .nav-label { color: #334155; }
        
        .progress-bar-card {
            height: 6px; background: rgba(255,255,255,0.3); border-radius: 4px;
            margin-top: 10px; overflow: hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
        }
        .progress-bar-fill {
            height: 100%; background: white; border-radius: 4px; width: 0%; transition: width 0.5s;
        }

        .panel { display:none; }
        .panel.active { display:block; }
        .detail-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px; padding: 18px 20px; margin: 0 16px 16px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.9);
        }
        .detail-row { display:flex; align-items:center; gap:16px; }
        .detail-emoji { font-size: 36px; width: 44px; text-align:center; flex-shrink:0; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1)); }
        .detail-main { flex:1; min-width:0; }
        .detail-title { font-size: 16px; font-weight: 900; color:#111827; }
        .detail-sub { font-size: 13px; color:#6b7280; font-weight:700; margin-top: 4px; }
        .detail-right { text-align:right; flex-shrink:0; }
        .detail-pct { font-size: 14px; font-weight: 900; color:#fff; background: var(--theme-gradient, #475569); padding: 4px 10px; border-radius: 12px; }
        .detail-stars { font-size: 13px; font-weight: 800; color:#f59e0b; margin-top: 6px; }
        .detail-actions { margin-top: 14px; display:flex; gap:12px; }
        .mini-btn {
            flex:1; border: none; border-radius: 16px; padding: 12px 16px;
            font-size: 13px; font-weight: 800; cursor: pointer; text-decoration: none;
            display: inline-flex; align-items: center; justify-content: center; gap: 8px; transition: all 0.2s;
        }
        .mini-btn.primary { background: var(--theme-gradient, linear-gradient(135deg, #475569, #334155)); color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .mini-btn.ghost { background: #f1f5f9; color: #475569; }
        
        .big-stars {
            margin: 0 16px 20px; background: linear-gradient(135deg, #f59e0b, #d97706);
            border-radius: 24px; padding: 25px 20px; color: white; text-align: center;
            box-shadow: 0 10px 30px rgba(245, 158, 11, 0.3); position: relative; overflow: hidden;
        }
        .big-stars .label { font-size: 14px; font-weight: 900; opacity: 0.95; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
        .big-stars .value { font-size: 48px; font-weight: 900; margin-top: 4px; line-height: 1; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); }
        .big-stars .hint { font-size: 14px; opacity: 0.95; margin-top: 12px; font-weight: 700; background: rgba(0,0,0,0.1); display: inline-block; padding: 6px 16px; border-radius: 20px; }

        @media(min-width: 768px) {
            .subjects-grid { grid-template-columns: repeat(4, 1fr); max-width: 1000px; margin: 0 auto; }
            .hero { padding: 40px 20px 60px; }
            .progress-section { max-width: 800px; margin: -50px auto 30px; }
            .section-title { max-width: 1000px; margin: 0 auto; justify-content: center; }
        }
    </style>'''

config = {
    'templates/lkg_dashboard.html': {
        '--bg-gradient': 'linear-gradient(135deg, #fff1f2 0%, #fee2e2 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #e11d48, #f43f5e)'
    },
    'templates/ukg_dashboard.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #0ea5e9, #2563eb)'
    },
    'templates/class1/dashboard.html': {
        '--bg-gradient': 'linear-gradient(135deg, #eef2ff 0%, #e0e7ff 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #4f46e5, #7c3aed)'
    },
    'templates/class2/dashboard.html': {
        '--bg-gradient': 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
        '--theme-gradient': 'linear-gradient(135deg, #16a34a, #22c55e)'
    }
}

for filepath, vars_dict in config.items():
    if not os.path.exists(filepath): continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace style block
    new_content = re.sub(r'<style>.*?</style>', unified_css, content, flags=re.DOTALL)
    
    # Check if we already injected styles into body
    if "style='--bg-gradient" not in new_content:
        style_str = f" style='--bg-gradient:{vars_dict['--bg-gradient']}; --theme-gradient:{vars_dict['--theme-gradient']};'"
        new_content = re.sub(r'<body([^>]*)>', r'<body\1' + style_str + '>', new_content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {filepath}')
