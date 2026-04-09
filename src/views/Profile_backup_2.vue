<template>
  <div class="profile">
    <div class="profile__container">
      <Transition name="fade" appear>
        <div class="profile__content">
          <div class="profile__header">
            <button class="profile__back-btn" @click="goBack" title="Voltar">
              <font-awesome-icon icon="arrow-left" />
            </button>
            <div class="profile__header-content">
              <h1 class="profile__title">Meu Perfil</h1>
              <p class="profile__subtitle">Área VIP • Gerencie seus dados</p>
            </div>
          </div>

          <Card variant="elevated" class="profile__card">
            <div class="profile__avatar-section">
              <div class="profile__avatar">
                <font-awesome-icon icon="user" class="profile__avatar-icon" />
              </div>
            </div>

            <div class="profile__info-section">
              <div class="profile__info-item">
                <font-awesome-icon icon="user" class="profile__info-icon" />
                <div class="profile__info-content">
                  <!-- Alterado para Nome Artístico -->
                  <div class="profile__info-label">Nome Artístico</div>
                  <div class="profile__info-value">{{ form.nickname || 'Carregando...' }}</div>
                </div>
              </div>
            </div>

            <div v-if="error" class="profile__message profile__message--error">
              <font-awesome-icon icon="exclamation-circle" />
              {{ error }}
            </div>

            <div v-if="success" class="profile__message profile__message--success">
              <font-awesome-icon icon="check-circle" />
              {{ success }}
            </div>

            <form @submit.prevent="handleSave" class="profile__form">
              <div class="profile__field">
                <label class="profile__label">
                  <font-awesome-icon icon="envelope" class="profile__label-icon" />
                  E-mail
                </label>
                <input
                  v-model="form.email"
                  type="email"
                  class="profile__input"
                  placeholder="ex: futuro.calouro@email.com"
                  required
                />
                <p class="profile__hint">Usado para seu acesso VIP e recuperação</p>
              </div>

              <div class="profile__field">
                <label class="profile__label">
                  <font-awesome-icon icon="lock" class="profile__label-icon" />
                  Nova Senha Secreta
                </label>
                <div class="profile__password-wrapper">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="profile__input"
                    placeholder="Deixe em branco para manter a atual"
                    :minlength="6"
                  />
                  <button
                    type="button"
                    class="profile__toggle-password"
                    @click="showPassword = !showPassword"
                  >
                    <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'" />
                  </button>
                </div>
                <p class="profile__hint">Mínimo de 6 caracteres</p>
              </div>

              <div class="profile__actions">
                <!-- Botão Salvar apenas em Laranja -->
                <button
                  type="submit"
                  :disabled="loading || !hasChanges"
                  class="profile__save-btn"
                >
                  <font-awesome-icon v-if="loading" icon="circle-notch" class="profile__spinner" />
                  {{ loading ? 'Afinando...' : 'Salvar' }}
                </button>
                <button
                  type="button"
                  @click="handleCancel"
                  :disabled="loading"
                  class="profile__cancel-btn"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </Card>

          <Card variant="outlined" class="profile__stats">
            <!-- Título atualizado para "No Holofote" -->
            <h2 class="profile__stats-title">No Holofote</h2>
            <div v-if="loadingStats" class="profile__stats-loading">
              <font-awesome-icon icon="circle-notch" class="profile__spinner" />
              Buscando dados...
            </div>
            <div v-else class="profile__stats-grid">
              <div class="profile__stat-item">
                <div class="profile__stat-value">{{ stats.totalQuizzes }}</div>
                <div class="profile__stat-label">Desafios Completos</div>
              </div>
              <div class="profile__stat-item">
                <div class="profile__stat-value">{{ stats.totalQuizzes > 0 ? stats.accuracy.toFixed(1) : '0.0' }}%</div>
                <div class="profile__stat-label">Taxa de Acerto</div>
              </div>
              <div class="profile__stat-item">
                <div class="profile__stat-value">{{ stats.position > 0 ? `#${stats.position}` : '--' }}</div>
                <div class="profile__stat-label">Posição no Ranking</div>
              </div>
            </div>
          </Card>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  nickname: '',
  email: '',
  password: ''
})

const originalForm = ref({
  email: '',
  password: ''
})

const stats = ref({
  totalQuizzes: 0,
  accuracy: 0,
  position: 0
})

const loading = ref(false)
const loadingStats = ref(false)
const showPassword = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

const hasChanges = computed(() => {
  return form.value.email !== originalForm.value.email ||
         (form.value.password !== '' && form.value.password.length >= 6)
})

async function loadUserData() {
  loading.value = true
  error.value = null
  
  try {
    const userData = await api.auth.me()
    if (userData.user) {
      form.value.nickname = userData.user.nickname || ''
      form.value.email = userData.user.email || ''
      originalForm.value.email = userData.user.email || ''
      
      authStore.user = userData.user
    }
  } catch (err: any) {
    if (!err.message?.includes('Sessão expirada') && 
        !err.message?.includes('Acesso negado') &&
        !err.message?.includes('Erro de conexão')) {
      error.value = err.message || 'Erro ao carregar dados do usuário'
    }
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  loadingStats.value = true
  
  try {
    const statsData = await api.users.getStats()
    stats.value.totalQuizzes = statsData.total_quizzes || 0
    stats.value.accuracy = statsData.accuracy || 0
    
    try {
      const rankingData = await api.ranking.get('all')
      if (rankingData && Array.isArray(rankingData)) {
        const currentUser = rankingData.find((r: any) => r.user_id === authStore.user?.id)
        if (currentUser && currentUser.position) {
          stats.value.position = currentUser.position
        } else {
          stats.value.position = 0
        }
      } else {
        stats.value.position = 0
      }
    } catch (rankingErr: any) {
      console.error('Erro ao carregar ranking:', rankingErr)
      stats.value.position = 0
    }
  } catch (err: any) {
    console.error('Erro ao carregar estatísticas:', err)
    stats.value.totalQuizzes = 0
    stats.value.accuracy = 0
    stats.value.position = 0
  } finally {
    loadingStats.value = false
  }
}

async function handleSave() {
  loading.value = true
  error.value = null
  success.value = null
  
  try {
    const updateData: { email?: string; password?: string } = {}
    
    if (form.value.email !== originalForm.value.email) {
      updateData.email = form.value.email
    }
    
    if (form.value.password && form.value.password.length >= 6) {
      updateData.password = form.value.password
    }
    
    if (Object.keys(updateData).length === 0) {
      error.value = 'Nenhuma alteração para salvar'
      loading.value = false
      return
    }
    
    const response = await api.users.updateProfile(updateData)
    
    if (response.user) {
      originalForm.value.email = response.user.email || form.value.email
      form.value.email = response.user.email || form.value.email
      form.value.password = ''
      
      authStore.user = response.user
      success.value = 'Conta VIP atualizada com sucesso!'
      
      setTimeout(() => {
        success.value = null
      }, 3000)
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao atualizar perfil'
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  form.value.email = originalForm.value.email
  form.value.password = ''
  error.value = null
  success.value = null
}

function goBack() {
  router.push('/')
}

onMounted(async () => {
  if (authStore.user) {
    form.value.nickname = authStore.user.nickname || ''
    form.value.email = authStore.user.email || ''
    originalForm.value.email = authStore.user.email || ''
  }
  
  await loadUserData()
  await loadStats()
})
</script>

<style scoped>
.profile {
  min-height: 100vh;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.profile__container {
  max-width: 100%;
  margin: 0 auto;
  z-index: 10;
  position: relative;
}

.profile__content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile__header {
  text-align: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.profile__back-btn {
  position: absolute;
  left: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #8B1E3F;
  color: #ffffff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 10px rgba(139, 30, 63, 0.2);
  font-size: 18px;
}

.profile__back-btn:hover {
  background: #E25822;
  transform: scale(1.05) translateX(-2px);
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.3);
}

.profile__back-btn:active {
  transform: scale(0.95);
}

.profile__header-content {
  text-align: center;
}

.profile__title {
  font-size: 32px;
  font-weight: 800;
  color: #8B1E3F;
  margin: 0 0 4px 0;
}

.profile__subtitle {
  font-size: 14px;
  font-weight: 500;
  color: #5a4a46;
  margin: 0;
}

.profile__card {
  padding: 32px 24px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.profile__avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 28px;
  position: relative;
}

.profile__avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(226, 88, 34, 0.2);
  border: 4px solid #ffffff;
}

.profile__avatar-icon {
  font-size: 44px;
  color: #ffffff;
}

.profile__info-section {
  margin-bottom: 28px;
  padding: 16px 20px;
  background: #fdfaf9;
  border-radius: 16px;
  border: 1px solid #e8dedc;
}

.profile__info-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.profile__info-icon {
  font-size: 24px;
  color: #E25822;
  flex-shrink: 0;
}

.profile__info-content {
  flex: 1;
  min-width: 0;
}

.profile__info-label {
  font-size: 12px;
  color: #b5a9a7;
  font-weight: 600;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile__info-value {
  font-size: 18px;
  color: #8B1E3F;
  font-weight: 800;
  word-wrap: break-word;
}

.profile__form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile__field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile__label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #5a4a46;
}

.profile__label-icon {
  font-size: 15px;
  color: #E25822;
}

.profile__input {
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

.profile__input:focus {
  border-color: #8B1E3F;
  box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1);
  transform: translateY(-1px);
}

.profile__input::placeholder {
  color: #b5a9a7;
  font-weight: 400;
}

.profile__password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.profile__password-wrapper .profile__input {
  padding-right: 50px;
}

.profile__toggle-password {
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

.profile__toggle-password:hover {
  color: #E25822;
  background: rgba(226, 88, 34, 0.1);
}

.profile__hint {
  font-size: 12px;
  color: #b5a9a7;
  margin: 0;
  font-weight: 500;
}

.profile__message {
  padding: 14px 16px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
}

.profile__message--error {
  background: #fdf2f2;
  border: 1px solid #e27d72;
  color: #d13d3d;
}

.profile__message--success {
  background: #fdfaf9;
  border: 1px solid #e8dedc;
  color: #8B1E3F; 
}

.profile__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

/* Botão Salvar apenas na cor Laranja Terroso */
.profile__save-btn {
  order: 1;
  width: 100%;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: #E25822;
  color: #ffffff;
  font-size: 16px;
  font-weight: 800;
  letter-spacing: 0.5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(226, 88, 34, 0.3);
}

.profile__save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(226, 88, 34, 0.4);
}

.profile__save-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.profile__save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.profile__cancel-btn {
  order: 2;
  width: 100%;
  padding: 14px;
  border: 2px solid #e8dedc;
  border-radius: 12px;
  background: transparent;
  color: #5a4a46;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.profile__cancel-btn:hover:not(:disabled) {
  border-color: #E25822;
  color: #E25822;
  background: rgba(226, 88, 34, 0.05);
}

.profile__cancel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.profile__spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.profile__stats {
  padding: 24px;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.profile__stats-title {
  font-size: 18px;
  font-weight: 800;
  color: #8B1E3F;
  margin: 0 0 20px 0;
  text-align: center;
}

.profile__stats-loading {
  text-align: center;
  padding: 20px;
  color: #b5a9a7;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.profile__stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.profile__stat-item {
  text-align: center;
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e8dedc;
  transition: transform 0.3s ease;
}

.profile__stat-item:hover {
  transform: translateY(-2px);
  border-color: #E25822;
  box-shadow: 0 4px 12px rgba(226, 88, 34, 0.08);
}

.profile__stat-value {
  font-size: 26px;
  font-weight: 900;
  color: #E25822; 
  margin-bottom: 4px;
  letter-spacing: -0.5px;
}

.profile__stat-label {
  font-size: 12px;
  color: #5a4a46;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

@media (min-width: 640px) {
  .profile__stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .profile__stat-value { font-size: 30px; }
  .profile__stat-label { font-size: 11px; }
}

@media (min-width: 768px) {
  .profile { padding: 32px; }
  .profile__container { max-width: 600px; }
  .profile__content { gap: 32px; }
  .profile__title { font-size: 36px; }
  .profile__subtitle { font-size: 16px; }
  .profile__card { padding: 48px; }
  .profile__avatar-section { margin-bottom: 32px; }
  .profile__avatar { width: 120px; height: 120px; }
  .profile__avatar-icon { font-size: 52px; }
  .profile__info-section { margin-bottom: 32px; padding: 20px 24px; }
  .profile__info-icon { font-size: 28px; }
  .profile__form { gap: 24px; }
  .profile__input { padding: 16px 18px; font-size: 16px; }
  .profile__stats { padding: 32px; }
  .profile__stats-title { font-size: 20px; margin-bottom: 24px; }
  .profile__back-btn { width: 48px; height: 48px; font-size: 20px; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.6s cubic-bezier(0.4, 0, 0.2, 1), transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from { opacity: 0; transform: translateY(20px); }
.fade-leave-to { opacity: 0; transform: translateY(-20px); }
</style>
