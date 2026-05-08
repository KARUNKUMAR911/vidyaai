import re, os

with open('app.py','r', encoding='utf-8') as f:
    code = f.read()

# Find all render_template calls
templates = re.findall(r"render_template\(['\"]([^'\"]+)['\"]", code)
missing = []
for t in templates:
    path = os.path.join('templates', t)
    if not os.path.exists(path):
        missing.append(t)

print(f'Total render_template calls: {len(templates)}')
print(f'Missing templates: {len(missing)}')
for m in missing:
    print(f'  MISSING: {m}')

# Find templates with no route
all_htmls = []
for root, dirs, files in os.walk('templates'):
    for f in files:
        if f.endswith('.html'):
            rel = os.path.relpath(os.path.join(root, f), 'templates').replace('\\','/')
            all_htmls.append(rel)

routed = set(templates)
# Also check f-string templates
fstring_templates = re.findall(r"render_template\(f['\"]([^'\"]+)['\"]", code)

unrouted = [h for h in all_htmls if h not in routed and 'index.html' not in h and 'dashboard' not in h]

# Check for duplicate routes
routes = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"]", code)
from collections import Counter
dupes = {k:v for k,v in Counter(routes).items() if v > 1}
if dupes:
    print(f'\nDuplicate routes: {len(dupes)}')
    for r, c in dupes.items():
        print(f'  DUPE ({c}x): {r}')

# Check for auth-unprotected API routes
api_routes = re.findall(r"@app\.route\(['\"](/api/[^'\"]+)['\"]", code)
print(f'\nAPI endpoints: {len(api_routes)}')

# Check lesson key mismatches
# What the HTML files save vs what the backend expects
print(f'\n--- Lesson key analysis ---')
for line_no, line in enumerate(code.split('\n'), 1):
    if 'GRADE' in line and 'LESSONS' in line and '=' in line and 'lessons' not in line.lower().split('=')[0].lower().strip()[-8:]:
        pass

# Check for SQLite pool options on PostgreSQL
if 'pool_size' in code:
    print('\nWARNING: pool_size/max_overflow set in SQLALCHEMY_ENGINE_OPTIONS.')
    print('  These work with PostgreSQL but SQLite ignores pool settings.')
    print('  Consider gating these behind DATABASE_URL check.')
