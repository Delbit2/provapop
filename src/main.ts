import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/colors.css'
import './styles/global.css'

library.add(fas as any, fab as any)

const app = createApp(App)
const pinia = createPinia()

app.config.errorHandler = (err, _instance, info) => {
  console.error('[VUE ERROR]', err, info)
}

app.use(pinia)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

async function bootstrap() {
  try {
    const authStore = useAuthStore(pinia)

    authStore.initAuthListener()
    await authStore.initAuth()
  } catch (err) {
    console.error('[BOOTSTRAP] Falha ao inicializar autenticação:', err)
  } finally {
    app.mount('#app')
  }
}

bootstrap()
