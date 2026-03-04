"""
Jobkorea-optimized Collector

잡코리아 채용공고 전용 최적화 Collector입니다.
잡코리아는 메인 페이지(요약) + iframe(상세 내용) 구조이므로
두 콘텐츠를 합쳐서 추출합니다.
"""

import re
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from .base import BaseCollector


class JobkoreaCollector(BaseCollector):
    """
    잡코리아 전용 최적화 Collector

    잡코리아 채용공고는 두 부분으로 나뉨:
    1. 메인 페이지: 요약 정보 (직무, 조건, 지역 등)
    2. iframe (GI_Read_Comt_Ifrm): 상세 채용 내용 (업무, 자격요건, 우대사항 등)

    Playwright로 메인 페이지 로드 후 main 태그 + iframe 내부 텍스트를 합침.
    """

    def __init__(self, timeout: int = 20000):
        self.timeout = timeout

    def collect(self, url: str) -> str:
        """
        잡코리아 채용공고 페이지에서 메인 + iframe 콘텐츠를 합쳐 추출합니다.
        """
        try:
            with sync_playwright() as p:
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
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                print(f"[JOBKOREA] JobkoreaCollector: 페이지 로딩 중... ({url})")
                page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')

                # 콘텐츠 로딩 대기
                try:
                    page.wait_for_selector('main', timeout=10000)
                except PlaywrightTimeout:
                    print(f"[WARN] 잡코리아 main 태그 대기 실패, 계속 진행...")

                # iframe 로딩 대기
                page.wait_for_timeout(2000)

                extracted_parts = []

                # 1. 메인 페이지 콘텐츠 (main 태그)
                try:
                    main_elem = page.query_selector('main')
                    if main_elem:
                        main_text = main_elem.inner_text()
                        if len(main_text) > 50:
                            extracted_parts.append(main_text)
                            print(f"[JOBKOREA] main 태그: {len(main_text)}자 추출")
                except Exception:
                    pass

                # 2. iframe 콘텐츠 (GI_Read_Comt_Ifrm - 상세 채용 내용)
                try:
                    for frame in page.frames:
                        if frame == page.main_frame:
                            continue
                        if 'Comt_Ifrm' in frame.url or 'GI_Read' in frame.url:
                            iframe_text = frame.inner_text('body')
                            if len(iframe_text) > 50:
                                extracted_parts.append(iframe_text)
                                print(f"[JOBKOREA] iframe: {len(iframe_text)}자 추출 ({frame.url[:80]})")
                            break
                except Exception as e:
                    print(f"[WARN] 잡코리아 iframe 추출 실패: {e}")

                # 3. iframe을 못 찾았으면 requests로 직접 가져오기
                if len(extracted_parts) < 2:
                    iframe_text = self._fetch_iframe_content(url)
                    if iframe_text:
                        extracted_parts.append(iframe_text)

                # 4. main도 못 잡았으면 body 전체
                if not extracted_parts:
                    print(f"[WARN] 잡코리아 셀렉터 실패, 전체 body 추출...")
                    extracted_parts.append(page.inner_text('body'))

                browser.close()

                extracted_text = '\n\n'.join(extracted_parts)
                print(f"[OK] JobkoreaCollector: {len(extracted_text)}자 추출")
                return extracted_text.strip()

        except PlaywrightTimeout as e:
            print(f"[FAIL] JobkoreaCollector 타임아웃: {e}")
            return ""
        except Exception as e:
            print(f"[FAIL] JobkoreaCollector 실패: {e}")
            return ""

    def _fetch_iframe_content(self, url: str) -> str:
        """
        잡코리아 iframe URL을 직접 requests로 가져옵니다.
        URL에서 공고번호(Gno)를 추출하여 iframe URL을 구성합니다.
        """
        try:
            # URL에서 공고번호 추출 (예: /Recruit/GI_Read/46495498 -> 46495498)
            match = re.search(r'/GI_Read/(\d+)', url)
            if not match:
                return ""

            gno = match.group(1)
            iframe_url = f"https://www.jobkorea.co.kr/Recruit/GI_Read_Comt_Ifrm?Gno={gno}"

            headers = {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/120.0.0.0 Safari/537.36'
                ),
            }
            resp = requests.get(iframe_url, headers=headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(["script", "style"]):
                tag.decompose()

            text = soup.get_text(separator='\n', strip=True)
            if len(text) > 50:
                print(f"[JOBKOREA] iframe 직접 요청: {len(text)}자 추출")
                return text
        except Exception as e:
            print(f"[WARN] 잡코리아 iframe 직접 요청 실패: {e}")

        return ""

    def can_handle(self, url: str) -> bool:
        return 'jobkorea.co.kr' in url.lower()
