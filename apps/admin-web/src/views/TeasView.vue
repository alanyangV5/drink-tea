<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import TeaEditModal from '@/components/TeaEditModal.vue'
import { adminDelete, adminGet, adminPost, adminPut, adminUpload } from '@/lib/api'

type TeaItem = {
  id: number
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

type TeaBase = Omit<TeaItem, 'id'>

type TeaListOut = { items: TeaItem[]; page: number; page_size: number; total: number }

const query = reactive({ keyword: '', status: '', category: '' })
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const list = ref<TeaItem[]>([])

const editOpen = ref(false)
const editId = ref<number | null>(null)
const editInitial = ref<TeaBase>({
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

const isEditing = computed(() => editId.value != null)

function toBase(t: TeaItem): TeaBase {
  return {
    name: t.name,
    category: t.category,
    year: t.year,
    origin: t.origin,
    spec: t.spec,
    price_min: t.price_min,
    price_max: t.price_max,
    intro: t.intro,
    cover_url: t.cover_url,
    status: t.status,
    weight: t.weight
  }
}

function openCreate() {
  editId.value = null
  editInitial.value = {
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
  }
  editOpen.value = true
}

function openUpdate(t: TeaItem) {
  editId.value = t.id
  editInitial.value = toBase(t)
  editOpen.value = true
}

function closeEdit() {
  editOpen.value = false
}

function fetchList() {
  loading.value = true
  error.value = ''

  const sp = new URLSearchParams()
  if (query.keyword.trim()) sp.set('keyword', query.keyword.trim())
  if (query.status) sp.set('status', query.status)
  if (query.category) sp.set('category', query.category)

  return adminGet<TeaListOut>(`/api/admin/teas?${sp.toString()}`)
    .then((res) => {
      list.value = res.items
    })
    .catch(() => {
      error.value = '加载失败，请检查后端是否启动或登录是否过期'
    })
    .finally(() => {
      loading.value = false
    })
}

function save(payload: TeaBase) {
  saving.value = true
  error.value = ''

  const req = isEditing.value
    ? adminPut<TeaItem>(`/api/admin/teas/${editId.value}`, payload)
    : adminPost<TeaItem>('/api/admin/teas', payload)

  return req
    .then(() => {
      closeEdit()
      return fetchList()
    })
    .catch(() => {
      error.value = '保存失败：请检查字段必填、图片上传与后端配置'
    })
    .finally(() => {
      saving.value = false
    })
}

function removeTea(t: TeaItem) {
  const ok = window.confirm(`确认删除「${t.name}」？该操作不可撤销。`)
  if (!ok) return

  saving.value = true
  error.value = ''

  return adminDelete(`/api/admin/teas/${t.id}`)
    .then(() => fetchList())
    .catch(() => {
      error.value = '删除失败：请检查登录状态'
    })
    .finally(() => {
      saving.value = false
    })
}

function toggleStatus(t: TeaItem) {
  const next = t.status === 'online' ? 'offline' : 'online'
  saving.value = true
  error.value = ''

  return adminPut<TeaItem>(`/api/admin/teas/${t.id}`, { ...toBase(t), status: next })
    .then(() => fetchList())
    .catch(() => {
      error.value = '更新失败：请检查登录状态'
    })
    .finally(() => {
      saving.value = false
    })
}

function updateWeight(t: TeaItem, weightRaw: string) {
  const weight = Number(weightRaw)
  if (Number.isNaN(weight)) return

  saving.value = true
  error.value = ''

  return adminPut<TeaItem>(`/api/admin/teas/${t.id}`, { ...toBase(t), weight })
    .then(() => fetchList())
    .catch(() => {
      error.value = '更新失败：请检查登录状态'
    })
    .finally(() => {
      saving.value = false
    })
}

function pickCover(file: File) {
  saving.value = true
  error.value = ''
  return adminUpload(file)
    .then((res) => {
      editInitial.value = { ...editInitial.value, cover_url: res.url }
    })
    .catch(() => {
      error.value = '上传失败：请检查后端是否安装 python-multipart 并启动'
    })
    .finally(() => {
      saving.value = false
    })
}

onMounted(() => {
  fetchList()
})
</script>

<template>
  <div>
    <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <div class="text-[16px] font-semibold text-white">茶叶管理</div>
        <div class="mt-1 text-[12px] text-slate-300">检索/创建/编辑/上下架/权重</div>
      </div>
      <div class="flex items-center gap-2">
        <button class="rounded-2xl bg-white px-4 py-3 text-[13px] font-semibold text-slate-900 hover:bg-slate-50" @click="openCreate">新增茶叶</button>
        <button class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="fetchList">刷新</button>
      </div>
    </div>

    <div class="mt-6 grid gap-3 md:grid-cols-3">
      <label class="grid gap-2">
        <span class="text-[12px] font-semibold text-slate-200">关键词</span>
        <input v-model="query.keyword" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30" placeholder="名称包含…" />
      </label>
      <label class="grid gap-2">
        <span class="text-[12px] font-semibold text-slate-200">状态</span>
        <select v-model="query.status" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30">
          <option value="">全部</option>
          <option value="online">上架</option>
          <option value="offline">下架</option>
        </select>
      </label>
      <label class="grid gap-2">
        <span class="text-[12px] font-semibold text-slate-200">分类</span>
        <select v-model="query.category" class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30">
          <option value="">全部</option>
          <option value="pu_er">普洱</option>
          <option value="white">白茶</option>
          <option value="yancha">岩茶</option>
          <option value="black">红茶</option>
        </select>
      </label>
    </div>

    <div class="mt-4 flex items-center gap-3">
      <button class="rounded-2xl bg-white/10 px-4 py-3 text-[13px] font-semibold text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="fetchList">搜索</button>
      <div v-if="loading" class="text-[12px] text-slate-300">加载中…</div>
      <div v-if="saving" class="text-[12px] text-slate-300">处理中…</div>
      <div v-if="error" class="text-[12px] text-rose-200">{{ error }}</div>
    </div>

    <div class="mt-6 overflow-hidden rounded-3xl bg-black/20 ring-1 ring-white/10">
      <table class="w-full text-left text-[12px]">
        <thead class="bg-white/5 text-slate-200">
          <tr>
            <th class="px-4 py-3">名称</th>
            <th class="px-4 py-3">分类</th>
            <th class="px-4 py-3">年份</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3">权重</th>
            <th class="px-4 py-3">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in list" :key="t.id" class="border-t border-white/10 text-slate-100">
            <td class="px-4 py-3">
              <div class="font-semibold">{{ t.name }}</div>
              <div class="mt-1 text-slate-300">{{ t.origin }} · {{ t.spec }}</div>
            </td>
            <td class="px-4 py-3 text-slate-200">{{ t.category }}</td>
            <td class="px-4 py-3 text-slate-200">{{ t.year }}</td>
            <td class="px-4 py-3">
              <button class="rounded-full px-3 py-1 text-[12px] ring-1" :class="t.status === 'online' ? 'bg-emerald-500/10 text-emerald-200 ring-emerald-400/20' : 'bg-slate-500/10 text-slate-200 ring-white/10'" @click="toggleStatus(t)">
                {{ t.status === 'online' ? '上架' : '下架' }}（点切换）
              </button>
            </td>
            <td class="px-4 py-3">
              <input class="w-20 rounded-xl bg-black/20 px-3 py-2 text-[12px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30" type="number" :value="t.weight" @change="(e) => updateWeight(t, (e.target as HTMLInputElement).value)" />
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <button class="rounded-xl bg-white/10 px-3 py-2 text-[12px] font-semibold ring-1 ring-white/10 hover:bg-white/15" @click="openUpdate(t)">编辑</button>
                <button class="rounded-xl bg-rose-500/10 px-3 py-2 text-[12px] font-semibold text-rose-200 ring-1 ring-rose-400/20 hover:bg-rose-500/15" @click="removeTea(t)">删除</button>
              </div>
            </td>
          </tr>
          <tr v-if="!loading && list.length === 0">
            <td class="px-4 py-6 text-slate-300" colspan="6">暂无数据。点击“新增茶叶”开始录入。</td>
          </tr>
        </tbody>
      </table>
    </div>

    <TeaEditModal :show="editOpen" :editing="isEditing" :saving="saving" :initial="editInitial" @close="closeEdit" @save="save" @pickCover="pickCover" />
  </div>
</template>
