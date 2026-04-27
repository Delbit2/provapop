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

      <!-- 2. O PROTAGONISTA: MISSÃO DO DIA (Absoluta na tela) -->
      <div class="home__hero-mission animate-slide-up" style="animation-delay: 0.1s;">
        <h2 class="section-title">Missão Principal</h2>
        
        <!-- O BOTÃO CAMALEÃO (Muda se a missão já foi concluída) -->
        <button 
          class="hero-card" 
          :class="{ 'hero-card--completed': missionCompletedToday }"
          @click="handleMissionAction"
        >
          <div class="hero-card__glow"></div>
          <div class="hero-card__content">
            
            <div class="hero-card__info">
              <div class="hero-card__badge" :class="{ 'badge-completed': missionCompletedToday }">
                {{ missionCompletedToday ? 'CONCLUÍDA ✅' : 'RECOMENDADO' }}
              </div>
              <h3 class="hero-card__title">
                {{ missionCompletedToday ? 'Ir para o Estúdio' : 'Desafio ENEM' }}
              </h3>
              <p class="hero-card__desc">
                {{ missionCompletedToday ? 'Missão de hoje cumprida! Revise suas obras.' : 'Quatro questões pra hoje!' }}
              </p>
            </div>
            
            <div class="hero-card__action">
              <div class="hero-play-btn" :class="{ 'btn-completed': missionCompletedToday }">
                <font-awesome-icon :icon="missionCompletedToday ? 'headphones' : 'play'" />
              </div>
            </div>

          </div>
        </button>
      </div>

      <!-- 3. PAINEL DA TURNÊ (Substitui a Chama!) 🚌🎶 -->
      <div class="home__tour-status animate-slide-up" style="animation-delay: 0.2s;">
        <div class="tour-card">
          
          <!-- O Ônibus da Banda (Status Atual) -->
          <div class="tour-main">
            <div class="tour-bus-wrapper" :class="{ 'on-the-road': userStreak > 0 }">
              <span class="bus-icon">🚌</span>
              <span v-if="userStreak > 0" class="music-notes">🎶</span>
            </div>
            <div class="tour-texts">
              <span class="tour-title">
                {{ userStreak > 0 ? `${userStreak} ${userStreak === 1 ? 'Dia em Turnê!' : 'Dias em Turnê!'}` : 'Van estacionada...' }}
              </span>
              <span class="tour-subtitle">
                {{ userStreak > 0 ? 'O show não pode parar! 🎸' : 'Cumpra a missão e pegue a estrada! 🚌' }}
              </span>
            </div>
          </div>

          <!-- Divisória Elegante -->
          <div class="tour-divider-horizontal"></div>

          <!-- Métricas de Sucesso (Recorde e Pontos) -->
          <div class="tour-stats">
            <!-- Recorde -->
            <div class="stat-item">
              <div class="stat-icon-wrapper record-bg">
                <span class="stat-icon">🏆</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ userRecord }} {{ userRecord === 1 ? 'dia' : 'dias' }}</span>
                <span class="stat-label">Turnê Recorde</span>
              </div>
            </div>

            <div class="stat-divider-vertical"></div>

            <!-- Pontos -->
            <div class="stat-item">
              <div class="stat-icon-wrapper points-bg">
                <span class="stat-icon">⭐</span>
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ userPoints }}</span>
                <span class="stat-label">Pontos Totais</span>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- 4. BANNER E-BOOK HOTMART (Conversão Principal) -->
      <div class="home__ebook-banner animate-slide-up" style="animation-delay: 0.3s;">
        <div class="ebook-content">
          <div class="ebook-icon">📚</div>
          <div class="ebook-text-area">
            <h3 class="ebook-title">E-book ProvaPop!</h3>
            <span class="badge-available">JÁ DISPONÍVEL</span>
          </div>
        </div>
        <button class="ebook-btn" @click="router.push('/ebook')">
          Garantir 🚀
        </button>
      </div>

      <!-- 5. BANNER: APOIE O PROJETO -->
      <div class="home__support-banner animate-slide-up" style="animation-delay: 0.4s;">
        <div class="support-content">
          <div class="support-icon">☕</div>
          <div class="support-text-area">
            <h3 class="support-title">Apoie o ProvaPop!</h3>
            <p class="support-desc">Pague um cafezinho para os DEVs.</p>
          </div>
        </div>
        <button class="support-btn" @click="handleSupport">
          Apoiar 
          <font-awesome-icon icon="heart" class="heart-icon" />
        </button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// ESTADO DA MISSÃO DO DIA
const missionCompletedToday = ref(false)

// LIGADO DIRETAMENTE AO BANCO DE DADOS (STORE) DO USUÁRIO
const userPoints = computed(() => authStore.user?.pontuacao || 0) 
const userStreak = computed(() => authStore.user?.ofensiva || 0)    
const userRecord = computed(() => authStore.user?.recorde_ofensiva || authStore.user?.ofensiva || 0)

const dynamicGreeting = computed(() => {
  const hour = new Date().getHours()
  let greeting = 'Boa noite'
  if (hour >= 5 && hour < 12) greeting = 'Bom dia'
  else if (hour >= 12 && hour < 18) greeting = 'Boa tarde'
  const userName = authStore.user?.nickname ? authStore.user.nickname.split(' ')[0] : 'Estudante'
  return `${greeting}, ${userName}! ✨`
})

// CHECAGEM DE STATUS DA MISSÃO AO CARREGAR A PÁGINA
async function checkMissionStatus() {
  // Lógica futura para checar com a API se a missão de hoje já foi feita
  // missionCompletedToday.value = await api.checkMission()
}

// O CLICK DO BOTÃO PRINCIPAL
function handleMissionAction() {
  if (missionCompletedToday.value) {
    // Se já respondeu, manda direto pro Estúdio!
    router.push('/jornada') 
  } else {
    // Manda para o Palco (Quiz)
    router.push({
      name: 'quiz',
      params: { prova: 'enem' }
    })
  }
}

function handleSupport() {
  alert('Que demais! 🧡 Em breve lançaremos nossa campanha de financiamento coletivo. Guarde esse café para nós! ☕')
}

// DISPARA QUANDO A PÁGINA HOME É ABERTA
onMounted(() => {
  checkMissionStatus()
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
  padding: 16px 16px 120px 16px; 
  
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
  height: 180px !important;
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
  margin-bottom: 24px;
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
}

.hero-card--completed {
  background: linear-gradient(135deg, #179B78 0%, #0c5c46 100%);
  box-shadow: 0 15px 30px rgba(23, 155, 120, 0.25);
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

.badge-completed {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
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

.btn-completed {
  color: #179B78;
}

@keyframes pulse-play {
  0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(255, 255, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}

/* --- PAINEL DA TURNÊ 🚌🎶 --- */
.home__tour-status { margin-bottom: 32px; }

.tour-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(226, 88, 34, 0.15);
  border-radius: 20px; padding: 20px; display: flex; flex-direction: column;
  backdrop-filter: blur(15px); box-shadow: 0 10px 30px rgba(139, 30, 63, 0.05);
}

.tour-main { display: flex; align-items: center; justify-content: center; gap: 16px; }

.tour-bus-wrapper {
  position: relative; width: 56px; height: 56px; background: #f5f5f5;
  border-radius: 16px; display: flex; align-items: center; justify-content: center;
  border: 2px solid #e0e0e0; transition: all 0.3s ease;
}

.bus-icon { font-size: 28px; filter: grayscale(1) opacity(0.5); transition: all 0.3s ease; }

.music-notes {
  position: absolute; top: -8px; right: -8px; font-size: 16px;
  animation: float-notes 2s infinite ease-in-out;
}

.tour-bus-wrapper.on-the-road {
  background: #FFF0E6; border-color: var(--secondary);
  box-shadow: 0 0 15px rgba(226, 88, 34, 0.2);
}

.tour-bus-wrapper.on-the-road .bus-icon {
  filter: grayscale(0) opacity(1);
  animation: drive-bus 1s infinite alternate;
}

@keyframes drive-bus {
  0% { transform: translateY(0px) rotate(-1deg); }
  100% { transform: translateY(-3px) rotate(1deg); }
}

@keyframes float-notes {
  0%, 100% { transform: translateY(0) rotate(0); opacity: 0.8; }
  50% { transform: translateY(-5px) rotate(10deg); opacity: 1; }
}

.tour-texts { display: flex; flex-direction: column; }
.tour-title { font-size: 18px; font-weight: 900; color: var(--text-main); margin-bottom: 2px; transition: color 0.3s ease; }
.tour-bus-wrapper.on-the-road + .tour-texts .tour-title { color: var(--secondary); }
.tour-subtitle { font-size: 13px; font-weight: 600; color: var(--text-muted); }

.tour-divider-horizontal { height: 1px; background: var(--border-light); margin: 16px 0; width: 100%; }
.stat-divider-vertical { width: 1px; background: var(--border-light); height: 40px; }

.tour-stats { display: flex; align-items: center; justify-content: space-around; }
.stat-item { display: flex; align-items: center; gap: 12px; flex: 1; justify-content: center; }
.stat-icon-wrapper { width: 36px; height: 36px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.record-bg { background: rgba(139, 30, 63, 0.1); }
.points-bg { background: rgba(212, 175, 55, 0.15); }
.stat-icon { font-size: 18px; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 16px; font-weight: 900; color: var(--text-main); line-height: 1.1; margin-bottom: 2px; }
.stat-label { font-size: 10px; font-weight: 800; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }

/* --- BANNER E-BOOK --- */
.home__ebook-banner {
  background: rgba(255, 255, 255, 0.9); border: 1px solid var(--border-light); border-radius: 20px;
  padding: 16px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;
  gap: 12px; backdrop-filter: blur(10px);
}
.ebook-content { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.ebook-icon { font-size: 28px; filter: grayscale(0.2); flex-shrink: 0; }
.ebook-text-area { flex: 1; min-width: 0; }
.ebook-title { color: var(--text-main); font-size: 15px; font-weight: 800; margin: 0 0 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.badge-available { 
  background: #179B78; 
  color: white; 
  font-size: 9px; 
  font-weight: 800; 
  padding: 3px 6px; 
  border-radius: 6px; 
  letter-spacing: 0.5px; 
  display: inline-block; 
}

.ebook-btn {
  background: rgba(23, 155, 120, 0.15); 
  color: #0c5c46; 
  border: none; 
  width: 40%; 
  min-width: 100px;
  padding: 12px 10px; 
  border-radius: 10px; 
  font-weight: 800; 
  font-size: 12px; 
  cursor: pointer; 
  flex-shrink: 0;
  display: flex; 
  align-items: center; 
  justify-content: center; 
  transition: all 0.2s ease;
}

.ebook-btn:hover { background: rgba(23, 155, 120, 0.25); }
.ebook-btn:active { transform: scale(0.95); }

/* --- BANNER APOIO --- */
.home__support-banner {
  background: linear-gradient(135deg, #fff0eb 0%, #ffe4d6 100%); border: 1px solid rgba(226, 88, 34, 0.2);
  border-radius: 20px; padding: 16px 20px; margin-bottom: 24px; display: flex; align-items: center;
  justify-content: space-between; gap: 12px; box-shadow: 0 4px 15px rgba(226, 88, 34, 0.08);
}
.support-content { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.support-icon { font-size: 32px; flex-shrink: 0; animation: float-coffee 3s ease-in-out infinite; }
@keyframes float-coffee { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
.support-text-area { flex: 1; min-width: 0; }
.support-title { color: var(--secondary); font-size: 15px; font-weight: 900; margin: 0 0 2px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.support-desc { color: var(--text-muted); font-size: 11px; font-weight: 600; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.support-btn {
  background: var(--secondary); color: #fff; border: none; width: 40%; min-width: 100px;
  padding: 12px 10px; border-radius: 10px; font-weight: 800; font-size: 12px; cursor: pointer; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 4px 10px rgba(226, 88, 34, 0.3); transition: all 0.2s ease;
}
.support-btn:active { transform: scale(0.95); }
.heart-icon { font-size: 12px; }
.support-btn:hover .heart-icon { animation: beat 1s infinite; }
@keyframes beat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.2); } }

/* Responsividade Básica */
@media (min-width: 768px) {
  .home { padding: 32px 32px 140px 32px; }
  .home__container { max-width: 600px; }
  .hero-card__title { font-size: 32px; }
}
</style>
