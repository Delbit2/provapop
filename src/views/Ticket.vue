<template>
  <div class="ticket-page">
    <Transition name="fade" appear>
      <div class="ticket-container">
        
        <!-- CABEÇALHO -->
        <div class="ticket-header">
          <p class="ticket-header__subtitle">Seu Passe VIP 🎫</p>
          <h1 class="ticket-header__title">Venha para o Show!</h1>
        </div>

        <!-- O INGRESSO FÍSICO (TICKET) -->
        <div class="ticket-wrapper">
          <!-- Adicionamos o ref="ticketRef" aqui para a "câmera" saber o que fotografar -->
          <div ref="ticketRef" class="ticket-card">
            
            <!-- Marca D'água de Exclusividade -->
            <div class="ticket-card__watermark">VIP</div>

            <!-- Efeito holográfico de brilho (Reflexo 3D metálico) -->
            <div class="ticket-card__shine"></div>

            <!-- Linha Interna de acabamento do padrão de segurança -->
            <div class="ticket-card__inner-line"></div>

            <!-- PARTE SUPERIOR DO INGRESSO -->
            <div class="ticket-card__top">
              <!-- BADGE AZUL EXCLUSIVO -->
              <div class="ticket-card__badge">ACESSO EXCLUSIVO</div>
              
              <!-- Logo Flutuante -->
              <img src="@/assets/logo.png" alt="ProvaPop! Logo" class="ticket-card__logo" />
              
              <!-- SLOGAN MAIS MODERNO -->
              <h2 class="ticket-card__slogan">Sua nota mais alta<br>no vestibular!</h2>
            </div>

            <!-- PICOTE (LINHA TRACEJADA DIVISÓRIA) -->
            <div class="ticket-card__divider"></div>

            <!-- PARTE INFERIOR (CANHOTO COM QR CODE) -->
            <div class="ticket-card__bottom">
              <div class="ticket-card__qr-wrapper">
                <img src="@/assets/qrcode.png" alt="QR Code ProvaPop" class="ticket-card__qr" />
              </div>
              <p class="ticket-card__url">provapop.com.br</p>
              <p class="ticket-card__serial">TKT-{{ serialNumber }} • SCAN TO PLAY</p>
            </div>
            
          </div>
        </div>

        <!-- BOTÕES DE AÇÃO (Estilo Duolingo: Compartilhamento Nativo) -->
        <div class="ticket-actions">
          <button @click="shareTicket" class="btn-primary" :disabled="isSharing">
            <font-awesome-icon :icon="isSharing ? 'spinner' : 'share-nodes'" :class="{ 'fa-spin': isSharing }" /> 
            {{ isSharing ? 'Gerando ingresso...' : 'Compartilhar Ingresso' }}
          </button>
        </div>

      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import html2canvas from 'html2canvas'

// Referência para o elemento HTML que vamos transformar em imagem
const ticketRef = ref<HTMLElement | null>(null)

// Controle de estado do botão (para não clicar duas vezes rápido)
const isSharing = ref(false)

// Gerador de Número de Série único para dar realismo ao ingresso
const serialNumber = ref(
  Math.random().toString(36).substring(2, 8).toUpperCase()
)

// A MÁGICA DO COMPARTILHAMENTO NATIVO (ESTILO DUOLINGO)
async function shareTicket() {
  if (!ticketRef.value || isSharing.value) return

  try {
    isSharing.value = true

    // 1. html2canvas tira uma "foto" do ingresso
    const canvas = await html2canvas(ticketRef.value, {
      scale: 2, // Escala 2x garante que o PNG fique em alta resolução (Retina Display)
      useCORS: true, // Permite carregar as imagens (como a Logo e o QR Code)
      backgroundColor: null // Mantém o fundo transparente para respeitar as bordas arredondadas
    })

    // 2. Converte o Canvas (foto) em um arquivo de imagem (Blob/PNG)
    canvas.toBlob(async (blob) => {
      if (!blob) throw new Error('Falha ao processar a imagem do ingresso')

      // Cria um objeto de "Arquivo" pronto para envio
      const file = new File([blob], 'meu-ingresso-provapop.png', { type: 'image/png' })

      // 3. Tenta abrir a gaveta de compartilhamento nativa do celular (iOS/Android)
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({
          title: 'Meu Ingresso VIP - ProvaPop!',
          text: 'Acabei de garantir meu ingresso para a melhor nota no ENEM! 🎫🎸 Vem pro show também: provapop.com.br',
          files: [file]
        })
      } else {
        // FALLBACK: Se estiver num PC ou navegador antigo que não suporta compartilhar arquivo
        // O sistema baixa a imagem automaticamente para a pessoa!
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'meu-ingresso-provapop.png'
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        alert('Seu ingresso foi salvo no seu dispositivo! Compartilhe com a galera! 📸')
      }
    }, 'image/png')

  } catch (error) {
    console.error('Erro ao compartilhar:', error)
    alert('Oops! Tivemos um problema ao gerar o PNG. Mas você ainda pode tirar um Print dessa tela! 📸')
  } finally {
    // Libera o botão novamente
    isSharing.value = false
  }
}
</script>

<style scoped>
.ticket-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 20px 120px 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
  overflow: hidden;
}

.ticket-container {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.ticket-header {
  text-align: center;
  margin-bottom: 32px;
}

.ticket-header__subtitle {
  font-size: 14px;
  font-weight: 800;
  color: #E25822;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 8px 0;
}

.ticket-header__title {
  font-size: 28px;
  font-weight: 900;
  color: #8B1E3F;
  margin: 0;
  letter-spacing: -0.5px;
}

/* =========================================
   O INGRESSO PLATINUM MÁGICO
   ========================================= */

.ticket-wrapper {
  filter: drop-shadow(0 20px 40px rgba(139, 30, 63, 0.2));
  transition: transform 0.3s ease;
}

.ticket-wrapper:hover {
  transform: translateY(-5px);
}

.ticket-card {
  width: 310px;
  height: 520px;
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 20%, #e4e4e4 50%, #ffffff 80%, #dcdcdc 100%);
  
  -webkit-mask-image: radial-gradient(circle at 0 360px, transparent 16px, black 16.5px),
                      radial-gradient(circle at 100% 360px, transparent 16px, black 16.5px);
  -webkit-mask-size: 51% 100%;
  -webkit-mask-position: left, right;
  -webkit-mask-repeat: no-repeat;
  
  mask-image: radial-gradient(circle at 0 360px, transparent 16px, black 16.5px),
              radial-gradient(circle at 100% 360px, transparent 16px, black 16.5px);
  mask-size: 51% 100%;
  mask-position: left, right;
  mask-repeat: no-repeat;
  
  border-radius: 16px;
  overflow: hidden;
}

/* Marca d'água no fundo do ingresso */
.ticket-card__watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  font-size: 130px;
  font-weight: 900;
  color: rgba(29, 78, 216, 0.1); 
  pointer-events: none;
  z-index: 1;
}

/* Malha de segurança (Guilloche) em todo o fundo */
.ticket-card__mesh {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: 
    repeating-linear-gradient(45deg, rgba(29, 78, 216, 0.04) 0px, rgba(29, 78, 216, 0.04) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, rgba(29, 78, 216, 0.04) 0px, rgba(29, 78, 216, 0.04) 1px, transparent 1px, transparent 10px);
  z-index: 1;
  pointer-events: none;
}

/* O reflexo de luz que passa por cima */
.ticket-card__shine {
  position: absolute;
  top: 0; left: -100%;
  width: 50%; height: 100%;
  background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-20deg);
  animation: hologramShine 5s infinite;
  z-index: 10;
  pointer-events: none;
}

@keyframes hologramShine {
  0% { left: -100%; }
  20% { left: 200%; }
  100% { left: 200%; }
}

/* Nova Borda Hachurada de Segurança (Marcas Metálicas Anticópia) */
.ticket-card__security-border {
  position: absolute;
  top: 10px; left: 10px; right: 10px; bottom: 10px;
  border-radius: 12px;
  padding: 5px; 
  
  background: repeating-linear-gradient(
    -45deg,
    rgba(255, 255, 255, 0.8) 0px,
    rgba(255, 255, 255, 0.8) 3px,
    rgba(29, 78, 216, 0.2) 3px,
    rgba(29, 78, 216, 0.2) 6px
  );
  
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  
  pointer-events: none;
  z-index: 2;
  box-shadow: inset 0 0 8px rgba(0,0,0,0.1);
}

/* Linha contínua por dentro da hachura, pra dar o acabamento gráfico */
.ticket-card__inner-line {
  position: absolute;
  top: 17px; left: 17px; right: 17px; bottom: 17px;
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px rgba(29, 78, 216, 0.08);
  pointer-events: none;
  z-index: 2;
}

/* --- PARTE SUPERIOR --- */
.ticket-card__top {
  height: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  text-align: center;
  position: relative;
  z-index: 5;
}

/* BADGE AZUL MODERNIZADO */
.ticket-card__badge {
  font-size: 10px;
  font-weight: 800;
  color: #fff;
  background: #1D4ED8; 
  padding: 6px 14px;
  border-radius: 20px;
  letter-spacing: 2px;
  margin-bottom: 24px;
  box-shadow: 0 4px 10px rgba(29, 78, 216, 0.3);
}

.ticket-card__logo {
  max-width: 170px;
  height: auto;
  margin-bottom: 28px;
  animation: float 6s ease-in-out infinite;
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
}

@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
  100% { transform: translateY(0px); }
}

/* SLOGAN COM NOVA FONTE E ESTILO MODERNIZADO */
.ticket-card__slogan {
  font-family: 'Montserrat', 'Helvetica Neue', system-ui, sans-serif;
  font-size: 22px;
  font-weight: 800;
  color: #5d142a;
  line-height: 1.2;
  margin: 0;
  letter-spacing: -0.5px;
  text-shadow: 1px 1px 0px rgba(255,255,255,0.8);
}

/* --- DIVISÓRIA --- */
.ticket-card__divider {
  position: absolute;
  top: 360px;
  left: 20px;
  right: 20px;
  border-top: 2px dashed rgba(45, 36, 34, 0.3);
  z-index: 6; 
}

/* --- PARTE INFERIOR --- */
.ticket-card__bottom {
  height: 160px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 24px;
  position: relative;
  z-index: 5;
}

.ticket-card__qr-wrapper {
  background: #fff;
  padding: 6px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  margin-bottom: 12px;
  border: 1px solid #e8dedc;
}

.ticket-card__qr {
  width: 64px;
  height: 64px;
  display: block;
}

.ticket-card__url {
  font-size: 16px;
  font-weight: 900;
  color: #2d2422;
  letter-spacing: 1.5px;
  margin: 0 0 4px 0;
}

.ticket-card__serial {
  font-size: 9px;
  font-weight: 700;
  color: #8B1E3F;
  letter-spacing: 1px;
  margin: 0;
  opacity: 0.8;
}

/* =========================================
   BOTÕES DE AÇÃO
   ========================================= */
.ticket-actions {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  width: 100%;
  max-width: 310px; /* Mesma largura do ingresso para alinhar perfeito! */
}

.btn-primary {
  width: 100%;
  padding: 14px 0;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  background: linear-gradient(135deg, #8B1E3F 0%, #E25822 100%);
  color: #ffffff;
  box-shadow: 0 6px 20px rgba(226, 88, 34, 0.25);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(139, 30, 63, 0.35);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(1px);
}

.btn-primary:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #64748b 100%);
  cursor: not-allowed;
  box-shadow: none;
}

/* Animações */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(20px); }
.fade-leave-to { opacity: 0; transform: translateY(-20px); }

@media (min-width: 768px) {
  .ticket-page { padding-bottom: 140px; }
}
</style>
