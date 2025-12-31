<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { showToast } from 'vant'
import 'vant/es/toast/style'

import FeedHeader from '@/components/FeedHeader.vue'
import TeaCard from '@/components/TeaCard.vue'
import TeaDetailPopup from '@/components/TeaDetailPopup.vue'
import FeedbackFormPopup from '@/components/FeedbackFormPopup.vue'

import type { FilterType, TeaItem } from '@/lib/api'
import { fetchTeas, postEvent, postFeedback, postMessageFeedback } from '@/lib/api'
import { getAnonUserId, getDailyFeedbackMap, setDailyFeedback, getAllHistoricalFeedback } from '@/lib/anon'

const categories = [
  { key: undefined as FilterType | undefined, label: '全部' },
  { key: 'pu_er' as const, label: '普洱' },
  { key: 'white' as const, label: '白茶' },
  { key: 'yancha' as const, label: '岩茶' },
  { key: 'black' as const, label: '红茶' },
  { key: 'liked' as const, label: '我喜欢的' },
  { key: 'disliked' as const, label: '我不喜欢的' }
]

const state = reactive({
  loading: false,
  error: '',
  page: 1,
  pageSize: 10,
  total: 0,
  category: undefined as FilterType | undefined,
  teas: [] as TeaItem[]
})

const online = ref(true)
const anonUserId = ref('')
const detailOpen = ref(false)
const detailTea = ref<TeaItem | null>(null)

const feedbackOpen = ref(false)
const feedbackTeaId = ref<number | undefined>(undefined)
const feedbackSubmitting = ref(false)

const topTea = computed(() => state.teas[0])
const restTeas = computed(() => state.teas.slice(1, 3))
const isHistoryView = computed(() => state.category === 'liked' || state.category === 'disliked')

const drag = reactive({ active: false, startX: 0, startY: 0, x: 0, y: 0, vx: 0, lastTs: 0, moved: false })

// 历史视图的拖拽状态
const historyDrag = reactive({ active: false, startX: 0, x: 0, direction: 0 as -1 | 0 | 1 })

const cardStyle = computed(() => {
  const x = drag.x
  const y = drag.y
  const rotate = Math.max(-12, Math.min(12, x / 24))
  const scale = drag.active ? 1.02 : 1
  return {
    transform: `translate3d(${x}px, ${y}px, 0) rotate(${rotate}deg) scale(${scale})`,
    transition: drag.active ? 'none' : 'transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1)'
  }
})

const historyCardStyle = computed(() => {
  return {
    transform: `translate3d(${historyDrag.x}px, 0, 0)`,
    transition: historyDrag.active ? 'none' : 'transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1)'
  }
})

const likeOpacity = computed(() => Math.max(0, Math.min(1, drag.x / 140)))
const dislikeOpacity = computed(() => Math.max(0, Math.min(1, -drag.x / 140)))

function resetDrag() {
  drag.active = false
  drag.x = 0
  drag.y = 0
  drag.vx = 0
}

function resetHistoryDrag() {
  historyDrag.active = false
  historyDrag.x = 0
  historyDrag.direction = 0
}

function onPointerDown(e: PointerEvent) {
  if (!topTea.value) return
  drag.active = true
  drag.startX = e.clientX
  drag.startY = e.clientY
  drag.lastTs = performance.now()
  drag.vx = 0
  drag.moved = false
}

function onPointerMove(e: PointerEvent) {
  if (!drag.active) return
  const dx = e.clientX - drag.startX
  const dy = e.clientY - drag.startY
  const now = performance.now()
  const dt = Math.max(1, now - drag.lastTs)
  drag.vx = (dx - drag.x) / dt
  drag.lastTs = now
  drag.x = dx
  drag.y = dy * 0.35
  if (!drag.moved && Math.hypot(dx, dy) > 8) drag.moved = true
}

function commit(action: 'like' | 'dislike') {
  const tea = topTea.value
  if (!tea) return
  setDailyFeedback(tea.id, action)
  postFeedback({ anon_user_id: anonUserId.value, tea_id: tea.id, action }).catch(() => {
    showToast({ message: '网络波动，已记录到本地', duration: 1200 })
  })
  showToast({ message: action === 'like' ? '已喜欢' : '不太合口味', duration: 800 })
  state.teas = state.teas.slice(1)
  resetDrag()
  if (state.teas.length < 5) loadMore()
}

function onPointerUp(_e?: PointerEvent) {
  if (!drag.active) return
  const tea = topTea.value
  if (!tea) return
  const threshold = Math.min(160, Math.max(120, window.innerWidth * 0.28))
  if (drag.x > threshold) {
    drag.active = false
    drag.x = window.innerWidth
    setTimeout(() => commit('like'), 60)
    return
  }
  if (drag.x < -threshold) {
    drag.active = false
    drag.x = -window.innerWidth
    setTimeout(() => commit('dislike'), 60)
    return
  }
  resetDrag()
  if (!drag.moved) openDetail(tea)
}

function onHistoryPointerDown(e: PointerEvent) {
  if (!topTea.value) return
  historyDrag.active = true
  historyDrag.startX = e.clientX
  historyDrag.x = 0
  historyDrag.direction = 0
}

function onHistoryPointerMove(e: PointerEvent) {
  if (!historyDrag.active) return
  const dx = e.clientX - historyDrag.startX
  historyDrag.x = dx
}

function onHistoryPointerUp(_e?: PointerEvent) {
  if (!historyDrag.active) return
  const threshold = Math.min(100, Math.max(80, window.innerWidth * 0.2))

  if (historyDrag.x > threshold) {
    // 向右滑动，查看下一张（移除当前卡片，显示下一张）
    historyDrag.active = false
    historyDrag.x = window.innerWidth
    setTimeout(() => {
      state.teas = state.teas.slice(1)
      resetHistoryDrag()
    }, 60)
    return
  }

  if (historyDrag.x < -threshold) {
    // 向左滑动，也移除当前卡片
    historyDrag.active = false
    historyDrag.x = -window.innerWidth
    setTimeout(() => {
      state.teas = state.teas.slice(1)
      resetHistoryDrag()
    }, 60)
    return
  }

  // 滑动距离不够，重置
  resetHistoryDrag()
  if (!historyDrag.direction) openDetail(topTea.value!)
}

function onKeydown(e: KeyboardEvent) {
  if (!topTea.value) return
  if (isHistoryView.value) {
    // 历史视图：方向键切换卡片
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      state.teas = state.teas.slice(1)
    }
    return
  }
  // 正常视图：方向键提交反馈
  if (e.key === 'ArrowRight') commit('like')
  if (e.key === 'ArrowLeft') commit('dislike')
}

function openDetail(tea: TeaItem) {
  detailTea.value = tea
  detailOpen.value = true
  postEvent({ anon_user_id: anonUserId.value, tea_id: tea.id, type: 'detail_open' }).catch(() => {})
}

function closeDetail() {
  detailOpen.value = false
  detailTea.value = null
}

function openFeedback(teaId?: number) {
  feedbackTeaId.value = teaId
  feedbackOpen.value = true
}

function closeFeedback() {
  feedbackOpen.value = false
  feedbackTeaId.value = undefined
}

function submitFeedback(payload: { message: string; contact?: string; teaId?: number }) {
  feedbackSubmitting.value = true
  return postMessageFeedback({
    anon_user_id: anonUserId.value,
    message: payload.message,
    contact: payload.contact,
    tea_id: payload.teaId
  })
    .then(() => {
      showToast({ message: '已收到，感谢你', duration: 1200 })
      closeFeedback()
    })
    .catch(() => {
      showToast({ message: '网络波动，稍后再试', duration: 1200 })
    })
    .finally(() => {
      feedbackSubmitting.value = false
    })
}

function getExcludeIds() {
  const { map } = getDailyFeedbackMap()
  return Object.keys(map).map((k) => Number(k))
}

function getLikedTeaIds(action: 'like' | 'dislike') {
  const allFeedback = getAllHistoricalFeedback()
  console.log('[DEBUG] All historical feedback:', allFeedback)
  const filtered = Object.entries(allFeedback)
    .filter(([_, act]) => act === action)
    .map(([teaId]) => Number(teaId))
  console.log('[DEBUG] Filtered teaIds for', action, ':', filtered)
  return filtered
}

function loadFirstPage() {
  state.page = 1
  state.total = 0
  state.teas = []
  return loadMore()
}

function loadMore() {
  if (state.loading) return Promise.resolve()
  state.loading = true
  state.error = ''

  // 根据过滤类型决定参数
  let category: FilterType | undefined = state.category
  let teaIds: number[] | undefined = undefined
  let excludeIds: number[] | undefined = undefined

  if (state.category === 'liked') {
    category = undefined
    teaIds = getLikedTeaIds('like')
  } else if (state.category === 'disliked') {
    category = undefined
    teaIds = getLikedTeaIds('dislike')
  } else {
    excludeIds = getExcludeIds()
  }

  console.log('[DEBUG] loadMore - category:', state.category, 'teaIds:', teaIds, 'excludeIds:', excludeIds)

  return fetchTeas({
    category: category as any,
    page: state.page,
    pageSize: state.pageSize,
    anonUserId: anonUserId.value,
    excludeIds,
    teaIds
  })
    .then((res) => {
      console.log('[DEBUG] API response:', res)
      state.total = res.total
      state.teas = [...state.teas, ...res.items]
      state.page += 1
      const top = res.items?.[0]
      if (top) postEvent({ anon_user_id: anonUserId.value, tea_id: top.id, type: 'impression' }).catch(() => {})
      if (res.items.length === 0 && state.teas.length === 0) {
        state.error = state.category === 'liked' || state.category === 'disliked' ? 'empty_feedback' : 'empty'
      }
    })
    .catch(() => {
      state.error = 'network'
    })
    .finally(() => {
      state.loading = false
    })
}

function retry() {
  if (state.teas.length) return
  loadFirstPage()
}

watch(
  () => state.category,
  () => {
    closeDetail()
    loadFirstPage()
  }
)

onMounted(() => {
  anonUserId.value = getAnonUserId()
  online.value = navigator.onLine
  window.addEventListener('online', () => (online.value = true))
  window.addEventListener('offline', () => (online.value = false))
  window.addEventListener('keydown', onKeydown)
  loadFirstPage()
})
</script>

<template>
  <div class="min-h-dvh bg-paper">
    <FeedHeader
      :categories="categories"
      :selected="state.category"
      :online="online"
      @select="(k) => (state.category = k)"
      @feedback="openFeedback()"
    />

    <div class="mx-auto max-w-[980px] px-5 pt-[132px]">
      <div v-if="state.error === 'empty'" class="rounded-3xl bg-white px-7 py-10 text-center shadow-tea ring-1 ring-black/5">
        <div class="mx-auto h-12 w-12 rounded-2xl bg-emerald-500/10 ring-1 ring-emerald-900/10" />
        <div class="mt-4 text-[16px] font-semibold text-slate-900">新茶即将上架，敬请期待</div>
        <div class="mt-2 text-[13px] text-slate-500">先去别的分类随缘看看，或稍后再来。</div>
      </div>

      <div v-else-if="state.error === 'empty_feedback'" class="rounded-3xl bg-white px-7 py-10 text-center shadow-tea ring-1 ring-black/5">
        <div class="mx-auto h-12 w-12 rounded-2xl bg-slate-500/10 ring-1 ring-slate-900/10" />
        <div class="mt-4 text-[16px] font-semibold text-slate-900">还没有记录</div>
        <div class="mt-2 text-[13px] text-slate-500">去浏览茶叶，标记你喜欢的口味吧。</div>
      </div>

      <div v-else-if="state.error === 'network' && state.teas.length === 0" class="rounded-3xl bg-white px-7 py-10 text-center shadow-tea ring-1 ring-black/5">
        <div class="mx-auto h-12 w-12 rounded-2xl bg-amber-500/10 ring-1 ring-amber-900/10" />
        <div class="mt-4 text-[16px] font-semibold text-slate-900">网络波动，点击品茗杯重试</div>
        <button class="mt-5 rounded-2xl bg-slate-900 px-5 py-3 text-[13px] font-semibold text-white hover:bg-slate-800" @click="retry">重试</button>
      </div>

        <div v-else class="mx-auto flex w-full max-w-[980px] items-center justify-center gap-4">
          <div v-if="!isHistoryView && topTea" class="hidden shrink-0 lg:block">
            <button class="flex h-32 w-32 items-center justify-center rounded-full bg-white px-5 py-3 text-[13px] font-semibold text-slate-700 ring-1 ring-black/5 hover:bg-slate-50 hover:scale-105 active:scale-95 transition-all" @click="commit('dislike')">
              <span class="text-slate-700">← 不喜欢</span>
            </button>
          </div>

          <div class="relative mx-auto w-full max-w-[520px]">
            <div v-if="topTea" class="relative">
              <div v-if="!isHistoryView" class="pointer-events-none absolute -left-2 top-6 z-30 rounded-2xl bg-emerald-500/90 px-4 py-2 text-[13px] font-semibold text-white" :style="{ opacity: likeOpacity }">喜欢</div>
              <div v-if="!isHistoryView" class="pointer-events-none absolute -right-2 top-6 z-30 rounded-2xl bg-rose-500/90 px-4 py-2 text-[13px] font-semibold text-white" :style="{ opacity: dislikeOpacity }">不喜欢</div>

              <div
                class="relative"
                :class="!isHistoryView ? 'touch-none select-none' : 'touch-none select-none cursor-grab active:cursor-grabbing'"
                :style="!isHistoryView ? cardStyle : historyCardStyle"
                @pointerdown="!isHistoryView ? onPointerDown($event) : onHistoryPointerDown($event)"
                @pointermove="!isHistoryView ? onPointerMove($event) : onHistoryPointerMove($event)"
                @pointerup="!isHistoryView ? onPointerUp($event) : onHistoryPointerUp($event)"
                @pointercancel="!isHistoryView ? onPointerUp($event) : onHistoryPointerUp($event)"
              >
                <TeaCard :tea="topTea" :isTop="true" :online="online" />
              </div>

              <div v-if="!isHistoryView" class="mt-5 flex items-center justify-between gap-3 lg:hidden">
                <button class="flex-1 rounded-full bg-white px-5 py-3 text-[13px] font-semibold text-slate-700 ring-1 ring-black/5 hover:bg-slate-50" @click="commit('dislike')">← 不喜欢</button>
                <button class="flex-1 rounded-full bg-slate-900 px-5 py-3 text-[13px] font-semibold text-white hover:bg-slate-800" @click="commit('like')">喜欢 →</button>
              </div>
              <div v-if="!isHistoryView" class="mt-4 text-center text-[12px] text-slate-400">移动端滑动或点击按钮，PC 用方向键选择</div>
              <div v-if="isHistoryView" class="mt-4 text-center text-[12px] text-slate-400">滑动卡片查看更多</div>
            </div>

            <div v-else class="rounded-3xl bg-white px-7 py-10 text-center shadow-tea ring-1 ring-black/5">
              <div class="text-[16px] font-semibold text-slate-900">这一轮都喝完了</div>
              <div class="mt-2 text-[13px] text-slate-500">换个分类，或明天再来。</div>
            </div>

            <div v-if="restTeas.length && !isHistoryView" class="pointer-events-none absolute inset-x-0 top-6 -z-10 mx-auto w-[96%] opacity-80">
              <div v-for="(t, idx) in restTeas" :key="t.id" class="absolute inset-x-0" :style="{ transform: `translateY(${(idx + 1) * 14}px) scale(${1 - (idx + 1) * 0.03})` }">
                <TeaCard :tea="t" :isTop="false" :online="online" />
              </div>
            </div>
          </div>

          <div v-if="!isHistoryView && topTea" class="hidden shrink-0 lg:block">
            <button class="flex h-32 w-32 items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-[13px] font-semibold text-white hover:bg-slate-800 hover:scale-105 active:scale-95 transition-all" @click="commit('like')">
              <span>喜欢 →</span>
            </button>
          </div>

          <div v-if="state.loading" class="absolute inset-x-0 top-1/2 -translate-y-1/2 flex items-center justify-center gap-3 text-[13px] text-slate-500 bg-paper/80 backdrop-blur-sm py-4"><van-loading size="18" />正在泡新茶…</div>
        </div>

        <div v-if="state.loading && !topTea" class="mt-6 flex items-center justify-center gap-3 text-[13px] text-slate-500"><van-loading size="18" />正在泡新茶…</div>
      </div>

    <TeaDetailPopup
      :show="detailOpen"
      :tea="detailTea"
      :isHistoryView="isHistoryView"
      @close="closeDetail"
      @like="commit('like'); closeDetail()"
      @dislike="commit('dislike'); closeDetail()"
      @feedback="openFeedback(detailTea?.id)"
    />

    <FeedbackFormPopup
      :show="feedbackOpen"
      :teaId="feedbackTeaId"
      :submitting="feedbackSubmitting"
      @close="closeFeedback"
      @submit="submitFeedback"
    />
  </div>
</template>
