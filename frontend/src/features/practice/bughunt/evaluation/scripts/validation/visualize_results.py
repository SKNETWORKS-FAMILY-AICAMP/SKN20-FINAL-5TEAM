"""
Bug Hunt 평가 검증 결과 시각화

4가지 검증 결과를 그래프로 표현
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# 한글 폰트 설정 - 사용 가능한 폰트 자동 탐지
import matplotlib.font_manager as fm

def get_korean_font():
    """사용 가능한 한글 폰트 찾기"""
    # 선호하는 한글 폰트 목록
    korean_fonts = ['Malgun Gothic', 'NanumGothic', 'NanumBarunGothic',
                    'AppleGothic', 'D2Coding', 'Noto Sans KR', 'Noto Sans CJK KR']

    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in korean_fonts:
        if font in available_fonts:
            return font

    # 한글 폰트가 없으면 DejaVu Sans 사용 (경고 무시)
    return 'DejaVu Sans'

korean_font = get_korean_font()
matplotlib.rc('font', family=korean_font)
matplotlib.rcParams['axes.unicode_minus'] = False

# 한글 폰트가 없을 경우 경고 무시
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class ResultVisualizer:
    """결과 시각화 클래스"""

    def __init__(self, analysis_results_file, output_dir):
        self.analysis_results_file = analysis_results_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(analysis_results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)

    def plot_consistency(self):
        """검증 1: 평가 일관성 박스플롯"""
        print("📊 그래프 1: 평가 일관성 박스플롯 생성 중...")

        details = self.results['consistency']['details']

        # 품질별 데이터 분리
        quality_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
        quality_labels = ['우수', '양호', '보통', '미흡', '매우\n미흡']
        quality_data = {q: [] for q in quality_order}

        for item in details:
            quality_data[item['quality']].append(item['scores'])

        # 박스플롯
        fig, ax = plt.subplots(figsize=(12, 6))

        positions = []
        data_to_plot = []

        for q in quality_order:
            if quality_data[q]:
                # 각 샘플의 여러 trial을 평탄화
                flattened = [score for scores in quality_data[q] for score in scores]
                data_to_plot.append(flattened)
                positions.append(len(data_to_plot))

        bp = ax.boxplot(data_to_plot, positions=positions,
                       widths=0.6, patch_artist=True,
                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2))

        ax.set_xticks(positions)
        ax.set_xticklabels(quality_labels[:len(positions)])
        ax.set_ylabel('평가 점수', fontsize=12)
        ax.set_xlabel('품질 레벨', fontsize=12)
        ax.set_title('평가 일관성: 품질별 점수 분포\n(각 샘플을 5회 반복 평가)', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        # 통계 정보 추가
        avg_std = self.results['consistency']['avg_std_dev']
        ax.text(0.02, 0.98, f'평균 표준편차: {avg_std:.2f}점\n목표: ≤5점',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        output_file = self.output_dir / 'consistency_boxplot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_discrimination(self):
        """검증 2: 극단 케이스 구분력 바 차트"""
        print("📊 그래프 2: 극단 케이스 구분력 바 차트 생성 중...")

        all_scores = self.results['discrimination']['all_scores']

        # 품질별 평균 점수
        quality_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
        quality_labels = ['우수', '양호', '보통', '미흡', '매우 미흡']
        quality_means = []
        quality_stds = []

        for q in quality_order:
            scores = [v['score'] for v in all_scores.values() if v['quality'] == q]
            if scores:
                quality_means.append(np.mean(scores))
                quality_stds.append(np.std(scores))
            else:
                quality_means.append(0)
                quality_stds.append(0)

        # 바 차트
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#95a5a6']
        bars = ax.bar(range(len(quality_means)), quality_means,
                     yerr=quality_stds, capsize=5,
                     color=colors, alpha=0.7, edgecolor='black')

        ax.set_xticks(range(len(quality_labels)))
        ax.set_xticklabels(quality_labels)
        ax.set_ylabel('평균 점수', fontsize=12)
        ax.set_xlabel('품질 레벨', fontsize=12)
        ax.set_title('극단 케이스 구분력: 품질별 평균 점수', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3)

        # 점수 표시
        for i, (mean, std) in enumerate(zip(quality_means, quality_stds)):
            ax.text(i, mean + std + 3, f'{mean:.1f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        # 차이 표시
        score_diff = self.results['discrimination']['score_diff']
        ax.text(0.02, 0.98,
                f'우수 vs 매우 미흡 점수 차이:\n{score_diff:.1f}점 (목표: ≥30점)',
                transform=ax.transAxes, fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if score_diff >= 30 else 'lightyellow', alpha=0.5))

        plt.tight_layout()
        output_file = self.output_dir / 'discrimination_barchart.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_correlation(self):
        """검증 4: 규칙 기반 vs LLM 상관관계 산점도"""
        print("📊 그래프 3: 규칙 기반 vs LLM 상관관계 산점도 생성 중...")

        rule_scores = self.results['convergent_validity']['rule_scores']
        llm_scores = self.results['convergent_validity']['llm_scores']
        pearson_r = self.results['convergent_validity']['pearson_r']

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.scatter(rule_scores, llm_scores, alpha=0.6, s=80, edgecolors='black', linewidth=0.5)

        # 회귀선
        z = np.polyfit(rule_scores, llm_scores, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(rule_scores), max(rule_scores), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, label=f'회귀선: y={z[0]:.2f}x+{z[1]:.2f}')

        # 대각선 (완벽한 일치)
        max_val = max(max(rule_scores), max(llm_scores))
        ax.plot([0, max_val], [0, max_val], 'k:', alpha=0.3, linewidth=1, label='완벽한 일치')

        ax.set_xlabel('규칙 기반 점수', fontsize=12)
        ax.set_ylabel('LLM 평가 점수', fontsize=12)
        ax.set_title('규칙 기반 vs LLM 평가 상관관계', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(alpha=0.3)
        ax.legend(loc='upper left')

        # 상관계수 표시
        ax.text(0.98, 0.02, f'Pearson r = {pearson_r:.3f}\np < 0.001\n목표: r ≥ 0.65',
                transform=ax.transAxes, fontsize=10,
                horizontalalignment='right', verticalalignment='bottom',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if pearson_r >= 0.65 else 'lightyellow', alpha=0.5))

        plt.tight_layout()
        output_file = self.output_dir / 'correlation_scatter.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_summary(self):
        """종합 요약 차트"""
        print("📊 그래프 4: 종합 검증 요약 차트 생성 중...")

        summary = self.results['summary']['summary']

        metrics = ['일관성\n(표준편차)', '극단 구분\n(점수 차이)', '순위 정확도\n(Kendall τ)', '규칙 상관\n(Pearson r)']
        values = [
            summary['consistency']['avg_std_dev'] / 5 * 100,  # 0-5점 → 0-100%
            summary['discrimination']['score_diff'] / 30 * 100,  # 30점 이상 → 100%
            summary['ranking']['avg_kendall_tau'] * 100,  # 0-1 → 0-100%
            summary['convergent_validity']['pearson_r'] * 100  # 0-1 → 0-100%
        ]
        values = [min(100, v) for v in values]  # 100 넘지 않도록

        passed = [
            summary['consistency']['passed'],
            summary['discrimination']['passed'],
            summary['ranking']['passed'],
            summary['convergent_validity']['passed']
        ]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#2ecc71' if p else '#e74c3c' for p in passed]
        bars = ax.barh(range(len(metrics)), values, color=colors, alpha=0.7, edgecolor='black')

        # 목표선 (100%)
        ax.axvline(x=100, color='blue', linestyle='--', linewidth=2, label='목표 (100%)')

        ax.set_yticks(range(len(metrics)))
        ax.set_yticklabels(metrics)
        ax.set_xlabel('달성도 (%)', fontsize=12)
        ax.set_title('Bug Hunt 평가 시스템 검증 종합 결과', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 120)
        ax.grid(axis='x', alpha=0.3)
        ax.legend()

        # 값 표시
        for i, (v, p) in enumerate(zip(values, passed)):
            status = '✅' if p else '❌'
            ax.text(v + 2, i, f'{v:.1f}% {status}',
                   va='center', fontsize=10, fontweight='bold')

        # 전체 통과 여부
        all_passed = all(passed)
        result_text = '✅ 전체 통과' if all_passed else '⚠️ 일부 미달'
        ax.text(0.02, 0.98, result_text,
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen' if all_passed else 'lightyellow', alpha=0.7))

        plt.tight_layout()
        output_file = self.output_dir / 'summary_chart.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def generate_all_visualizations(self):
        """모든 시각화 생성"""
        print("\n🎨 시각화 생성 시작...")

        self.plot_consistency()
        self.plot_discrimination()
        self.plot_correlation()
        self.plot_summary()

        print(f"\n✅ 모든 시각화 완료!")
        print(f"📁 저장 위치: {self.output_dir}")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation'
    analysis_results = data_dir / 'analysis_results.json'
    output_dir = data_dir / 'visualizations'

    visualizer = ResultVisualizer(analysis_results, output_dir)
    visualizer.generate_all_visualizations()
