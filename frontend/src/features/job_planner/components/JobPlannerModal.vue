<template>
  <transition name="fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
      <div class="job-planner-modal">
        <!-- Header -->
        <header class="modal-header">
          <div class="title-section">
            <div class="planner-badge">💼 JOB PLANNER</div>
            <h2 class="modal-title">AI 채용공고 분석</h2>
          </div>
          <button class="close-btn" @click="closeModal">&times;</button>
        </header>

        <!-- Main Flow Tabs -->
        <div class="flow-tabs">
          <button
            :class="['flow-tab', { active: currentStep === 'input' }]"
            @click="currentStep = 'input'"
          >
            1. 공고 입력
          </button>
          <button
            :class="['flow-tab', { active: currentStep === 'profile' }]"
            @click="currentStep = 'profile'"
            :disabled="!jobData"
          >
            2. 내 정보
          </button>
          <button
            :class="['flow-tab', { active: currentStep === 'agent' }]"
            @click="currentStep = 'agent'"
            :disabled="!analysisResult"
          >
            3. 추가 질문
          </button>
          <button
            :class="['flow-tab', { active: currentStep === 'result' }]"
            @click="currentStep = 'result'"
            :disabled="!analysisResult"
          >
            4. 최종 결과
          </button>
        </div>

        <!-- Content Area -->
        <div class="modal-body">
          <!-- Step 1: 공고 입력 -->
          <div v-if="currentStep === 'input'" class="input-step">
            <h3 class="step-title">채용공고를 입력하세요</h3>

            <!-- URL Input -->
            <div class="input-panel">
              <label>채용공고 URL</label>
              <input
                v-model="urlInput"
                type="text"
                placeholder="https://www.jobkorea.co.kr/..."
                class="url-input"
              >
              <p class="input-hint">
                잡코리아, 사람인, 원티드 등의 채용공고 URL을 입력하세요
              </p>
              <button
                class="btn-parse"
                @click="parseJobPosting"
                :disabled="!urlInput || isParsing"
              >
                <span v-if="!isParsing">🔍 공고 분석</span>
                <span v-else>⏳ 분석 중...</span>
              </button>
            </div>

            <!-- Parsed Job Data Preview -->
            <div v-if="jobData" class="job-preview">
              <h4>✅ 파싱 완료</h4>
              <div class="preview-grid">
                <div class="preview-item">
                  <span class="preview-label">회사</span>
                  <span class="preview-value">{{ jobData.company_name }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">포지션</span>
                  <span class="preview-value">{{ jobData.position }}</span>
                </div>
                <div class="preview-item">
                  <span class="preview-label">경력</span>
                  <span class="preview-value">{{ jobData.experience_range || '-' }}</span>
                </div>
              </div>

              <!-- 주요 업무 -->
              <div v-if="jobData.job_responsibilities" class="preview-detail-section">
                <div class="preview-detail-title">📋 주요 업무</div>
                <div class="preview-detail-content">{{ jobData.job_responsibilities }}</div>
              </div>

              <!-- 필수 요건 -->
              <div v-if="jobData.required_qualifications" class="preview-detail-section">
                <div class="preview-detail-title">✅ 필수 요건</div>
                <div class="preview-detail-content">{{ jobData.required_qualifications }}</div>
                <div v-if="jobData.required_skills && jobData.required_skills.length > 0" class="preview-skill-tags">
                  <span v-for="(skill, idx) in jobData.required_skills" :key="'req-' + idx" class="skill-tag required">
                    {{ skill }}
                  </span>
                </div>
              </div>

              <!-- 우대 조건 -->
              <div v-if="jobData.preferred_qualifications" class="preview-detail-section">
                <div class="preview-detail-title">⭐ 우대 조건</div>
                <div class="preview-detail-content">{{ jobData.preferred_qualifications }}</div>
                <div v-if="jobData.preferred_skills && jobData.preferred_skills.length > 0" class="preview-skill-tags">
                  <span v-for="(skill, idx) in jobData.preferred_skills" :key="'pref-' + idx" class="skill-tag preferred">
                    {{ skill }}
                  </span>
                </div>
              </div>

              <!-- 정보 충분도 인디케이터 -->
              <div v-if="dataCompleteness" class="completeness-indicator">
                <div class="completeness-header">
                  <span class="completeness-icon">
                    {{ dataCompleteness.level === 'good' ? '✅' : dataCompleteness.level === 'fair' ? '⚠️' : '❌' }}
                  </span>
                  <span class="completeness-title">정보 충분도</span>
                  <span class="completeness-score">{{ Math.round(dataCompleteness.rate * 100) }}%</span>
                </div>
                <div class="completeness-bar">
                  <div
                    class="completeness-fill"
                    :class="dataCompleteness.level"
                    :style="{ width: (dataCompleteness.rate * 100) + '%' }"
                  ></div>
                </div>
                <div v-if="needsMoreInfo" class="completeness-warning">
                  <div class="warning-text">
                    ⚠️ 부족한 정보: <strong>{{ missingFields.join(', ') }}</strong>
                  </div>

                  <!-- 추가 입력 섹션 -->
                  <div class="supplement-input-section">
                    <p class="supplement-title">💡 이미지 또는 텍스트를 추가로 입력하면 더 정확하게 분석할 수 있어요</p>

                    <div class="supplement-method-tabs">
                      <button
                        :class="['supp-tab', { active: supplementMethod === 'image' }]"
                        @click="supplementMethod = 'image'"
                      >
                        📸 이미지 추가
                      </button>
                      <button
                        :class="['supp-tab', { active: supplementMethod === 'text' }]"
                        @click="supplementMethod = 'text'"
                      >
                        📝 텍스트 추가
                      </button>
                    </div>

                    <!-- 이미지 업로드 -->
                    <div v-if="supplementMethod === 'image'" class="supplement-panel">
                      <div class="supplement-upload-area" @click="$refs.supplementImageInput.click()">
                        <input
                          ref="supplementImageInput"
                          type="file"
                          accept="image/*"
                          multiple
                          @change="handleSupplementImageUpload"
                          style="display: none"
                        >
                        <div v-if="supplementImages.length === 0" class="upload-placeholder">
                          <div class="upload-icon">📸</div>
                          <p>채용공고 이미지를 추가로 업로드하세요</p>
                          <p class="upload-hint">PNG, JPG, JPEG 지원 • 여러 장 선택 가능</p>
                        </div>
                        <div v-else class="image-previews-grid">
                          <div
                            v-for="(preview, idx) in supplementImagePreviews"
                            :key="idx"
                            class="image-preview-item"
                          >
                            <img :src="preview" alt="미리보기">
                            <button class="btn-remove-image" @click.stop="removeSupplementImage(idx)">&times;</button>
                            <div class="image-number">{{ idx + 1 }}</div>
                          </div>
                        </div>
                      </div>
                      <button
                        class="btn-supplement-parse"
                        @click="parseSupplementData"
                        :disabled="supplementImages.length === 0 || isSupplementParsing"
                      >
                        <span v-if="!isSupplementParsing">🔍 추가 분석 {{ supplementImages.length > 0 ? `(${supplementImages.length}장)` : '' }}</span>
                        <span v-else>⏳ 분석 중...</span>
                      </button>
                    </div>

                    <!-- 텍스트 입력 -->
                    <div v-if="supplementMethod === 'text'" class="supplement-panel">
                      <textarea
                        v-model="supplementText"
                        rows="6"
                        placeholder="채용공고 내용을 붙여넣으세요...

예시:
[회사명] 테크 스타트업
[포지션] 백엔드 개발자
[필수 스킬] Python, Django, PostgreSQL
..."
                        class="supplement-textarea"
                      ></textarea>
                      <button
                        class="btn-supplement-parse"
                        @click="parseSupplementData"
                        :disabled="!supplementText.trim() || isSupplementParsing"
                      >
                        <span v-if="!isSupplementParsing">🔍 추가 분석</span>
                        <span v-else>⏳ 분석 중...</span>
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="completeness-success">
                  ✅ 충분한 정보가 수집되었습니다
                </div>
              </div>

              <div class="job-preview-actions">
                <button class="btn-reset-job" @click="resetJobData">
                  🔄 공고 초기화
                </button>
                <button class="btn-next" @click="currentStep = 'profile'">
                  다음: 내 정보 입력 →
                </button>
              </div>
            </div>
          </div>

          <!-- Step 2: 내 프로필 -->
          <div v-if="currentStep === 'profile'" class="profile-step">
            <h3 class="step-title">내 정보를 입력하세요</h3>

            <div class="profile-form">
              <!-- 기업분석 섹션 (먼저 실행되도록 최상단 배치) -->
              <div class="company-analysis-section">
                <h4 class="section-subtitle">🏢 기업 분석 (선택사항)</h4>
                <p class="section-hint">⏱️ 시간이 걸리니 먼저 분석을 시작하고, 아래 정보를 입력하세요</p>

                <div class="company-input-tabs">
                  <button
                    :class="['company-tab', { active: companyAnalysisType === 'url' }]"
                    @click="companyAnalysisType = 'url'"
                  >
                    🔗 URL
                  </button>
                  <button
                    :class="['company-tab', { active: companyAnalysisType === 'text' }]"
                    @click="companyAnalysisType = 'text'"
                  >
                    📝 텍스트
                  </button>
                </div>

                <div v-if="companyAnalysisType === 'url'" class="company-input-panel">
                  <input
                    v-model="companyUrl"
                    type="text"
                    placeholder="https://company.com 또는 https://www.wanted.co.kr/company/..."
                    class="company-input"
                  >
                </div>

                <div v-else class="company-input-panel">
                  <textarea
                    v-model="companyText"
                    rows="4"
                    placeholder="회사 정보를 입력하세요 (예: 설립연도, 사업 분야, 기술 스택, 복지 등)"
                    class="company-textarea"
                  ></textarea>
                </div>

                <button
                  v-if="(companyAnalysisType === 'url' && companyUrl) || (companyAnalysisType === 'text' && companyText)"
                  class="btn-company-analyze"
                  @click="analyzeCompany"
                  :disabled="isAnalyzingCompany"
                >
                  <span v-if="!isAnalyzingCompany">🔍 기업 분석하기</span>
                  <span v-else>⏳ 분석 중...</span>
                </button>

                <div v-if="companyAnalysis" class="company-analysis-preview">
                  <div class="preview-badge">✅ 기업분석 완료</div>
                  <div class="preview-score">
                    종합 점수: {{ (companyAnalysis.overall_score?.total_score * 100).toFixed(0) }}점
                  </div>
                </div>
              </div>

              <!-- 기본 정보 -->
              <div class="form-section">
                <h4 class="form-section-title">📝 기본 정보</h4>
                <div class="form-row-2col">
                  <div class="form-group">
                    <label>이름 <span class="optional">(선택)</span></label>
                    <input
                      v-model="name"
                      type="text"
                      placeholder="홍길동"
                    >
                  </div>
                  <div class="form-group">
                    <label>현재 직무 <span class="optional">(선택)</span></label>
                    <input
                      v-model="currentRole"
                      type="text"
                      placeholder="백엔드 개발자"
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>경력 (년) <span class="required">*</span></label>
                    <input
                      v-model.number="experienceYears"
                      type="number"
                      min="0"
                      placeholder="2"
                    >
                  </div>
                </div>
              </div>

              <!-- 스킬 및 숙련도 -->
              <div class="form-section">
                <h4 class="form-section-title">💻 보유 스킬 및 숙련도 <span class="required">*</span></h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>보유 스킬 (쉼표로 구분)</label>
                    <input
                      v-model="userSkillsInput"
                      type="text"
                      placeholder="Python, Django, MySQL, React"
                      @input="parseUserSkills"
                    >
                    <p class="input-hint">입력 후 아래에서 각 스킬의 숙련도를 선택하세요</p>
                  </div>
                </div>

                <!-- 스킬 레벨 입력 -->
                <div v-if="userSkills.length > 0" class="skill-levels-container">
                  <div
                    v-for="skill in userSkills"
                    :key="skill"
                    class="skill-level-item"
                  >
                    <div class="skill-name">{{ skill }}</div>
                    <div class="skill-level-selector">
                      <button
                        v-for="level in [1, 2, 3, 4, 5]"
                        :key="level"
                        :class="['level-btn', { active: skillLevels[skill] === level }]"
                        @click="skillLevels[skill] = level"
                      >
                        {{ level }}
                      </button>
                    </div>
                    <div class="skill-level-label">
                      {{ getLevelLabel(skillLevels[skill] || 3) }}
                    </div>
                  </div>
                  <p class="level-guide">
                    1=입문 | 2=초급 | 3=중급 | 4=고급 | 5=전문가
                  </p>
                </div>
              </div>

              <!-- 추가 정보 -->
              <div class="form-section">
                <h4 class="form-section-title">🎓 추가 정보 <span class="optional">(선택)</span></h4>
                <div class="form-row">
                  <div class="form-group">
                    <label>학력</label>
                    <input
                      v-model="education"
                      type="text"
                      placeholder="예: 컴퓨터공학 학사"
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>자격증 (쉼표로 구분)</label>
                    <input
                      v-model="certificationsInput"
                      type="text"
                      placeholder="정보처리기사, AWS Solutions Architect"
                      @input="parseCertifications"
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>커리어 목표</label>
                    <textarea
                      v-model="careerGoals"
                      rows="2"
                      placeholder="예: 대규모 트래픽을 처리하는 백엔드 시스템 개발 경험 쌓기"
                    ></textarea>
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label>준비 가능 일수</label>
                    <input
                      v-model.number="availablePrepDays"
                      type="number"
                      min="0"
                      placeholder="14"
                    >
                    <p class="input-hint">면접까지 준비할 수 있는 날짜 수</p>
                  </div>
                </div>
              </div>

              <button
                class="btn-analyze"
                @click="analyzeMatch"
                :disabled="!userSkills.length || isAnalyzing"
              >
                <span v-if="!isAnalyzing">🚀 매칭 분석 시작</span>
                <span v-else>⏳ 분석 중...</span>
              </button>
            </div>
          </div>

          <!-- Step 2.5: 에이전트 추가 질문 -->
          <div v-if="currentStep === 'agent'" class="agent-step">
            <h3 class="step-title">📋 추가 정보가 필요합니다</h3>
            <p class="step-description">
              부족한 스킬에 대해 몇 가지 질문에 답변해주세요. 더 정확한 분석을 제공할 수 있습니다.
            </p>

            <!-- 질문 로딩 중 -->
            <div v-if="agentQuestions.length === 0" class="loading-questions">
              <div class="loading-spinner"></div>
              <p class="loading-text">💭 맞춤형 질문을 생성하고 있습니다...</p>
            </div>

            <div v-else class="agent-questions-list">
              <div
                v-for="(q, idx) in agentQuestions"
                :key="q.id"
                class="agent-question-item"
              >
                <div class="question-header">
                  <span class="question-number">Q{{ idx + 1 }}</span>
                  <span class="question-skill">{{ q.skill }}</span>
                </div>
                <div class="question-text">{{ q.question }}</div>
                <textarea
                  v-model="agentAnswers[q.id]"
                  rows="3"
                  :placeholder="`${q.skill}에 대한 답변을 입력하세요...`"
                  class="answer-input"
                ></textarea>
              </div>
            </div>

            <div class="agent-actions">
              <button class="btn-skip" @click="skipAgentQuestions">
                건너뛰기
              </button>
              <button
                class="btn-generate-report"
                @click="generateFinalReport(true)"
                :disabled="isGeneratingReport"
              >
                <span v-if="!isGeneratingReport">🚀 최종 보고서 생성</span>
                <span v-else>⏳ 보고서 생성 중...</span>
              </button>
            </div>
          </div>

          <!-- Step 3: 분석 결과 -->
          <div v-if="currentStep === 'result' && analysisResult" class="result-step">
            <h3 class="step-title">분석 결과</h3>

            <!-- Score Overview -->
            <div class="score-overview">
              <div class="score-card">
                <div class="score-label">준비도</div>
                <div class="score-value" :class="getScoreClass(analysisResult.readiness_score)">
                  {{ (analysisResult.readiness_score * 100).toFixed(1) }}%
                </div>
              </div>
              <div class="score-card">
                <div class="score-label">스킬 갭</div>
                <div class="score-value" :class="getScoreClass(1 - analysisResult.skill_gap_score)">
                  {{ (analysisResult.skill_gap_score * 100).toFixed(1) }}%
                </div>
              </div>
              <div class="score-card">
                <div class="score-label">경력 적합도</div>
                <div class="score-value" :class="getScoreClass(analysisResult.experience_fit)">
                  {{ (analysisResult.experience_fit * 100).toFixed(1) }}%
                </div>
              </div>
              <div v-if="analysisResult.proficiency_score" class="score-card">
                <div class="score-label">숙련도</div>
                <div class="score-value" :class="getScoreClass(analysisResult.proficiency_score)">
                  {{ (analysisResult.proficiency_score * 100).toFixed(1) }}%
                </div>
              </div>
            </div>

            <!-- Insights -->
            <div v-if="analysisResult.insights && analysisResult.insights.length > 0" class="insights-section">
              <h4 class="section-subtitle">💡 인사이트</h4>
              <div class="insights-list">
                <div
                  v-for="(insight, idx) in analysisResult.insights"
                  :key="'insight-' + idx"
                  :class="['insight-item', insight.type]"
                >
                  <div class="insight-header">
                    <span class="insight-icon">
                      {{ insight.type === 'positive' ? '✅' : insight.type === 'warning' ? '⚠️' : 'ℹ️' }}
                    </span>
                    <span class="insight-title">{{ insight.title }}</span>
                  </div>
                  <div class="insight-message">{{ insight.message }}</div>
                </div>
              </div>
            </div>

            <!-- Matched Skills -->
            <div class="skill-section">
              <h4 class="section-subtitle">✅ 매칭된 스킬 ({{ analysisResult.matched_skills.length }}개)</h4>
              <div class="skill-list matched">
                <div
                  v-for="(match, idx) in analysisResult.matched_skills"
                  :key="'matched-' + idx"
                  class="skill-item"
                >
                  <span class="skill-required">{{ match.required }}</span>
                  <span class="skill-arrow">↔</span>
                  <span class="skill-user">{{ match.user_skill }}</span>
                  <span class="skill-similarity">{{ (match.similarity * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>

            <!-- Missing Skills -->
            <div class="skill-section" v-if="analysisResult.missing_skills.length > 0">
              <h4 class="section-subtitle">❌ 부족한 스킬 ({{ analysisResult.missing_skills.length }}개)</h4>
              <div class="skill-list missing">
                <div
                  v-for="(miss, idx) in analysisResult.missing_skills"
                  :key="'missing-' + idx"
                  class="skill-item"
                >
                  <span class="skill-name">{{ miss.required }}</span>
                </div>
              </div>
            </div>

            <!-- Job Recommendations -->
            <div v-if="recommendations.length > 0" class="recommendations-section">
              <h3 class="recommendations-title">💡 추천 채용공고</h3>
              <p class="recommendations-subtitle">
                현재 스킬과 더 잘 맞는 공고들을 찾았습니다 ({{ recommendations.length }}개)
              </p>

              <div class="recommendations-list">
                <div
                  v-for="(rec, idx) in recommendations"
                  :key="'rec-' + idx"
                  class="recommendation-card"
                >
                  <div class="rec-header">
                    <div class="rec-main-info">
                      <h4 class="rec-title">{{ rec.title }}</h4>
                      <div class="rec-company">{{ rec.company_name }}</div>
                    </div>
                    <div class="rec-match">
                      <div class="rec-match-rate" :class="getScoreClass(rec.match_rate)">
                        {{ (rec.match_rate * 100).toFixed(0) }}%
                      </div>
                      <div class="rec-match-label">매칭률</div>
                    </div>
                  </div>

                  <div class="rec-details">
                    <div class="rec-info-row">
                      <span class="rec-label">📍 위치:</span>
                      <span class="rec-value">{{ rec.location || '정보 없음' }}</span>
                    </div>
                    <div class="rec-info-row">
                      <span class="rec-label">🔗 출처:</span>
                      <span class="rec-value">{{ rec.source }}</span>
                    </div>
                    <div class="rec-info-row">
                      <span class="rec-label">✅ 매칭:</span>
                      <span class="rec-value">{{ rec.matched_count }} / {{ rec.total_skills }}개 스킬</span>
                    </div>
                  </div>

                  <div class="rec-reason">
                    <span class="rec-reason-icon">💬</span>
                    <span class="rec-reason-text">{{ rec.reason }}</span>
                  </div>

                  <div class="rec-skills">
                    <span class="rec-skill-label">요구 스킬:</span>
                    <div class="rec-skill-tags">
                      <span
                        v-for="(skill, sidx) in rec.skills.slice(0, 6)"
                        :key="'skill-' + sidx"
                        class="rec-skill-tag"
                      >
                        {{ skill }}
                      </span>
                      <span v-if="rec.skills.length > 6" class="rec-skill-more">
                        +{{ rec.skills.length - 6 }}
                      </span>
                    </div>
                  </div>

                  <a
                    v-if="rec.url"
                    :href="rec.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="rec-link"
                  >
                    공고 보러가기 →
                  </a>
                </div>
              </div>
            </div>

            <!-- Loading Recommendations -->
            <div v-if="isLoadingRecommendations || (analysisResult && analysisResult.readiness_score < 0.6 && recommendations.length === 0 && !isLoadingRecommendations)" class="loading-recommendations">
              <div class="loading-spinner"></div>
              <p v-if="isLoadingRecommendations">
                추천 공고를 찾고 있습니다... (사람인, 잡코리아 검색 중)
              </p>
              <p v-else>
                추천 공고를 준비 중입니다...
              </p>
            </div>

            <!-- Company Analysis Results -->
            <div v-if="companyAnalysis" class="company-analysis-results">
              <h3 class="analysis-title">🏢 기업 분석 결과</h3>

              <!-- Overall Scores -->
              <div class="company-score-grid">
                <div class="company-score-card">
                  <div class="score-label">기술력</div>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: (companyAnalysis.overall_score.tech_score * 100) + '%' }"></div>
                  </div>
                  <div class="score-text">{{ (companyAnalysis.overall_score.tech_score * 100).toFixed(0) }}점</div>
                </div>
                <div class="company-score-card">
                  <div class="score-label">성장성</div>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: (companyAnalysis.overall_score.growth_score * 100) + '%' }"></div>
                  </div>
                  <div class="score-text">{{ (companyAnalysis.overall_score.growth_score * 100).toFixed(0) }}점</div>
                </div>
                <div class="company-score-card">
                  <div class="score-label">복지</div>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: (companyAnalysis.overall_score.welfare_score * 100) + '%' }"></div>
                  </div>
                  <div class="score-text">{{ (companyAnalysis.overall_score.welfare_score * 100).toFixed(0) }}점</div>
                </div>
              </div>

              <!-- Company Overview -->
              <div class="analysis-section">
                <h4 class="section-subtitle">📋 회사 개요</h4>
                <div class="analysis-content">
                  <p>{{ companyAnalysis.overview.description }}</p>
                  <div class="info-grid">
                    <div class="info-item" v-if="companyAnalysis.overview.industry">
                      <span class="info-label">산업:</span>
                      <span class="info-value">{{ companyAnalysis.overview.industry }}</span>
                    </div>
                    <div class="info-item" v-if="companyAnalysis.overview.size">
                      <span class="info-label">규모:</span>
                      <span class="info-value">{{ companyAnalysis.overview.size }}</span>
                    </div>
                    <div class="info-item" v-if="companyAnalysis.overview.founded_year">
                      <span class="info-label">설립:</span>
                      <span class="info-value">{{ companyAnalysis.overview.founded_year }}년</span>
                    </div>
                  </div>
                  <p v-if="companyAnalysis.overview.vision" class="vision-text">
                    <strong>비전:</strong> {{ companyAnalysis.overview.vision }}
                  </p>
                </div>
              </div>

              <!-- Tech Stack -->
              <div class="analysis-section">
                <h4 class="section-subtitle">💻 기술 스택 및 개발 문화</h4>
                <div class="analysis-content">
                  <div class="tech-tags" v-if="companyAnalysis.tech_stack.languages?.length">
                    <span class="tag-label">언어:</span>
                    <span v-for="(lang, idx) in companyAnalysis.tech_stack.languages" :key="'lang-' + idx" class="tech-tag">
                      {{ lang }}
                    </span>
                  </div>
                  <div class="tech-tags" v-if="companyAnalysis.tech_stack.frameworks?.length">
                    <span class="tag-label">프레임워크:</span>
                    <span v-for="(fw, idx) in companyAnalysis.tech_stack.frameworks" :key="'fw-' + idx" class="tech-tag">
                      {{ fw }}
                    </span>
                  </div>
                  <div class="tech-tags" v-if="companyAnalysis.tech_stack.tools?.length">
                    <span class="tag-label">도구:</span>
                    <span v-for="(tool, idx) in companyAnalysis.tech_stack.tools" :key="'tool-' + idx" class="tech-tag">
                      {{ tool }}
                    </span>
                  </div>
                  <p v-if="companyAnalysis.tech_stack.culture">{{ companyAnalysis.tech_stack.culture }}</p>
                  <p v-if="companyAnalysis.tech_stack.tech_blog" class="tech-blog-info">
                    📝 {{ companyAnalysis.tech_stack.tech_blog }}
                  </p>
                </div>
              </div>

              <!-- Growth & Stability -->
              <div class="analysis-section">
                <h4 class="section-subtitle">📈 성장성 및 안정성</h4>
                <div class="analysis-content">
                  <div class="growth-grid">
                    <div class="growth-item">
                      <span class="growth-label">투자:</span>
                      <span class="growth-value">{{ companyAnalysis.growth.funding || '정보 없음' }}</span>
                    </div>
                    <div class="growth-item">
                      <span class="growth-label">시장 위치:</span>
                      <span class="growth-value">{{ companyAnalysis.growth.market_position || '정보 없음' }}</span>
                    </div>
                    <div class="growth-item">
                      <span class="growth-label">성장 가능성:</span>
                      <span :class="['growth-badge', companyAnalysis.growth.growth_potential]">
                        {{ companyAnalysis.growth.growth_potential }}
                      </span>
                    </div>
                    <div class="growth-item">
                      <span class="growth-label">안정성:</span>
                      <span :class="['growth-badge', companyAnalysis.growth.stability]">
                        {{ companyAnalysis.growth.stability }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Welfare -->
              <div class="analysis-section">
                <h4 class="section-subtitle">🎁 복지 및 근무환경</h4>
                <div class="analysis-content">
                  <div class="welfare-item" v-if="companyAnalysis.welfare.salary_level">
                    <strong>연봉 수준:</strong> {{ companyAnalysis.welfare.salary_level }}
                  </div>
                  <div class="welfare-item" v-if="companyAnalysis.welfare.benefits?.length">
                    <strong>복지 혜택:</strong>
                    <ul class="benefits-list">
                      <li v-for="(benefit, idx) in companyAnalysis.welfare.benefits" :key="'benefit-' + idx">
                        {{ benefit }}
                      </li>
                    </ul>
                  </div>
                  <div class="welfare-item" v-if="companyAnalysis.welfare.work_life_balance">
                    <strong>워라밸:</strong> {{ companyAnalysis.welfare.work_life_balance }}
                  </div>
                  <div class="welfare-item" v-if="companyAnalysis.welfare.remote_work">
                    <strong>리모트:</strong> {{ companyAnalysis.welfare.remote_work }}
                  </div>
                </div>
              </div>

              <!-- Recommendation -->
              <div class="analysis-section recommendation-section">
                <h4 class="section-subtitle">💡 종합 평가</h4>
                <div class="recommendation-content">
                  {{ companyAnalysis.recommendation }}
                </div>
              </div>
            </div>

            <!-- Final Report -->
            <div v-if="finalReport" class="final-report-section">
              <h3 class="report-title">📊 종합 취업 전략 보고서</h3>

              <!-- SWOT Analysis -->
              <div class="swot-section">
                <h4 class="section-subtitle">🎯 SWOT 분석</h4>
                <div class="swot-grid">
                  <div class="swot-card strengths">
                    <div class="swot-header">💪 Strengths (강점)</div>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in finalReport.swot.strengths" :key="'s-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="swot-card weaknesses">
                    <div class="swot-header">⚠️ Weaknesses (약점)</div>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in finalReport.swot.weaknesses" :key="'w-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="swot-card opportunities">
                    <div class="swot-header">🌟 Opportunities (기회)</div>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in finalReport.swot.opportunities" :key="'o-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="swot-card threats">
                    <div class="swot-header">🚨 Threats (위협)</div>
                    <ul class="swot-list">
                      <li v-for="(item, idx) in finalReport.swot.threats" :key="'t-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Interview Questions -->
              <div class="interview-section">
                <h4 class="section-subtitle">💬 예상 면접 질문 TOP 5</h4>
                <div class="interview-questions-list">
                  <div
                    v-for="(q, idx) in finalReport.interview_questions"
                    :key="'iq-' + idx"
                    class="interview-question-card"
                  >
                    <div class="question-number-badge">Q{{ idx + 1 }}</div>
                    <div class="question-content">
                      <div class="question-title">{{ q.question }}</div>
                      <div class="answer-guide">
                        <strong>답변 가이드:</strong> {{ q.answer_guide }}
                      </div>
                      <div v-if="q.tips" class="tips">
                        <strong>💡 Tip:</strong> {{ q.tips }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Experience Packaging -->
              <div class="packaging-section">
                <h4 class="section-subtitle">📦 경험 포장 가이드</h4>
                <div class="packaging-grid">
                  <div class="packaging-card">
                    <div class="packaging-title">📄 이력서 강조 포인트</div>
                    <ul class="packaging-list">
                      <li v-for="(item, idx) in finalReport.experience_packaging.resume_highlights" :key="'rh-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="packaging-card">
                    <div class="packaging-title">💼 포트폴리오 팁</div>
                    <ul class="packaging-list">
                      <li v-for="(item, idx) in finalReport.experience_packaging.portfolio_tips" :key="'pt-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                  <div class="packaging-card">
                    <div class="packaging-title">🛠️ 스킬 보완 전략</div>
                    <ul class="packaging-list">
                      <li v-for="(item, idx) in finalReport.experience_packaging.skill_compensation" :key="'sc-' + idx">
                        {{ item }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Execution Strategy -->
              <div class="execution-section">
                <h4 class="section-subtitle">🎯 실행 전략</h4>
                <div class="timeline">
                  <div class="timeline-item immediate">
                    <div class="timeline-badge">🔥 즉시</div>
                    <div class="timeline-content">
                      <ul class="timeline-list">
                        <li v-for="(item, idx) in finalReport.execution_strategy.immediate" :key="'im-' + idx">
                          {{ item }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div class="timeline-item short-term">
                    <div class="timeline-badge">⚡ 1-2주</div>
                    <div class="timeline-content">
                      <ul class="timeline-list">
                        <li v-for="(item, idx) in finalReport.execution_strategy.short_term" :key="'st-' + idx">
                          {{ item }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div class="timeline-item mid-term">
                    <div class="timeline-badge">📅 1개월</div>
                    <div class="timeline-content">
                      <ul class="timeline-list">
                        <li v-for="(item, idx) in finalReport.execution_strategy.mid_term" :key="'mt-' + idx">
                          {{ item }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div class="timeline-item application">
                    <div class="timeline-badge">🎯 지원 시점</div>
                    <div class="timeline-content">
                      <p class="application-timing">{{ finalReport.execution_strategy.application_timing }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Final Message -->
              <div class="final-message-section">
                <div class="final-message">
                  {{ finalReport.final_message }}
                </div>
              </div>
            </div>

            <button class="btn-restart" @click="resetAll">
              🔄 새로운 공고 분석하기
            </button>
          </div>

          <!-- Error Display -->
          <div v-if="errorMessage" class="error-banner">
            ⚠️ {{ errorMessage }}
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from 'axios';
import { useGameStore } from '@/stores/game';

export default {
  name: 'JobPlannerModal',
  props: {
    isOpen: Boolean
  },
  data() {
    return {
      currentStep: 'input',

      // Input data
      urlInput: '',

      // Parsed job data
      jobData: null,
      dataCompleteness: null,  // 정보 충분도 평가
      needsMoreInfo: false,    // 추가 정보 필요 여부
      missingFields: [],       // 부족한 필드 목록

      // 추가 입력 (URL 파싱 후 정보 부족 시)
      supplementMethod: 'image',     // 'image' | 'text'
      supplementImages: [],
      supplementImagePreviews: [],
      supplementText: '',
      isSupplementParsing: false,

      // User data
      name: '',
      currentRole: '',
      experienceYears: 0,
      userSkills: [],
      userSkillsInput: '',
      skillLevels: {},  // {"Python": 4, "Django": 3}
      education: '',
      certifications: [],
      certificationsInput: '',
      careerGoals: '',
      availablePrepDays: null,

      // Company Analysis
      companyAnalysisType: 'url',  // 'url' or 'text'
      companyUrl: '',
      companyText: '',
      companyAnalysis: null,
      isAnalyzingCompany: false,

      // Analysis result
      analysisResult: null,

      // Agent Questions & Report
      agentQuestions: [],
      agentAnswers: {},
      finalReport: null,
      isGeneratingReport: false,

      // Recommendations
      recommendations: [],
      isLoadingRecommendations: false,

      // Status
      isParsing: false,
      isAnalyzing: false,
      errorMessage: ''
    };
  },
  methods: {
    closeModal() {
      this.$emit('close');
    },

    async parseJobPosting() {
      this.isParsing = true;
      this.errorMessage = '';

      try {
        const requestData = { type: 'url', url: this.urlInput };
        const response = await axios.post('/api/core/job-planner/parse/', requestData);
        this.mergeJobData(response.data);

      } catch (error) {
        console.error('파싱 실패:', error);
        this.errorMessage = error.response?.data?.error || '공고 파싱 중 오류가 발생했습니다.';
      } finally {
        this.isParsing = false;

        if (this.jobData) {
          this.checkDataCompleteness();
          const gameStore = useGameStore();
          gameStore.setLastParsedJob(this.jobData);
        }
      }
    },

    checkDataCompleteness() {
      // 정보 충분도 평가
      const missing = [];
      let score = 0;
      const maxScore = 7;

      // 1. 회사명 (필수)
      if (this.jobData.company_name &&
          this.jobData.company_name !== '알 수 없음' &&
          this.jobData.company_name.trim() !== '') {
        score += 1;
      } else {
        missing.push('회사명');
      }

      // 2. 포지션 (필수)
      if (this.jobData.position &&
          this.jobData.position !== '개발자' &&
          this.jobData.position.trim() !== '') {
        score += 1;
      } else {
        missing.push('포지션');
      }

      // 3. 필수 스킬 (중요)
      if (this.jobData.required_skills && this.jobData.required_skills.length > 0) {
        score += 2;  // 가중치 높음
      } else {
        missing.push('필수 스킬');
      }

      // 4. 주요 업무
      if (this.jobData.job_responsibilities &&
          this.jobData.job_responsibilities.length > 20) {
        score += 1;
      } else {
        missing.push('주요 업무');
      }

      // 5. 필수 요건
      if (this.jobData.required_qualifications &&
          this.jobData.required_qualifications !== '정보 없음' &&
          this.jobData.required_qualifications.length > 10) {
        score += 1;
      } else {
        missing.push('필수 요건');
      }

      // 6. 우대 조건 (선택)
      if (this.jobData.preferred_qualifications &&
          this.jobData.preferred_qualifications !== '정보 없음' &&
          this.jobData.preferred_qualifications.length > 10) {
        score += 1;
      }

      const completenessRate = score / maxScore;

      this.dataCompleteness = {
        score: score,
        maxScore: maxScore,
        rate: completenessRate,
        level: completenessRate >= 0.7 ? 'good' : completenessRate >= 0.4 ? 'fair' : 'poor'
      };

      this.missingFields = missing;
      this.needsMoreInfo = completenessRate < 0.7;
    },

    handleSupplementImageUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        this.supplementImages.push(file);
        const reader = new FileReader();
        reader.onload = (e) => {
          this.supplementImagePreviews.push(e.target.result);
        };
        reader.readAsDataURL(file);
      });
    },

    removeSupplementImage(index) {
      this.supplementImages.splice(index, 1);
      this.supplementImagePreviews.splice(index, 1);
    },

    async parseSupplementData() {
      this.isSupplementParsing = true;
      this.errorMessage = '';

      try {
        if (this.supplementMethod === 'image') {
          for (let i = 0; i < this.supplementImages.length; i++) {
            const file = this.supplementImages[i];
            const reader = new FileReader();
            const base64Promise = new Promise((resolve) => {
              reader.onload = (e) => resolve(e.target.result);
              reader.readAsDataURL(file);
            });
            const imageData = await base64Promise;
            const response = await axios.post('/api/core/job-planner/parse/', { type: 'image', image: imageData });
            this.mergeJobData(response.data);
          }
          // 업로드한 이미지 초기화
          this.supplementImages = [];
          this.supplementImagePreviews = [];
        } else if (this.supplementMethod === 'text') {
          const response = await axios.post('/api/core/job-planner/parse/', { type: 'text', text: this.supplementText });
          this.mergeJobData(response.data);
          this.supplementText = '';
        }
      } catch (error) {
        console.error('추가 파싱 실패:', error);
        this.errorMessage = error.response?.data?.error || '추가 분석 중 오류가 발생했습니다.';
      } finally {
        this.isSupplementParsing = false;
        if (this.jobData) {
          this.checkDataCompleteness();
        }
      }
    },

    mergeJobData(newData) {
      // 유효한 값인지 체크 (빈 값이나 기본값이 아닌지)
      const isValidValue = (value) => {
        if (!value) return false;
        if (typeof value === 'string') {
          const normalized = value.trim().toLowerCase();
          return normalized !== '' &&
                 normalized !== '알 수 없음' &&
                 normalized !== '정보 없음' &&
                 normalized !== 'unknown';
        }
        return true;
      };

      // 텍스트 필드 병합 함수 (중복 내용 체크)
      const mergeText = (oldText, newText) => {
        // 타입 체크 및 문자열 변환
        if (typeof oldText !== 'string') {
          oldText = oldText ? String(oldText) : '';
        }
        if (typeof newText !== 'string') {
          newText = newText ? String(newText) : '';
        }

        // 빈 값 체크
        if (!oldText || oldText.trim() === '') return newText || '';
        if (!newText || newText.trim() === '') return oldText;

        // 정확히 같은 내용이면 중복 추가 안함
        if (oldText.trim() === newText.trim()) return oldText;

        // 새로운 텍스트가 이미 포함되어 있으면 추가 안함
        if (oldText.includes(newText.trim())) return oldText;

        // 기존 텍스트가 새로운 텍스트에 포함되어 있으면 새로운 것으로 대체
        if (newText.includes(oldText.trim())) return newText;

        return `${oldText}\n\n${newText}`;
      };

      if (this.jobData) {
        this.jobData = {
          // 회사명과 포지션은 유효한 값일 때만 업데이트
          company_name: isValidValue(newData.company_name) ? newData.company_name : this.jobData.company_name,
          position: isValidValue(newData.position) ? newData.position : this.jobData.position,

          // 스킬 배열 병합 (중복 제거)
          required_skills: [...new Set([
            ...(this.jobData.required_skills || []),
            ...(newData.required_skills || [])
          ])],
          preferred_skills: [...new Set([
            ...(this.jobData.preferred_skills || []),
            ...(newData.preferred_skills || [])
          ])],

          // 텍스트 필드 병합 (중복 체크)
          job_responsibilities: mergeText(this.jobData.job_responsibilities, newData.job_responsibilities),
          required_qualifications: mergeText(this.jobData.required_qualifications, newData.required_qualifications),
          preferred_qualifications: mergeText(this.jobData.preferred_qualifications, newData.preferred_qualifications),

          experience_range: isValidValue(newData.experience_range) ? newData.experience_range : this.jobData.experience_range,
          deadline: newData.deadline || this.jobData.deadline,
          source: this.jobData.source.includes(newData.source) ? this.jobData.source : this.jobData.source + ' + ' + newData.source,
          raw_text: this.jobData.raw_text + '\n\n---\n\n' + newData.raw_text
        };
      } else {
        this.jobData = newData;
      }
    },

    async analyzeMatch() {
      this.isAnalyzing = true;
      this.errorMessage = '';

      try {
        // 스킬 레벨 기본값 설정 (입력 안한 스킬은 3으로)
        const completedSkillLevels = {};
        this.userSkills.forEach(skill => {
          completedSkillLevels[skill] = this.skillLevels[skill] || 3;
        });

        const response = await axios.post('/api/core/job-planner/analyze/', {
          // 기본 프로필
          user_skills: this.userSkills,
          skill_levels: completedSkillLevels,
          experience_years: this.experienceYears,

          // 상세 프로필
          name: this.name,
          current_role: this.currentRole,
          education: this.education,
          certifications: this.certifications,
          career_goals: this.careerGoals,
          available_prep_days: this.availablePrepDays,

          // 채용공고 정보
          required_skills: this.jobData.required_skills,
          preferred_skills: this.jobData.preferred_skills,
          experience_range: this.jobData.experience_range,

          // 필수/우대 요건 전체 텍스트 (추가 역량 추출용)
          required_qualifications: this.jobData.required_qualifications || '',
          preferred_qualifications: this.jobData.preferred_qualifications || '',
          job_responsibilities: this.jobData.job_responsibilities || ''
        });

        this.analysisResult = response.data;

        // 부족한 스킬이 있으면 에이전트 질문 페이지로 이동
        if (this.analysisResult.missing_skills && this.analysisResult.missing_skills.length > 0) {
          this.currentStep = 'agent';

          this.fetchAgentQuestions();

          if (this.analysisResult.readiness_score < 0.6) {
            this.fetchRecommendations();
          }

          this.generateFinalReport();
        } else {
          this.currentStep = 'result';

          if (this.analysisResult.readiness_score < 0.6) {
            this.fetchRecommendations();
          }

          this.generateFinalReport();
        }

      } catch (error) {
        console.error('분석 실패:', error);
        this.errorMessage = error.response?.data?.error || '분석 중 오류가 발생했습니다.';
      } finally {
        this.isAnalyzing = false;
      }
    },

    async fetchAgentQuestions() {
      try {
        const response = await axios.post('/api/core/job-planner/agent-questions/', {
          missing_skills: this.analysisResult.missing_skills,
          matched_skills: this.analysisResult.matched_skills,
          user_profile: this.analysisResult.profile_summary
        });

        this.agentQuestions = response.data.questions || [];

        // 각 질문에 대한 답변 초기화
        this.agentAnswers = {};
        this.agentQuestions.forEach(q => {
          this.agentAnswers[q.id] = '';
        });

      } catch (error) {
        console.error('질문 생성 실패:', error);
        // 질문 생성 실패해도 계속 진행
        this.agentQuestions = [];
      }
    },

    async generateFinalReport(autoNavigate = false) {
      this.isGeneratingReport = true;
      this.errorMessage = '';

      try {
        const response = await axios.post('/api/core/job-planner/agent-report/', {
          job_data: this.jobData,
          analysis_result: this.analysisResult,
          company_analysis: this.companyAnalysis,
          agent_answers: this.agentAnswers
        });

        this.finalReport = response.data;

        // autoNavigate가 true일 때만 자동으로 페이지 전환
        if (autoNavigate) {
          this.currentStep = 'result';
        }

      } catch (error) {
        console.error('보고서 생성 실패:', error);
        this.errorMessage = error.response?.data?.error || '보고서 생성 중 오류가 발생했습니다.';
      } finally {
        this.isGeneratingReport = false;
      }
    },

    skipAgentQuestions() {
      // 질문 건너뛰고 바로 최종 보고서 생성 (자동 페이지 전환)
      this.agentAnswers = {};
      this.generateFinalReport(true);  // autoNavigate = true
    },

    async fetchRecommendations() {
      this.isLoadingRecommendations = true;
      this.errorMessage = '';

      try {
        // 스킬 레벨 기본값 설정
        const completedSkillLevels = {};
        this.userSkills.forEach(skill => {
          completedSkillLevels[skill] = this.skillLevels[skill] || 3;
        });

        const response = await axios.post('/api/core/job-planner/recommend/', {
          user_skills: this.userSkills,
          skill_levels: completedSkillLevels,
          readiness_score: this.analysisResult.readiness_score,
          job_position: this.jobData?.position || '개발자',
          // 현재 분석 중인 공고 정보 (중복 제거용)
          current_job_url: this.urlInput || '',
          current_job_company: this.jobData?.company_name || '',
          current_job_title: this.jobData?.position || ''
        });

        this.recommendations = response.data.recommendations || [];

      } catch (error) {
        console.error('추천 공고 로드 실패:', error);
        // 실패해도 에러 메시지 표시하지 않음 (선택 기능)
        this.recommendations = [];
      } finally {
        this.isLoadingRecommendations = false;
      }
    },

    async analyzeCompany() {
      this.isAnalyzingCompany = true;
      this.errorMessage = '';

      try {
        const requestData = {
          type: this.companyAnalysisType,
          company_name: this.jobData?.company_name || '회사'
        };

        if (this.companyAnalysisType === 'url') {
          requestData.url = this.companyUrl;
        } else {
          requestData.text = this.companyText;
        }

        const response = await axios.post('/api/core/job-planner/company-analyze/', requestData);
        this.companyAnalysis = response.data;

      } catch (error) {
        console.error('기업분석 실패:', error);
        this.errorMessage = error.response?.data?.error || '기업분석 중 오류가 발생했습니다.';
      } finally {
        this.isAnalyzingCompany = false;
      }
    },

    parseUserSkills() {
      this.userSkills = this.userSkillsInput
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);

      // 새로 추가된 스킬에 기본 레벨 3 설정
      this.userSkills.forEach(skill => {
        if (!(skill in this.skillLevels)) {
          this.skillLevels[skill] = 3;
        }
      });
    },

    parseCertifications() {
      this.certifications = this.certificationsInput
        .split(',')
        .map(s => s.trim())
        .filter(s => s.length > 0);
    },

    getLevelLabel(level) {
      const labels = {
        1: '입문',
        2: '초급',
        3: '중급',
        4: '고급',
        5: '전문가'
      };
      return labels[level] || '중급';
    },

    getScoreClass(score) {
      if (score >= 0.8) return 'excellent';
      if (score >= 0.6) return 'good';
      if (score >= 0.4) return 'fair';
      return 'poor';
    },

    resetJobData() {
      this.urlInput = '';
      this.jobData = null;
      this.dataCompleteness = null;
      this.needsMoreInfo = false;
      this.missingFields = [];
      this.supplementMethod = 'image';
      this.supplementImages = [];
      this.supplementImagePreviews = [];
      this.supplementText = '';
      this.isSupplementParsing = false;
      this.analysisResult = null;
      this.agentQuestions = [];
      this.agentAnswers = {};
      this.finalReport = null;
      this.recommendations = [];
      this.errorMessage = '';
      this.currentStep = 'input';
    },

    resetAll() {
      this.currentStep = 'input';
      this.urlInput = '';
      this.jobData = null;
      this.dataCompleteness = null;
      this.needsMoreInfo = false;
      this.missingFields = [];
      this.supplementMethod = 'image';
      this.supplementImages = [];
      this.supplementImagePreviews = [];
      this.supplementText = '';
      this.isSupplementParsing = false;

      // 프로필 초기화
      this.name = '';
      this.currentRole = '';
      this.experienceYears = 0;
      this.userSkills = [];
      this.userSkillsInput = '';
      this.skillLevels = {};
      this.education = '';
      this.certifications = [];
      this.certificationsInput = '';
      this.careerGoals = '';
      this.availablePrepDays = null;

      // 기업분석 초기화
      this.companyAnalysisType = 'url';
      this.companyUrl = '';
      this.companyText = '';
      this.companyAnalysis = null;

      // 결과 초기화
      this.analysisResult = null;
      this.agentQuestions = [];
      this.agentAnswers = {};
      this.finalReport = null;
      this.recommendations = [];
      this.errorMessage = '';
    }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}

.job-planner-modal {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 24px 32px;
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.planner-badge {
  font-size: 12px;
  font-weight: 600;
  color: #60a5fa;
  letter-spacing: 1px;
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #f1f5f9;
}

.flow-tabs {
  display: flex;
  gap: 0;
  padding: 0 32px;
  background: #0f172a;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.flow-tab {
  flex: 1;
  padding: 16px 24px;
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
}

.flow-tab:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.flow-tab.active {
  color: #60a5fa;
}

.flow-tab.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: #60a5fa;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}

.step-title {
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 24px 0;
}

.input-method-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.method-tab {
  flex: 1;
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  color: #cbd5e1;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.method-tab.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: #60a5fa;
  color: #60a5fa;
}

.input-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-panel label {
  font-size: 14px;
  font-weight: 600;
  color: #cbd5e1;
}

.url-input,
.text-input {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
}

.url-input:focus,
.text-input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.text-input {
  resize: vertical;
  line-height: 1.6;
}

.input-hint {
  font-size: 13px;
  color: #64748b;
  margin: -8px 0 0 0;
}

.image-upload-area {
  min-height: 300px;
  background: rgba(15, 23, 42, 0.6);
  border: 2px dashed rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.image-upload-area:hover {
  border-color: #60a5fa;
  background: rgba(59, 130, 246, 0.05);
}

.upload-placeholder {
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-placeholder p {
  color: #cbd5e1;
  margin: 8px 0;
}

.upload-hint {
  font-size: 13px;
  color: #64748b;
}

.image-previews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  width: 100%;
  padding: 8px;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-number {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(59, 130, 246, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.image-preview {
  width: 100%;
  height: 100%;
  position: relative;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: rgba(239, 68, 68, 0.9);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove-image:hover {
  background: #ef4444;
  transform: scale(1.1);
}

.job-preview-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.job-preview-actions .btn-next {
  margin-top: 0;
  flex: 1;
}

.btn-reset-job {
  padding: 14px 24px;
  background: transparent;
  border: 2px solid #6b7280;
  border-radius: 10px;
  color: #9ca3af;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-reset-job:hover {
  border-color: #ef4444;
  color: #ef4444;
  transform: translateY(-2px);
}

.btn-parse,
.btn-analyze,
.btn-next,
.btn-restart {
  padding: 14px 32px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-parse:hover:not(:disabled),
.btn-analyze:hover:not(:disabled),
.btn-next:hover,
.btn-restart:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
}

.btn-parse:disabled,
.btn-analyze:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.job-preview {
  margin-top: 32px;
  padding: 24px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 12px;
}

.job-preview h4 {
  font-size: 16px;
  font-weight: 700;
  color: #22c55e;
  margin: 0 0 16px 0;
}

.preview-grid {
  display: grid;
  gap: 12px;
  margin-bottom: 20px;
}

.preview-item {
  display: flex;
  gap: 12px;
}

.preview-label {
  font-weight: 600;
  color: #94a3b8;
  min-width: 80px;
}

.preview-value {
  color: #f1f5f9;
}

/* 새로운 상세 정보 섹션 */
.preview-detail-section {
  margin-top: 20px;
  padding: 16px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 8px;
  border-left: 3px solid rgba(59, 130, 246, 0.5);
}

.preview-detail-title {
  font-size: 14px;
  font-weight: 600;
  color: #60a5fa;
  margin-bottom: 8px;
}

.preview-detail-content {
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.preview-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 12px;
}

.skill-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.skill-tag.required {
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.skill-tag.preferred {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #93c5fd;
}

/* 정보 충분도 인디케이터 */
.completeness-indicator {
  margin-top: 24px;
  padding: 16px;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.completeness-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.completeness-icon {
  font-size: 20px;
}

.completeness-title {
  font-size: 14px;
  font-weight: 600;
  color: #cbd5e1;
  flex: 1;
}

.completeness-score {
  font-size: 16px;
  font-weight: 700;
  color: #60a5fa;
}

.completeness-bar {
  width: 100%;
  height: 8px;
  background: rgba(30, 41, 59, 0.8);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.completeness-fill {
  height: 100%;
  transition: width 0.5s ease;
  border-radius: 4px;
}

.completeness-fill.good {
  background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
}

.completeness-fill.fair {
  background: linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%);
}

.completeness-fill.poor {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.completeness-warning {
  padding: 12px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid #f59e0b;
  border-radius: 6px;
}

.warning-text {
  font-size: 13px;
  color: #fbbf24;
  margin-bottom: 6px;
}

.warning-text strong {
  color: #fcd34d;
}

.supplement-input-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.supplement-title {
  font-size: 12px;
  color: #cbd5e1;
  margin-bottom: 10px;
}

.supplement-method-tabs {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.supp-tab {
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: transparent;
  color: #94a3b8;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.supp-tab.active {
  background: rgba(99, 102, 241, 0.25);
  border-color: #6366f1;
  color: #a5b4fc;
}

.supplement-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.supplement-upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  min-height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.2s;
}

.supplement-upload-area:hover {
  border-color: #6366f1;
}

.supplement-textarea {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 13px;
  padding: 10px;
  resize: vertical;
  box-sizing: border-box;
}

.supplement-textarea::placeholder {
  color: #64748b;
}

.btn-supplement-parse {
  padding: 8px 16px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  align-self: flex-start;
}

.btn-supplement-parse:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.completeness-success {
  padding: 12px;
  background: rgba(16, 185, 129, 0.1);
  border-left: 3px solid #10b981;
  border-radius: 6px;
  font-size: 13px;
  color: #34d399;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: #cbd5e1;
}

.form-group input {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.score-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.score-card {
  padding: 24px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  text-align: center;
}

.score-label {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 8px;
}

.score-value {
  font-size: 32px;
  font-weight: 700;
}

.score-value.excellent {
  color: #22c55e;
}

.score-value.good {
  color: #3b82f6;
}

.score-value.fair {
  color: #f59e0b;
}

.score-value.poor {
  color: #ef4444;
}

.skill-section {
  margin-bottom: 24px;
}

.section-subtitle {
  font-size: 16px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 12px 0;
}

.skill-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skill-item {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.skill-list.matched .skill-item {
  border-left: 3px solid #22c55e;
}

.skill-list.missing .skill-item {
  border-left: 3px solid #ef4444;
}

.skill-required {
  font-weight: 700;
  color: #f1f5f9;
  flex: 1;
}

.skill-arrow {
  color: #64748b;
}

.skill-user,
.skill-closest {
  color: #cbd5e1;
  flex: 1;
}

.skill-similarity {
  padding: 4px 12px;
  background: rgba(34, 197, 94, 0.2);
  border-radius: 6px;
  color: #22c55e;
  font-weight: 600;
  font-size: 12px;
}

.skill-similarity.weak {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.error-banner {
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: #fca5a5;
  text-align: center;
  margin-top: 16px;
}

/* Profile Form Styles */
.form-section {
  margin-bottom: 32px;
  padding: 24px;
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
}

.form-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 20px 0;
}

.form-row {
  margin-bottom: 20px;
}

.form-row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #cbd5e1;
}

.form-group input,
.form-group textarea {
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.form-group textarea {
  resize: vertical;
  line-height: 1.6;
}

.required {
  color: #ef4444;
}

.optional {
  color: #64748b;
  font-weight: 400;
  font-size: 12px;
}

/* Skill Levels */
.skill-levels-container {
  margin-top: 16px;
  padding: 16px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(96, 165, 250, 0.2);
  border-radius: 8px;
}

.skill-level-item {
  display: grid;
  grid-template-columns: 150px 1fr auto;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.skill-level-item:last-child {
  border-bottom: none;
}

.skill-name {
  font-weight: 600;
  color: #f1f5f9;
}

.skill-level-selector {
  display: flex;
  gap: 8px;
}

.level-btn {
  width: 40px;
  height: 40px;
  background: rgba(15, 23, 42, 0.6);
  border: 2px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  color: #cbd5e1;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.level-btn:hover {
  border-color: #60a5fa;
  background: rgba(59, 130, 246, 0.1);
}

.level-btn.active {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-color: #60a5fa;
  color: white;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.skill-level-label {
  font-size: 13px;
  color: #94a3b8;
  min-width: 60px;
  text-align: right;
}

.level-guide {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  font-size: 12px;
  color: #64748b;
  text-align: center;
}

/* Insights */
.insights-section {
  margin-bottom: 24px;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.insight-item {
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.insight-item.positive {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.insight-item.warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
}

.insight-item.neutral {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.insight-icon {
  font-size: 16px;
}

.insight-title {
  font-weight: 700;
  color: #f1f5f9;
  font-size: 14px;
}

.insight-message {
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.6;
  margin-left: 24px;
}

/* Company Analysis Styles */
.company-analysis-section {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.section-hint {
  font-size: 13px;
  color: #94a3b8;
  margin: -8px 0 16px 0;
}

.company-input-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.company-tab {
  flex: 1;
  padding: 10px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 6px;
  color: #cbd5e1;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.company-tab.active {
  background: rgba(139, 92, 246, 0.2);
  border-color: #a78bfa;
  color: #a78bfa;
}

.company-input-panel {
  margin-bottom: 16px;
}

.company-input,
.company-textarea {
  width: 100%;
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.2s;
}

.company-input:focus,
.company-textarea:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.company-textarea {
  resize: vertical;
  line-height: 1.6;
}

.btn-company-analyze {
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.btn-company-analyze:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
}

.btn-company-analyze:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.company-analysis-preview {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.preview-badge {
  font-size: 14px;
  font-weight: 600;
  color: #a78bfa;
}

.preview-score {
  font-size: 14px;
  font-weight: 700;
  color: #f1f5f9;
}

.company-analysis-results {
  margin-top: 32px;
  padding-top: 32px;
  border-top: 2px solid rgba(139, 92, 246, 0.3);
}

.analysis-title {
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 24px 0;
}

.company-score-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.company-score-card {
  padding: 16px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
}

.company-score-card .score-label {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.score-bar {
  height: 8px;
  background: rgba(100, 116, 139, 0.3);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
  transition: width 0.6s ease;
}

.score-text {
  font-size: 16px;
  font-weight: 700;
  color: #a78bfa;
}

.analysis-section {
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
}

.analysis-content {
  color: #cbd5e1;
  line-height: 1.7;
}

.analysis-content p {
  margin: 0 0 12px 0;
}

.info-grid,
.growth-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.info-item,
.growth-item,
.welfare-item {
  margin-bottom: 8px;
}

.info-label,
.growth-label {
  font-weight: 600;
  color: #94a3b8;
  margin-right: 8px;
}

.info-value,
.growth-value {
  color: #f1f5f9;
}

.vision-text {
  padding: 12px;
  background: rgba(139, 92, 246, 0.1);
  border-left: 3px solid #a78bfa;
  border-radius: 6px;
  margin-top: 12px;
}

.tech-tags {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.tag-label {
  font-weight: 600;
  color: #94a3b8;
}

.tech-tag {
  padding: 6px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(96, 165, 250, 0.3);
  border-radius: 6px;
  color: #60a5fa;
  font-size: 13px;
  font-weight: 600;
}

.tech-blog-info {
  padding: 10px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 6px;
  font-size: 13px;
  color: #93c5fd;
}

.growth-badge {
  padding: 4px 12px;
  background: rgba(100, 116, 139, 0.3);
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  color: #cbd5e1;
}

.growth-badge.상 {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.growth-badge.중 {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.growth-badge.하 {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.benefits-list {
  margin: 8px 0;
  padding-left: 24px;
  color: #cbd5e1;
}

.benefits-list li {
  margin: 4px 0;
}

.recommendation-section {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.3);
}

.recommendation-content {
  font-size: 15px;
  line-height: 1.8;
  color: #f1f5f9;
  font-weight: 500;
}

/* Agent Questions Step */
.agent-step {
  padding: 0;
}

.step-description {
  font-size: 14px;
  color: #94a3b8;
  margin: -16px 0 24px 0;
  line-height: 1.6;
}

/* 질문 로딩 중 */
.loading-questions {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 15px;
  color: #94a3b8;
  font-weight: 500;
}

.agent-questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 32px;
}

.agent-question-item {
  padding: 20px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  border-left: 4px solid #60a5fa;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.question-number {
  padding: 6px 12px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 6px;
  color: white;
  font-weight: 700;
  font-size: 13px;
}

.question-skill {
  padding: 6px 12px;
  background: rgba(96, 165, 250, 0.2);
  border: 1px solid rgba(96, 165, 250, 0.3);
  border-radius: 6px;
  color: #60a5fa;
  font-weight: 600;
  font-size: 13px;
}

.question-text {
  font-size: 15px;
  color: #f1f5f9;
  margin-bottom: 12px;
  line-height: 1.6;
  font-weight: 500;
}

.answer-input {
  width: 100%;
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  color: #f1f5f9;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
  transition: all 0.2s;
}

.answer-input:focus {
  outline: none;
  border-color: #60a5fa;
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
}

.agent-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}

.btn-skip {
  padding: 14px 32px;
  background: rgba(100, 116, 139, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  color: #cbd5e1;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-skip:hover {
  background: rgba(100, 116, 139, 0.5);
  border-color: #64748b;
}

.btn-generate-report {
  padding: 14px 32px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.btn-generate-report:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.5);
}

.btn-generate-report:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Final Report Styles */
.final-report-section {
  margin-top: 48px;
  padding-top: 48px;
  border-top: 3px solid rgba(16, 185, 129, 0.3);
}

.report-title {
  font-size: 24px;
  font-weight: 700;
  color: #10b981;
  margin: 0 0 32px 0;
  text-align: center;
}

/* SWOT */
.swot-section {
  margin-bottom: 40px;
}

.swot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.swot-card {
  padding: 20px;
  border-radius: 12px;
  border: 2px solid;
}

.swot-card.strengths {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.swot-card.weaknesses {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.swot-card.opportunities {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

.swot-card.threats {
  background: rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
}

.swot-header {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}

.swot-card.strengths .swot-header {
  color: #22c55e;
}

.swot-card.weaknesses .swot-header {
  color: #ef4444;
}

.swot-card.opportunities .swot-header {
  color: #3b82f6;
}

.swot-card.threats .swot-header {
  color: #f59e0b;
}

.swot-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
}

.swot-list li {
  margin: 8px 0;
  line-height: 1.6;
}

/* Interview Questions */
.interview-section {
  margin-bottom: 40px;
}

.interview-questions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.interview-question-card {
  padding: 20px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  display: flex;
  gap: 16px;
}

.question-number-badge {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 12px;
  color: white;
  font-weight: 700;
  font-size: 16px;
}

.question-content {
  flex: 1;
}

.question-title {
  font-size: 16px;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 12px;
}

.answer-guide {
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.7;
  margin-bottom: 8px;
  padding: 12px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 8px;
}

.tips {
  font-size: 13px;
  color: #a78bfa;
  line-height: 1.6;
  padding: 8px 12px;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 6px;
}

/* Experience Packaging */
.packaging-section {
  margin-bottom: 40px;
}

.packaging-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.packaging-card {
  padding: 20px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
}

.packaging-title {
  font-size: 15px;
  font-weight: 700;
  color: #60a5fa;
  margin-bottom: 12px;
}

.packaging-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
}

.packaging-list li {
  margin: 8px 0;
  line-height: 1.6;
  font-size: 14px;
}

/* Execution Strategy */
.execution-section {
  margin-bottom: 40px;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-item {
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid;
  display: flex;
  gap: 16px;
}

.timeline-item.immediate {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.timeline-item.short-term {
  background: rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
}

.timeline-item.mid-term {
  background: rgba(59, 130, 246, 0.1);
  border-color: #3b82f6;
}

.timeline-item.application {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
}

.timeline-badge {
  flex-shrink: 0;
  padding: 8px 16px;
  border-radius: 8px;
  color: white;
  font-weight: 700;
  font-size: 14px;
  height: fit-content;
}

.timeline-item.immediate .timeline-badge {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.timeline-item.short-term .timeline-badge {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.timeline-item.mid-term .timeline-badge {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.timeline-item.application .timeline-badge {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.timeline-content {
  flex: 1;
}

.timeline-list {
  margin: 0;
  padding-left: 20px;
  color: #cbd5e1;
}

.timeline-list li {
  margin: 8px 0;
  line-height: 1.6;
  font-size: 14px;
}

.application-timing {
  margin: 0;
  color: #f1f5f9;
  font-size: 15px;
  line-height: 1.7;
  font-weight: 500;
}

/* Final Message */
.final-message-section {
  margin-bottom: 32px;
}

.final-message {
  padding: 24px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.1) 100%);
  border: 2px solid #10b981;
  border-radius: 16px;
  color: #f1f5f9;
  font-size: 16px;
  line-height: 1.8;
  text-align: center;
  font-weight: 500;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Recommendations Section */
.recommendations-section {
  margin: 32px 0;
  padding: 24px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.05) 100%);
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 16px;
}

.recommendations-title {
  font-size: 24px;
  font-weight: 700;
  color: #60a5fa;
  margin-bottom: 8px;
}

.recommendations-subtitle {
  color: #cbd5e1;
  font-size: 14px;
  margin-bottom: 20px;
}

.recommendations-list {
  display: grid;
  gap: 16px;
  max-height: 600px;
  overflow-y: auto;
  padding-right: 8px;
}

.recommendations-list::-webkit-scrollbar {
  width: 6px;
}

.recommendations-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.recommendations-list::-webkit-scrollbar-thumb {
  background: rgba(59, 130, 246, 0.5);
  border-radius: 10px;
}

.recommendation-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.15);
}

.rec-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
}

.rec-main-info {
  flex: 1;
}

.rec-title {
  font-size: 18px;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.rec-company {
  color: #94a3b8;
  font-size: 14px;
}

.rec-match {
  text-align: center;
  min-width: 80px;
}

.rec-match-rate {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.rec-match-rate.excellent {
  color: #10b981;
}

.rec-match-rate.good {
  color: #3b82f6;
}

.rec-match-rate.fair {
  color: #f59e0b;
}

.rec-match-rate.poor {
  color: #ef4444;
}

.rec-match-label {
  color: #94a3b8;
  font-size: 12px;
}

.rec-details {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.rec-info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.rec-label {
  color: #94a3b8;
  min-width: 80px;
}

.rec-value {
  color: #cbd5e1;
}

.rec-reason {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
  border-radius: 8px;
  margin-bottom: 12px;
}

.rec-reason-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.rec-reason-text {
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.6;
}

.rec-skills {
  margin-bottom: 16px;
}

.rec-skill-label {
  display: block;
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 8px;
  font-weight: 500;
}

.rec-skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.rec-skill-tag {
  padding: 4px 12px;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  color: #93c5fd;
  font-size: 12px;
  font-weight: 500;
}

.rec-skill-more {
  padding: 4px 12px;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  color: #cbd5e1;
  font-size: 12px;
}

.rec-link {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.rec-link:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  transform: translateX(4px);
}

.loading-recommendations {
  padding: 40px;
  text-align: center;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
