import os
import sys
import argparse
from dotenv import load_dotenv

# 소스 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "02_source"))

from utils import validate_date, ErrorHandler, get_cached_data, save_json_data
from llm_client import LLMClient
from map_client import MapClient
from report_generator import save_report

# dotenv 로드
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(dotenv_path=env_path)

def print_api_guide():
    """
    API 키 미설정 시 출력할 가이드 메시지입니다.
    """
    guide = """
================================================================================
[오류] 필수 API 키가 설정되지 않았습니다! (Google Gemini & Naver Local API)
================================================================================
프로그램을 실행하려면 API 키 설정이 필요합니다. 아래 가이드를 따라주세요.

1. 프로젝트 루트 디렉터리에 있는 `.env.template` 파일을 복사하여 `.env` 파일을 만듭니다.
2. 생성한 `.env` 파일 안에 다음 API 키 정보를 기입해 주세요.

   # Google Gemini API 키 (필수)
   GEMINI_API_KEY=your_gemini_api_key_here

   # Naver Client ID & Client Secret (필수)
   NAVER_CLIENT_ID=your_naver_client_id_here
   NAVER_CLIENT_SECRET=your_naver_client_secret_here

3. 저장 후 다시 명령어를 실행해 주세요.
================================================================================
"""
    print(guide)

def main():
    # CLI 인자 설정
    parser = argparse.ArgumentParser(description="날짜 입력 기반 국내 여행지 추천 및 맛집 검색 CLI 프로그램 (Gemini & Naver 연동)")
    parser.add_argument(
        "--date", "-date",
        type=str,
        required=False,
        help="여행할 날짜 (형식: YYYY-MM-DD)"
    )
    
    args = parser.parse_args()
    date_str = args.date
    interactive_mode = False
    
    # 실행할 때 날짜를 지정하지 않았다면, 화면에서 날짜를 직접 입력받도록 작동
    if not date_str:
        interactive_mode = True
        print("\n=== Travel Planner 대화형 실행 모드 ===")
        date_str = input("여행할 날짜를 입력해 주세요 (형식: YYYY-MM-DD, 예: 2026-03-15): ").strip()
    
    # 입력된 문자열에서 YYYY-MM-DD 날짜 형식만 자동으로 추출 (예외 입력 보정)
    import re
    if date_str:
        match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
        if match:
            date_str = match.group(0)
    
    # 1. 날짜 검증
    if not validate_date(date_str):
        print(f"\n[오류] 입력한 날짜 '{date_str}'는 유효하지 않은 날짜 형식이거나 올바르지 않습니다.")
        print("사용법: python travel_planner.py --date \"YYYY-MM-DD\"  (예: 2026-03-15)\n")
        if interactive_mode:
            input("종료하려면 엔터 키를 누르세요...")
        sys.exit(1)
        
    # 2. 에러 핸들러 및 API 클라이언트 초기화
    error_handler = ErrorHandler()
    llm_client = LLMClient()
    map_client = MapClient()
    
    # API 키 검증 (Gemini와 Naver 둘 다 키가 설정되어 있어야 완벽한 기능이 작동함)
    if not llm_client.has_valid_key() or not map_client.has_valid_key():
        print_api_guide()
        sys.exit(1)
        
    print(f"\n>>> {date_str} 날짜의 여행 계획 생성을 시작합니다. (LLM: Gemini / Map: Naver)")

    # 3. 결과 캐싱 확인 (보너스 과제)
    cached_data = get_cached_data(date_str)
    
    if cached_data:
        print(f"  [캐시 감지] 기존에 실행된 {date_str}의 원본 데이터가 존재합니다. API 호출을 건너뜁니다.")
        recommendation = {
            "recommended_cities": cached_data.get("recommended_cities", []),
            "recommended_city": cached_data.get("recommended_city", ""),
            "weather": cached_data.get("weather", ""),
            "events": cached_data.get("events", []),
            "reason": cached_data.get("reason", "")
        }
        places_data = cached_data.get("restaurants", {})
        # 캐싱된 에러 불러오기
        for err in cached_data.get("errors", []):
            error_handler.add_error(err["step"], err["type"], err["message"])
            
        print("  [3/3] 최종 리포트 재생성 중(LLM)...")
        report_content = llm_client.generate_report(date_str, recommendation, places_data, error_handler)
    else:
        # 4. 1차 추천 생성 (LLM)
        print("  [1/3] 1차 추천 생성 중(LLM)...")
        recommendation = llm_client.get_recommendation(date_str, error_handler)
        
        if not recommendation:
            print("    [오류] LLM 1차 추천 생성에 실패했습니다. 기본 값으로 계속 진행합니다.")
            recommendation = {
                "recommended_cities": ["서울"],
                "recommended_city": "서울",
                "weather": "날씨 정보를 불러올 수 없습니다.",
                "events": [],
                "reason": "추천 결과를 정상적으로 불러오지 못해 임시로 기본 지역을 설정했습니다."
            }
            
        cities = recommendation.get("recommended_cities", [recommendation.get("recommended_city")])
        print(f"    - 추천된 지역: {', '.join(cities)}")
        
        # 5. 맛집 검색 (지도 API)
        print("  [2/3] 맛집 검색 중(지도/장소 API)...")
        places_data = {}
        for city in cities:
            print(f"    - '{city}' 맛집 검색 중...")
            restaurants = map_client.search_restaurants(city, error_handler, limit=5)
            places_data[city] = restaurants
            print(f"      ㄴ {len(restaurants)}곳 검색 완료")
            
        # 6. 최종 리포트 생성 (LLM)
        print("  [3/3] 최종 리포트 생성 중(LLM)...")
        report_content = llm_client.generate_report(date_str, recommendation, places_data, error_handler)

    # 7. 리포트 저장 및 결과 출력
    if not report_content:
        report_content = f"""# {date_str} 국내 여행 추천 리포트
## 추천 지역
{', '.join(recommendation.get('recommended_cities', []))}

## 추천 이유
{recommendation.get('reason')}

## 날씨 요약
{recommendation.get('weather')}

## 행사/축제
{', '.join(recommendation.get('events', [])) if recommendation.get('events') else '정보 없음'}

## 맛집 추천
데이터 없음 (리포트 생성 오류)

## 오류 요약(errors)
- 리포트 생성 단계에서 API 에러가 발생하여 마크다운이 간이 빌드되었습니다.
"""
    
    # 원본 데이터 저장 준비
    raw_data = {
        "recommended_cities": recommendation.get("recommended_cities"),
        "recommended_city": recommendation.get("recommended_city"),
        "weather": recommendation.get("weather"),
        "events": recommendation.get("events"),
        "reason": recommendation.get("reason"),
        "restaurants": places_data,
        "errors": error_handler.get_errors()
    }
    
    # 파일 저장
    json_path = save_json_data(date_str, raw_data)
    md_path = save_report(date_str, report_content)
    
    # CLI에 최종 리포트 마크다운 출력
    print("\n" + "="*80)
    print("📄 생성된 최종 여행 리포트 내용")
    print("="*80)
    print(report_content)
    print("="*80)
    
    print(f"\n>>> 완료! 아래 결과 파일을 확인하세요.")
    print(f"  - 원본 데이터 JSON: {json_path}")
    print(f"  - 최종 리포트 Markdown: {md_path}\n")
    
    if interactive_mode:
        print("="*80)
        input("프로그램이 완료되었습니다. 창을 닫으려면 엔터 키를 누르세요...")

if __name__ == "__main__":
    main()
