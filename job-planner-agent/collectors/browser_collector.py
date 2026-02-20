"""
Browser-based Collector

Playwright를 사용하여 JavaScript 렌더링이 필요한 SPA 사이트에서
텍스트를 추출합니다.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .base import BaseCollector


class BrowserCollector(BaseCollector):
    """
    브라우저 기반 수집기

    Playwright를 사용하여 실제 브라우저를 실행하고,
    JavaScript 렌더링 후 텍스트를 추출합니다.

    장점:
    - SPA(Single Page Application) 완벽 대응
    - JavaScript 동적 콘텐츠 추출 가능
    - 실제 사용자가 보는 것과 동일한 내용 수집

    단점:
    - 느림 (3-5초)
    - 메모리/CPU 사용량 높음 (200-300MB)
    - 서버 리소스 많이 소비
    """

    def __init__(self, timeout: int = 20000, wait_for_selector: str = "body"):
        """
        Args:
            timeout (int): 페이지 로딩 타임아웃 (밀리초). 기본값 20초.
            wait_for_selector (str): 대기할 CSS 선택자. 기본값 "body".
        """
        self.timeout = timeout
        self.wait_for_selector = wait_for_selector

    def collect(self, url: str) -> str:
        """
        브라우저로 페이지를 렌더링하고 텍스트를 추출합니다.

        Args:
            url (str): 채용공고 URL

        Returns:
            str: 추출된 텍스트 (실패 시 빈 문자열)
        """
        try:
            with sync_playwright() as p:
                # 1. 브라우저 실행 (headless 모드)
                browser = p.chromium.launch(headless=True)

                # 2. 새 페이지 열기
                page = browser.new_page()

                # 3. URL로 이동 (타임아웃 설정)
                print(f"[BROWSER] BrowserCollector: 페이지 로딩 중... ({url})")
                page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                # 4. 특정 요소가 나타날 때까지 대기 (렌더링 대기)
                try:
                    page.wait_for_selector(self.wait_for_selector, timeout=3000)
                except PlaywrightTimeout:
                    print(f"[WARN] 선택자 '{self.wait_for_selector}' 대기 시간 초과, 계속 진행...")

                # 5. 추가 대기 (동적 콘텐츠 로딩을 위해)
                page.wait_for_timeout(1000)  # 1초 추가 대기

                # 6. 텍스트 추출 (innerText로 실제 보이는 텍스트만)
                text = page.inner_text('body')

                # 7. 브라우저 종료
                browser.close()

                print(f"[OK] BrowserCollector: {len(text)} 문자 추출")
                return text

        except PlaywrightTimeout as e:
            print(f"[FAIL] BrowserCollector 타임아웃: {e}")
            return ""
        except Exception as e:
            print(f"[FAIL] BrowserCollector 실패: {e}")
            return ""

    def can_handle(self, url: str) -> bool:
        """
        모든 URL을 처리 가능합니다 (fallback으로 사용).

        Args:
            url (str): 채용공고 URL

        Returns:
            bool: 항상 True
        """
        return True
