<template>
  <div class="promo-banner bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden w-full my-4">
    <!-- Marca d'água de fundo (para dar aquele ar Premium) -->
    <div class="absolute -right-4 -top-4 opacity-10 text-8xl pointer-events-none">
      <font-awesome-icon icon="book-open" />
    </div>
    
    <!-- Textos de Venda (O Copywriting que você aprovou!) -->
    <h3 class="font-black text-xl mb-2 relative z-10 text-left">Domine o ENEM! 🚀</h3>
    <p class="text-sm text-purple-100 mb-5 relative z-10 leading-relaxed text-left">
      Conheça nosso guia compacto das 120 músicas do ENEM!!!
    </p>
    
    <!-- Botão de Compra -->
    <button class="w-full bg-white text-purple-700 font-bold py-3.5 rounded-xl shadow-sm hover:bg-gray-100 transition-colors relative z-10 flex justify-center items-center gap-2 active:scale-95 duration-200">
      <font-awesome-icon icon="book" />
      Garantir meu Guia
    </button>
  </div>
</template>

<script setup lang="ts">
// Aqui no futuro podemos colocar a função que abre o link de compra
</script>

<style scoped>
/* Apenas um respiro extra se necessário, o Tailwind já faz 99% do trabalho */
.promo-banner {
  box-shadow: 0 10px 25px -5px rgba(124, 58, 237, 0.4);
}
</style>
