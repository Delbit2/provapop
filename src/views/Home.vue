<template>
  <div class="home">
    <div class="home__container">
      
      <!-- 1. CABEÇALHO (A Identidade) -->
      <div class="home__header animate-fade-down">
        <div class="home__header-content">
          <img src="@/assets/logo.png" alt="ProvaPop!" class="home__logo" />
          <p class="home__subtitle">Alcance sua nota mais alta! 🎯</p>
          <p class="home__greeting">{{ dynamicGreeting }}</p>
        </div>
      </div>

      <!-- 2. O PROTAGONISTA: MISSÃO DO DIA (Chamativa e Gigante) -->
      <div class="home__hero-mission animate-slide-up" style="animation-delay: 0.1s;">
        <h2 class="section-title">Missão Principal</h2>
        
        <button class="hero-card" @click="startQuiz('enem')">
          <div class="hero-card__glow"></div>
          <div class="hero-card__content">
            <div class="hero-card__info">
              <div class="hero-card__badge">RECOMENDADO</div>
              <h3 class="hero-card__title">Desafio ENEM</h3>
              <p class="hero-card__desc">Continue sua jornada. 2 questões aguardam você!</p>
            </div>
            <div class="hero-card__action">
              <div class="hero-play-btn">
                <font-awesome-icon icon="play" />
              </div>
            </div>
          </div>
        </button>

        <!-- Missão Secundária (Menor para não roubar a cena) -->
        <button class="secondary-card" @click="startQuiz('foco')">
          <div class="secondary-card__icon">
            <font-awesome-icon icon="rocket" />
          </div>
          <div class="secondary-card__text">
            <span class="secondary-title">Da Terra à Lua</span>
            <span class="secondary-subtitle">Treino Temático</span>
          </div>
          <font-awesome-icon icon="chevron-right" class="secondary-arrow" />
        </button>
      </div>

      <!-- 3. PAINEL DO JOGADOR (Status, Pontos e Foguinho) -->
      <div class="home__player-dashboard animate-slide-up" style="animation-delay: 0.2s;">
        <h2 class="section-title">Seu Progresso</h2>
        
        <div class="dashboard-glass">
          <!-- O "Cofre" Principal -->
          <div class="dashboard-main-stats">
            <div class="hud-badge streak" :class="{ 'active': userStreak > 0 }">
              <span class="hud-icon fire-icon">🔥</span>
              <div class="hud-text">
                <span class="hud-value">{{ userStreak }}</span>
                <span class="hud-label">Dias Seguidos</span>
              </div>
            </div>
            
            <div class="hud-badge points">
              <span class="hud-icon">⚡</span>
              <div class="hud-text">
                <span class="hud-value">{{ userPoints }}</span>
                <span class="hud-label">Pontos ProvaPop</span>
              </div>
            </div>
          </div>

          <!-- Estatísticas Menores -->
          <div class="dashboard-sub-stats">
            <div class="sub-stat">
              <font-awesome-icon icon="trophy" class="sub-stat-icon" />
              <span class="sub-stat-val">{{ stats.total_quizzes || 0 }}</span>
              <span class="sub-stat-lbl">Quizzes</span>
            </div>
            <div class="sub-stat divider"></div>
            <div class="sub-stat">
              <font-awesome-icon icon="check-circle" class="sub-stat-icon success" />
              <span class="sub-stat-val">{{ stats.accuracy ? `${Math.round(stats.accuracy)}%` : '0%' }}</span>
              <span class="sub-stat-lbl">Acertos</span>
            </div>
            <div class="sub-stat divider"></div>
            <div class="sub-stat">
              <font-awesome-icon icon="chart-line" class="sub-stat-icon gold" />
              <span class="sub-stat-val">{{ stats.ranking_position ? `#${stats.ranking_position}` : '#--' }}</span>
              <span class="sub-stat-lbl">Ranking</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 4. BANNER INTERATIVO DO WEBBOOK -->
      <div class="home__webbook-banner animate-slide-up" style="animation-delay: 0.3s;">
        <div class="webbook-content">
          <div class="webbook-icon">⭐</div>
          <div class="webbook-text-area">
            <h3 class="webbook-title">Webbook Premium</h3>
            <span class="webbook-badge-soon">EM BREVE</span>
          </div>
        </div>
        <button class="webbook-btn-disabled" @click="handleWebbook">
          Aguarde!
        </button>
      </div>

    </div>

    <!-- BOTTOM NAVIGATION BAR -->
    <nav class="bottom-nav">
      <button class="nav-item active">
        <font-awesome-icon icon="home" class="nav-icon" />
        <span class="nav-label">Início</span>
      </button>
      <button class="nav-item" @click="goToCategories">
        <font-awesome-icon icon="dumbbell" class="nav-icon" />
        <span class="nav-label">Treino</span>
      </button>
      <button class="nav-item" @click="handleRanking">
        <font-awesome-icon icon="trophy" class="nav-icon" />
        <span class="nav-label">Ranking</span>
      </button>
      <button class="nav-item" @click="goToProfile">
        <font-awesome-icon icon="user" class="nav-icon" />
        <span class="nav-label">Perfil</span>
      </button>
    </nav>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
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

const dynamicGreeting = computed(() => {
  const hour = new Date().getHours()
  let greeting = 'Boa noite'
  
  if (hour >= 5 && hour < 12) {
    greeting = 'Bom dia'
  } else if (hour >= 12 && hour < 18) {
    greeting = 'Boa tarde'
  }

  const userName = authStore.user?.nickname ? authStore.user.nickname.split(' ')[0] : 'Estudante'
  
  return `${greeting}, ${userName}! ✨`
})

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

function startQuiz(categoryId: string) {
  router.push({
    name: 'quiz',
    params: { category: categoryId }
  })
}

function goToCategories() {
  router.push('/categorias')
}

function handleRanking() {
  router.push('/ranking')
}

function handleWebbook() {
  alert('O Webbook Premium está no forno! 🚀 Em breve você terá acesso a um material incrível!')
}

function goToProfile() {
  router.push('/perfil')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.home {
  --primary: #8B1E3F;
  --primary-dark: #5d142a;
  --secondary: #E25822;
  --text-main: #2d2422;
  --text-muted: #5a4a46;
  --border-light: rgba(139, 30, 63, 0.1);

  min-height: 100vh;
  padding: 16px 16px 90px 16px; 
  background-color: #FFF4EF;
  background-image: linear-gradient(180deg, #FFF4EF 0%, #FFFFFF 35%, #FCF2EE 80%, #EBD2CB 100%);
  position: relative;
  overflow-x: hidden;
}

.home__container {
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

/* Títulos das Seções */
.section-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 12px 4px;
}

/* --- ANIMAÇÕES --- */
.animate-slide-up {
  opacity: 0;
  transform: translateY(20px);
  animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-fade-down {
  opacity: 0;
  transform: translateY(-15px);
  animation: fadeDown 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUpFade {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
  to { opacity: 1; transform: translateY(0); }
}

/* --- CABEÇALHO --- */
.home__header {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
  padding-top: 8px;
}

.home__header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.home__logo {
  height: 180px !important; /* Ajuste sutil para dar espaço à missão gigante */
  width: auto !important;
  object-fit: contain;
  display: block;
  animation: float 4s ease-in-out infinite; 
  filter: drop-shadow(0 10px 15px rgba(139, 30, 63, 0.15));
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

.home__subtitle {
  font-size: 18px;
  font-weight: 800;
  color: var(--primary);
  margin: 4px 0 4px 0;
  letter-spacing: 0.5px;
}

.home__greeting {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

/* --- O PROTAGONISTA: MISSÃO DO DIA --- */
.home__hero-mission {
  margin-bottom: 32px;
}

.hero-card {
  width: 100%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: 24px;
  padding: 24px;
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  box-shadow: 0 15px 30px rgba(139, 30, 63, 0.3);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: left;
  margin-bottom: 12px;
}

.hero-card:active {
  transform: scale(0.97);
}

.hero-card__glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0) 70%);
  transform: rotate(45deg);
  animation: shimmer-glow 4s linear infinite;
  pointer-events: none;
}

@keyframes shimmer-glow {
  0% { transform: rotate(0deg) translate(-10%, -10%); }
  100% { transform: rotate(360deg) translate(-10%, -10%); }
}

.hero-card__content {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hero-card__info {
  flex: 1;
}

.hero-card__badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 12px;
  margin-bottom: 10px;
  letter-spacing: 1px;
  backdrop-filter: blur(5px);
}

.hero-card__title {
  color: #fff;
  font-size: 26px;
  font-weight: 900;
  margin: 0 0 6px 0;
  text-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.hero-card__desc {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  line-height: 1.4;
  max-width: 90%;
}

.hero-play-btn {
  width: 56px;
  height: 56px;
  background: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary);
  font-size: 22px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
  margin-left: 16px;
  flex-shrink: 0;
  animation: pulse-play 2s infinite;
}

@keyframes pulse-play {
  0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(255, 255, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}

/* Missão Secundária */
.secondary-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(226, 88, 34, 0.2);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(226, 88, 34, 0.05);
  transition: all 0.2s ease;
}

.secondary-card:active { transform: scale(0.98); }

.secondary-card__icon {
  width: 40px;
  height: 40px;
  background: rgba(226, 88, 34, 0.1);
  color: var(--secondary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.secondary-card__text {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.secondary-title {
  color: var(--text-main);
  font-weight: 800;
  font-size: 16px;
}

.secondary-subtitle {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
}

.secondary-arrow {
  color: var(--border-light);
  font-size: 16px;
}

/* --- PAINEL DO JOGADOR --- */
.home__player-dashboard {
  margin-bottom: 32px;
}

.dashboard-glass {
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 1);
  border-radius: 24px;
  padding: 20px;
  backdrop-filter: blur(15px);
  box-shadow: 0 10px 30px rgba(139, 30, 63, 0.05);
}

.dashboard-main-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.hud-badge {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
}

.hud-icon {
  font-size: 28px;
}

.hud-text {
  display: flex;
  flex-direction: column;
}

.hud-value {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-main);
  line-height: 1;
  margin-bottom: 4px;
}

.hud-label {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.hud-badge.points {
  border: 1px solid rgba(212, 175, 55, 0.2);
}
.hud-badge.points .hud-value { color: #D4AF37; }

.hud-badge.streak {
  border: 1px solid var(--border-light);
}

.hud-badge.streak.active {
  border: 1px solid rgba(226, 88, 34, 0.3);
  background: #FFF4EF;
}

.hud-badge.streak.active .hud-value {
  color: var(--secondary);
}

.hud-badge.streak.active .fire-icon {
  animation: pulse-fire 1.5s infinite alternate;
}

@keyframes pulse-fire {
  0% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(226,88,34,0.5)); }
  100% { transform: scale(1.2); filter: drop-shadow(0 0 6px rgba(226,88,34,0.8)); }
}

.dashboard-sub-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.02);
  padding: 12px 16px;
  border-radius: 16px;
}

.sub-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.sub-stat.divider {
  flex: 0;
  width: 1px;
  height: 30px;
  background: var(--border-light);
}

.sub-stat-icon {
  font-size: 16px;
  color: var(--primary);
}
.sub-stat-icon.success { color: #2e7d32; }
.sub-stat-icon.gold { color: #D4AF37; }

.sub-stat-val {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-main);
}

.sub-stat-lbl {
  font-size: 10px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* --- BANNER WEBBOOK --- */
.home__webbook-banner {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  backdrop-filter: blur(10px);
}

.webbook-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.webbook-icon {
  font-size: 28px;
  filter: grayscale(0.8);
  opacity: 0.7;
}

.webbook-title {
  color: var(--text-main);
  font-size: 15px;
  font-weight: 800;
  margin: 0 0 4px 0;
}

.webbook-badge-soon {
  background: var(--text-muted);
  color: white;
  font-size: 9px;
  font-weight: 800;
  padding: 3px 6px;
  border-radius: 6px;
  letter-spacing: 0.5px;
}

.webbook-btn-disabled {
  background: var(--border-light);
  color: var(--text-muted);
  border: none;
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

/* --- BOTTOM NAVIGATION BAR --- */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 75px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 -10px 25px rgba(139, 30, 63, 0.05);
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 10px 10px 10px; 
  z-index: 100;
}

.nav-item {
  background: none;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-muted);
  cursor: pointer;
  flex: 1;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.7;
}

.nav-icon {
  font-size: 22px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-label {
  font-size: 11px;
  font-weight: 700;
}

.nav-item.active {
  color: var(--primary);
  opacity: 1;
}

.nav-item.active .nav-icon {
  transform: translateY(-4px);
  filter: drop-shadow(0 4px 6px rgba(139, 30, 63, 0.2));
}

/* Responsividade Básica */
@media (min-width: 768px) {
  .home { padding: 32px 32px 100px 32px; }
  .home__container { max-width: 600px; } /* Mantém formato celular no desktop */
  .hero-card__title { font-size: 32px; }
  .hud-value { font-size: 24px; }
  
  .bottom-nav {
    max-width: 600px;
    height: 70px;
    left: 50%;
    transform: translateX(-50%);
    bottom: 24px;
    border-radius: 35px;
    border: 1px solid rgba(255, 255, 255, 0.8);
    box-shadow: 0 15px 35px rgba(139, 30, 63, 0.1);
    padding: 0 20px;
  }
}
</style>
