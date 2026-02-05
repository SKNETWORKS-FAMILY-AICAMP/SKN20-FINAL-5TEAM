"""
모델 비교 시각화 스크립트

여러 모델의 평가 결과를 그래프로 비교
"""
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import matplotlib.font_manager as fm


def get_korean_font():
    """사용 가능한 한글 폰트 찾기"""
    korean_fonts = ['Malgun Gothic', 'NanumGothic', 'NanumBarunGothic',
                    'AppleGothic', 'D2Coding', 'Noto Sans KR', 'Noto Sans CJK KR']
    available_fonts = [f.name for f in fm.fontManager.ttflist]

    for font in korean_fonts:
        if font in available_fonts:
            return font

    return 'DejaVu Sans'


korean_font = get_korean_font()
matplotlib.rc('font', family=korean_font)
matplotlib.rcParams['axes.unicode_minus'] = False

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')


class ModelComparisonVisualizer:
    """모델 비교 시각화 클래스"""

    def __init__(self, analysis_file, output_dir):
        self.analysis_file = analysis_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(analysis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.metadata = data['metadata']
            self.analysis = data['analysis']
            self.summary = data['summary']

    def plot_consistency_comparison(self):
        """일관성 비교 바 차트"""
        print("📊 그래프 1: 일관성 비교 차트 생성 중...")

        models = self.summary['models']
        std_devs = [self.analysis[model]['consistency']['avg_std_dev'] for model in models]

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = ['#2ecc71' if std < 5 else '#f39c12' if std < 7 else '#e74c3c' for std in std_devs]
        bars = ax.bar(range(len(models)), std_devs, color=colors, alpha=0.7, edgecolor='black')

        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.set_ylabel('평균 표준편차 (점)', fontsize=12)
        ax.set_xlabel('모델', fontsize=12)
        ax.set_title('모델별 평가 일관성 비교\n(낮을수록 일관성 높음)', fontsize=14, fontweight='bold')
        ax.axhline(y=5, color='green', linestyle='--', linewidth=2, alpha=0.5, label='목표 기준 (5점)')
        ax.grid(axis='y', alpha=0.3)
        ax.legend()

        # 값 표시
        for i, (model, std) in enumerate(zip(models, std_devs)):
            ax.text(i, std + 0.2, f'{std:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / 'consistency_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_discrimination_comparison(self):
        """구분력 비교 바 차트"""
        print("📊 그래프 2: 구분력 비교 차트 생성 중...")

        models = self.summary['models']
        score_diffs = [self.analysis[model]['discrimination']['score_diff'] for model in models]

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = ['#2ecc71' if diff >= 30 else '#f39c12' if diff >= 20 else '#e74c3c' for diff in score_diffs]
        bars = ax.bar(range(len(models)), score_diffs, color=colors, alpha=0.7, edgecolor='black')

        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.set_ylabel('점수 차이 (우수 - 매우 미흡)', fontsize=12)
        ax.set_xlabel('모델', fontsize=12)
        ax.set_title('모델별 극단 케이스 구분력 비교\n(높을수록 구분력 높음)', fontsize=14, fontweight='bold')
        ax.axhline(y=30, color='green', linestyle='--', linewidth=2, alpha=0.5, label='목표 기준 (30점)')
        ax.grid(axis='y', alpha=0.3)
        ax.legend()

        # 값 표시
        for i, (model, diff) in enumerate(zip(models, score_diffs)):
            ax.text(i, diff + 1, f'{diff:.1f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / 'discrimination_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_performance_comparison(self):
        """성능 비교 차트 (속도 vs 비용)"""
        print("📊 그래프 3: 성능 비교 차트 생성 중...")

        models = self.summary['models']
        avg_times = [self.analysis[model]['performance']['avg_time'] for model in models]
        total_costs = [self.analysis[model]['performance']['total_cost'] for model in models]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # 속도 비교
        colors1 = ['#3498db' for _ in models]
        ax1.bar(range(len(models)), avg_times, color=colors1, alpha=0.7, edgecolor='black')
        ax1.set_xticks(range(len(models)))
        ax1.set_xticklabels(models, rotation=45, ha='right')
        ax1.set_ylabel('평균 응답 시간 (초)', fontsize=12)
        ax1.set_xlabel('모델', fontsize=12)
        ax1.set_title('모델별 평균 응답 시간\n(낮을수록 빠름)', fontsize=14, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        for i, (model, time) in enumerate(zip(models, avg_times)):
            ax1.text(i, time + 0.1, f'{time:.2f}s',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        # 비용 비교
        colors2 = ['#e74c3c' if cost > 0 else '#2ecc71' for cost in total_costs]
        ax2.bar(range(len(models)), total_costs, color=colors2, alpha=0.7, edgecolor='black')
        ax2.set_xticks(range(len(models)))
        ax2.set_xticklabels(models, rotation=45, ha='right')
        ax2.set_ylabel('총 비용 (USD)', fontsize=12)
        ax2.set_xlabel('모델', fontsize=12)
        ax2.set_title('모델별 총 비용\n(낮을수록 경제적)', fontsize=14, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        for i, (model, cost) in enumerate(zip(models, total_costs)):
            label = f'${cost:.4f}' if cost > 0 else 'Free'
            ax2.text(i, cost + (max(total_costs) * 0.02 if max(total_costs) > 0 else 0), label,
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / 'performance_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_quality_distribution(self):
        """품질별 점수 분포 비교"""
        print("📊 그래프 4: 품질별 점수 분포 비교 생성 중...")

        models = self.summary['models']
        quality_order = ['excellent', 'good', 'average', 'poor', 'very_poor']
        quality_labels = ['우수', '양호', '보통', '미흡', '매우\n미흡']

        fig, ax = plt.subplots(figsize=(14, 7))

        x = np.arange(len(quality_labels))
        width = 0.8 / len(models)

        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

        for i, model in enumerate(models):
            means = [self.analysis[model]['discrimination']['quality_means'][q] for q in quality_order]
            offset = (i - len(models) / 2) * width + width / 2
            ax.bar(x + offset, means, width, label=model, color=colors[i % len(colors)], alpha=0.7)

        ax.set_xlabel('품질 레벨', fontsize=12)
        ax.set_ylabel('평균 점수', fontsize=12)
        ax.set_title('모델별 품질 레벨 점수 분포', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(quality_labels)
        ax.legend(loc='upper right')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / 'quality_distribution.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_overall_ranking(self):
        """종합 순위 차트"""
        print("📊 그래프 5: 종합 순위 차트 생성 중...")

        ranking = self.summary['overall_ranking']['ranking']
        scores = [self.summary['overall_ranking']['scores'][model] for model in ranking]

        fig, ax = plt.subplots(figsize=(12, 8))

        colors = ['#FFD700', '#C0C0C0', '#CD7F32'] + ['#3498db'] * (len(ranking) - 3)
        bars = ax.barh(range(len(ranking)), scores, color=colors, alpha=0.7, edgecolor='black')

        ax.set_yticks(range(len(ranking)))
        ax.set_yticklabels([f"{i+1}. {model}" for i, model in enumerate(ranking)])
        ax.set_xlabel('종합 점수', fontsize=12)
        ax.set_title('모델 종합 순위\n(일관성, 구분력, 정확도, 속도, 비용, 오류율 종합)', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        # 점수 표시
        for i, (model, score) in enumerate(zip(ranking, scores)):
            ax.text(score + 0.1, i, f'{score:.2f}',
                   va='center', fontsize=10, fontweight='bold')

        # 1등 강조
        ax.text(0.02, 0.98, f'🏆 최우수 모델: {ranking[0]}',
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='gold', alpha=0.7))

        plt.tight_layout()
        output_file = self.output_dir / 'overall_ranking.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def plot_radar_chart(self):
        """레이더 차트 (모델별 종합 성능)"""
        print("📊 그래프 6: 레이더 차트 생성 중...")

        models = self.summary['models']

        # 지표 정규화 (0-100)
        metrics = ['일관성', '구분력', '순위정확도', '속도', '비용효율', '신뢰성']
        num_metrics = len(metrics)

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
        angles += angles[:1]

        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

        for idx, model in enumerate(models):
            # 각 지표를 0-100으로 정규화
            consistency = max(0, 100 - (self.analysis[model]['consistency']['avg_std_dev'] / 10 * 100))
            discrimination = min(100, self.analysis[model]['discrimination']['score_diff'] / 50 * 100)
            ranking = (self.analysis[model]['ranking']['kendall_tau'] + 1) / 2 * 100
            speed = max(0, 100 - (self.analysis[model]['performance']['avg_time'] / 10 * 100))
            cost_eff = 100 if self.analysis[model]['performance']['total_cost'] == 0 else max(0, 100 - (self.analysis[model]['performance']['total_cost'] * 100))
            reliability = 100 - self.analysis[model]['error_rate']['error_rate']

            values = [consistency, discrimination, ranking, speed, cost_eff, reliability]
            values += values[:1]

            ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx % len(colors)])
            ax.fill(angles, values, alpha=0.15, color=colors[idx % len(colors)])

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.set_title('모델별 종합 성능 레이더 차트\n(외곽으로 갈수록 우수)', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)

        plt.tight_layout()
        output_file = self.output_dir / 'radar_chart.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✅ 저장: {output_file}")

    def generate_all_visualizations(self):
        """모든 시각화 생성"""
        print("\n🎨 모델 비교 시각화 생성 시작...")

        self.plot_consistency_comparison()
        self.plot_discrimination_comparison()
        self.plot_performance_comparison()
        self.plot_quality_distribution()
        self.plot_overall_ranking()
        self.plot_radar_chart()

        print(f"\n✅ 모든 시각화 완료!")
        print(f"📁 저장 위치: {self.output_dir}")


if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent.parent / 'data' / 'validation' / 'model_comparison'
    analysis_file = data_dir / 'model_comparison_analysis.json'
    output_dir = data_dir / 'visualizations'

    visualizer = ModelComparisonVisualizer(analysis_file, output_dir)
    visualizer.generate_all_visualizations()
