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
              <p class="profile__subtitle">Gerencie suas informações pessoais</p>
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
                  <div class="profile__info-label">Apelido</div>
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
                  Email
                </label>
                <input
                  v-model="form.email"
                  type="email"
                  class="profile__input"
                  placeholder="Digite seu email"
                  required
                />
                <p class="profile__hint">Usado para login e recuperação de senha</p>
              </div>

              <div class="profile__field">
                <label class="profile__label">
                  <font-awesome-icon icon="lock" class="profile__label-icon" />
                  Nova Senha
                </label>
                <div class="profile__password-wrapper">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="profile__input"
                    placeholder="Digite sua nova senha (mínimo 6 caracteres)"
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
                <p class="profile__hint">Deixe em branco para manter a senha atual (mínimo 6 caracteres)</p>
              </div>

              <div class="profile__actions">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  :disabled="loading || !hasChanges"
                  class="profile__save-btn"
                >
                  <font-awesome-icon v-if="loading" icon="circle-notch" class="profile__spinner" />
                  {{ loading ? 'Salvando...' : 'Salvar Alterações' }}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="md"
                  @click="handleCancel"
                  :disabled="loading"
                  class="profile__cancel-btn"
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </Card>

          <Card variant="outlined" class="profile__stats">
            <h2 class="profile__stats-title">Estatísticas</h2>
            <div v-if="loadingStats" class="profile__stats-loading">
              <font-awesome-icon icon="circle-notch" class="profile__spinner" />
              Carregando...
            </div>
            <div v-else class="profile__stats-grid">
              <div class="profile__stat-item">
                <div class="profile__stat-value">{{ stats.totalQuizzes }}</div>
                <div class="profile__stat-label">Quizzes Completos</div>
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
import Button from '@/components/Button.vue'
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
    // Se não houver usuário na resposta, o api.ts já tratou o erro 401/403
    // Não precisamos fazer nada aqui, o callback de logout já foi chamado
  } catch (err: any) {
    // Se for erro 401/403, o authStore já foi atualizado pelo api.ts
    // Não mostrar mensagem de erro de autenticação, apenas outros erros
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
    
    // Buscar posição no ranking
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
      // Ranking não requer autenticação, então apenas logar o erro
      console.error('Erro ao carregar ranking:', rankingErr)
      stats.value.position = 0
    }
  } catch (err: any) {
    // Se for erro 401/403, o authStore já foi atualizado pelo api.ts
    // Apenas resetar stats
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
      success.value = 'Perfil atualizado com sucesso!'
      
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
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.profile__container {
  max-width: 100%;
  margin: 0 auto;
}

.profile__content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile__header {
  text-align: center;
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.profile__back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--green-primary);
  color: var(--white);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
  font-size: 18px;
  margin-top: 0;
}

.profile__back-btn:hover {
  background: var(--green-dark);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.profile__back-btn:active {
  transform: scale(0.95);
  background: var(--green-dark);
}

.profile__header-content {
  flex: 1;
  text-align: center;
}

.profile__title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.profile__subtitle {
  font-size: 14px;
  color: var(--black-soft);
  margin: 0;
}

.profile__card {
  padding: 24px;
}

.profile__avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
  position: relative;
}

.profile__avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-lg);
}

.profile__avatar-icon {
  font-size: 40px;
  color: var(--white);
}

.profile__info-section {
  margin-bottom: 24px;
  padding: 16px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
  border: 2px solid var(--gray-light);
}

.profile__info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile__info-icon {
  font-size: 20px;
  color: var(--green-primary);
  flex-shrink: 0;
}

.profile__info-content {
  flex: 1;
  min-width: 0;
}

.profile__info-label {
  font-size: 11px;
  color: var(--gray-dark);
  font-weight: 500;
  margin-bottom: 4px;
}

.profile__info-value {
  font-size: 16px;
  color: var(--black-soft);
  font-weight: 600;
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
  color: var(--black-soft);
}

.profile__label-icon {
  font-size: 14px;
  color: var(--green-primary);
}

.profile__input {
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

.profile__input:focus {
  border-color: var(--green-primary);
  box-shadow: 0 0 0 3px var(--green-pastel);
}

.profile__input::placeholder {
  color: var(--gray);
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

.profile__toggle-password:hover {
  color: var(--green-primary);
}

.profile__hint {
  font-size: 12px;
  color: var(--gray-dark);
  margin: 0;
  padding-left: 22px;
}

.profile__message {
  padding: 12px 16px;
  border-radius: var(--border-radius-md);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.profile__message--error {
  background: #fee;
  color: #c33;
  border: 2px solid #fcc;
}

.profile__message--success {
  background: #efe;
  color: #3c3;
  border: 2px solid #cfc;
}

.profile__stats-loading {
  text-align: center;
  padding: 20px;
  color: var(--gray-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.profile__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.profile__save-btn {
  order: 1;
}

.profile__cancel-btn {
  order: 2;
}

.profile__spinner {
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

.profile__stats {
  padding: 20px;
}

.profile__stats-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--green-dark);
  margin: 0 0 16px 0;
  text-align: center;
}

.profile__stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.profile__stat-item {
  text-align: center;
  padding: 16px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
}

.profile__stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--green-primary);
  margin-bottom: 4px;
}

.profile__stat-label {
  font-size: 11px;
  color: var(--gray-dark);
  font-weight: 500;
}

@media (min-width: 640px) {
  .profile__stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
  }

  .profile__stat-value {
    font-size: 28px;
  }

  .profile__stat-label {
    font-size: 12px;
  }
}

@media (min-width: 768px) {
  .profile {
    padding: 24px;
  }

  .profile__container {
    max-width: 600px;
  }

  .profile__content {
    gap: 24px;
  }

  .profile__title {
    font-size: 40px;
  }

  .profile__subtitle {
    font-size: 16px;
  }

  .profile__card {
    padding: 40px;
  }

  .profile__avatar-section {
    margin-bottom: 32px;
  }

  .profile__avatar {
    width: 120px;
    height: 120px;
  }

  .profile__avatar-icon {
    font-size: 48px;
  }

  .profile__info-section {
    margin-bottom: 32px;
    padding: 20px;
  }

  .profile__info-item {
    gap: 16px;
  }

  .profile__info-icon {
    font-size: 24px;
  }

  .profile__info-label {
    font-size: 12px;
  }

  .profile__info-value {
    font-size: 18px;
  }

  .profile__form {
    gap: 24px;
  }

  .profile__input {
    padding: 14px 16px;
    font-size: 16px;
  }

  .profile__stats {
    padding: 24px;
  }

  .profile__stats-title {
    font-size: 20px;
    margin-bottom: 20px;
  }

  .profile__back-btn {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }
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