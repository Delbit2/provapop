<template>
  <div class="register">
    <Transition name="fade" appear>
      <div class="register__container">
        <div class="register__header">
          <h1 class="register__title">Quiz Musical</h1>
          <p class="register__subtitle">Crie sua conta e comece a estudar</p>
        </div>

        <Card variant="elevated" class="register__card">
          <form @submit.prevent="handleRegister" class="register__form">
            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="user" class="register__label-icon" />
                Apelido
              </label>
              <input
                v-model="form.nickname"
                type="text"
                class="register__input"
                placeholder="Digite seu apelido"
                required
                maxlength="20"
              />
              <p class="register__hint">Este nome será exibido no ranking</p>
            </div>

            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="envelope" class="register__label-icon" />
                Email
              </label>
              <input
                v-model="form.email"
                type="email"
                class="register__input"
                placeholder="Digite seu email"
                required
              />
            </div>

            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="lock" class="register__label-icon" />
                Senha
              </label>
              <div class="register__password-wrapper">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="register__input"
                  :class="{ 'register__input--error': passwordError }"
                  placeholder="Digite sua senha"
                  required
                  minlength="6"
                  @input="validatePassword"
                />
                <button
                  type="button"
                  class="register__toggle-password"
                  @click="showPassword = !showPassword"
                >
                  <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
                </button>
              </div>
              <p v-if="passwordError" class="register__error">{{ passwordError }}</p>
            </div>

            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="lock" class="register__label-icon" />
                Confirmar Senha
              </label>
              <div class="register__password-wrapper">
                <input
                  v-model="form.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="register__input"
                  :class="{ 'register__input--error': confirmPasswordError }"
                  placeholder="Confirme sua senha"
                  required
                  @input="validateConfirmPassword"
                />
                <button
                  type="button"
                  class="register__toggle-password"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <font-awesome-icon :icon="showConfirmPassword ? 'eye-slash' : 'eye'" />
                </button>
              </div>
              <p v-if="confirmPasswordError" class="register__error">{{ confirmPasswordError }}</p>
            </div>

            <div v-if="authStore.error" class="register__error-message">
              {{ authStore.error }}
            </div>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              full-width
              :disabled="authStore.loading || !isFormValid"
              class="register__submit"
            >
              <font-awesome-icon v-if="authStore.loading" icon="circle-notch" class="register__spinner" />
              {{ authStore.loading ? 'Criando conta...' : 'Criar Conta' }}
            </Button>
          </form>

          <div class="register__footer">
            <p>Já tem uma conta? <a href="#" @click.prevent="goToLogin" class="register__link">Fazer login</a></p>
          </div>
        </Card>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  nickname: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const passwordError = ref('')
const confirmPasswordError = ref('')

const isFormValid = computed(() => {
  return form.value.nickname.trim() !== '' &&
         form.value.email.trim() !== '' &&
         form.value.password.length >= 6 &&
         form.value.password === form.value.confirmPassword &&
         passwordError.value === '' &&
         confirmPasswordError.value === ''
})

function validatePassword() {
  if (form.value.password.length > 0 && form.value.password.length < 6) {
    passwordError.value = 'A senha deve ter no mínimo 6 caracteres'
  } else {
    passwordError.value = ''
  }
  validateConfirmPassword()
}

function validateConfirmPassword() {
  if (form.value.confirmPassword.length > 0) {
    if (form.value.password !== form.value.confirmPassword) {
      confirmPasswordError.value = 'As senhas não coincidem'
    } else {
      confirmPasswordError.value = ''
    }
  } else {
    confirmPasswordError.value = ''
  }
}

async function handleRegister() {
  if (isFormValid.value) {
    try {
      await authStore.register(form.value.nickname, form.value.email, form.value.password)
    } catch (error) {
      console.error('Register error:', error)
    }
  }
}

function goToLogin() {
  router.push('/entrar')
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.register__container {
  width: 100%;
  max-width: 100%;
}

.register__header {
  text-align: center;
  margin-bottom: 24px;
}

.register__title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register__subtitle {
  font-size: 14px;
  color: var(--black-soft);
  margin: 0;
}

.register__card {
  padding: 24px;
}

.register__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.register__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.register__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--black-soft);
}

.register__label-icon {
  font-size: 14px;
  color: var(--green-primary);
}

.register__input {
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

.register__input:focus {
  border-color: var(--green-primary);
  box-shadow: 0 0 0 3px var(--green-pastel);
}

.register__input--error {
  border-color: var(--yellow-primary);
}

.register__input--error:focus {
  border-color: var(--yellow-primary);
  box-shadow: 0 0 0 3px var(--yellow-pastel);
}

.register__input::placeholder {
  color: var(--gray);
}

.register__password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.register__password-wrapper .register__input {
  padding-right: 50px;
}

.register__toggle-password {
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

.register__toggle-password:active {
  color: var(--green-primary);
}

.register__hint {
  font-size: 12px;
  color: var(--gray-dark);
  margin: 0;
  padding-left: 22px;
}

.register__error {
  font-size: 12px;
  color: var(--yellow-dark);
  margin: 0;
  padding-left: 22px;
  font-weight: 500;
}

.register__error-message {
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

.register__submit {
  margin-top: 8px;
}

.register__spinner {
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

.register__footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid var(--gray-light);
  font-size: 13px;
  color: var(--black-soft);
}

.register__link {
  color: var(--green-primary);
  text-decoration: none;
  font-weight: 600;
  transition: color var(--transition-base);
  cursor: pointer;
}

.register__link:active {
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

@media (min-width: 768px) {
  .register {
    padding: 24px;
  }

  .register__container {
    max-width: 440px;
  }

  .register__header {
    margin-bottom: 32px;
  }

  .register__title {
    font-size: 48px;
  }

  .register__subtitle {
    font-size: 16px;
  }

  .register__card {
    padding: 40px;
  }

  .register__form {
    gap: 24px;
  }

  .register__input {
    padding: 14px 16px;
    font-size: 16px;
  }

  .register__toggle-password:hover {
    color: var(--green-primary);
  }

  .register__footer {
    padding-top: 24px;
    font-size: 14px;
  }

  .register__link:hover {
    color: var(--green-dark);
    text-decoration: underline;
  }
}
</style>