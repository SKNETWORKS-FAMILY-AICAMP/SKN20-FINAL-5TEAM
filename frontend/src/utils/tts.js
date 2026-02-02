/**
 * [생성일: 2026-02-01]
 * [내용: Web Speech API를 활용한 Coduck 전용 TTS 유틸리티]
 */

class TTSManager {
    constructor() {
        this.synth = window.speechSynthesis;
        this.voice = null;
        this.isMuted = false;
        this.initVoice();
    }

    initVoice() {
        // 브라우저마다 목소리 로딩 시점이 다를 수 있음
        const loadVoices = () => {
            const voices = this.synth.getVoices();
            // 한국어 목소리 우선 찾기
            this.voice = voices.find(v => v.lang === 'ko-KR') || voices[0];
        };

        if (this.synth.onvoiceschanged !== undefined) {
            this.synth.onvoiceschanged = loadVoices;
        }
        loadVoices();
    }

    speak(text) {
        if (this.isMuted || !text) return;

        // 현재 재생 중인 음성 중지
        this.stop();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = this.voice;
        utterance.lang = 'ko-KR';
        utterance.pitch = 1.2; // 약간 높은 톤으로 오리(Coduck) 느낌 부여
        utterance.rate = 1.0;  // 표준 속도

        this.synth.speak(utterance);
    }

    stop() {
        if (this.synth.speaking) {
            this.synth.cancel();
        }
    }

    setMute(muted) {
        this.isMuted = muted;
        if (muted) this.stop();
    }

    toggleMute() {
        this.setMute(!this.isMuted);
        return this.isMuted;
    }
}

export const tts = new TTSManager();
