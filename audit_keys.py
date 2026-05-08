import re, os

save_data = {}
for root, dirs, files in os.walk('templates'):
    for f in files:
        if not f.endswith('.html'): continue
        fp = os.path.join(root, f)
        content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
        m = re.search(r"grade:\s*'([^']+)'.*?subject:\s*'([^']+)'.*?lesson:\s*'([^']+)'", content)
        if m:
            g, s, l = m.groups()
            save_data.setdefault(f'{g}/{s}', set()).add(l)

for k in sorted(save_data.keys()):
    vals = sorted(save_data[k])
    print(f'{k} ({len(vals)} lessons): {vals}')
