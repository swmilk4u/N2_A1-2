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
> 실행 전 반드시 아래 순서대로 설정을 완료해 주세요.

### Step 1 — `.env` 파일 생성

프로젝트 루트 폴더(README.md가 있는 위치)에서 `.env.template` 파일을 복사하여 `.env` 파일을 만듭니다.

```bash
# macOS / Linux
cp .env.template .env

# Windows PowerShell
Copy-Item .env.template .env
```

> 💡 **초보자 설명**: `.env` 파일은 비밀번호처럼 민감한 정보(API 키)를 소스 코드 밖에서 따로 보관하는 "비밀 설정 파일"입니다. `.env.template`은 어떤 키가 필요한지 보여주는 "빈 양식"이고, 이를 복사하여 실제 키를 채워넣는 방식입니다.

### Step 2 — `.env` 파일에 API 키 입력

생성한 `.env` 파일을 열고 아래 3개의 키 값을 각자의 발급 키로 교체합니다.

```dotenv
# Google Gemini API 키 (LLM 여행 추천 및 리포트 생성에 사용)
GEMINI_API_KEY=여기에_발급받은_Gemini_키를_입력

# Naver Local Search API (맛집 검색에 사용)
NAVER_CLIENT_ID=여기에_발급받은_Naver_Client_ID를_입력
NAVER_CLIENT_SECRET=여기에_발급받은_Naver_Client_Secret을_입력
```

> 💡 **초보자 설명**: 이 키들은 외부 서비스가 "너는 인증된 사용자야"라고 확인하는 일종의 디지털 신분증입니다. 키가 없으면 API 서버가 요청을 거부합니다(401 Unauthorized 오류).
>
> **키 발급 안내**
> - **Google Gemini API 키**: [Google AI Studio](https://aistudio.google.com/) 에서 발급
> - **Naver Local Search API**: [Naver Developers](https://developers.naver.com/) 에서 애플리케이션 등록 후 발급

### Step 3 — 환경변수로 직접 설정 (선택사항)

`.env` 파일 대신 터미널 환경변수로 직접 설정할 수도 있습니다.

```powershell
# Windows PowerShell (현재 터미널 세션에만 적용)
$env:GEMINI_API_KEY="your_gemini_api_key_here"
$env:NAVER_CLIENT_ID="your_naver_client_id_here"
$env:NAVER_CLIENT_SECRET="your_naver_client_secret_here"
```

```bash
# macOS / Linux (현재 터미널 세션에만 적용)
export GEMINI_API_KEY="your_gemini_api_key_here"
export NAVER_CLIENT_ID="your_naver_client_id_here"
export NAVER_CLIENT_SECRET="your_naver_client_secret_here"
```

> 💡 **초보자 설명**: "환경변수"란 운영체제 안에 저장해두는 변수입니다. 터미널 창을 닫으면 사라지므로 임시로 테스트할 때 편리합니다. 영구 사용을 원하면 Step 2의 `.env` 파일 방식이 더 안정적입니다.

---

## 🚀 프로그램 실행 방법

### 방법 1 — CLI 날짜 옵션 지정 실행 (권장)

```bash
python travel_planner.py --date "2026-10-15"
```

### 방법 2 — 대화형 실행 (옵션 없이 실행 또는 더블클릭)

```bash
python travel_planner.py
```

> 💡 **초보자 설명**: 날짜 옵션 없이 실행하면 프로그램이 자동으로 대화형 입력 모드로 전환되어 날짜 입력을 기다립니다. 파일 탐색기에서 더블클릭으로 실행해도 창이 바로 닫히지 않습니다.

### 실행 시 터미널 출력 예시

```
>>> 2026-10-15 날짜의 여행 계획 생성을 시작합니다. (LLM: Gemini / Map: Naver)
  [1/3] 1차 추천 생성 중(LLM)...
    - 추천된 지역: 단양, 설악산, 경주
  [2/3] 맛집 검색 중(지도/장소 API)...
    - '단양' 맛집 검색 중...
      ㄴ 5곳 검색 완료
    - '설악산' 맛집 검색 중...
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

> 💡 **초보자 설명**: `results/` 폴더는 프로그램이 처음 실행될 때 자동으로 만들어집니다. 아래 코드([utils.py](./02_source/utils.py))가 이 역할을 담당합니다.
>
> ```python
> # 02_source/utils.py — results/ 폴더 자동 생성
> def save_json_data(date_str: str, data: dict, results_dir: str = "results") -> str:
>     if not os.path.exists(results_dir):          # 폴더가 없으면
>         os.makedirs(results_dir, exist_ok=True)  # 폴더를 새로 만든다
>     file_path = os.path.join(results_dir, f"{date_str}_data.json")
>     with open(file_path, "w", encoding="utf-8") as f:
>         json.dump(data, f, ensure_ascii=False, indent=4)  # 데이터를 예쁘게 정렬해서 파일에 저장
>     return file_path
> ```

### 원본 데이터 JSON 구조 예시

```json
{
  "recommended_city": "단양",
  "recommended_cities": ["단양", "설악산"],
  "weather": "10월 중순 평균 14°C 내외, 단풍이 절정에 달하는 시기",
  "events": ["단양 마늘축제", "설악 단풍 걷기 대회"],
  "reason": "10월 중순은 내륙 산간 지역의 단풍이 가장 아름다운 시기입니다...",
  "restaurants": {
    "단양": [
      {
        "name": "단양식당",
        "address": "충북 단양군 단양읍 ...",
        "category": "한식",
        "url": "https://...",
        "x": 128.365,
        "y": 36.984
      }
    ]
  },
  "errors": []
}
```

> 💡 **초보자 설명**: JSON은 프로그램끼리 데이터를 주고받을 때 쓰는 표준 형식입니다. `{}`(중괄호)는 하나의 객체, `[]`(대괄호)는 목록을 의미합니다. `"errors": []`처럼 오류 목록이 비어있으면 정상적으로 실행된 것입니다.

### 최종 리포트 포함 섹션

생성되는 `_travel_plan.md` 파일은 아래 항목들을 포함합니다.

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

> 💡 **초보자 설명**: Markdown은 `#`, `##`, `-` 같은 간단한 기호로 문서를 꾸미는 텍스트 형식입니다. GitHub, Notion 등 대부분의 플랫폼에서 자동으로 예쁘게 렌더링해줍니다. VS Code에서 `.md` 파일을 열고 미리보기(Ctrl+Shift+V)로 확인할 수 있습니다.

---

## 1. 개요 및 개발 아키텍처

- **수행 목표**: 단일 API 호출의 한계를 넘어, LLM의 구조화된 JSON 출력을 다음 지도 검색 API의 입력으로 결합하는 파이프라인 아키텍처를 구축하고, 예외 복구(Fallback) 및 최적화(Caching)를 만족하는 안정적인 비즈니스 로직을 실현합니다.
- **연동 기술 스택**:
  - **LLM**: Google Gemini 2.5-flash (google-genai SDK 및 REST API 폴백 탑재)
  - **Local/Map**: Naver Local Search API (지역/장소 검색)
  - **환경 및 유틸**: Python 3.10+, python-dotenv (환경변수 관리), requests (HTTP 통신)

> 💡 **[핵심 연동 개념] 파이프라인(Pipeline)이란?**
>
> 공장의 컨베이어 벨트처럼 각 단계가 앞 단계의 결과를 이어받아 처리합니다.
>
> ```
> 사용자 날짜 입력
>       ↓
> [1단계] Gemini AI → 추천 도시 이름 (JSON)
>       ↓  추천 도시명을 그대로 다음 단계 입력으로 연결
> [2단계] Naver 지도 API → 맛집 목록 (JSON)
>       ↓  두 결과를 합쳐 다시 AI에게 전달
> [3단계] Gemini AI → 최종 여행 리포트 (Markdown)
>       ↓
> results/ 폴더에 파일 저장
> ```

---

## 2. 과제 요구사항별 구현 현황 및 핵심 소스 코드

### ① CLI 인터페이스 및 입력값 검증 (argparse)

- **구현 내용**: `argparse` 모듈을 적용하여 최상위 진입점 [travel_planner.py](./travel_planner.py)에서 `--date` (또는 `-date`) 인자를 인지하도록 구현했습니다.
- **날짜 형식 오류 처리**: 날짜 형식이 올바르지 않거나 달력에 없는 날짜(`2026-02-30` 등)이면 오류 메시지와 올바른 사용법을 출력한 뒤 즉시 종료(`sys.exit(1)`)합니다.
- **사용자 편의성(UX) 업그레이드**: 인자 없이 실행(더블클릭 등)하면 **대화형 입력 모드**로 자동 전환합니다.

#### 📂 핵심 소스 코드 — [travel_planner.py](./travel_planner.py)

```python
import argparse
import sys
import re
from utils import validate_date

def main():
    # argparse: 터미널 실행 시 뒤에 붙이는 옵션(--date)을 자동으로 해석
    parser = argparse.ArgumentParser(
        description="날짜 입력 기반 국내 여행지 추천 및 맛집 검색 CLI 프로그램"
    )
    parser.add_argument(
        "--date", "-date",
        type=str,
        required=False,           # 필수 아님 → 없으면 대화형 모드로 전환
        help="여행할 날짜 (형식: YYYY-MM-DD)"
    )

    args = parser.parse_args()
    date_str = args.date
    interactive_mode = False

    # --date 옵션 없이 실행되면 대화형 모드로 전환 (더블클릭 시 창 바로 꺼지는 현상 방지)
    if not date_str:
        interactive_mode = True
        print("\n=== Travel Planner 대화형 실행 모드 ===")
        date_str = input("여행할 날짜를 입력해 주세요 (형식: YYYY-MM-DD, 예: 2026-03-15): ").strip()

    # 정규식으로 날짜 패턴(YYYY-MM-DD)만 추출 — 실수로 "--date 2026-03-15"를 통째로 입력해도 처리
    if date_str:
        match = re.search(r'\d{4}-\d{2}-\d{2}', date_str)
        if match:
            date_str = match.group(0)

    # 날짜 유효성 검사: 형식이 틀리거나 달력에 없는 날짜면 사용법 출력 후 종료
    if not validate_date(date_str):
        print(f"\n[오류] 입력한 날짜 '{date_str}'는 유효하지 않습니다.")
        print("사용법: python travel_planner.py --date \"YYYY-MM-DD\"  (예: 2026-03-15)\n")
        sys.exit(1)   # 오류 코드 1로 프로그램 강제 종료
```

#### 📂 날짜 유효성 검증 코드 — [02_source/utils.py](./02_source/utils.py)

```python
from datetime import datetime

def validate_date(date_str: str) -> bool:
    """
    날짜 문자열이 YYYY-MM-DD 형식에 맞는지와
    실제 달력에 존재하는 날짜인지 동시에 검증합니다.
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")  # 형식 + 유효성 동시 검사
        return True
    except ValueError:
        return False  # "2026-02-30", "abcd-xx-yy" 같은 잘못된 입력 모두 False
```

> 💡 **초보자 설명**:
> - `argparse`는 파이썬 내장 모듈로, 터미널에서 `--date "2026-10-15"` 처럼 추가 정보를 넘기는 방법을 자동으로 처리해줍니다. 직접 `sys.argv`를 파싱하지 않아도 되어 편리합니다.
> - `re.search(r'\d{4}-\d{2}-\d{2}', ...)` 는 정규식(Regular Expression)으로, 긴 문자열 속에서 `숫자4개-숫자2개-숫자2개` 패턴을 찾는 "텍스트 필터"입니다.
> - `datetime.strptime()`은 `"2026-02-30"` 같이 형식은 맞지만 달력에 없는 날짜도 오류로 잡아냅니다.
> - `sys.exit(1)`은 프로그램을 즉시 종료하며, `1`은 "오류가 있어서 종료"를 뜻하는 관례적인 코드입니다. (정상 종료는 `0`)

---

### ② LLM API 연동 및 JSON 구조화 (1차 추천)

- **구현 내용**: 날짜 정보를 Google Gemini 2.5-flash API로 전달하여 계절에 어울리는 국내 여행 지역 **2~3곳**, 날씨, 행사, 추천 근거를 JSON 형태로 응답받습니다. (보너스: 복수 지역 추천 구현)
- **파싱 실패 방어**: JSON 형식이 아닌 답변이 오면 에러를 기록하고 **최대 1회 재요청**합니다. 재시도도 실패하면 기본 폴백 값으로 계속 진행합니다.

#### 📂 핵심 소스 코드 — [02_source/llm_client.py](./02_source/llm_client.py)

```python
import json
from google import genai
from google.genai import types

class LLMClient:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")  # .env에서 키 로드

    def _call_gemini_api(self, prompt: str, system_prompt: str, json_mode: bool = True) -> str:
        """Gemini SDK로 API를 호출합니다. SDK 미설치 시 REST API로 자동 폴백."""
        if GEMINI_SDK_AVAILABLE and self.gemini_key:
            client = genai.Client(api_key=self.gemini_key)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
            if json_mode:
                config.response_mime_type = "application/json"  # AI에게 JSON만 출력하도록 강제

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            return response.text
        else:
            # SDK 없을 때: HTTP 직접 호출(REST API)로 대체
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            response = requests.post(url, json=payload, timeout=30)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]

    def get_recommendation(self, date_str: str, error_handler) -> dict | None:
        """여행지 추천 JSON을 요청하고, 실패 시 1회 재시도합니다."""
        system_prompt = (
            "You are a professional travel planner. "
            "You must respond ONLY with a JSON object."  # 절대 JSON만 출력하도록 지시
        )
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

        # 1차 시도
        try:
            response_text = self._call_gemini_api(prompt, system_prompt, json_mode=True)
            result = json.loads(response_text)  # 문자열 → 파이썬 딕셔너리로 변환
            return result
        except Exception as e:
            error_handler.add_error("llm_recommendation_attempt1", "PARSE_ERROR", str(e))

        # 2차 재시도 (최대 1회) — 프롬프트에 경고 문구 추가
        print("    [Warning] JSON 형식 오류. 프롬프트 보정 후 재시도합니다...")
        retry_prompt = prompt + "\n경고: 반드시 중괄호로 시작하는 엄격한 JSON 형식만 출력해주세요."
        try:
            response_text = self._call_gemini_api(retry_prompt, system_prompt, json_mode=True)
            return json.loads(response_text)
        except Exception as e:
            error_handler.add_error("llm_recommendation_attempt2", "PARSE_ERROR", str(e))
            return None  # 최종 실패 → 호출부에서 기본값으로 대체
```

> 💡 **초보자 설명**:
> - AI에게 질문할 때 `response_mime_type = "application/json"` 설정을 추가하면, AI가 일반 문장이 아닌 오직 JSON 형식으로만 답하도록 제한됩니다. 마치 "반드시 엑셀 표 형태로만 답해줘"라고 지시하는 것과 같습니다.
> - `json.loads(text)` 는 `'{"city": "부산"}'` 같은 **문자열**을 `{"city": "부산"}` 처럼 파이썬이 실제로 사용할 수 있는 **딕셔너리 데이터**로 변환하는 함수입니다.
> - 재시도를 최대 1회로 제한하는 이유: 무한 재시도는 API 비용을 낭비하고 프로그램을 멈추게 만들 수 있습니다. 1회 실패하면 기본값으로 대체하고 다음 단계를 계속 진행하는 것이 더 안전합니다.

---

### ③ 지도/장소 검색 API 연동 및 예외 처리 (Naver Local)

- **구현 내용**: 추천된 도시명에 `" 맛집"`을 결합(예: `"부산 맛집"`)하여 네이버 로컬 검색 API에 요청하고, 각 도시별 최대 5곳의 식당 정보를 수집합니다.
- **오류 격리(Error Isolation)**: 인증 오류(401/403), 검색 결과 0건, 네트워크 장애 등 어떤 오류가 발생해도 프로그램이 강제 종료되지 않습니다. 오류를 기록하고 빈 목록으로 다음 단계를 이어갑니다.

#### 📂 핵심 소스 코드 — [02_source/map_client.py](./02_source/map_client.py)

```python
import requests

class MapClient:
    def __init__(self):
        # .env 파일에서 네이버 API 키를 읽어옴
        self.naver_id     = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")

    def has_valid_key(self) -> bool:
        """키가 설정되어 있는지 확인합니다."""
        return bool(self.naver_id and self.naver_secret)

    def _clean_html_tags(self, text: str) -> str:
        """네이버 응답에 포함된 <b>...</b> 같은 HTML 태그를 제거합니다."""
        return re.sub(r'<[^>]*>', '', text) if text else ""

    def _search_naver(self, city_name: str, limit: int, error_handler) -> list:
        url = "https://openapi.naver.com/v1/search/local.json"
        headers = {
            "X-Naver-Client-Id":     self.naver_id,     # 헤더에 인증 키를 담아 전송 (GET 방식)
            "X-Naver-Client-Secret": self.naver_secret
        }
        params = {
            "query":   f"{city_name} 맛집",  # "부산 맛집" 처럼 자동 조합
            "display": limit                  # 최대 5건
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)

            # 인증 실패 (401: 키 오류, 403: 권한 없음)
            if response.status_code in (401, 403):
                error_handler.add_error("place_search", "AUTH_ERROR",
                                        f"Naver API 인증 실패 (HTTP {response.status_code})")
                return []  # 빈 리스트 반환 → 프로그램 계속 진행

            # 기타 오류 (500 서버 오류 등)
            if response.status_code != 200:
                error_handler.add_error("place_search", "API_ERROR",
                                        f"HTTP {response.status_code}: {response.text}")
                return []

            data  = response.json()
            items = data.get("items", [])  # 검색 결과 목록 (없으면 빈 리스트)

            results = []
            for item in items:
                results.append({
                    "name":     self._clean_html_tags(item.get("title", "")),
                    "address":  item.get("roadAddress") or item.get("address", ""),
                    "category": item.get("category", ""),
                    "url":      item.get("link", ""),
                    "x":        float(item.get("mapx")) if item.get("mapx") else None,
                    "y":        float(item.get("mapy")) if item.get("mapy") else None,
                })

            # 검색 결과가 0건인 경우도 오류로 기록하고 빈 리스트 반환
            if not results:
                error_handler.add_error("place_search", "EMPTY_RESULT",
                                        f"'{city_name} 맛집' 검색 결과 0건")
            return results

        except requests.exceptions.RequestException as e:
            # 인터넷 연결 끊김, 타임아웃(15초 초과) 등 네트워크 오류
            error_handler.add_error("place_search", "NETWORK_ERROR", str(e))
            return []

    def search_restaurants(self, city_name: str, error_handler, limit: int = 5) -> list:
        """도시명으로 맛집을 검색합니다. 키 미설정 시 빈 목록을 반환합니다."""
        if not self.has_valid_key():
            error_handler.add_error("place_search", "AUTH_ERROR", "네이버 API 키 미설정")
            return []
        return self._search_naver(city_name, limit, error_handler)
```

> 💡 **초보자 설명**:
> - **HTTP GET vs POST**: 네이버 지도 API는 GET 방식입니다. `params={"query": "부산 맛집"}` 로 넘기면 실제 URL이 `...?query=부산+맛집` 처럼 만들어져 서버로 전송됩니다.
> - **헤더(Headers)**: HTTP 요청의 "편지 봉투"에 해당합니다. 본문(body)이 아닌 봉투에 "나는 `Client-Id=xxx`인 사용자야"라고 인증 정보를 담아 보냅니다.
> - **`try-except`**: "시도해보고 실패하면 이렇게 처리해"라는 파이썬 구문입니다. `except` 블록에서 `return []`(빈 리스트)를 반환하므로 오류가 나도 프로그램 전체가 멈추지 않습니다.
> - **`timeout=15`**: 서버가 15초 이내에 응답하지 않으면 포기하고 오류로 처리합니다. 이 값이 없으면 서버가 응답하지 않을 때 프로그램이 무한정 대기합니다.

---

### ④ 오류 누적 관리 — ErrorHandler

과제 요구사항에 따라 모든 오류를 중단 없이 기록하고 최종 결과물에 반영합니다.

#### 📂 핵심 소스 코드 — [02_source/utils.py](./02_source/utils.py)

```python
class ErrorHandler:
    """
    프로그램 실행 중 발생한 오류들을 내부적으로 누적하고 관리하는 클래스입니다.
    오류가 발생해도 프로그램을 멈추지 않고, 나중에 리포트에 함께 기록합니다.
    """
    def __init__(self):
        self.errors = []  # 오류 목록을 담는 빈 리스트로 시작

    def add_error(self, step: str, error_type: str, message: str):
        """오류 정보를 딕셔너리로 만들어 목록에 추가합니다."""
        error_entry = {
            "step":    step,        # 어느 단계에서 발생했는지 (예: "place_search")
            "type":    error_type,  # 오류 종류 (예: "AUTH_ERROR", "NETWORK_ERROR")
            "message": message      # 상세 오류 내용
        }
        self.errors.append(error_entry)

    def get_errors(self) -> list:
        """누적된 오류 목록을 반환합니다. JSON 파일 저장 시 'errors' 키에 담깁니다."""
        return self.errors
```

오류 발생 시 JSON 파일의 `errors` 섹션 예시:

```json
{
  "errors": [
    {
      "step": "place_search",
      "type": "AUTH_ERROR",
      "message": "Naver API 인증 실패 (HTTP 401)"
    }
  ]
}
```

> 💡 **초보자 설명**:
> - **왜 오류가 나도 계속 진행하나요?**: 맛집 검색 API가 실패했다고 프로그램 전체가 멈추면 사용자가 아무 결과도 못 받습니다. 오류를 "기록"만 하고 계속 진행하면, 맛집 섹션만 "데이터 없음"으로 표기된 완성된 리포트를 줄 수 있습니다. 이것을 **Graceful Degradation(우아한 성능 저하)** 이라고 합니다.
> - `self.errors.append(error_entry)`: `append()`는 파이썬 리스트에 항목을 추가하는 메서드입니다. 마치 메모장에 오류 내역을 한 줄씩 적는 것과 같습니다.

---

### ⑤ 최종 리포트 생성 및 결과 저장

- **최종 리포트**: 1차 추천 JSON + 도시별 맛집 목록 + 에러 기록을 Gemini에게 전달하여 Markdown 형식의 여행 리포트를 생성합니다. `추천 지역`, `날씨 요약`, `행사/축제`, `맛집 추천`, **`1일 일정 제안`**(오전/오후/저녁), `오류 요약` 섹션을 포함합니다.
- **결과 캐싱 (보너스)**: 동일 날짜로 재실행 시 이미 저장된 JSON이 있으면 API 호출을 건너뛰고 리포트를 즉시 재생성합니다.

#### 📂 핵심 소스 코드 — 결과 저장 ([travel_planner.py](./travel_planner.py) + [02_source/report_generator.py](./02_source/report_generator.py))

```python
# travel_planner.py — 전체 수집 데이터를 하나의 딕셔너리로 조립
raw_data = {
    "recommended_cities": recommendation.get("recommended_cities"),
    "recommended_city":   recommendation.get("recommended_city"),
    "weather":            recommendation.get("weather"),
    "events":             recommendation.get("events"),
    "reason":             recommendation.get("reason"),
    "restaurants":        places_data,              # 도시별 맛집 리스트 (0건 가능)
    "errors":             error_handler.get_errors()  # 발생한 오류 목록
}

# 파일로 저장
json_path = save_json_data(date_str, raw_data)    # results/{date}_data.json
md_path   = save_report(date_str, report_content) # results/{date}_travel_plan.md

# 터미널에 최종 리포트 출력
print("\n" + "="*80)
print("📄 생성된 최종 여행 리포트 내용")
print("="*80)
print(report_content)
print(f"\n>>> 완료! 아래 결과 파일을 확인하세요.")
print(f"  - 원본 데이터 JSON : {json_path}")
print(f"  - 최종 리포트 Markdown: {md_path}")
```

```python
# 02_source/report_generator.py — Markdown 파일 저장
def save_report(date_str: str, report_content: str, results_dir: str = "results") -> str:
    if not os.path.exists(results_dir):
        os.makedirs(results_dir, exist_ok=True)  # results/ 폴더 자동 생성
    file_path = os.path.join(results_dir, f"{date_str}_travel_plan.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    return file_path
```

#### 📂 핵심 소스 코드 — 캐싱 ([02_source/utils.py](./02_source/utils.py))

```python
def get_cached_data(date_str: str, results_dir: str = "results") -> dict | None:
    """
    같은 날짜로 이전에 저장된 JSON 파일이 있으면 불러옵니다.
    있으면 딕셔너리 반환, 없으면 None 반환.
    """
    cache_path = os.path.join(results_dir, f"{date_str}_data.json")
    if os.path.exists(cache_path):         # 파일이 존재하는지 확인
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)        # 파일을 읽어 딕셔너리로 변환
        except Exception:
            return None                    # 파일이 깨진 경우 무시하고 새로 요청
    return None
```

```python
# travel_planner.py — 캐싱 분기 처리
cached_data = get_cached_data(date_str)

if cached_data:
    # 기존 JSON 파일이 있으면 API 호출 없이 즉시 리포트 재생성
    print(f"  [캐시 감지] 이미 저장된 {date_str} 데이터를 재사용합니다. API 호출을 건너뜁니다.")
    recommendation = {
        "recommended_cities": cached_data.get("recommended_cities", []),
        "recommended_city":   cached_data.get("recommended_city", ""),
        "weather":            cached_data.get("weather", ""),
        "events":             cached_data.get("events", []),
        "reason":             cached_data.get("reason", "")
    }
    places_data = cached_data.get("restaurants", {})
else:
    # 처음 실행: API를 모두 호출하여 데이터 수집
    print("  [1/3] 1차 추천 생성 중(LLM)...")
    recommendation = llm_client.get_recommendation(date_str, error_handler)
    ...
```

> 💡 **초보자 설명**:
> - **캐싱(Caching)이란?**: 처음에 힘들게 가져온 데이터를 파일로 저장해두고, 같은 요청이 다시 오면 저장된 파일을 바로 읽어주는 것입니다. 컴퓨터가 "이미 답을 알고 있으니 다시 계산하지 않는다"는 개념입니다.
> - **왜 유용한가?**: Gemini API와 Naver API는 호출 횟수에 제한(쿼터)이 있거나 비용이 발생할 수 있습니다. 같은 날짜로 10번 실행해도 API는 1번만 호출하므로 비용을 90% 절약합니다.
> - `json.load(f)` vs `json.loads(text)`: `load()`는 파일 객체에서, `loads()`는 문자열에서 JSON을 읽습니다. 's' = 'string'의 약자입니다.

---

## 3. 🔒 API 키 관리 및 보안 준수 사항

본 프로그램은 과제의 보안 규칙에 따라 API 키 유출을 원천 차단하고 안전하게 관리합니다.

1. **환경변수(.env) 기반 관리**: API 키를 소스코드나 문서 내에 직접 쓰지 않고, 외부 설정 파일인 `.env`에 격리하여 로드합니다.

```python
# 02_source/llm_client.py, map_client.py — 공통 패턴
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)        # .env 파일 로드

self.gemini_key  = os.getenv("GEMINI_API_KEY")     # 환경변수에서 값 읽기
self.naver_id    = os.getenv("NAVER_CLIENT_ID")
self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")
```

> 💡 **초보자 설명**: `os.getenv("GEMINI_API_KEY")` 는 `.env` 파일(또는 시스템 환경변수)에서 `GEMINI_API_KEY`라는 이름의 값을 가져옵니다. 코드 어디에도 실제 키 값이 쓰이지 않아서, 소스 코드를 GitHub에 올려도 키가 노출되지 않습니다.

2. **키 미설정 시 즉시 종료**: `GEMINI_API_KEY`, `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 중 하나라도 비어있으면 아래와 같이 설정 방법 가이드를 출력하고 즉시 종료합니다.

```python
# travel_planner.py — API 키 확인 및 가이드 출력
def print_api_guide():
    print("""
================================================================================
[오류] 필수 API 키가 설정되지 않았습니다! (Google Gemini & Naver Local API)
================================================================================
1. .env.template 파일을 복사하여 .env 파일을 만듭니다.
2. .env 파일에 아래 키 정보를 기입해 주세요.
   GEMINI_API_KEY=your_gemini_api_key_here
   NAVER_CLIENT_ID=your_naver_client_id_here
   NAVER_CLIENT_SECRET=your_naver_client_secret_here
3. 저장 후 다시 실행해 주세요.
================================================================================
    """)

# 키 확인 후 없으면 가이드 출력 + 종료
if not llm_client.has_valid_key() or not map_client.has_valid_key():
    print_api_guide()
    sys.exit(1)
```

3. **Git 추적 배제**: `.env` 파일과 `results/` 폴더가 Git에 올라가지 않도록 [.gitignore](./.gitignore)에 등록했습니다.

```gitignore
# .gitignore
.env          # 실제 API 키가 담긴 파일 — Git에서 영구 제외
results/      # 실행 결과물 폴더 — 로컬에만 보관
```

---

## 📝 학습 점검 및 과제 미션 보고서

### Q1. REST API의 요청/응답 구조와 HTTP 메서드(GET/POST)의 차이

- **REST API**는 자원(Resource)을 이름으로 구분하여 HTTP 프로토콜로 데이터를 주고받는 아키텍처 스타일입니다. 클라이언트가 URL에 HTTP Headers, Query Parameters, Body 등을 포함하여 **요청(Request)**을 보내면, 서버는 HTTP 상태 코드(200 OK, 401 Unauthorized 등)와 함께 JSON 등으로 **응답(Response)**합니다.
- **HTTP Methods 차이**:
  - **GET**: 서버로부터 정보를 **조회**합니다. 데이터가 URL에 노출됩니다. (예: Naver Local Search — `?query=부산+맛집`)
  - **POST**: 서버에 데이터를 **전송**합니다. 데이터가 HTTP Body에 담겨 URL에 노출되지 않습니다. (예: Google Gemini — JSON Body에 프롬프트 전송)

```python
# GET 방식 예시 (Naver 맛집 검색)
response = requests.get(
    "https://openapi.naver.com/v1/search/local.json",
    headers={"X-Naver-Client-Id": "...", "X-Naver-Client-Secret": "..."},
    params={"query": "부산 맛집", "display": 5}  # URL 뒤에 ?query=부산+맛집&display=5 로 붙음
)

# POST 방식 예시 (Gemini LLM 호출)
response = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=...",
    json={"contents": [{"parts": [{"text": "부산 여행 추천해줘"}]}]}  # Body에 데이터를 담아 전송
)
```

### Q2. LLM 출력 결과를 구조화(JSON)하여 다음 단계의 입력으로 활용하는 파이프라인 흐름

1. **정밀 프롬프트 설계**: LLM에게 `response_mime_type = "application/json"` 설정과 프롬프트로 순수 JSON만 출력하도록 강제합니다.
2. **JSON 파싱 및 검증**: `json.loads()`로 문자열을 딕셔너리로 변환하고, 필수 키(`recommended_city`, `weather`, `events`, `reason`)가 모두 있는지 확인합니다.
3. **다음 API 입력으로 주입**: `recommendation["recommended_cities"]` 에서 도시명을 꺼내 `query=f"{city} 맛집"` 으로 맛집 검색 API에 연결합니다.

```python
# 파이프라인 흐름 요약
recommendation = llm_client.get_recommendation("2026-10-15", error_handler)
# → {"recommended_cities": ["단양", "설악산"], "weather": "...", ...}

for city in recommendation["recommended_cities"]:      # LLM 결과를 다음 API 입력으로 연결
    restaurants = map_client.search_restaurants(city, error_handler, limit=5)
    places_data[city] = restaurants
# → {"단양": [{name, address, ...}], "설악산": [...]}

report = llm_client.generate_report("2026-10-15", recommendation, places_data, error_handler)
# → "# 2026-10-15 국내 여행 추천 리포트\n## 추천 지역\n..."
```

### Q3. 외부 API 호출에서 발생하는 대표 오류와 대응 원칙

| 오류 유형 | HTTP 코드 | 원인 | 대응 방법 |
|-----------|-----------|------|-----------|
| **AUTH_ERROR** | 401 / 403 | 키 오류, 권한 없음 | 에러 기록 후 "데이터 없음" 처리, 계속 진행 |
| **RATE_LIMIT** | 429 | 쿼터 초과 | 사용자에게 할당량 초과 안내 |
| **NETWORK_ERROR** | — | 인터넷 끊김, 타임아웃 | `timeout=15` 설정, 오류 기록 후 빈 리스트 반환 |
| **PARSE_ERROR** | 200 | AI가 JSON 아닌 텍스트 반환 | 프롬프트 보정 후 1회 재시도, 실패 시 기본값 사용 |

### Q4. API 키를 코드에 직접 작성하지 않고 .env/환경변수로 관리하는 이유

- **보안 사고 예방**: Git에 키가 올라가면 누구나 볼 수 있어 타인이 무단 사용하거나 비용이 청구될 수 있습니다.
- **유지보수 유연성**: `.env` 파일만 바꾸면 코드 수정 없이 개발/테스트/운영 환경의 키를 즉시 교체할 수 있습니다.
- **과금 사고 예방**: 과금이 걸린 API 키가 공개되면 타인이 무단으로 사용하여 요금이 폭증하는 사고를 예방합니다.
