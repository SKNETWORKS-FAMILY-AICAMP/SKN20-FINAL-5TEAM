/**
 * Architecture Practice API Service (Enhanced Version)
 * 질문별 모범 답안 비교, 파트별 점수 근거 명시, 종합 평가 로직 포함
 *
 * 7단계 프로세스 (sys-arc.md 기반):
 * 3. 질문 및 꼬리질문: txt 파일(6대 기둥) 기반, 전문 용어를 시나리오로 번역
 * 7. 맥락 유지: 고정 맥락 + 유동 맥락 세션 동안 유지
 */

import architectureProblems from '@/data/architecture.json';

// 6대 기둥 txt 파일 import (Vite ?raw 쿼리 사용)
import costTxt from '@/data/비용.txt?raw';
import operationalTxt from '@/data/운영유용성.txt?raw';
import performanceTxt from '@/data/최적화.txt?raw';
import reliabilityTxt from '@/data/신뢰성.txt?raw';
import securityTxt from '@/data/보안.txt?raw';
import sustainabilityTxt from '@/data/지속가능성.txt?raw';

const getApiKey = () => import.meta.env.VITE_OPENAI_API_KEY;

/**
 * 6대 기둥 질문 전략 (txt 파일 기반)
 */
const PILLAR_STRATEGIES = {
  costOptimization: {
    name: '비용 최적화',
    content: costTxt,
    keywords: ['비용', '가격', '요금', '유휴', 'spot', '약정', 'CUD']
  },
  operationalExcellence: {
    name: '운영 우수성',
    content: operationalTxt,
    keywords: ['배포', '자동화', 'CI/CD', '모니터링', '알람', '롤백', '장애 대응']
  },
  performanceOptimization: {
    name: '성능 최적화',
    content: performanceTxt,
    keywords: ['성능', '지연', '응답', '병목', '캐시', '확장', '오토스케일링']
  },
  reliability: {
    name: '신뢰성',
    content: reliabilityTxt,
    keywords: ['장애', '복구', '가용성', 'SLO', 'SPOF', '이중화', '백업']
  },
  securityPrivacyCompliance: {
    name: '보안',
    content: securityTxt,
    keywords: ['보안', '인증', '암호화', 'IAM', '접근 제어', '데이터 보호']
  },
  sustainability: {
    name: '지속 가능성',
    content: sustainabilityTxt,
    keywords: ['탄소', '에너지', '효율', '서버리스', '유휴', '친환경']
  }
};

/**
 * 아키텍처와 사용자 설명 기반으로 관련 기둥 선택
 */
function selectRelevantPillars(components, userExplanation) {
  const combinedText = `${components.map(c => c.text).join(' ')} ${userExplanation}`.toLowerCase();

  const scores = Object.entries(PILLAR_STRATEGIES).map(([id, pillar]) => {
    const matchCount = pillar.keywords.filter(kw => combinedText.includes(kw.toLowerCase())).length;
    return { id, name: pillar.name, score: matchCount };
  });

  // 점수순 정렬, 상위 3개 선택 (최소 1개는 항상 포함)
  scores.sort((a, b) => b.score - a.score);
  const selected = scores.slice(0, 3).filter(s => s.score > 0);

  // 매칭이 없으면 기본 3개 선택
  if (selected.length === 0) {
    return ['reliability', 'performanceOptimization', 'operationalExcellence'];
  }

  return selected.map(s => s.id);
}

/**
 * OpenAI API 호출 기본 함수
 */
async function callOpenAI(prompt, options = {}) {
  const {
    model = 'gpt-4o-mini',
    maxTokens = 1500,
    temperature = 0.4,
    systemMessage = null
  } = options;

  const messages = [];
  if (systemMessage) {
    messages.push({ role: 'system', content: systemMessage });
  }
  messages.push({ role: 'user', content: prompt });

  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getApiKey()}`
      },
      body: JSON.stringify({
        model,
        messages,
        max_tokens: maxTokens,
        temperature
      })
    });

    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    const data = await response.json();
    return data.choices[0].message.content.trim();
  } catch (error) {
    console.error('OpenAI Call Error:', error);
    throw error;
  }
}

/**
 * 문제 데이터 로드
 */
export async function fetchProblems() {
  return architectureProblems;
}

/**
 * 사용자 설명 기반 꼬리질문 생성 (7단계 프로세스 적용)
 *
 * sys-arc.md 기반:
 * - 3단계: txt 파일(6대 기둥) 기반 질문, 전문 용어를 시나리오로 번역
 * - 7단계: 맥락 유지 (고정 맥락 + 유동 맥락)
 *
 * @param {Object} problem - 문제 데이터
 * @param {Array} components - 배치된 컴포넌트
 * @param {Array} connections - 연결 관계
 * @param {string} mermaidCode - 머메이드 다이어그램 코드
 * @param {string} userExplanation - 사용자 설명
 * @param {Object} sessionContext - 세션 맥락 (고정 + 유동)
 */
export async function generateFollowUpQuestions(problem, components, connections, mermaidCode, userExplanation, sessionContext = {}) {
  const componentList = components.map(c => `- ${c.text} (타입: ${c.type})`).join('\n');
  const connectionList = connections.map(conn => {
    const from = components.find(c => c.id === conn.from);
    const to = components.find(c => c.id === conn.to);
    return from && to ? `- ${from.text} → ${to.text}` : null;
  }).filter(Boolean).join('\n');

  const scenario = problem?.scenario || '';
  const rubricNfr = problem?.rubricNonFunctional || problem?.rubric_non_functional || [];
  const nfrTopics = rubricNfr.map(r => `${r.category}: ${r.question_intent}`).join('\n') || '없음';

  // 컴포넌트 타입별로 정리
  const componentTypes = [...new Set(components.map(c => c.type))];
  const hasCache = components.some(c => c.type === 'cache' || c.text.toLowerCase().includes('cache') || c.text.toLowerCase().includes('redis'));
  const hasQueue = components.some(c => c.type === 'queue' || c.type === 'broker' || c.text.toLowerCase().includes('queue') || c.text.toLowerCase().includes('kafka'));
  const hasLoadBalancer = components.some(c => c.type === 'loadbalancer' || c.text.toLowerCase().includes('load') || c.text.toLowerCase().includes('lb'));
  const hasDatabase = components.some(c => c.type === 'rdbms' || c.type === 'nosql' || c.text.toLowerCase().includes('db') || c.text.toLowerCase().includes('database'));

  // 7단계: 세션 맥락 유지
  const fixedContext = sessionContext.fixedContext || '';
  const dynamicContext = sessionContext.dynamicContext || '';
  const previousFacts = sessionContext.facts || [];

  // 3단계: 관련 기둥 선택 및 txt 파일 기반 질문 전략 로드
  const relevantPillars = selectRelevantPillars(components, userExplanation);
  const pillarStrategies = relevantPillars.map(id => {
    const pillar = PILLAR_STRATEGIES[id];
    return `### ${pillar.name} 질문 전략\n${pillar.content}`;
  }).join('\n\n');

  const prompt = `당신은 시스템 아키텍처 면접관입니다.
학생이 설계한 아키텍처와 그에 대한 설명을 분석하여, 꼬리질문 3개를 생성하세요.

---

## 🎯 7단계 프로세스 맥락

### 고정 맥락 (아키텍처 + 첫 설명)
${fixedContext || '(첫 질문)'}

### 유동 맥락 (이전 Q&A 요약)
${dynamicContext || '(이전 대화 없음)'}

### 파악된 사실
${previousFacts.length > 0 ? previousFacts.map(f => `- ${f}`).join('\n') : '(아직 없음)'}

---

## 문제 정보
- 제목: ${problem?.title || '시스템 아키텍처 설계'}
- 시나리오: ${scenario}

### 평가 기준:
${nfrTopics}

---

## 📊 학생의 아키텍처 다이어그램 (Mermaid)

\`\`\`mermaid
${mermaidCode || 'graph LR\n    %% 컴포넌트 없음'}
\`\`\`

## ⚠️ 중요: 학생이 실제로 배치한 컴포넌트 목록 (이것만 기준으로 질문!)
### 컴포넌트 (${components.length}개):
${componentList || '없음'}

### 컴포넌트 타입: ${componentTypes.join(', ')}
- 캐시 포함 여부: ${hasCache ? '있음' : '없음'}
- 메시지 큐 포함 여부: ${hasQueue ? '있음' : '없음'}
- 로드밸런서 포함 여부: ${hasLoadBalancer ? '있음' : '없음'}
- 데이터베이스 포함 여부: ${hasDatabase ? '있음' : '없음'}

### 연결 관계 (${connections.length}개):
${connectionList || '없음'}

## 학생의 설명
"${userExplanation}"

---

## 📚 6대 기둥 질문 전략 (txt 파일 기반 - 상황 기반 질문으로 번역!)

${pillarStrategies}

---

## ⚠️ 핵심 규칙 (반드시 준수!)

### 절대 금지 사항
1. **없는 컴포넌트에 대해 질문하지 말 것**
   - 캐시가 없으면 → 캐시 관련 질문 금지
   - 메시지 큐가 없으면 → 비동기 처리 질문 금지
   - 로드밸런서가 없으면 → 부하 분산 질문 금지

2. **학생이 배치한 컴포넌트만** 기준으로 질문해야 함
   - 위 '컴포넌트 목록'에 있는 것만 언급 가능

3. **전문 용어를 상황/시나리오로 번역**하여 질문 (txt 파일 참고)
   - (X) "SLO를 정의했나요?"
   - (O) "서비스에 장애가 났을 때, 관리자가 알기 전에 시스템이 먼저 알려주는 알람 기능이 있나요?"

### 질문 생성 기준 (txt 파일 '대화 규칙' 참고)
1. 한 번에 **하나의 질문**만
2. 학생 답변에서 **부족한 부분**이 감지되면 날카로운 **꼬리질문**
3. 아키텍처 도형(Mermaid)에서 **파악되지 않은 구간**을 찾는 데 집중

## 출력 형식 (JSON만):
{
  "student_components": ["학생이 실제로 배치한 컴포넌트 목록"],
  "selected_pillars": ["선택된 6대 기둥 ID"],
  "explanation_analysis": {
    "key_points": ["학생이 언급한 핵심 포인트"],
    "unclear_points": ["불명확한 부분 - 꼬리질문 대상"],
    "missing_aspects": ["배치된 컴포넌트 기준으로 누락된 관점"],
    "new_facts": ["이번 설명에서 새롭게 파악된 사실"]
  },
  "questions": [
    {"category": "6대 기둥 중 하나", "question": "상황 기반으로 번역된 질문", "intent": "이 질문으로 확인하려는 것", "pillar": "관련 기둥 ID"},
    {"category": "6대 기둥 중 하나", "question": "상황 기반으로 번역된 질문", "intent": "이 질문으로 확인하려는 것", "pillar": "관련 기둥 ID"},
    {"category": "6대 기둥 중 하나", "question": "상황 기반으로 번역된 질문", "intent": "이 질문으로 확인하려는 것", "pillar": "관련 기둥 ID"}
  ]
}`;

  try {
    const response = await callOpenAI(prompt, { maxTokens: 1200, temperature: 0.7 });
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      return {
        analysis: parsed.explanation_analysis || {},
        questions: parsed.questions || [],
        selectedPillars: parsed.selected_pillars || relevantPillars,
        newFacts: parsed.explanation_analysis?.new_facts || []
      };
    }
    throw new Error('Invalid JSON');
  } catch (error) {
    console.error('Follow-up questions error:', error);
    // Fallback: 학생이 배치한 컴포넌트 기반 상황 질문 (txt 파일 스타일)
    const firstComponent = components[0]?.text || '주요 컴포넌트';
    const lastComponent = components[components.length - 1]?.text || '데이터 저장소';

    return {
      analysis: {
        key_points: ['분석 실패'],
        unclear_points: [],
        missing_aspects: [],
        new_facts: []
      },
      questions: [
        {
          category: '신뢰성',
          question: `만약 ${firstComponent}가 갑자기 다운된다면, 서비스 전체가 멈추나요? 아니면 다른 경로로 우회할 수 있는 구조인가요?`,
          intent: '단일 장애점(SPOF) 파악',
          pillar: 'reliability'
        },
        {
          category: '운영 우수성',
          question: `${firstComponent}에서 ${lastComponent}까지 요청이 흐르는 동안 어느 구간에서 병목이 생기는지 실시간으로 파악할 수 있는 모니터링이 있나요?`,
          intent: '가시성 및 모니터링 확인',
          pillar: 'operationalExcellence'
        },
        {
          category: '성능 최적화',
          question: '갑자기 사용자가 10배로 늘어나는 이벤트 상황이 발생하면, 이 시스템이 자동으로 대응하나요? 아니면 수동으로 서버를 늘려야 하나요?',
          intent: '탄력적 확장성 확인',
          pillar: 'performanceOptimization'
        }
      ],
      selectedPillars: ['reliability', 'operationalExcellence', 'performanceOptimization'],
      newFacts: []
    };
  }
}
