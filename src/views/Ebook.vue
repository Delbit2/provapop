<template>
  <div class="landing">
    <div class="landing__container">
      <Transition name="fade" appear>
        <div class="landing__content">
          
          <!-- CABEÇALHO -->
          <header class="landing__header animate-slide-up" style="animation-delay: 0.1s">
            <div class="badge-rebranding">NOVO NOME, NOVA EXPERIÊNCIA</div>
            <h1 class="landing__logo">ProvaPop!</h1>
            <p class="landing__subtitle">Acervo Musical Oficial</p>
          </header>

          <!-- HERO SECTION (Apresentação Principal) -->
          <section class="hero animate-slide-up" style="animation-delay: 0.2s">
            <h2 class="hero__title">O E-book definitivo para quem quer gabaritar com música!</h2>
            <p class="hero__description">
              O antigo <strong>ENEM Musical</strong> evoluiu. O método que já ajudou centenas de estudantes agora está de cara nova, totalmente atualizado e focado no seu sucesso.
            </p>

            <!-- MOCKUP DO LIVRO -->
            <div class="hero__mockup-wrapper">
              <div class="book-mockup">
                <div class="book-mockup__cover">
                  <span class="book-mockup__icon">🎧</span>
                  <span class="book-mockup__title">ProvaPop!</span>
                  <span class="book-mockup__subtitle">SONGBOOK OFICIAL</span>
                </div>
                <div class="book-mockup__pages"></div>
              </div>
            </div>

            <!-- BOTÃO DE COMPRA PRINCIPAL -->
            <button class="cta-button" @click="abrirHotmart">
              Quero garantir meu E-book 🚀
            </button>
            <p class="hero__security">
              <font-awesome-icon icon="lock" class="security-icon" /> Compra 100% segura pela Hotmart
            </p>
          </section>

          <!-- BENEFÍCIOS (Por que comprar?) -->
          <section class="features animate-slide-up" style="animation-delay: 0.3s">
            <div class="feature-card">
              <div class="feature-card__icon">🧠</div>
              <h3 class="feature-card__title">Memorização Acelerada</h3>
              <p class="feature-card__text">Associe fórmulas e conceitos complexos às melodias que não saem da sua cabeça.</p>
            </div>

            <div class="feature-card">
              <div class="feature-card__icon">🎯</div>
              <h3 class="feature-card__title">Foco no que cai</h3>
              <p class="feature-card__text">Curadoria minuciosa com as músicas e paródias dos temas mais cobrados nas provas.</p>
            </div>

            <div class="feature-card">
              <div class="feature-card__icon">📱</div>
              <h3 class="feature-card__title">Estude em qualquer lugar</h3>
              <p class="feature-card__text">Material digital otimizado para leitura no celular, tablet ou computador.</p>
            </div>
          </section>

          <!-- CALL TO ACTION FINAL -->
          <section class="final-cta animate-slide-up" style="animation-delay: 0.4s">
            <div class="final-cta__box">
              <h3>Pronto para aumentar sua nota?</h3>
              <p>Junte-se à comunidade de estudantes que hackearam os estudos com o ProvaPop!</p>
              <button class="cta-button cta-button--secondary" @click="abrirHotmart">
                Acessar o Material Agora
              </button>
            </div>
          </section>

          <!-- RODAPÉ -->
          <footer class="landing__footer">
            <p>© 2026 ProvaPop! - Todos os direitos reservados.</p>
            <button class="back-button" @click="router.push('/home')">
              <font-awesome-icon icon="arrow-left" /> Voltar para o jogo
            </button>
          </footer>

        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function abrirHotmart() {
  window.open('https://pay.hotmart.com/M101751189O?off=vhmvx202&hotfeature=51&_hi=eyJjaWQiOiIxNzYxMzM5ODUxMTE2NTkxMDgyODU5MTQyNDI4ODAwIiwiYmlkIjoiMTc2MTMzOTg1MTExNjU5MTA4Mjg1OTE0MjQyODgwMCIsInNpZCI6IjhhZDdhYWJlOGRmYjQxNGI4N2I4M2ZkMDY0MDgwODA3In0=.1777250703902&bid=1777250707788', '_blank')
}
</script>

<style scoped>
/* =========================================
   ESTRUTURA PRINCIPAL (Alinhado ao ProvaPop!)
   ========================================= */
.landing {
  min-height: 100dvh;
  padding: 40px 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 30%, #fcf2ee 60%, #ebd2cb 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.landing__container {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  z-index: 10;
}

.landing__content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* =========================================
   CABEÇALHO
   ========================================= */
.landing__header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.badge-rebranding {
  background: #179B78;
  color: white;
  font-size: 10px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 12px;
  letter-spacing: 1px;
  margin-bottom: 4px;
}

.landing__logo {
  font-size: 36px;
  font-weight: 900;
  color: #8B1E3F; /* Cor principal ProvaPop! */
  margin: 0;
  letter-spacing: -1px;
}

.landing__subtitle {
  font-size: 14px;
  font-weight: 700;
  color: #b5a9a7;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0;
}

/* =========================================
   HERO SECTION
   ========================================= */
.hero {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero__title {
  font-size: 24px;
  font-weight: 800;
  color: #2d2422;
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.hero__description {
  font-size: 15px;
  color: #5a4a46;
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.hero__description strong {
  color: #E25822; /* Laranja ProvaPop! */
}

/* O LIVRO (Feito em CSS puro para carregar instantaneamente) */
.hero__mockup-wrapper {
  margin: 20px 0 32px 0;
  perspective: 1000px;
}

.book-mockup {
  width: 160px;
  height: 220px;
  position: relative;
  transform: rotateY(-15deg) rotateX(5deg);
  transform-style: preserve-3d;
  transition: transform 0.5s ease;
  box-shadow: 15px 15px 30px rgba(0,0,0,0.15);
  border-radius: 4px 12px 12px 4px;
}

.book-mockup:hover {
  transform: rotateY(-5deg) rotateX(0deg) translateY(-5px);
}

.book-mockup__cover {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #8B1E3F 0%, #5a1228 100%);
  border-radius: 4px 12px 12px 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 2;
  border-left: 4px solid #5a1228;
}

.book-mockup__icon { font-size: 40px; margin-bottom: 10px; }
.book-mockup__title { font-size: 20px; font-weight: 900; letter-spacing: -0.5px; }
.book-mockup__subtitle { font-size: 8px; font-weight: 700; letter-spacing: 1px; margin-top: 4px; opacity: 0.8; }

.book-mockup__pages {
  position: absolute;
  top: 4px;
  right: -8px;
  width: 100%;
  height: calc(100% - 8px);
  background: #f4f4f4;
  border-radius: 0 10px 10px 0;
  z-index: 1;
  transform: translateZ(-10px);
  border-right: 1px solid #ddd;
}

/* =========================================
   BOTÕES DE AÇÃO
   ========================================= */
.cta-button {
  width: 100%;
  max-width: 320px;
  padding: 18px 24px;
  background: #E25822; /* Laranja de conversão */
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(226, 88, 34, 0.4);
  transition: all 0.3s ease;
  animation: pulse 2s infinite;
}

.cta-button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 30px rgba(226, 88, 34, 0.5);
  animation: none;
}

.cta-button--secondary {
  background: #8B1E3F;
  box-shadow: 0 8px 25px rgba(139, 30, 63, 0.3);
  animation: none;
  margin-top: 16px;
}

.cta-button--secondary:hover {
  box-shadow: 0 12px 30px rgba(139, 30, 63, 0.4);
}

.hero__security {
  font-size: 11px;
  color: #5a4a46;
  margin-top: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.security-icon { color: #179B78; }

/* =========================================
   BENEFÍCIOS (CARDS)
   ========================================= */
.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.03);
  transition: transform 0.3s ease;
}

.feature-card:hover { transform: translateY(-3px); }
.feature-card__icon { font-size: 32px; margin-bottom: 12px; }
.feature-card__title { font-size: 16px; font-weight: 800; color: #8B1E3F; margin: 0 0 8px 0; }
.feature-card__text { font-size: 13px; color: #5a4a46; margin: 0; line-height: 1.4; }

/* =========================================
   BOX FINAL
   ========================================= */
.final-cta__box {
  background: linear-gradient(135deg, #fffafa 0%, #fcedea 100%);
  border: 2px solid rgba(139, 30, 63, 0.1);
  padding: 32px 20px;
  border-radius: 24px;
  text-align: center;
}

.final-cta__box h3 { font-size: 20px; font-weight: 900; color: #8B1E3F; margin: 0 0 12px 0; }
.final-cta__box p { font-size: 14px; color: #5a4a46; margin: 0; line-height: 1.4; }

/* =========================================
   RODAPÉ
   ========================================= */
.landing__footer {
  margin-top: 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.landing__footer p { font-size: 11px; color: #b5a9a7; margin: 0; }

.back-button {
  background: transparent;
  border: none;
  color: #8B1E3F;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.back-button:hover { background: rgba(139, 30, 63, 0.1); }

/* =========================================
   ANIMAÇÕES
   ========================================= */
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(226, 88, 34, 0.4); }
  70% { box-shadow: 0 0 0 15px rgba(226, 88, 34, 0); }
  100% { box-shadow: 0 0 0 0 rgba(226, 88, 34, 0); }
}

.animate-slide-up { animation: slideUpFade 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; transform: translateY(20px); }
@keyframes slideUpFade { to { opacity: 1; transform: translateY(0); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
