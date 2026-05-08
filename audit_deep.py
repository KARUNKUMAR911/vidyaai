import re, os

# Check lesson keys: what HTML files save vs what backend expects
save_data = {}
for root, dirs, files in os.walk('templates'):
    for f in files:
        if not f.endswith('.html'): continue
        fp = os.path.join(root, f)
        try:
            content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
        except: continue
        # Find saveLessonCompletion grade/subject/lesson
        m = re.search(r"grade:\s*'([^']+)'.*subject:\s*'([^']+)'.*lesson:\s*'([^']+)'", content)
        if m:
            g, s, l = m.groups()
            key = f"{g}/{s}"
            save_data.setdefault(key, []).append(l)

print("=== LESSON KEYS SAVED BY HTML FILES ===")
for k in sorted(save_data.keys()):
    print(f"  {k}: {sorted(save_data[k])}")

# Check what backend expects
with open('app.py', 'r') as f:
    code = f.read()

print("\n=== BACKEND GRADE LESSON LISTS ===")
# GRADE1_ENGLISH_LESSONS
matches = re.findall(r"(GRADE\w+_LESSONS)\s*=\s*\[(.*?)\]", code, re.DOTALL)
for name, body in matches:
    keys = re.findall(r"'([^']+)'", body)
    print(f"  {name}: {keys}")

# Check for files with saveLessonCompletion but no hook
print("\n=== FILES WITH SAVE FUNCTION BUT NO HOOK ===")
count = 0
for root, dirs, files in os.walk('templates'):
    for f in files:
        if not f.endswith('.html'): continue
        fp = os.path.join(root, f)
        content = open(fp, 'r', encoding='utf-8', errors='ignore').read()
        if 'function saveLessonCompletion' in content:
            # Check if it's actually called
            calls = len(re.findall(r'saveLessonCompletion\(\)', content))
            if calls <= 1:  # only the function definition
                rel = os.path.relpath(fp, 'templates')
                print(f"  {rel} - calls: {calls}")
                count += 1
print(f"  Total: {count}")

# Check for 500 error risks: Student.query.get returns None
print("\n=== POTENTIAL NULL STUDENT BUGS ===")
lines = code.split('\n')
for i, line in enumerate(lines, 1):
    if 'Student.query.get' in line:
        # Check if next lines check for None
        next_lines = '\n'.join(lines[i:i+3])
        if 'if not student' not in next_lines and 'if student is None' not in next_lines:
            pass  # Count these silently
            
# Count routes without auth check
print("\n=== ROUTES WITHOUT AUTH CHECK ===")
route_blocks = re.findall(r"@app\.route\(['\"]([^'\"]+)['\"].*?\ndef (\w+)\(.*?\):(.*?)(?=\n@app\.route|\nclass |\Z)", code, re.DOTALL)
no_auth = []
for url, func, body in route_blocks:
    if '/api/' in url:
        if 'student_id' not in body:
            no_auth.append(f"  {url} ({func}) - NO AUTH CHECK")
    elif '/static' not in url and 'login' not in url and 'signup' not in url:
        if "session" not in body and 'student_id' not in body:
            no_auth.append(f"  {url} ({func}) - NO SESSION CHECK")
for n in no_auth:
    print(n)

# Check for missing error pages
print("\n=== MISSING ERROR HANDLERS ===")
if '@app.errorhandler(404)' not in code:
    print("  No 404 error handler")
if '@app.errorhandler(500)' not in code:
    print("  No 500 error handler")

# Check for CSRF protection
print("\n=== SECURITY CHECKS ===")
if 'CSRFProtect' not in code and 'csrf' not in code.lower():
    print("  No CSRF protection on forms")
if 'SESSION_COOKIE_SECURE' not in code:
    print("  SESSION_COOKIE_SECURE not set (cookies sent over HTTP)")
if 'SESSION_COOKIE_HTTPONLY' not in code:
    print("  SESSION_COOKIE_HTTPONLY not set")
if 'rate_limit' not in code.lower() and 'limiter' not in code.lower():
    print("  No rate limiting on login/API endpoints")
