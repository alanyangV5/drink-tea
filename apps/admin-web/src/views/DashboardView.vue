<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { adminGet } from '@/lib/api'

import VChart from 'vue-echarts'

import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

type Summary = { pv: number; likes: number; dislikes: number; like_rate: number | null }

type RankRow = {
  tea: { id: number; name: string; category: string; year: number; origin: string; spec: string; weight: number }
  pv: number
  likes: number
  dislikes: number
  like_rate: number | null
}

type TrendOut = { points: Array<{ date: string; pv: number; likes: number; dislikes: number }> }

const loading = ref(false)
const error = ref('')

const preset = ref<'7d' | '30d' | 'all'>('7d')

const summary = ref<Summary>({ pv: 0, likes: 0, dislikes: 0, like_rate: null })
const rank = ref<RankRow[]>([])
const trend = ref<TrendOut>({ points: [] })

function formatDate(d: Date) {
  const yyyy = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

const range = computed(() => {
  if (preset.value === 'all') return null
  const now = new Date()
  const to = formatDate(now)
  const fromDate = new Date(now)
  fromDate.setDate(now.getDate() - (preset.value === '7d' ? 6 : 29))
  const from = formatDate(fromDate)
  return { from, to }
})

const likeRateText = computed(() => {
  if (summary.value.like_rate == null) return '暂无数据'
  return `${Math.round(summary.value.like_rate * 100)}%`
})

const chartOption = computed(() => {
  const x = trend.value.points.map((p) => p.date)
  const pv = trend.value.points.map((p) => p.pv)
  const likes = trend.value.points.map((p) => p.likes)
  const dislikes = trend.value.points.map((p) => p.dislikes)

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#cbd5e1' } },
    grid: { left: 24, right: 24, top: 36, bottom: 24, containLabel: true },
    xAxis: { type: 'category', data: x, axisLabel: { color: '#94a3b8' }, axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } } },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } } },
    series: [
      { name: 'PV', type: 'line', smooth: true, data: pv },
      { name: '喜欢', type: 'line', smooth: true, data: likes },
      { name: '不喜欢', type: 'line', smooth: true, data: dislikes }
    ]
  }
})

function load() {
  loading.value = true
  error.value = ''

  const qs = range.value ? `?from=${range.value.from}&to=${range.value.to}` : ''
  const sortQs = range.value ? `?sort=like_rate&from=${range.value.from}&to=${range.value.to}` : '?sort=like_rate'

  const p1 = adminGet<Summary>(`/api/admin/dashboard/summary${qs}`)
  const p2 = adminGet<{ items: RankRow[] }>(`/api/admin/dashboard/rank${sortQs}`)
  const p3 = range.value ? adminGet<TrendOut>(`/api/admin/dashboard/trend?from=${range.value.from}&to=${range.value.to}`) : Promise.resolve({ points: [] })

  return Promise.all([p1, p2, p3])
    .then(([s, r, t]) => {
      summary.value = s
      rank.value = r.items
      trend.value = t
    })
    .catch(() => {
      error.value = '加载失败：请检查后端是否启动、登录是否过期'
    })
    .finally(() => {
      loading.value = false
    })
}

watch(
  () => preset.value,
  () => {
    load()
  }
)

onMounted(() => {
  load()
})
</script>

<template>
  <div>
    <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <div class="text-[16px] font-semibold text-white">数据看板</div>
        <div class="mt-1 text-[12px] text-slate-300">PV、反馈与喜好率</div>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10"
          :class="preset === '7d' ? 'bg-white text-slate-900' : 'bg-white/10 text-slate-100 hover:bg-white/15'"
          @click="preset = '7d'"
        >
          近7天
        </button>
        <button
          class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10"
          :class="preset === '30d' ? 'bg-white text-slate-900' : 'bg-white/10 text-slate-100 hover:bg-white/15'"
          @click="preset = '30d'"
        >
          近30天
        </button>
        <button
          class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10"
          :class="preset === 'all' ? 'bg-white text-slate-900' : 'bg-white/10 text-slate-100 hover:bg-white/15'"
          @click="preset = 'all'"
        >
          全部
        </button>
        <button class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="load">
          刷新
        </button>
      </div>
    </div>

    <div v-if="loading" class="mt-5 text-[12px] text-slate-300">加载中…</div>
    <div v-if="error" class="mt-5 text-[12px] text-rose-200">{{ error }}</div>

    <div class="mt-6 grid gap-3 md:grid-cols-4">
      <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
        <div class="text-[12px] text-slate-300">PV</div>
        <div class="mt-1 text-[22px] font-semibold text-white">{{ summary.pv }}</div>
      </div>
      <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
        <div class="text-[12px] text-slate-300">喜欢</div>
        <div class="mt-1 text-[22px] font-semibold text-emerald-200">{{ summary.likes }}</div>
      </div>
      <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
        <div class="text-[12px] text-slate-300">不喜欢</div>
        <div class="mt-1 text-[22px] font-semibold text-rose-200">{{ summary.dislikes }}</div>
      </div>
      <div class="rounded-3xl bg-white/5 px-5 py-4 ring-1 ring-white/10">
        <div class="text-[12px] text-slate-300">喜好率</div>
        <div class="mt-1 text-[22px] font-semibold text-slate-100">{{ likeRateText }}</div>
      </div>
    </div>

    <div v-if="trend.points.length" class="mt-6 overflow-hidden rounded-3xl bg-black/20 p-4 ring-1 ring-white/10">
      <VChart :option="chartOption" autoresize class="h-[280px] w-full" />
    </div>

    <div class="mt-6 overflow-hidden rounded-3xl bg-black/20 ring-1 ring-white/10">
      <div class="px-5 py-4 text-[13px] font-semibold text-slate-100">Top 茶叶（按喜好率）</div>
      <table class="w-full text-left text-[12px]">
        <thead class="bg-white/5 text-slate-200">
          <tr>
            <th class="px-4 py-3">名称</th>
            <th class="px-4 py-3">PV</th>
            <th class="px-4 py-3">喜欢</th>
            <th class="px-4 py-3">不喜欢</th>
            <th class="px-4 py-3">喜好率</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in rank.slice(0, 12)" :key="r.tea.id" class="border-t border-white/10 text-slate-100">
            <td class="px-4 py-3">
              <div class="font-semibold">{{ r.tea.name }}</div>
              <div class="mt-1 text-slate-300">{{ r.tea.category }} · {{ r.tea.year }}</div>
            </td>
            <td class="px-4 py-3 text-slate-200">{{ r.pv }}</td>
            <td class="px-4 py-3 text-emerald-200">{{ r.likes }}</td>
            <td class="px-4 py-3 text-rose-200">{{ r.dislikes }}</td>
            <td class="px-4 py-3 text-slate-200">{{ r.like_rate == null ? '暂无' : Math.round(r.like_rate * 100) + '%' }}</td>
          </tr>
          <tr v-if="!loading && rank.length === 0">
            <td colspan="5" class="px-4 py-6 text-slate-300">暂无排行数据。先在用户端产生一些浏览与反馈。</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
