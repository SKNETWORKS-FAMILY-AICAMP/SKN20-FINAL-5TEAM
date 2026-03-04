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
                # 1. 브라우저 실행 (봇 감지 우회 설정)
                browser = p.chromium.launch(
                    headless=True,
                    args=['--disable-blink-features=AutomationControlled']
                )
                context = browser.new_context(
                    user_agent=(
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/120.0.0.0 Safari/537.36'
                    ),
                    viewport={'width': 1920, 'height': 1080},
                )
                page = context.new_page()
                # webdriver 속성 숨김 (봇 감지 우회)
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                # 2. 원티드 페이지 로드 (domcontentloaded로 빠르게 로드 후 콘텐츠 대기)
                print(f"[WANTED] WantedCollector: 원티드 페이지 로딩 중... ({url})")
                page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                # 3. 원티드 콘텐츠 렌더링 대기 (React 하이드레이션)
                try:
                    page.wait_for_selector(
                        '[class*="JobDescription"], [class*="JobDetail"], [class*="position"], main',
                        timeout=10000
                    )
                except PlaywrightTimeout:
                    print(f"[WARN] 원티드 콘텐츠 영역 대기 실패, 전체 본문 추출 시도...")

                # 3.5. "더보기" 버튼 모두 클릭 (접힌 콘텐츠 펼치기)
                clicked = 0
                try:
                    # JS로 텍스트 기반 버튼 탐색 및 클릭 (CSS Modules 클래스명 변동에 강건)
                    clicked = page.evaluate("""() => {
                        let count = 0;
                        const buttons = document.querySelectorAll('button, a, span[role="button"]');
                        for (const btn of buttons) {
                            const text = btn.textContent.trim();
                            if (text.includes('더보기') || text.includes('펼치기') || text.includes('상세 정보')) {
                                btn.click();
                                count++;
                            }
                        }
                        return count;
                    }""")
                    if clicked:
                        page.wait_for_timeout(1000)
                        print(f"[WANTED] '더보기' 버튼 {clicked}개 클릭 완료")
                except Exception:
                    print(f"[WANTED] '더보기' 버튼 없음 또는 클릭 실패 (무시)")

                # 4. 원티드 본문 추출 (정확한 셀렉터 우선, 광범위 셀렉터는 fallback)
                extracted_text = ""

                # 4-1. 정확한 채용공고 본문 셀렉터 (노이즈 최소화)
                precise_selectors = [
                    '[class*="JobDescription"]',  # CSS Modules: JobDescription_*
                    '[class*="JobDetail"]',       # CSS Modules: JobDetail_*
                    '[class*="job-description"]', # kebab-case 클래스
                    '[class*="JobPosting"]',      # JobPosting 컴포넌트
                ]

                for selector in precise_selectors:
                    try:
                        elements = page.query_selector_all(selector)
                        if elements:
                            for elem in elements:
                                text = elem.inner_text()
                                if text and len(text) > 100:
                                    extracted_text += text + "\n\n"
                    except Exception:
                        continue

                # 4-2. 정확한 셀렉터로 충분한 텍스트를 못 잡았으면 광범위 셀렉터 시도
                if len(extracted_text) < 500:
                    print(f"[WARN] 정확한 셀렉터 부족 ({len(extracted_text)}자), 광범위 셀렉터 시도...")
                    for selector in ['article', 'main']:
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
