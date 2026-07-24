# ✈️ 국내 여행지 추천 및 맛집 검색 프로그램 보고서

이 프로그램([travel_planner.py](./travel_planner.py))은 사용자가 입력한 특정 날짜를 기반으로 **Google Gemini API**와 **Naver Local Search API**를 유기적으로 연동하여 맞춤형 여행 코스 및 맛집 리스트를 생성하는 CLI 프로그램입니다.

---

### 📂 프로젝트 폴더 및 주요 파일 역할
```text
├── 01_document/            # 과제 문서 보관 폴더
├── 02_source/              # 핵심 모듈 소스 폴더
│   ├── llm_client.py       # Google Gemini LLM API 연동 및 JSON 수집 모듈
│   ├── map_client.py       # Naver Local API 연동 및 맛집 검색 모듈
│   ├── report_generator.py # 수집된 데이터를 합쳐 가독성 높은 리포트로 조립하는 모듈
│   └── utils.py            # 날짜 검증, 결과 캐싱(Caching), 오류 누적 기록 등 유틸 모듈
├── results/                # 날짜별로 최종 생성되는 결과물 폴더 (JSON, Markdown) — 자동 생성
├── travel_planner.py       # 메인 실행 파일 (날짜 옵션 및 대화형 입력 처리)
├── .env                    # 실제 API 키 입력 파일 (직접 생성 필요, Git 추적 제외)
├── .env.template           # API 키 입력 양식 템플릿 (키 값 없이 제공)
├── .gitignore              # Git 버전 관리에서 .env 및 결과물(results/) 자동 차단
└── README.md               # 최종 프로젝트 수행 보고서 (본 문서)
```

---

## 🔑 API 키 설정 방법 (반드시 먼저 진행)

> **⚠️ API 키가 설정되지 않으면 프로그램이 즉시 종료됩니다.**

### Step 1 — `.env` 파일 생성

프로젝트 루트 폴더에서 `.env.template`을 복사하여 `.env` 파일을 생성합니다.

```bash
# macOS / Linux
cp .env.template .env

# Windows PowerShell
Copy-Item .env.template .env
```

`.env` 파일은 API 키처럼 민감한 정보를 소스 코드 밖에서 별도로 보관하는 설정 파일입니다. `.env.template`은 어떤 키 항목이 필요한지 보여주는 양식이며, 이를 복사하여 실제 값을 채워넣는 방식으로 사용합니다.

### Step 2 — `.env` 파일에 API 키 입력

생성한 `.env` 파일에 아래 3개의 키 값을 발급받은 키로 입력합니다.

```dotenv
GEMINI_API_KEY=발급받은_Gemini_키
NAVER_CLIENT_ID=발급받은_Naver_Client_ID
NAVER_CLIENT_SECRET=발급받은_Naver_Client_Secret
```

- **Google Gemini API 키**: [Google AI Studio](https://aistudio.google.com/) 에서 발급
- **Naver Local Search API**: [Naver Developers](https://developers.naver.com/) 에서 애플리케이션 등록 후 발급

키가 없으면 API 서버가 요청을 거부(HTTP 401 Unauthorized)합니다. 이 키들은 서비스가 "인증된 사용자"임을 확인하는 디지털 신분증 역할을 합니다.

### Step 3 — 환경변수로 직접 설정 (선택)

`.env` 파일 방식 외에 터미널 환경변수로 직접 설정할 수도 있습니다. 단, 터미널 창을 닫으면 설정이 초기화되므로 테스트 목적에 적합합니다.

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
$env:NAVER_CLIENT_ID="your_naver_client_id_here"
$env:NAVER_CLIENT_SECRET="your_naver_client_secret_here"
```

```bash
# macOS / Linux
export GEMINI_API_KEY="your_gemini_api_key_here"
export NAVER_CLIENT_ID="your_naver_client_id_here"
export NAVER_CLIENT_SECRET="your_naver_client_secret_here"
```

---

## 🚀 프로그램 실행 방법

**방법 1 — CLI 날짜 옵션 지정 (권장)**

```bash
python travel_planner.py --date "2026-10-15"
```

**방법 2 — 대화형 실행 (옵션 없이 실행 또는 더블클릭)**

```bash
python travel_planner.py
```

날짜 옵션 없이 실행하면 대화형 입력 모드로 자동 전환되어 날짜 입력을 기다립니다. 파일 탐색기에서 더블클릭으로 실행해도 창이 즉시 닫히지 않습니다.

**실행 시 터미널 출력 예시**

```
>>> 2026-10-15 날짜의 여행 계획 생성을 시작합니다. (LLM: Gemini / Map: Naver)
  [1/3] 1차 추천 생성 중(LLM)...
    - 추천된 지역: 단양, 설악산, 경주
  [2/3] 맛집 검색 중(지도/장소 API)...
    - '단양' 맛집 검색 중...
      ㄴ 5곳 검색 완료
  [3/3] 최종 리포트 생성 중(LLM)...

================================================================================
📄 생성된 최종 여행 리포트 내용
================================================================================
(리포트 본문 전체 출력)
================================================================================

>>> 완료! 아래 결과 파일을 확인하세요.
  - 원본 데이터 JSON : results/2026-10-15_data.json
  - 최종 리포트 Markdown: results/2026-10-15_travel_plan.md
```

---

## 📁 결과물 확인 방법

프로그램 실행이 완료되면 `results/` 폴더(없으면 자동 생성)에 아래 2개 파일이 생성됩니다.

| 파일명 | 설명 |
|--------|------|
| `results/YYYY-MM-DD_data.json` | 1차 추천 결과 + 맛집 검색 결과 + 오류 목록이 담긴 원본 데이터 |
| `results/YYYY-MM-DD_travel_plan.md` | 최종 여행 리포트 (Markdown 형식) |

`results/` 폴더는 [utils.py](./02_source/utils.py)의 `save_json_data()` 함수가 최초 실행 시 자동으로 생성합니다.

```python
# 02_source/utils.py
if not os.path.exists(results_dir):
    os.makedirs(results_dir, exist_ok=True)  # 폴더가 없으면 자동으로 생성
```

**원본 데이터 JSON 구조 예시**

수집된 모든 데이터(추천 결과, 맛집 목록, 오류 이력)를 하나의 JSON 파일로 통합 저장합니다.

```json
{
  "recommended_city": "단양",
  "recommended_cities": ["단양", "설악산"],
  "weather": "10월 중순 평균 14°C 내외, 단풍이 절정에 달하는 시기",
  "events": ["단양 마늘축제", "설악 단풍 걷기 대회"],
  "reason": "10월 중순은 내륙 산간 지역의 단풍이 가장 아름다운 시기입니다...",
  "restaurants": {
    "단양": [{ "name": "단양식당", "address": "충북 단양군...", "category": "한식" }]
  },
  "errors": []
}
```

`"errors": []`처럼 오류 목록이 비어 있으면 모든 단계가 정상적으로 처리된 것이며, 오류 발생 시 해당 단계와 유형이 기록됩니다.

**최종 리포트 구성 섹션**

```markdown
# YYYY-MM-DD 국내 여행 추천 리포트
## 추천 지역
## 추천 이유
## 날씨 요약
## 행사/축제
## 맛집 추천        ← 0건이면 "데이터 없음 (장소 검색 결과 0건)" 표기
## 1일 일정 제안    ← 오전 / 오후 / 저녁 동선 포함
## 오류 요약(errors) ← 오류 발생 시에만 표기
```

---

## 1. 개요 및 개발 아키텍처

- **수행 목표**: 단일 API 호출의 한계를 넘어, LLM의 구조화된 JSON 출력을 다음 지도 검색 API의 입력으로 결합하는 파이프라인 아키텍처를 구축하고, 예외 복구(Fallback) 및 최적화(Caching)를 만족하는 안정적인 비즈니스 로직을 실현합니다.
- **연동 기술 스택**:
  - **LLM**: Google Gemini 2.5-flash (google-genai SDK 및 REST API 폴백 탑재)
  - **Local/Map**: Naver Local Search API (지역/장소 검색)
  - **환경 및 유틸**: Python 3.10+, python-dotenv (환경변수 관리), requests (HTTP 통신)

**파이프라인(Pipeline) 구조** — 각 단계의 출력이 다음 단계의 입력으로 자동 연결됩니다.

```
사용자 날짜 입력
      ↓
[1단계] Gemini AI  →  추천 도시명 포함 JSON
      ↓  도시명을 그대로 다음 단계 입력으로 전달
[2단계] Naver 지도 API  →  맛집 목록 JSON
      ↓  두 결과를 합쳐 AI에게 재전달
[3단계] Gemini AI  →  최종 여행 리포트 (Markdown)
      ↓
results/ 폴더에 JSON + .md 파일 저장
```

---

## 2. 과제 요구사항별 구현 현황 및 핵심 소스 코드

### ① CLI 인터페이스 및 입력값 검증 (argparse)

- **구현 내용**: `argparse` 모듈을 적용하여 [travel_planner.py](./travel_planner.py)에서 `--date` (또는 `-date`) 인자를 처리하도록 구현했습니다.
- **날짜 형식 오류 처리**: 형식이 잘못되거나 달력에 없는 날짜(`2026-02-30` 등)이면 사용법을 출력하고 `sys.exit(1)`로 즉시 종료합니다.
- **UX 보완**: 인자 없이 실행(더블클릭 포함)하면 대화형 입력 모드로 자동 전환됩니다.

#### 📂 [travel_planner.py](./travel_planner.py) — CLI 옵션 파싱

`argparse`는 터미널에서 `--date "날짜"` 처럼 추가 정보를 넘기는 방법을 자동으로 해석해주는 파이썬 표준 모듈입니다.

```python
parser = argparse.ArgumentParser(description="국내 여행지 추천 및 맛집 검색 CLI 프로그램")
parser.add_argument("--date", "-date", type=str, required=False, help="여행할 날짜 (YYYY-MM-DD)")
args = parser.parse_args()
```

`required=False`로 설정하여 날짜 옵션이 생략된 경우에도 오류 없이 진입하고, 이후 대화형 모드로 분기합니다.

#### 📂 [travel_planner.py](./travel_planner.py) — 대화형 모드 전환 및 날짜 정제

```python
if not date_str:
    interactive_mode = True
    date_str = input("여행할 날짜를 입력해 주세요 (YYYY-MM-DD): ").strip()

# 정규식으로 날짜 패턴만 추출 — "--date 2026-03-15"를 통째로 입력한 경우에도 처리
match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
if match:
    date_str = match.group(0)
```

`re.search()`의 정규식 패턴 `\d{4}-\d{2}-\d{2}` 는 "숫자 4자리-숫자 2자리-숫자 2자리" 형태를 찾는 텍스트 필터입니다. 사용자가 명령어 전체를 잘못 입력해도 날짜 부분만 자동 추출합니다.

#### 📂 [02_source/utils.py](./02_source/utils.py) — 날짜 유효성 검증

```python
def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # 형식과 달력 유효성 동시 검사
        return True
    except ValueError:
        return False
```

`datetime.strptime()`은 형식이 올바르더라도 `"2026-02-30"` 처럼 실제 달력에 없는 날짜는 `ValueError`를 발생시킵니다. 이를 통해 형식 검사와 유효성 검사를 한 번에 처리합니다. 검증 실패 시 `sys.exit(1)`로 종료하며, `1`은 관례적으로 "비정상 종료"를 의미하는 오류 코드입니다.

---

### ② LLM API 연동 및 JSON 구조화 (1차 추천)

- **구현 내용**: 날짜 정보를 Google Gemini 2.5-flash API로 전달하여 국내 여행 지역 **2~3곳**, 날씨, 행사, 추천 근거를 JSON 형태로 응답받습니다. (보너스: 복수 지역 추천 구현)
- **파싱 실패 방어**: JSON 형식이 아닌 답변이 반환되면 에러를 기록하고 프롬프트를 보정하여 **최대 1회 재요청**합니다. 재시도도 실패하면 기본 폴백 값으로 계속 진행합니다.

#### 📂 [02_source/llm_client.py](./02_source/llm_client.py) — JSON 응답 강제 설정

```python
config = types.GenerateContentConfig(system_instruction=system_prompt)
config.response_mime_type = "application/json"  # AI 응답을 JSON 형식으로 강제
```

`response_mime_type = "application/json"` 설정은 Gemini에게 일반 텍스트 대신 순수 JSON 구조로만 응답하도록 제한합니다. 이렇게 해야만 응답을 파이썬 딕셔너리로 변환하여 다음 단계의 입력으로 활용할 수 있습니다.

#### 📂 [02_source/llm_client.py](./02_source/llm_client.py) — 1차 요청 및 JSON 파싱

```python
response_text = self._call_gemini_api(prompt, system_prompt, json_mode=True)
result = json.loads(response_text)  # 문자열 → 파이썬 딕셔너리 변환
```

`json.loads()`는 `'{"city": "부산"}'` 같은 JSON **문자열**을 `{"city": "부산"}` 형태의 파이썬 **딕셔너리**로 변환합니다. 변환에 실패하면 파싱 오류로 처리되어 재시도 로직으로 진입합니다.

#### 📂 [02_source/llm_client.py](./02_source/llm_client.py) — 파싱 실패 시 1회 재시도

```python
except Exception as e:
    error_handler.add_error("llm_recommendation_attempt1", "PARSE_ERROR", str(e))

# 프롬프트에 경고 문구를 추가하여 재시도 (최대 1회)
retry_prompt = prompt + "\n경고: 반드시 중괄호로 시작하는 엄격한 JSON 형식만 출력해주세요."
```

재시도를 최대 1회로 제한하는 이유는, 무한 재시도는 API 쿼터를 낭비하고 프로그램 응답성을 저하시키기 때문입니다. 2차 시도도 실패하면 호출부에서 기본값으로 대체하고 다음 단계를 계속 진행합니다.

---

### ③ 지도/장소 검색 API 연동 및 예외 처리 (Naver Local)

- **구현 내용**: 추천된 도시명에 `" 맛집"`을 결합(예: `"부산 맛집"`)하여 Naver Local Search API에 GET 방식으로 요청하고, 각 도시별 최대 5곳의 식당 정보를 수집합니다.
- **오류 격리(Error Isolation)**: 인증 오류(401/403), 결과 0건, 네트워크 장애 등 어떤 오류가 발생해도 프로그램이 강제 종료되지 않습니다. 오류를 기록하고 빈 목록으로 다음 단계를 이어갑니다.

#### 📂 [02_source/map_client.py](./02_source/map_client.py) — API 인증 및 요청

```python
headers = {
    "X-Naver-Client-Id":     self.naver_id,
    "X-Naver-Client-Secret": self.naver_secret
}
params = {"query": f"{city_name} 맛집", "display": limit}
response = requests.get(url, headers=headers, params=params, timeout=15)
```

Naver API는 인증 정보를 HTTP **헤더(Headers)**에 담아 전달하는 GET 방식입니다. `params`에 넘긴 검색어는 자동으로 URL 뒤에 `?query=부산+맛집&display=5` 형태로 조합됩니다. `timeout=15`는 15초 내 응답이 없으면 오류로 처리하여 무한 대기를 방지합니다.

#### 📂 [02_source/map_client.py](./02_source/map_client.py) — 상태 코드별 오류 분기

```python
if response.status_code in (401, 403):   # 인증 실패
    error_handler.add_error("place_search", "AUTH_ERROR", f"HTTP {response.status_code}")
    return []   # 빈 리스트 반환 → 프로그램은 중단 없이 계속 진행

if response.status_code != 200:          # 기타 서버 오류
    error_handler.add_error("place_search", "API_ERROR", f"HTTP {response.status_code}")
    return []
```

`401`은 API 키가 잘못됐거나 없는 경우, `403`은 해당 API 사용 권한이 없는 경우입니다. 두 경우 모두 오류 내역만 `ErrorHandler`에 기록하고 빈 리스트를 반환합니다. 이로써 맛집 섹션만 "데이터 없음"으로 표기되고 리포트 생성은 계속 진행됩니다.

#### 📂 [02_source/map_client.py](./02_source/map_client.py) — 네트워크 오류 처리

```python
except requests.exceptions.RequestException as e:
    error_handler.add_error("place_search", "NETWORK_ERROR", str(e))
    return []
```

인터넷 연결 끊김이나 타임아웃처럼 HTTP 응답 자체를 받지 못하는 경우는 `RequestException`으로 일괄 처리합니다. `try-except` 구문은 "시도해보고 실패하면 이렇게 처리해"라는 파이썬의 예외 처리 구문으로, 외부 API처럼 언제든 실패할 수 있는 연산에서 필수적으로 사용합니다.

---

### ④ 오류 누적 관리 — ErrorHandler

과제 요구사항에 따라, 실행 중 발생한 모든 오류를 프로그램 중단 없이 내부적으로 수집하여 최종 JSON 및 리포트에 함께 기록합니다.

#### 📂 [02_source/utils.py](./02_source/utils.py) — ErrorHandler 클래스

```python
class ErrorHandler:
    def __init__(self):
        self.errors = []  # 실행 중 발생한 오류를 누적하는 리스트

    def add_error(self, step: str, error_type: str, message: str):
        self.errors.append({"step": step, "type": error_type, "message": message})

    def get_errors(self) -> list:
        return self.errors   # 저장 시 JSON의 "errors" 키에 담김
```

오류가 발생한 단계(`step`)와 유형(`type`), 상세 내용(`message`)을 딕셔너리로 묶어 리스트에 누적합니다. 이를 **Graceful Degradation(우아한 성능 저하)** 이라 하며, 부분 실패가 전체 실패로 번지지 않도록 격리하는 설계 원칙입니다.

오류 발생 시 원본 JSON의 `errors` 섹션 기록 예시:

```json
{
  "errors": [
    { "step": "place_search", "type": "AUTH_ERROR", "message": "HTTP 401" }
  ]
}
```

---

### ⑤ 최종 리포트 생성 및 결과 저장

- **최종 리포트**: 1차 추천 JSON + 도시별 맛집 목록 + 에러 기록을 Gemini에게 전달하여 Markdown 형식의 리포트를 생성합니다. `추천 지역`, `날씨 요약`, `행사/축제`, `맛집 추천`, `1일 일정 제안`(오전/오후/저녁), `오류 요약` 섹션을 포함합니다.
- **결과 캐싱 (보너스)**: 동일 날짜로 재실행 시 기저장된 JSON이 있으면 API 호출을 건너뛰고 리포트를 즉시 재생성합니다.

#### 📂 [travel_planner.py](./travel_planner.py) — 원본 데이터 조립 및 파일 저장

```python
raw_data = {
    "recommended_cities": recommendation.get("recommended_cities"),
    "weather":            recommendation.get("weather"),
    "restaurants":        places_data,               # 도시별 맛집 리스트
    "errors":             error_handler.get_errors() # 누적된 오류 목록
}

json_path = save_json_data(date_str, raw_data)     # results/{date}_data.json
md_path   = save_report(date_str, report_content)  # results/{date}_travel_plan.md
```

수집된 전체 데이터를 하나의 딕셔너리로 조립한 뒤 JSON 파일로 저장하고, LLM이 생성한 마크다운 리포트는 별도의 `.md` 파일로 저장합니다. 이로써 원본 데이터와 최종 결과물이 분리되어 보관됩니다.

#### 📂 [02_source/utils.py](./02_source/utils.py) — 캐싱 처리

캐싱(Caching)은 이전 실행 결과를 파일로 저장해두고, 동일한 날짜로 재실행 시 API를 다시 호출하지 않고 저장된 파일을 그대로 활용하는 최적화 기법입니다.

```python
def get_cached_data(date_str: str, results_dir: str = "results") -> dict | None:
    cache_path = os.path.join(results_dir, f"{date_str}_data.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)   # 저장된 JSON 파일을 딕셔너리로 읽어옴
    return None
```

`json.load(f)`는 파일 객체에서 JSON을 읽는 함수로, 문자열에서 읽는 `json.loads()`와 구별됩니다. 동일 날짜로 재실행 시 Gemini와 Naver API 호출을 모두 건너뛰므로 API 쿼터 낭비와 중복 비용을 방지합니다.

---

## 3. 🔒 API 키 관리 및 보안 준수 사항

본 프로그램은 과제의 보안 규칙에 따라 API 키 유출을 원천 차단하고 안전하게 관리합니다.

**1. 환경변수(.env) 기반 관리**

API 키를 소스코드나 문서에 직접 작성하지 않고, 외부 설정 파일 `.env`에 격리하여 로드합니다.

```python
# llm_client.py, map_client.py 공통 패턴
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)

self.gemini_key   = os.getenv("GEMINI_API_KEY")
self.naver_id     = os.getenv("NAVER_CLIENT_ID")
self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
```

`os.getenv()`는 `.env` 파일 또는 시스템 환경변수에서 해당 키 이름의 값을 읽어옵니다. 코드 어디에도 실제 키 값이 등장하지 않으므로, 소스 코드를 GitHub에 올려도 키가 노출되지 않습니다.

**2. API 키 미설정 시 즉시 종료**

3개 키 중 하나라도 비어있으면 설정 방법 가이드를 출력하고 즉시 종료합니다.

```python
if not llm_client.has_valid_key() or not map_client.has_valid_key():
    print_api_guide()   # 설정 방법 안내 출력
    sys.exit(1)
```

**3. Git 추적 배제 (.gitignore)**

실제 키가 담긴 `.env` 파일과 로컬 실행 결과물인 `results/` 폴더가 Git 저장소에 포함되지 않도록 차단 규칙을 등록했습니다.

```gitignore
.env        # 실제 API 키가 담긴 파일 — Git에서 영구 제외
results/    # 실행 결과물 폴더 — 로컬에만 보관
```

**4. 템플릿 분리 제공**

협업 환경에서의 키 노출 방지를 위해 실제 키 값을 지운 [.env.template](./.env.template)만 저장소에 포함하여 제공합니다.

---

## 📝 학습 점검 및 과제 미션 보고서

### Q1. REST API의 요청/응답 구조와 HTTP 메서드(GET/POST)의 차이

**REST API**는 자원(Resource)을 URL로 식별하고 HTTP 프로토콜로 데이터를 주고받는 아키텍처 스타일입니다. 클라이언트가 URL에 Headers, Parameters, Body 등을 포함하여 **요청(Request)**을 보내면, 서버는 HTTP 상태 코드(200 OK, 401 Unauthorized 등)와 JSON 데이터로 **응답(Response)**합니다.

**HTTP 메서드 비교**

| 메서드 | 용도 | 데이터 위치 | 본 프로그램 적용 |
|--------|------|------------|----------------|
| **GET** | 정보 조회 | URL Query String에 노출 | Naver 맛집 검색 |
| **POST** | 데이터 전송·처리 요청 | HTTP Body에 은닉 | Gemini LLM 호출 |

```python
# GET — URL에 파라미터가 붙는 방식 (?query=부산+맛집&display=5)
requests.get(url, headers={...}, params={"query": "부산 맛집"})

# POST — Body에 데이터를 담아 전송하는 방식
requests.post(url, json={"contents": [{"parts": [{"text": "여행 추천해줘"}]}]})
```

### Q2. LLM 출력 결과를 구조화(JSON)하여 다음 단계의 입력으로 활용하는 파이프라인 흐름

1. **JSON 응답 강제**: `response_mime_type = "application/json"` 설정과 프롬프트로 LLM이 순수 JSON 구조로만 응답하도록 제한합니다.
2. **파싱 및 검증**: `json.loads()`로 응답 문자열을 딕셔너리로 변환하고 필수 키(`recommended_city`, `weather`, `events`, `reason`) 존재 여부를 확인합니다.
3. **다음 API 입력 연결**: 파싱된 `recommendation["recommended_cities"]`에서 도시명을 순서대로 꺼내 `query=f"{city} 맛집"` 형태로 Naver API에 주입합니다.

```python
# 파이프라인 흐름 요약
recommendation = llm_client.get_recommendation("2026-10-15", error_handler)
# → {"recommended_cities": ["단양", "설악산"], "weather": "...", ...}

for city in recommendation["recommended_cities"]:
    places_data[city] = map_client.search_restaurants(city, error_handler, limit=5)

report = llm_client.generate_report("2026-10-15", recommendation, places_data, error_handler)
# → "# 2026-10-15 국내 여행 추천 리포트\n## 추천 지역\n..."
```

### Q3. 외부 API 호출에서 발생하는 대표 오류와 대응 원칙

| 오류 유형 | HTTP 코드 | 원인 | 대응 방법 |
|-----------|-----------|------|-----------|
| **AUTH_ERROR** | 401 / 403 | 키 오류, 권한 없음 | 에러 기록 후 "데이터 없음" 처리, 계속 진행 |
| **RATE_LIMIT** | 429 | 쿼터 초과, 과다 요청 | 사용자에게 할당량 초과 안내 |
| **NETWORK_ERROR** | — | 인터넷 끊김, 타임아웃 | `timeout=15` 초과 시 오류 기록 후 빈 리스트 반환 |
| **PARSE_ERROR** | 200 | AI가 JSON 외 텍스트 반환 | 프롬프트 보정 후 1회 재시도, 실패 시 기본값으로 대체 |

### Q4. API 키를 코드에 직접 작성하지 않고 .env/환경변수로 관리하는 이유

- **보안 사고 예방**: Git에 소스 코드와 함께 키가 올라가면 누구나 열람할 수 있어, 타인의 무단 사용 또는 비용 청구 사고로 이어질 수 있습니다.
- **유지보수 유연성**: 코드를 수정하지 않고 `.env` 파일만 변경하여 개발·테스트·운영 환경의 키를 즉시 교체할 수 있습니다.
- **과금 사고 예방**: 과금이 연동된 API 키가 공개되면 타인이 무제한으로 사용하여 예상치 못한 요금이 부과될 수 있습니다.
