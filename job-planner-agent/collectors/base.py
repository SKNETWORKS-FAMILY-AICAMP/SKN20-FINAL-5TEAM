"""
Base Collector Interface

모든 Collector가 구현해야 하는 기본 인터페이스입니다.
"""

from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """
    데이터 수집기 기본 클래스

    모든 Collector는 이 클래스를 상속받아 collect() 메서드를 구현해야 합니다.
    """

    @abstractmethod
    def collect(self, url: str) -> str:
        """
        URL에서 텍스트 데이터를 수집합니다.

        Args:
            url (str): 채용공고 URL

        Returns:
            str: 추출된 텍스트 (실패 시 빈 문자열)

        Raises:
            Exception: 수집 중 오류 발생 시
        """
        pass

    def can_handle(self, url: str) -> bool:
        """
        이 Collector가 해당 URL을 처리할 수 있는지 확인합니다.

        Args:
            url (str): 채용공고 URL

        Returns:
            bool: 처리 가능 여부
        """
        return True  # 기본적으로 모든 URL 처리 가능
