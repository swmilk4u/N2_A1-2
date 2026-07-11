# ✈️ 국내 여행지 추천 및 맛집 검색 프로그램 최종 수행 보고서
**[코디세이 AI 네이티브 과정 과제미션 N2_A1-2 최종 제출물]**

본 보고서는 사용자가 입력한 특정 날짜를 기반으로 **Google Gemini API**와 **Naver Local Search API**를 유기적으로 연동하여 맞춤형 가을/여름 여행 코스 및 맛집 리스트를 생성하는 CLI 프로그램의 최종 구현 성과를 기술합니다.

특히 초보자 관점에서 소스 코드와 핵심 원리를 완벽히 파악하고 동료나 채점관에게 쉽게 설명할 수 있도록 친절한 해설과 코드 조각을 곁들였습니다.

---

## 1. 과제 개요 및 개발 아키텍처

- **수행 목표**: 단일 API 호출의 한계를 넘어, LLM의 구조화된 JSON 출력을 다음 지도 검색 API의 입력으로 결합하는 파이프라인 아키텍처를 구축하고, 예외 복구(Fallback) 및 최적화(Caching)를 만족하는 안정적인 비즈니스 로직을 실현합니다.
- **연동 기술 스택**: 
  - **LLM**: Google Gemini 2.5-flash (google-genai SDK 및 REST API 폴백 탑재)
  - **Local/Map**: Naver Local Search API (지역/장소 검색)
  - **환경 및 유틸**: Python 3.10+, python-dotenv (환경변수 관리), requests (HTTP 통신)

> **💡 [초보자를 위한 쉬운 개념 이해]**
> - **파이프라인(Pipeline)**이란 공장의 '조립 라인'과 같습니다. 첫 번째 기계(Gemini)가 가공한 부품(도시 이름)을 받아서, 두 번째 기계(네이버 지도 검색)가 바로 조립하여 최종 제품(여행 일정표)을 완성해내는 일련의 연결 통로를 의미합니다.

---

## 2. 과제 요구사항별 구현 현황 및 핵심 소스 코드 (Implementation Detail)

### ① CLI 인터페이스 및 입력값 검증 (argparse)
- **구현 내용**: `argparse` 모듈을 적용하여 최상위 진입점 [travel_planner.py](./travel_planner.py)에서 `--date` (또는 `-date`) 인자를 인지하도록 구현했습니다. 날짜 형식이 올바르지 않으면 즉시 올바른 사용법을 안내하고 종료시킵니다.
- **사용자 편의성(UX) 업그레이드**: 사용자가 인자 없이 실행(예: 마우스 더블클릭 등)하면 **대화형(인터랙티브) 실행 모드**로 자동 전환하여 입력을 대기시킵니다. 사용자가 실수로 `--date "2026-03-15"`와 같이 명령어 전체를 적더라도 정규식을 통해 날짜 정보만 영리하게 정제하여 처리하도록 예외 보정 처리를 완료했습니다.

#### 📂 핵심 소스 코드 조각 (Code Snippet)
```python
# travel_planner.py
def main():
    parser = argparse.ArgumentParser(description="날짜 입력 기반 국내 여행지 추천 및 맛집 검색 CLI 프로그램...")
    parser.add_argument("--date", "-date", type=str, required=False, help="여행할 날짜 (형식: YYYY-MM-DD)")
    
    args = parser.parse_args()
    date_str = args.date
    interactive_mode = False
    
    # 인자가 입력되지 않았다면 대화형 입력을 유도 (더블클릭 실행 시 창 닫힘 방지)
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
```

> **💡 [발표 및 설명용 팁]**
> "보통 파이썬 프로그램을 더블클릭하면 명령창이 켜졌다가 에러와 함께 1초 만에 스르륵 닫혀버립니다. 저희 프로그램은 **argparse** 옵션이 비어있으면 스스로 **대화형 모드**로 들어가 입력을 대기하고, 사용자가 입력창에 명령어를 실수로 섞어 써도 **정규식(Regular Expression)**을 돌려 날짜만 쏙 발라내기 때문에 오작동 없이 작동합니다."

---

### ② LLM API 연동 및 JSON 구조화 (1차 추천)
- **구현 내용**: 날짜 정보를 Google Gemini 2.5-flash API로 전달하여 계절에 가장 어울리는 국내 여행 지역, 상세 날씨, 행사, 추천 근거를 JSON 데이터 형식으로 응답받습니다.
- **파싱 실패 방어**: LLM 응답이 올바른 JSON 구조가 아닐 경우, 에러 리스트에 기록하고 프롬프트를 좀 더 엄격하게 수정하여 **최대 1회 재요청(Retry)**하도록 설계했습니다.

#### 📂 핵심 소스 코드 조각 (Code Snippet)
```python
# 02_source/llm_client.py
def get_recommendation(self, date_str: str, error_handler) -> dict | None:
    system_prompt = "You are a professional travel planner. You must respond ONLY with a JSON object."
    prompt = f"""
    날짜: {date_str}
    이 시기에 한국에서 여행하기 좋은 국내 도시 2~3곳을 추천해줘.
    다음 구조의 JSON 객체로 반드시 응답해줘.
    {{
        "recommended_cities": ["도시1", "도시2"],
        "recommended_city": "도시1",
        "weather": "이 시기 날씨 기온 요약",
        "events": ["행사 목록 1~3개"],
        "reason": "추천 근거 3~4문장"
    }}
    """
    # 1차 호출 시도 및 JSON 파싱 실패 시 재시도 진행
    try:
        response_text = self._call_gemini_api(prompt, system_prompt, json_mode=True)
        return json.loads(response_text)  # JSON 문자열을 파이썬 딕셔너리로 즉시 파싱
    except Exception as e:
        # 에러를 누적 기록하고 2차 시도 수행
        error_handler.add_error("llm_recommendation_attempt1", "PARSE_ERROR", str(e))
        # ... (이후 2차 시도 로직)
```

> **💡 [발표 및 설명용 팁]**
> "인공지능(LLM)은 때때로 사람이 말하는 것처럼 '추천해 드리겠습니다!' 같은 미사여구를 붙여 답변을 줍니다. 하지만 프로그램이 이 답변을 받아 다음 지도 API의 입력값으로 쓰려면 컴퓨터가 다룰 수 있는 **구조화된 데이터(JSON)**여야 합니다. 그래서 저희는 Gemini API의 JSON 모드를 강제하고, 만약 형태가 깨지면 즉시 **1회 재요청**하여 견고하게 파싱 오류를 극복합니다."

---

### ③ 지도/장소 검색 API 연동 및 예외 처리 (Naver Local)
- **구현 내용**: 1차 추천 완료된 도시의 이름을 입력으로 받아, 자동으로 `" 맛집"`을 결합(예: "부산 맛집")해 네이버 로컬 검색 API를 통해 식당 명칭, 주소, 카테고리, 좌표, 웹페이지 주소를 최대 5곳 수집합니다.
- **오류 격리 및 우아한 폴백**: API 키 인증 오류(401/403) 또는 검색 결과가 0건일지라도 프로그램이 비정상 종료(Crash)되지 않도록 `try-except`로 오류를 감싸고, 에러 이력을 남긴 채 **"데이터 없음"** 상태로 다음 단계(마크다운 리포트 생성)를 차분히 이어 나갑니다.

#### 📂 핵심 소스 코드 조각 (Code Snippet)
```python
# 02_source/map_client.py
def _search_naver(self, city_name: str, limit: int, error_handler) -> list:
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": self.naver_id,
        "X-Naver-Client-Secret": self.naver_secret
    }
    params = {"query": f"{city_name} 맛집", "display": limit}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code != 200:
            # 401, 403 등의 에러 발생 시 핸들러에 적재하고 프로그램 중단 방지
            error_handler.add_error("place_search", "AUTH_ERROR", f"HTTP {response.status_code}")
            return []  # 빈 리스트 반환하여 다음 단계 진행 유도
            
        data = response.json()
        items = data.get("items", [])
        # ... (이후 데이터 정제 및 반환)
    except Exception as e:
        error_handler.add_error("place_search", "NETWORK_ERROR", str(e))
        return []
```

> **💡 [발표 및 설명용 팁]**
> "외부 지도 API(네이버)는 언제든지 인터넷 상태나 인증키 만료, API 일일 허용량 초과 등으로 멈출 수 있습니다. 이럴 때 프로그램 전체가 멈춰버리는 것은 나쁜 설계입니다. 저희는 이를 **오류 격리(Error Isolation)** 기법을 적용하여, 네이버 API가 실패해도 오류 내용만 일기장(errors)에 적어둔 뒤, 맛집 부분만 '데이터 없음'으로 처리하고 최종 여행 계획 보고서를 끝까지 완성해냅니다."

---

### ④ 결과 캐싱 및 최종 리포트 출력
- **결과 캐싱 (보너스)**: 동일 날짜로 재실행 시, 이미 `results/` 폴더에 캐싱된 `{date}_data.json` 원본 데이터 파일이 있는지 감사합니다. 파일이 존재할 경우 외부 API 호출을 생략해 쿼터를 절약하고 캐싱된 데이터로 1초 만에 마크다운 문서를 신속 재생성합니다.
- **최종 출력**: 마크다운 파일 저장뿐만 아니라 CLI 콘솔 화면에 리포트 본문 전체를 줄무늬 경계선과 함께 출력하여 터미널 상에서 바로 결과를 즐길 수 있게 설계했습니다.

#### 📂 핵심 소스 코드 조각 (Code Snippet)
```python
# travel_planner.py
# 3. 결과 캐싱 확인
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
    # ... (생략된 데이터로 즉시 최종 리포트 빌드)
```

---

## 3. 🔒 API 키 관리 및 보안 준수 사항

본 프로그램은 과제의 보안 및 비공개 수행 규칙에 맞추어 API 키 유출을 원천 차단하고 안전하게 관리하도록 설계 및 구현되었습니다.

1. **환경변수(.env) 기반 관리**: API 키를 소스코드나 문서 내에 하드코딩하지 않고, 외부 설정 파일인 `.env`에 격리하여 로드하도록 구현했습니다.
2. **템플릿 제공 및 가이드 분리**: 협업 및 배포 환경에서의 정보 노출 방지를 위해 실제 키 값을 지운 [.env.template](./.env.template)만을 리포지토리에 제공하여 안전성을 확보했습니다.
3. **Git 추적 배제 (.gitignore)**: 실제 작동에 사용되는 `.env` 파일 및 실행 날짜 기준으로 자동 생성되는 로컬 데이터 폴더(`results/`)가 Git 버전 관리에 절대 수집되지 않도록 최상위 [.gitignore](./.gitignore)에 차단 규칙을 등록하여 우발적인 유출 사고를 방지했습니다.

---

## 📝 [학습 점검 및 과제 미션 보고서]

### Q1. REST API의 요청/응답 구조와 HTTP 메서드(GET/POST)의 차이
- **REST API**는 자원(Resource)을 이름으로 구분하여 해당 자원의 상태를 HTTP 프로토콜 상에서 주고받는 아키텍처 스타일입니다. 클라이언트가 특정 URL(URI)에 HTTP Headers, Query Parameters, Body 등을 포함하여 **요청(Request)**을 보내면, 서버는 처리 결과에 맞는 HTTP 상태 코드(예: 200 OK, 400 Bad Request, 401 Unauthorized)와 함께 JSON 등의 데이터로 **응답(Response)**합니다.
- **HTTP Methods 차이**:
  - **GET**: 서버로부터 정보를 조회하기 위해 사용됩니다. 데이터가 URL의 Query String에 노출되므로 보안성이 요구되거나 크기가 큰 데이터 전송에는 부적합합니다. (예: Naver Local Search 맛집 검색 API)
  - **POST**: 서버에 데이터를 전송하여 새로운 리소스를 생성하거나 행위를 지시할 때 사용됩니다. 데이터는 HTTP Body에 담겨 전송되므로 대용량 및 비교적 안전한 전송이 가능합니다. (예: Google Gemini LLM 요청 API)

### Q2. LLM 출력 결과를 구조화(JSON)하여 다음 단계의 입력으로 활용하는 파이프라인 흐름
1. **정밀 프롬프트 설계**: LLM에게 답변 형식을 단순 텍스트가 아닌, 기정의된 스키마(예: `recommended_cities`, `weather`, `events`, `reason` 등)를 갖춘 순수 JSON 구조로만 응답하도록 강제합니다. (Gemini의 `response_mime_type` 설정 활용)
2. **JSON 파싱 및 검증**: LLM의 응답 문자열을 `json.loads()`를 통해 파이썬 딕셔너리로 변환하고 필수 키들이 누락되었는지 확인합니다.
3. **다음 API의 입력 값 주입**: 파싱에 성공하면 `recommendation["recommended_cities"]`에서 도시명을 하나씩 꺼내어 맛집 검색 API의 Query Parameter(예: `query="{city} 맛집"`)로 주입하여 연동 흐름을 완성합니다.

### Q3. 외부 API 호출에서 발생하는 대표 오류와 대응 원칙
- **인증 에러 (AUTH_ERROR, 401/403)**:
  - *원인*: 유효하지 않은 API 키 사용, 키 미등록, 도메인/권한 차단.
  - *대응*: 오류 목록(`errors`)에 인증 오류 상태를 기록하고, 해당 정보(예: 맛집)는 "데이터 없음" 처리 후 리포트 생성을 계속 진행합니다.
- **쿼터/비용 초과 (RATE_LIMIT_ERROR, 429)**:
  - *원인*: 무료 제공 트래픽 초과 혹은 너무 잦은 요청.
  - *대응*: 대기 시간 후 재시도(Exponential Backoff)를 적용하거나 즉시 사용자에게 할당량 초과 사실을 알립니다.
- **네트워크 에러 (NETWORK_ERROR / 타임아웃)**:
  - *원인*: 서버 다운, 인터넷 차단, DNS 오류.
  - *대응*: `requests.exceptions.RequestException` 등 예외 처리를 통해 일정 타임아웃(Timeout) 한도를 초과하면 에러로 판단하고 우아하게 기본 디폴트 값이나 캐시로 폴백합니다.
- **파싱 에러 (PARSE_ERROR)**:
  - *원인*: JSON 형식이 아닌 일반 텍스트나 깨진 구조를 반환함.
  - *대응*: 1회에 한하여 프롬프트에 경고문을 추가해 재요청을 시도하고, 최종 실패 시에는 기본 폴백 값을 제공하여 시스템이 다운되지 않도록 합니다.

### Q4. API 키를 코드에 직접 작성하지 않고 .env/환경변수로 관리하는 이유
- **보안 사고 예방**: Git 등 소스 코드 관리 시스템(VCS)에 API 키가 올라가는 실수(Credential Leak)를 완벽히 격리 및 차단합니다.
- **유지보수 및 배포 유연성**: 코드를 한 줄도 수정하지 않고 개발환경(Dev), 테스트환경(Test), 운영환경(Production)에 맞게 다르게 발급된 API 키나 연결 정보들을 파일 하나(`.env`) 변경만으로 즉시 스위칭할 수 있습니다.
