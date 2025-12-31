<script setup lang="ts">
import { computed } from 'vue'
import type { TeaItem } from '@/lib/api'

const props = defineProps<{
  tea: TeaItem
  isTop: boolean
  online: boolean
}>()

const yearTag = computed(() => {
  const years = new Date().getFullYear() - props.tea.year
  if (years <= 3) return { label: '新茶', color: '#66BB6A' }
  if (years <= 10) return { label: '陈茶', color: '#FFA726' }
  return { label: '老茶', color: '#8B4513' }
})

const categoryText = computed(() => {
  const m: Record<string, string> = { pu_er: '普洱', white: '白茶', yancha: '岩茶', black: '红茶' }
  return m[props.tea.category] || '其他'
})

function priceText() {
  const min = props.tea.price_min
  const max = props.tea.price_max
  if (min == null && max == null) return '价格区间：未标注'
  if (min != null && max == null) return `价格区间：¥${min}+`
  if (min == null && max != null) return `价格区间：≤¥${max}`
  return `价格区间：¥${min}–¥${max}`
}
</script>

<template>
  <div class="relative w-full overflow-hidden rounded-[26px] bg-white shadow-tea ring-1 ring-black/5">
    <div class="absolute left-5 top-5 z-20 flex items-center gap-2">
      <span class="text-[12px] tracking-wide text-slate-500">#{{ categoryText }}</span>
    </div>

    <div
      class="absolute right-5 top-5 z-20 rounded-full px-3 py-1 text-[12px] font-semibold text-white"
      :style="{ backgroundColor: yearTag.color }"
    >
      {{ yearTag.label }} · {{ tea.year }}
    </div>

    <div class="relative">
      <img
        class="h-[70vh] w-full object-cover"
        :src="tea.cover_url"
        :alt="tea.name"
        @error="(e) => (((e.target as HTMLImageElement).src = '/tea-mist.svg'))"
      />
      <div class="pointer-events-none absolute inset-x-0 bottom-0 h-36 bg-gradient-to-t from-white to-transparent" />
    </div>

    <div class="px-6 pb-6 pt-5">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h2 class="text-[22px] font-semibold leading-tight text-slate-900">{{ tea.name }}</h2>
          <p class="mt-2 text-[13px] leading-relaxed text-slate-600">
            {{ tea.origin }} · {{ tea.spec }}
          </p>
        </div>
        <div class="mt-1 text-right text-[12px] text-slate-500">{{ priceText() }}</div>
      </div>

      <p v-if="tea.intro" class="mt-4 text-[13px] leading-relaxed text-slate-700">
        {{ tea.intro }}
      </p>

      <div v-if="!online" class="mt-5 rounded-xl bg-amber-50 px-4 py-3 text-[12px] text-amber-700">
        当前离线：优先展示最近缓存的茶卡片。
      </div>

      <div v-if="!isTop" class="mt-4 text-[12px] text-slate-400">向左或向右滑动进行选择</div>
    </div>
  </div>
</template>
