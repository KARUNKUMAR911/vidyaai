
with open('C:/vidyaai/app.py') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'class1_dashboard_kannada' in line and 'def' in line:
        print(f'Line {i}: {line.strip()}')

