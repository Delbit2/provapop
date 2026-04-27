<template>
  <div class="jornada">
    
    <!-- CABEÇALHO FIXO NO TOPO -->
    <div class="jornada__top-fixed animate-fade-down">
      <div class="jornada__header">
        <h1 class="page-title">Meu Estúdio</h1>
        <p class="page-subtitle">Seus bastidores musicais 🎵</p>
      </div>

      <!-- AS ABAS -->
      <div class="jornada__tabs">
        <button 
          @click="activeTab = 'musicas'"
          :class="['tab-btn', { active: activeTab === 'musicas' }]"
        >
          <font-awesome-icon icon="headphones" class="tab-icon" />
          Minhas Músicas
        </button>
        <button 
          @click="activeTab = 'discos'"
          :class="['tab-btn', { active: activeTab === 'discos' }]"
        >
          <font-awesome-icon icon="compact-disc" class="tab-icon" />
          Meus Discos
        </button>
      </div>
    </div>

    <!-- ÁREA DE CONTEÚDO (ROLA POR BAIXO DO TOPO E RODAPÉ) -->
    <div class="jornada__scroll-area">
      <transition name="fade" mode="out-in">
        
        <!-- ABA 1: MINHAS MÚSICAS -->
        <div v-if="activeTab === 'musicas'" key="musicas" class="animate-slide-up" style="animation-delay: 0.1s">
          <div class="section-header">
            <h2>Estúdio de Ensaios</h2>
            <span class="badge badge--active">Acesso Liberado</span>
          </div>

          <div class="musicas-list">
            <button class="folder-card folder-card--bis" @click="abrirPasta('bis')">
              <div class="folder-info">
                <div class="folder-icon icon-bis">
                  <font-awesome-icon icon="star" />
                  <span class="folder-emoji">✨</span>
                </div>
                <div class="folder-text">
                  <h3>Bis!</h3>
                  <p>Revise seus acertos para gravar a música definitivamente nos seus discos.</p>
                </div>
              </div>
              <div class="folder-stats">
                <span class="stats-number">{{ bisCount }}</span>
                <span class="stats-label">aguardando</span>
              </div>
            </button>

            <button class="folder-card folder-card--riscado" @click="abrirPasta('riscado')">
              <div class="folder-info">
                <div class="folder-icon icon-riscado">
                  <font-awesome-icon icon="compact-disc" />
                  <span class="folder-emoji">⚠️</span>
                </div>
                <div class="folder-text">
                  <h3>Disco Riscado</h3>
                  <p>Segunda chance! Recupere as questões que você errou na missão.</p>
                </div>
              </div>
              <div class="folder-stats stats--alert">
                <span class="stats-number">{{ riscadoCount }}</span>
                <span class="stats-label">para refazer</span>
              </div>
            </button>
          </div>
        </div>

        <!-- ABA 2: MEUS DISCOS -->
        <div v-else-if="activeTab === 'discos'" key="discos" class="animate-slide-up" style="animation-delay: 0.1s">
          <div class="section-header" style="margin-bottom: 24px;">
            <h2>Acervo Definitivo</h2>
            <span class="badge badge--locked">Sua Coleção</span>
          </div>

          <div class="jornada__path">
            <div class="path-line"></div>
            <div 
              v-for="(level, index) in journeyLevels" 
              :key="level.id"
              class="level-node"
              :class="[level.status, index % 2 === 0 ? 'left' : 'right']"
            >
              <div class="level-disc">
                <span v-if="level.status === 'locked'" class="disc-icon">🔒</span>
                <span v-else class="disc-icon">💿</span>
              </div>
              <div class="level-card">
                <div class="level-card-header">
                  <h3 class="level-title">{{ level.title }}</h3>
                  <span v-if="level.status === 'current'" class="level-progress">5/20</span>
                </div>
                <p class="level-desc">{{ level.description }}</p>
              </div>
            </div>
          </div>
        </div>

      </transition>

      <!-- =================================================== -->
      <!-- NOVA SEÇÃO: MERCH OFICIAL (PREENCHE O ESPAÇO VAZIO) -->
      <!-- =================================================== -->
      <div class="store-section animate-slide-up" style="animation-delay: 0.3s">
        <div class="section-header" style="margin: 32px 0 16px 0;">
          <h2>Merch Oficial 🛍️</h2>
          <span class="badge badge--vip">Material de Apoio</span>
        </div>

        <div class="store-grid">
          
          <!-- PRODUTO 1: E-BOOK HOTMART (JÁ VENDE) -->
          <div class="store-card">
            <div class="store-card__image bg-ebook">📚</div>
            <div class="store-card__content">
              <span class="store-tag tag-hot">JÁ DISPONÍVEL</span>
              <h3 class="store-title">E-book ProvaPop!</h3>
              <p class="store-desc">A estratégia completa para alavancar sua nota no vestibular.</p>
              <button @click="router.push('/ebook')" class="store-btn btn-buy">
                Garantir o meu 🚀
              </button>
            </div>
          </div>

          <!-- PRODUTO 2: WEBBOOK CONTEXTO (FUTURO) -->
          <div class="store-card store-card--disabled">
            <div class="store-card__image bg-webbook">🎧</div>
            <div class="store-card__content">
              <span class="store-tag tag-soon">EM BREVE</span>
              <h3 class="store-title">Webbook: Contexto & Repertório</h3>
              <p class="store-desc">De Liniker a Luiz Gonzaga: O guia interativo das obras do ENEM.</p>
              <button class="store-btn btn-disabled" disabled>
                No Forno... ⏳
              </button>
            </div>
          </div>

        </div>
      </div>
      <!-- Fim da Lojinha -->

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('musicas')
const bisCount = ref(0)
const riscadoCount = ref(0)

const journeyLevels = ref([
  { id: 1, title: 'MPB', description: 'Acervo consolidado. Continue aprovando músicas no Bis! para expandir.', status: 'current' },
  { id: 2, title: 'Rock / Pop / Rap', description: 'Trancado. Domine as questões desta categoria no Bis!', status: 'locked' },
  { id: 3, title: 'Samba', description: 'Trancado. Domine as questões desta categoria no Bis!', status: 'locked' }
])

function abrirPasta(tipo: 'bis' | 'riscado') {
  if (tipo === 'bis') {
    if (bisCount.value === 0) return alert('Seu Bis! está vazio.')
    alert(`✨ Abrindo modo revisão: BIS!`)
  } else {
    if (riscadoCount.value === 0) return alert('Nenhum Disco Riscado!')
    alert(`⚠️ Abrindo modo recuperação: DISCO RISCADO!`)
  }
}

function carregarDadosDoEstudio() {
  bisCount.value = Number(localStorage.getItem('dev_bis_count')) || 0
  riscadoCount.value = Number(localStorage.getItem('dev_riscado_count')) || 0
}

onMounted(() => {
  carregarDadosDoEstudio()
})
</script>

<style scoped>
.jornada {
  --primary: #8B1E3F;
  --primary-dark: #5d142a;
  --secondary: #E25822;
  --text-main: #2d2422;
  --text-muted: #5a4a46;
  --border-light: rgba(139, 30, 63, 0.1);

  min-height: 100vh;
  /* Reduzi o padding bottom porque não temos mais o banner fixo gigante! */
  padding: 160px 16px 120px 16px; 
  background-color: #FFF4EF;
  background-image: linear-gradient(180deg, #FFF4EF 0%, #FFFFFF 35%, #FCF2EE 80%, #EBD2CB 100%);
  position: relative;
  overflow-x: hidden;
}

.jornada__top-fixed {
  position: fixed; top: 0; left: 0; right: 0; margin: 0 auto;
  width: 100%; max-width: 600px;
  background: rgba(255, 244, 239, 0.85); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
  z-index: 90; padding: 16px 16px 8px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 15px rgba(139, 30, 63, 0.05);
}
.jornada__header { text-align: center; margin-bottom: 16px; }
.page-title { font-size: 24px; font-weight: 900; color: var(--primary); margin: 0 0 4px 0; }
.page-subtitle { font-size: 14px; font-weight: 600; color: var(--text-muted); margin: 0; }

.jornada__tabs {
  display: flex; background: rgba(255, 255, 255, 0.7); border-radius: 16px;
  padding: 6px; box-shadow: inset 0 2px 5px rgba(0,0,0,0.03); border: 1px solid rgba(255,255,255,0.9);
}
.tab-btn {
  flex: 1; padding: 10px; border: none; background: transparent;
  border-radius: 12px; font-size: 14px; font-weight: 800; color: var(--text-muted);
  cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; gap: 8px;
}
.tab-btn.active {
  background: #fff; color: var(--primary);
  box-shadow: 0 4px 10px rgba(139, 30, 63, 0.1); transform: scale(1.02);
}

.jornada__scroll-area { max-width: 600px; margin: 0 auto; position: relative; z-index: 10; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin: 0 0 16px 0; padding: 0 4px; }
.section-header h2 { font-size: 14px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin: 0; }

.badge { padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 800; }
.badge--active { background: rgba(226, 88, 34, 0.15); color: var(--secondary); }
.badge--locked { background: rgba(90, 74, 70, 0.1); color: var(--text-muted); }
.badge--vip { background: rgba(212, 175, 55, 0.2); color: #b89320; }

/* Pastas e Discos (mantidos do original) */
.musicas-list { display: flex; flex-direction: column; gap: 16px; }
.folder-card {
  width: 100%; text-align: left; background: #ffffff; border: 1px solid rgba(255, 255, 255, 1);
  border-radius: 20px; padding: 20px; display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 8px 25px rgba(139, 30, 63, 0.05); cursor: pointer; transition: all 0.3s ease;
}
.folder-card--bis { background: linear-gradient(135deg, #ffffff 0%, #fffcf5 100%); border: 1px solid rgba(212, 175, 55, 0.3); }
.folder-card--riscado { background: linear-gradient(135deg, #ffffff 0%, #fff5f5 100%); border: 1px solid rgba(139, 30, 63, 0.15); }
.folder-info { display: flex; align-items: center; gap: 16px; flex: 1; }
.folder-icon { width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 24px; position: relative; flex-shrink: 0; }
.icon-bis { background: rgba(212, 175, 55, 0.15); color: #D4AF37; }
.icon-riscado { background: rgba(139, 30, 63, 0.1); color: var(--primary); }
.folder-emoji { position: absolute; bottom: -6px; right: -6px; font-size: 16px; background: #fff; border-radius: 50%; padding: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.folder-text h3 { margin: 0 0 6px 0; font-size: 18px; font-weight: 900; color: var(--text-main); }
.folder-text p { margin: 0; font-size: 12px; color: var(--text-muted); font-weight: 600; line-height: 1.3; max-width: 90%; }
.folder-stats { display: flex; flex-direction: column; align-items: center; justify-content: center; background: #FFF4EF; padding: 10px 14px; border-radius: 14px; border: 1px solid rgba(226, 88, 34, 0.15); flex-shrink: 0; min-width: 75px; }
.stats--alert { background: #fff5f5; border-color: rgba(139, 30, 63, 0.2); }
.stats-number { font-size: 22px; font-weight: 900; color: var(--secondary); line-height: 1; margin-bottom: 2px; }
.stats--alert .stats-number { color: var(--primary); }
.stats-label { font-size: 9px; font-weight: 800; color: var(--text-muted); text-transform: uppercase; }

.jornada__path { position: relative; padding: 10px 0; }
.path-line { position: absolute; top: 0; bottom: 0; left: 35px; width: 4px; background: var(--border-light); border-radius: 4px; z-index: 1; }
.level-node { display: flex; align-items: center; margin-bottom: 30px; position: relative; z-index: 2; gap: 20px; }
.level-disc { width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #fff; border: 4px solid #eaeaea; box-shadow: 0 4px 10px rgba(0,0,0,0.1); flex-shrink: 0; font-size: 32px; }
.level-card { background: rgba(255, 255, 255, 0.9); border: 1px solid rgba(255,255,255,1); border-radius: 16px; padding: 16px; flex-grow: 1; box-shadow: 0 4px 15px rgba(139, 30, 63, 0.05); position: relative; }
.level-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.level-title { font-size: 16px; font-weight: 800; color: var(--text-main); margin: 0; }
.level-progress { font-size: 11px; font-weight: 800; color: var(--secondary); background: rgba(226, 88, 34, 0.1); padding: 2px 8px; border-radius: 10px; }
.level-desc { font-size: 13px; color: var(--text-muted); margin: 0; line-height: 1.3; }
.level-node.current .level-title { color: var(--secondary); }
.level-node.current .level-disc { border-color: var(--secondary); background: #fff0eb; box-shadow: 0 0 15px rgba(226, 88, 34, 0.4); }
.level-node.locked { opacity: 0.6; }
.level-node.locked .level-disc { background: #f1f5f9; border-color: #cbd5e1; }
.level-node.locked .level-card { background: rgba(241, 245, 249, 0.6); border-color: transparent; box-shadow: none; }

/* =========================================
   ESTILOS DA NOVA LOJINHA / MERCH OFICIAL
   ========================================= */
.store-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.store-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(255, 255, 255, 1);
  border-radius: 20px;
  padding: 16px;
  display: flex;
  gap: 16px;
  box-shadow: 0 8px 20px rgba(139, 30, 63, 0.06);
  transition: transform 0.3s ease;
}

.store-card:hover:not(.store-card--disabled) {
  transform: translateY(-3px);
  border-color: rgba(226, 88, 34, 0.3);
}

.store-card--disabled {
  opacity: 0.7;
  filter: grayscale(0.5);
}

.store-card__image {
  width: 80px;
  height: 100px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.bg-ebook { background: linear-gradient(135deg, #179B78 0%, #0c5c46 100%); }
.bg-webbook { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); }

.store-card__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.store-tag {
  align-self: flex-start;
  font-size: 9px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}

.tag-hot { background: #E25822; color: #fff; }
.tag-soon { background: var(--text-muted); color: #fff; }

.store-title {
  font-size: 15px;
  font-weight: 900;
  color: var(--text-main);
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.store-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0 0 12px 0;
  line-height: 1.3;
}

.store-btn {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 800;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-buy {
  background: rgba(23, 155, 120, 0.15);
  color: #0c5c46;
}

.btn-buy:active { transform: scale(0.96); }

.btn-disabled {
  background: var(--border-light);
  color: var(--text-muted);
  cursor: not-allowed;
}

/* Animações */
.animate-slide-up { opacity: 0; transform: translateY(20px); animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-fade-down { opacity: 0; transform: translateY(-15px); animation: fadeDown 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
@keyframes slideUpFade { to { opacity: 1; transform: translateY(0); } }
@keyframes fadeDown { to { opacity: 1; transform: translateY(0); } }

@media (min-width: 768px) {
  .jornada { padding: 160px 32px 140px 32px; }
  .path-line { left: 50%; transform: translateX(-50%); }
  .level-node { width: 100%; justify-content: flex-start; }
  .level-node.left { flex-direction: row-reverse; }
  .level-disc { margin: 0 calc(50% - 35px); position: absolute; left: 0; }
  .level-card { width: calc(50% - 50px); flex-grow: 0; }
  
  .store-grid { grid-template-columns: 1fr 1fr; }
}
</style>
