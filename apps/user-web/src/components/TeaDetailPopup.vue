<script setup lang="ts">
import type { TeaItem } from '@/lib/api'

const props = defineProps<{
  show: boolean
  tea: TeaItem | null
  isHistoryView?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'like'): void
  (e: 'dislike'): void
  (e: 'feedback'): void
}>()

function categoryText(category: string | undefined) {
  const m: Record<string, string> = { pu_er: '普洱', white: '白茶', yancha: '岩茶', black: '红茶' }
  return (category && m[category]) || '其他'
}
</script>

<template>
  <van-popup
    :show="props.show"
    position="bottom"
    round
    :style="{ height: '78vh' }"
    @click-overlay="emit('close')"
  >
    <div class="h-full bg-paper px-6 pb-8 pt-6">
      <div class="flex items-start justify-between gap-4">
        <div>
          <div class="text-[18px] font-semibold text-slate-900">{{ props.tea?.name }}</div>
          <div class="mt-1 text-[13px] text-slate-600">{{ props.tea?.origin }} · {{ props.tea?.spec }}</div>
        </div>
        <button class="rounded-full bg-white px-3 py-2 text-[12px] text-slate-600 ring-1 ring-black/5" @click="emit('close')">
          关闭
        </button>
      </div>

      <div class="mt-4 overflow-hidden rounded-3xl bg-white shadow-tea ring-1 ring-black/5">
        <img
          v-if="props.tea"
          class="h-56 w-full object-cover"
          :src="props.tea.cover_url"
          :alt="props.tea.name"
          @error="(e) => (((e.target as HTMLImageElement).src = '/tea-mist.svg'))"
        />
        <div class="px-5 py-5">
          <div class="text-[13px] text-slate-700">
            <div class="flex flex-wrap gap-x-4 gap-y-2">
              <span class="text-slate-500">年份</span>
              <span class="font-semibold text-slate-900">{{ props.tea?.year }}</span>
              <span class="text-slate-500">分类</span>
              <span class="font-semibold text-slate-900">{{ categoryText(props.tea?.category) }}</span>
            </div>
          </div>

          <div class="mt-4 text-[13px] leading-relaxed text-slate-700" v-if="props.tea?.intro">
            {{ props.tea?.intro }}
          </div>

          <div class="mt-5 rounded-2xl bg-slate-50 px-4 py-3 text-[12px] text-slate-600">
            价格区间：
            <span v-if="props.tea?.price_min != null">¥{{ props.tea?.price_min }}</span>
            <span v-else>未标注</span>
            <span v-if="props.tea?.price_max != null">–¥{{ props.tea?.price_max }}</span>
          </div>
        </div>
      </div>

      <div v-if="!props.isHistoryView" class="mt-6 grid grid-cols-2 gap-3">
        <button
          class="rounded-2xl bg-white px-5 py-4 text-[13px] font-semibold text-slate-700 ring-1 ring-black/5 hover:bg-slate-50"
          :disabled="!props.tea"
          @click="emit('dislike')"
        >
          不喜欢
        </button>
        <button
          class="rounded-2xl bg-slate-900 px-5 py-4 text-[13px] font-semibold text-white hover:bg-slate-800"
          :disabled="!props.tea"
          @click="emit('like')"
        >
          喜欢
        </button>
      </div>

      <div v-if="!props.isHistoryView" class="mt-4 text-center text-[12px] text-slate-400">反馈会影响推荐，并在今天不再出现这张茶卡</div>
      <button class="mt-5 w-full text-center text-[12px] font-semibold text-slate-600 hover:text-slate-800" @click="emit('feedback')">
        信息有误 / 想法建议？点这里
      </button>
    </div>
  </van-popup>
</template>
