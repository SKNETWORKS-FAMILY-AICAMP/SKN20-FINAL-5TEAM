"""
Static HTML Collector

requests + BeautifulSoup를 사용하는 기본 수집기입니다.
정적 HTML 페이지에서 텍스트를 추출합니다.
"""

import requests
from bs4 import BeautifulSoup
from .base import BaseCollector


class StaticCollector(BaseCollector):
    """
    정적 HTML 수집기

    requests 라이브러리로 HTML을 가져오고,
    BeautifulSoup으로 텍스트를 추출합니다.

    장점:
    - 빠른 속도 (1-2초)
    - 간단한 구현
    - 서버 리소스 적게 사용

    단점:
    - JavaScript 렌더링 불가 (SPA 사이트 실패)
    - 동적 콘텐츠 추출 불가
    """

    def __init__(self, timeout: int = 10):
        """
        Args:
            timeout (int): 요청 타임아웃 (초). 기본값 10초.
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def collect(self, url: str) -> str:
        """
        정적 HTML에서 텍스트를 추출합니다.

        Args:
            url (str): 채용공고 URL

        Returns:
            str: 추출된 텍스트 (실패 시 빈 문자열)

        Raises:
            requests.RequestException: HTTP 요청 실패 시
        """
        try:
            # 1. HTTP 요청
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            # 2. HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')

            # 3. 불필요한 태그 제거 (script, style, nav, header, footer 등)
            for tag in soup(["script", "style", "meta", "link", "nav", "header", "footer",
                              "noscript", "iframe", "aside"]):
                tag.decompose()

            # 4. 채용공고 주요 콘텐츠 영역 우선 추출
            content_selectors = [
                "main", "article",
                "[class*='job']", "[class*='recruit']", "[class*='position']",
                "[class*='content']", "[class*='detail']", "[id*='content']",
                "section", ".wrap", "#wrap",
            ]
            for selector in content_selectors:
                try:
                    elements = soup.select(selector)
                    combined = '\n'.join(
                        el.get_text(separator='\n', strip=True)
                        for el in elements
                        if len(el.get_text(strip=True)) > 200
                    )
                    if len(combined) > 300:
                        print(f"[OK] StaticCollector: {len(combined)} 문자 추출 (selector: {selector})")
                        return combined
                except Exception:
                    continue

            # 5. 콘텐츠 선택자 실패 시 전체 body 텍스트 추출
            text = soup.get_text(separator='\n', strip=True)

            print(f"[OK] StaticCollector: {len(text)} 문자 추출 (full body)")
            return text

        except requests.RequestException as e:
            print(f"[FAIL] StaticCollector 실패: {e}")
            return ""

    def can_handle(self, url: str) -> bool:
        """
        모든 URL을 시도 가능합니다 (기본 수집기).

        Args:
            url (str): 채용공고 URL

        Returns:
            bool: 항상 True
        """
        return True
