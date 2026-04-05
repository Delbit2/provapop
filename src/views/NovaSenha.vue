<template>
  <div class="auth-screen">
    <Transition name="fade" appear>
      <div class="auth-screen__container">
        <div class="auth-screen__header">
          <h1 class="auth-screen__title">ProvaPop!</h1>
          <p class="auth-screen__subtitle">Criar Nova Senha</p>
        </div>

        <Card variant="elevated" class="auth-screen__card">
          <div v-if="success" class="auth-screen__success">
            Senha alterada com sucesso! Você já pode fazer login.
            <Button @click="goToLogin" variant="primary" class="auth-screen__mt">Ir para o Login</Button>
          </div>
          
          <form v-else @submit.prevent="handleReset" class="auth-screen__form">
            <div class="auth-screen__field">
              <label class="auth-screen__label">
                <font-awesome-icon icon="lock" class="auth-screen__label-icon" />
                Nova Senha
              </label>
              <div class="auth-screen__password-wrapper">
                <input
                  v-model="password"
                  :type="showPassword ? 'text' : 'password'"
                  class="auth-screen__input"
                  placeholder="Sua nova senha"
                  required
                />
                <button type="button" class="auth-screen__toggle-password" @click="showPassword = !showPassword">
                  <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
                </button>
              </div>
            </div>

            <div class="auth-screen__field">
              <label class="auth-screen__label">
                <font-awesome-icon icon="lock" class="auth-screen__label-icon" />
                Confirmar Nova Senha
              </label>
              <div class="auth-screen__password-wrapper">
                <input
                  v-model="confirmPassword"
                  :type="showPassword ? 'text' : 'password'"
                  class="auth-screen__input"
                  placeholder="Repita a nova senha"
                  required
                />
              </div>
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
              {{ loading ? 'Salvando...' : 'Salvar Nova Senha' }}
            </Button>
          </form>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'

const router = useRouter()
const route = useRoute()

const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleReset() {
  if (password.value !== confirmPassword.value) {
    error.value = 'As senhas não coincidem.'
    return
  }

  const token = route.query.token // Pega o token da URL ?token=abc123

  if (!token) {
    error.value = 'Link de recuperação inválido ou expirado.'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    // Ajuste a URL se o seu backend for diferente
    const response = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: password.value })
    })
    
    if (!response.ok) throw new Error('Falha ao redefinir a senha. O link pode ter expirado.')
    
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
/* Aproveitando as mesmas classes exatas do EsqueciSenha / Login */
.auth-screen { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 16px; background: var(--white); border: 1px solid var(--green-pastel); }
.auth-screen__container { width: 100%; max-width: 100%; }
.auth-screen__header { text-align: center; margin-bottom: 24px; }
.auth-screen__title { font-size: 36px; font-weight: 700; margin: 0 0 8px 0; background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.auth-screen__subtitle { font-size: 14px; color: var(--black-soft); margin: 0; }
.auth-screen__card { padding: 24px; }
.auth-screen__form { display: flex; flex-direction: column; gap: 20px; }
.auth-screen__field { display: flex; flex-direction: column; gap: 8px; }
.auth-screen__label { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: var(--black-soft); }
.auth-screen__label-icon { font-size: 14px; color: var(--green-primary); }
.auth-screen__input { width: 100%; padding: 12px 16px; font-size: 15px; border: 2px solid var(--gray-light); border-radius: var(--border-radius-full); background: var(--white); color: var(--black-soft); transition: all var(--transition-base); font-family: inherit; outline: none; }
.auth-screen__input:focus { border-color: var(--green-primary); box-shadow: 0 0 0 3px var(--green-pastel); }
.auth-screen__password-wrapper { position: relative; display: flex; align-items: center; }
.auth-screen__password-wrapper .auth-screen__input { padding-right: 50px; }
.auth-screen__toggle-password { position: absolute; right: 16px; background: none; border: none; color: var(--gray-dark); cursor: pointer; padding: 4px; display: flex; align-items: center; justify-content: center; transition: color var(--transition-base); }
.auth-screen__toggle-password:hover { color: var(--green-primary); }
.auth-screen__error { padding: 12px; background: var(--yellow-pastel); border: 2px solid var(--yellow-primary); border-radius: var(--border-radius-md); color: var(--yellow-dark); font-size: 13px; font-weight: 500; text-align: center; }
.auth-screen__success { display:flex; flex-direction:column; gap:16px; padding: 16px; background: #e8f5e9; border: 2px solid var(--green-primary); border-radius: var(--border-radius-md); color: #2e7d32; font-size: 14px; font-weight: 500; text-align: center; }
.auth-screen__submit { margin-top: 8px; }
.auth-screen__spinner { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity var(--transition-slow), transform var(--transition-slow); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(20px); }
.auth-screen__mt { margin-top: 10px; }

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
