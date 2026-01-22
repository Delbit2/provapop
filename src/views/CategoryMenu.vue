<template>
  <div class="category-menu">
    <div class="category-menu__container">
      <div class="category-menu__header">
        <button class="category-menu__back-btn" @click="goToHome">
          <font-awesome-icon icon="arrow-left" />
        </button>
        <div class="category-menu__header-content">
          <h1 class="category-menu__title">Escolha o Exame</h1>
          <p class="category-menu__subtitle">Selecione a categoria para começar os quizzes</p>
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
              <font-awesome-icon :icon="category.icon" />
            </div>
            <div class="category-menu__card-text">
              <h3 class="category-menu__card-title">{{ category.name }}</h3>
              <p class="category-menu__card-description">{{ category.description }}</p>
            </div>
            <font-awesome-icon icon="angle-right" class="category-menu__card-arrow" />
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

const categories = ref<Category[]>([
  {
    id: 'unicamp',
    name: 'UNICAMP',
    description: 'Questões do vestibular da UNICAMP',
    icon: 'university'
  },
  {
    id: 'fuvest',
    name: 'FUVEST',
    description: 'Questões do vestibular da FUVEST',
    icon: 'graduation-cap'
  },
  {
    id: 'enem',
    name: 'ENEM',
    description: 'Questões do Exame Nacional do Ensino Médio',
    icon: 'certificate'
  },
  {
    id: 'others',
    name: 'Outros',
    description: 'Outras questões e vestibulares',
    icon: 'book'
  }
])

function selectCategory(categoryId: string) {
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
  min-height: 100vh;
  padding: 16px;
  background: var(--white);
}

.category-menu__container {
  max-width: 100%;
  margin: 0 auto;
}

.category-menu__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 32px;
}

.category-menu__back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--green-pastel);
  color: var(--green-primary);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
  font-size: 18px;
}

.category-menu__back-btn:active {
  transform: scale(0.95);
  background: var(--green-light);
}

.category-menu__header-content {
  flex: 1;
}

.category-menu__title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 4px 0;
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--yellow-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.category-menu__subtitle {
  font-size: 14px;
  color: var(--gray-dark);
  margin: 0;
}

.category-menu__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.category-menu__card {
  padding: 20px;
  transition: all var(--transition-base);
}

.category-menu__card:active {
  transform: scale(0.98);
}

.category-menu__card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.category-menu__card-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--border-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
  transition: all var(--transition-base);
}

.category-menu__card-icon--unicamp {
  background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%);
  color: white;
}

.category-menu__card-icon--fuvest {
  background: linear-gradient(135deg, #4A90E2 0%, #6BA3E8 100%);
  color: white;
}

.category-menu__card-icon--enem {
  background: linear-gradient(135deg, var(--green-primary) 0%, var(--green-light) 100%);
  color: white;
}

.category-menu__card-icon--others {
  background: linear-gradient(135deg, var(--yellow-primary) 0%, #FFD93D 100%);
  color: var(--black-soft);
}

.category-menu__card-text {
  flex: 1;
  min-width: 0;
}

.category-menu__card-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--black-soft);
  margin: 0 0 6px 0;
}

.category-menu__card-description {
  font-size: 14px;
  color: var(--gray-dark);
  margin: 0;
  line-height: 1.4;
}

.category-menu__card-arrow {
  font-size: 20px;
  color: var(--gray);
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .category-menu {
    padding: 24px;
  }

  .category-menu__container {
    max-width: 800px;
  }

  .category-menu__header {
    margin-bottom: 40px;
  }

  .category-menu__title {
    font-size: 48px;
  }

  .category-menu__subtitle {
    font-size: 16px;
  }

  .category-menu__back-btn {
    width: 52px;
    height: 52px;
    font-size: 20px;
  }

  .category-menu__back-btn:hover {
    background: var(--green-light);
    transform: scale(1.05);
    box-shadow: var(--shadow-md);
  }

  .category-menu__grid {
    gap: 20px;
  }

  .category-menu__card {
    padding: 24px;
  }

  .category-menu__card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }

  .category-menu__card-icon {
    width: 72px;
    height: 72px;
    font-size: 32px;
  }

  .category-menu__card-title {
    font-size: 22px;
  }

  .category-menu__card-description {
    font-size: 15px;
  }

  .category-menu__card-arrow {
    font-size: 24px;
  }
}

@media (min-width: 1024px) {
  .category-menu__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
