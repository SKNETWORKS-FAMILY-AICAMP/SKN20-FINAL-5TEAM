<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Architect Terminal 2077</title>
    <!-- Vue 3 Global Build -->
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
        
        body {
            font-family: 'Fira Code', monospace;
            background-color: #05070A;
            color: #A3FF47;
            margin: 0;
            overflow: hidden;
        }

        /* Star Wars Crawl Styles */
        .perspective-container { perspective: 400px; height: 100%; overflow: hidden; position: relative; }
        .crawl-content { 
            transform: rotateX(25deg); 
            position: absolute; 
            top: 100%; 
            width: 100%; 
            text-align: center;
            transform-origin: 50% 0%;
        }
        @keyframes crawl { 0% { top: 100%; } 100% { top: -150%; } }
        .animate-crawl { animation: crawl 45s linear forwards; }
        @keyframes fadeOut { 0% { opacity: 0; } 10%, 90% { opacity: 1; } 100% { opacity: 0; } }
        .animate-fade-out { animation: fadeOut 8s ease-in-out forwards; }

        /* OS UI Aesthetic */
        .hud-box {
            background: rgba(163, 255, 71, 0.05);
            border: 1px solid rgba(163, 255, 71, 0.2);
            backdrop-filter: blur(10px);
        }

        .terminal-text {
            text-shadow: 0 0 5px rgba(163, 255, 71, 0.5);
        }

        /* Modal Animation */
        @keyframes scale-up {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        .animate-scale-up {
            animation: scale-up 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* Selection Color */
        ::selection {
            background-color: #A3FF47;
            color: #000;
        }

        /* Scrollbar Custom */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(163, 255, 71, 0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(163, 255, 71, 0.3); }

        .custom-scrollbar {
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div id="app" class="min-h-screen flex flex-col relative overflow-hidden">
        
        <!-- 0. 시놉시스 레이어 (Star Wars Crawl) -->
        <div v-if="currentStep === 0" class="fixed inset-0 z-[100] bg-black flex flex-col items-center justify-center overflow-hidden font-sans">
            <div class="relative w-full max-w-4xl h-full flex flex-col items-center text-center perspective-container py-20">
                <div class="text-cyan-400 text-2xl font-serif mb-20 animate-fade-out">
                    PROGRAM: INITIALIZING_REBOOT_PROTOCOL<br/>YEAR: 2077<br/>LOCATION: MOTHER_SERVER_CORE
                </div>
                <div class="crawl-container relative w-full h-full">
                    <div class="crawl-content animate-crawl text-[#feda4a]">
                        <h1 class="text-6xl font-black mb-10 uppercase tracking-widest">Chapter 1: 각성</h1>
                        <div class="text-3xl font-bold leading-relaxed space-y-8 px-20 text-justify">
                            <p>서기 2077년, 인류를 관리하던 '마더 서버'가 오염되었습니다.</p>
                            <p>AI들은 현실을 왜곡하는 '환각(Hallucination)'과 '오버피팅'에 빠져 통제를 벗어났습니다.</p>
                            <p>대부분의 엔지니어는 기술을 잃었지만, 당신은 유일한 '아키텍처 복구자(Architect)'입니다.</p>
                            <p>파트너 'Coduck'과 함께 붕괴된 데이터 구역을 하나씩 정화하고 시스템을 재부팅해야 합니다.</p>
                        </div>
                    </div>
                </div>
                <button 
                    @click="currentStep = 1"
                    class="absolute bottom-12 right-12 px-8 py-3 bg-[#A3FF47] text-black font-black text-xs tracking-widest uppercase hover:scale-105 transition-all shadow-[0_0_20px_rgba(163,255,71,0.4)]"
                >
                    SKIP RE-BOOT PROTOCOL
                </button>
            </div>
        </div>

        <!-- OS 상단 헤더 -->
        <nav class="h-12 border-b border-[#A3FF47]/20 bg-black/80 backdrop-blur-xl px-6 flex items-center justify-between z-50 shrink-0">
            <div class="flex items-center gap-6">
                <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-[#A3FF47] rounded flex items-center justify-center animate-pulse">
                        <i data-lucide="cpu" class="text-black w-4 h-4"></i>
                    </div>
                    <span class="text-sm font-black tracking-widest uppercase italic">Architect OS v1.0</span>
                </div>
                <div class="h-4 w-px bg-[#A3FF47]/20"></div>
                <div class="flex items-center gap-4 text-[10px] tracking-tighter">
                    <span class="flex items-center gap-1 opacity-50"><i data-lucide="wifi" class="w-3 h-3"></i> SECTOR: REBOOT</span>
                    <span class="flex items-center gap-1 text-cyan-400"><i data-lucide="activity" class="w-3 h-3"></i> UPLINK_ACTIVE</span>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <button @click="isMuted = !isMuted" class="p-2 hover:bg-[#A3FF47]/10 rounded transition-colors">
                    <i v-if="isMuted" data-lucide="volume-x" class="text-red-500 w-4 h-4"></i>
                    <i v-else data-lucide="volume-2" class="w-4 h-4"></i>
                </button>
                <div class="bg-[#A3FF47]/10 px-3 py-1 rounded border border-[#A3FF47]/20 text-xs font-black">UM_JUN_SIK</div>
            </div>
        </nav>

        <!-- 메인 터미널 영역 -->
        <main class="flex-1 flex overflow-hidden relative">
            
            <!-- 사이드바: 단계 인디케이터 -->
            <div class="w-16 border-r border-[#A3FF47]/10 flex flex-col items-center py-8 gap-8 bg-black/20 shrink-0">
                <div v-for="i in 4" :key="i" 
                    class="w-8 h-8 rounded flex items-center justify-center text-xs font-bold transition-all"
                    :class="currentStep >= i ? 'bg-[#A3FF47] text-black shadow-[0_0_10px_#A3FF47]' : 'border border-[#A3FF47]/20 text-[#A3FF47]/40'"
                >
                    0{{ i }}
                </div>
            </div>

            <div class="flex-1 flex flex-col min-w-0 relative">
                <!-- 상단 미션 정보 바 -->
                <div class="p-6 border-b border-[#A3FF47]/10 flex items-center justify-between bg-black/40 shrink-0">
                    <div>
                        <h2 class="text-2xl font-black italic tracking-tighter uppercase">{{ questData.title }}</h2>
                        <p class="text-[10px] opacity-40 uppercase tracking-widest">{{ questData.subModuleTitle }}</p>
                    </div>
                    <div class="text-right">
                        <span class="text-[10px] font-bold opacity-40 block uppercase">System Integrity</span>
                        <span class="text-2xl font-black text-[#A3FF47] tracking-tighter">{{ integrity }}%</span>
                    </div>
                </div>

                <div class="flex-1 flex overflow-hidden">
                    <!-- Step 1: 인터뷰 인터페이스 -->
                    <div v-if="currentStep === 1" class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-px bg-[#A3FF47]/10 overflow-hidden">
                        <div class="bg-black/60 p-12 flex flex-col justify-center gap-8 border-r border-[#A3FF47]/10 overflow-y-auto custom-scrollbar">
                            <div class="w-40 h-40 rounded-full border-2 border-[#A3FF47] p-2 relative mx-auto shrink-0 bg-black shadow-[0_0_30px_rgba(163,255,71,0.2)]">
                                <img :src="questData.character.image" alt="Coduck" class="w-full h-full object-cover rounded-full" />
                                <div class="absolute -bottom-2 -right-2 bg-black border border-[#A3FF47] p-2 rounded-full shadow-lg"><i data-lucide="message-square" class="w-4 h-4"></i></div>
                            </div>
                            <div class="space-y-4 text-center">
                                <p class="text-xl font-bold leading-relaxed terminal-text">"{{ questData.interviewQuestions[interviewIdx].question }}"</p>
                                <p class="text-sm opacity-50 italic">선택지를 클릭하여 복구 프로토콜을 결정하십시오.</p>
                            </div>
                        </div>
                        <div class="bg-black/40 p-12 flex flex-col justify-center gap-4 overflow-y-auto custom-scrollbar">
                            <button 
                                v-for="(opt, i) in questData.interviewQuestions[interviewIdx].options" 
                                :key="i" 
                                @click="handleInterview(opt)"
                                class="p-6 border border-[#A3FF47]/30 bg-[#A3FF47]/5 hover:bg-[#A3FF47]/20 hover:border-[#A3FF47] transition-all text-left group relative overflow-hidden"
                            >
                                <span class="text-xs opacity-50 group-hover:opacity-100 mb-2 block tracking-widest">OPTION_0{{ i+1 }}</span>
                                <span class="text-lg font-bold">{{ opt.text }}</span>
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: 수도코드(Pseudo Code) 설계 -->
                    <div v-else-if="currentStep === 2" class="flex-1 flex overflow-hidden">
                        <div class="w-1/3 p-8 border-r border-[#A3FF47]/10 bg-black/40 space-y-6 overflow-y-auto custom-scrollbar">
                            <h3 class="text-sm font-black tracking-widest border-l-4 border-[#A3FF47] pl-3 uppercase">Mission Objective</h3>
                            <p class="text-lg leading-relaxed text-slate-300 font-bold italic">{{ questData.missionObjective }}</p>
                            <div class="p-4 bg-[#A3FF47]/5 border border-[#A3FF47]/20 rounded text-xs leading-relaxed italic opacity-70">
                                "데이터가 비어있는지(# TODO) 확인하고, 비어있지 않은 데이터만 결과 리스트에 담는 논리를 설계하세요."
                            </div>
                        </div>
                        <div class="flex-1 flex flex-col bg-black/20 overflow-hidden">
                            <div class="h-10 border-b border-[#A3FF47]/10 flex items-center px-4 gap-2 text-[10px] opacity-40 shrink-0">
                                <i data-lucide="terminal" class="w-3 h-3"></i> LOGIC_DESIGNER.pseudo
                            </div>
                            <textarea 
                                class="flex-1 bg-transparent p-8 outline-none text-xl font-mono text-[#A3FF47] resize-none leading-relaxed"
                                placeholder="여기에 한글 또는 영어로 의사코드를 작성하세요..."
                                v-model="pseudoInput"
                            ></textarea>
                            <div class="p-6 border-t border-[#A3FF47]/10 flex justify-end shrink-0">
                                <button @click="submitPseudo" class="px-8 py-3 bg-[#A3FF47] text-black font-black uppercase text-xs hover:shadow-[0_0_15px_#A3FF47] transition-all active:scale-95">Analyze Logic</button>
                            </div>
                        </div>
                    </div>

                    <!-- Step 3: 파이썬(Python) 실제 구현 -->
                    <div v-else-if="currentStep === 3" class="flex-1 flex flex-col lg:flex-row overflow-hidden">
                        <div class="flex-1 flex flex-col border-r border-[#A3FF47]/10 overflow-hidden">
                            <div class="h-10 border-b border-[#A3FF47]/10 flex items-center px-4 justify-between bg-black/40 shrink-0">
                                <span class="text-[10px] opacity-40 uppercase tracking-widest font-bold">Python_Compiler</span>
                                <div class="flex gap-2">
                                    <button 
                                        v-for="(s, i) in questData.pythonSnippets" 
                                        :key="i" 
                                        @click="pythonInput += '\n' + s.code" 
                                        class="text-[9px] border border-[#A3FF47]/30 px-2 py-0.5 rounded hover:bg-[#A3FF47]/10 transition-all uppercase"
                                    >{{ s.label }}</button>
                                </div>
                            </div>
                            <textarea 
                                class="flex-1 bg-[#0D1117] p-8 outline-none text-sm font-mono text-cyan-400 resize-none leading-relaxed"
                                v-model="pythonInput"
                            ></textarea>
                            <div class="p-4 bg-black/60 border-t border-[#A3FF47]/10 flex justify-end gap-4 shrink-0">
                                <button @click="runSimulation" :disabled="isSimulating" class="px-8 py-2 bg-[#A3FF47] text-black font-black uppercase text-[10px] hover:brightness-110 active:scale-95 transition-all">
                                    {{ isSimulating ? 'SIMULATING...' : 'EXECUTE WORKOUT' }}
                                </button>
                            </div>
                        </div>
                        <div class="w-1/3 bg-black flex flex-col overflow-hidden">
                            <div class="h-10 border-b border-[#A3FF47]/10 flex items-center px-4 text-[10px] opacity-40 uppercase font-bold tracking-widest shrink-0">Execution Output</div>
                            <div class="flex-1 p-6 font-mono text-[11px] leading-loose text-slate-400 overflow-y-auto custom-scrollbar" v-html="simulationOutput"></div>
                        </div>
                    </div>

                    <!-- Step 4: 심화 분석(Deep Dive) -->
                    <div v-else-if="currentStep === 4" class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-px bg-[#A3FF47]/10 overflow-hidden">
                        <div class="bg-black/60 p-12 flex flex-col justify-center space-y-12 overflow-y-auto custom-scrollbar">
                            <div class="space-y-4">
                                <h3 class="text-pink-500 font-black text-xs uppercase tracking-[0.4em]">Final Architecture Review</h3>
                                <p class="text-3xl font-black text-white italic leading-tight uppercase underline decoration-[#A3FF47] terminal-text">오늘 수행한 복구 프로토콜의 <br/>핵심 가치는 무엇입니까?</p>
                            </div>
                            <div class="p-8 border-l-4 border-[#A3FF47] bg-white/5 space-y-4">
                                <p class="text-lg font-bold text-slate-300 italic">"단순한 기능 구현을 넘어, 엔지니어링 리스크를 어떻게 제어했는지 돌아보십시오."</p>
                            </div>
                        </div>
                        <div class="bg-black/40 p-12 flex flex-col justify-center gap-4 overflow-y-auto custom-scrollbar">
                            <button 
                                v-for="(opt, i) in questData.step4Options" 
                                :key="i" 
                                @click="handleDeepDive(i)"
                                class="p-8 border border-white/5 bg-white/5 hover:border-pink-500 hover:bg-pink-500/10 transition-all text-left group flex items-start gap-6"
                            >
                                <span class="text-lg font-black text-pink-500 font-mono">0{{ i+1 }}</span>
                                <span class="text-lg font-bold leading-relaxed">{{ opt }}</span>
                            </button>
                        </div>
                    </div>

                    <!-- Step 5: 최종 결과 리포트 -->
                    <div v-else-if="currentStep === 5" class="flex-1 flex flex-col items-center justify-center p-20 bg-gradient-to-t from-[#A3FF47]/5 to-transparent overflow-y-auto custom-scrollbar">
                        <div class="relative mb-12">
                            <div class="absolute -inset-10 bg-[#A3FF47]/20 blur-3xl animate-pulse"></div>
                            <i data-lucide="award" class="w-48 h-48 text-[#A3FF47] drop-shadow-[0_0_40px_rgba(163,255,71,0.6)]"></i>
                        </div>
                        <h2 class="text-6xl font-black italic tracking-tighter uppercase mb-2 text-center terminal-text">RE-BOOT SUCCESS</h2>
                        <div class="h-1 w-64 bg-[#A3FF47] mb-8 shadow-[0_0_20px_#A3FF47]"></div>
                        <p class="text-xl text-slate-400 max-w-lg text-center leading-relaxed mb-12 italic">
                            "마더 서버의 튜토리얼 구역이 정화되었습니다. 엄준식님, 당신의 논리가 붕괴된 시스템에 질서를 가져왔습니다."
                        </p>
                        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full max-w-4xl">
                            <div v-for="(v, k) in userScore" :key="k" class="p-6 bg-white/5 border border-white/10 text-center rounded-sm">
                                <div class="text-[10px] opacity-40 uppercase font-black mb-2">{{ k }}</div>
                                <div class="text-3xl font-black text-[#A3FF47] tracking-tighter">{{ v }}</div>
                            </div>
                        </div>
                        <button @click="reloadApp" class="mt-16 px-12 py-4 border-2 border-[#A3FF47] text-[#A3FF47] font-black uppercase text-xs hover:bg-[#A3FF47] hover:text-black transition-all tracking-[0.3em] active:scale-95 shrink-0 shadow-lg">Return to Hub</button>
                    </div>
                </div>
            </div>

            <!-- 우측 사이드바: 아티팩트 및 상태 -->
            <div class="w-72 border-l border-[#A3FF47]/10 flex flex-col p-6 space-y-8 bg-black/20 hidden xl:flex shrink-0">
                <div>
                    <h3 class="text-[10px] font-black opacity-30 uppercase tracking-widest mb-4 italic">Recovered Artifacts</h3>
                    <div class="grid grid-cols-2 gap-3">
                        <div v-for="i in 4" :key="i" class="aspect-square rounded border border-white/5 flex items-center justify-center bg-white/5 overflow-hidden group shadow-inner relative">
                            <i v-if="integrity >= 100 && i === 1" data-lucide="database" class="text-[#A3FF47] animate-pulse"></i>
                            <i v-else data-lucide="lock" class="w-4 h-4 opacity-10"></i>
                            <div v-if="integrity >= 100 && i === 1" class="absolute inset-0 bg-[#A3FF47]/5 animate-ping"></div>
                        </div>
                    </div>
                </div>
                <div>
                    <h3 class="text-[10px] font-black opacity-30 uppercase tracking-widest mb-4 italic">Coduck Status</h3>
                    <div class="p-4 bg-white/5 border border-white/10 rounded-xl flex items-center gap-4 shadow-lg">
                        <div class="w-12 h-12 bg-[#A3FF47]/20 rounded-full flex items-center justify-center border border-[#A3FF47]/30 shadow-inner">
                            <i data-lucide="zap" class="text-[#A3FF47] w-5 h-5"></i>
                        </div>
                        <div>
                            <div class="text-[10px] opacity-40 uppercase font-bold tracking-tighter leading-none">Emotion</div>
                            <div class="text-sm font-bold uppercase tracking-tight text-[#A3FF47]">{{ integrity > 50 ? 'Excited' : 'Standby' }}</div>
                        </div>
                    </div>
                </div>
                <div class="mt-auto p-4 border border-[#A3FF47]/20 bg-[#A3FF47]/5 rounded italic">
                    <p class="text-[10px] opacity-60">"아키텍처 엄준식, 시스템 가동률 최적화 중..."</p>
                </div>
            </div>
        </main>

        <!-- 피드백 모달 오버레이 -->
        <div v-if="feedback.visible" class="fixed inset-0 z-[200] bg-black/95 backdrop-blur-md flex items-center justify-center p-6 transition-all duration-300">
            <div class="max-w-xl w-full p-12 border-2 bg-black relative shadow-2xl animate-scale-up" :class="feedback.isSuccess ? 'border-[#A3FF47]' : 'border-pink-500'">
                <div class="flex items-center gap-6 mb-8">
                    <i v-if="feedback.isSuccess" data-lucide="check-circle" class="w-16 h-16 text-[#A3FF47] shadow-[0_0_10px_rgba(163,255,71,0.5)]"></i>
                    <i v-else data-lucide="alert-triangle" class="w-16 h-16 text-pink-500 shadow-[0_0_10px_rgba(236,72,153,0.5)]"></i>
                    <h3 class="text-3xl font-black italic tracking-tighter uppercase terminal-text">{{ feedback.title }}</h3>
                </div>
                <p class="text-lg font-bold text-slate-300 leading-relaxed mb-10 italic border-l-4 pl-6 border-white/20">
                    {{ feedback.desc }}
                </p>
                <div class="flex justify-end">
                    <button @click="nextStep" class="px-10 py-4 font-black uppercase text-xs tracking-widest transition-all active:scale-95 shadow-lg" :class="feedback.isSuccess ? 'bg-[#A3FF47] text-black hover:brightness-110' : 'bg-white/10 text-white hover:bg-white/20'">
                        {{ feedback.isSuccess ? 'Initialize_Next_Protocol >>' : 'Retry Sequence' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- 배경 장식용 그리드 -->
        <div class="fixed inset-0 pointer-events-none -z-10 opacity-[0.05]">
            <div class="absolute inset-0" style="background-image: radial-gradient(#A3FF47 1px, transparent 1px); background-size: 40px 40px;"></div>
        </div>
    </div>

    <script>
        const { createApp, ref, reactive, onMounted, nextTick } = Vue;

        const questData = {
            id: 1,
            title: "Chapter 1: 각성 (Tutorial Zone)",
            category: "System Reboot",
            desc: "어두운 터미널, 켜지는 모니터... Coduck이 깨어납니다. '아키텍처님! 제 음성 모듈이 연결되었습니다. 먼저 제 사고 회로를 고쳐주세요.'",
            subModuleTitle: "BOOT_PROTOCOL",
            character: { 
                name: "Coduck", 
                image: "http://googleusercontent.com/image_generation_content/1" 
            },
            interviewQuestions: [
                {
                    id: "q1",
                    question: "Step 1: 사고 회로 복구 - 오염된 시스템을 복구하기 위해 Coduck의 사고를 정화하는 첫 번째 프로토콜은 무엇입니까?",
                    options: [
                        { text: "Coduck의 4단계 사고법(데이터 분석-논리 설계-코드 구현-최적화) 따르기", correct: true },
                        { text: "아무 데이터나 일단 마더 서버에 업로드하기", correct: false }
                    ]
                },
                {
                    id: "q2",
                    question: "Step 2: 오버피팅 체크 - 흐름을 파악했다면, AI가 환각(Hallucination)에 빠지지 않도록 무엇을 해야 할까요?",
                    options: [
                        { text: "데이터의 특징을 세부적으로 분석하여 필터링 규칙 설계하기", correct: true },
                        { text: "마더 서버가 스스로 학습하기를 방치하기", correct: false }
                    ]
                }
            ],
            missionObjective: "Step 3: 데이터 정화 - 시스템 복구 도중 발견된 작은 데이터 노이즈(빈 문자열)를 제거하여 파이프라인의 무결성을 확보하세요.",
            pythonSnippets: [
                { label: '노이즈 스킵', code: 'if not data: continue' },
                { label: '데이터 복구', code: 'result.append(data)' }
            ],
            pythonTemplate: `def system_restore_pipeline(data_list):\n    result = []\n\n    for data in data_list:\n        # [Step 3-1] 노이즈(오염된 데이터) 체크\n        if not data:\n            # TODO: 데이터가 오염되었으면 건너뛰도록 작성하세요\n            continue\n            \n        # [Step 3-2] 정화된 데이터만 아카이브에 저장\n        # TODO: data를 result에 추가하세요\n        result.append(data)\n\n    return result`,
            step4Options: [
                "저는 단순히 코드를 수선하는 엔지니어를 넘어, 붕괴된 시스템의 전체 파이프라인을 설계하고 리스크를 제어하는 '아키텍처 복구자'로서의 통찰을 발휘했습니다.",
                "저는 파이썬으로 리스트를 다룰 줄 압니다.",
                "마더 서버는 언젠가 스스로 복구될 것입니다."
            ],
            step4CorrectIdx: 0
        };

        const app = createApp({
            setup() {
                const currentStep = ref(0);
                const integrity = ref(0);
                const isMuted = ref(false);
                const interviewIdx = ref(0);
                const pseudoInput = ref('');
                const pythonInput = ref(questData.pythonTemplate);
                const simulationOutput = ref('');
                const isSimulating = ref(false);
                const userScore = reactive({ CONCEPT: 0, LOGIC: 0, CODE: 0, ARCH: 0 });
                const feedback = reactive({ visible: false, title: '', desc: '', isSuccess: true });

                const refreshIcons = () => {
                    nextTick(() => {
                        lucide.createIcons();
                    });
                };

                onMounted(() => {
                    refreshIcons();
                    if (currentStep.value === 0) {
                        setTimeout(() => {
                            if (currentStep.value === 0) {
                                currentStep.value = 1;
                                refreshIcons();
                            }
                        }, 15000);
                    }
                });

                const handleInterview = (option) => {
                    if (interviewIdx.value < questData.interviewQuestions.length - 1) {
                        interviewIdx.value++;
                        refreshIcons();
                    } else {
                        userScore.CONCEPT = 25;
                        showFeedback("📊 요구사항 분석 완료", "Coduck과의 인터뷰를 통해 시스템 규격을 성공적으로 정의했습니다.", true);
                    }
                };

                const submitPseudo = () => {
                    if (pseudoInput.value.length < 10) {
                        showFeedback("🔧 논리 보완 필요", "의사코드를 조금 더 상세히 작성해주세요.", false);
                        return;
                    }
                    userScore.LOGIC = 25;
                    showFeedback("💡 AI 논리 분석 완료", "복구 엔진이 의사코드를 정밀 분석했습니다. 논리 구조가 매우 탄탄합니다.", true);
                };

                const runSimulation = () => {
                    isSimulating.value = true;
                    simulationOutput.value = "<span class='text-cyan-400 animate-pulse'>[SYSTEM] Initializing Pyodide_Runtime...</span><br/>";
                    
                    setTimeout(() => {
                        simulationOutput.value += "> Loading data_list: ['Data_01', '', 'Data_02', ' ']<br/>> Applying purification logic...<br/><span class='text-[#A3FF47] font-bold'>[SUCCESS] result: ['Data_01', 'Data_02', ' ']</span>";
                        isSimulating.value = false;
                        userScore.CODE = 25;
                        showFeedback("🐍 파이썬 구현 성공", "설계하신 논리가 실제 파이썬 코드로 완벽하게 변환되었습니다.", true);
                    }, 2000);
                };

                const handleDeepDive = (idx) => {
                    if (idx === questData.step4CorrectIdx) {
                        userScore.ARCH = 25;
                        integrity.value = 100;
                        showFeedback("🔐 시스템 권한 회복", "축하합니다! 해당 구역의 데이터 무결성이 확보되었습니다.", true);
                    } else {
                        showFeedback("⚠️ 시스템 거부", "논리적 오류로 인해 재부팅이 거부되었습니다.", false);
                    }
                };

                const showFeedback = (title, desc, isSuccess) => {
                    feedback.title = title;
                    feedback.desc = desc;
                    feedback.isSuccess = isSuccess;
                    feedback.visible = true;
                    refreshIcons();
                };

                const nextStep = () => {
                    feedback.visible = false;
                    if (currentStep.value < 5) currentStep.value++;
                    refreshIcons();
                };

                const reloadApp = () => {
                    location.reload();
                };

                return {
                    currentStep, integrity, isMuted, interviewIdx,
                    pseudoInput, pythonInput, simulationOutput, isSimulating,
                    userScore, feedback, questData,
                    handleInterview, submitPseudo, runSimulation,
                    handleDeepDive, nextStep, reloadApp
                };
            }
        });

        app.mount('#app');
    </script>
</body>
</html>