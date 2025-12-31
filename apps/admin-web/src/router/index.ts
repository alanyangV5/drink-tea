import { createRouter, createWebHashHistory } from 'vue-router'
import { isAuthed } from '@/lib/auth'

import LoginView from '@/views/LoginView.vue'
import AdminLayout from '@/layout/AdminLayout.vue'
import TeasView from '@/views/TeasView.vue'
import ImportView from '@/views/ImportView.vue'
import DashboardView from '@/views/DashboardView.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/admin/teas' },
    { path: '/login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: 'teas', component: TeasView },
        { path: 'import', component: ImportView },
        { path: 'dashboard', component: DashboardView },
        { path: '', redirect: '/admin/teas' }
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isAuthed()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.path === '/login' && isAuthed()) {
    return { path: '/admin/teas' }
  }
  return true
})
