# ✅ generate_log.py
# 자동 커밋 로그 -> Markdown 학습일지 생성 + README 자동 업데이트
import os
import subprocess
import datetime
import re
import chardet

LOG_DIR = "logs"
README_PATH = "README.md"


def get_latest_commit_message():
    result = subprocess.run(["git", "log", "-1", "--pretty=%B"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def get_changed_files():
    result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip().split("\n") if result.returncode == 0 else []


def extract_tags(commit_msg, changed_files):
    tags = set()
    # 기본 규칙 기반 추출
    if "README" in commit_msg.upper():
        tags.add("📘 문서")
    if "fix" in commit_msg.lower() or "bug" in commit_msg.lower():
        tags.add("🛠 버그수정")
    if any(f.endswith(".py") for f in changed_files):
        tags.add("💻 코드")
    if "test" in commit_msg.lower():
        tags.add("✅ 테스트")
    return tags


def detect_encoding(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
            result = chardet.detect(raw)
            return result['encoding']
    except:
        return None


def update_readme_log_links():
    try:
        encoding = detect_encoding(README_PATH) or 'utf-8'
        with open(README_PATH, 'r', encoding=encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        print("❗ README 인코딩 오류. UTF-8로 강제 시도 중...")
        with open(README_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_path = f"logs/log_{today}.md"
    log_link = f"- [{today} 학습기록]({log_path})"

    # 기존 링크 있으면 중복 방지
    if log_link not in content:
        content += f"\n{log_link}\n"
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(content)
        print("📎 README에 링크 추가 완료")


def create_log():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    log_filename = f"log_{today}.md"
    log_path = os.path.join(LOG_DIR, log_filename)

    commit_msg = get_latest_commit_message()
    changed_files = get_changed_files()
    tags = extract_tags(commit_msg, changed_files)

    log_content = f"""
# 📅 {today} 커밋 기록

**커밋 메시지**: {commit_msg}

**변경된 파일 목록**:
{chr(10).join(f'- {file}' for file in changed_files)}

**자동 태그**: {' '.join(tags) if tags else '없음'}
"""

    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content.strip())

    print(f"✅ 로그 파일 생성 완료: {log_path}")
    update_readme_log_links()


if __name__ == "__main__":
    create_log()
