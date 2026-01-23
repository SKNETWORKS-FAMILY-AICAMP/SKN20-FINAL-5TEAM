<template>
  <div class="arch-challenge-container">
    <div class="bg-animation"></div>
    
    <div class="game-container">
      <div class="palette">
        <h2>⚡ Components</h2>
        
        <div class="component-group">
          <h3>Client</h3>
          <div 
            class="component user" 
            draggable="true" 
            @dragstart="onDragStart($event, 'user', '👤 User')"
          >
            👤 User
          </div>
        </div>

        <div class="component-group">
          <h3>Server</h3>
          <div 
            class="component api" 
            draggable="true" 
            @dragstart="onDragStart($event, 'api', '🔌 API Server')"
          >
            🔌 API Server
          </div>
          <div 
            class="component server" 
            draggable="true" 
            @dragstart="onDragStart($event, 'server', '🖥️ Web Server')"
          >
            🖥️ Web Server
          </div>
          <div 
            class="component loadbalancer" 
            draggable="true" 
            @dragstart="onDragStart($event, 'loadbalancer', '⚖️ Load Balancer')"
          >
            ⚖️ Load Balancer
          </div>
        </div>

        <div class="component-group">
          <h3>Data</h3>
          <div 
            class="component db" 
            draggable="true" 
            @dragstart="onDragStart($event, 'db', '💾 Database')"
          >
            💾 Database
          </div>
          <div 
            class="component cache" 
            draggable="true" 
            @dragstart="onDragStart($event, 'cache', '⚡ Cache')"
          >
            ⚡ Cache
          </div>
        </div>

        <div class="component-group">
          <h3>Infrastructure</h3>
          <div 
            class="component queue" 
            draggable="true" 
            @dragstart="onDragStart($event, 'queue', '📬 Message Queue')"
          >
            📬 Message Queue
          </div>
          <div 
            class="component cdn" 
            draggable="true" 
            @dragstart="onDragStart($event, 'cdn', '🌐 CDN')"
          >
            🌐 CDN
          </div>
        </div>
      </div>

      <div class="canvas">
        <div class="canvas-header">
          <h2>⚡ ARCHITECTURE CANVAS</h2>
          <div class="btn-group">
            <button 
              class="btn btn-mode" 
              :class="{ active: isConnectionMode }" 
              @click="toggleMode"
            >
              {{ isConnectionMode ? '🎯 배치' : '🔗 연결' }}
            </button>
            <button class="btn btn-clear" @click="clearCanvas">🗑️ 초기화</button>
          </div>
        </div>
        
        <div 
          class="canvas-area" 
          ref="canvasArea"
          @dragover.prevent
          @drop="onDrop"
          @mousemove="onMouseMove"
          @mouseup="stopDragging"
          @mouseleave="stopDragging"
        >
          <template v-for="(conn, index) in renderedConnections" :key="'conn-'+index">
            <div class="connection-line" :style="conn.lineStyle"></div>
            <div class="connection-arrow" :style="conn.arrowStyle"></div>
          </template>

          <div
            v-for="comp in droppedComponents"
            :key="comp.id"
            :id="comp.id"
            class="dropped-component"
            :class="[comp.type, { selected: selectedComponentId === comp.id }]"
            :style="{ left: comp.x + 'px', top: comp.y + 'px' }"
            @mousedown.stop="onComponentMouseDown($event, comp)"
            @dblclick.stop="startEditingComponent(comp.id)"
          >
            <input
              v-if="editingComponentId === comp.id"
              v-model="editingComponentText"
              class="component-name-input"
              @blur="finishEditingComponent"
              @keyup.enter="finishEditingComponent"
              @keyup.escape="cancelEditingComponent"
              @click.stop
              @mousedown.stop
              ref="componentNameInput"
            />
            <span v-else>{{ comp.text }}</span>
          </div>
        </div>
      </div>

      <div class="result-panel">
        <h2>🎯 CHALLENGE</h2>
        
        <!-- <div class="problem-selector">
          <button 
            v-for="(problem, index) in problems" 
            :key="index"
            class="problem-btn"
            :class="{ active: currentProblemIndex === index }"
            @click="loadProblem(index)"
          >
            {{ problem.level }}
          </button>
        </div> -->

        <div class="problem-card" v-if="currentProblem">
          <h3>{{ currentProblem.title }}</h3>
          <p>{{ currentProblem.description }}</p>
          <div class="problem-requirements">
            <h4>📋 요구사항</h4>
            <ul>
              <li v-for="(req, i) in currentProblem.requirements" :key="i">{{ req }}</li>
            </ul>
          </div>
          <span 
            class="difficulty-badge" 
            :class="`difficulty-${currentProblem.difficulty}`"
          >
            {{ currentProblem.difficulty.toUpperCase() }}
          </span>
        </div>

        <div 
          class="mode-indicator" 
          :class="{ 'connection-mode': isConnectionMode }"
        >
          {{ modeIndicatorText }}
        </div>

        <div class="stats">
          <h3>STATS</h3>
          <div class="stat-item">
            <span>Components:</span>
            <span class="stat-value">{{ droppedComponents.length }}</span>
          </div>
          <div class="stat-item">
            <span>Connections:</span>
            <span class="stat-value">{{ connections.length }}</span>
          </div>
        </div>

        <button 
          class="evaluate-btn" 
          :disabled="droppedComponents.length === 0 || isEvaluating"
          @click="openEvaluationModal"
        >
          {{ isEvaluating ? '🤖 분석 중...' : '🤖 AI 평가 시작' }}
          <span v-if="isEvaluating" class="loading-spinner"></span>
        </button>

        <div v-if="evaluationResult" class="evaluation-result" :class="evaluationResult.grade">
          <div class="score-display" :style="{ color: getGradeColor(evaluationResult.grade) }">
            {{ getGradeEmoji(evaluationResult.grade) }} {{ evaluationResult.score }}점
          </div>
          
          <div class="feedback-section">
            <h4>📊 종합 평가</h4>
            <p>{{ evaluationResult.summary }}</p>
          </div>

          <div v-if="evaluationResult.strengths.length" class="feedback-section">
            <h4>✅ 강점</h4>
            <ul>
              <li v-for="s in evaluationResult.strengths" :key="s">{{ s }}</li>
            </ul>
          </div>

          <div v-if="evaluationResult.weaknesses.length" class="feedback-section">
            <h4>⚠️ 개선점</h4>
            <ul>
              <li v-for="w in evaluationResult.weaknesses" :key="w">{{ w }}</li>
            </ul>
          </div>

          <div v-if="evaluationResult.suggestions.length" class="feedback-section">
            <h4>💡 제안</h4>
            <ul>
              <li v-for="s in evaluationResult.suggestions" :key="s">{{ s }}</li>
            </ul>
          </div>
        </div>

        <h3 class="section-title">📊 Mermaid Preview</h3>
        <div class="mermaid-preview" ref="mermaidContainer"></div>

        <h3 class="section-title">💻 Generated Code</h3>
        <div class="code-output">{{ mermaidCode }}</div>

        <!-- LLM Chat Section -->
        <h3 class="section-title">💬 AI Assistant</h3>
        <div class="chat-container">
          <div class="chat-messages" ref="chatMessages">
            <div
              v-for="(msg, index) in chatMessages"
              :key="index"
              class="chat-message"
              :class="msg.role"
            >
              <span class="message-role">{{ msg.role === 'user' ? '👤 You' : '🤖 AI' }}</span>
              <p class="message-content">{{ msg.content }}</p>
            </div>
            <div v-if="isChatLoading" class="chat-message assistant">
              <span class="message-role">🤖 AI</span>
              <p class="message-content typing-indicator">생각 중...</p>
            </div>
          </div>
          <div class="chat-input-area">
            <input
              type="text"
              v-model="chatInput"
              @keyup.enter="sendChatMessage"
              placeholder="아키텍처에 대해 질문하세요..."
              :disabled="isChatLoading"
              class="chat-input"
            />
            <button
              @click="sendChatMessage"
              :disabled="isChatLoading || !chatInput.trim()"
              class="chat-send-btn"
            >
              전송
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Evaluation Modal -->
    <div class="modal-overlay" :class="{ active: isModalActive }">
      <div class="modal-window">
        <div class="modal-header">
          <h3>🧐 심층 분석 질문</h3>
          <div style="color: #64b5f6; font-size: 0.9em;">AI Architect Bot</div>
        </div>
        <div class="modal-body">
          <div v-if="isGeneratingQuestion" class="loading-question">
            <div class="loading-spinner-large"></div>
            <p>아키텍처를 분석하여 질문을 생성하는 중...</p>
          </div>
          <template v-else>
            <div class="ai-question">
              <span class="ai-question-title">QUESTION</span>
              <span>{{ generatedQuestion || (currentProblem ? currentProblem.followUpQuestion : '') }}</span>
            </div>
            <textarea
              class="user-answer"
              v-model="userAnswer"
              placeholder="여기에 답변을 작성해주세요... (예: CDN을 사용하여 정적 리소스를 캐싱하여 부하를 줄입니다.)"
            ></textarea>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModal">취소</button>
          <button class="btn-submit" @click="submitAnswer" :disabled="isGeneratingQuestion">답변 제출 및 평가</button>
        </div>
      </div>
    </div>

    <!-- Deep Dive Question Modal (for connection questions) -->
    <div class="modal-overlay" :class="{ active: isDeepDiveModalActive }">
      <div class="modal-window deep-dive-modal">
        <div class="modal-header">
          <h3>🔗 연결 심화 질문</h3>
          <div style="color: #ff4785; font-size: 0.9em;">Connection Deep Dive</div>
        </div>
        <div class="modal-body">
          <div v-if="isGeneratingDeepDive" class="loading-question">
            <div class="loading-spinner-large"></div>
            <p>연결에 대한 질문을 생성하는 중...</p>
          </div>
          <template v-else>
            <div class="ai-question deep-dive">
              <span class="ai-question-title">DEEP DIVE QUESTION</span>
              <span>{{ deepDiveQuestion }}</span>
            </div>
            <textarea
              class="user-answer"
              v-model="deepDiveAnswer"
              placeholder="이 연결에 대해 설명해주세요..."
            ></textarea>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="skipDeepDive">건너뛰기</button>
          <button class="btn-submit" @click="submitDeepDiveAnswer" :disabled="isGeneratingDeepDive">답변 저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import mermaid from 'mermaid';

export default {
  name: 'SystemArchitectureChallenge',
  data() {
    return {
      // Logic State
      isConnectionMode: false,
      droppedComponents: [], // { id, type, text, x, y }
      connections: [], // { from: id, to: id, fromType, toType }
      selectedComponentId: null,
      componentCounter: 0,

      // Component Editing State
      editingComponentId: null,
      editingComponentText: '',

      // Dragging State
      draggingComponentId: null,
      dragOffset: { x: 0, y: 0 },

      // Problem & Evaluation State
      currentProblemIndex: 0,
      userAnswer: '',
      isModalActive: false,
      isEvaluating: false,
      evaluationResult: null,
      mermaidCode: 'graph LR\n    %% 컴포넌트를 배치하고 연결하세요!',

      // Deep Dive Question State (for connection questions)
      deepDiveQuestion: null,
      isDeepDiveModalActive: false,
      deepDiveAnswer: '',
      connectionQuestionCount: 0,
      lastQuestionedConnectionTypes: new Set(),
      isGeneratingDeepDive: false,

      // Evaluation Modal State
      isGeneratingQuestion: false,
      generatedQuestion: null,

      // Problems will be loaded from test.json
      problems: [],
      // Chat State
      chatMessages: [],
      chatInput: '',
      isChatLoading: false,
      openaiApiKey: '', // 환경변수에서 가져오거나 직접 설정

      mockEvaluations: {
        0: {
          score: 85,
          grade: "good",
          summary: "기본적인 3-Tier 아키텍처 구조를 잘 이해하고 계시네요. 특히 CDN을 적절히 배치한 점이 훌륭합니다.",
          strengths: ["Client와 API의 분리", "DB 연결의 명확성", "정적 리소스 처리를 위한 CDN 배치"],
          weaknesses: ["API 서버의 이중화 부족"],
          suggestions: ["서버 장애 대비를 위해 Load Balancer 도입을 고려해보세요."]
        },
        1: {
          score: 92,
          grade: "excellent",
          summary: "트래픽 분산과 캐싱 전략이 매우 훌륭합니다. 블랙프라이데이와 같은 상황에서도 안정적으로 동작할 것 같네요.",
          strengths: ["Redis 캐시를 통한 DB 부하 감소 전략", "Load Balancer를 이용한 Scale-out 구조"],
          weaknesses: ["비동기 처리에 대한 구체적 흐름 미흡"],
          suggestions: ["주문 처리와 결제 알림 등을 분리하기 위해 Message Queue를 더 적극적으로 활용해보세요."]
        },
        2: {
          score: 78,
          grade: "needs-improvement",
          summary: "글로벌 서비스를 위한 기본적인 컴포넌트는 갖추었으나, 실시간성 보장을 위한 구조가 다소 아쉽습니다.",
          strengths: ["글로벌 CDN 활용 의도", "데이터베이스 분리"],
          weaknesses: ["UDP/TCP 서버 분리 미고려", "지역별 엣지 서버 배치 전략 부재"],
          suggestions: ["실시간 게임 서버는 상태(Stateful) 관리가 중요하므로 Redis Session Store 활용을 구체화해보세요."]
        }
      }
    };
  },
  computed: {
    currentProblem() {
      return this.problems[this.currentProblemIndex];
    },
    modeIndicatorText() {
      return this.isConnectionMode 
        ? '🔗 연결 모드 - 컴포넌트를 클릭하여 연결하세요' 
        : '🎯 배치 모드 - 컴포넌트를 드래그하여 배치하세요';
    },
    // Dynamically calculate lines based on component positions
    renderedConnections() {
      return this.connections.map(conn => {
        const fromComp = this.droppedComponents.find(c => c.id === conn.from);
        const toComp = this.droppedComponents.find(c => c.id === conn.to);
        
        if (!fromComp || !toComp) return null;

        // Assuming standard size + padding (approx centers)
        // Note: In a real app, you might use ResizeObserver or dynamic refs
        const width = 140; 
        const height = 50; 
        
        const x1 = fromComp.x + width / 2;
        const y1 = fromComp.y + height / 2;
        const x2 = toComp.x + width / 2;
        const y2 = toComp.y + height / 2;

        const length = Math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2);
        const angle = Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI);

        return {
          lineStyle: {
            width: `${length}px`,
            left: `${x1}px`,
            top: `${y1}px`,
            transform: `rotate(${angle}deg)`
          },
          arrowStyle: {
            left: `${x2}px`,
            top: `${y2 - 6}px`, // -6 to center arrow
            transform: `rotate(${angle}deg)`
          }
        };
      }).filter(Boolean);
    }
  },
  async mounted() {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        primaryColor: '#00ff9d',
        primaryTextColor: '#0a0e27',
        primaryBorderColor: '#00e676',
        lineColor: '#64b5f6',
        secondaryColor: '#ff4785',
        tertiaryColor: '#ffc107'
      },
      securityLevel: 'loose'
    });
    await this.fetchProblems();
    this.updateMermaid();
  },
  methods: {
    // --- Fetch Problems from test.json ---
    async fetchProblems() {
      try {
        const response = await fetch('/test.json');
        const data = await response.json();
        this.problems = this.transformProblems(data);
      } catch (error) {
        console.error('Failed to load problems:', error);
        // Fallback to empty array
        this.problems = [];
      }
    },
    transformProblems(data) {
      return data.map((item, index) => {
        // Determine difficulty based on index or id
        let difficulty = 'easy';
        let level = '초급';
        if (index >= 7) {
          difficulty = 'hard';
          level = '고급';
        } else if (index >= 4) {
          difficulty = 'medium';
          level = '중급';
        }

        // Convert requirements string to array
        const requirementsArray = item.requirements
          .split(/[,،]/)
          .map(req => req.trim())
          .filter(req => req.length > 0);

        // Generate follow-up question from question_topics
        let followUpQuestion = '';
        if (item.question_topics && item.question_topics.length > 0) {
          const topic = item.question_topics[0];
          followUpQuestion = `${topic.topic}에 대해 설명해주세요. (키워드: ${topic.keywords.join(', ')})`;
        }

        // Map key_components types to expected component types
        const componentTypeMap = {
          'entry': 'loadbalancer',
          'storage': 'db',
          'db': 'db',
          'cache': 'cache',
          'message_queue': 'queue',
          'network': 'cdn',
          'compute': 'server',
          'external': 'api'
        };
        const expectedComponents = item.key_components.map(comp =>
          componentTypeMap[comp.type] || comp.type
        );

        return {
          level,
          title: item.title,
          description: item.requirements,
          difficulty,
          requirements: requirementsArray,
          followUpQuestion,
          expectedComponents,
          referenceMermaid: item.reference_mermaid,
          referenceConcept: item.reference_concept,
          evaluationRubric: item.evaluation_rubric
        };
      });
    },

    // --- Drag & Drop ---
    onDragStart(event, type, text) {
      event.dataTransfer.setData('componentType', type);
      event.dataTransfer.setData('componentText', text);
    },
    onDrop(event) {
      if (this.isConnectionMode) return;

      const type = event.dataTransfer.getData('componentType');
      const text = event.dataTransfer.getData('componentText');
      if (!type) return;

      const rect = this.$refs.canvasArea.getBoundingClientRect();
      const x = event.clientX - rect.left - 70; // Center offset
      const y = event.clientY - rect.top - 25;

      this.droppedComponents.push({
        id: `comp_${this.componentCounter++}`,
        type,
        text,
        x,
        y
      });

      this.updateMermaid();
    },
    
    // --- Component Movement ---
    onComponentMouseDown(event, comp) {
      if (this.isConnectionMode) {
        this.handleConnectionClick(comp);
        return;
      }

      this.draggingComponentId = comp.id;
      this.dragOffset.x = event.clientX - comp.x; // Use raw coordinate logic
      this.dragOffset.y = event.clientY - comp.y;
    },
    onMouseMove(event) {
      if (!this.draggingComponentId) return;

      const comp = this.droppedComponents.find(c => c.id === this.draggingComponentId);
      if (comp) {
        // Simple movement logic relative to window, 
        // in production consider canvas bounds
        const rect = this.$refs.canvasArea.getBoundingClientRect();
        // Calculate relative to canvas
        comp.x = event.clientX - rect.left - (this.dragOffset.x - comp.x) - rect.left; 
        // Correcting logic: 
        // The simple way: 
        // New X = Current Mouse X - Offset calculated at start
        // Offset = Start Mouse X - Start Component X (absolute)
        
        // Let's use simplified logic for the Vue conversion:
        // We know the offset inside the component
        const offsetX = event.clientX - this.dragOffset.x; // this won't work perfectly with above
        
        // Re-implementing simplified drag:
        // 1. Get current component X/Y is stored in data
        // 2. Mouse delta? 
        
        // Using the logic from the HTML example:
        // startX = clientX - elem.offsetLeft
        // move: newX = clientX - startX
        
        // Since we are data driven, let's just calculate delta.
        // Actually, easier:
        // mouseDown: save (clientX, clientY) and (comp.x, comp.y)
        // mouseMove: deltaX = clientX - savedClientX. newCompX = savedCompX + deltaX
        
        // Let's stick to the simpler absolute mapping if canvas is relative
        // For this demo, let's assume dragOffset holds the difference between Mouse and Comp TopLeft
        // To do that correctly:
        // dragOffset.x = event.clientX - (rect.left + comp.x)
        
        // Let's fix onComponentMouseDown:
        // const rect = this.$refs.canvasArea.getBoundingClientRect();
        // this.dragOffset.x = event.clientX - (rect.left + comp.x);
        // this.dragOffset.y = event.clientY - (rect.top + comp.y);
        
        // Then here:
        // comp.x = event.clientX - rect.left - this.dragOffset.x;
        // comp.y = event.clientY - rect.top - this.dragOffset.y;
        
        // But for now, let's trust the logic below which is roughly:
        // Move component center to mouse? No.
        
        // Correct implementation for this context:
        // We need to know where we grabbed the component.
        // Let's rely on standard drag logic. 
        // Since I can't easily change the template @mousedown structure too much, 
        // let's do this:
        
        // Re-fix MouseDown:
        // this.startMouseX = event.clientX
        // this.startMouseY = event.clientY
        // this.startCompX = comp.x
        // this.startCompY = comp.y
        
        const deltaX = event.clientX - this.dragStartPos.mouseX;
        const deltaY = event.clientY - this.dragStartPos.mouseY;
        
        comp.x = this.dragStartPos.compX + deltaX;
        comp.y = this.dragStartPos.compY + deltaY;
      }
    },
    // Override MouseDown for better logic
    onComponentMouseDown(event, comp) {
      if (this.isConnectionMode) {
        this.handleConnectionClick(comp);
        return;
      }
      this.draggingComponentId = comp.id;
      this.dragStartPos = {
        mouseX: event.clientX,
        mouseY: event.clientY,
        compX: comp.x,
        compY: comp.y
      };
    },
    stopDragging() {
      if (this.draggingComponentId) {
        this.draggingComponentId = null;
        this.updateMermaid(); // Update graph on drop
      }
    },

    // --- Component Name Editing ---
    startEditingComponent(compId) {
      if (this.isConnectionMode) return;
      const comp = this.droppedComponents.find(c => c.id === compId);
      if (!comp) return;

      this.editingComponentId = compId;
      this.editingComponentText = comp.text;

      this.$nextTick(() => {
        const input = this.$refs.componentNameInput;
        if (input && input[0]) {
          input[0].focus();
          input[0].select();
        }
      });
    },
    finishEditingComponent() {
      if (!this.editingComponentId) return;

      const comp = this.droppedComponents.find(c => c.id === this.editingComponentId);
      if (comp && this.editingComponentText.trim()) {
        comp.text = this.editingComponentText.trim();
        this.updateMermaid();
      }

      this.editingComponentId = null;
      this.editingComponentText = '';
    },
    cancelEditingComponent() {
      this.editingComponentId = null;
      this.editingComponentText = '';
    },

    // --- Connections ---
    async handleConnectionClick(comp) {
      if (this.selectedComponentId === comp.id) {
        this.selectedComponentId = null; // Deselect
        return;
      }

      if (!this.selectedComponentId) {
        // Select first
        this.selectedComponentId = comp.id;
      } else {
        // Connect
        const exists = this.connections.some(c =>
          (c.from === this.selectedComponentId && c.to === comp.id) ||
          (c.from === comp.id && c.to === this.selectedComponentId)
        );

        if (!exists) {
          const fromComp = this.droppedComponents.find(c => c.id === this.selectedComponentId);
          this.connections.push({
            from: this.selectedComponentId,
            to: comp.id,
            fromType: fromComp.type,
            toType: comp.type
          });
          this.updateMermaid();

          // Check if we should ask a deep dive question
          if (this.shouldAskDeepDive(fromComp.type, comp.type)) {
            this.lastQuestionedConnectionTypes.add(`${fromComp.type}-${comp.type}`);
            this.connectionQuestionCount++;
            await this.generateDeepDiveQuestion(fromComp, comp);
          }
        }

        this.selectedComponentId = null; // Reset
      }
    },

    // --- Deep Dive Question Logic ---
    shouldAskDeepDive(fromType, toType) {
      // Important connection combinations
      const importantConnections = [
        ['api', 'db'],
        ['api', 'cache'],
        ['loadbalancer', 'api'],
        ['loadbalancer', 'server'],
        ['server', 'queue'],
        ['server', 'db'],
        ['user', 'loadbalancer'],
        ['user', 'cdn'],
        ['cache', 'db'],
        ['queue', 'server'],
      ];

      // Check if already questioned (bidirectional check)
      const key1 = `${fromType}-${toType}`;
      const key2 = `${toType}-${fromType}`;
      if (this.lastQuestionedConnectionTypes.has(key1) ||
          this.lastQuestionedConnectionTypes.has(key2)) return false;

      // Maximum 3 questions per session
      if (this.connectionQuestionCount >= 3) return false;

      // Check if it's an important connection
      return importantConnections.some(([a, b]) =>
        (fromType === a && toType === b) || (fromType === b && toType === a)
      );
    },

    async generateDeepDiveQuestion(fromComp, toComp) {
      this.isDeepDiveModalActive = true;
      this.isGeneratingDeepDive = true;
      this.deepDiveAnswer = '';

      const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${this.currentProblem?.title || '시스템 아키텍처 설계'}
요구사항: ${this.currentProblem?.requirements?.join(', ') || '없음'}

학생이 "${fromComp.text}"와 "${toComp.text}"를 연결했습니다.
이 연결에 대해 깊이 있는 면접 질문 1개를 생성해주세요.

예시 질문 유형:
- 이 연결에서 발생할 수 있는 문제점은?
- 왜 이 두 컴포넌트를 연결했나요?
- 이 연결의 데이터 흐름을 설명해주세요.
- 장애 상황에서 이 연결은 어떻게 처리되나요?

질문만 출력하세요. 다른 설명은 포함하지 마세요.`;

      try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiApiKey || import.meta.env.VITE_OPENAI_API_KEY}`
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 200,
            temperature: 0.7
          })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();
        this.deepDiveQuestion = data.choices[0].message.content.trim();
      } catch (error) {
        console.error('Deep dive question error:', error);
        this.deepDiveQuestion = `${fromComp.text}와 ${toComp.text}의 연결에서 예상되는 데이터 흐름과 잠재적인 병목 현상에 대해 설명해주세요.`;
      } finally {
        this.isGeneratingDeepDive = false;
      }
    },

    skipDeepDive() {
      this.isDeepDiveModalActive = false;
      this.deepDiveQuestion = null;
      this.deepDiveAnswer = '';
    },

    submitDeepDiveAnswer() {
      // Store the answer for later evaluation
      if (this.deepDiveAnswer.trim()) {
        this.chatMessages.push({
          role: 'user',
          content: `[연결 질문] ${this.deepDiveQuestion}\n\n[답변] ${this.deepDiveAnswer}`
        });
        this.chatMessages.push({
          role: 'assistant',
          content: '답변이 저장되었습니다. 최종 평가 시 반영됩니다.'
        });
      }
      this.isDeepDiveModalActive = false;
      this.deepDiveQuestion = null;
      this.deepDiveAnswer = '';
    },
    toggleMode() {
      this.isConnectionMode = !this.isConnectionMode;
      this.selectedComponentId = null;
    },
    clearCanvas() {
      if (confirm('모든 컴포넌트와 연결을 삭제하시겠습니까?')) {
        this.droppedComponents = [];
        this.connections = [];
        this.componentCounter = 0;
        this.evaluationResult = null;
        // Reset deep dive state
        this.connectionQuestionCount = 0;
        this.lastQuestionedConnectionTypes = new Set();
        this.deepDiveQuestion = null;
        this.deepDiveAnswer = '';
        // Reset chat messages
        this.chatMessages = [];
        this.updateMermaid();
      }
    },

    // --- Problem & Mermaid ---
    loadProblem(index) {
      this.currentProblemIndex = index;
      this.clearCanvas();
    },
    async updateMermaid() {
      if (this.droppedComponents.length === 0) {
        this.mermaidCode = 'graph LR\n    %% 컴포넌트를 배치하고 연결하세요!';
        if(this.$refs.mermaidContainer) this.$refs.mermaidContainer.innerHTML = '';
        return;
      }

      let code = 'graph LR\n';
      
      this.droppedComponents.forEach(comp => {
        const label = comp.text.replace(/[^\w\s가-힣]/g, '');
        code += `    ${comp.id}["${label}"]\n`;
      });
      
      code += '\n';
      this.connections.forEach(conn => {
        code += `    ${conn.from} --> ${conn.to}\n`;
      });

      code += '\n';
      const styleMap = {
        'user': 'fill:#ff4785,stroke:#ff1744,stroke-width:3px,color:#fff',
        'api': 'fill:#64b5f6,stroke:#2196f3,stroke-width:3px,color:#fff',
        'db': 'fill:#00ff9d,stroke:#00e676,stroke-width:3px,color:#0a0e27',
        'cache': 'fill:#ffc107,stroke:#ffa000,stroke-width:3px,color:#0a0e27',
        'server': 'fill:#ab47bc,stroke:#8e24aa,stroke-width:3px,color:#fff',
        'queue': 'fill:#ff8a65,stroke:#ff5722,stroke-width:3px,color:#fff',
        'loadbalancer': 'fill:#26c6da,stroke:#00acc1,stroke-width:3px,color:#0a0e27',
        'cdn': 'fill:#66bb6a,stroke:#43a047,stroke-width:3px,color:#fff'
      };

      this.droppedComponents.forEach(comp => {
        if (styleMap[comp.type]) {
          code += `    style ${comp.id} ${styleMap[comp.type]}\n`;
        }
      });

      this.mermaidCode = code;

      if (this.$refs.mermaidContainer) {
        this.$refs.mermaidContainer.innerHTML = `<div class="mermaid">${code}</div>`;
        try {
          await mermaid.run({
            nodes: this.$refs.mermaidContainer.querySelectorAll('.mermaid')
          });
        } catch (e) {
          console.error('Mermaid rendering error:', e);
        }
      }
    },

    // --- Evaluation & Modal ---
    async openEvaluationModal() {
      this.userAnswer = '';
      this.isModalActive = true;
      this.isGeneratingQuestion = true;
      this.generatedQuestion = null;

      // Generate LLM question based on architecture
      const architectureContext = this.buildFullArchitectureContext();

      const prompt = `당신은 시스템 아키텍처 면접관입니다.

문제: ${this.currentProblem?.title || '시스템 아키텍처 설계'}
요구사항: ${this.currentProblem?.requirements?.join(', ') || '없음'}
주제 힌트: ${this.currentProblem?.evaluationRubric ? Object.keys(this.currentProblem.evaluationRubric).join(', ') : ''}

학생의 아키텍처:
${architectureContext}

이 아키텍처에 대해 심층적인 면접 질문 1개를 생성하세요.
학생이 설계한 내용을 바탕으로 트레이드오프, 확장성, 장애 대응 등에 대해 질문하세요.
질문만 출력하세요.`;

      try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiApiKey || import.meta.env.VITE_OPENAI_API_KEY}`
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 300,
            temperature: 0.7
          })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();
        this.generatedQuestion = data.choices[0].message.content.trim();
      } catch (error) {
        console.error('Question generation error:', error);
        this.generatedQuestion = this.currentProblem?.followUpQuestion || '설계하신 아키텍처에서 가장 중요한 트레이드오프는 무엇인가요?';
      } finally {
        this.isGeneratingQuestion = false;
      }
    },
    closeModal() {
      this.isModalActive = false;
      this.generatedQuestion = null;
    },
    submitAnswer() {
      if (!this.userAnswer.trim()) {
        alert('답변을 입력해주세요!');
        return;
      }
      this.isModalActive = false;
      this.evaluate();
    },
    async evaluate() {
      this.isEvaluating = true;
      this.evaluationResult = null;

      const architectureContext = this.buildFullArchitectureContext();
      const rubric = this.currentProblem?.evaluationRubric;

      // Collect all deep dive answers from chat history
      const deepDiveAnswers = this.chatMessages
        .filter(msg => msg.role === 'user' && msg.content.startsWith('[연결 질문]'))
        .map(msg => msg.content)
        .join('\n\n');

      const prompt = `당신은 시스템 아키텍처 면접관입니다.
다음 평가 기준에 따라 학생의 아키텍처를 평가해주세요.

문제: ${this.currentProblem?.title || '시스템 아키텍처 설계'}
요구사항: ${this.currentProblem?.requirements?.join(', ') || '없음'}

평가 기준:
${rubric ? JSON.stringify(rubric, null, 2) : '- 요구사항 충족도\n- 확장성\n- 장애 대응\n- 컴포넌트 적절성'}

학생의 아키텍처:
${architectureContext}

심층 질문: ${this.generatedQuestion || this.currentProblem?.followUpQuestion || ''}
학생의 답변: ${this.userAnswer}

${deepDiveAnswers ? `추가 연결 질문 답변:\n${deepDiveAnswers}` : ''}

다음 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{
  "score": 0에서 100 사이의 숫자,
  "grade": "excellent" 또는 "good" 또는 "needs-improvement" 또는 "poor",
  "summary": "종합 평가 (2-3문장)",
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["개선점1"],
  "suggestions": ["제안1", "제안2"]
}`;

      try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiApiKey || import.meta.env.VITE_OPENAI_API_KEY}`
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: prompt }],
            max_tokens: 800,
            temperature: 0.5
          })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();
        const content = data.choices[0].message.content.trim();

        // Parse JSON from response
        const jsonMatch = content.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          this.evaluationResult = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error('Invalid JSON response');
        }
      } catch (error) {
        console.error('Evaluation error:', error);
        // Fallback to mock evaluation
        const mock = this.mockEvaluations[this.currentProblemIndex] || this.mockEvaluations[0];
        const result = JSON.parse(JSON.stringify(mock));
        result.summary = `API 연결 문제로 기본 평가를 제공합니다. ` + result.summary;
        this.evaluationResult = result;
      } finally {
        this.isEvaluating = false;
      }
    },

    buildFullArchitectureContext() {
      if (this.droppedComponents.length === 0) {
        return '배치된 컴포넌트가 없습니다.';
      }

      let context = `배치된 컴포넌트 (${this.droppedComponents.length}개):\n`;
      this.droppedComponents.forEach(comp => {
        context += `- ${comp.text} (${comp.type})\n`;
      });

      if (this.connections.length > 0) {
        context += `\n연결 (${this.connections.length}개):\n`;
        this.connections.forEach(conn => {
          const from = this.droppedComponents.find(c => c.id === conn.from);
          const to = this.droppedComponents.find(c => c.id === conn.to);
          if (from && to) {
            context += `- ${from.text} → ${to.text}\n`;
          }
        });
      }

      context += `\nMermaid 코드:\n${this.mermaidCode}`;

      return context;
    },
    getGradeColor(grade) {
      const colors = {
        'excellent': '#00ff9d',
        'good': '#64b5f6',
        'needs-improvement': '#ffc107',
        'poor': '#ff4785'
      };
      return colors[grade] || '#e0e0e0';
    },
    getGradeEmoji(grade) {
      const emojis = {
        'excellent': '🏆',
        'good': '👍',
        'needs-improvement': '💡',
        'poor': '📝'
      };
      return emojis[grade] || '❓';
    },

    // --- Chat with OpenAI ---
    async sendChatMessage() {
      const userMessage = this.chatInput.trim();
      if (!userMessage) return;

      // Add user message
      this.chatMessages.push({
        role: 'user',
        content: userMessage
      });
      this.chatInput = '';
      this.isChatLoading = true;

      // Scroll to bottom
      this.$nextTick(() => {
        if (this.$refs.chatMessages) {
          this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
        }
      });

      try {
        // Build context about current problem (title + requirements only)
        const chatContext = this.buildChatContext();

        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.openaiApiKey || import.meta.env.VITE_OPENAI_API_KEY}`
          },
          body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [
              {
                role: 'system',
                content: `당신은 시스템 아키텍처 면접관입니다.
학생이 주어진 문제의 기능적/비기능적 요구사항에 대해 질문하면 답변해주세요.

중요 규칙:
1. 직접적인 정답이나 완성된 아키텍처 설계를 알려주지 마세요.
2. 힌트와 고려사항만 제공하세요.
3. 학생이 스스로 생각할 수 있도록 유도 질문을 하세요.
4. 요구사항의 의미나 우선순위에 대해서는 명확히 설명해주세요.

현재 문제:
${chatContext}

친절하지만 교육적인 태도로 답변해주세요. 한국어로 답변하세요.`
              },
              ...this.chatMessages.map(msg => ({
                role: msg.role,
                content: msg.content
              }))
            ],
            max_tokens: 500,
            temperature: 0.7
          })
        });

        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        const assistantMessage = data.choices[0].message.content;

        this.chatMessages.push({
          role: 'assistant',
          content: assistantMessage
        });

      } catch (error) {
        console.error('Chat error:', error);
        this.chatMessages.push({
          role: 'assistant',
          content: 'API 연결에 문제가 발생했습니다. API 키를 확인해주세요.'
        });
      } finally {
        this.isChatLoading = false;
        this.$nextTick(() => {
          if (this.$refs.chatMessages) {
            this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
          }
        });
      }
    },

    // Build context for chat - only uses title and requirements
    buildChatContext() {
      if (!this.currentProblem) return '';

      return `문제: ${this.currentProblem.title}
요구사항: ${this.currentProblem.requirements.join(', ')}`;
    },

    buildArchitectureContext() {
      // For chat: only problem info, no architecture details
      return this.buildChatContext();
    }
  }
};
</script>

<style scoped>
/* Fonts Import - In a real app, this should be in index.html or App.vue */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Orbitron:wght@700;900&family=Space+Mono:wght@400;700&display=swap');

:root {
  --primary: #00ff9d;
  --secondary: #64b5f6;
  --accent: #ff4785;
  --bg-dark: #0a0e27;
  --bg-panel: rgba(17, 24, 39, 0.95);
  --text-main: #e0e0e0;
}

.arch-challenge-container {
  font-family: 'Space Mono', monospace;
  background: #0a0e27;
  color: #e0e0e0;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* Background Animation */
.bg-animation {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.3;
  background: 
      radial-gradient(ellipse at 20% 30%, rgba(0, 255, 157, 0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 70%, rgba(255, 71, 133, 0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 50% 50%, rgba(100, 181, 246, 0.1) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -30px) scale(1.1); }
  66% { transform: translate(-30px, 30px) scale(0.9); }
}

.game-container {
  display: grid;
  grid-template-columns: 280px 1fr 450px;
  height: 100vh;
  gap: 0;
  position: relative;
  z-index: 1;
}

/* Palette */
.palette {
  background: rgba(17, 24, 39, 0.95);
  padding: 24px;
  overflow-y: auto;
  border-right: 1px solid rgba(0, 255, 157, 0.2);
  backdrop-filter: blur(10px);
}

.palette h2 {
  color: #00ff9d;
  margin-bottom: 24px;
  font-size: 1.4em;
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 0 20px rgba(0, 255, 157, 0.5);
}

.component-group {
  margin-bottom: 28px;
}

.component-group h3 {
  color: #64b5f6;
  font-size: 0.85em;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 700;
  opacity: 0.9;
}

.component {
  background: linear-gradient(135deg, rgba(0, 255, 157, 0.1) 0%, rgba(100, 181, 246, 0.1) 100%);
  color: #00ff9d;
  padding: 14px;
  margin: 10px 0;
  border-radius: 8px;
  cursor: move;
  text-align: center;
  font-weight: 700;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(0, 255, 157, 0.3);
  font-size: 0.9em;
  letter-spacing: 0.5px;
}

.component:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 25px rgba(0, 255, 157, 0.3);
  border-color: #00ff9d;
}

.component.user { border-color: rgba(255, 71, 133, 0.5); color: #ff4785; }
.component.api { border-color: rgba(100, 181, 246, 0.5); color: #64b5f6; }
.component.db { border-color: rgba(0, 255, 157, 0.5); color: #00ff9d; }
.component.cache { border-color: rgba(255, 193, 7, 0.5); color: #ffc107; }
.component.server { border-color: rgba(171, 71, 188, 0.5); color: #ab47bc; }
.component.queue { border-color: rgba(255, 138, 101, 0.5); color: #ff8a65; }
.component.loadbalancer { border-color: rgba(38, 198, 218, 0.5); color: #26c6da; }
.component.cdn { border-color: rgba(102, 187, 106, 0.5); color: #66bb6a; }

/* Canvas */
.canvas {
  background: rgba(10, 14, 39, 0.8);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.canvas-header {
  background: rgba(17, 24, 39, 0.95);
  padding: 20px 24px;
  border-bottom: 2px solid rgba(0, 255, 157, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(10px);
  height: 75px;
}

.canvas-header h2 {
  color: #00ff9d;
  font-size: 1.3em;
  font-family: 'Orbitron', sans-serif;
  text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
}

.btn-group {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: 2px solid;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.3s;
  font-family: 'Space Mono', monospace;
  font-size: 0.85em;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  background: transparent;
}

.btn-clear {
  border-color: #ff4785;
  color: #ff4785;
}

.btn-clear:hover {
  background: #ff4785;
  color: #0a0e27;
  box-shadow: 0 0 20px rgba(255, 71, 133, 0.5);
}

.btn-mode {
  border-color: #64b5f6;
  color: #64b5f6;
}

.btn-mode:hover {
  background: #64b5f6;
  color: #0a0e27;
}

.btn-mode.active {
  background: #00ff9d;
  border-color: #00ff9d;
  color: #0a0e27;
}

.canvas-area {
  flex: 1;
  position: relative;
  background-image: 
      linear-gradient(rgba(0, 255, 157, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 255, 157, 0.05) 1px, transparent 1px);
  background-size: 30px 30px;
  overflow: hidden;
}

.dropped-component {
  position: absolute;
  padding: 16px 28px;
  border-radius: 10px;
  cursor: move;
  font-weight: 700;
  min-width: 140px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 3px solid;
  backdrop-filter: blur(5px);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  user-select: none;
  z-index: 2;
}

.dropped-component:hover {
  transform: scale(1.08);
  z-index: 10;
}

.dropped-component.selected {
  box-shadow: 0 0 30px currentColor;
  animation: pulse-border 1.5s infinite;
}

@keyframes pulse-border {
  0%, 100% { border-width: 3px; }
  50% { border-width: 5px; }
}

.dropped-component.user { background: rgba(255, 71, 133, 0.15); border-color: #ff4785; color: #ff4785; }
.dropped-component.api { background: rgba(100, 181, 246, 0.15); border-color: #64b5f6; color: #64b5f6; }
.dropped-component.db { background: rgba(0, 255, 157, 0.15); border-color: #00ff9d; color: #00ff9d; }
.dropped-component.cache { background: rgba(255, 193, 7, 0.15); border-color: #ffc107; color: #ffc107; }
.dropped-component.server { background: rgba(171, 71, 188, 0.15); border-color: #ab47bc; color: #ab47bc; }
.dropped-component.queue { background: rgba(255, 138, 101, 0.15); border-color: #ff8a65; color: #ff8a65; }
.dropped-component.loadbalancer { background: rgba(38, 198, 218, 0.15); border-color: #26c6da; color: #26c6da; }
.dropped-component.cdn { background: rgba(102, 187, 106, 0.15); border-color: #66bb6a; color: #66bb6a; }

/* Connections */
.connection-line {
  position: absolute;
  height: 3px;
  background: linear-gradient(90deg, #00ff9d, #64b5f6);
  transform-origin: left center;
  pointer-events: none;
  z-index: 1;
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
}

.connection-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border-left: 12px solid #64b5f6;
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
  pointer-events: none;
  z-index: 1;
  filter: drop-shadow(0 0 5px rgba(100, 181, 246, 0.5));
}

/* Result Panel */
.result-panel {
  background: rgba(17, 24, 39, 0.95);
  padding: 24px;
  overflow-y: auto;
  border-left: 1px solid rgba(0, 255, 157, 0.2);
  backdrop-filter: blur(10px);
}

.result-panel h2 {
  color: #00ff9d;
  margin-bottom: 20px;
  font-size: 1.3em;
  font-family: 'Orbitron', sans-serif;
  text-shadow: 0 0 15px rgba(0, 255, 157, 0.5);
}

.problem-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.problem-btn {
  flex: 1;
  min-width: 80px;
  padding: 10px;
  background: rgba(0, 255, 157, 0.1);
  border: 2px solid rgba(0, 255, 157, 0.3);
  color: #00ff9d;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Space Mono', monospace;
  font-size: 0.8em;
  font-weight: 700;
  transition: all 0.3s;
}

.problem-btn:hover {
  background: rgba(0, 255, 157, 0.2);
  border-color: #00ff9d;
}

.problem-btn.active {
  background: #00ff9d;
  color: #0a0e27;
}

.problem-card {
  background: linear-gradient(135deg, rgba(255, 71, 133, 0.1), rgba(171, 71, 188, 0.1));
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  border: 2px solid rgba(255, 71, 133, 0.3);
  animation: glow-border 3s ease-in-out infinite;
}

@keyframes glow-border {
  0%, 100% { border-color: rgba(255, 71, 133, 0.3); }
  50% { border-color: rgba(255, 71, 133, 0.6); }
}

.problem-card h3 {
  color: #ff4785;
  margin-bottom: 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1em;
}

.problem-card p {
  line-height: 1.6;
  margin-bottom: 10px;
  font-size: 0.9em;
}

.problem-requirements {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px;
  border-radius: 6px;
  margin-top: 10px;
}

.problem-requirements h4 {
  color: #64b5f6;
  font-size: 0.85em;
  margin-bottom: 8px;
}

.problem-requirements ul {
  margin-left: 20px;
  color: #b0b0b0;
  font-size: 0.85em;
}

.difficulty-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.75em;
  font-weight: 700;
  margin-top: 8px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.difficulty-easy { background: #00ff9d; color: #0a0e27; }
.difficulty-medium { background: #ffc107; color: #0a0e27; }
.difficulty-hard { background: #ff4785; color: #fff; }

.mode-indicator {
  background: linear-gradient(135deg, #00ff9d, #64b5f6);
  color: #0a0e27;
  padding: 12px;
  border-radius: 6px;
  text-align: center;
  margin-bottom: 15px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  box-shadow: 0 0 20px rgba(0, 255, 157, 0.3);
}

.mode-indicator.connection-mode {
  background: linear-gradient(135deg, #ff4785, #ab47bc);
  color: #fff;
}

.stats {
  background: linear-gradient(135deg, rgba(0, 255, 157, 0.1), rgba(100, 181, 246, 0.1));
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid rgba(0, 255, 157, 0.3);
}

.stats h3 {
  color: #00ff9d;
  margin-bottom: 12px;
  font-size: 0.95em;
  font-family: 'Orbitron', sans-serif;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin: 8px 0;
  font-size: 0.9em;
}

.stat-value {
  color: #00ff9d;
  font-weight: 700;
}

.evaluate-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #00ff9d, #64b5f6);
  border: none;
  border-radius: 8px;
  color: #0a0e27;
  font-weight: 700;
  font-size: 1.1em;
  cursor: pointer;
  margin: 20px 0;
  font-family: 'Orbitron', sans-serif;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  transition: all 0.3s;
  box-shadow: 0 4px 20px rgba(0, 255, 157, 0.3);
}

.evaluate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 255, 157, 0.5);
}

.evaluate-btn:disabled {
  background: rgba(100, 100, 100, 0.3);
  cursor: not-allowed;
  box-shadow: none;
}

.loading-spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 255, 157, 0.3);
  border-top-color: #00ff9d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-left: 10px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.evaluation-result {
  background: rgba(0, 0, 0, 0.4);
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  border: 2px solid;
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.evaluation-result.excellent { border-color: #00ff9d; background: rgba(0, 255, 157, 0.1); }
.evaluation-result.good { border-color: #64b5f6; background: rgba(100, 181, 246, 0.1); }
.evaluation-result.needs-improvement { border-color: #ffc107; background: rgba(255, 193, 7, 0.1); }
.evaluation-result.poor { border-color: #ff4785; background: rgba(255, 71, 133, 0.1); }

.score-display {
  font-size: 3em;
  font-family: 'Orbitron', sans-serif;
  text-align: center;
  margin: 20px 0;
  text-shadow: 0 0 20px currentColor;
}

.feedback-section {
  margin-top: 15px;
}

.feedback-section h4 {
  color: #64b5f6;
  margin-bottom: 10px;
  font-size: 0.95em;
}

.feedback-section ul {
  margin-left: 20px;
  margin-top: 8px;
}

.feedback-section li {
  margin: 6px 0;
}

.mermaid-preview {
  background: rgba(0, 0, 0, 0.3);
  padding: 15px;
  border-radius: 8px;
  margin: 15px 0;
  border: 1px solid rgba(0, 255, 157, 0.2);
  min-height: 150px;
}

.code-output {
  background: rgba(0, 0, 0, 0.5);
  color: #00ff9d;
  padding: 15px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  overflow-x: auto;
  white-space: pre-wrap;
  border: 1px solid rgba(0, 255, 157, 0.2);
  margin: 15px 0;
}

.section-title {
  color: #64b5f6;
  margin: 20px 0 10px 0;
  font-size: 1em;
  font-family: 'Orbitron', sans-serif;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.modal-overlay.active {
  opacity: 1;
  pointer-events: all;
}

.modal-window {
  background: #111827;
  border: 2px solid #00ff9d;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 0 50px rgba(0, 255, 157, 0.2);
  transform: translateY(20px);
  transition: transform 0.3s ease;
}

.modal-overlay.active .modal-window {
  transform: translateY(0);
}

.modal-header {
  background: linear-gradient(90deg, rgba(0, 255, 157, 0.1), transparent);
  padding: 20px;
  border-bottom: 1px solid rgba(0, 255, 157, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  color: #00ff9d;
  font-family: 'Orbitron', sans-serif;
  font-size: 1.2em;
}

.modal-body {
  padding: 24px;
}

.ai-question {
  background: rgba(100, 181, 246, 0.1);
  border-left: 4px solid #64b5f6;
  padding: 16px;
  margin-bottom: 20px;
  line-height: 1.6;
}

.ai-question-title {
  color: #64b5f6;
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
  font-size: 0.9em;
  text-transform: uppercase;
}

.user-answer {
  width: 100%;
  height: 150px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 16px;
  border-radius: 8px;
  font-family: 'Space Mono', monospace;
  font-size: 1em;
  resize: vertical;
  transition: border-color 0.3s;
}

.user-answer:focus {
  outline: none;
  border-color: #00ff9d;
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.1);
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #ff4785;
  color: #ff4785;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Space Mono', monospace;
  font-weight: bold;
}

.btn-submit {
  background: #00ff9d;
  border: none;
  color: #0a0e27;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-family: 'Orbitron', sans-serif;
  font-weight: bold;
  box-shadow: 0 0 15px rgba(0, 255, 157, 0.3);
  transition: transform 0.2s;
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 25px rgba(0, 255, 157, 0.5);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 157, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 157, 0.4);
}

/* Chat Styles */
.chat-container {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(0, 255, 157, 0.3);
  border-radius: 10px;
  margin-top: 10px;
  overflow: hidden;
}

.chat-messages {
  height: 200px;
  overflow-y: auto;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-message {
  max-width: 85%;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.9em;
  line-height: 1.5;
}

.chat-message.user {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.2), rgba(100, 181, 246, 0.1));
  border: 1px solid rgba(100, 181, 246, 0.4);
  align-self: flex-end;
}

.chat-message.assistant {
  background: linear-gradient(135deg, rgba(0, 255, 157, 0.15), rgba(0, 255, 157, 0.05));
  border: 1px solid rgba(0, 255, 157, 0.3);
  align-self: flex-start;
}

.message-role {
  display: block;
  font-size: 0.75em;
  font-weight: 700;
  margin-bottom: 4px;
  opacity: 0.8;
}

.chat-message.user .message-role {
  color: #64b5f6;
}

.chat-message.assistant .message-role {
  color: #00ff9d;
}

.message-content {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.typing-indicator {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.5; }
}

.chat-input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid rgba(0, 255, 157, 0.2);
  background: rgba(0, 0, 0, 0.2);
}

.chat-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(100, 181, 246, 0.3);
  color: #e0e0e0;
  padding: 10px 14px;
  border-radius: 6px;
  font-family: 'Space Mono', monospace;
  font-size: 0.9em;
  transition: border-color 0.3s;
}

.chat-input:focus {
  outline: none;
  border-color: #64b5f6;
  box-shadow: 0 0 10px rgba(100, 181, 246, 0.2);
}

.chat-input:disabled {
  opacity: 0.6;
}

.chat-send-btn {
  background: linear-gradient(135deg, #00ff9d, #64b5f6);
  border: none;
  color: #0a0e27;
  padding: 10px 20px;
  border-radius: 6px;
  font-family: 'Space Mono', monospace;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.chat-send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 255, 157, 0.4);
}

.chat-send-btn:disabled {
  background: rgba(100, 100, 100, 0.4);
  cursor: not-allowed;
}

/* Component Name Editing Input */
.component-name-input {
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid #00ff9d;
  color: inherit;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9em;
  font-weight: 700;
  text-align: center;
  width: 100%;
  min-width: 80px;
  outline: none;
}

.component-name-input:focus {
  box-shadow: 0 0 10px rgba(0, 255, 157, 0.5);
}

/* Loading Question State */
.loading-question {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 16px;
}

.loading-question p {
  color: #64b5f6;
  font-size: 0.95em;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.loading-spinner-large {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 255, 157, 0.3);
  border-top-color: #00ff9d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Deep Dive Modal Styles */
.deep-dive-modal .modal-header {
  background: linear-gradient(90deg, rgba(255, 71, 133, 0.2), transparent);
}

.deep-dive-modal .modal-header h3 {
  color: #ff4785;
}

.ai-question.deep-dive {
  background: rgba(255, 71, 133, 0.1);
  border-left: 4px solid #ff4785;
}

.ai-question.deep-dive .ai-question-title {
  color: #ff4785;
}

/* Dropped component text truncation for editing */
.dropped-component span {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>