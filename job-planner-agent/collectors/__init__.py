"""
Job Posting Data Collectors

데이터 수집 레이어 - 다양한 방법으로 채용공고 텍스트를 수집합니다.

Phase 1: BaseCollector, StaticCollector
Phase 2: BrowserCollector, CollectorRouter with fallback
Phase 3: SaraminCollector, JobkoreaCollector, WantedCollector (사이트별 최적화)
"""

from .base import BaseCollector
from .static_collector import StaticCollector
from .browser_collector import BrowserCollector
from .saramin_collector import SaraminCollector
from .jobkorea_collector import JobkoreaCollector
from .wanted_collector import WantedCollector
from .router import CollectorRouter

__all__ = [
    'BaseCollector',
    'StaticCollector',
    'BrowserCollector',
    'SaraminCollector',
    'JobkoreaCollector',
    'WantedCollector',
    'CollectorRouter'
]
