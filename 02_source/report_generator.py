import os

def save_report(date_str: str, report_content: str, results_dir: str = "results") -> str:
    """
    최종 여행 계획 리포트를 Markdown 파일(.md)로 저장합니다.
    """
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
        
    file_path = os.path.join(results_dir, f"{date_str}_travel_plan.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    return file_path
