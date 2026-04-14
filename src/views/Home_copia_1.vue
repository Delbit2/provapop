<template>
  <div class="home">
    <div class="home__container">
      
      <!-- CABEÇALHO (Logo Flutuante, Subtítulo e Saudação Dinâmica) -->
      <div class="home__header animate-fade-down">
        <div class="home__header-content">
          <img src="@/assets/logo.png" alt="ProvaPop!" class="home__logo" />
          <p class="home__subtitle">Alcance sua nota mais alta! 🎯</p>
          <!-- Saudação Personalizada -->
          <p class="home__greeting">{{ dynamicGreeting }}</p>
        </div>
      </div>

      <!-- BARRA DE STATUS (Premium Pills) -->
      <div class="home__hud animate-slide-up" style="animation-delay: 0.1s;">
        <div class="hud-badge points">
          <span class="hud-icon">⚡</span>
          <span class="hud-value">{{ userPoints }} pts</span>
        </div>
        
        <div class="hud-badge streak" :class="{ 'active': userStreak > 0 }">
          <span class="hud-icon fire-icon">🔥</span>
          <span class="hud-value">{{ userStreak }} dias</span>
        </div>
      </div>

      <!-- ESTATÍSTICAS (Vidro Fosco) -->
      <div class="home__stats animate-slide-up" style="animation-delay: 0.2s;">
        <div class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="trophy" class="home__stat-icon wine-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.total_quizzes || 0 }}</div>
              <div class="home__stat-label">Quizzes</div>
            </div>
          </div>
        </div>
        <div class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="check-circle" class="home__stat-icon orange-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.accuracy ? `${Math.round(stats.accuracy)}%` : '0%' }}</div>
              <div class="home__stat-label">Acertos</div>
            </div>
          </div>
        </div>
        <div class="home__stat-card">
          <div class="home__stat-item">
            <font-awesome-icon icon="chart-line" class="home__stat-icon wine-icon" />
            <div class="home__stat-content">
              <div class="home__stat-value">{{ stats.ranking_position ? `#${stats.ranking_position}` : '#--' }}</div>
              <div class="home__stat-label">Ranking</div>
            </div>
          </div>
        </div>
      </div>

      <!-- PAINEL DE MISSÕES (O Coração do Game) -->
      <div class="home__missions animate-slide-up" style="animation-delay: 0.3s;">
        <div class="home__missions-header">
          <h2 class="home__missions-title">Missões de Hoje</h2>
          <p class="home__missions-subtitle">Complete as etapas para manter sua ofensiva!</p>
        </div>

        <div class="home__journey-buttons">
          <!-- Botão ENEM (Vinho Premium) -->
          <button class="mission-btn mission-btn--enem" @click="startQuiz('enem')">
            <div class="mission-btn-content">
              <div class="mission-btn-icon">
                <font-awesome-icon icon="certificate" />
              </div>
              <div class="mission-btn-text">
                <span class="btn-title">ENEM</span>
                <span class="btn-subtitle">2 questões oficiais</span>
              </div>
            </div>
            <font-awesome-icon icon="play-circle" class="mission-btn-play" />
          </button>

          <!-- Botão Da Terra à Lua (Laranja Vibrante) -->
          <button class="mission-btn mission-btn--thematic" @click="startQuiz('foco')">
            <div class="mission-btn-content">
              <div class="mission-btn-icon">
                <font-awesome-icon icon="rocket" />
              </div>
              <div class="mission-btn-text">
                <span class="btn-title">Da Terra à Lua</span>
                <span class="btn-subtitle">2 questões ProvaPop!</span>
              </div>
            </div>
            <font-awesome-icon icon="play-circle" class="mission-btn-play" />
          </button>
        </div>
      </div>

      <!-- BANNER INTERATIVO DO WEBBOOK (Com Tag "Em Breve") -->
      <div class="home__webbook-banner animate-slide-up" style="animation-delay: 0.4s;">
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

    <!-- BOTTOM NAVIGATION BAR (A cereja do bolo App Premium) -->
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

// SAUDAÇÃO DINÂMICA (Bom dia, Boa tarde, Boa noite + Nome)
const dynamicGreeting = computed(() => {
  const hour = new Date().getHours()
  let greeting = 'Boa noite'
  
  if (hour >= 5 && hour < 12) {
    greeting = 'Bom dia'
  } else if (hour >= 12 && hour < 18) {
    greeting = 'Boa tarde'
  }

  // Pega o primeiro nome do usuário, se existir. Se não, chama de 'Estudante'
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

// Direciona direto para as questões da banca selecionada!
function startQuiz(categoryId: string) {
  router.push({
    name: 'quiz',
    params: { category: categoryId }
  })
}

// O botão do meio (antigo Jogar) agora leva para a "área de treino"
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
  --border-light: #e8dedc;

  min-height: 100vh;
  padding: 16px 16px 90px 16px; 
  /* FUNDO QUENTE E PREMIUM: Pêssego suave até o branco e depois desce pro vinho muito claro */
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
  margin-bottom: 32px;
  padding-top: 16px;
}

.home__header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* LOGO FLUTUANTE 🎈 */
.home__logo {
  height: 220px !important;
  max-height: none !important;
  width: auto !important;
  max-width: none !important;
  margin-bottom: 0;
  object-fit: contain;
  display: block;
  animation: float 4s ease-in-out infinite; 
  filter: drop-shadow(0 15px 15px rgba(139, 30, 63, 0.15));
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-12px); }
  100% { transform: translateY(0px); }
}

.home__subtitle {
  font-size: 20px;
  font-weight: 800;
  color: var(--primary);
  margin: 8px 0 4px 0;
  letter-spacing: 0.5px;
  text-align: center;
}

.home__greeting {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

/* --- HUD (Premium Pills) --- */
.home__hud {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}

.hud-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 20px;
  font-weight: 800;
  font-size: 15px;
  flex: 1;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}

.hud-badge.points {
  color: #D4AF37;
  border: 1px solid rgba(212, 175, 55, 0.3);
}

.hud-badge.streak {
  color: var(--text-muted);
  border: 1px solid var(--border-light);
}

.hud-badge.streak.active {
  color: var(--secondary);
  border: 1px solid rgba(226, 88, 34, 0.3);
  background: rgba(226, 88, 34, 0.05);
}

.hud-badge.streak.active .fire-icon {
  animation: pulse-fire 1.5s infinite alternate;
}

@keyframes pulse-fire {
  0% { transform: scale(1); filter: drop-shadow(0 0 2px rgba(226,88,34,0.5)); }
  100% { transform: scale(1.2); filter: drop-shadow(0 0 6px rgba(226,88,34,0.8)); }
}

/* --- ESTATÍSTICAS --- */
.home__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 32px;
}

.home__stat-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 16px 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.03);
  transition: transform 0.3s ease;
}

.home__stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(139, 30, 63, 0.2);
}

.home__stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.home__stat-icon {
  font-size: 22px;
}

.wine-icon { color: var(--primary); }
.orange-icon { color: var(--secondary); }

.home__stat-value {
  font-size: 20px;
  font-weight: 900;
  color: var(--text-main);
  line-height: 1;
  margin-bottom: 4px;
}

.home__stat-label {
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* --- MISSÕES --- */
.home__missions {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-light);
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px rgba(139, 30, 63, 0.05);
  backdrop-filter: blur(15px);
}

.home__missions-header {
  margin-bottom: 20px;
  text-align: center;
}

.home__missions-title {
  font-size: 22px;
  font-weight: 900;
  color: var(--primary);
  margin: 0 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.home__missions-subtitle {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
  margin: 0;
}

.home__journey-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Botões de Missão Super Premium */
.mission-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 20px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.mission-btn:active {
  transform: scale(0.97);
}

.mission-btn::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(rgba(255,255,255,0.2), rgba(255,255,255,0));
  border-radius: 20px;
  pointer-events: none;
}

.mission-btn--enem {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  box-shadow: 0 8px 20px rgba(139, 30, 63, 0.25);
}

.mission-btn--thematic {
  background: linear-gradient(135deg, var(--secondary) 0%, #b84112 100%);
  box-shadow: 0 8px 20px rgba(226, 88, 34, 0.25);
}

.mission-btn-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mission-btn-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #ffffff;
  backdrop-filter: blur(5px);
}

.mission-btn-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  color: #ffffff;
}

.btn-title {
  font-size: 20px;
  font-weight: 900;
  margin-bottom: 2px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-subtitle {
  font-size: 13px;
  font-weight: 600;
  opacity: 0.9;
}

.mission-btn-play {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.9);
  transition: transform 0.3s ease;
}

.mission-btn:hover .mission-btn-play {
  transform: scale(1.1) translateX(4px);
}

/* --- BANNER WEBBOOK "EM BREVE" --- */
.home__webbook-banner {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border-light);
  border-radius: 20px;
  padding: 20px;
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
  font-size: 32px;
  filter: grayscale(0.8);
  opacity: 0.7;
}

.webbook-title {
  color: var(--text-main);
  font-size: 16px;
  font-weight: 800;
  margin: 0 0 6px 0;
}

.webbook-badge-soon {
  background: var(--text-muted);
  color: white;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 6px;
  letter-spacing: 0.5px;
}

.webbook-btn-disabled {
  background: var(--border-light);
  color: var(--text-muted);
  border: none;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 13px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.webbook-btn-disabled:hover {
  background: #dfd4d2;
}

/* --- BOTTOM NAVIGATION BAR (Menu Inferior Premium) --- */
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

/* Estado Ativo */
.nav-item.active {
  color: var(--primary);
  opacity: 1;
}

.nav-item.active .nav-icon {
  transform: translateY(-4px);
  filter: drop-shadow(0 4px 6px rgba(139, 30, 63, 0.2));
}

.nav-item:active .nav-icon {
  transform: scale(0.85);
}

/* Responsividade */
@media (min-width: 768px) {
  .home { padding: 32px 32px 100px 32px; }
  .home__container { max-width: 800px; }
  .home__header { margin-bottom: 40px; }
  .home__logo { height: 260px !important; }
  .home__subtitle { font-size: 24px; } 
  .home__hud { justify-content: center; gap: 24px; }
  .hud-badge { flex: none; width: 220px; padding: 12px 20px; font-size: 16px; }
  .home__stats { gap: 20px; margin-bottom: 40px; }
  .home__stat-card { padding: 20px; }
  .home__missions { padding: 32px; }
  .home__missions-title { font-size: 26px; }
  .mission-btn { padding: 24px; }
  .mission-btn-icon { width: 56px; height: 56px; font-size: 28px; }
  .btn-title { font-size: 24px; }
  
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
