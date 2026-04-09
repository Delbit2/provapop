<template>
  <div class="forgot">
    <Transition name="fade" appear>
      <div class="forgot__container">
        
        <!-- Cabeçalho -->
        <div class="forgot__header">
          <div class="forgot__logo-wrapper">
            <img src="@/assets/logo_login.png" alt="ProvaPop! Logo" class="forgot__logo" />
          </div>
          <p class="forgot__subtitle">Calma, a gente te ajuda...</p>
        </div>

        <Card variant="elevated" class="forgot__card">
          <div class="forgot__welcome-text">
            <h3>Recuperar Senha</h3>
          </div>

          <!-- Mensagem de Sucesso -->
          <div v-if="success" class="forgot__success">
            <font-awesome-icon icon="check-circle" class="forgot__success-icon"></font-awesome-icon>
            <p>E-mail de recuperação enviado! Verifique sua caixa de entrada (e spam).</p>
          </div>
          
          <!-- Formulário -->
          <form v-else @submit.prevent="handleForgot" class="forgot__form">
            <p class="forgot__text">Digite o e-mail cadastrado e enviaremos um link para você redefinir sua senha.</p>
            
            <div class="forgot__field">
              <label class="forgot__label">
                <font-awesome-icon icon="envelope" class="forgot__label-icon"></font-awesome-icon>
                Seu E-mail
              </label>
              <input
                v-model="email"
                type="email"
                class="forgot__input"
                placeholder="ex: futuro.calouro@email.com"
                required
              />
            </div>

            <div v-if="error" class="forgot__error">
              <font-awesome-icon icon="exclamation-circle"></font-awesome-icon>
              {{ error }}
            </div>

            <!-- Botão de Ação -->
            <div class="forgot__action">
              <button
                type="submit"
                :disabled="loading"
                class="forgot__submit-btn"
              >
                <font-awesome-icon v-if="loading" icon="circle-notch" class="forgot__spinner"></font-awesome-icon>
                {{ loading ? 'Enviando...' : 'Enviar Link' }}
              </button>
            </div>
          </form>

          <div class="forgot__footer">
            <p>Lembrou a senha? <a href="#" @click.prevent="goToLogin" class="forgot__link">Voltar para o palco</a></p>
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

const router = useRouter()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleForgot() {
  loading.value = true
  error.value = ''
  
  try {
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
  router.push('/login')
}
</script>

<style scoped>
.forgot {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.forgot__container {
  width: 100%;
  max-width: 420px;
  z-index: 10;
}

.forgot__header {
  text-align: center;
  margin-bottom: 24px;
}

.forgot__logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.forgot__logo {
  max-width: 240px;
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.forgot__subtitle {
  font-size: 18px;
  font-weight: 600;
  color: #8B1E3F;
  margin: 0;
  letter-spacing: -0.3px;
}

.forgot__welcome-text {
  text-align: center;
  margin-bottom: 16px;
}

.forgot__welcome-text h3 {
  font-size: 22px;
  font-weight: 800;
  color: #8B1E3F;
  margin: 0;
}

.forgot__text {
  font-size: 14px;
  color: #5a4a46;
  margin-bottom: 24px;
  text-align: center;
  line-height: 1.5;
}

.forgot__card {
  padding: 32px 24px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.forgot__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.forgot__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.forgot__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #5a4a46;
}

.forgot__label-icon {
  font-size: 15px;
  color: #E25822; 
}

.forgot__input {
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

.forgot__input:focus {
  border-color: #8B1E3F;
  box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1);
  transform: translateY(-1px);
}

.forgot__input::placeholder {
  color: #b5a9a7;
  font-weight: 400;
}

.forgot__error {
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

.forgot__success {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: #f6fcf8;
  border: 2px solid #84dcc6;
  border-radius: 16px;
  color: #2b7a65;
  text-align: center;
}

.forgot__success-icon {
  font-size: 32px;
  color: #84dcc6;
}

.forgot__success p {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.5;
}

.forgot__action {
  margin-top: 8px;
}

.forgot__submit-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(226, 88, 34, 0.2);
}

.forgot__submit-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 10px 25px rgba(139, 30, 63, 0.3);
}

.forgot__submit-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.forgot__submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.forgot__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.forgot__footer {
  text-align: center;
  padding-top: 24px;
  margin-top: 24px;
  border-top: 1px solid #e8dedc;
  font-size: 14px;
  color: #5a4a46;
}

.forgot__link {
  color: #E25822;
  text-decoration: none;
  font-weight: 800;
  transition: color 0.3s ease;
  margin-left: 4px;
}

.forgot__link:hover {
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
  .forgot__card {
    padding: 48px 40px;
  }
  
  .forgot__logo {
    max-width: 280px;
  }
}
</style>
