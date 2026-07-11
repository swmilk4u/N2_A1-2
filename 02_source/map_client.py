import os
import re
import requests
from dotenv import load_dotenv

# 설정 파일(.env) 불러오기
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(parent_dir, ".env")
load_dotenv(dotenv_path=env_path)

class MapClient:
    """
    Naver Local Search API를 사용하여
    추천 지역의 맛집 리스트를 검색하는 클래스입니다.
    """
    def __init__(self):
        self.naver_id = os.getenv("NAVER_CLIENT_ID")
        self.naver_secret = os.getenv("NAVER_CLIENT_SECRET")

    def has_valid_key(self) -> bool:
        """
        사용 가능한 네이버 지도 검색 API 키가 존재하는지 확인합니다.
        """
        return bool(self.naver_id and self.naver_secret)

    def _clean_html_tags(self, text: str) -> str:
        """
        네이버 검색 결과 글자에 포함되어 나오는 두꺼운 글씨 태그(예: <b>...</b>) 등을 깨끗하게 청소하여 지웁니다.
        """
        if not text:
            return ""
        return re.sub(r'<[^>]*>', '', text)

    def _search_naver(self, city_name: str, limit: int, error_handler) -> list:
        """
        네이버 장소 검색 API를 이용하여 추천 도시의 맛집 리스트를 수집합니다.
        """
        url = "https://openapi.naver.com/v1/search/local.json"
        headers = {
            "X-Naver-Client-Id": self.naver_id,
            "X-Naver-Client-Secret": self.naver_secret
        }
        params = {
            "query": f"{city_name} 맛집",
            "display": limit
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 401 or response.status_code == 403:
                error_handler.add_error(
                    step="place_search",
                    error_type="AUTH_ERROR",
                    message=f"Naver API 인증 실패 (HTTP {response.status_code})"
                )
                return []
            
            if response.status_code != 200:
                error_handler.add_error(
                    step="place_search",
                    error_type="API_ERROR",
                    message=f"Naver API 에러 (HTTP {response.status_code}): {response.text}"
                )
                return []
            
            data = response.json()
            items = data.get("items", [])
            
            results = []
            for item in items:
                try:
                    x = float(item.get("mapx")) if item.get("mapx") else None
                    y = float(item.get("mapy")) if item.get("mapy") else None
                except ValueError:
                    x, y = None, None
                
                results.append({
                    "name": self._clean_html_tags(item.get("title", "")),
                    "address": item.get("roadAddress") or item.get("address", ""),
                    "category": item.get("category", ""),
                    "url": item.get("link", ""),
                    "x": x,
                    "y": y
                })
            
            if not results:
                error_handler.add_error(
                    step="place_search",
                    error_type="EMPTY_RESULT",
                    message=f"Naver API에서 '{city_name} 맛집' 검색 결과 0건"
                )
                
            return results

        except requests.exceptions.RequestException as e:
            error_handler.add_error(
                step="place_search",
                error_type="NETWORK_ERROR",
                message=f"Naver API 네트워크 연결 실패: {str(e)}"
            )
            return []

    def search_restaurants(self, city_name: str, error_handler, limit: int = 5) -> list:
        """
        추천된 도시명을 바탕으로 주변 식당을 검색합니다. 개발자 키가 등록되어 있지 않거나 에러 발생 시 기록장에 남기고 빈 목록을 반환해 다음 단계로 진행시킵니다.
        """
        if not self.has_valid_key():
            error_handler.add_error(
                step="place_search",
                error_type="AUTH_ERROR",
                message="설정된 네이버 API 키(Client ID/Secret)가 없어 맛집을 검색할 수 없습니다."
            )
            return []
        
        return self._search_naver(city_name, limit, error_handler)
