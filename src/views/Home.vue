<template>
  <div class="home">
    <div class="home__container">
      <div class="home__header">
        <div class="home__header-content">
          <h1 class="home__title">Quiz Musical</h1>
          <p class="home__subtitle">Prepare-se para o ENEM com música</p>
        </div>
        <div class="home__header-actions">
          <button class="home__profile-btn" @click="goToProfile" title="Meu Perfil">
            <font-awesome-icon icon="user" />
          </button>
          <button class="home__logout-btn" @click="handleLogout" title="Sair">
            <font-awesome-icon icon="power-off" />
          </button>
        </div>
      </div>

      <div class="home__stats">
        <Card variant="outlined" class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="trophy" class="home__stat-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.total_quizzes || 0 }}</div>
              <div class="home__stat-label">Quizzes</div>
            </div>
          </div>
        </Card>
        <Card variant="outlined" class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="check-circle" class="home__stat-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.accuracy ? `${Math.round(stats.accuracy)}%` : '0%' }}</div>
              <div class="home__stat-label">Acertos</div>
            </div>
          </div>
        </Card>
        <Card variant="outlined" class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="chart-line" class="home__stat-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.ranking_position ? `#${stats.ranking_position}` : '#--' }}</div>
              <div class="home__stat-label">Ranking</div>
            </div>
          </div>
        </Card>
      </div>

      <div class="home__actions">
        <Button variant="primary" size="lg" full-width @click="handleStart" class="home__start-btn">
          <font-awesome-icon icon="play" />
          Começar Quiz
        </Button>
      </div>

      <div class="home__sections">
        <Card variant="elevated" class="home__section-card" clickable @click="handleRanking">
          <div class="home__section-content">
            <div class="home__section-icon">
              <font-awesome-icon icon="trophy" />
            </div>
            <div class="home__section-text">
              <h3 class="home__section-title">Ranking</h3>
              <p class="home__section-description">Veja sua posição entre os melhores</p>
            </div>
            <font-awesome-icon icon="angle-right" class="home__section-arrow" />
          </div>
        </Card>

        <Card variant="elevated" class="home__section-card" clickable @click="goToProfile">
          <div class="home__section-content">
            <div class="home__section-icon">
              <font-awesome-icon icon="user" />
            </div>
            <div class="home__section-text">
              <h3 class="home__section-title">Meu Perfil</h3>
              <p class="home__section-description">Gerencie suas informações</p>
            </div>
            <font-awesome-icon icon="angle-right" class="home__section-arrow" />
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Button from '@/components/Button.vue'
import Card from '@/components/Card.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  total_quizzes: 0,
  accuracy: 0,
  ranking_position: null as number | null
})

const loading = ref(false)

async function loadStats() {
  if (!authStore.isAuthenticated) {
    return
  }

  loading.value = true
  try {
    // Buscar estatísticas do usuário
    const userStats = await api.users.getStats()
    stats.value.total_quizzes = userStats.total_quizzes || 0
    stats.value.accuracy = userStats.accuracy || 0

    // Buscar posição no ranking
    try {
      const ranking = await api.ranking.get('all')
      const currentUser = ranking.find(u => u.user_id === authStore.user?.id)
      if (currentUser) {
        stats.value.ranking_position = currentUser.position
      }
    } catch (err) {
      console.warn('Erro ao buscar ranking:', err)
      // Não é crítico, apenas não mostra a posição
    }
  } catch (error) {
    console.error('Erro ao carregar estatísticas:', error)
  } finally {
    loading.value = false
  }
}

function handleStart() {
  router.push('/categorias')
}

function handleRanking() {
  router.push('/ranking')
}

function goToProfile() {
  router.push('/perfil')
}

async function handleLogout() {
  try {
    await authStore.logout()
  } catch (error) {
    console.error('Erro ao fazer logout:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.home__container {
  max-width: 100%;
  margin: 0 auto;
}

.home__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.home__header-content {
  flex: 1;
}

.home__header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.home__title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.home__subtitle {
  font-size: 14px;
  color: var(--gray-dark);
  margin: 0;
}

.home__profile-btn,
.home__logout-btn {
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

.home__profile-btn:active,
.home__logout-btn:active {
  transform: scale(0.95);
  background: var(--green-dark);
}

.home__logout-btn {
  background: var(--yellow-primary);
}

.home__logout-btn:hover {
  background: var(--yellow-dark);
}

.home__logout-btn:active {
  background: var(--yellow-dark);
}

.home__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.home__stat-card {
  padding: 16px;
}

.home__stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.home__stat-icon {
  font-size: 20px;
  color: var(--green-primary);
  flex-shrink: 0;
}

.home__stat-content {
  flex: 1;
  min-width: 0;
}

.home__stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--black-soft);
  line-height: 1.2;
}

.home__stat-label {
  font-size: 11px;
  color: var(--gray-dark);
  font-weight: 500;
}

.home__actions {
  margin-bottom: 20px;
}

.home__start-btn {
  gap: 8px;
}

.home__sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.home__section-card {
  padding: 16px;
}

.home__section-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.home__section-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-md);
  background: var(--green-pastel);
  color: var(--green-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.home__section-text {
  flex: 1;
  min-width: 0;
}

.home__section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--black-soft);
  margin: 0 0 4px 0;
}

.home__section-description {
  font-size: 13px;
  color: var(--gray-dark);
  margin: 0;
}

.home__section-arrow {
  font-size: 16px;
  color: var(--gray);
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .home {
    padding: 24px;
  }

  .home__container {
    max-width: 800px;
  }

  .home__header {
    margin-bottom: 32px;
  }

  .home__title {
    font-size: 48px;
  }

  .home__subtitle {
    font-size: 16px;
  }

  .home__profile-btn,
  .home__logout-btn {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }

  .home__profile-btn:hover {
    background: var(--green-dark);
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
  }

  .home__logout-btn:hover {
    background: var(--yellow-dark);
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
  }

  .home__stats {
    gap: 16px;
    margin-bottom: 24px;
  }

  .home__stat-card {
    padding: 20px;
  }

  .home__stat-icon {
    font-size: 24px;
  }

  .home__stat-value {
    font-size: 22px;
  }

  .home__stat-label {
    font-size: 12px;
  }

  .home__actions {
    margin-bottom: 24px;
  }

  .home__sections {
    gap: 16px;
    margin-bottom: 24px;
  }

  .home__section-card {
    padding: 20px;
  }

  .home__section-icon {
    width: 56px;
    height: 56px;
    font-size: 24px;
  }

  .home__section-title {
    font-size: 18px;
  }

  .home__section-description {
    font-size: 14px;
  }
}
</style>
