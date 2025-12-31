<script setup lang="ts">
import type { FilterType } from '@/lib/api'

const props = defineProps<{
  categories: Array<{ key: FilterType | undefined; label: string }>
  selected: FilterType | undefined
  online: boolean
}>()

const emit = defineEmits<{
  (e: 'select', key: FilterType | undefined): void
  (e: 'feedback'): void
}>()
</script>

<template>
  <div class="fixed left-0 right-0 top-0 z-50 bg-paper/90 backdrop-blur">
    <div class="mx-auto flex max-w-[980px] items-center justify-between px-5 py-4">
      <div class="flex items-center gap-3">
        <div
          class="h-9 w-9 animate-float rounded-2xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 ring-1 ring-emerald-900/10"
        />
        <div>
          <div class="text-[16px] font-semibold tracking-wide text-slate-900">来喝茶</div>
          <div class="text-[12px] text-slate-500">以茶会友，不亦乐乎</div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          class="rounded-full bg-white px-4 py-2 text-[12px] font-semibold text-slate-700 ring-1 ring-black/5 hover:bg-slate-50"
          @click="emit('feedback')"
        >
          反馈
        </button>
        <span
          v-if="!props.online"
          class="rounded-full bg-amber-50 px-3 py-1 text-[12px] text-amber-700 ring-1 ring-amber-200"
        >
          离线
        </span>
      </div>
    </div>

    <div class="mx-auto max-w-[980px] px-5 pb-3">
      <div class="flex gap-2 overflow-x-auto pb-1">
        <button
          v-for="c in props.categories"
          :key="String(c.key)"
          class="whitespace-nowrap rounded-full px-4 py-2 text-[13px] ring-1 transition"
          :class="
            props.selected === c.key
              ? 'bg-slate-900 text-white ring-slate-900'
              : 'bg-white text-slate-700 ring-black/5 hover:bg-slate-50'
          "
          @click="emit('select', c.key)"
        >
          {{ c.label }}
        </button>
      </div>
    </div>
  </div>
</template>
