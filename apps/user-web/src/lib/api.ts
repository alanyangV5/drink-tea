export type TeaCategory = 'pu_er' | 'white' | 'yancha' | 'black'
export type FilterType = TeaCategory | 'liked' | 'disliked'

export interface TeaItem {
  id: number
  name: string
  category: TeaCategory
  year: number
  origin: string
  spec: string
  price_min: number | null
  price_max: number | null
  intro: string | null
  cover_url: string
  status: 'online' | 'offline'
  weight: number
}

export interface TeaListResponse {
  items: TeaItem[]
  page: number
  page_size: number
  total: number
}

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

function toQuery(params: Record<string, string | number | undefined>) {
  const sp = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined) return
    sp.set(k, String(v))
  })
  const qs = sp.toString()
  return qs ? `?${qs}` : ''
}

export function fetchTeas(params: {
  category?: TeaCategory
  page: number
  pageSize: number
  anonUserId?: string
  excludeIds?: number[]
  teaIds?: number[]
}) {
  const exclude = params.excludeIds?.length ? params.excludeIds.join(',') : undefined
  const teaIds = params.teaIds?.length ? params.teaIds.join(',') : undefined
  const url = `${API_BASE}/api/teas${toQuery({
    category: params.category,
    page: params.page,
    page_size: params.pageSize,
    anon_user_id: params.anonUserId,
    exclude_ids: exclude,
    tea_ids: teaIds
  })}`

  return fetch(url)
    .then((r) => (r.ok ? r.json() : Promise.reject(r)))
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<TeaListResponse>
}

export function postEvent(input: { anon_user_id: string; tea_id: number; type: 'impression' | 'detail_open' }) {
  const url = `${API_BASE}/api/events`
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  })
    .then((r) => (r.ok ? r.json() : Promise.reject(r)))
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    })
}

export function postFeedback(input: { anon_user_id: string; tea_id: number; action: 'like' | 'dislike' }) {
  const url = `${API_BASE}/api/feedback`
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  })
    .then((r) => (r.ok ? r.json() : Promise.reject(r)))
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    })
}

export function postMessageFeedback(input: {
  anon_user_id: string
  message: string
  contact?: string
  tea_id?: number
}) {
  const url = `${API_BASE}/api/feedback/message`
  return fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  })
    .then((r) => (r.ok ? r.json() : Promise.reject(r)))
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    })
}
