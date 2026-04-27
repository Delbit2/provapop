<template>
  <nav class="bottom-nav">
    <button class="nav-item" :class="{ active: currentRoute === '/' }" @click="navigate('/')">
      <font-awesome-icon icon="microphone" class="nav-icon" />
      <span class="nav-label">Show</span>
    </button>
    
    <button class="nav-item" :class="{ active: currentRoute === '/jornada' }" @click="navigate('/jornada')">
      <font-awesome-icon icon="headphones" class="nav-icon" />
      <span class="nav-label">Estúdio</span>
    </button>
    
    <button class="nav-item" :class="{ active: currentRoute === '/ranking' }" @click="navigate('/ranking')">
      <font-awesome-icon icon="trophy" class="nav-icon" />
      <span class="nav-label">Ranking</span>
    </button>
    
    <button class="nav-item" :class="{ active: currentRoute === '/perfil' }" @click="navigate('/perfil')">
      <font-awesome-icon icon="user" class="nav-icon" />
      <span class="nav-label">Perfil</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const currentRoute = computed(() => route.path)

function navigate(path: string) {
  router.push(path)
}
</script>

<style scoped>
/* =========================================
   A PÍLULA FLUTUANTE (DESIGN MODERNO)
   ========================================= */
.bottom-nav {
  position: fixed;
  bottom: 20px; /* Descola do fundo da tela! */
  left: 16px; /* Margem de respiro nas laterais */
  right: 16px;
  margin: 0 auto; /* Centraliza horizontalmente */
  width: auto; 
  max-width: 450px; /* Limita a largura para ficar sempre como uma pílula elegante */
  height: 70px;
  
  /* Efeito Vidro Premium */
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  
  /* Bordas totalmente arredondadas */
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 35px; 
  
  /* Sombra difusa e chic */
  box-shadow: 0 10px 35px rgba(139, 30, 63, 0.12), 0 2px 8px rgba(0, 0, 0, 0.04);
  
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 0 10px; 
  z-index: 100;
}

.nav-item {
  background: none;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #b5a9a7; /* Tom pálido chique para os inativos */
  cursor: pointer;
  flex: 1;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.nav-icon {
  font-size: 20px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), filter 0.3s ease;
}

.nav-label {
  font-size: 11px;
  font-weight: 700;
  transition: color 0.3s ease;
}

/* O Botão Ativo (A Página Atual) */
.nav-item.active {
  color: #8B1E3F; /* Bordô do ProvaPop! */
}

.nav-item.active .nav-icon {
  transform: translateY(-4px); /* Dá aquele pulinho charmoso */
  filter: drop-shadow(0 4px 6px rgba(139, 30, 63, 0.25));
}

/* O Hover para desktop ou toque suave */
.nav-item:hover:not(.active) {
  color: #E25822; /* Laranja no hover/toque */
}

/* Ajuste para telas maiores (Tablets/PCs) */
@media (min-width: 768px) {
  .bottom-nav {
    max-width: 500px;
    bottom: 24px;
    height: 75px;
  }
  .nav-icon {
    font-size: 22px;
  }
  .nav-label {
    font-size: 12px;
  }
}
</style>
