import os
import json
import requests
from dotenv import load_dotenv

# dotenv 로드
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)

try:
    from google import genai
    from google.genai import types
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False

class LLMClient:
    """
    Google Gemini 2.5-flash API를 활용해
    여행 추천 및 리포트를 생성하는 클라이언트 클래스입니다.
    """
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def has_valid_key(self) -> bool:
        """
        사용 가능한 Gemini API 키가 존재하는지 확인합니다.
        """
        return bool(self.gemini_key)

    def _call_gemini_api(self, prompt: str, system_prompt: str, json_mode: bool = True) -> str:
        """
        Gemini API를 google-genai SDK 혹은 REST API로 호출합니다.
        """
        if GEMINI_SDK_AVAILABLE and self.gemini_key:
            # SDK 사용
            client = genai.Client(api_key=self.gemini_key)
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
            if json_mode:
                config.response_mime_type = "application/json"
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            return response.text
        else:
            # SDK가 없거나 오류가 있을 경우 REST API 폴백 호출
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "systemInstruction": {
                    "parts": [{"text": system_prompt}]
                },
                "generationConfig": {
                    "temperature": 0.7
                }
            }
            if json_mode:
                payload["generationConfig"]["responseMimeType"] = "application/json"
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Gemini API 호출 에러 (HTTP {response.status_code}): {response.text}")
            
            result_json = response.json()
            return result_json["candidates"][0]["content"]["parts"][0]["text"]

    def get_recommendation(self, date_str: str, error_handler) -> dict | None:
        """
        1차 여행지 추천 결과를 획득합니다. JSON 형식 출력을 강제하고 실패 시 1회 재시도합니다.
        """
        system_prompt = (
            "You are a professional travel planner. You must respond ONLY with a JSON object. "
            "Do not include any markdown formatting (like ```json ... ```) in your response, just the raw JSON."
        )
        
        prompt = f"""
        날짜: {date_str}
        이 시기에 한국에서 여행하기 좋은 국내 도시 2~3곳을 추천해줘.
        다음 구조의 JSON 객체로 반드시 응답해줘.
        {{
            "recommended_cities": ["도시1", "도시2"],
            "recommended_city": "도시1", // 추천된 도시 중 대표적인 한 곳
            "weather": "이 시기 추천 도시들의 일반적이고 상세한 날씨 정보 및 기온 요약",
            "events": ["진행되는 축제 혹은 문화 행사 목록 1~3개"],
            "reason": "해당 날짜에 이 도시들을 추천하는 과학적이고 매력적인 근거 3~4문장"
        }}
        """

        def parse_json(text: str) -> dict | None:
            try:
                cleaned_text = text.strip()
                if cleaned_text.startswith("```"):
                    lines = cleaned_text.splitlines()
                    if lines[0].startswith("```json") or lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    cleaned_text = "\n".join(lines).strip()
                
                parsed = json.loads(cleaned_text)
                
                if "recommended_cities" not in parsed and "recommended_city" in parsed:
                    parsed["recommended_cities"] = [parsed["recommended_city"]]
                elif "recommended_cities" in parsed and "recommended_city" not in parsed:
                    if parsed["recommended_cities"]:
                        parsed["recommended_city"] = parsed["recommended_cities"][0]
                    else:
                        parsed["recommended_city"] = ""
                
                required_keys = ["recommended_city", "recommended_cities", "weather", "events", "reason"]
                for key in required_keys:
                    if key not in parsed:
                        raise ValueError(f"필수 키 누락: {key}")
                
                return parsed
            except Exception:
                return None

        # 1차 시도
        try:
            response_text = self._call_gemini_api(prompt, system_prompt, json_mode=True)
            result = parse_json(response_text)
            if result:
                return result
            else:
                raise ValueError("JSON 파싱 혹은 스키마 검증 실패")
        except Exception as e:
            error_handler.add_error(
                step="llm_recommendation_attempt1",
                error_type="PARSE_ERROR" if "JSON" in str(e) or "파싱" in str(e) else "API_ERROR",
                message=f"1차 시도 실패: {str(e)}"
            )

        # 2차 시도 (재요청 1회)
        print("    [Warning] LLM 응답이 올바른 JSON 형식이 아닙니다. 프롬프트를 수정하여 재시도합니다 (최대 1회)...")
        retry_prompt = prompt + "\n경고: 이전 요청에서 JSON 형식이 올바르지 않았습니다. 반드시 중괄호로 시작하고 끝나는 엄격한 표준 JSON 형식만 출력해주세요. 다른 텍스트나 설명은 절대 덧붙이지 마세요."
        try:
            response_text = self._call_gemini_api(retry_prompt, system_prompt, json_mode=True)
            result = parse_json(response_text)
            if result:
                return result
            else:
                raise ValueError("재시도에서도 JSON 파싱 혹은 스키마 검증 실패")
        except Exception as e:
            error_handler.add_error(
                step="llm_recommendation_attempt2",
                error_type="PARSE_ERROR" if "JSON" in str(e) or "파싱" in str(e) else "API_ERROR",
                message=f"2차 재시도 실패: {str(e)}"
            )
            return None

    def generate_report(self, date_str: str, recommendation: dict, places_data: dict, error_handler) -> str | None:
        """
        1차 추천 JSON과 맛집 검색 결과(0건일 수 있음) 및 오류 요약을 전달하여 최종 리포트 Markdown을 생성합니다.
        """
        system_prompt = "You are a professional travel writer. Generate a beautiful travel guide in Markdown format."
        
        prompt = f"""
        날짜: {date_str}
        
        다음은 AI가 추천한 정보와 각 지역별 맛집 검색 결과입니다.
        이를 바탕으로 가독성이 좋고 미학적으로 아름다운 최종 국내 여행 추천 리포트를 Markdown으로 한국어로 작성해줘.
        
        [AI 추천 정보]
        - 추천 도시들: {recommendation.get('recommended_cities')}
        - 날씨 정보: {recommendation.get('weather')}
        - 관련 축제 및 행사: {recommendation.get('events')}
        - 추천 근거: {recommendation.get('reason')}
        
        [검색된 맛집 정보]
        {json.dumps(places_data, ensure_ascii=False, indent=2)}
        
        [요구사항]
        1. Markdown 제목(#)은 '{date_str} 국내 여행 추천 리포트'로 시작해줘.
        2. 다음 섹션을 반드시 마크다운 헤더로 포함해줘:
           - ## 추천 지역
           - ## 추천 이유
           - ## 날씨 요약
           - ## 행사/축제
           - ## 맛집 추천 (지역별로 맛집이 있는 경우 깔끔하게 리스트로 나열. 맛집 목록이 비었거나 데이터가 없으면 '데이터 없음 (장소 검색 결과 0건)'으로 표기하고 주소나 지도 링크(URL)가 있다면 클릭할 수 있게 마크다운 링크로 함께 표기해줘.)
           - ## 1일 일정 제안 (추천 지역들에 대해 오전, 오후, 저녁 동선을 포함한 재미있고 알찬 1일 여행 계획 제안)
        3. 만약 맛집 검색 중 API 오류나 결과 없음 등이 발생했다면, 리포트 맨 아래에 `## 오류 요약(errors)` 섹션을 만들고 발생한 오류 목록을 리스트로 간략하게 한국어로 정리해서 작성해줘. (오류가 없었다면 이 섹션은 생략하거나 오류 없음으로 기록)
        """

        try:
            return self._call_gemini_api(prompt, system_prompt, json_mode=False)
        except Exception as e:
            error_handler.add_error(
                step="report_generation",
                error_type="API_ERROR",
                message=f"리포트 생성 API 오류: {str(e)}"
            )
            return None
