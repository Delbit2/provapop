<template>
  <div class="ranking">
    <div class="ranking__container">
      <Transition name="fade" appear>
        <div class="ranking__content">
          <div class="ranking__header">
            <button class="ranking__back-btn" @click="goBack" title="Voltar">
              <font-awesome-icon icon="arrow-left"></font-awesome-icon>
            </button>
            <div class="ranking__header-content">
              <h1 class="ranking__title">Ranking</h1>
              <p class="ranking__subtitle">Os astros do ProvaPop!</p>
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
              <font-awesome-icon :icon="filter.icon"></font-awesome-icon>
              {{ filter.label }}
            </button>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="ranking__loading">
            <div class="ranking__loading-spinner"></div>
            <p>Afinando os instrumentos...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="ranking__error">
            <font-awesome-icon icon="exclamation-triangle" class="ranking__error-icon"></font-awesome-icon>
            <p>{{ error }}</p>
            <button class="ranking__retry-btn" @click="loadRanking">Tentar Novamente</button>
          </div>

          <!-- Empty State -->
          <div v-else-if="filteredRanking.length === 0" class="ranking__empty">
            <font-awesome-icon icon="trophy" class="ranking__empty-icon"></font-awesome-icon>
            <p>O palco está vazio. Seja o primeiro a pontuar!</p>
          </div>

          <!-- Content -->
          <template v-else>
            <!-- Top 3 Podium (Limpíssimo!) -->
            <div class="ranking__podium">
              <!-- 2º LUGAR -->
              <div v-if="filteredRanking.length >= 2" class="ranking__podium-item ranking__podium-item--second">
                <div class="ranking__podium-avatar">
                  <img src="@/assets/avatar-default.png" alt="Avatar" class="ranking__avatar-img" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[1].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[1].total_score) }} pts</div>
              </div>

              <!-- 1º LUGAR -->
              <div v-if="filteredRanking.length >= 1" class="ranking__podium-item ranking__podium-item--first">
                <div class="ranking__podium-crown">
                  <font-awesome-icon icon="trophy"></font-awesome-icon>
                </div>
                <div class="ranking__podium-avatar ranking__podium-avatar--first">
                  <img src="@/assets/avatar-default.png" alt="Avatar" class="ranking__avatar-img" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[0].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[0].total_score) }} pts</div>
              </div>

              <!-- 3º LUGAR -->
              <div v-if="filteredRanking.length >= 3" class="ranking__podium-item ranking__podium-item--third">
                <div class="ranking__podium-avatar">
                  <img src="@/assets/avatar-default.png" alt="Avatar" class="ranking__avatar-img" />
                </div>
                <div class="ranking__podium-name">{{ filteredRanking[2].nickname }}</div>
                <div class="ranking__podium-score">{{ formatScore(filteredRanking[2].total_score) }} pts</div>
              </div>
            </div>

            <!-- Ranking List -->
            <Card variant="elevated" class="ranking__list-card">
              <div class="ranking__list-header">
                <h2 class="ranking__list-title">Classificação</h2>
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
                    <!-- Apenas números com cores de destaque para os top 3 -->
                    <span :class="['ranking__list-position-number', `ranking__list-position-number--${index + 1}`]">
                      {{ index + 1 }}º
                    </span>
                  </div>
                  
                  <div class="ranking__list-avatar">
                    <img src="@/assets/avatar-default.png" alt="Avatar" class="ranking__avatar-img" />
                  </div>
                  
                  <div class="ranking__list-info">
                    <div class="ranking__list-name">
                      {{ user.nickname }}
                    </div>
                    <div class="ranking__list-stats">
                      <span class="ranking__list-stat">
                        <font-awesome-icon icon="check-circle"></font-awesome-icon>
                        {{ user.correct_answers }} acertos
                      </span>
                      <span class="ranking__list-stat">
                        <font-awesome-icon icon="chart-line"></font-awesome-icon>
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
                  <div class="ranking__user-label">Sua Posição Atual</div>
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

type FilterType = 'week' | 'month'

const filters = [
  { value: 'week' as FilterType, label: 'Nesta Semana', icon: 'calendar-day' },
  { value: 'month' as FilterType, label: 'Neste Mês', icon: 'calendar' }
]

const selectedFilter = ref<FilterType>('week')

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

async function loadRanking() {
  loading.value = true
  error.value = null
  
  try {
    const data = await api.ranking.get(selectedFilter.value)
    
    if (!data) {
      rankingData.value = []
      return
    }
    
    if (!Array.isArray(data)) {
      throw new Error('Resposta inválida da API')
    }
    
    rankingData.value = data.map(user => ({
      ...user,
      is_current_user: user.user_id === authStore.user?.id
    }))
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar ranking. Tente novamente.'
  } finally {
    loading.value = false
  }
}

watch(selectedFilter, () => {
  loadRanking()
})

onMounted(() => {
  loadRanking()
})

const filteredRanking = computed(() => {
  return rankingData.value.map(user => ({
    ...user,
    is_current_user: user.user_id === authStore.user?.id
  }))
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
  --primary: #8B1E3F;
  --primary-dark: #5d142a;
  --secondary: #E25822;
  --text-main: #2d2422;
  --text-muted: #5a4a46;
  --border-light: #e8dedc;
  
  min-height: 100vh;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.ranking__container {
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.ranking__content {
  animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.ranking__header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.ranking__back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: #ffffff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 10px rgba(139, 30, 63, 0.2);
  flex-shrink: 0;
  font-size: 18px;
}

.ranking__back-btn:hover {
  background: var(--secondary);
  transform: scale(1.05) translateX(-2px);
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.3);
}

.ranking__back-btn:active {
  transform: scale(0.95);
}

.ranking__header-content {
  flex: 1;
}

.ranking__title {
  font-size: 32px;
  font-weight: 800;
  color: var(--primary);
  margin: 0 0 4px 0;
}

.ranking__subtitle {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  margin: 0;
}

/* Filter Tabs */
.ranking__filters {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}

.ranking__filter-btn {
  flex: 1;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid var(--border-light);
  border-radius: 16px;
  color: var(--text-muted);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  backdrop-filter: blur(10px);
}

.ranking__filter-btn:hover {
  border-color: var(--secondary);
  color: var(--secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(226, 88, 34, 0.1);
}

.ranking__filter-btn--active {
  background: var(--primary);
  border-color: var(--primary);
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(139, 30, 63, 0.25);
}

.ranking__filter-btn--active:hover {
  background: var(--primary-dark);
  border-color: var(--primary-dark);
  color: #ffffff;
}

/* Common Avatars & Images Rules */
.ranking__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Podium Styles */
.ranking__podium {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 32px;
  padding: 0 8px;
}

.ranking__podium-item {
  flex: 1;
  max-width: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 12px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  backdrop-filter: blur(10px);
}

.ranking__podium-item--first {
  order: 2;
  padding-bottom: 28px;
  /* Fundo limpo, mas com borda dourada para dar o charme */
  border: 2px solid #FFD700;
  box-shadow: 0 15px 35px rgba(255, 215, 0, 0.2);
  transform: scale(1.1);
  z-index: 2;
}

.ranking__podium-item--second {
  order: 1;
  padding-bottom: 24px;
}

.ranking__podium-item--third {
  order: 3;
  padding-bottom: 20px;
}

/* O troféu agora brilha absoluto no topo! */
.ranking__podium-crown {
  position: absolute;
  top: -26px;
  font-size: 40px;
  color: #FFD700;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
}

.ranking__podium-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  border: 3px solid #e8dedc;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.ranking__podium-item--first .ranking__podium-avatar {
  width: 76px;
  height: 76px;
  border: 3px solid #FFD700; /* Borda dourada no avatar do vencedor */
}

.ranking__podium-name {
  font-size: 13px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  color: var(--text-main);
}

.ranking__podium-score {
  font-size: 16px;
  font-weight: 800;
  color: var(--secondary);
}

/* List Styles */
.ranking__list-card {
  padding: 24px;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.ranking__list-header {
  margin-bottom: 20px;
  text-align: center;
}

.ranking__list-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--primary);
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
  gap: 16px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.ranking__list-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.08);
  border-color: var(--secondary);
}

.ranking__list-item--top3 {
  background: #fdfaf9;
  border-color: #fce4dc;
}

.ranking__list-item--current {
  border-color: var(--secondary);
  border-width: 2px;
  background: rgba(226, 88, 34, 0.03);
  box-shadow: 0 4px 12px rgba(226, 88, 34, 0.1);
}

.ranking__list-position {
  width: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ranking__list-position-number {
  font-size: 16px;
  font-weight: 900;
  color: var(--text-muted);
}

/* Cores especiais para os números do pódio na lista */
.ranking__list-position-number--1 { color: #D4AF37; font-size: 22px; }
.ranking__list-position-number--2 { color: #9CA3AF; font-size: 20px; }
.ranking__list-position-number--3 { color: #CD7F32; font-size: 20px; }

.ranking__list-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid var(--border-light);
  overflow: hidden;
}

.ranking__list-item--current .ranking__list-avatar {
  border-color: var(--secondary);
}

.ranking__list-info {
  flex: 1;
  min-width: 0;
}

.ranking__list-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 4px;
}

.ranking__list-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.ranking__list-stat {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.ranking__list-stat svg {
  font-size: 12px;
  color: var(--secondary);
}

.ranking__list-score {
  text-align: right;
  flex-shrink: 0;
}

.ranking__list-score-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--secondary);
  line-height: 1.1;
}

.ranking__list-score-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* User Card */
.ranking__user-card {
  padding: 24px;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  border: none;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(226, 88, 34, 0.3);
  margin-top: 24px;
}

.ranking__user-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking__user-info { flex: 1; }

.ranking__user-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 4px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ranking__user-position {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
}

.ranking__user-score { text-align: right; }

.ranking__user-score-value {
  font-size: 36px;
  font-weight: 900;
  color: #ffffff;
  line-height: 1.1;
}

.ranking__user-score-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Loading, Error, Empty */
.ranking__loading, .ranking__error, .ranking__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.ranking__loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-light);
  border-top-color: var(--secondary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.ranking__loading p, .ranking__error p, .ranking__empty p {
  font-size: 16px;
  color: var(--text-muted);
  font-weight: 500;
  margin: 0;
}

.ranking__error-icon, .ranking__empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.ranking__error-icon { color: var(--secondary); }
.ranking__empty-icon { color: var(--border-light); }

.ranking__retry-btn {
  margin-top: 20px;
  padding: 14px 28px;
  background: var(--primary);
  color: #ffffff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(139, 30, 63, 0.2);
}

.ranking__retry-btn:hover {
  background: var(--secondary);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(226, 88, 34, 0.3);
}

@media (min-width: 768px) {
  .ranking { padding: 32px; }
  .ranking__container { max-width: 800px; }
  .ranking__header { margin-bottom: 32px; }
  .ranking__title { font-size: 42px; }
  .ranking__filters { gap: 16px; }
  .ranking__filter-btn { padding: 16px 24px; font-size: 16px; }
  .ranking__podium { gap: 24px; }
  .ranking__podium-item { max-width: 160px; padding: 24px 16px; }
  .ranking__podium-avatar { width: 72px; height: 72px; }
  .ranking__podium-item--first .ranking__podium-avatar { width: 88px; height: 88px; }
  .ranking__podium-name { font-size: 15px; }
  .ranking__podium-score { font-size: 20px; }
  .ranking__list-card { padding: 32px; }
  .ranking__list-item { padding: 20px; }
  .ranking__list-avatar { width: 56px; height: 56px; }
  .ranking__list-name { font-size: 18px; }
  .ranking__list-score-value { font-size: 24px; }
  .ranking__user-card { padding: 32px; }
  .ranking__user-position { font-size: 32px; }
  .ranking__user-score-value { font-size: 48px; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from { opacity: 0; transform: translateY(20px); }
.fade-leave-to { opacity: 0; transform: translateY(-20px); }
</style>
