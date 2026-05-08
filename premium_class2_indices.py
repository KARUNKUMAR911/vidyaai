import os
import re

# Premium Subject Index Template
premium_index_css = '''    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&family=Noto+Sans+Kannada:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body {
            font-family: 'Noto Sans Kannada', 'Outfit', sans-serif;
            background: #f8fafc;
            min-height: 100vh; overflow-x: hidden; position: relative; padding-bottom: 100px;
            color: #1e293b;
        }

        /* DYNAMIC BACKGROUND */
        .bg-blob {
            position: fixed; width: clamp(200px, 40vw, 500px); height: clamp(200px, 40vw, 500px); border-radius: 50%;
            filter: blur(80px); z-index: -1; opacity: 0.2; animation: float 15s infinite alternate;
        }
        .blob-1 { top: -10%; right: -10%; background: var(--accent, #6366f1); }
        .blob-2 { bottom: -10%; left: -10%; background: #22d3ee; }
        @keyframes float { 
            0% { transform: translate(0,0) scale(1); } 
            100% { transform: translate(10%, 20%) scale(1.1); } 
        }

        .navbar {
            background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            padding: 16px 24px; display: flex; align-items: center; justify-content: space-between;
            position: sticky; top: 0; z-index: 500;
            box-shadow: 0 4px 30px rgba(0,0,0,0.03); border-bottom: 1px solid rgba(255,255,255,0.8);
        }
        .navbar-logo { font-size: 24px; font-weight: 900; background: var(--theme-gradient, #334155); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; font-family: 'Outfit', sans-serif; }
        .home-link { text-decoration: none; font-size: 20px; background: white; padding: 8px; border-radius: 50%; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }

        .hero {
            background: var(--theme-gradient, #334155);
            padding: clamp(40px, 8vw, 70px) 24px clamp(60px, 10vw, 90px);
            text-align: center; color: white; position: relative; overflow: hidden;
            border-bottom-left-radius: 50px; border-bottom-right-radius: 50px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        }
        .hero h1 { font-size: clamp(28px, 5vw, 42px); font-weight: 900; margin-bottom: 8px; }
        .hero p { font-size: 16px; opacity: 0.9; font-weight: 600; }

        .prog-card {
            background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px);
            margin: -40px 24px 30px; border-radius: 35px; padding: 24px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.08); border: 1px solid rgba(255,255,255,1);
            position: relative; z-index: 100;
        }
        .prog-bar { background: #f1f5f9; height: 14px; border-radius: 50px; overflow: hidden; }
        .prog-fill { background: var(--theme-gradient, #334155); height: 100%; border-radius: 50px; width: 0%; transition: width 1s ease; }

        .chapters-list { padding: 0 20px 50px; display: flex; flex-direction: column; gap: 16px; }
        
        .chapter-card {
            background: white; border-radius: 30px; padding: 20px;
            text-decoration: none; display: flex; align-items: center; gap: 16px;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(0,0,0,0.02); box-shadow: 0 8px 25px rgba(0,0,0,0.04);
        }
        .chapter-card:hover { transform: translateX(10px) scale(1.02); box-shadow: 0 15px 35px rgba(0,0,0,0.08); border-color: var(--accent); }
        
        .ch-num { 
            width: 50px; height: 50px; border-radius: 18px; 
            background: var(--theme-gradient, #f1f5f9); color: white;
            display: flex; align-items: center; justify-content: center;
            font-weight: 900; font-size: 20px; flex-shrink: 0; font-family: 'Outfit', sans-serif;
        }
        .ch-info { flex: 1; min-width: 0; }
        .ch-title { font-size: 17px; font-weight: 800; color: #1e293b; margin-bottom: 2px; }
        .ch-sub { font-size: 13px; color: #64748b; font-weight: 600; }
        
        .ch-status { font-size: 22px; width: 40px; text-align: center; }

        @media(min-width: 768px) {
            .chapters-list { max-width: 800px; margin: 0 auto; }
            .prog-card { max-width: 600px; margin: -40px auto 40px; }
        }
    </style>'''

def modernize_index(filepath, accent, grad):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    css = premium_index_css.replace('var(--accent, #6366f1)', accent).replace('var(--theme-gradient, #334155)', grad)
    content = re.sub(r'<style>.*?</style>', css, content, flags=re.DOTALL)
    
    if 'bg-blob' not in content:
        content = content.replace('<body', f'<body style="--accent:{accent}; --theme-gradient:{grad};"><div class="bg-blob blob-1"></div><div class="bg-blob blob-2"></div><body')
        content = content.replace('<body<body', '<body')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

configs = {
    'templates/class2/english/index.html': ('#ec4899', 'linear-gradient(135deg, #ec4899, #db2777)'),
    'templates/class2/maths/index.html': ('#3b82f6', 'linear-gradient(135deg, #3b82f6, #2563eb)'),
    'templates/class2/evs/index.html': ('#10b981', 'linear-gradient(135deg, #10b981, #059669)'),
    'templates/class2/kannada/index.html': ('#f59e0b', 'linear-gradient(135deg, #f59e0b, #d97706)'),
    'templates/class2/maths_kn/index.html': ('#3b82f6', 'linear-gradient(135deg, #3b82f6, #2563eb)'),
    'templates/class2/evs_kn/index.html': ('#10b981', 'linear-gradient(135deg, #10b981, #059669)'),
}

for path, (accent, grad) in configs.items():
    if os.path.exists(path):
        modernize_index(path, accent, grad)
        print(f"Modernized {path}")
