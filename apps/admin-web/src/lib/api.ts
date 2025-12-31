import { getToken } from './auth'

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(r: Response) {
  if (!r.ok) {
    let errorMsg = `HTTP ${r.status}`
    try {
      const data = await r.json()
      if (data.detail) {
        if (typeof data.detail === 'string') {
          errorMsg = data.detail
        } else if (data.detail.message) {
          errorMsg = data.detail.message
        }
      }
    } catch {
      // 如果无法解析为 JSON，使用默认错误信息
    }
    const error = new Error(errorMsg) as any
    error.status = r.status
    error.response = r
    throw error
  }
  return r.json()
}

export function adminLogin(input: { username: string; password: string }) {
  return fetch(`${API_BASE}/api/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input)
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<{ token: string }>
}

export function adminGet<T>(path: string) {
  return fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` }
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<T>
}

export function adminPost<T>(path: string, body: unknown) {
  return fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
    body: JSON.stringify(body)
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<T>
}

export function adminPut<T>(path: string, body: unknown) {
  return fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
    body: JSON.stringify(body)
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<T>
}

export function adminDelete(path: string) {
  return fetch(`${API_BASE}${path}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${getToken()}` }
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<{ ok: boolean }>
}

export function adminUpload(file: File) {
  const fd = new FormData()
  fd.append('file', file)

  return fetch(`${API_BASE}/api/admin/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: fd
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<{ url: string }>
}

export function adminUploadExcelPreview(file: File) {
  const fd = new FormData()
  fd.append('file', file)

  return fetch(`${API_BASE}/api/admin/import/excel`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: fd
  })
    .then(handleResponse)
    .catch((e) => {
      console.error(e)
      return Promise.reject(e)
    }) as Promise<{ columns: string[]; rows: Array<{ index: number; ok: boolean; errors: string[]; data: any }>; total_rows: number }>
}
