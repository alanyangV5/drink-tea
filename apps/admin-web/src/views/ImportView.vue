<script setup lang="ts">
import { computed, ref } from 'vue'
import { adminUploadExcelPreview, adminPost } from '@/lib/api'

type TeaBase = {
  name: string
  category: string
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

type ImportPreviewRow = { index: number; ok: boolean; errors: string[]; data: TeaBase | null }

type ImportPreviewOut = { columns: string[]; rows: ImportPreviewRow[]; total_rows: number }

const loading = ref(false)
const committing = ref(false)
const error = ref('')
const preview = ref<ImportPreviewOut | null>(null)

const okRows = computed(() => (preview.value?.rows || []).filter((r) => r.ok && r.data))
const badRows = computed(() => (preview.value?.rows || []).filter((r) => !r.ok))

function onPickFile(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  loading.value = true
  error.value = ''
  preview.value = null

  adminUploadExcelPreview(file)
    .then((res) => {
      preview.value = res
    })
    .catch(() => {
      error.value = '解析失败：请检查 Excel 模板列名是否正确，或后端是否已安装 pandas/openpyxl'
    })
    .finally(() => {
      loading.value = false
      ;(e.target as HTMLInputElement).value = ''
    })
}

function commit() {
  if (!preview.value) return
  const items = okRows.value.map((r) => r.data as TeaBase)
  if (!items.length) return

  committing.value = true
  error.value = ''

  adminPost<{ ok: boolean; inserted: number }>('/api/admin/import/commit', { items })
    .then((res) => {
      preview.value = null
      alert(`导入完成：成功写入 ${res.inserted} 条`) 
    })
    .catch(() => {
      error.value = '导入失败：请检查登录状态或后端错误日志'
    })
    .finally(() => {
      committing.value = false
    })
}

function downloadFailures() {
  if (!preview.value) return
  const rows = badRows.value
  if (!rows.length) return

  const header = ['row_index', 'errors'].join(',')
  const lines = rows.map((r) => [r.index, JSON.stringify(r.errors)].join(','))
  const csv = [header, ...lines].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'import-failures.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div>
    <div class="flex items-end justify-between">
      <div>
        <div class="text-[16px] font-semibold text-white">Excel 导入</div>
        <div class="mt-1 text-[12px] text-slate-300">上传 → 预览校验 → 确认导入</div>
      </div>
      <div class="flex items-center gap-2">
        <label class="rounded-2xl bg-white px-4 py-3 text-[13px] font-semibold text-slate-900 hover:bg-slate-50">
          选择 Excel
          <input class="hidden" type="file" accept=".xlsx,.xls" @change="onPickFile" />
        </label>
        <button
          class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
          :disabled="!preview || !okRows.length || committing"
          @click="commit"
        >
          {{ committing ? '导入中…' : '确认导入' }}
        </button>
        <button
          class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15 disabled:opacity-50"
          :disabled="!preview || !badRows.length"
          @click="downloadFailures"
        >
          导出失败明细
        </button>
      </div>
    </div>

    <div v-if="loading" class="mt-5 text-[12px] text-slate-300">解析中…</div>
    <div v-if="error" class="mt-5 text-[12px] text-rose-200">{{ error }}</div>

    <div v-if="preview" class="mt-6 grid gap-4">
      <div class="grid grid-cols-3 gap-3">
        <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
          <div class="text-[12px] text-slate-300">总行数</div>
          <div class="mt-1 text-[18px] font-semibold text-white">{{ preview.total_rows }}</div>
        </div>
        <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
          <div class="text-[12px] text-slate-300">可导入</div>
          <div class="mt-1 text-[18px] font-semibold text-emerald-200">{{ okRows.length }}</div>
        </div>
        <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
          <div class="text-[12px] text-slate-300">失败</div>
          <div class="mt-1 text-[18px] font-semibold text-rose-200">{{ badRows.length }}</div>
        </div>
      </div>

      <div class="overflow-hidden rounded-3xl bg-black/20 ring-1 ring-white/10">
        <table class="w-full text-left text-[12px]">
          <thead class="bg-white/5 text-slate-200">
            <tr>
              <th class="px-4 py-3">行</th>
              <th class="px-4 py-3">状态</th>
              <th class="px-4 py-3">名称</th>
              <th class="px-4 py-3">分类</th>
              <th class="px-4 py-3">年份</th>
              <th class="px-4 py-3">错误</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in preview.rows.slice(0, 50)" :key="r.index" class="border-t border-white/10">
              <td class="px-4 py-3 text-slate-200">{{ r.index }}</td>
              <td class="px-4 py-3">
                <span class="rounded-full px-3 py-1 text-[12px] ring-1" :class="r.ok ? 'bg-emerald-500/10 text-emerald-200 ring-emerald-400/20' : 'bg-rose-500/10 text-rose-200 ring-rose-400/20'">
                  {{ r.ok ? 'OK' : '失败' }}
                </span>
              </td>
              <td class="px-4 py-3 text-slate-100">{{ r.data?.name || '-' }}</td>
              <td class="px-4 py-3 text-slate-200">{{ r.data?.category || '-' }}</td>
              <td class="px-4 py-3 text-slate-200">{{ r.data?.year || '-' }}</td>
              <td class="px-4 py-3 text-rose-200">{{ r.errors.join('；') }}</td>
            </tr>
            <tr v-if="preview.rows.length > 50">
              <td colspan="6" class="px-4 py-4 text-slate-300">仅预览前 50 行。</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="rounded-3xl bg-black/20 px-5 py-4 text-[12px] text-slate-300 ring-1 ring-white/10">
        模板列名（必须匹配）：名称、分类、年份、产地、规格、主图URL；可选：价格下限、价格上限、简介。
      </div>
    </div>
  </div>
</template>
