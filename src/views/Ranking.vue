<template>
  <div class="ranking">
    <div class="ranking__container">
      <Transition name="fade" appear>
        <div class="ranking__content">
          <div class="ranking__header">
            <button class="ranking__back-btn" @click="goBack" title="Voltar">
              <font-awesome-icon icon="arrow-left" />
            </button>
            <div class="ranking__header-content">
              <h1 class="ranking__title">Ranking</h1>
              <p class="ranking__subtitle">Top jogadores do Quiz Musical</p>
            </div>
          </div>

          <!-- Filter Tabs -->
          <div class="ranking__filters">
            <button
              v-for="filter in filters"
              :key="filter.value"
              :class="[
                'ranking__filter-btn',
                { 'ranking__filter-btn--active': selectedFilter === filter.value }
              ]"
              @click="selectedFilter = filter.value"
            >
              <font-awesome-icon :icon="filter.icon" />
              {{ filter.label }}
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="ranking__loading">
            <div class="ranking__loading-spinner"></div>
            <p>Carregando ranking...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="ranking__error">
            <font-awesome-icon icon="exclamation-triangle" class="ranking__error-icon" />
            <p>{{ error }}</p>
            <button class="ranking__retry-btn" @click="loadRanking">Tentar Novamente</button>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredRanking.length === 0" class="ranking__empty">
            <font-awesome-icon icon="trophy" class="ranking__empty-icon" />
            <p>Nenhum usuário encontrado neste período.</p>
          </div>

          <!-- Content -->
          <template v-else>
            <!-- Top 3 Podium -->
            <div class="ranking__podium">
              <div v-if="filteredRanking.length >= 2" class="ranking__podium-item ranking__podium-item--second">
                <div class="ranking__podium-medal ranking__podium-medal--silver">
                  <font-awesome-icon icon="award" />
                </div>
                <div class="ranking__podium-avatar">
                  <font-awesome-icon icon="user" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[1].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[1].total_score) }} pts</div>
              </div>

              <div v-if="filteredRanking.length >= 1" class="ranking__podium-item ranking__podium-item--first">
                <div class="ranking__podium-crown">
                  <font-awesome-icon icon="trophy" />
                </div>
                <div class="ranking__podium-medal ranking__podium-medal--gold">
                  <font-awesome-icon icon="award" />
                </div>
                <div class="ranking__podium-avatar ranking__podium-avatar--first">
                  <font-awesome-icon icon="user" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[0].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[0].total_score) }} pts</div>
              </div>

              <div v-if="filteredRanking.length >= 3" class="ranking__podium-item ranking__podium-item--third">
                <div class="ranking__podium-medal ranking__podium-medal--bronze">
                  <font-awesome-icon icon="award" />
                </div>
                <div class="ranking__podium-avatar">
                  <font-awesome-icon icon="user" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[2].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[2].total_score) }} pts</div>
              </div>
            </div>

            <!-- Ranking List -->
            <Card variant="elevated" class="ranking__list-card">
              <div class="ranking__list-header">
                <h2 class="ranking__list-title">Classificação Completa</h2>
              </div>
              <div class="ranking__list">
              <div
                v-for="(user, index) in filteredRanking"
                :key="user.user_id"
                :class="[
                  'ranking__list-item',
                  {
                    'ranking__list-item--top3': index < 3,
                    'ranking__list-item--current': user.is_current_user
                  }
                ]"
              >
                <div class="ranking__list-position">
                  <span v-if="index === 0" class="ranking__list-medal ranking__list-medal--gold">
                    <font-awesome-icon icon="award" />
                  </span>
                  <span v-else-if="index === 1" class="ranking__list-medal ranking__list-medal--silver">
                    <font-awesome-icon icon="award" />
                  </span>
                  <span v-else-if="index === 2" class="ranking__list-medal ranking__list-medal--bronze">
                    <font-awesome-icon icon="award" />
                  </span>
                  <span v-else class="ranking__list-position-number">{{ index + 1 }}º</span>
                </div>
                <div class="ranking__list-avatar">
                  <font-awesome-icon icon="user" />
                </div>
                <div class="ranking__list-info">
                  <div class="ranking__list-name">
                    {{ user.nickname }}
                    <span v-if="user.is_current_user" class="ranking__list-badge">Você</span>
                  </div>
                  <div class="ranking__list-stats">
                    <span class="ranking__list-stat">
                      <font-awesome-icon icon="check-circle" />
                      {{ user.correct_answers }} acertos
                    </span>
                    <span class="ranking__list-stat">
                      <font-awesome-icon icon="chart-line" />
                      {{ user.accuracy }}% precisão
                    </span>
                  </div>
                </div>
                <div class="ranking__list-score">
                  <div class="ranking__list-score-value">{{ formatScore(user.total_score) }}</div>
                  <div class="ranking__list-score-label">pts</div>
                </div>
              </div>
            </div>
          </Card>

          <!-- User Position Card -->
          <Card v-if="!loading && !error && filteredRanking.length > 0" variant="outlined" class="ranking__user-card">
            <div class="ranking__user-content">
              <div class="ranking__user-info">
                <div class="ranking__user-label">Sua Posição</div>
                <div class="ranking__user-position">
                  {{ currentUserPosition }}º lugar
                </div>
              </div>
              <div class="ranking__user-score">
                <div class="ranking__user-score-value">{{ formatScore(currentUserScore) }}</div>
                <div class="ranking__user-score-label">pontos</div>
              </div>
            </div>
          </Card>
          </template>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

type FilterType = 'all' | 'week' | 'month'

// Filter options
const filters = [
  { value: 'all' as FilterType, label: 'Geral', icon: 'calendar-alt' },
  { value: 'week' as FilterType, label: 'Semana', icon: 'calendar-day' },
  { value: 'month' as FilterType, label: 'Mês', icon: 'calendar' }
]

const selectedFilter = ref<FilterType>('all')
const rankingData = ref<Array<{
  is_current_user?: boolean
  user_id: number
  nickname: string
  total_quizzes: number
  correct_answers: number
  accuracy: number
  position: number
  total_score: number
}>>([])
const loading = ref(false)
const error = ref<string | null>(null)

// Load ranking data from API
async function loadRanking() {
  loading.value = true
  error.value = null
  
  try {
    console.log('Carregando ranking com filtro:', selectedFilter.value)
    console.log('Usuário atual:', authStore.user)
    
    const data = await api.ranking.get(selectedFilter.value)
    console.log('Dados recebidos da API:', data)
    console.log('Tipo dos dados:', typeof data, Array.isArray(data))
    
    if (!data) {
      console.warn('API retornou null ou undefined')
      rankingData.value = []
      return
    }
    
    if (!Array.isArray(data)) {
      console.error('Resposta não é um array:', data)
      throw new Error('Resposta inválida da API: esperado array, recebido ' + typeof data)
    }
    
    console.log('Total de usuários recebidos:', data.length)
    
    rankingData.value = data.map(user => ({
      ...user,
      is_current_user: user.user_id === authStore.user?.id
    }))
    
    console.log('Ranking processado:', rankingData.value)
    console.log('Usuário atual encontrado:', rankingData.value.find(u => u.is_current_user))
  } catch (err: any) {
    console.error('Erro completo ao carregar ranking:', err)
    console.error('Stack:', err.stack)
    error.value = err.message || 'Erro ao carregar ranking. Tente novamente.'
  } finally {
    loading.value = false
  }
}

// Watch for filter changes and reload data
watch(selectedFilter, () => {
  loadRanking()
})

// Load data on mount
onMounted(() => {
  loadRanking()
})

// Filtered ranking (already filtered by API, but we add is_current_user flag)
const filteredRanking = computed(() => {
  console.log('Computing filteredRanking, rankingData.value:', rankingData.value)
  const result = rankingData.value.map(user => ({
    ...user,
    is_current_user: user.user_id === authStore.user?.id
  }))
  console.log('Filtered ranking result:', result)
  return result
})

const currentUserPosition = computed(() => {
  const currentUser = filteredRanking.value.find(user => user.is_current_user)
  if (!currentUser) return filteredRanking.value.length + 1
  return currentUser.position
})

const currentUserScore = computed(() => {
  const currentUser = filteredRanking.value.find(user => user.is_current_user)
  return currentUser?.total_score || 0
})

function formatScore(score: number): string {
  return score.toLocaleString('pt-BR')
}

function goBack() {
  router.push('/')
}
</script>

<style scoped>
.ranking {
  min-height: 100vh;
  padding: 16px;
  background: var(--white);
}

.ranking__container {
  max-width: 100%;
  margin: 0 auto;
}

.ranking__content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ranking__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.ranking__back-btn {
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
}

.ranking__back-btn:active {
  transform: scale(0.95);
  background: var(--green-dark);
}

.ranking__header-content {
  flex: 1;
}

.ranking__title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.ranking__subtitle {
  font-size: 14px;
  color: var(--gray-dark);
  margin: 0;
}

/* Filter Styles */
.ranking__filters {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.ranking__filter-btn {
  flex: 1;
  min-width: 100px;
  padding: 12px 16px;
  background: var(--white);
  border: 2px solid var(--gray-light);
  border-radius: var(--border-radius-md);
  color: var(--gray-dark);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.ranking__filter-btn:hover {
  border-color: var(--green-primary);
  color: var(--green-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.ranking__filter-btn--active {
  background: var(--green-primary);
  border-color: var(--green-primary);
  color: var(--white);
  box-shadow: var(--shadow-md);
}

.ranking__filter-btn--active:hover {
  background: var(--green-dark);
  border-color: var(--green-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.ranking__filter-btn svg {
  font-size: 14px;
}

/* Loading, Error, Empty States */
.ranking__loading,
.ranking__error,
.ranking__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.ranking__loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--gray-light);
  border-top-color: var(--green-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.ranking__loading p,
.ranking__error p,
.ranking__empty p {
  font-size: 16px;
  color: var(--gray-dark);
  margin: 0;
}

.ranking__error-icon,
.ranking__empty-icon {
  font-size: 48px;
  color: var(--gray);
  margin-bottom: 16px;
}

.ranking__error-icon {
  color: var(--yellow-primary);
}

.ranking__empty-icon {
  color: var(--green-primary);
  opacity: 0.5;
}

.ranking__retry-btn {
  margin-top: 16px;
  padding: 12px 24px;
  background: var(--green-primary);
  color: var(--white);
  border: none;
  border-radius: var(--border-radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
}

.ranking__retry-btn:hover {
  background: var(--green-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.ranking__retry-btn:active {
  transform: translateY(0);
}

/* Podium Styles */
.ranking__podium {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 8px;
  margin-bottom: 24px;
  padding: 0 8px;
}

.ranking__podium-item {
  flex: 1;
  max-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 12px;
  background: var(--white);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  position: relative;
}

.ranking__podium-item--first {
  order: 2;
  padding-bottom: 24px;
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  transform: scale(1.1);
  z-index: 2;
}

.ranking__podium-item--second {
  order: 1;
  padding-bottom: 20px;
  background: linear-gradient(135deg, #C0C0C0 0%, #A0A0A0 100%);
}

.ranking__podium-item--third {
  order: 3;
  padding-bottom: 18px;
  background: linear-gradient(135deg, #CD7F32 0%, #A0522D 100%);
}

.ranking__podium-crown {
  position: absolute;
  top: -20px;
  font-size: 32px;
  color: #FFD700;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.ranking__podium-medal {
  font-size: 24px;
  margin-bottom: 8px;
}

.ranking__podium-medal--gold {
  color: #FFD700;
}

.ranking__podium-medal--silver {
  color: #C0C0C0;
}

.ranking__podium-medal--bronze {
  color: #CD7F32;
}

.ranking__podium-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 8px;
  border: 3px solid rgba(255, 255, 255, 0.5);
}

.ranking__podium-avatar--first {
  width: 64px;
  height: 64px;
  font-size: 28px;
  border-width: 4px;
}

.ranking__podium-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--white);
  text-align: center;
  margin-bottom: 4px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

.ranking__podium-score {
  font-size: 16px;
  font-weight: 700;
  color: var(--white);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* List Styles */
.ranking__list-card {
  padding: 20px;
  margin-bottom: 16px;
}

.ranking__list-header {
  margin-bottom: 16px;
}

.ranking__list-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--green-dark);
  margin: 0;
}

.ranking__list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking__list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--white);
  border: 2px solid var(--gray-light);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-base);
}

.ranking__list-item--top3 {
  background: linear-gradient(135deg, var(--green-pastel) 0%, var(--yellow-pastel) 100%);
  border-color: var(--green-primary);
}

.ranking__list-item--current {
  border-color: var(--green-primary);
  border-width: 3px;
  box-shadow: 0 0 0 2px var(--green-pastel);
}

.ranking__list-position {
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ranking__list-medal {
  font-size: 24px;
}

.ranking__list-medal--gold {
  color: #FFD700;
}

.ranking__list-medal--silver {
  color: #C0C0C0;
}

.ranking__list-medal--bronze {
  color: #CD7F32;
}

.ranking__list-position-number {
  font-size: 16px;
  font-weight: 700;
  color: var(--gray-dark);
}

.ranking__list-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--green-pastel);
  color: var(--green-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.ranking__list-info {
  flex: 1;
  min-width: 0;
}

.ranking__list-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--black-soft);
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ranking__list-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  background: var(--green-primary);
  color: var(--white);
  border-radius: var(--border-radius-full);
}

.ranking__list-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.ranking__list-stat {
  font-size: 12px;
  color: var(--gray-dark);
  display: flex;
  align-items: center;
  gap: 4px;
}

.ranking__list-stat svg {
  font-size: 11px;
  color: var(--green-primary);
}

.ranking__list-score {
  text-align: right;
  flex-shrink: 0;
}

.ranking__list-score-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--green-primary);
  line-height: 1.2;
}

.ranking__list-score-label {
  font-size: 11px;
  color: var(--gray-dark);
  font-weight: 500;
}

/* User Card */
.ranking__user-card {
  padding: 20px;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--green-dark) 100%);
  border: none;
}

.ranking__user-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking__user-info {
  flex: 1;
}

.ranking__user-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
}

.ranking__user-position {
  font-size: 24px;
  font-weight: 700;
  color: var(--white);
}

.ranking__user-score {
  text-align: right;
}

.ranking__user-score-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--white);
  line-height: 1.2;
}

.ranking__user-score-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

@media (min-width: 768px) {
  .ranking {
    padding: 24px;
  }

  .ranking__container {
    max-width: 800px;
  }

  .ranking__header {
    margin-bottom: 32px;
  }

  .ranking__title {
    font-size: 48px;
  }

  .ranking__subtitle {
    font-size: 16px;
  }

  .ranking__filters {
    gap: 12px;
    margin-bottom: 32px;
  }

  .ranking__filter-btn {
    padding: 14px 20px;
    font-size: 15px;
  }

  .ranking__filter-btn svg {
    font-size: 16px;
  }

  .ranking__back-btn {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }

  .ranking__back-btn:hover {
    background: var(--green-dark);
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
  }

  .ranking__podium {
    gap: 16px;
    margin-bottom: 32px;
    padding: 0;
  }

  .ranking__podium-item {
    max-width: 180px;
    padding: 24px 16px;
  }

  .ranking__podium-item--first {
    padding-bottom: 32px;
  }

  .ranking__podium-item--second {
    padding-bottom: 28px;
  }

  .ranking__podium-item--third {
    padding-bottom: 24px;
  }

  .ranking__podium-crown {
    top: -24px;
    font-size: 40px;
  }

  .ranking__podium-medal {
    font-size: 32px;
  }

  .ranking__podium-avatar {
    width: 72px;
    height: 72px;
    font-size: 32px;
  }

  .ranking__podium-avatar--first {
    width: 84px;
    height: 84px;
    font-size: 36px;
  }

  .ranking__podium-name {
    font-size: 15px;
  }

  .ranking__podium-score {
    font-size: 20px;
  }

  .ranking__list-card {
    padding: 24px;
  }

  .ranking__list-title {
    font-size: 20px;
  }

  .ranking__list-item {
    padding: 16px;
  }

  .ranking__list-avatar {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }

  .ranking__list-name {
    font-size: 16px;
  }

  .ranking__list-score-value {
    font-size: 20px;
  }

  .ranking__user-card {
    padding: 24px;
  }

  .ranking__user-position {
    font-size: 28px;
  }

  .ranking__user-score-value {
    font-size: 40px;
  }
}
</style>
