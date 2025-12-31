<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { adminLogin } from '@/lib/api'
import { setToken } from '@/lib/auth'

const router = useRouter()
const route = useRoute()

const username = ref('admin')
const password = ref('')
const loading = ref(false)
const error = ref('')

const canSubmit = computed(() => username.value.trim() && password.value.trim() && !loading.value)

function submit() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = ''

  adminLogin({ username: username.value.trim(), password: password.value })
    .then((res) => {
      setToken(res.token)
      const redirect = (route.query.redirect as string) || '/admin/teas'
      router.push(redirect)
    })
    .catch(() => {
      error.value = '账号或密码不正确'
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <div class="min-h-dvh">
    <div class="mx-auto flex max-w-[1100px] items-center justify-center px-6 py-14">
      <div class="grid w-full grid-cols-1 gap-6 lg:grid-cols-2">
        <div class="hidden lg:block">
          <div class="rounded-[32px] bg-white/5 p-8 shadow-glass ring-1 ring-white/10 backdrop-blur">
            <div class="text-[26px] font-semibold text-white">来喝茶 · 管理台</div>
            <div class="mt-3 text-[13px] leading-relaxed text-slate-200">
              这里是茶叶内容与数据的控制中心：上架、导入、看板与排序调参。
            </div>
            <div class="mt-8 grid gap-3">
              <div class="rounded-2xl bg-black/20 px-4 py-3 text-[12px] text-slate-200 ring-1 ring-white/10">极简字段规范 · 让内容可控</div>
              <div class="rounded-2xl bg-black/20 px-4 py-3 text-[12px] text-slate-200 ring-1 ring-white/10">喜欢率排行 · 让选品有据</div>
              <div class="rounded-2xl bg-black/20 px-4 py-3 text-[12px] text-slate-200 ring-1 ring-white/10">导入校验与报告 · 让数据可靠</div>
            </div>
          </div>
        </div>

        <div>
          <div class="rounded-[32px] bg-white/5 p-8 shadow-glass ring-1 ring-white/10 backdrop-blur">
            <div class="text-[18px] font-semibold text-white">登录</div>
            <div class="mt-2 text-[13px] text-slate-300">单管理员账号密码</div>

            <div class="mt-6 grid gap-4">
              <label class="grid gap-2">
                <span class="text-[12px] font-semibold text-slate-200">账号</span>
                <input
                  v-model="username"
                  class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30"
                  placeholder="admin"
                />
              </label>
              <label class="grid gap-2">
                <span class="text-[12px] font-semibold text-slate-200">密码</span>
                <input
                  v-model="password"
                  type="password"
                  class="rounded-2xl bg-black/20 px-4 py-3 text-[13px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-emerald-400/30"
                  placeholder="请输入密码"
                />
              </label>

              <div v-if="error" class="rounded-2xl bg-rose-500/10 px-4 py-3 text-[12px] text-rose-200 ring-1 ring-rose-400/20">
                {{ error }}
              </div>

              <button
                class="mt-1 rounded-2xl bg-white px-5 py-4 text-[13px] font-semibold text-slate-900 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="!canSubmit"
                @click="submit"
              >
                {{ loading ? '登录中…' : '进入管理台' }}
              </button>

              <div class="text-center text-[12px] text-slate-400">建议在内网环境使用；生产环境请修改默认账号密码。</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
