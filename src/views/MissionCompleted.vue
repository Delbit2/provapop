<template>
  <div class="mission-completed">
    <div class="mc__container">
      <div class="mc__content animate-slide-up">
        <div class="mc__header">
          <div class="mc__trophy-wrapper">
            <img src="@/assets/logogold1.png" alt="Troféu ProvaPop" class="mc__trophy-img" />
          </div>
        </div>

        <div
          ref="shareCardRef"
          class="mc__share-wrapper"
          style="background: #FFFFFF; border-radius: 24px; padding: 16px; margin-bottom: 24px;"
        >
          <div class="mc__header" style="margin-bottom: 16px;">
            <div class="mc__tag" style="margin-bottom: 8px;">HIT CONCLUÍDO 👏</div>
            <h1 class="mc__title" style="font-size: 32px;">Dei um Show!</h1>
          </div>

          <div class="mc__stats-card" style="box-shadow: none; border: 1px solid rgba(226, 88, 34, 0.15); margin-bottom: 16px;">
            <div class="mc__stat-row">
              <div class="mc__stat-item">
                <span class="mc__stat-icon gold">⚡</span>
                <span class="mc__stat-value text-gold">+{{ finalScore }}</span>
                <span class="mc__stat-label">Pontos</span>
              </div>
              <div class="mc__stat-divider"></div>
              <div class="mc__stat-item">
                <span class="mc__stat-icon success">🎯</span>
                <span class="mc__stat-value text-success">{{ precisionText }}</span>
                <span class="mc__stat-label">Precisão</span>
              </div>
              <div class="mc__stat-divider"></div>
              <div class="mc__stat-item">
                <span class="mc__stat-icon orange">🔥</span>
                <span class="mc__stat-value text-orange">{{ userStreakFormatted }}</span>
                <span class="mc__stat-label">Em Turnê</span>
              </div>
            </div>
          </div>

          <div class="mc__vip-ticket" style="margin-bottom: 0; box-shadow: none;">
            <div class="mc__ticket-user">
              <div class="mc__user-avatar">
                <font-awesome-icon icon="headphones" />
              </div>
              <div class="mc__user-info">
                <span class="mc__user-name">{{ userName }}</span>
                <span class="mc__app-tag">Jogando ProvaPop</span>
              </div>
            </div>

            <div class="mc__ticket-divider"></div>

            <div class="mc__ticket-scan">
              <img
                src="@/assets/URL_playprovapopcombr.png"
                alt="Escaneie para jogar o ProvaPop"
                class="mc__qr-code-img"
              />
            </div>
          </div>
        </div>

        <div class="mc__actions animate-slide-up" style="animation-delay: 1s;">
          <Button
            variant="primary"
            size="lg"
            full-width
            @click="shareVictory"
            class="btn-share"
            :disabled="isSharing"
          >
            <font-awesome-icon v-if="!isSharing" icon="share-alt" class="share-icon" />
            <span v-if="!isSharing">Compartilhar o Hit</span>
            <span v-else>Preparando imagem... 📸</span>
          </Button>

          <Button
            variant="secondary"
            size="md"
            full-width
            @click="goToRanking"
            class="btn-ranking"
          >
            <font-awesome-icon icon="trophy" style="margin-right: 8px;" />
            Ver Ranking
          </Button>

          <Button
            variant="secondary"
            size="md"
            full-width
            @click="goHome"
            class="btn-home"
          >
            <font-awesome-icon icon="door-open" style="margin-right: 8px;" />
            Voltar para o Camarim
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import confetti from 'canvas-confetti'
import Button from '@/components/Button.vue'
import html2canvas from 'html2canvas'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const shareCardRef = ref<HTMLElement | null>(null)
const isSharing = ref(false)

const userName = computed(() => {
  return authStore.user?.nickname || 'Estudante Pop'
})

const finalScore = computed(() => {
  const raw = route.query.pontos

  if (Array.isArray(raw)) {
    return raw[0] || '0'
  }

  if (typeof raw === 'string') {
    return raw
  }

  return '0'
})

const precisionText = computed(() => {
  const totalRespondidas = authStore.user?.total_respondidas ?? 0
  const totalAcertos = authStore.user?.total_acertos ?? 0

  if (!totalRespondidas) return '0%'

  const precision = Math.round((totalAcertos / totalRespondidas) * 100)
  return `${precision}%`
})

const userStreakFormatted = computed(() => {
  const streak = authStore.user?.ofensiva || 0
  return streak === 1 ? '1 Dia' : `${streak} Dias`
})

function triggerVictoryConfetti() {
  const duration = 4000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 }

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min
  }

  confetti({
    particleCount: 150,
    spread: 100,
    origin: { y: 0.6 },
    colors: ['#D4AF37', '#E25822', '#8B1E3F', '#2ACEA4']
  })

  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now()
    if (timeLeft <= 0) {
      clearInterval(interval)
      return
    }

    const particleCount = 50 * (timeLeft / duration)

    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#D4AF37', '#8B1E3F', '#E25822']
    })

    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#D4AF37', '#8B1E3F', '#E25822']
    })
  }, 250)
}

function canvasToBlob(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob)
      } else {
        reject(new Error('Falha ao gerar a imagem'))
      }
    }, 'image/png')
  })
}

async function shareVictory() {
  if (isSharing.value || !shareCardRef.value) return

  try {
    isSharing.value = true

    const canvas = await html2canvas(shareCardRef.value, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true
    })

    const blob = await canvasToBlob(canvas)
    const file = new File([blob], 'provapop-show.png', { type: 'image/png' })
    const filesArray = [file]

    const shareData: any = {
      title: 'Dei um show no ProvaPop!',
      text: `Acabei de fazer ${finalScore.value} pontos no palco do ProvaPop! 🎤✨ Vem jogar e garanta seu ingresso pra aprovação!`,
      url: 'https://provapop.com.br'
    }

    if (navigator.canShare && navigator.canShare({ files: filesArray })) {
      shareData.files = filesArray
    }

    if (navigator.share) {
      await navigator.share(shareData)
    } else {
      alert('Seu navegador não suporta envio direto. Mas você arrasou!')
    }
  } catch (err: any) {
    if (err?.name !== 'AbortError') {
      console.error('Erro no compartilhamento:', err)
      alert('Tire um print dessa tela lindona e poste nos seus Stories marcando a gente! 📸✨')
    }
  } finally {
    isSharing.value = false
  }
}

const goToRanking = () => router.push('/ranking')
const goHome = () => router.push('/')

onMounted(async () => {
  if (authStore.fetchUserProfile) {
    await authStore.fetchUserProfile()
  }

  setTimeout(() => {
    triggerVictoryConfetti()
  }, 300)
})
</script>

<style scoped>
.mission-completed {
  --primary: #8B1E3F; 
  --text-muted: #665651; 
  --gold: #D4AF37;
  --success: #2ACEA4;
  --orange: #E25822;

  min-height: 100vh;
  width: 100vw;
  background: linear-gradient(180deg, #FFFFFF 0%, #FFFFFF 50%, #FCF2EE 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 40px 24px;
  overflow-y: auto; 
  overflow-x: hidden;
}

.mc__container { width: 100%; max-width: 400px; position: relative; z-index: 10; padding: 20px 0; margin-bottom: 40px; }
.mc__content { display: flex; flex-direction: column; align-items: center; width: 100%; }

.mc__header { text-align: center; display: flex; flex-direction: column; align-items: center; }
.mc__trophy-wrapper { position: relative; width: 340px; height: 280px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; animation: floatTrophy 4s ease-in-out infinite; }
.mc__trophy-img { width: 320px; height: auto; position: relative; z-index: 2; filter: drop-shadow(0 15px 25px rgba(212, 175, 55, 0.25)); }
.mc__tag { background: rgba(139, 30, 63, 0.08); color: var(--primary); padding: 6px 16px; border-radius: 20px; font-size: 12px; font-weight: 900; letter-spacing: 2px; border: 1px solid rgba(139, 30, 63, 0.1); }
.mc__title { color: var(--primary); font-weight: 900; margin: 0; letter-spacing: -1px; }
.mc__stats-card { width: 100%; background: #ffffff; border-radius: 24px; padding: 24px; }
.mc__stat-row { display: flex; justify-content: space-between; align-items: center; }
.mc__stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px; }
.mc__stat-divider { width: 1px; height: 40px; background: rgba(139, 30, 63, 0.1); }
.mc__stat-icon { font-size: 20px; }
.mc__stat-value { font-size: 22px; font-weight: 900; line-height: 1; }
.text-gold { color: #B58500; } 
.text-success { color: #179B78; }
.text-orange { color: var(--orange); }
.mc__stat-label { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }

.mc__vip-ticket { width: 100%; display: flex; align-items: center; justify-content: space-between; background: #ffffff; padding: 16px 20px; border-radius: 20px; border: 1px dashed rgba(212, 175, 55, 0.4); }
.mc__ticket-user { display: flex; align-items: center; gap: 12px; flex: 1; }
.mc__user-avatar { width: 42px; height: 42px; background: rgba(139, 30, 63, 0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--primary); font-size: 18px; }
.mc__user-info { display: flex; flex-direction: column; align-items: flex-start; }
.mc__user-name { color: var(--primary); font-weight: 800; font-size: 15px; max-width: 130px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mc__app-tag { color: var(--orange); font-size: 11px; font-weight: 700; }
.mc__ticket-divider { width: 1px; height: 90px; background: repeating-linear-gradient(to bottom, transparent, transparent 4px, rgba(226, 88, 34, 0.2) 4px, rgba(226, 88, 34, 0.2) 8px); margin: 0 16px; }
.mc__ticket-scan { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.mc__qr-code-img { width: 84px; height: 84px; object-fit: contain; border-radius: 8px; mix-blend-mode: multiply; }

.mc__actions { width: 100%; display: flex; flex-direction: column; gap: 16px; }
.btn-share { background: linear-gradient(135deg, #D4AF37 0%, #E25822 100%) !important; color: #ffffff !important; border: none !important; border-radius: 20px !important; font-weight: 900 !important; font-size: 18px !important; padding: 20px !important; text-transform: uppercase; letter-spacing: 0.5px; box-shadow: 0 10px 25px rgba(226, 88, 34, 0.3) !important; display: flex; align-items: center; justify-content: center; gap: 10px; position: relative; overflow: hidden; transition: all 0.3s ease; }
.btn-home { background: #FFF0E6 !important; color: var(--orange) !important; border: 2px solid rgba(226, 88, 34, 0.2) !important; border-radius: 20px !important; font-weight: 800 !important; font-size: 16px !important; }
.btn-ranking { background: #FFF9E6 !important; color: #D4AF37 !important; border: 2px solid rgba(212, 175, 55, 0.4) !important; border-radius: 20px !important; font-weight: 800 !important; font-size: 16px !important; }

@keyframes floatTrophy { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
.animate-slide-up { opacity: 0; transform: translateY(30px); animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-fade-in { opacity: 0; animation: fadeIn 0.8s ease forwards; }
@keyframes slideUp { to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { to { opacity: 1; } }
</style>
