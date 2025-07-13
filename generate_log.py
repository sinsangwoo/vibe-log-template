import os
import datetime
import subprocess

def get_committed_files():
    """Git 커밋된 파일 목록을 가져옵니다."""
    try:
        # 마지막 커밋의 변경된 파일 목록을 가져옴
        command = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        files = result.stdout.strip().split('\n')
        return [f for f in files if f] # 빈 문자열 제거
    except subprocess.CalledProcessError as e:
        print(f"Git 명령어 실행 중 오류 발생: {e}")
        print(f"Stderr: {e.stderr}")
        return []
    except Exception as e:
        print(f"커밋된 파일 목록을 가져오는 중 오류 발생: {e}")
        return []

def generate_log_entry(committed_files):
    """학습 로그 엔트리를 생성합니다."""
    today = datetime.date.today()
    log_date = today.strftime("%Y-%m-%d")

    # 커밋 메시지 가져오기
    try:
        commit_message_cmd = ["git", "log", "-1", "--pretty=%B"]
        commit_message_result = subprocess.run(commit_message_cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
        commit_message = commit_message_result.stdout.strip().split('\n')[0] # 첫 줄만 사용
    except Exception:
        commit_message = "No commit message found."

    log_content = f"## {log_date} 학습 일지\n\n"
    log_content += f"### 커밋 메시지: {commit_message}\n\n"
    log_content += "### 변경된 파일 목록:\n"
    if committed_files:
        for file in committed_files:
            log_content += f"- `{file}`\n"
    else:
        log_content += "- 변경된 파일 없음.\n"

    log_content += "\n--- (추가 학습 내용 여기에 기록) ---\n\n"

    return log_content, log_date

def save_log_to_file(log_content, log_date):
    """생성된 로그를 파일로 저장하고 README에 링크를 업데이트합니다."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir) # logs 디렉토리가 없으면 생성

    log_filepath = os.path.join(log_dir, f"log_{log_date}.md")
    try:
        with open(log_filepath, "a", encoding='utf-8') as f:
            f.write(log_content)
        print(f"로그가 {log_filepath} 에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"로그 파일을 저장하는 중 오류 발생: {e}")

    # README 업데이트 (간단한 예시)
    readme_path = "README.md"
    try:
        with open(readme_path, "r+", encoding='utf-8') as f:
            readme_lines = f.readlines()
            f.seek(0) # 파일 포인터를 맨 앞으로 이동

            # 이미 링크가 있는지 확인
            log_link_line = f"- [{log_date} 학습 일지](logs/log_{log_date}.md)\n"

            # 로그 링크 섹션이 있다면 그 밑에 추가, 없다면 새로 추가
            updated = False
            for i, line in enumerate(readme_lines):
                if "## 학습 로그" in line: # 학습 로그 섹션 가정
                    if log_link_line not in readme_lines: # 중복 방지
                        readme_lines.insert(i + 1, log_link_line)
                        updated = True
                    break

            if not updated and log_link_line not in readme_lines: # 섹션이 없거나 추가되지 않은 경우 맨 뒤에 추가
                if not any("## 학습 로그" in line for line in readme_lines):
                    readme_lines.append("\n## 학습 로그\n")
                if log_link_line not in readme_lines:
                    readme_lines.append(log_link_line)

            f.writelines(readme_lines)
        print(f"README.md가 업데이트되었습니다.")
    except Exception as e:
        print(f"README.md를 업데이트하는 중 오류 발생: {e}")

if __name__ == "__main__":
    committed_files = get_committed_files()
    log_content, log_date = generate_log_entry(committed_files)
    save_log_to_file(log_content, log_date)