<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  show: boolean
  teaId?: number
  submitting?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'submit', payload: { message: string; contact?: string; teaId?: number }): void
}>()

const message = ref('')
const contact = ref('')

watch(
  () => props.show,
  (v) => {
    if (!v) return
    message.value = ''
    contact.value = ''
  }
)

function submit() {
  const m = message.value.trim()
  if (!m) return
  emit('submit', { message: m, contact: contact.value.trim() || undefined, teaId: props.teaId })
}
</script>

<template>
  <van-popup :show="props.show" position="bottom" round :style="{ height: '70vh' }" @click-overlay="emit('close')">
    <div class="h-full bg-paper px-6 pb-8 pt-6">
      <div class="flex items-center justify-between">
        <div class="text-[16px] font-semibold text-slate-900">意见反馈</div>
        <button class="rounded-full bg-white px-3 py-2 text-[12px] text-slate-600 ring-1 ring-black/5" @click="emit('close')">关闭</button>
      </div>

      <div class="mt-5 rounded-3xl bg-white p-5 shadow-tea ring-1 ring-black/5">
        <div class="text-[12px] font-semibold text-slate-700">想对我们说点什么？</div>
        <textarea
          v-model="message"
          :disabled="props.submitting"
          class="mt-3 h-32 w-full resize-none rounded-2xl bg-slate-50 px-4 py-3 text-[13px] leading-relaxed text-slate-800 outline-none ring-1 ring-black/5 focus:ring-2 focus:ring-emerald-400/40 disabled:opacity-60"
          placeholder="比如：更喜欢清甜口感的白茶，希望按香型筛选；或者某张茶卡信息不完整。"
        />

        <div class="mt-4 text-[12px] font-semibold text-slate-700">联系方式（可选）</div>
        <input
          v-model="contact"
          :disabled="props.submitting"
          class="mt-2 w-full rounded-2xl bg-slate-50 px-4 py-3 text-[13px] text-slate-800 outline-none ring-1 ring-black/5 focus:ring-2 focus:ring-emerald-400/40 disabled:opacity-60"
          placeholder="手机号 / 微信 / 邮箱"
        />

        <div v-if="props.teaId" class="mt-4 text-[12px] text-slate-500">关联茶卡：#{{ props.teaId }}</div>
      </div>

      <button
        class="mt-6 w-full rounded-2xl bg-slate-900 px-5 py-4 text-[13px] font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        :disabled="!message.trim() || props.submitting"
        @click="submit"
      >
        {{ props.submitting ? '提交中…' : '提交' }}
      </button>

      <div class="mt-4 text-center text-[12px] text-slate-400">匿名收集，只用于改进推荐与体验。</div>
    </div>
  </van-popup>
</template>
