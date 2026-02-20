"""
Wanted-optimized Collector

원티드 채용공고 전용 최적화 Collector입니다.
Playwright를 사용하되, 원티드의 HTML 구조에 맞춰 정확한 본문만 추출합니다.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .base import BaseCollector


class WantedCollector(BaseCollector):
    """
    원티드 전용 최적화 Collector

    원티드 채용공고 페이지의 구조를 정확히 파악하여
    광고, 헤더, 푸터를 제외하고 본문만 추출합니다.

    장점:
    - 노이즈 제거 (광고, 헤더, 푸터 등 제외)
    - 정확한 채용공고 본문만 추출
    - BrowserCollector보다 정확도 높음

    단점:
    - 원티드에만 사용 가능
    - Playwright 필요 (느림, 3-5초)
    """

    def __init__(self, timeout: int = 20000):
        """
        Args:
            timeout (int): 페이지 로딩 타임아웃 (밀리초). 기본값 20초.
        """
        self.timeout = timeout

    def collect(self, url: str) -> str:
        """
        원티드 채용공고 페이지에서 본문만 정확하게 추출합니다.

        추출 대상:
        - 채용 제목
        - 회사 정보
        - 주요 업무
        - 자격 요건 (필수/우대)
        - 근무 조건
        - 복리후생

        제외 대상:
        - 광고
        - 헤더/푸터
        - 사이드바
        - 추천 공고

        Args:
            url (str): 원티드 채용공고 URL

        Returns:
            str: 추출된 텍스트 (실패 시 빈 문자열)
        """
        try:
            with sync_playwright() as p:
                # 1. 브라우저 실행
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # 2. 원티드 페이지 로드
                print(f"[WANTED] WantedCollector: 원티드 페이지 로딩 중... ({url})")
                page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                # 3. 원티드 특정 요소 대기
                # 원티드는 Next.js/React 기반, JobDescription 컴포넌트 사용
                try:
                    # 메인 콘텐츠 영역이 로드될 때까지 대기
                    page.wait_for_selector('[class*="JobDescription"], [class*="JobDetail"], section', timeout=3000)
                except PlaywrightTimeout:
                    print(f"[WARN] 원티드 콘텐츠 영역 대기 실패, 전체 본문 추출 시도...")

                # 추가 렌더링 대기 (React 컴포넌트 로딩)
                page.wait_for_timeout(2000)

                # 4. 원티드 본문 추출 (최적화된 셀렉터)
                # 원티드는 CSS Modules를 사용하므로 클래스명이 동적일 수 있음
                # 따라서 contains 선택자 사용
                selectors_to_try = [
                    '[class*="JobDescription"]',  # CSS Modules: JobDescription_*
                    '[class*="JobDetail"]',       # CSS Modules: JobDetail_*
                    'section',                    # HTML5 section 태그
                    'article',                    # HTML5 article 태그
                    'main',                       # HTML5 main 태그
                    '[class*="Content"]'          # CSS Modules: Content_*
                ]

                extracted_text = ""

                for selector in selectors_to_try:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            for elem in elements:
                                text = elem.inner_text()
                                if text and len(text) > 100:
                                    extracted_text += text + "\n\n"
                    except Exception:
                        continue

                # 5. 셀렉터로 찾지 못했다면 전체 본문 추출
                if len(extracted_text) < 200:
                    print(f"[WARN] 원티드 최적화 셀렉터 실패, 전체 body 추출...")
                    extracted_text = page.inner_text('body')

                # 6. 브라우저 종료
                browser.close()

                print(f"[OK] WantedCollector: {len(extracted_text)} 문자 추출")
                return extracted_text.strip()

        except PlaywrightTimeout as e:
            print(f"[FAIL] WantedCollector 타임아웃: {e}")
            return ""
        except Exception as e:
            print(f"[FAIL] WantedCollector 실패: {e}")
            return ""

    def can_handle(self, url: str) -> bool:
        """
        원티드 URL만 처리 가능합니다.

        Args:
            url (str): 채용공고 URL

        Returns:
            bool: 원티드 URL이면 True, 아니면 False
        """
        return 'wanted.co.kr' in url.lower()
