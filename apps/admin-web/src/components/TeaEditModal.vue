<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

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

const props = defineProps<{
  show: boolean
  editing: boolean
  saving: boolean
  initial: TeaBase
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', payload: TeaBase): void
  (e: 'pickCover', file: File): void
}>()

const form = reactive<TeaBase>({
  name: '',
  category: 'pu_er',
  year: new Date().getFullYear(),
  origin: '',
  spec: '357g/饼',
  price_min: null,
  price_max: null,
  intro: null,
  cover_url: '',
  status: 'online',
  weight: 0
})

const coverInputMode = ref<'file' | 'url' | 'preview'>('file')
const coverUrlInput = ref('')

// 监听模态框显示状态，初始化表单
watch(
  () => props.show,
  (show) => {
    if (show) {
      // 模态框打开时，重置表单
      Object.assign(form, props.initial)
      coverUrlInput.value = props.initial.cover_url
      coverInputMode.value = props.initial.cover_url ? 'preview' : 'file'
    }
  },
  { immediate: false }
)

// 监听上传回调，URL 改变时更新表单
watch(
  () => props.initial.cover_url,
  (newUrl, oldUrl) => {
    // 只在上传后更新（新 URL 不为空且不同于当前值）
    // 并且避免初始化时的触发
    if (oldUrl !== undefined && newUrl && newUrl !== form.cover_url) {
      form.cover_url = newUrl
      coverUrlInput.value = newUrl
      coverInputMode.value = 'preview'
    }
  },
  { flush: 'post' }
)

const canSave = computed(() => form.name.trim() && form.cover_url.trim() && !props.saving)

function switchToMode(mode: 'file' | 'url' | 'preview') {
  coverInputMode.value = mode
  if (mode === 'url') {
    coverUrlInput.value = form.cover_url
  }
}

function onPickCover(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  emit('pickCover', file)
  ;(e.target as HTMLInputElement).value = ''
}

function onConfirmUrl() {
  const url = coverUrlInput.value.trim()
  if (!url) return
  form.cover_url = url
  coverInputMode.value = 'preview'
}

function save() {
  if (!canSave.value) return
  emit('save', { ...form })
}
</script>

<template>
  <div v-if="props.show" class="fixed inset-0 z-50 flex items-end justify-center bg-black/60 p-4 md:items-center">
    <div class="w-full max-w-[820px] overflow-hidden rounded-[28px] bg-[#0F172A] shadow-glass ring-1 ring-white/10">
      <div class="flex items-center justify-between border-b border-white/10 px-6 py-5">
        <div class="text-[14px] font-semibold text-white">{{ props.editing ? '编辑茶叶' : '新增茶叶' }}</div>
        <button class="rounded-full bg-white/10 px-3 py-2 text-[12px] text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="emit('close')">关闭</button>
      </div>

      <div class="grid gap-4 p-6 md:grid-cols-2">
        <label class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">名称 *</span>
          <input v-model="form.name" :disabled="props.saving" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
        </label>

        <label class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">分类 *</span>
          <select v-model="form.category" :disabled="props.saving" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60">
            <option value="pu_er">普洱</option>
            <option value="white">白茶</option>
            <option value="yancha">岩茶</option>
            <option value="black">红茶</option>
          </select>
        </label>

        <label class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">年份 *</span>
          <input v-model.number="form.year" :disabled="props.saving" type="number" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
        </label>

        <label class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">产地 *</span>
          <input v-model="form.origin" :disabled="props.saving" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
        </label>

        <label class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">规格 *</span>
          <input v-model="form.spec" :disabled="props.saving" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
        </label>

        <div class="grid gap-2">
          <span class="text-[12px] font-semibold text-slate-200">主图 *</span>

          <!-- 已有图片预览 -->
          <div v-if="form.cover_url && coverInputMode === 'preview'" class="flex items-center gap-3">
            <img :src="form.cover_url" alt="预览" class="h-16 w-16 rounded-xl object-cover ring-1 ring-white/10" />
            <div class="min-w-0 flex-1">
              <div class="min-w-0 truncate text-[12px] text-slate-300">{{ form.cover_url }}</div>
              <div class="mt-2 flex items-center gap-2">
                <button class="text-[12px] text-emerald-400 hover:text-emerald-300" @click="switchToMode('file')">更换图片</button>
                <span class="text-[12px] text-slate-500">|</span>
                <button class="text-[12px] text-emerald-400 hover:text-emerald-300" @click="switchToMode('url')">粘贴链接</button>
              </div>
            </div>
          </div>

          <!-- 无图片或显示输入模式 -->
          <div v-else>
            <div class="flex items-center gap-2 mb-2">
              <button
                class="rounded-xl px-3 py-2 text-[12px] ring-1 transition-colors"
                :class="coverInputMode === 'file' ? 'bg-emerald-500/10 text-emerald-200 ring-emerald-400/20' : 'bg-white/5 text-slate-300 ring-white/10 hover:bg-white/10'"
                @click="switchToMode('file')"
              >
                本地上传
              </button>
              <button
                class="rounded-xl px-3 py-2 text-[12px] ring-1 transition-colors"
                :class="coverInputMode === 'url' ? 'bg-emerald-500/10 text-emerald-200 ring-emerald-400/20' : 'bg-white/5 text-slate-300 ring-white/10 hover:bg-white/10'"
                @click="switchToMode('url')"
              >
                图片链接
              </button>
              <button v-if="form.cover_url" class="ml-auto text-[12px] text-slate-400 hover:text-slate-200" @click="switchToMode('preview')">返回预览</button>
            </div>

            <!-- 文件上传模式 -->
            <div v-if="coverInputMode === 'file'" class="flex items-center gap-3">
              <input :disabled="props.saving" type="file" accept="image/*" @change="onPickCover" class="text-[12px] text-slate-200" />
              <div class="min-w-0 text-[12px] text-slate-400">支持 jpg、png、webp</div>
            </div>

            <!-- URL 输入模式 -->
            <div v-if="coverInputMode === 'url'" class="flex items-center gap-2">
              <input
                v-model="coverUrlInput"
                :disabled="props.saving"
                type="url"
                placeholder="https://example.com/image.jpg"
                class="min-w-0 flex-1 rounded-xl bg-black/20 px-3 py-2 text-[12px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60"
                @keyup.enter="onConfirmUrl"
              />
              <button :disabled="props.saving || !coverUrlInput.trim()" class="rounded-xl bg-emerald-500/10 px-3 py-2 text-[12px] font-semibold text-emerald-200 ring-1 ring-emerald-400/20 hover:bg-emerald-500/15 disabled:opacity-60" @click="onConfirmUrl">确认</button>
            </div>
          </div>
        </div>

        <label class="grid gap-2 md:col-span-2">
          <span class="text-[12px] font-semibold text-slate-200">简介</span>
          <textarea v-model="form.intro" :disabled="props.saving" class="h-24 resize-none rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
        </label>

        <div class="grid grid-cols-2 gap-4">
          <label class="grid gap-2">
            <span class="text-[12px] font-semibold text-slate-200">价格下限</span>
            <input v-model.number="form.price_min" :disabled="props.saving" type="number" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
          </label>
          <label class="grid gap-2">
            <span class="text-[12px] font-semibold text-slate-200">价格上限</span>
            <input v-model.number="form.price_max" :disabled="props.saving" type="number" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
          </label>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <label class="grid gap-2">
            <span class="text-[12px] font-semibold text-slate-200">状态</span>
            <select v-model="form.status" :disabled="props.saving" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60">
              <option value="online">上架</option>
              <option value="offline">下架</option>
            </select>
          </label>
          <label class="grid gap-2">
            <span class="text-[12px] font-semibold text-slate-200">权重</span>
            <input v-model.number="form.weight" :disabled="props.saving" type="number" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30 disabled:opacity-60" />
          </label>
        </div>
      </div>

      <div class="flex items-center justify-between border-t border-white/10 px-6 py-5">
        <div class="text-[12px] text-slate-300">必填：名称、主图、分类、年份、产地、规格</div>
        <div class="flex items-center gap-2">
          <button class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="emit('close')">取消</button>
          <button class="rounded-2xl bg-white px-5 py-3 text-[13px] font-semibold text-slate-900 hover:bg-slate-50 disabled:opacity-60" :disabled="!canSave" @click="save">
            {{ props.saving ? '保存中…' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
