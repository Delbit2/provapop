<template>
  <div class="ranking">
    <div class="ranking__container">
      
      <!-- CABEÇALHO -->
      <div class="ranking__header animate-fade-down">
        <div class="ranking__logo-wrapper">
          <img src="@/assets/logo_login.png" alt="ProvaPop! Logo" class="ranking__logo" />
        </div>
        <h1 class="ranking__title">Parabéns, {{ userName }}! 🎉</h1>
        <p class="ranking__subtitle">A persistência é seu maior superpoder!</p>
      </div>

      <!-- CARD DE ESTATÍSTICAS (A BILLBOARD) -->
      <div class="ranking__stats-card animate-slide-up" style="animation-delay: 0.1s">
        <div class="stats-welcome">
          <h2>Billboard</h2>
        </div>

        <div class="stats-grid">
          <!-- Pontuação Destaque -->
          <div class="stat-box stat-box--main">
            <span class="stat-box__value highlight">{{ userScore }}</span>
            <span class="stat-box__label">Pontos Acumulados</span>
          </div>

          <!-- Ofensiva (Turnê!) 🚌 -->
          <div class="stat-box">
            <div class="stat-box__icon tour">
              🚌
            </div>
            <span class="stat-box__value">{{ userStreak }} {{ userStreak === 1 ? 'dia' : 'dias' }}</span>
            <span class="stat-box__label">Em Turnê</span>
          </div>

          <!-- Precisão -->
          <div class="stat-box">
            <div class="stat-box__icon target">
              <font-awesome-icon icon="bullseye" />
            </div>
            <span class="stat-box__value">{{ userAccuracy }}%</span>
            <span class="stat-box__label">Precisão</span>
          </div>

          <!-- Questões Feitas -->
          <div class="stat-box">
            <div class="stat-box__icon list">
              <font-awesome-icon icon="clipboard-list" />
            </div>
            <span class="stat-box__value">{{ totalQuizzes }}</span>
            <span class="stat-box__label">Questões Feitas</span>
          </div>

          <!-- Respostas Certas -->
          <div class="stat-box">
            <div class="stat-box__icon check">
              <font-awesome-icon icon="check-circle" />
            </div>
            <span class="stat-box__value">{{ correctAnswers }}</span>
            <span class="stat-box__label">Acertos</span>
          </div>
        </div>
      </div>

      <!-- HUB DE AÇÕES (ROLÁVEL, SEM SOBREPOSIÇÃO) -->
      <div class="ranking__actions-stack animate-slide-up" style="animation-delay: 0.2s">
        
        <!-- 1. UPSELL DIRETO: E-BOOK HOTMART -->
        <div class="action-card action-card--ebook">
          <div class="action-card__icon">📚</div>
          <div class="action-card__content">
            <span class="badge-available">JÁ DISPONÍVEL</span>
            <h3>Alcance sua maior nota!</h3>
            <p>E-book esclusivo ProvaPop!</p>
          </div>
          <button @click="router.push('/ebook')" class="btn-action btn-action--ebook">
            Garantir 🚀
          </button>
        </div>

        <!-- 2. CRESCIMENTO ORGÂNICO: COMPARTILHAR INGRESSO -->
        <div class="action-card action-card--share">
          <div class="share-content">
            <h3>Quem você convidaria pro show? 🎸</h3>
                        
            <button @click="navigate('/ingresso')" class="btn-share-highlight">
              <font-awesome-icon icon="ticket-alt" class="ticket-icon" />
              Compartilhar Ingresso VIP
            </button>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 🔥 SINCRONIZAÇÃO COM O BANCO
onMounted(async () => {
  if (typeof authStore.fetchUser === 'function') {
    await authStore.fetchUser()
  } else if (typeof authStore.getUser === 'function') {
    await authStore.getUser()
  }
})

function navigate(path: string) {
  router.push(path)
}

// 🎸 Nome do Rockstar
const userName = computed(() => authStore.user?.nome || authStore.user?.nickname || authStore.user?.name || 'Estudante VIP')

// ==========================================
// 📊 DADOS ALINHADOS COM A HOME.VUE
// ==========================================

// Pontos Acumulados
const userScore = computed(() => authStore.user?.pontuacao || authStore.user?.pontuacao_total || 0)

// Dias em Turnê
const userStreak = computed(() => authStore.user?.ofensiva || authStore.user?.ofensiva_atual || 0)

// Questões Feitas
const totalQuizzes = computed(() => authStore.user?.total_respondidas || authStore.user?.estatisticas_gamer?.total_respondidas || 0)

// Acertos Totais
const correctAnswers = computed(() => authStore.user?.total_acertos || authStore.user?.estatisticas_gamer?.total_acertos || 0)

// Precisão de Vida (%) 
const userAccuracy = computed(() => {
  if (totalQuizzes.value === 0) return 0 
  return Math.round((correctAnswers.value / totalQuizzes.value) * 100)
})

</script>

<style scoped>
/* =========================================
   ESTRUTURA PRINCIPAL
   ========================================= */
.ranking {
  min-height: 100dvh; 
  display: flex;
  flex-direction: column;
  align-items: center;
  /* Reduzi o padding-bottom porque não temos mais elementos fixos sobrepondo! */
  padding: max(3vh, 16px) 20px 120px 20px; 
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
  overflow-x: hidden;
}

.ranking__container {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 16px; 
  z-index: 10;
  flex-grow: 1; 
}

/* =========================================
   CABEÇALHO COMPRIMIDO
   ========================================= */
.ranking__header {
  text-align: center;
  margin-top: 0;
}

.ranking__logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 0px;
}

.ranking__logo {
  max-width: 180px; 
  height: auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-4px); }
  100% { transform: translateY(0px); }
}

.ranking__title {
  font-size: 26px; 
  font-weight: 900;
  color: #8B1E3F;
  margin: 0 0 2px 0;
  letter-spacing: -0.5px;
}

.ranking__subtitle {
  font-size: 15px;
  font-weight: 600;
  color: #5a4a46;
  margin: 0;
}

/* =========================================
   CARD DA BILLBOARD (OTIMIZADO)
   ========================================= */
.ranking__stats-card {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px; 
  padding: 16px; 
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
}

.stats-welcome {
  text-align: center;
  margin-bottom: 12px;
}

.stats-welcome h2 {
  font-size: 20px;
  font-weight: 800;
  color: #8B1E3F;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0; 
}

/* O GRID CIRÚRGICO */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px; 
}

.stat-box {
  background: #ffffff;
  border: 2px solid #e8dedc;
  border-radius: 14px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-box:hover {
  transform: translateY(-2px);
  border-color: #f0e6e4;
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.08);
}

.stat-box--main {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, rgba(139, 30, 63, 0.03) 0%, rgba(226, 88, 34, 0.03) 100%);
  border-color: rgba(226, 88, 34, 0.15);
  padding: 16px;
}

.stat-box__icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  margin-bottom: 6px;
}

.stat-box__icon.tour { background: rgba(226, 88, 34, 0.1); font-size: 16px; }
.stat-box__icon.target { background: rgba(139, 30, 63, 0.1); color: #8B1E3F; }
.stat-box__icon.list { background: rgba(90, 74, 70, 0.08); color: #5a4a46; }
.stat-box__icon.check { background: rgba(16, 185, 129, 0.1); color: #10b981; }

.stat-box__value {
  font-size: 18px;
  font-weight: 800;
  color: #2d2422;
  margin-bottom: 2px;
}

.stat-box__value.highlight {
  font-size: 32px;
  font-weight: 900;
  color: #8B1E3F;
  letter-spacing: -1px;
}

.stat-box__label {
  font-size: 10px;
  font-weight: 700;
  color: #8a7a77;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* =========================================
   HUB DE AÇÕES (STACK ROLÁVEL)
   ========================================= */
.ranking__actions-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 4px;
}

/* 1. Card E-book (Horizontal) */
.action-card--ebook {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(23, 155, 120, 0.2);
  border-radius: 20px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 8px 20px rgba(23, 155, 120, 0.06);
  backdrop-filter: blur(10px);
}

.action-card__icon {
  font-size: 32px;
  filter: grayscale(0.2);
  flex-shrink: 0;
  animation: float-book 3s ease-in-out infinite;
}

@keyframes float-book {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.action-card__content {
  flex: 1;
  min-width: 0;
}

.badge-available {
  background: #179B78;
  color: white;
  font-size: 9px;
  font-weight: 800;
  padding: 3px 6px;
  border-radius: 6px;
  letter-spacing: 0.5px;
  display: inline-block;
  margin-bottom: 4px;
}

.action-card__content h3 {
  font-size: 14px;
  font-weight: 900;
  color: #2d2422;
  margin: 0 0 2px 0;
  line-height: 1.1;
}

.action-card__content p {
  font-size: 11px;
  color: #5a4a46;
  margin: 0;
  line-height: 1.3;
}

.btn-action--ebook {
  background: rgba(23, 155, 120, 0.15);
  color: #0c5c46;
  border: none;
  padding: 12px 14px;
  border-radius: 12px;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.btn-action--ebook:hover { background: rgba(23, 155, 120, 0.25); transform: translateY(-1px); }
.btn-action--ebook:active { transform: scale(0.95); }

/* 2. Card Compartilhar Ingresso (Vertical / Destaque) */
.action-card--share {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 240, 235, 0.8) 100%);
  border: 1px solid rgba(226, 88, 34, 0.2);
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(139, 30, 63, 0.05);
}

.share-content h3 {
  color: #8B1E3F;
  font-size: 16px;
  font-weight: 900;
  margin: 0 0 6px 0;
  letter-spacing: -0.3px;
}

.share-content p {
  color: #5a4a46;
  font-size: 13px;
  font-weight: 600;
  margin: 0 auto 16px auto; 
  line-height: 1.4;
}

.btn-share-highlight {
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  color: #ffffff;
  border: none;
  padding: 14px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 800;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 6px 20px rgba(226, 88, 34, 0.25);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;
}

.ticket-icon {
  font-size: 16px;
  transform: rotate(-15deg);
}

.btn-share-highlight:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 30, 63, 0.35);
}

.btn-share-highlight:active {
  transform: translateY(1px);
  box-shadow: 0 3px 8px rgba(139, 30, 63, 0.2);
}

/* Efeito de luz passando no botão */
.btn-share-highlight::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%; 
  width: 50%;
  height: 100%;
  background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-25deg);
  animation: sweep-light 3s infinite; 
}

@keyframes sweep-light {
  0% { left: -100%; } 
  20% { left: 200%; } 
  100% { left: 200%; } 
}

/* =========================================
   ANIMAÇÕES E TRANSIÇÕES
   ========================================= */
.animate-slide-up { opacity: 0; transform: translateY(20px); animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-fade-down { opacity: 0; transform: translateY(-15px); animation: fadeDown 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes slideUpFade { to { opacity: 1; transform: translateY(0); } }
@keyframes fadeDown { to { opacity: 1; transform: translateY(0); } }

@media (min-width: 768px) {
  .ranking__container { max-width: 480px; }
}
</style>
