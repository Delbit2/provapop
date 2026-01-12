<template>
  <div :class="['card', `card--${variant}`, { 'card--clickable': clickable }]" @click="handleClick">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'default' | 'elevated' | 'outlined'
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  clickable: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

function handleClick(event: MouseEvent) {
  if (props.clickable) {
    emit('click', event)
  }
}
</script>

<style scoped>
.card {
  background: var(--white);
  border-radius: var(--border-radius-md);
  padding: 24px;
  transition: all var(--transition-base);
}

.card--default {
  box-shadow: var(--shadow-sm);
}

.card--elevated {
  box-shadow: var(--shadow-lg);
}

.card--outlined {
  border: 2px solid var(--gray-light);
  box-shadow: none;
}

.card--clickable {
  cursor: pointer;
}

.card--clickable:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.card--clickable:active {
  transform: translateY(-2px);
}
</style>
