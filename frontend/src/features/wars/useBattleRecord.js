// 전적 관리 유틸 — WarsModeSelect, ArchDrawQuiz, BugBubbleMonster 등에서 공유
const STORAGE_KEY = 'wars_battle_records'

export function loadBattleRecords() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch { return [] }
}

// result: 'win' | 'lose' | 'draw'
export function addBattleRecord(name, result) {
  if (!name || !['win', 'lose', 'draw'].includes(result)) return
  const records = loadBattleRecords()
  let player = records.find(r => r.name === name)
  if (!player) {
    player = { name, win: 0, lose: 0, draw: 0 }
    records.push(player)
  }
  player[result]++
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
}

export function clearBattleRecords() {
  localStorage.removeItem(STORAGE_KEY)
}
