<template>
  <button
    :class="['option-btn', { 'option-btn--selected': selected, 'option-btn--correct': correct, 'option-btn--wrong': wrong }]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <span class="option-btn__label" v-if="label">{{ label }}</span>
    <span class="option-btn__content">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  label?: string
  selected?: boolean
  correct?: boolean
  wrong?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  selected: false,
  correct: false,
  wrong: false,
  disabled: false
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.option-btn {
  width: 100%;
  padding: 16px 24px;
  border-radius: var(--border-radius-full);
  background: var(--white);
  border: 2px solid var(--gray-light);
  color: var(--black-soft);
  font-size: 16px;
  font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  overflow: hidden;
}

.option-btn::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 0;
  background: var(--green-primary);
  transition: width var(--transition-base);
}

.option-btn:hover:not(:disabled) {
  border-color: var(--green-primary);
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.option-btn:hover:not(:disabled)::before {
  width: 4px;
}

.option-btn--selected {
  background: var(--green-pastel);
  border-color: var(--green-primary);
  color: var(--green-dark);
  transform: translateX(4px);
}

.option-btn--selected::before {
  width: 4px;
}

.option-btn--correct {
  background: var(--green-light);
  border-color: var(--green-primary);
  color: var(--green-dark);
  animation: pulse 0.5s ease;
}

.option-btn--wrong {
  background: var(--yellow-pastel);
  border-color: var(--yellow-primary);
  color: var(--yellow-dark);
  animation: shake 0.5s ease;
}

.option-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.option-btn__label {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--gray-light);
  color: var(--gray-dark);
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  transition: all var(--transition-base);
}

.option-btn--selected .option-btn__label {
  background: var(--green-primary);
  color: var(--white);
}

.option-btn--correct .option-btn__label {
  background: var(--green-dark);
  color: var(--white);
}

.option-btn--wrong .option-btn__label {
  background: var(--yellow-primary);
  color: var(--black);
}

.option-btn__content {
  flex: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  75% {
    transform: translateX(4px);
  }
}
</style>

