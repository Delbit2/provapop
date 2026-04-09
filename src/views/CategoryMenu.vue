<template>
  <div class="category-menu">
    <div class="category-menu__container">
      <div class="category-menu__header">
        <button class="category-menu__back-btn" @click="goToHome" title="Voltar">
          <font-awesome-icon icon="arrow-left"></font-awesome-icon>
        </button>
        <div class="category-menu__header-content">
          <h1 class="category-menu__title">Módulo de Treino</h1>
          <p class="category-menu__subtitle">Aqueça para o desafio diário escolhendo uma banca</p>
        </div>
      </div>

      <div class="category-menu__grid">
        <Card 
          v-for="category in categories" 
          :key="category.id"
          variant="elevated" 
          class="category-menu__card" 
          clickable 
          @click="selectCategory(category.id)"
        >
          <div class="category-menu__card-content">
            <div class="category-menu__card-icon" :class="`category-menu__card-icon--${category.id}`">
              <font-awesome-icon :icon="category.icon"></font-awesome-icon>
            </div>
            <div class="category-menu__card-text">
              <h3 class="category-menu__card-title">{{ category.name }}</h3>
              <p class="category-menu__card-description">{{ category.description }}</p>
            </div>
            <div class="category-menu__card-arrow">
              <font-awesome-icon icon="angle-right"></font-awesome-icon>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'

const router = useRouter()

interface Category {
  id: string
  name: string
  description: string
  icon: string
}

// Atualizado para refletir sua nova visão de jogo
const categories = ref<Category[]>([
  {
    id: 'enem',
    name: 'ENEM',
    description: 'A prova mais importante do país. Treine suas habilidades.',
    icon: 'certificate'
  },
  {
    id: 'foco', // antiga categoria "others" adaptada
    name: 'Da Terra à Lua',
    description: 'Questões temáticas, curiosidades e conhecimentos gerais.',
    icon: 'rocket' 
  },
  {
    id: 'fuvest',
    name: 'FUVEST',
    description: 'O vestibular mais concorrido. Nível de exigência alto.',
    icon: 'graduation-cap'
  },
  {
    id: 'unicamp',
    name: 'UNICAMP',
    description: 'Questões analíticas e de raciocínio lógico.',
    icon: 'university'
  }
])

function selectCategory(categoryId: string) {
  // Mantemos a rota configurada, mas você pode redirecionar para um aviso de "Em breve" se quiser
  router.push({
    name: 'quiz',
    params: { category: categoryId }
  })
}

function goToHome() {
  router.push('/')
}
</script>

<style scoped>
.category-menu {
  --primary: #8B1E3F;
  --secondary: #E25822;
  --text-main: #2d2422;
  --text-muted: #5a4a46;
  --border-light: #e8dedc;

  min-height: 100vh;
  padding: 20px;
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
}

.category-menu__container {
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.category-menu__header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
  animation: fadeInDown 0.4s ease-out;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-15px); }
  to { opacity: 1; transform: translateY(0); }
}

.category-menu__back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: #ffffff;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 10px rgba(139, 30, 63, 0.2);
  flex-shrink: 0;
  font-size: 18px;
}

.category-menu__back-btn:hover {
  background: var(--secondary);
  transform: scale(1.05) translateX(-2px);
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.3);
}

.category-menu__back-btn:active {
  transform: scale(0.95);
}

.category-menu__header-content {
  flex: 1;
}

.category-menu__title {
  font-size: 32px;
  font-weight: 800;
  color: var(--primary);
  margin: 0 0 4px 0;
}

.category-menu__subtitle {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  margin: 0;
}

.category-menu__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.category-menu__card {
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 25px rgba(226, 88, 34, 0.05);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  cursor: pointer;
}

.category-menu__card:hover {
  transform: translateY(-4px);
  box-shadow: 0 15px 35px rgba(139, 30, 63, 0.15);
  border-color: var(--secondary);
}

.category-menu__card:active {
  transform: scale(0.98);
}

.category-menu__card-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.category-menu__card-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* Cores dos Ícones seguindo a paleta Pop */
.category-menu__card-icon--enem {
  background: linear-gradient(135deg, var(--primary) 0%, #b32a55 100%);
  color: white;
}

.category-menu__card-icon--foco {
  background: linear-gradient(135deg, #FFD700 0%, var(--secondary) 100%);
  color: white;
}

.category-menu__card-icon--fuvest {
  background: linear-gradient(135deg, #4A90E2 0%, #2b5c92 100%);
  color: white;
}

.category-menu__card-icon--unicamp {
  background: linear-gradient(135deg, var(--secondary) 0%, #b84112 100%);
  color: white;
}

.category-menu__card-text {
  flex: 1;
  min-width: 0;
}

.category-menu__card-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0 0 4px 0;
  transition: color 0.3s ease;
}

.category-menu__card:hover .category-menu__card-title {
  color: var(--primary);
}

.category-menu__card-description {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
  margin: 0;
  line-height: 1.4;
}

.category-menu__card-arrow {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #fdfaf9;
  color: var(--secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.category-menu__card:hover .category-menu__card-arrow {
  background: var(--secondary);
  color: #ffffff;
  transform: translateX(4px);
}

@media (min-width: 768px) {
  .category-menu { padding: 32px; }
  .category-menu__container { max-width: 800px; }
  .category-menu__header { margin-bottom: 40px; }
  .category-menu__title { font-size: 40px; }
  .category-menu__subtitle { font-size: 16px; }
  .category-menu__back-btn { width: 52px; height: 52px; font-size: 20px; }
  .category-menu__grid { gap: 24px; }
  .category-menu__card { padding: 28px; }
  .category-menu__card-icon { width: 72px; height: 72px; font-size: 32px; border-radius: 20px; }
  .category-menu__card-title { font-size: 22px; }
  .category-menu__card-description { font-size: 14px; }
}

@media (min-width: 1024px) {
  .category-menu__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
