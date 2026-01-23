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

app.use(pinia)
app.use(router)
app.component('font-awesome-icon', FontAwesomeIcon)

const authStore = useAuthStore()
// Verificar autenticação na inicialização, mas não bloquear o mount
// O router guard cuidará da autenticação nas rotas
authStore.verifyAuth().catch(() => {
  // Ignorar erros na verificação inicial
  // O usuário será redirecionado pelo router guard se necessário
}).finally(() => {
  app.mount('#app')
})
