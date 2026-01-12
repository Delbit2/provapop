<template>
  <div class="login">
    <Transition name="fade" appear>
      <div class="login__container">
        <div class="login__header">
          <h1 class="login__title">Quiz Musical</h1>
          <p class="login__subtitle">Entre para começar a estudar</p>
        </div>

        <Card variant="elevated" class="login__card">
          <form @submit.prevent="handleLogin" class="login__form">
            <div class="login__field">
              <label class="login__label">
                <font-awesome-icon icon="user" class="login__label-icon" />
                Email ou Usuário
              </label>
              <input
                v-model="form.email"
                type="text"
                class="login__input"
                placeholder="Digite seu email ou usuário"
                required
              />
            </div>

            <div class="login__field">
              <label class="login__label">
                <font-awesome-icon icon="lock" class="login__label-icon" />
                Senha
              </label>
              <div class="login__password-wrapper">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="login__input"
                  placeholder="Digite sua senha"
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
                <span>Lembrar-me</span>
              </label>
              <a href="#" class="login__forgot">Esqueci minha senha</a>
            </div>

            <div v-if="authStore.error" class="login__error">
              {{ authStore.error }}
            </div>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              full-width
              :disabled="authStore.loading"
              class="login__submit"
            >
              <font-awesome-icon v-if="authStore.loading" icon="circle-notch" class="login__spinner" />
              {{ authStore.loading ? 'Entrando...' : 'Entrar' }}
            </Button>
          </form>

          <div class="login__footer">
            <p>Não tem uma conta? <a href="#" @click.prevent="goToRegister" class="login__link">Cadastre-se</a></p>
          </div>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember: false
})

const showPassword = ref(false)

async function handleLogin() {
  try {
    await authStore.login(form.value.email, form.value.password)
  } catch (error) {
    console.error('Login error:', error)
  }
}

function goToRegister() {
  router.push('/register')
}

import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.login__container {
  width: 100%;
  max-width: 100%;
}

.login__header {
  text-align: center;
  margin-bottom: 24px;
}

.login__title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login__subtitle {
  font-size: 14px;
  color: var(--black-soft);
  margin: 0;
}

.login__card {
  padding: 24px;
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
  color: var(--black-soft);
}

.login__label-icon {
  font-size: 14px;
  color: var(--green-primary);
}

.login__input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  border: 2px solid var(--gray-light);
  border-radius: var(--border-radius-full);
  background: var(--white);
  color: var(--black-soft);
  transition: all var(--transition-base);
  font-family: inherit;
  outline: none;
}

.login__input:focus {
  border-color: var(--green-primary);
  box-shadow: 0 0 0 3px var(--green-pastel);
}

.login__input::placeholder {
  color: var(--gray);
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
  right: 16px;
  background: none;
  border: none;
  color: var(--gray-dark);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--transition-base);
}

.login__toggle-password:hover {
  color: var(--green-primary);
}

.login__options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  font-size: 13px;
}

.login__checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: var(--black-soft);
}

.login__checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--green-primary);
}

.login__forgot {
  color: var(--green-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-base);
}

.login__forgot:hover {
  color: var(--green-dark);
  text-decoration: underline;
}

.login__error {
  padding: 12px;
  background: var(--yellow-pastel);
  border: 2px solid var(--yellow-primary);
  border-radius: var(--border-radius-md);
  color: var(--yellow-dark);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
  text-align: center;
}

.login__submit {
  margin-top: 8px;
}

.login__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.login__footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid var(--gray-light);
  font-size: 13px;
  color: var(--black-soft);
}

@media (min-width: 768px) {
  .login {
    padding: 24px;
  }

  .login__container {
    max-width: 440px;
  }

  .login__header {
    margin-bottom: 32px;
  }

  .login__title {
    font-size: 48px;
  }

  .login__subtitle {
    font-size: 16px;
  }

  .login__card {
    padding: 40px;
  }

  .login__form {
    gap: 24px;
  }

  .login__input {
    padding: 14px 16px;
    font-size: 16px;
  }

  .login__options {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
  }

  .login__footer {
    padding-top: 24px;
    font-size: 14px;
  }
}

.login__link {
  color: var(--green-primary);
  text-decoration: none;
  font-weight: 600;
  transition: color var(--transition-base);
}

.login__link:hover {
  color: var(--green-dark);
  text-decoration: underline;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-slow), transform var(--transition-slow);
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>