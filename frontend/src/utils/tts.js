/**
 * [수정일: 2026-02-23]
 * [내용: 큐 기반 순차 재생 + onQueueEmpty 콜백 지원]
 */

// 면접관 음성 설정 (변경 시 여기만 수정)
// alloy(중성) | nova(여성) | onyx(남성) | shimmer(부드러운 여성) | echo | fable
const DEFAULT_VOICE = 'nova'

// 재생 속도 (1.0 = 기본, 1.1~1.2 = 약간 빠르게, 0.9 = 약간 느리게)
const PLAYBACK_RATE = 1.1

class TTSManager {
    constructor() {
        this.isMuted = false;
        this._currentAudio = null;
        this._queue = [];         // 재생 대기열
        this._processing = false;
        this.onQueueEmpty = null; // 큐가 모두 비었을 때 호출되는 콜백
    }

    /**
     * 텍스트를 큐에 추가. 재생 중이면 순서대로 이어서 재생.
     * @param {string} text
     */
    speak(text) {
        if (this.isMuted || !text?.trim()) return;
        this._queue.push(text.trim());
        if (!this._processing) {
            this._processQueue();
        }
    }

    async _processQueue() {
        if (this._queue.length === 0) {
            this._processing = false;
            if (this.onQueueEmpty) {
                this.onQueueEmpty();
            }
            return;
        }

        this._processing = true;
        const text = this._queue[0];

        try {
            const response = await fetch('/api/core/tts/synthesize/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, voice: DEFAULT_VOICE }),
            });

            if (!response.ok) {
                console.error('[TTS] API 오류:', response.status, await response.text());
                this._queue.shift();
                this._processQueue();
                return;
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);

            this._currentAudio = new Audio(audioUrl);
            this._currentAudio.playbackRate = PLAYBACK_RATE;
            this._currentAudio.onended = () => {
                URL.revokeObjectURL(audioUrl);
                this._currentAudio = null;
                this._queue.shift();
                this._processQueue();
            };

            await this._currentAudio.play();

        } catch (e) {
            console.error('[TTS] 재생 오류:', e);
            this._queue.shift();
            this._processQueue();
        }
    }

    stop() {
        this._queue = [];
        this._processing = false;
        if (this._currentAudio) {
            this._currentAudio.pause();
            this._currentAudio = null;
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
