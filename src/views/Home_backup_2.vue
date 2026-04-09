<template>
  <div class="home">
    <div class="home__container">
      
      <!-- CABEÇALHO (Logo centralizada, texto vinho e botão de sair no canto) -->
      <div class="home__header">
        <div class="home__header-content">
          <img src="@/assets/logo.png" alt="ProvaPop!" class="home__logo" />
          <p class="home__subtitle">Alcance sua nota mais alta! 🎯</p>
        </div>

        <div class="home__header-actions">
          <button class="home__logout-btn" @click="handleLogout" title="Sair">
            <font-awesome-icon icon="power-off" />
          </button>
        </div>
      </div>

      <!-- BARRA DE STATUS FASE 2 -->
      <div class="home__hud">
        <div class="hud-badge points">
          <span class="hud-icon">⚡</span>
          <span class="hud-value">{{ userPoints }} pts</span>
        </div>
        
        <div class="hud-badge streak" :class="{ 'active': userStreak > 0 }">
          <span class="hud-icon fire-icon">🔥</span>
          <span class="hud-value">{{ userStreak }} dias</span>
        </div>
      </div>

      <!-- ESTATÍSTICAS (Minimalista) -->
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

      <!-- PAINEL DE MISSÕES (Textos Curtos e Diretos) -->
      <div class="home__missions">
        <div class="home__missions-header">
          <h2 class="home__missions-title">Missões de Hoje</h2>
        </div>

        <div class="home__journey-buttons">
          <Button variant="primary" size="lg" full-width @click="handleStart" class="journey-btn daily-btn">
            <div class="btn-content">
              <span class="btn-title">ENEM</span>
              <span class="btn-subtitle">5 questões</span>
            </div>
          </Button>

          <Button variant="primary" size="lg" full-width @click="handleStart" class="journey-btn thematic-btn">
            <div class="btn-content">
              <span class="btn-title">Da Terra à Lua 🚀</span>
              <span class="btn-subtitle">2 questões</span>
            </div>
          </Button>
        </div>
      </div>

      <!-- BANNER INTERATIVO DO WEBBOOK (Direto ao ponto) -->
      <div class="home__webbook-banner">
        <div class="webbook-content">
          <div class="webbook-icon">⭐</div>
          <div class="webbook-text-area">
            <h3 class="webbook-title">Webbook Premium</h3>
            <p class="webbook-text">Preço promocional!</p>
          </div>
        </div>
        <button class="webbook-btn" @click="handleWebbook">
          Eu Quero!
        </button>
      </div>

      <!-- SEÇÕES GERAIS -->
      <div class="home__sections">
        <Card variant="elevated" class="home__section-card" clickable @click="handleRanking">
          <div class="home__section-content">
            <div class="home__section-icon">
              <font-awesome-icon icon="trophy" />
            </div>
            <div class="home__section-text">
              <h3 class="home__section-title">Ranking</h3>
              <p class="home__section-description">Sua posição global</p>
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
              <p class="home__section-description">Sua conta</p>
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

const userPoints = ref(1250) 
const userStreak = ref(3)    

const router = useRouter()
const authStore = useAuthStore()

const stats = ref({
  total_quizzes: 0,
  accuracy: 0,
  ranking_position: null as number | null
})

const loading = ref(false)

async function loadStats() {
  if (!authStore.isAuthenticated) return

  loading.value = true
  try {
    const userStats = await api.users.getStats()
    stats.value.total_quizzes = userStats.total_quizzes || 0
    stats.value.accuracy = userStats.accuracy || 0

    try {
      const ranking = await api.ranking.get('all')
      const currentUser = ranking.find(u => u.user_id === authStore.user?.id)
      if (currentUser) {
        stats.value.ranking_position = currentUser.position
      }
    } catch (err) {
      console.warn('Erro ao buscar ranking:', err)
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

function handleWebbook() {
  alert('Redirecionando para a página fantástica de vendas do Webbook ProvaPop! 🚀📚')
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
}

.home__container {
  max-width: 100%;
  margin: 0 auto;
}

/* --- CABEÇALHO REFEITO (Centralizado) --- */
.home__header {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 28px;
  padding-top: 8px;
}

.home__header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* --- ESTILO DA LOGO --- */
.home__logo {
  height: 250px !important;
  max-height: none !important;
  width: auto !important;
  max-width: none !important;
  margin-bottom: 0;
  object-fit: contain;
  display: block;
}

/* --- NOVO ESTILO DO SUBTÍTULO (Vinho, maior e centralizado) --- */
.home__subtitle {
  font-size: 19px;
  font-weight: 800;
  color: #800020; /* Cor Vinho elegante */
  margin: 12px 0 0 0;
  letter-spacing: 0.5px;
  text-align: center;
}

/* --- BOTÕES DO TOPO (Apenas Deslogar, no canto) --- */
.home__header-actions {
  position: absolute;
  right: 0;
  top: 0;
}

.home__logout-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--yellow-primary);
  color: var(--white);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-size: 18px;
}

.home__logout-btn:active {
  transform: scale(0.95);
}

/* --- HUD --- */
.home__hud {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.hud-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  flex: 1;
  justify-content: center;
}

.hud-badge.points {
  background-color: rgba(245, 158, 11, 0.1); 
  color: #D97706; 
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.hud-badge.streak {
  background-color: rgba(100, 116, 139, 0.1);
  color: #64748B;
  border: 1px solid rgba(100, 116, 139, 0.2);
}

.hud-badge.streak.active {
  background-color: rgba(239, 68, 68, 0.1); 
  color: #DC2626; 
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.hud-badge.streak.active .fire-icon {
  animation: pulse-fire 1.5s infinite alternate;
}

@keyframes pulse-fire {
  0% { transform: scale(1); }
  100% { transform: scale(1.2); }
}

/* --- ESTATÍSTICAS --- */
.home__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.home__stat-card {
  padding: 16px 12px;
}

.home__stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.home__stat-icon {
  font-size: 20px;
  color: var(--green-primary);
}

.home__stat-value {
  font-size: 18px;
  font-weight: 800;
  color: var(--black-soft);
  line-height: 1;
}

.home__stat-label {
  font-size: 11px;
  color: var(--gray-dark);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* --- MISSÕES --- */
.home__missions {
  background: var(--white);
  border: 1px solid var(--green-pastel);
  border-radius: var(--border-radius-lg);
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}

.home__missions-header {
  margin-bottom: 16px;
  text-align: center;
}

.home__missions-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--black-soft);
  margin: 0;
  text-transform: uppercase;
}

.home__journey-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.journey-btn {
  height: auto !important;
  padding: 16px !important;
  border-radius: 12px !important;
}

/* --- NOVA COR: Azul Espacial Profundo (Harmônico) --- */
.thematic-btn {
  background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
}

.btn-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.btn-title {
  font-size: 18px;
  font-weight: 800;
}

.btn-subtitle {
  font-size: 13px;
  opacity: 0.9;
  font-weight: 500;
}

/* --- BANNER WEBBOOK --- */
.home__webbook-banner {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1px solid #FCD34D;
  border-radius: var(--border-radius-lg);
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.1);
  animation: pulse-border 2.5s infinite;
}

@keyframes pulse-border {
  0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.2); }
  70% { box-shadow: 0 0 0 6px rgba(245, 158, 11, 0); }
  100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
}

.webbook-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.webbook-icon {
  font-size: 28px;
}

.webbook-title {
  color: #B45309;
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 2px 0;
}

.webbook-text {
  color: #78350F;
  font-size: 13px;
  font-weight: 500;
  margin: 0;
}

.webbook-btn {
  background: #F59E0B;
  color: #FFFFFF;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
  flex-shrink: 0;
}

.webbook-btn:hover {
  transform: scale(1.05);
  background: #D97706;
}

/* --- SEÇÕES FINAIS --- */
.home__sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.home__section-card {
  padding: 16px;
  transition: transform 0.2s ease;
}

.home__section-card:active {
  transform: scale(0.98);
}

.home__section-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.home__section-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
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
}

.home__section-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--black-soft);
  margin: 0 0 2px 0;
}

.home__section-description {
  font-size: 13px;
  color: var(--gray-dark);
  margin: 0;
}

.home__section-arrow {
  font-size: 16px;
  color: var(--gray-light);
}

/* Responsividade */
@media (min-width: 768px) {
  .home { padding: 24px; }
  .home__container { max-width: 800px; }
  .home__logo { height: 250px; }
  .home__subtitle { font-size: 22px; } /* Ainda maior no PC! */
  .home__hud { justify-content: center; gap: 24px; }
  .hud-badge { flex: none; width: 200px; }
}
</style>
