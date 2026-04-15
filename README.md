# 🔍 AI Code Review Tool

Local AI-powered code reviewer using CodeLlama + Ollama. No API key, no internet — runs entirely on your machine.

## Features
- Supports `.py`, `.cpp`, `.ino`, `.js`, `.ts`, `.html`, `.css`
- Quality score (0-100) with color-coded progress bar
- Honest, realistic feedback — no invented issues
- Clean dark mode HTML report
- Works on a single file or entire folder

## Requirements
- [Ollama](https://ollama.com) installed
- CodeLlama model: `ollama pull codellama`
- Python 3

## Usage
```bash
python3 review.py <file_or_folder>
```

## Example
```bash
python3 review.py ~/my-project
python3 review.py ~/my-project/main.py
```

Report opens automatically in your browser.

---
Built by [Tugay Akdemir](https://www.linkedin.com/in/tugay-akdemir/)
