<template>
  <div class="auth-screen">
    <Transition name="fade" appear>
      <div class="auth-screen__container">
        <div class="auth-screen__header">
          <h1 class="auth-screen__title">ProvaPop!</h1>
          <p class="auth-screen__subtitle">Recuperação de Senha</p>
        </div>

        <Card variant="elevated" class="auth-screen__card">
          <div v-if="success" class="auth-screen__success">
            E-mail de recuperação enviado! Verifique sua caixa de entrada (e spam).
          </div>
          
          <form v-else @submit.prevent="handleForgot" class="auth-screen__form">
            <p class="auth-screen__text">Digite o e-mail cadastrado e enviaremos um link para você redefinir sua senha.</p>
            
            <div class="auth-screen__field">
              <label class="auth-screen__label">
                <font-awesome-icon icon="envelope" class="auth-screen__label-icon" />
                Email
              </label>
              <input
                v-model="email"
                type="email"
                class="auth-screen__input"
                placeholder="Digite seu email"
                required
              />
            </div>

            <div v-if="error" class="auth-screen__error">
              {{ error }}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              full-width
              :disabled="loading"
              class="auth-screen__submit"
            >
              <font-awesome-icon v-if="loading" icon="circle-notch" class="auth-screen__spinner" />
              {{ loading ? 'Enviando...' : 'Enviar Link' }}
            </Button>
          </form>

          <div class="auth-screen__footer">
            <p>Lembrou a senha? <a href="#" @click.prevent="goToLogin" class="auth-screen__link">Voltar para Login</a></p>
          </div>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'

const router = useRouter()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleForgot() {
  loading.value = true
  error.value = ''
  
  try {
    // Ajuste a URL '/api/auth/forgot-password' se o seu backend for diferente
    const response = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })
    
    if (!response.ok) throw new Error('Erro ao solicitar recuperação. Verifique o e-mail.')
    
    success.value = true
  } catch (e: any) {
    error.value = e.message || 'Ocorreu um erro.'
  } finally {
    loading.value = false
  }
}

function goToLogin() {
  router.push('/entrar')
}
</script>

<style scoped>
.auth-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.auth-screen__container { width: 100%; max-width: 100%; }
.auth-screen__header { text-align: center; margin-bottom: 24px; }
.auth-screen__title {
  font-size: 36px; font-weight: 700; margin: 0 0 8px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.auth-screen__subtitle { font-size: 14px; color: var(--black-soft); margin: 0; }
.auth-screen__card { padding: 24px; }
.auth-screen__text { font-size: 14px; color: var(--black-soft); margin-bottom: 16px; text-align: center; }
.auth-screen__form { display: flex; flex-direction: column; gap: 20px; }
.auth-screen__field { display: flex; flex-direction: column; gap: 8px; }
.auth-screen__label { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--black-soft); }
.auth-screen__label-icon { font-size: 14px; color: var(--green-primary); }
.auth-screen__input {
  width: 100%; padding: 12px 16px; font-size: 15px; border: 2px solid var(--gray-light);
  border-radius: var(--border-radius-full); background: var(--white); color: var(--black-soft);
  transition: all var(--transition-base); font-family: inherit; outline: none;
}
.auth-screen__input:focus { border-color: var(--green-primary); box-shadow: 0 0 0 3px var(--green-pastel); }
.auth-screen__error {
  padding: 12px; background: var(--yellow-pastel); border: 2px solid var(--yellow-primary);
  border-radius: var(--border-radius-md); color: var(--yellow-dark); font-size: 13px; font-weight: 500; text-align: center;
}
.auth-screen__success {
  padding: 16px; background: #e8f5e9; border: 2px solid var(--green-primary);
  border-radius: var(--border-radius-md); color: #2e7d32; font-size: 14px; font-weight: 500; text-align: center; margin-bottom: 16px;
}
.auth-screen__submit { margin-top: 8px; }
.auth-screen__spinner { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.auth-screen__footer { text-align: center; padding-top: 20px; border-top: 1px solid var(--gray-light); font-size: 13px; margin-top: 20px;}
.auth-screen__link { color: var(--green-primary); text-decoration: none; font-weight: 600; transition: color var(--transition-base); }
.auth-screen__link:hover { color: var(--green-dark); text-decoration: underline; }
.fade-enter-active, .fade-leave-active { transition: opacity var(--transition-slow), transform var(--transition-slow); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(20px); }

@media (min-width: 768px) {
  .auth-screen { padding: 24px; }
  .auth-screen__container { max-width: 440px; }
  .auth-screen__header { margin-bottom: 32px; }
  .auth-screen__title { font-size: 48px; }
  .auth-screen__subtitle { font-size: 16px; }
  .auth-screen__card { padding: 40px; }
  .auth-screen__input { padding: 14px 16px; font-size: 16px; }
}
</style>
