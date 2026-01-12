<template>
  <div class="quiz">
    <div class="quiz__container">
      <Card variant="elevated" class="quiz__card">
        <div class="quiz__header">
          <button class="quiz__back-btn" @click="goToHome">
            <font-awesome-icon icon="arrow-left" />
          </button>
          <div class="quiz__header-content">
            <h2 class="quiz__title">Quiz Musical - ENEM</h2>
            <div class="quiz__question-number">Questão 1 de 10</div>
          </div>
        </div>

        <div class="quiz__content">
          <div class="quiz__audio-section">
            <button class="quiz__play-btn" @click="togglePlay" :class="{ 'quiz__play-btn--playing': isPlaying }">
              <font-awesome-icon :icon="isPlaying ? 'pause' : 'play'" class="quiz__play-icon" />
            </button>
            <div class="quiz__audio-info">
              <div class="quiz__audio-title">Engenheiros do Hawaii - Toda Forma de Poder</div>
              <div class="quiz__audio-progress" v-if="isPlaying">
                <div class="quiz__audio-progress-bar"></div>
              </div>
            </div>
          </div>

          <div class="quiz__lyrics">
            <div class="quiz__lyrics-text">
              <p>"E toda forma de poder</p>
              <p>Me inspira terror</p>
              <p>Me inspira horror</p>
              <p>Deixa eu te dizer</p>
              <p>Por que eu sou contra</p>
              <p>A toda forma de poder"</p>
            </div>
          </div>

          <div class="quiz__statement">
            <p class="quiz__statement-text">
              Na letra da canção "Toda Forma de Poder", dos Engenheiros do Hawaii, o compositor expressa uma crítica 
              social. Considerando o contexto histórico e social do Brasil na década de 1980, a mensagem central da música 
              refere-se à crítica:
            </p>
          </div>

          <div class="quiz__options">
            <OptionButton
              v-for="(option, index) in options"
              :key="index"
              :label="option.label"
              :selected="selectedOption === index"
              @click="selectOption(index)"
              :disabled="answered"
              :correct="answered && option.isCorrect"
              :wrong="answered && selectedOption === index && !option.isCorrect"
            >
              {{ option.text }}
            </OptionButton>
          </div>
        </div>

        <div class="quiz__actions" v-if="selectedOption !== null">
          <Button 
            variant="primary" 
            size="lg" 
            full-width 
            @click="confirmAnswer"
            :disabled="answered"
          >
            Confirmar Resposta
          </Button>
        </div>

        <div class="quiz__feedback" v-if="answered">
          <div class="quiz__feedback-content" :class="isCorrect ? 'quiz__feedback--correct' : 'quiz__feedback--wrong'">
            <font-awesome-icon 
              :icon="isCorrect ? 'check-circle' : 'times-circle'" 
              class="quiz__feedback-icon"
            />
            <div class="quiz__feedback-text">
              <strong>{{ isCorrect ? 'Resposta Correta!' : 'Resposta Incorreta' }}</strong>
              <p v-if="!isCorrect">A resposta correta é a alternativa {{ correctAnswer }}.</p>
            </div>
          </div>
          <Button variant="secondary" size="md" full-width @click="nextQuestion" class="quiz__next-btn">
            Próxima Questão
          </Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import confetti from 'canvas-confetti'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'
import OptionButton from '@/components/OptionButton.vue'

const router = useRouter()

const isPlaying = ref(false)
const selectedOption = ref<number | null>(null)
const answered = ref(false)
const isCorrect = ref(false)
const correctAnswer = ref('C')

const options = [
  {
    label: 'A',
    text: 'à política partidária e aos sistemas eleitorais democráticos, defendendo uma monarquia absoluta.',
    isCorrect: false
  },
  {
    label: 'B',
    text: 'à concentração de poder nas mãos de grupos minoritários, sem questionar as estruturas sociais existentes.',
    isCorrect: false
  },
  {
    label: 'C',
    text: 'às estruturas autoritárias e à concentração de poder que limitavam as liberdades individuais e coletivas.',
    isCorrect: true
  },
  {
    label: 'D',
    text: 'exclusivamente ao poder militar, ignorando outros aspectos do contexto social e político da época.',
    isCorrect: false
  },
  {
    label: 'E',
    text: 'ao poder econômico, sem relacionar com as questões políticas e sociais do período.',
    isCorrect: false
  }
]

function togglePlay() {
  isPlaying.value = !isPlaying.value
}

function selectOption(index: number) {
  if (!answered.value) {
    selectedOption.value = index
  }
}

function triggerConfetti() {
  const duration = 3000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 }

  function randomInRange(min: number, max: number) {
    return Math.random() * (max - min) + min
  }

  confetti({
    particleCount: 100,
    spread: 70,
    origin: { y: 0.6 },
    colors: ['#2ecc71', '#27ae60', '#52e88f', '#f1c40f', '#f39c12', '#f7dc6f']
  })

  const interval: NodeJS.Timeout = setInterval(function() {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      return clearInterval(interval)
    }

    const particleCount = 50 * (timeLeft / duration)
    
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#2ecc71', '#27ae60', '#52e88f', '#f1c40f', '#f39c12', '#f7dc6f']
    })
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#2ecc71', '#27ae60', '#52e88f', '#f1c40f', '#f39c12', '#f7dc6f']
    })
  }, 250)
}

function confirmAnswer() {
  if (selectedOption.value !== null) {
    answered.value = true
    const correct = options[selectedOption.value].isCorrect
    isCorrect.value = correct
    
    if (correct) {
      setTimeout(() => {
        triggerConfetti()
      }, 300)
    }
  }
}

function nextQuestion() {
  selectedOption.value = null
  answered.value = false
  isCorrect.value = false
  isPlaying.value = false
}

function goToHome() {
  router.push('/')
}
</script>

<style scoped>
.quiz {
  min-height: 100vh;
  padding: 16px;
  background: var(--white);
  border: 1px solid var(--green-pastel);
}

.quiz__container {
  max-width: 100%;
  margin: 0 auto;
}

.quiz__card {
  padding: 20px;
}

.quiz__content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quiz__header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--gray-light);
}

.quiz__back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--gray-light);
  color: var(--black-soft);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
}

.quiz__back-btn:active {
  background: var(--green-primary);
  color: var(--white);
  transform: scale(0.95);
}

.quiz__header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.quiz__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--green-dark);
  margin: 0;
}

.quiz__question-number {
  font-size: 12px;
  color: var(--gray-dark);
  font-weight: 500;
  background: var(--gray-light);
  padding: 6px 12px;
  border-radius: var(--border-radius-full);
  align-self: flex-start;
}

.quiz__audio-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
  border: 2px solid var(--gray-light);
}

.quiz__play-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--green-primary);
  color: var(--white);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
  flex-shrink: 0;
}

.quiz__play-btn:active {
  transform: scale(0.95);
}

.quiz__play-btn--playing {
  background: var(--yellow-primary);
}

.quiz__play-icon {
  font-size: 20px;
}

.quiz__audio-info {
  flex: 1;
  min-width: 0;
}

.quiz__audio-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--black-soft);
  margin-bottom: 8px;
  word-wrap: break-word;
}

.quiz__audio-progress {
  height: 4px;
  background: var(--gray-light);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.quiz__audio-progress-bar {
  height: 100%;
  width: 45%;
  background: var(--green-primary);
  border-radius: var(--border-radius-full);
  animation: progress 3s ease-in-out infinite;
}

@keyframes progress {
  0% {
    width: 0%;
  }
  100% {
    width: 100%;
  }
}

.quiz__lyrics {
  padding: 16px;
  background: var(--yellow-pastel);
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--yellow-primary);
}

.quiz__lyrics-text {
  font-size: 15px;
  line-height: 1.7;
  color: var(--black-soft);
  font-style: italic;
  text-align: center;
}

.quiz__lyrics-text p {
  margin: 6px 0;
}

.quiz__statement {
  padding: 16px;
  background: var(--white);
  border-radius: var(--border-radius-md);
  border: 2px solid var(--green-pastel);
}

.quiz__statement-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--black-soft);
  margin: 0;
}

.quiz__options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.quiz__actions {
  margin-top: 24px;
}

.quiz__feedback {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 2px solid var(--gray-light);
}

.quiz__feedback-content {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: var(--border-radius-md);
  margin-bottom: 12px;
}

.quiz__feedback--correct {
  background: var(--green-pastel);
  border: 2px solid var(--green-primary);
}

.quiz__feedback--wrong {
  background: var(--yellow-pastel);
  border: 2px solid var(--yellow-primary);
}

.quiz__feedback-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.quiz__feedback--correct .quiz__feedback-icon {
  color: var(--green-dark);
}

.quiz__feedback--wrong .quiz__feedback-icon {
  color: var(--yellow-dark);
}

.quiz__feedback-text {
  flex: 1;
  min-width: 0;
}

.quiz__feedback-text strong {
  display: block;
  font-size: 16px;
  margin-bottom: 6px;
}

.quiz__feedback-text p {
  margin: 0;
  font-size: 13px;
  color: var(--black-soft);
}

.quiz__next-btn {
  margin-top: 12px;
}

@media (min-width: 768px) {
  .quiz {
    padding: 24px;
  }

  .quiz__container {
    max-width: 700px;
  }

  .quiz__card {
    padding: 32px;
  }

  .quiz__content {
    gap: 24px;
  }

  .quiz__header {
    margin-bottom: 32px;
  }

  .quiz__back-btn {
    width: 44px;
    height: 44px;
  }

  .quiz__back-btn:hover {
    background: var(--green-primary);
    color: var(--white);
    transform: scale(1.05);
  }

  .quiz__header-content {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .quiz__title {
    font-size: 24px;
  }

  .quiz__question-number {
    font-size: 14px;
  }

  .quiz__audio-section {
    padding: 20px;
    gap: 16px;
  }

  .quiz__play-btn {
    width: 64px;
    height: 64px;
  }

  .quiz__play-btn:hover {
    background: var(--green-dark);
    transform: scale(1.05);
    box-shadow: var(--shadow-lg);
  }

  .quiz__play-btn--playing:hover {
    background: var(--yellow-dark);
  }

  .quiz__play-icon {
    font-size: 24px;
  }

  .quiz__audio-title {
    font-size: 16px;
  }

  .quiz__lyrics {
    padding: 24px;
  }

  .quiz__lyrics-text {
    font-size: 18px;
  }

  .quiz__lyrics-text p {
    margin: 8px 0;
  }

  .quiz__statement {
    padding: 20px;
  }

  .quiz__statement-text {
    font-size: 16px;
  }

  .quiz__options {
    gap: 12px;
  }

  .quiz__actions {
    margin-top: 32px;
  }

  .quiz__feedback {
    margin-top: 32px;
    padding-top: 24px;
  }

  .quiz__feedback-content {
    gap: 16px;
    padding: 20px;
    margin-bottom: 16px;
  }

  .quiz__feedback-icon {
    font-size: 32px;
  }

  .quiz__feedback-text strong {
    font-size: 18px;
    margin-bottom: 8px;
  }

  .quiz__feedback-text p {
    font-size: 14px;
  }

  .quiz__next-btn {
    margin-top: 16px;
  }
}

@media (min-width: 1024px) {
  .quiz__container {
    max-width: 800px;
  }
}
</style>
