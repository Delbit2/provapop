<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BottomNav from '@/components/BottomNav.vue'

const route = useRoute()

const showBottomNav = computed(() => {
  return !route.meta.hideBottomNav
})
</script>

<template>
  <router-view />
  <BottomNav v-if="showBottomNav" />
</template>

<style>
#app {
  width: 100%;
  height: 100%;
}
</style>
