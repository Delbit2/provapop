<template>
  <button
    :class="['btn', `btn--${variant}`, `btn--${size}`, { 'btn--icon-only': iconOnly, 'btn--full-width': fullWidth }]"
    :disabled="disabled"
    @click="$emit('click', $event)"
  >
    <font-awesome-icon v-if="icon && !iconRight" :icon="icon" :class="['btn__icon', { 'btn__icon--left': !iconOnly }]" />
    <span v-if="!iconOnly" class="btn__text">
      <slot></slot>
    </span>
    <font-awesome-icon v-if="icon && iconRight" :icon="icon" :class="['btn__icon', 'btn__icon--right']" />
  </button>
</template>

<script setup lang="ts">
import { IconDefinition } from '@fortawesome/fontawesome-svg-core'

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  icon?: IconDefinition | string | Array<string>
  iconRight?: boolean
  iconOnly?: boolean
  fullWidth?: boolean
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  iconRight: false,
  iconOnly: false,
  fullWidth: false,
  disabled: false
})

defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 600;
  border-radius: var(--border-radius-full);
  transition: all var(--transition-base);
  text-align: center;
  user-select: none;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.btn:active::before {
  width: 300px;
  height: 300px;
}

.btn--sm {
  padding: 8px 16px;
  font-size: 14px;
  min-height: 36px;
}

.btn--md {
  padding: 12px 24px;
  font-size: 16px;
  min-height: 44px;
}

.btn--lg {
  padding: 16px 32px;
  font-size: 18px;
  min-height: 52px;
}

.btn--icon-only.btn--sm {
  width: 36px;
  padding: 8px;
}

.btn--icon-only.btn--md {
  width: 44px;
  padding: 12px;
}

.btn--icon-only.btn--lg {
  width: 52px;
  padding: 16px;
}

.btn--full-width {
  width: 100%;
}

.btn__icon {
  font-size: 1em;
  flex-shrink: 0;
}

.btn__icon--left {
  margin-right: -4px;
}

.btn__icon--right {
  margin-left: -4px;
}

.btn--primary {
  background: var(--green-primary);
  color: var(--white);
  box-shadow: var(--shadow-sm);
}

.btn--primary:hover:not(:disabled) {
  background: var(--green-dark);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn--secondary {
  background: var(--yellow-primary);
  color: var(--black);
  box-shadow: var(--shadow-sm);
}

.btn--secondary:hover:not(:disabled) {
  background: var(--yellow-dark);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn--secondary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn--success {
  background: var(--green-light);
  color: var(--black-soft);
  box-shadow: var(--shadow-sm);
}

.btn--success:hover:not(:disabled) {
  background: var(--green-primary);
  color: var(--white);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn--success:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn--warning {
  background: var(--yellow-light);
  color: var(--black-soft);
  box-shadow: var(--shadow-sm);
}

.btn--warning:hover:not(:disabled) {
  background: var(--yellow-primary);
  color: var(--black);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.btn--warning:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.btn--outline {
  background: transparent;
  color: var(--green-primary);
  border: 2px solid var(--green-primary);
}

.btn--outline:hover:not(:disabled) {
  background: var(--green-primary);
  color: var(--white);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.btn--outline:active:not(:disabled) {
  transform: translateY(0);
}

.btn--ghost {
  background: transparent;
  color: var(--black-soft);
}

.btn--ghost:hover:not(:disabled) {
  background: var(--gray-light);
  color: var(--black);
}

.btn--ghost:active:not(:disabled) {
  background: var(--gray);
}

.btn:disabled {
  opacity: 0.6;
  transform: none !important;
  box-shadow: none !important;
}
</style>
