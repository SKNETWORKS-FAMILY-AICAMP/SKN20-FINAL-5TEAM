import axios from 'axios'

/**
 * [수정일: 2026-03-03] DB에서 전적 데이터를 가져오도록 변경
 * @param {string} nickname 현재 로그인한 유저의 닉네임
 * @returns {Promise<Array>} 전적 리포트 리스트 (UI 호환을 위해 배열 반환)
 */
export async function loadBattleRecords(nickname) {
  try {
    const response = await axios.get('/api/core/wars/record/')
    const data = response.data
    // WarsModeSelect.vue 의 기존 v-for 로직과 호환되도록 배열 형태로 반환
    return [{
      name: nickname || 'Me',
      win: data.win,
      draw: data.draw,
      lose: data.lose,
      total: data.total
    }]
  } catch (error) {
    console.error('Failed to load battle records from server:', error)
    return []
  }
}

// [수정일: 2026-03-03] 전적 저장은 이제 백엔드 소켓 서버에서 자동으로 수행됩니다.
// 클라이언트 측의 수동 저장은 더 이상 필요하지 않으므로 비활성화합니다.
export function addBattleRecord(name, result) {
  console.log(`[BattleRecord] Result '${result}' for '${name}' will be saved by the server.`)
}

export function clearBattleRecords() {
  console.warn('[BattleRecord] Persistence is now handled by DB. Local clear is disabled.')
}
