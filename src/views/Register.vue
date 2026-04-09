<template>
  <div class="register">
    <Transition name="fade" appear>
      <div class="register__container">
        
        <div class="register__header">
          <div class="register__logo-wrapper">
            <img src="@/assets/logo_login.png" alt="ProvaPop! Logo" class="register__logo" />
          </div>
          <p class="register__subtitle">Sua jornada começa aqui...</p>
        </div>

        <Card variant="elevated" class="register__card">
          <div class="register__welcome-text">
            <h3>Crie seu Passe VIP</h3>
          </div>

          <form @submit.prevent="handleRegister" class="register__form">
            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="user" class="register__label-icon" />
                Como quer ser chamado?
              </label>
              <input
                v-model="form.name"
                type="text"
                class="register__input"
                placeholder="ex: Fernando"
                required
              />
            </div>

            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="envelope" class="register__label-icon" />
                Seu E-mail
              </label>
              <input
                v-model="form.email"
                type="email"
                class="register__input"
                placeholder="ex: futuro.calouro@email.com"
                required
              />
            </div>

            <div class="register__field">
              <label class="register__label">
                <font-awesome-icon icon="lock" class="register__label-icon" />
                Crie uma Senha Secreta
              </label>
              <div class="register__password-wrapper">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="register__input"
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  class="register__toggle-password"
                  @click="showPassword = !showPassword"
                >
                  <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
                </button>
              </div>
            </div>

            <div v-if="authStore.error" class="register__error">
              <font-awesome-icon icon="exclamation-circle" />
              {{ authStore.error }}
            </div>

            <div class="register__action">
              <button
                type="submit"
                :disabled="authStore.loading"
                class="register__submit-btn"
              >
                <font-awesome-icon v-if="authStore.loading" icon="circle-notch" class="register__spinner" />
                {{ authStore.loading ? 'Preparando...' : 'Cadastrar!' }}
              </button>
            </div>
          </form>

          <div class="register__footer">
            <p>Já tem ingresso? <a href="#" @click.prevent="goToLogin" class="register__link">Faça Login</a></p>
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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: ''
})

const showPassword = ref(false)

async function handleRegister() {
  try {
    await authStore.register(form.value.name, form.value.email, form.value.password)
    // A store de auth normalmente redireciona após o sucesso
  } catch (error) {
    console.error('Registration error:', error)
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.register__container {
  width: 100%;
  max-width: 420px;
  z-index: 10;
}

.register__header {
  text-align: center;
  margin-bottom: 24px;
}

.register__logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.register__logo {
  max-width: 240px;
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.register__subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #8B1E3F;
  margin: 0;
  letter-spacing: -0.3px;
}

.register__welcome-text {
  text-align: center;
  margin-bottom: 28px;
}

.register__welcome-text h3 {
  font-size: 22px;
  font-weight: 800;
  color: #8B1E3F;
  margin: 0;
}

.register__card {
  padding: 32px 24px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
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
  color: #5a4a46;
}

.register__label-icon {
  font-size: 15px;
  color: #E25822; 
}

.register__input {
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

.register__input:focus {
  border-color: #8B1E3F;
  box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1);
  transform: translateY(-1px);
}

.register__input::placeholder {
  color: #b5a9a7;
  font-weight: 400;
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

.register__toggle-password:hover {
  color: #E25822;
  background: rgba(226, 88, 34, 0.1);
}

.register__error {
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

.register__action {
  margin-top: 8px;
}

.register__submit-btn {
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

.register__submit-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 10px 25px rgba(139, 30, 63, 0.3);
}

.register__submit-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.register__submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.register__footer {
  text-align: center;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid #e8dedc;
  font-size: 14px;
  color: #5a4a46;
}

.register__link {
  color: #E25822;
  text-decoration: none;
  font-weight: 800;
  transition: color 0.3s ease;
  margin-left: 4px;
}

.register__link:hover {
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
  .register__card {
    padding: 48px 40px;
  }
  .register__logo {
    max-width: 280px;
  }
}
</style>
