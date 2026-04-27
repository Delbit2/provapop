<template>
  <div class="login">
    <Transition name="fade" appear>
      <div class="login__container">
        <div class="login__header">
          <div class="login__logo-wrapper">
            <img src="@/assets/logo_login.png" alt="ProvaPop! Logo" class="login__logo" />
          </div>
          <p class="login__subtitle">Estude no seu ritmo...</p>
        </div>

        <Card variant="elevated" class="login__card">
          <div class="login__welcome-text">
            <h3>Pronto para o desafio?</h3>
          </div>

          <form @submit.prevent="handleLogin" class="login__form">
            <div class="login__field">
              <label class="login__label">
                <font-awesome-icon icon="envelope" class="login__label-icon" />
                Seu E-mail
              </label>
              <input
                v-model.trim="form.email"
                type="email"
                class="login__input"
                placeholder="ex: futuro.calouro@email.com"
                autocomplete="email"
                required
              />
            </div>

            <div class="login__field">
              <label class="login__label">
                <font-awesome-icon icon="lock" class="login__label-icon" />
                Sua Senha Secreta
              </label>
              <div class="login__password-wrapper">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="login__input"
                  placeholder="••••••••"
                  autocomplete="current-password"
                  required
                />
                <button
                  type="button"
                  class="login__toggle-password"
                  @click="showPassword = !showPassword"
                >
                  <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
                </button>
              </div>
            </div>

            <div class="login__options">
              <label class="login__checkbox">
                <input type="checkbox" v-model="form.remember" />
                <span>Lembrar meu acesso</span>
              </label>
              <a href="#" @click.prevent="goToForgot" class="login__forgot">Esqueceu a senha?</a>
            </div>

            <div v-if="errorMessage" class="login__error">
              <font-awesome-icon icon="exclamation-circle" />
              {{ errorMessage }}
            </div>

            <div class="login__action">
              <button
                type="submit"
                :disabled="loading"
                class="login__submit-btn"
              >
                <font-awesome-icon v-if="loading" icon="circle-notch" class="login__spinner" />
                {{ loading ? 'Afinando...' : 'Play!' }}
              </button>
            </div>
          </form>

          <div class="login__footer">
            <p>
              Primeira vez no palco?
              <a href="#" @click.prevent="goToRegister" class="login__link">Crie sua conta VIP</a>
            </p>
          </div>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Card from '@/components/Card.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember: false,
})

const showPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  if (!authStore.authInitialized) {
    await authStore.initAuth()
  }

  if (authStore.isAuthenticated) {
    const redirectTo =
      typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
        ? route.query.redirect
        : '/'

    router.replace(redirectTo)
  }
})

async function handleLogin() {
  try {
    loading.value = true
    errorMessage.value = ''

    const email = form.value.email.trim().toLowerCase()
    const password = form.value.password

    if (!email || !password) {
      errorMessage.value = 'Preencha e-mail e senha.'
      return
    }

    await authStore.login(email, password)

    const redirectTo =
      typeof route.query.redirect === 'string' && route.query.redirect.startsWith('/')
        ? route.query.redirect
        : '/'

    router.push(redirectTo)
  } catch (error: any) {
    console.error('Login error:', error)
    errorMessage.value =
      authStore.error || 'Erro inesperado de conexão. Verifique sua internet.'
  } finally {
    loading.value = false
  }
}

function goToForgot() {
  router.push('/esqueci-senha')
}

function goToRegister() {
  router.push('/register')
}
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.login__container {
  width: 100%;
  max-width: 420px;
  z-index: 10;
}

.login__header {
  text-align: center;
  margin-bottom: 24px;
}

.login__logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.login__logo {
  max-width: 240px;
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.login__subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #8B1E3F;
  margin: 0;
  letter-spacing: -0.3px;
}

.login__welcome-text {
  text-align: center;
  margin-bottom: 28px;
}

.login__welcome-text h3 {
  font-size: 22px;
  font-weight: 800;
  color: #8B1E3F;
  margin: 0;
}

.login__card {
  padding: 32px 24px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.login__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.login__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #5a4a46;
}

.login__label-icon {
  font-size: 15px;
  color: #E25822;
}

.login__input {
  width: 100%;
  padding: 14px 16px;
  font-size: 15px;
  border: 2px solid #e8dedc;
  border-radius: 12px;
  background: #ffffff;
  color: #2d2422;
  transition: all 0.3s ease;
  font-family: inherit;
  outline: none;
}

.login__input:focus {
  border-color: #8B1E3F;
  box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1);
  transform: translateY(-1px);
}

.login__input::placeholder {
  color: #b5a9a7;
  font-weight: 400;
}

.login__password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.login__password-wrapper .login__input {
  padding-right: 50px;
}

.login__toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #b5a9a7;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.login__toggle-password:hover {
  color: #E25822;
  background: rgba(226, 88, 34, 0.1);
}

.login__options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13.5px;
  margin-top: 4px;
}

.login__checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #5a4a46;
  font-weight: 500;
}

.login__checkbox input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #E25822;
  border-radius: 4px;
}

.login__forgot {
  color: #E25822;
  text-decoration: none;
  font-weight: 700;
  transition: all 0.3s ease;
}

.login__forgot:hover {
  color: #8B1E3F;
  text-decoration: underline;
}

.login__error {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #fdf2f2;
  border: 1px solid #e27d72;
  border-radius: 12px;
  color: #d13d3d;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 4px;
}

.login__action {
  margin-top: 8px;
}

.login__submit-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  color: #ffffff;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(226, 88, 34, 0.2);
}

.login__submit-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 10px 25px rgba(139, 30, 63, 0.3);
}

.login__submit-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.login__submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.login__footer {
  text-align: center;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid #e8dedc;
  font-size: 14px;
  color: #5a4a46;
}

.login__link {
  color: #E25822;
  text-decoration: none;
  font-weight: 800;
  transition: color 0.3s ease;
  margin-left: 4px;
}

.login__link:hover {
  color: #8B1E3F;
  text-decoration: underline;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@media (min-width: 768px) {
  .login__card {
    padding: 48px 40px;
  }

  .login__logo {
    max-width: 280px;
  }
}
</style>
