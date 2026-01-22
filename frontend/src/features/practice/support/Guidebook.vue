<template>
  <div class="guidebook-container h-full flex flex-col gap-8 p-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- 
      [작성일: 2026-01-23]
      [작성내용: Unit 1 가이드북 (게임 매뉴얼) 컴포넌트 구현]
    -->
    
    <!-- Hero Section -->
    <div class="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-indigo-900/40 to-slate-900/40 border border-indigo-500/20 p-10 group">
      <div class="absolute top-0 right-0 p-10 opacity-10 group-hover:opacity-20 transition-opacity">
        <BookOpen class="w-40 h-40 text-indigo-400" />
      </div>
      <div class="relative z-10">
        <h2 class="text-[10px] text-indigo-400 font-black tracking-[0.5em] uppercase mb-4 orbitron">Mission_Directives</h2>
        <h1 class="text-4xl font-black text-white mb-6 rajdhani italic uppercase leading-none">
          How_to_Train_Your_<span class="text-indigo-400">Logic</span>
        </h1>
        <p class="text-slate-400 text-lg max-w-2xl leading-relaxed rajdhani">
          뉴럴 링크를 통해 전송되는 알고리즘 조각을 재구성하고, 직접 코드를 주입하여 논리적 안정성을 확보하십시오. 
          아래는 당신의 성공적인 미션 수행을 위한 가이드입니다.
        </p>
      </div>
    </div>

    <!-- Guide Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Logic Puzzle -->
      <div class="guide-card p-8 bg-slate-900/30 border border-slate-800/50 rounded-[2rem] hover:border-cyan-500/30 transition-all">
        <div class="w-12 h-12 bg-cyan-500/10 rounded-2xl flex items-center justify-center mb-6 border border-cyan-500/20">
          <Puzzle class="w-6 h-6 text-cyan-400" />
        </div>
        <h3 class="text-xl font-black text-white mb-4 orbitron uppercase tracking-wider">01_Neural_Puzzle</h3>
        <p class="text-slate-400 leading-relaxed rajdhani">
          분해된 로직 블록을 올바른 순서로 배치하십시오. 들여쓰기(Indentation)가 정확해야 싱크율이 상승합니다.
        </p>
      </div>

      <!-- Code Editor -->
      <div class="guide-card p-8 bg-slate-900/30 border border-slate-800/50 rounded-[2rem] hover:border-indigo-500/30 transition-all">
        <div class="w-12 h-12 bg-indigo-500/10 rounded-2xl flex items-center justify-center mb-6 border border-indigo-500/20">
          <Zap class="w-6 h-6 text-indigo-400" />
        </div>
        <h3 class="text-xl font-black text-white mb-4 orbitron uppercase tracking-wider">02_Logic_Expert</h3>
        <p class="text-slate-400 leading-relaxed rajdhani">
          직접 파이썬 코드를 주입하십시오. <span class="text-indigo-400 font-bold">if, for, def</span> 등 주요 구문 사용 시 엔진이 즉각적으로 반응합니다.
        </p>
      </div>

      <!-- Sync Telemetry -->
      <div class="guide-card p-8 bg-slate-900/30 border border-slate-800/50 rounded-[2rem] hover:border-emerald-500/30 transition-all">
        <div class="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-6 border border-emerald-500/20">
          <Activity class="w-6 h-6 text-emerald-400" />
        </div>
        <h3 class="text-xl font-black text-white mb-4 orbitron uppercase tracking-wider">Sync_Telemetry</h3>
        <p class="text-slate-400 leading-relaxed rajdhani">
          작성 중인 코드의 논리적 충실도를 실시간으로 측정합니다. 100%에 가까워질수록 미션 성공 확률이 높아집니다.
        </p>
      </div>

      <!-- Impact Engine -->
      <div class="guide-card p-8 bg-slate-900/30 border border-slate-800/50 rounded-[2rem] hover:border-rose-500/30 transition-all">
        <div class="w-12 h-12 bg-rose-500/10 rounded-2xl flex items-center justify-center mb-6 border border-rose-500/20">
          <Flame class="w-6 h-6 text-rose-400" />
        </div>
        <h3 class="text-xl font-black text-white mb-4 orbitron uppercase tracking-wider">Impact_Engine</h3>
        <p class="text-slate-400 leading-relaxed rajdhani">
          강력한 코드를 주입하거나 제출할 때 화면이 진동합니다. 이는 당신의 논리가 가상 환경에 물리적인 영향을 주고 있음을 의미합니다.
        </p>
      </div>
    </div>

    <!-- Live Flow Tooltip -->
    <div class="bg-indigo-500/5 border border-indigo-500/20 p-8 rounded-[2.5rem] flex items-center gap-8">
      <div class="shrink-0 w-24 h-24 bg-indigo-500/10 rounded-[2rem] flex items-center justify-center border border-indigo-500/20">
        <Share2 class="w-10 h-10 text-indigo-400 animate-pulse" />
      </div>
      <div>
        <h4 class="text-lg font-black text-white mb-2 orbitron tracking-tighter uppercase">Logic_Flow_Live</h4>
        <p class="text-slate-500 rajdhani leading-snug">
          입력한 코드는 실시간으로 시각적 순서도(Flowchart)로 변환됩니다. 사이드바 하단의 디스플레이를 통해 로직의 분기와 흐름을 모니터링하십시오.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { BookOpen, Puzzle, Zap, Activity, Flame, Share2 } from 'lucide-vue-next';
</script>

<style scoped>
.guide-card:hover {
  transform: translateY(-5px);
  background: rgba(15, 23, 42, 0.4);
}
</style>
