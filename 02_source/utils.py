import os
import json
from datetime import datetime

def validate_date(date_str: str) -> bool:
    """
    날짜 문자열이 YYYY-MM-DD 형식에 맞는지와 실제 존재하는 유효한 날짜인지 검증합니다.
    """
    try:
        # 형식 및 날짜 유효성 동시 검증
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

class ErrorHandler:
    """
    프로그램 실행 중 발생하는 오류들을 내부적으로 누적하고 관리하는 클래스입니다.
    """
    def __init__(self):
        self.errors = []

    def add_error(self, step: str, error_type: str, message: str):
        """
        오류를 추가합니다.
        - step: 오류 발생 단계 (예: 'llm_recommendation', 'place_search', 'report_generation')
        - error_type: 에러의 유형 (예: 'AUTH_ERROR', 'PARSE_ERROR', 'EMPTY_RESULT', 'API_ERROR')
        - message: 세부 에러 메시지
        """
        error_entry = {
            "step": step,
            "type": error_type,
            "message": message
        }
        self.errors.append(error_entry)

    def get_errors(self) -> list:
        """
        누적된 에러 목록을 반환합니다.
        """
        return self.errors

    def has_errors(self) -> bool:
        """
        기록된 에러가 있는지 여부를 반환합니다.
        """
        return len(self.errors) > 0


def get_cached_data(date_str: str, results_dir: str = "results") -> dict | None:
    """
    동일한 날짜로 저장된 원본 JSON 캐시 데이터가 있는지 확인하고, 존재하면 데이터를 반환합니다.
    """
    cache_path = os.path.join(results_dir, f"{date_str}_data.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # 캐시를 읽다가 에러가 나면 캐시가 없는 것으로 간주하고 새로 요청하도록 함
            return None
    return None

def save_json_data(date_str: str, data: dict, results_dir: str = "results") -> str:
    """
    수집 및 파싱된 원본 데이터를 JSON 파일로 저장합니다.
    """
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)
    
    file_path = os.path.join(results_dir, f"{date_str}_data.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    return file_path
