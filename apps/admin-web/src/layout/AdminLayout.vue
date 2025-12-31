<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearToken } from '@/lib/auth'

const route = useRoute()
const router = useRouter()

const active = computed(() => {
  if (route.path.startsWith('/admin/teas')) return 'teas'
  if (route.path.startsWith('/admin/import')) return 'import'
  if (route.path.startsWith('/admin/dashboard')) return 'dashboard'
  return 'teas'
})

function logout() {
  clearToken()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-dvh">
    <div class="mx-auto flex max-w-[1200px] gap-5 px-6 py-6">
      <aside class="w-[280px] shrink-0 rounded-[26px] bg-white/5 p-5 shadow-glass ring-1 ring-white/10 backdrop-blur">
        <div class="flex items-center justify-between">
          <div>
            <div class="text-[16px] font-semibold text-slate-50">来喝茶 · 管理台</div>
            <div class="mt-1 text-[12px] text-slate-300">内容管理 · 导入 · 看板</div>
          </div>
          <button class="rounded-full bg-white/10 px-3 py-2 text-[12px] text-slate-100 ring-1 ring-white/10 hover:bg-white/15" @click="logout">
            退出
          </button>
        </div>

        <nav class="mt-6 grid gap-2">
          <router-link
            to="/admin/teas"
            class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10 transition"
            :class="active === 'teas' ? 'bg-white/15 text-white' : 'bg-transparent text-slate-200 hover:bg-white/10'"
          >
            茶叶管理
          </router-link>
          <router-link
            to="/admin/import"
            class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10 transition"
            :class="active === 'import' ? 'bg-white/15 text-white' : 'bg-transparent text-slate-200 hover:bg-white/10'"
          >
            Excel 导入
          </router-link>
          <router-link
            to="/admin/dashboard"
            class="rounded-2xl px-4 py-3 text-[13px] font-semibold ring-1 ring-white/10 transition"
            :class="active === 'dashboard' ? 'bg-white/15 text-white' : 'bg-transparent text-slate-200 hover:bg-white/10'"
          >
            数据看板
          </router-link>
        </nav>

        <div class="mt-6 rounded-2xl bg-black/20 px-4 py-3 text-[12px] text-slate-300 ring-1 ring-white/10">
          提示：本环境缺少 Node.js，前端依赖需在本机安装 Node 后执行安装。
        </div>
      </aside>

      <main class="min-w-0 flex-1">
        <div class="rounded-[26px] bg-white/5 p-6 shadow-glass ring-1 ring-white/10 backdrop-blur">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>
