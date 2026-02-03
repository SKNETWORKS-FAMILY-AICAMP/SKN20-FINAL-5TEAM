# 🚀 EvaluationResultScreen Design Tone Guide

## 개요

이 디자인은 **"우주 탐사 보고서 (Space Mission Report)"** 컨셉으로, SF/사이버펑크 미학과 글래스모피즘을 결합한 몰입형 UI입니다.

---

## 🎨 컬러 시스템

### Primary Colors (우주 배경)

| 변수명 | HEX | 용도 |
|--------|-----|------|
| `--space-deep` | `#0a0a1a` | 가장 어두운 배경 (딥 스페이스) |
| `--space-dark` | `#12122a` | 기본 배경색 |
| - | `#1a1a3a` | 그라데이션 종료 색상 |

### Accent Colors (네뷸라/성운)

| 변수명 | HEX | 용도 |
|--------|-----|------|
| `--nebula-purple` | `#6b5ce7` | 주 강조색, 버튼, 링크 |
| `--nebula-blue` | `#4fc3f7` | 보조 강조색, 성공/긍정 |
| `--nebula-pink` | `#f06292` | 경고/부정/개선필요 |
| `--star-white` | `#ffffff` | 별, 하이라이트 |

### Text Colors

| 변수명 | 값 | 용도 |
|--------|-----|------|
| `--text-primary` | `#e8eaed` | 주요 텍스트 |
| `--text-secondary` | `rgba(232, 234, 237, 0.7)` | 보조 텍스트, 라벨 |

### Glass Effect (글래스모피즘)

| 변수명 | 값 | 용도 |
|--------|-----|------|
| `--glass-bg` | `rgba(255, 255, 255, 0.05)` | 카드/박스 배경 |
| `--glass-border` | `rgba(255, 255, 255, 0.1)` | 카드 테두리 |

---

## 🔤 타이포그래피

### Font Families

```css
/* 제목, 라벨, UI 요소 */
font-family: 'Orbitron', sans-serif;

/* 본문 텍스트 */
font-family: 'Rajdhani', sans-serif;
```

### Font Scale

| 용도 | 크기 | Weight | Font |
|------|------|--------|------|
| 메인 타이틀 | `1.8rem` | 900 | Orbitron |
| 섹션 타이틀 | `0.85rem` | 700 | Orbitron |
| 라벨 | `0.7rem` | 700 | Orbitron |
| 본문 | `0.9rem - 1rem` | 400-500 | Rajdhani |
| 힌트 텍스트 | `0.75rem` | 400 | - |

### Letter Spacing

- 제목/라벨: `2px - 3px` (넓은 자간으로 SF 느낌 강조)
- 본문: 기본값

---

## 🎯 상태별 컬러 매핑

### Score-based States

| 상태 | 점수 범위 | Primary Color | 용도 |
|------|-----------|---------------|------|
| `excellent` | 80+ | `--nebula-blue` (#4fc3f7) | 성공, 승인 |
| `good` | 60-79 | `--nebula-purple` (#6b5ce7) | 양호, 검토 |
| `moderate` | 40-59 | 혼합 | 보통 |
| `poor` | 0-39 | `--nebula-pink` (#f06292) | 실패, 거부 |

### Verdict Stamps

| 상태 | 스탬프 텍스트 | Border/Glow Color |
|------|---------------|-------------------|
| excellent | "APPROVED" | Cyan glow |
| good | "REVIEW" | Purple glow |
| poor | "REJECTED" | Pink glow |

---

## 📦 컴포넌트 스타일 패턴

### Glass Card

```css
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}
```

### Gradient Border Effect

```css
.gradient-border {
  background: linear-gradient(135deg, var(--space-dark) 0%, #15153a 100%);
  border: 1px solid transparent;
  background-clip: padding-box;
}
```

### Glow Effect

```css
.glow {
  box-shadow: 0 0 20px rgba(107, 92, 231, 0.3);
}

/* 호버 시 강화 */
.glow:hover {
  box-shadow: 0 0 30px rgba(107, 92, 231, 0.5),
              0 0 60px rgba(107, 92, 231, 0.3);
}
```

### Primary Button

```css
.btn-primary {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 16px 40px;
  background: linear-gradient(135deg, #6b5ce7, #4fc3f7);
  color: white;
  border: none;
  border-radius: 30px;
  letter-spacing: 2px;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(107, 92, 231, 0.4);
}
```

---

## ✨ 애니메이션

### 1. Star Twinkle (별 반짝임)

```css
@keyframes twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}
```

### 2. Pulse Glow (맥동 발광)

```css
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(107, 92, 231, 0.3); }
  50% { box-shadow: 0 0 40px rgba(107, 92, 231, 0.6); }
}
```

### 3. Orbit (궤도 회전)

```css
@keyframes orbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

### 4. Stamp Animation (도장 찍기)

```css
@keyframes stamp {
  0% { transform: scale(3) rotate(-15deg); opacity: 0; }
  50% { transform: scale(1.1) rotate(-12deg); opacity: 0.8; }
  100% { transform: scale(1) rotate(-12deg); opacity: 1; }
}
```

### 5. Float (부유)

```css
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
```

---

## 🖼️ 배경 시스템

### Star Layers (다층 별 효과)

3개의 레이어로 깊이감 표현:

| 레이어 | 크기 | 애니메이션 속도 | Opacity |
|--------|------|----------------|---------|
| `.stars` | 1px | 50s | 0.5 |
| `.stars2` | 2px | 100s | 0.3 |
| `.stars3` | 3px | 150s | 0.2 |

### Nebula Overlay

```css
.nebula-overlay {
  background: 
    radial-gradient(ellipse at 20% 80%, rgba(107, 92, 231, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(79, 195, 247, 0.1) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(240, 98, 146, 0.05) 0%, transparent 70%);
}
```

---

## 📐 레이아웃 가이드

### Container

- 최대 너비: `700px`
- 패딩: `40px`
- Border Radius: `20px`

### Spacing Scale

| 크기 | 값 | 용도 |
|------|-----|------|
| xs | `8px` | 내부 간격 |
| sm | `15px` | 카드 패딩, 요소 간격 |
| md | `20-25px` | 섹션 마진 |
| lg | `30px` | 주요 섹션 간격 |
| xl | `40px` | 컨테이너 패딩 |

### Border Radius

| 용도 | 값 |
|------|-----|
| 버튼 | `30px` (pill shape) |
| 카드 | `12px` |
| 모달 | `16px` |
| 태그/뱃지 | `20px` |
| 아바타 | `50%` |

---

## 📱 반응형 브레이크포인트

```css
/* Mobile */
@media (max-width: 600px) {
  .pillar-grid { grid-template-columns: repeat(2, 1fr); }
  .feedback-grid { grid-template-columns: 1fr; }
  .stamp-mark { font-size: 0.7rem; }
  .report-title { font-size: 1.4rem; }
  .result-report { padding: 25px; }
}
```

---

## 🎭 디자인 무드 키워드

1. **Futuristic (미래적)** - SF 폰트, 네온 그라데이션
2. **Immersive (몰입형)** - 전체 화면, 우주 배경
3. **Professional (전문적)** - 리포트 형식, 체계적 구조
4. **Gamified (게임화)** - 점수 링, 스탬프, 레벨 표시
5. **Elegant (우아함)** - 글래스모피즘, 미묘한 애니메이션

---

## 🔧 사용 시 주의사항

1. **폰트 로드** - Google Fonts에서 Orbitron과 Rajdhani 필수 임포트
2. **다크 모드 전용** - 밝은 배경에서는 색상 대비 문제 발생
3. **애니메이션 성능** - 별 배경은 GPU 가속 필요, 저사양 기기 고려
4. **접근성** - 텍스트 contrast ratio 확인 필요 (특히 secondary text)

---

## 📝 Quick Copy - CSS Variables

```css
:root {
  /* Space Background */
  --space-deep: #0a0a1a;
  --space-dark: #12122a;
  
  /* Nebula Accents */
  --nebula-purple: #6b5ce7;
  --nebula-blue: #4fc3f7;
  --nebula-pink: #f06292;
  
  /* Text */
  --text-primary: #e8eaed;
  --text-secondary: rgba(232, 234, 237, 0.7);
  
  /* Glass Effect */
  --glass-bg: rgba(255, 255, 255, 0.05);
  --glass-border: rgba(255, 255, 255, 0.1);
}
```
