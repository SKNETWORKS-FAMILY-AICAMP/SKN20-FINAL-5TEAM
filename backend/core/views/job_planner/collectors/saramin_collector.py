"""
Saramin-optimized Collector

사람인 채용공고 전용 최적화 Collector입니다.
사람인은 SSR 기반으로 requests + BeautifulSoup으로 충분히 추출 가능합니다.
(Playwright는 사람인에서 차단됨)
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from .base import BaseCollector


class SaraminCollector(BaseCollector):
    """
    사람인 전용 최적화 Collector

    사람인은 SSR(Server-Side Rendering) 사이트로,
    Playwright 없이 requests + BeautifulSoup으로 본문 추출이 가능합니다.
    (Playwright/headless 브라우저는 사람인에서 차단됨)
    """

    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def collect(self, url: str) -> str:
        """
        사람인 채용공고 페이지에서 본문을 추출합니다.
        requests + BeautifulSoup 사용 (SSR 사이트).
        """
        try:
            # relay URL → 직접 view URL 변환
            actual_url = self._resolve_relay_url(url)
            if actual_url != url:
                print(f"[SARAMIN] relay URL 변환: {url[:60]}... -> {actual_url}")

            # HTTP 요청
            print(f"[SARAMIN] SaraminCollector: 페이지 요청 중... ({actual_url})")
            resp = requests.get(actual_url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')

            # 불필요한 태그 제거
            for tag in soup(["script", "style", "meta", "link", "nav", "header",
                             "footer", "noscript", "aside"]):
                tag.decompose()

            extracted_text = ""

            # 1차: .wrap_jv_cont (채용공고 메인 래퍼, 가장 정확)
            wrap = soup.select_one('.wrap_jv_cont')
            if wrap:
                extracted_text = wrap.get_text(separator='\n', strip=True)
                if len(extracted_text) > 200:
                    print(f"[OK] SaraminCollector: .wrap_jv_cont에서 {len(extracted_text)}자 추출")
                    return extracted_text

            # 2차: .user_content (회사가 작성한 본문)
            user_content = soup.select_one('.user_content')
            if user_content:
                extracted_text = user_content.get_text(separator='\n', strip=True)
                if len(extracted_text) > 100:
                    print(f"[OK] SaraminCollector: .user_content에서 {len(extracted_text)}자 추출")
                    return extracted_text

            # 3차: .jv_detail (채용 상세 영역) - 여러 개 합침
            details = soup.select('.jv_detail')
            if details:
                parts = []
                for d in details:
                    t = d.get_text(separator='\n', strip=True)
                    if len(t) > 50:
                        parts.append(t)
                if parts:
                    extracted_text = '\n\n'.join(parts)
                    if len(extracted_text) > 200:
                        print(f"[OK] SaraminCollector: .jv_detail에서 {len(extracted_text)}자 추출")
                        return extracted_text

            # 4차: .jv_cont (채용 콘텐츠) - 여러 개 합침
            conts = soup.select('.jv_cont')
            if conts:
                parts = []
                for c in conts:
                    t = c.get_text(separator='\n', strip=True)
                    if len(t) > 50:
                        parts.append(t)
                if parts:
                    extracted_text = '\n\n'.join(parts)
                    if len(extracted_text) > 200:
                        print(f"[OK] SaraminCollector: .jv_cont에서 {len(extracted_text)}자 추출")
                        return extracted_text

            # 5차: #content 전체
            content = soup.select_one('#content')
            if content:
                extracted_text = content.get_text(separator='\n', strip=True)
                if len(extracted_text) > 200:
                    print(f"[OK] SaraminCollector: #content에서 {len(extracted_text)}자 추출")
                    return extracted_text

            # 최종 fallback: body 전체
            extracted_text = soup.get_text(separator='\n', strip=True)
            print(f"[WARN] SaraminCollector: 전체 body fallback ({len(extracted_text)}자)")
            return extracted_text

        except requests.RequestException as e:
            print(f"[FAIL] SaraminCollector 요청 실패: {e}")
            return ""
        except Exception as e:
            print(f"[FAIL] SaraminCollector 실패: {e}")
            return ""

    def _resolve_relay_url(self, url: str) -> str:
        """
        사람인 relay/view URL을 실제 채용공고 URL로 변환합니다.

        relay URL 예시:
          https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx=52948032&...
        실제 URL 예시:
          https://www.saramin.co.kr/zf_user/jobs/view?rec_idx=52948032
        """
        if '/relay/view' in url:
            params = parse_qs(urlparse(url).query)
            rec_idx = params.get('rec_idx', [None])[0]
            if rec_idx:
                return f"https://www.saramin.co.kr/zf_user/jobs/view?rec_idx={rec_idx}"
        return url

    def can_handle(self, url: str) -> bool:
        return 'saramin.co.kr' in url.lower()
