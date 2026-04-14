<template>
  <div class="mission-completed">
    <div class="mc__container">
      
      <!-- Efeito de Brilho de Fundo -->
      <div class="mc__glow-bg"></div>

      <div class="mc__content animate-slide-up">
        
        <!-- HEADER (Troféu e Títulos) -->
        <div class="mc__header">
          <div class="mc__trophy-wrapper">
            <div class="mc__trophy-glow"></div>
            <font-awesome-icon icon="trophy" class="mc__trophy-icon" />
          </div>
          
          <div class="mc__tag animate-fade-in" style="animation-delay: 0.3s;">MISSÃO CUMPRIDA</div>
          <h1 class="mc__title animate-fade-in" style="animation-delay: 0.4s;">Você Arrasou!</h1>
          <p class="mc__subtitle animate-fade-in" style="animation-delay: 0.5s;">
            Mais um passo dado rumo à sua aprovação.
          </p>
        </div>

        <!-- CARD DE ESTATÍSTICAS (Vidro Fosco Premium) -->
        <div class="mc__stats-card animate-slide-up" style="animation-delay: 0.6s;">
          <div class="mc__stat-row">
            <div class="mc__stat-item">
              <span class="mc__stat-icon gold">⚡</span>
              <span class="mc__stat-value text-gold">+150</span>
              <span class="mc__stat-label">Pontos Ganhos</span>
            </div>
            <div class="mc__stat-divider"></div>
            <div class="mc__stat-item">
              <span class="mc__stat-icon success">🎯</span>
              <span class="mc__stat-value text-success">100%</span>
              <span class="mc__stat-label">Precisão</span>
            </div>
            <div class="mc__stat-divider"></div>
            <div class="mc__stat-item">
              <span class="mc__stat-icon orange">🔥</span>
              <span class="mc__stat-value text-orange">4 Dias</span>
              <span class="mc__stat-label">Ofensiva</span>
            </div>
          </div>
        </div>

        <!-- SELO DO JOGADOR (Para ficar bonito no Print) -->
        <div class="mc__user-badge animate-fade-in" style="animation-delay: 0.8s;">
          <div class="mc__user-avatar">
            <font-awesome-icon icon="user-astronaut" />
          </div>
          <div class="mc__user-info">
            <span class="mc__user-name">{{ userName }}</span>
            <span class="mc__app-tag">@ProvaPop</span>
          </div>
        </div>

        <!-- AÇÕES -->
        <div class="mc__actions animate-slide-up" style="animation-delay: 1s;">
          <Button 
            variant="primary" 
            size="lg" 
            full-width 
            @click="shareVictory"
            class="btn-share"
          >
            <font-awesome-icon icon="share-alt" class="share-icon" /> 
            Compartilhar Vitória
          </Button>
          
          <Button 
            variant="secondary" 
            size="md" 
            full-width 
            @click="goHome"
            class="btn-home"
          >
            Voltar ao QG
          </Button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import confetti from 'canvas-confetti'
import Button from '@/components/Button.vue'

const router = useRouter()
const authStore = useAuthStore()

// Pega o nome do usuário para o "Selo" do print
const userName = computed(() => {
  return authStore.user?.nickname || 'Estudante Pop'
})

// MÁGICA DOS CONFETES DA VITÓRIA 🎉
const triggerVictoryConfetti = () => {
  const duration = 4000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min;
  }

  // Explosão inicial
  confetti({
    particleCount: 150,
    spread: 100,
    origin: { y: 0.6 },
    colors: ['#D4AF37', '#E25822', '#ffffff', '#2ACEA4']
  });

  // Chuva contínua
  const interval: any = setInterval(function() {
    const timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
      return clearInterval(interval);
    }

    const particleCount = 50 * (timeLeft / duration);
    confetti({
      ...defaults, particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#D4AF37', '#ffffff', '#E25822']
    });
    confetti({
      ...defaults, particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#D4AF37', '#ffffff', '#E25822']
    });
  }, 250);
}

// COMPARTILHAMENTO NATIVO 📱
const shareVictory = async () => {
  const shareData = {
    title: 'Missão Cumprida no ProvaPop!',
    text: `Acabei de gabaritar mais uma missão no ProvaPop! 🚀 Vem estudar comigo!`,
    url: 'https://provapop.com.br' // Troque pela URL real do seu app depois
  }

  try {
    if (navigator.share && navigator.canShare(shareData)) {
      await navigator.share(shareData)
    } else {
      // Fallback para quem tá no PC ou browser antigo
      alert('Tire um print dessa tela lindona e poste nos seus Stories marcando a gente! 📸✨')
    }
  } catch (err) {
    console.log('Compartilhamento cancelado ou falhou', err)
  }
}

const goHome = () => {
  router.push('/')
}

onMounted(() => {
  // Dispara os confetes assim que a tela abre!
  setTimeout(() => {
    triggerVictoryConfetti()
  }, 300)
})
</script>

<style scoped>
.mission-completed {
  /* Paleta Exclusiva para esta tela */
  --mc-bg-dark: #3a0d1a;
  --mc-bg-light: #8B1E3F;
  --gold: #D4AF37;
  --success: #2ACEA4;
  --orange: #E25822;

  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, var(--mc-bg-dark) 0%, var(--mc-bg-light) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
  /* Garante que cubra tudo, ideal para stories */
  position: fixed;
  top: 0; left: 0; z-index: 1000;
}

.mc__container {
  width: 100%;
  max-width: 400px; /* Mantém a proporção fina de celular mesmo no PC */
  position: relative;
  z-index: 10;
}

/* Efeito luminoso de fundo */
.mc__glow-bg {
  position: absolute;
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0) 70%);
  border-radius: 50%;
  pointer-events: none;
  animation: pulse-glow 4s ease-in-out infinite alternate;
}

@keyframes pulse-glow {
  0% { transform: translateX(-50%) scale(1); opacity: 0.5; }
  100% { transform: translateX(-50%) scale(1.2); opacity: 1; }
}

.mc__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

/* HEADER */
.mc__header {
  text-align: center;
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mc__trophy-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

.mc__trophy-glow {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(212, 175, 55, 0.3);
  filter: blur(20px);
  border-radius: 50%;
}

.mc__trophy-icon {
  font-size: 80px;
  color: var(--gold);
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.3));
}

.mc__tag {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 2px;
  margin-bottom: 16px;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255,255,255,0.2);
}

.mc__title {
  color: #fff;
  font-size: 36px;
  font-weight: 900;
  margin: 0 0 8px 0;
  text-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.mc__subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  max-width: 80%;
}

/* STATS CARD */
.mc__stats-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 15px 35px rgba(0,0,0,0.2);
}

.mc__stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mc__stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.mc__stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
}

.mc__stat-icon { font-size: 20px; }
.mc__stat-value { font-size: 22px; font-weight: 900; line-height: 1; }
.text-gold { color: var(--gold); }
.text-success { color: var(--success); }
.text-orange { color: var(--orange); }

.mc__stat-label {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* USER BADGE */
.mc__user-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.2);
  padding: 10px 20px;
  border-radius: 30px;
  margin-bottom: 40px;
  border: 1px solid rgba(255,255,255,0.05);
}

.mc__user-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
}

.mc__user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.mc__user-name {
  color: #fff;
  font-weight: 800;
  font-size: 14px;
}

.mc__app-tag {
  color: var(--gold);
  font-size: 11px;
  font-weight: 700;
}

/* ACTIONS */
.mc__actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Botão de Share Super Premium */
.btn-share {
  background: linear-gradient(135deg, #D4AF37 0%, #AA8A25 100%) !important;
  color: #3a0d1a !important;
  border: none !important;
  border-radius: 20px !important;
  font-weight: 900 !important;
  font-size: 18px !important;
  padding: 20px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3) !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-share:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px rgba(212, 175, 55, 0.4) !important;
}

.share-icon {
  font-size: 20px;
}

.btn-home {
  background: transparent !important;
  color: rgba(255, 255, 255, 0.8) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 20px !important;
  font-weight: 700 !important;
}

.btn-home:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #fff !important;
}

/* ANIMAÇÕES */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
  100% { transform: translateY(0px); }
}

.animate-slide-up {
  opacity: 0;
  transform: translateY(30px);
  animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-fade-in {
  opacity: 0;
  animation: fadeIn 0.8s ease forwards;
}

@keyframes slideUp {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeIn {
  to { opacity: 1; }
}
</style>
