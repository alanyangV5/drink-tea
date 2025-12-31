function uuid() {
  // 足够用于匿名标识（非安全用途）
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export function getAnonUserId() {
  const key = 'drinktea:anonUserId'
  const existing = localStorage.getItem(key)
  if (existing) return existing
  const id = uuid()
  localStorage.setItem(key, id)
  return id
}

export function getTodayKey() {
  const d = new Date()
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

export function getDailyFeedbackMap() {
  const key = `drinktea:dailyFeedback:${getTodayKey()}`
  const raw = localStorage.getItem(key)
  if (!raw) return { key, map: {} as Record<string, 'like' | 'dislike'> }
  return { key, map: JSON.parse(raw) as Record<string, 'like' | 'dislike'> }
}

export function setDailyFeedback(teaId: number, action: 'like' | 'dislike') {
  const { key, map } = getDailyFeedbackMap()
  map[String(teaId)] = action
  localStorage.setItem(key, JSON.stringify(map))
}

export function getAllHistoricalFeedback() {
  const feedbackMap: Record<number, 'like' | 'dislike'> = {}
  // 遍历最近30天的反馈记录
  for (let i = 0; i < 30; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const yyyy = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const key = `drinktea:dailyFeedback:${yyyy}-${mm}-${dd}`
    const raw = localStorage.getItem(key)
    if (raw) {
      const map = JSON.parse(raw) as Record<string, 'like' | 'dislike'>
      Object.entries(map).forEach(([teaId, action]) => {
        feedbackMap[Number(teaId)] = action
      })
    }
  }
  return feedbackMap
}
