import { createApp } from 'vue'
import App from './App.vue'

import { Loading, Popup } from 'vant'

import 'vant/lib/index.css'
import './style.css'

const app = createApp(App)
app.use(Loading)
app.use(Popup)
app.mount('#app')
