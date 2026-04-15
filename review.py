import sys
import os
import re
import json
import urllib.request
from pathlib import Path
import html as htmllib

EXTENSIONS = [".py", ".cpp", ".ino", ".js", ".ts", ".html", ".css"]

def get_code_files(target):
    path = Path(target)
    if path.is_file():
        return [path]
    files = []
    for ext in EXTENSIONS:
        for f in path.rglob(f"*{ext}"):
            files.append(f)
    return files

def review_file(filepath):
    with open(filepath, "r", errors="ignore") as f:
        code = f.read()
    if len(code) > 3000:
        code = code[:3000]
    prompt = f"""You are a senior software engineer doing an honest code review. Be direct and realistic. If the code is well-written and functional, say so clearly. Do not invent problems. Only report real significant issues. At the very end of your review, on a new line, write exactly: SCORE: X where X is a number from 0 to 100 representing overall code quality.

Code to review:

{code}"""
    data = json.dumps({
        "model": "codellama",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0
        }
    }).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result.get("response", "").strip()

def extract_score(review_text):
    match = re.search(r'SCORE:\s*(\d+)', review_text)
    if match:
        score = int(match.group(1))
        return min(max(score, 0), 100)
    return 50

def score_color(score):
    if score >= 80:
        return "#22c55e"
    elif score >= 60:
        return "#eab308"
    elif score >= 40:
        return "#f97316"
    else:
        return "#ef4444"

def score_message(score):
    if score >= 90:
        return "🔥 Mükemmel kod — production'a hazır."
    elif score >= 80:
        return "✅ İyi iş, küçük dokunuşlar yeterli."
    elif score >= 60:
        return "⚠️ Fena değil ama biraz düzenleme gerek."
    elif score >= 40:
        return "🛠️ Çalışıyor ama ciddi iyileştirme lazım."
    else:
        return "❌ Baştan yazılması düşünülmeli."

def generate_html(reviews):
    html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>AI Code Review Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #0f1117;
    color: #e0e0e0;
    padding: 40px 20px;
  }
  .container { max-width: 860px; margin: 0 auto; }
  header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 36px;
    border-bottom: 1px solid #2a2a3a;
    padding-bottom: 20px;
  }
  header h1 { font-size: 26px; color: #ffffff; }
  .card {
    background: #1a1d27;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    margin-bottom: 24px;
    overflow: hidden;
  }
  .card-header {
    background: #12151f;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
    border-bottom: 1px solid #2a2d3e;
  }
  .card-header .icon { font-size: 18px; }
  .card-header .filename {
    font-size: 14px;
    font-weight: 600;
    color: #58a6ff;
    word-break: break-all;
  }
  .badge {
    margin-left: auto;
    background: #1f6feb;
    color: white;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
  }
  .score-section {
    padding: 16px 20px 10px;
    border-bottom: 1px solid #2a2d3e;
  }
  .score-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .score-number { font-size: 28px; font-weight: 700; }
  .score-msg { font-size: 13px; color: #aaa; }
  .score-bar-bg {
    background: #2a2d3e;
    border-radius: 8px;
    height: 10px;
    overflow: hidden;
  }
  .score-bar-fill { height: 10px; border-radius: 8px; }
  .card-body {
    padding: 20px;
    font-size: 14px;
    line-height: 1.8;
    color: #cdd5e0;
    white-space: pre-wrap;
  }
  footer {
    text-align: right;
    color: #333;
    font-size: 12px;
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid #1a1d27;
  }
  footer span { color: #58a6ff; }
</style>
</head>
<body>
<div class="container">
  <header>
    <span style="font-size:30px">🔍</span>
    <h1>AI Code Review Report</h1>
    <span style="margin-left:auto; font-size:12px; color:#555;">CodeLlama · Ollama &nbsp;·&nbsp; <span style="color:#58a6ff;">✦ Tugay Akdemir</span></span>
  </header>
"""
    for filepath, review in reviews:
        filename = Path(filepath).name
        ext = Path(filepath).suffix.lower()
        icons = {".py":"🐍", ".js":"🟨", ".ts":"🔷", ".html":"🌐", ".css":"🎨", ".cpp":"⚙️", ".ino":"🔌"}
        icon = icons.get(ext, "📄")
        score = extract_score(review)
        color = score_color(score)
        message = score_message(score)
        clean_review = re.sub(r'SCORE:\s*\d+', '', review).strip()
        safe_review = htmllib.escape(clean_review)
        html += f"""
  <div class="card">
    <div class="card-header">
      <span class="icon">{icon}</span>
      <span class="filename">{filename}</span>
      <span class="badge">{ext}</span>
    </div>
    <div class="score-section">
      <div class="score-top">
        <span class="score-number" style="color:{color};">{score}/100</span>
        <span class="score-msg">{message}</span>
      </div>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width:{score}%; background:{color};"></div>
      </div>
    </div>
    <div class="card-body">{safe_review}</div>
  </div>
"""
    html += """
  <footer>built with ️ &nbsp;·&nbsp; <span>✦ Tugay Akdemir</span></footer>
</div></body></html>"""
    return html

def main():
    if len(sys.argv) < 2:
        print("Kullanim: python3 review.py <dosya_veya_klasor>")
        sys.exit(1)
    target = sys.argv[1]
    print(f"Taranıyor: {target}")
    files = get_code_files(target)
    if not files:
        print("Desteklenen kod dosyası bulunamadı.")
        sys.exit(1)
    print(f"{len(files)} dosya bulundu.")
    reviews = []
    for i, f in enumerate(files):
        print(f"[{i+1}/{len(files)}] İnceleniyor: {f.name}")
        review = review_file(f)
        reviews.append((str(f), review))
    html = generate_html(reviews)
    output = os.path.join(os.path.expanduser("~"), "code-reviewer", "report.html")
    with open(output, "w") as out:
        out.write(html)
    print(f"\nRapor hazır: {output}")
    os.system(f"open '{output}'")

if __name__ == "__main__":
    main()
