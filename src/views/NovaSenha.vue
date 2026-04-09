<template>
  <div class="auth-screen">
    <Transition name="fade" appear>
      <div class="auth-screen__container">
        
        <!-- Cabeçalho com a nova Logo_login Flutuante -->
        <div class="auth-screen__header">
          <div class="auth-screen__logo-wrapper">
            <img src="@/assets/logo_login.png" alt="ProvaPop! Logo" class="auth-screen__logo" />
          </div>
          <p class="auth-screen__subtitle">Quase lá! Crie sua nova senha secreta...</p>
        </div>

        <Card variant="elevated" class="auth-screen__card">
          <!-- Bloco de Sucesso Premium -->
          <div v-if="success" class="auth-screen__success">
            <div class="auth-screen__success-icon">
              <font-awesome-icon icon="check-circle" />
            </div>
            <h3>Tudo certo!</h3>
            <p>Sua senha foi alterada com sucesso. O palco é todo seu novamente.</p>
            <button @click="goToLogin" class="auth-screen__submit-btn auth-screen__mt">
              Ir para o Login
            </button>
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
              <font-awesome-icon icon="exclamation-circle" />
              {{ error }}
            </div>

            <!-- Botão Master -->
            <div class="auth-screen__action">
              <button
                type="submit"
                :disabled="loading"
                class="auth-screen__submit-btn"
              >
                <font-awesome-icon v-if="loading" icon="circle-notch" class="auth-screen__spinner" />
                {{ loading ? 'Afinando...' : 'Salvar Nova Senha' }}
              </button>
            </div>
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
/* O SEGREDO DO FUNDO: Branco no topo, descendo para tom terroso */
.auth-screen { 
  min-height: 100vh; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  padding: 20px; 
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.auth-screen__container { 
  width: 100%; 
  max-width: 420px; 
  z-index: 10;
}

.auth-screen__header { 
  text-align: center; 
  margin-bottom: 24px; 
}

.auth-screen__logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

/* Animação da logo */
.auth-screen__logo {
  max-width: 240px;
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.auth-screen__subtitle { 
  font-size: 18px;
  font-weight: 600;
  color: #8B1E3F; /* Vinho */
  margin: 0;
  letter-spacing: -0.3px;
}

.auth-screen__card { 
  padding: 32px 24px; 
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.auth-screen__form { 
  display: flex; 
  flex-direction: column; 
  gap: 20px; 
}

.auth-screen__field { 
  display: flex; 
  flex-direction: column; 
  gap: 8px; 
}

.auth-screen__label { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  font-size: 14px; 
  font-weight: 600; 
  color: #5a4a46; 
}

.auth-screen__label-icon { 
  font-size: 15px; 
  color: #E25822; /* Laranja Terroso */
}

.auth-screen__input { 
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

.auth-screen__input:focus { 
  border-color: #8B1E3F; 
  box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1); 
  transform: translateY(-1px);
}

.auth-screen__input::placeholder {
  color: #b5a9a7;
  font-weight: 400;
}

.auth-screen__password-wrapper { 
  position: relative; 
  display: flex; 
  align-items: center; 
}

.auth-screen__password-wrapper .auth-screen__input { 
  padding-right: 50px; 
}

.auth-screen__toggle-password { 
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

.auth-screen__toggle-password:hover { 
  color: #E25822; 
  background: rgba(226, 88, 34, 0.1);
}

.auth-screen__error { 
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

/* Sucesso Premium */
.auth-screen__success { 
  display: flex; 
  flex-direction: column; 
  align-items: center;
  gap: 8px; 
  padding: 24px 16px; 
  background: #fdfaf9; 
  border: 1px solid #e8dedc; 
  border-radius: 16px; 
  text-align: center; 
}

.auth-screen__success-icon {
  font-size: 40px;
  color: #8B1E3F; /* Usa o vinho para manter a identidade */
  margin-bottom: 8px;
}

.auth-screen__success h3 {
  color: #8B1E3F;
  font-size: 20px;
  margin: 0;
  font-weight: 800;
}

.auth-screen__success p {
  color: #5a4a46;
  font-size: 14px;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.auth-screen__action {
  margin-top: 8px;
}

/* BOTÃO MASTER - Idêntico ao da tela de login */
.auth-screen__submit-btn {
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  color: #ffffff;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(226, 88, 34, 0.2);
}

.auth-screen__submit-btn:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 10px 25px rgba(139, 30, 63, 0.3);
}

.auth-screen__submit-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.auth-screen__submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-screen__mt { margin-top: 16px; }
.auth-screen__spinner { animation: spin 1s linear infinite; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(20px); }

@media (min-width: 768px) {
  .auth-screen { padding: 24px; }
  .auth-screen__container { max-width: 440px; }
  .auth-screen__header { margin-bottom: 32px; }
  .auth-screen__card { padding: 48px 40px; }
  .auth-screen__input { padding: 14px 16px; font-size: 16px; }
  .auth-screen__logo { max-width: 280px; }
}
</style>
