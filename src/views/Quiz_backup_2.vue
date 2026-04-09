<template>
  <div class="quiz">
    <div class="quiz__container">
      <Card variant="elevated" class="quiz__card">
        <!-- Loading State -->
        <div v-if="loading" class="quiz__loading">
          <div class="quiz__loading-spinner"></div>
          <p>Carregando questões...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="quiz__error">
          <font-awesome-icon icon="exclamation-triangle" class="quiz__error-icon" />
          <p>{{ error }}</p>
          <Button variant="primary" @click="() => loadQuestions()">Tentar Novamente</Button>
        </div>

        <!-- No Questions State -->
        <div v-else-if="allQuestions.length === 0" class="quiz__empty">
          <font-awesome-icon icon="inbox" class="quiz__empty-icon" />
          <p>Nenhuma questão disponível.</p>
          <p class="quiz__empty-hint">Adicione questões na planilha Google Sheets e sincronize.</p>
          <Button variant="primary" @click="goToHome">Voltar para Home</Button>
        </div>

        <!-- Empty Filter State -->
        <div v-else-if="filteredQuestions.length === 0 && allQuestions.length > 0" class="quiz__empty-filter">
          <font-awesome-icon 
            :icon="viewMode === 'unanswered' ? 'check-circle' : 'question-circle'" 
            class="quiz__empty-filter-icon" 
          />
          <p>
            <strong>
              {{ viewMode === 'unanswered' ? 'Parabéns!' : 'Nenhuma questão respondida ainda' }}
            </strong>
          </p>
          <p>
            {{ viewMode === 'unanswered' 
              ? 'Você respondeu todas as questões disponíveis!' 
              : 'Responda algumas questões para vê-las aqui.' 
            }}
          </p>
          <div class="quiz__empty-filter-actions">
            <Button 
              v-if="viewMode === 'unanswered' && answeredQuestions.length > 0"
              variant="primary" 
              @click="setViewMode('answered')"
            >
              Ver Questões Respondidas
            </Button>
            <Button 
              v-else-if="viewMode === 'answered' && unansweredQuestions.length > 0"
              variant="primary" 
              @click="setViewMode('unanswered')"
            >
              Ver Questões Não Respondidas
            </Button>
            <Button 
              variant="secondary" 
              @click="goToHome"
            >
              Voltar para Home
            </Button>
          </div>
        </div>

        <!-- Quiz Content -->
        <template v-else-if="currentQuestion">
          <div class="quiz__header">
            <button class="quiz__back-btn" @click="goToHome">
              <font-awesome-icon icon="arrow-left" />
            </button>
            <div class="quiz__header-content">
              <h2 class="quiz__title">ProvaPop! - {{ categoryName }}</h2>
              <div class="quiz__header-info">
                <div class="quiz__question-number">
                  Questão {{ currentQuestionIndex + 1 }} de {{ filteredQuestions.length }}
                  <span class="quiz__question-total">({{ totalQuestionsCount }} total)</span>
                </div>
                <div v-if="currentQuestion?.already_answered" class="quiz__already-answered-badge">
                  <font-awesome-icon icon="check-circle" />
                  Já respondida
                </div>
              </div>
            </div>
          </div>

          <!-- Question Filter Tabs -->
          <div class="quiz__filter-tabs">
            <button
              class="quiz__filter-tab"
              :class="{ 'quiz__filter-tab--active': viewMode === 'unanswered' }"
              @click="setViewMode('unanswered')"
            >
              <font-awesome-icon icon="question-circle" />
              Não Respondidas
              <span class="quiz__filter-count">({{ unansweredQuestions.length }})</span>
            </button>
            <button
              class="quiz__filter-tab"
              :class="{ 'quiz__filter-tab--active': viewMode === 'answered' }"
              @click="setViewMode('answered')"
            >
              <font-awesome-icon icon="check-circle" />
              Já Respondidas
              <span class="quiz__filter-count">({{ answeredQuestions.length }})</span>
            </button>
          </div>

          <!-- Navigation Controls -->
          <div class="quiz__navigation">
            <button
              class="quiz__nav-btn"
              :disabled="currentQuestionIndex === 0"
              @click="previousQuestion"
            >
              <font-awesome-icon icon="chevron-left" />
              Anterior
            </button>
            <div class="quiz__nav-info">
              {{ currentQuestionIndex + 1 }} / {{ filteredQuestions.length }}
            </div>
            <button
              class="quiz__nav-btn"
              :disabled="currentQuestionIndex >= filteredQuestions.length - 1"
              @click="nextQuestion"
            >
              Próxima
              <font-awesome-icon icon="chevron-right" />
            </button>
          </div>

          <div class="quiz__content">
            <!-- Music Info Section -->
            <div class="quiz__music-info">
              <div class="quiz__audio-section">
                <button 
                  class="quiz__play-btn" 
                  @click="playYoutube" 
                  :class="{ 'quiz__play-btn--playing': isPlaying }"
                  :disabled="!youtubeVideoId || isPlaying"
                >
                  <font-awesome-icon icon="play" class="quiz__play-icon" />
                </button>
                <div class="quiz__audio-info">
                  <div class="quiz__audio-title">
                    {{ currentQuestion.artist }} - {{ currentQuestion.song_title }}
                  </div>
                  <span v-if="isPlaying" style="font-size: 13px; color: var(--green-primary); font-weight: bold;">
                    >>>playing>>>
                  </span>
                  
                  <!-- BARRINHA DE PROGRESSO -->
                  <div class="quiz__audio-progress" v-if="isPlaying && audioDuration > 0" style="margin-top: 8px;">
                    <div class="quiz__audio-progress-bar" :style="{ width: `${audioProgress}%` }"></div>
                  </div>

                   <!-- Player do YouTube (Modo JS API para enganar o Safari) -->
                  <iframe 
                    ref="youtubeIframe"
                    v-show="youtubeVideoId"
                    :src="youtubeUrl"
                    allow="autoplay; encrypted-media"
                    style="width: 200px; height: 150px; opacity: 0.01; position: absolute; top: 0; left: 0; pointer-events: none;"
                  ></iframe>

                </div>
              </div>

              <!-- Year Information -->
              <div class="quiz__years-info" v-if="currentQuestion.composition_year || currentQuestion.enem_year">
                <div class="quiz__year-badge" v-if="currentQuestion.composition_year">
                  <font-awesome-icon icon="calendar-alt" />
                  <span class="quiz__year-label">Ano da Composição:</span>
                  <span class="quiz__year-value">{{ currentQuestion.composition_year }}</span>
                </div>
                <div class="quiz__year-badge quiz__year-badge--enem" v-if="currentQuestion.enem_year">
                  <font-awesome-icon icon="graduation-cap" />
                  <span class="quiz__year-label">Ano ENEM:</span>
                  <span class="quiz__year-value">{{ currentQuestion.enem_year }}</span>
                </div>
              </div>
            
            <div class="quiz__lyrics" v-if="currentQuestion.lyrics">
              <div class="quiz__lyrics-text">
                <p v-for="(line, index) in lyricsLines" :key="index">{{ line }}</p>
              </div>
            </div>

            <div class="quiz__statement">
              <p class="quiz__statement-text">{{ currentQuestion.statement }}</p>
            </div>

            <div class="quiz__options">
              <OptionButton
                v-for="(option, index) in questionOptions"
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

          <div class="quiz__actions" v-if="selectedOption !== null && !answered">
            <Button 
              variant="primary" 
              size="lg" 
              full-width 
              @click="confirmAnswer"
            >
              Confirmar Resposta
            </Button>
          </div>

          <!-- Skip Button -->
          <div class="quiz__skip-action" v-if="!answered && selectedOption === null">
            <Button 
              variant="secondary" 
              size="md" 
              full-width 
              @click="nextQuestion"
            >
              Pular Questão
              <font-awesome-icon icon="arrow-right" />
            </Button>
          </div>

            <div class="quiz__feedback" v-if="answered">
              <div v-if="alreadyAnswered" class="quiz__already-answered-warning">
                <font-awesome-icon icon="info-circle" class="quiz__warning-icon" />
                <p>
                  <strong>Você já respondeu esta questão antes.</strong>
                  <span v-if="previousResult !== null">
                    Sua resposta anterior foi <strong>{{ previousResult ? 'correta' : 'incorreta' }}</strong>.
                  </span>
                  Esta tentativa não afetará sua pontuação.
                </p>
              </div>
              
              <div class="quiz__feedback-content" :class="isCorrect ? 'quiz__feedback--correct' : 'quiz__feedback--wrong'">
                <font-awesome-icon 
                  :icon="isCorrect ? 'check-circle' : 'times-circle'" 
                  class="quiz__feedback-icon"
                />
                <div class="quiz__feedback-text">
                  <strong>{{ isCorrect ? 'Resposta Correta!' : 'Resposta Incorreta' }}</strong>
                  <p v-if="!isCorrect">A resposta correta é a alternativa {{ correctAnswer }}.</p>
                  <p v-if="pointsEarned && pointsValue !== 0" class="quiz__points-info">
                    <strong>{{ pointsValue > 0 ? '+' : '' }}{{ pointsValue }} pontos</strong>
                  </p>
                  <p v-else-if="alreadyAnswered" class="quiz__points-info quiz__points-info--no-points">
                    Nenhum ponto ganho/perdido (já respondida anteriormente)
                  </p>
                </div>
              </div>

            <!-- Comment Section -->
            <div class="quiz__comment-section" v-if="isCorrect && currentQuestion.comment">
              <div class="quiz__comment-header">
                <font-awesome-icon icon="comment" class="quiz__comment-icon" />
                <h3 class="quiz__comment-title">Comentário</h3>
              </div>
              <div class="quiz__comment-content">
                <p>{{ currentQuestion.comment }}</p>
              </div>
            </div>

              <!-- Curiosidade Section -->
              <div class="quiz__curiosity-section" v-if="isCorrect && currentQuestion.curiosity">
                <div class="quiz__curiosity-header">
                  <font-awesome-icon icon="star" class="quiz__curiosity-icon" />
                  <h3 class="quiz__curiosity-title">Curiosidade</h3>
                </div>
                <div class="quiz__curiosity-content">
                  <p>{{ currentQuestion.curiosity }}</p>
                </div>
              </div>
            <div class="quiz__feedback-actions">
              <Button 
                v-if="hasNextQuestion"
                variant="secondary" 
                size="md" 
                full-width 
                @click="nextQuestion" 
                class="quiz__next-btn"
              >
                Próxima Questão
              </Button>
              <Button 
                v-else
                variant="primary" 
                size="md" 
                full-width 
                @click="finishQuiz" 
                class="quiz__finish-btn"
              >
                Finalizar Quiz
              </Button>
            </div></div></div></template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import confetti from 'canvas-confetti'
import Card from '@/components/Card.vue'
import Button from '@/components/Button.vue'
import OptionButton from '@/components/OptionButton.vue'
import { api } from '@/services/api'

const router = useRouter()
const route = useRoute()

const category = computed(() => (route.params.category as string) || 'enem')

const categoryNames: Record<string, string> = {
  'enem': 'ENEM',
  'fuvest': 'FUVEST',
  'unicamp': 'UNICAMP',
  'outros': 'Outros'
}

const categoryName = computed(() => categoryNames[category.value] || 'ENEM')

// State
const loading = ref(true)
const error = ref<string | null>(null)
const allQuestions = ref<any[]>([]) 
const currentQuestionIndex = ref(0)
const selectedOption = ref<number | null>(null)
const answered = ref(false)
const isCorrect = ref(false)
const correctAnswer = ref('')

// VARIAVEIS DO PLAYER
const isPlaying = ref(false)
const youtubeIframe = ref<HTMLIFrameElement | null>(null)
const audioProgress = ref(0)
const audioDuration = ref(0)
let progressInterval: any = null

// Mágicas do YouTube
const youtubeVideoId = computed(() => {
  const rawData = currentQuestion.value?.music_drive_url
  if (!rawData) return null
  const firstPart = rawData.split(',')[0].trim()
  if (firstPart.includes('youtu')) {
    const regExp = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/
    const match = firstPart.match(regExp)
    return (match && match[2].length === 11) ? match[2] : null
  }
  return firstPart.length === 11 ? firstPart : null
})

const youtubeStartTime = computed(() => {
  const rawData = currentQuestion.value?.music_drive_url
  if (!rawData) return ''
  const parts = rawData.split(',')
  return parts[1] ? parts[1].trim() : '' 
})

const youtubeEndTime = computed(() => {
  const rawData = currentQuestion.value?.music_drive_url
  if (!rawData) return ''
  const parts = rawData.split(',')
  return parts[2] ? parts[2].trim() : '' 
})

// Aqui está o truque principal: Carregamos o URL antes, com a API de JS ativada (enablejsapi=1)
const youtubeUrl = computed(() => {
  if (!youtubeVideoId.value) return 'about:blank'
  return `https://www.youtube.com/embed/${youtubeVideoId.value}?enablejsapi=1&controls=0&playsinline=1&start=${youtubeStartTime.value}&end=${youtubeEndTime.value}`
})

const alreadyAnswered = ref(false)
const previousResult = ref<boolean | null>(null)
const pointsEarned = ref(false)
const pointsValue = ref(0)
const viewMode = ref<'unanswered' | 'answered'>('unanswered') 
const displayedQuestion = ref<any>(null) 

const answeredQuestions = computed(() => {
  return allQuestions.value.filter(q => q.already_answered === true)
})

const unansweredQuestions = computed(() => {
  return allQuestions.value.filter(q => !q.already_answered || q.already_answered === false)
})

const filteredQuestions = computed(() => {
  return viewMode.value === 'unanswered' ? unansweredQuestions.value : answeredQuestions.value
})

const currentQuestion = computed(() => {
  if (displayedQuestion.value && answered.value) {
    return displayedQuestion.value
  }
  if (filteredQuestions.value.length === 0) return null
  if (currentQuestionIndex.value >= filteredQuestions.value.length) {
    currentQuestionIndex.value = 0
  }
  const question = filteredQuestions.value[currentQuestionIndex.value]
  if (!answered.value && question) {
    displayedQuestion.value = question
  }
  return question
})

const totalQuestionsCount = computed(() => allQuestions.value.length)
const hasNextQuestion = computed(() => currentQuestionIndex.value < filteredQuestions.value.length - 1)
const hasPreviousQuestion = computed(() => currentQuestionIndex.value > 0)
const lyricsLines = computed(() => {
  if (!currentQuestion.value?.lyrics) return []
  return currentQuestion.value.lyrics.split('\n').filter((line: string) => line.trim())
})
const questionOptions = computed(() => {
  if (!currentQuestion.value) return []
  const q = currentQuestion.value
  return [
    { label: 'A', text: q.options.A, isCorrect: false },
    { label: 'B', text: q.options.B, isCorrect: false },
    { label: 'C', text: q.options.C, isCorrect: false },
    { label: 'D', text: q.options.D, isCorrect: false },
    { label: 'E', text: q.options.E, isCorrect: false },
  ]
})

async function loadQuestions(forceRefresh = false) {
  loading.value = true
  error.value = null
  try {
    if (forceRefresh) {
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
    const categoryParam = category.value
    const categoryMap: Record<string, string> = {
      'unicamp': 'Unicamp',
      'fuvest': 'Fuvest',
      'enem': 'Enem',
      'outros': 'Outros'
    }
    const backendCategory = categoryMap[categoryParam] || categoryParam
    const data = await api.questions.getAll(backendCategory)
    
    if (data && data.length > 0) {
      allQuestions.value = data.sort(() => Math.random() - 0.5)
      if (unansweredQuestions.value.length > 0) {
        viewMode.value = 'unanswered'
        currentQuestionIndex.value = 0
      } else if (answeredQuestions.value.length > 0) {
        viewMode.value = 'answered'
        currentQuestionIndex.value = 0
      }
      resetQuestionState()
    } else {
      allQuestions.value = []
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao carregar questões'
  } finally {
    loading.value = false
  }
}

function resetQuestionState() {
  selectedOption.value = null
  answered.value = false
  isCorrect.value = false
  correctAnswer.value = ''
  
  // Força o vídeo anterior a pausar usando a API
  if (youtubeIframe.value && isPlaying.value) {
    youtubeIframe.value.contentWindow?.postMessage(
      JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), 
      '*'
    )
  }
  
  isPlaying.value = false
  audioProgress.value = 0
  if (progressInterval) clearInterval(progressInterval)
  
  alreadyAnswered.value = false
  previousResult.value = null
  pointsEarned.value = false
  pointsValue.value = 0
  displayedQuestion.value = null 
  
  if (currentQuestion.value && typeof currentQuestion.value === 'object' && currentQuestion.value !== null) {
    if (currentQuestion.value.already_answered) {
      alreadyAnswered.value = true
      previousResult.value = (currentQuestion.value.previous_result !== undefined && currentQuestion.value.previous_result !== null) 
        ? currentQuestion.value.previous_result 
        : null
    }
  }
}

function playYoutube() {
  if (youtubeVideoId.value && youtubeIframe.value) {
    isPlaying.value = true
    
    // Grito Ninja para a API do YouTube: "Toca agora!"
    youtubeIframe.value.contentWindow?.postMessage(
      JSON.stringify({ event: 'command', func: 'playVideo', args: [] }), 
      '*'
    )
    
    audioProgress.value = 0
    const start = parseInt(youtubeStartTime.value) || 0
    const end = parseInt(youtubeEndTime.value) || 0
    
    if (end > start) {
      audioDuration.value = end - start
      const intervalMs = 100 
      const step = (100 / (audioDuration.value * 1000)) * intervalMs
      
      clearInterval(progressInterval)
      
      // O SEGREDO AQUI: Espera 1 segundo (1000ms) para o buffer antes de mover a barra
      setTimeout(() => {
        // Só começa a contar se a música ainda estiver com status de tocando
        if (isPlaying.value) {
          progressInterval = setInterval(() => {
            audioProgress.value += step
            if (audioProgress.value >= 100) {
              audioProgress.value = 100
              isPlaying.value = false 
              // Pausa quando a barra acaba
              youtubeIframe.value?.contentWindow?.postMessage(
                JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), 
                '*'
              )
              clearInterval(progressInterval)
            }
          }, intervalMs)
        }
      }, 1000) // <- Aqui está o 1 segundo de "gordura"
    }
  }
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

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now()
    if (timeLeft <= 0) return clearInterval(interval)

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

async function confirmAnswer() {
  if (selectedOption.value === null || !currentQuestion.value) return
  const selectedLabel = questionOptions.value[selectedOption.value].label
  
  try {
    const result = await api.questions.checkAnswer(currentQuestion.value.id, selectedLabel)
    answered.value = true
    isCorrect.value = result.is_correct
    correctAnswer.value = result.correct_answer
    alreadyAnswered.value = result.already_answered || false
    previousResult.value = result.previous_result
    pointsEarned.value = result.points_earned || false
    pointsValue.value = result.points || 0
    
    if (!displayedQuestion.value && currentQuestion.value) {
      displayedQuestion.value = { ...currentQuestion.value }
    }
    if (displayedQuestion.value) {
      displayedQuestion.value.already_answered = true
      displayedQuestion.value.previous_result = previousResult.value
    }
    
    const currentQ = displayedQuestion.value || currentQuestion.value
    if (currentQ && typeof currentQ === 'object' && currentQ !== null) {
      try {
        const questionId = currentQ.id
        if (questionId) {
          const questionInAllList = allQuestions.value.find(q => q && q.id === questionId)
          if (questionInAllList && typeof questionInAllList === 'object' && questionInAllList !== null) {
            try {
              if (!('already_answered' in questionInAllList)) {
                questionInAllList.already_answered = false
              }
              if (!('previous_result' in questionInAllList)) {
                questionInAllList.previous_result = null
              }
              questionInAllList.already_answered = true
              questionInAllList.previous_result = previousResult.value
            } catch (err) {}
          }
        }
      } catch (err) {}
    }
    
    if (isCorrect.value && pointsEarned.value) {
      setTimeout(() => triggerConfetti(), 300)
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao verificar resposta'
  }
}

function nextQuestion() {
  if (hasNextQuestion.value) {
    currentQuestionIndex.value++
    resetQuestionState()
  } else if (viewMode.value === 'unanswered' && answeredQuestions.value.length > 0) {
    viewMode.value = 'answered'
    currentQuestionIndex.value = 0
    resetQuestionState()
  }
}

function previousQuestion() {
  if (hasPreviousQuestion.value) {
    currentQuestionIndex.value--
    resetQuestionState()
  }
}

function setViewMode(mode: 'unanswered' | 'answered') {
  viewMode.value = mode
  currentQuestionIndex.value = 0
  resetQuestionState()
}

function finishQuiz() {
  router.push('/')
}

function goToHome() {
  router.push('/')
}

onMounted(() => {
  loadQuestions(true) 
})

onUnmounted(() => {
  isPlaying.value = false 
  if (youtubeIframe.value) {
    youtubeIframe.value.contentWindow?.postMessage(
      JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), 
      '*'
    )
  }
  if (progressInterval) clearInterval(progressInterval)
})
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
  display: flex;
  align-items: center;
  gap: 4px;
}

.quiz__question-total {
  color: var(--gray);
  font-size: 11px;
}

/* Filter Tabs */
.quiz__filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 2px solid var(--gray-light);
}

.quiz__filter-tab {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--gray-dark);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all var(--transition-base);
}

.quiz__filter-tab:hover {
  background: var(--gray-light);
  color: var(--black-soft);
}

.quiz__filter-tab--active {
  color: var(--green-primary);
  border-bottom-color: var(--green-primary);
  font-weight: 600;
}

.quiz__filter-count {
  font-size: 12px;
  color: var(--gray);
  font-weight: 400;
}

.quiz__filter-tab--active .quiz__filter-count {
  color: var(--green-primary);
  font-weight: 500;
}

/* Navigation */
.quiz__navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
  margin-bottom: 16px;
}

.quiz__nav-btn {
  padding: 10px 16px;
  background: var(--white);
  border: 2px solid var(--gray-light);
  border-radius: var(--border-radius-md);
  color: var(--black-soft);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all var(--transition-base);
}

.quiz__nav-btn:hover:not(:disabled) {
  background: var(--green-pastel);
  border-color: var(--green-primary);
  color: var(--green-primary);
  transform: translateY(-1px);
}

.quiz__nav-btn:active:not(:disabled) {
  transform: translateY(0);
}

.quiz__nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.quiz__nav-info {
  font-size: 14px;
  font-weight: 600;
  color: var(--gray-dark);
  padding: 0 12px;
}

/* Skip Action */
.quiz__skip-action {
  margin-top: 12px;
  margin-bottom: 16px;
}

.quiz__feedback-actions {
  margin-top: 16px;
}

/* Music Info Section */
.quiz__music-info {
  margin-bottom: 16px;
}

.quiz__audio-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
  border: 2px solid var(--gray-light);
  margin-bottom: 12px;
  position: relative;
  overflow: hidden;
}

/* Years Info */
.quiz__years-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--white-off);
  border-radius: var(--border-radius-md);
  border: 2px solid var(--gray-light);
}

.quiz__year-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--white);
  border-radius: var(--border-radius-full);
  border: 2px solid var(--green-pastel);
  font-size: 13px;
  color: var(--black-soft);
}

.quiz__year-badge--enem {
  border-color: var(--yellow-pastel);
  background: var(--yellow-pastel);
}

.quiz__year-badge svg {
  color: var(--green-primary);
  font-size: 14px;
}

.quiz__year-badge--enem svg {
  color: var(--yellow-primary);
}

.quiz__year-label {
  font-weight: 500;
  color: var(--gray-dark);
}

.quiz__year-value {
  font-weight: 600;
  color: var(--green-primary);
}

.quiz__year-badge--enem .quiz__year-value {
  color: var(--yellow-primary);
}

/* Comment Section */
.quiz__comment-section {
  margin-bottom: 16px;
  padding: 16px;
  background: linear-gradient(135deg, var(--yellow-pastel) 0%, #fff5e6 100%);
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--yellow-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.quiz__comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.quiz__comment-icon {
  color: var(--yellow-primary);
  font-size: 18px;
}

.quiz__comment-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--yellow-dark);
  margin: 0;
}

.quiz__comment-content {
  color: var(--black-soft);
  font-size: 14px;
  line-height: 1.6;
}

.quiz__comment-content p {
  margin: 0;
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
  z-index: 10; /* Mantém o botão acima do iframe invisível */
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
  z-index: 10;
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
  background: var(--green-primary);
  border-radius: var(--border-radius-full);
  transition: width 0.1s linear;
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

.quiz__finish-btn {
  margin-top: 12px;
}

.quiz__feedback-actions {
  margin-top: 16px;
}

/* Curiosity Section */
.quiz__curiosity-section {
  margin-top: 20px;
  padding: 16px;
  background: linear-gradient(135deg, var(--green-pastel) 0%, #e8f8f0 100%);
  border-radius: var(--border-radius-md);
  border-left: 4px solid var(--green-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.quiz__curiosity-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.quiz__curiosity-icon {
  color: var(--green-primary);
  font-size: 18px;
  animation: sparkle 2s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.quiz__curiosity-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--green-dark);
  margin: 0;
}

.quiz__curiosity-content {
  color: var(--black-soft);
  font-size: 14px;
  line-height: 1.6;
}

.quiz__curiosity-content p {
  margin: 0;
}

/* Empty Filter State */
.quiz__empty-filter {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 400px;
}

.quiz__empty-filter-icon {
  font-size: 64px;
  color: var(--green-primary);
  margin-bottom: 20px;
  opacity: 0.7;
}

.quiz__empty-filter p {
  color: var(--black-soft);
  font-size: 16px;
  margin: 8px 0;
}

.quiz__empty-filter p strong {
  display: block;
  font-size: 18px;
  color: var(--green-primary);
  margin-bottom: 8px;
}

.quiz__empty-filter-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  max-width: 300px;
  width: 100%;
}

.quiz__loading,
.quiz__error,
.quiz__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 400px;
}

.quiz__loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--gray-light);
  border-top-color: var(--green-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.quiz__loading p,
.quiz__error p,
.quiz__empty p {
  color: var(--black-soft);
  font-size: 16px;
  margin: 8px 0;
}

.quiz__error-icon,
.quiz__empty-icon {
  font-size: 64px;
  color: var(--gray-dark);
  margin-bottom: 20px;
}

.quiz__error-icon {
  color: var(--yellow-primary);
}

.quiz__empty-hint {
  font-size: 14px;
  color: var(--gray-dark);
  margin-top: 8px;
}

.quiz__play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.quiz__header-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.quiz__already-answered-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--yellow-pastel);
  color: var(--yellow-dark);
  border-radius: var(--border-radius-full);
  font-size: 12px;
  font-weight: 600;
  border: 1px solid var(--yellow-primary);
}

.quiz__already-answered-warning {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--yellow-pastel);
  border: 2px solid var(--yellow-primary);
  border-radius: var(--border-radius-md);
  margin-bottom: 16px;
}

.quiz__warning-icon {
  font-size: 20px;
  color: var(--yellow-dark);
  flex-shrink: 0;
  margin-top: 2px;
}

.quiz__already-answered-warning p {
  margin: 0;
  color: var(--black-soft);
  font-size: 14px;
  line-height: 1.6;
}

.quiz__already-answered-warning strong {
  color: var(--yellow-dark);
}

.quiz__points-info {
  margin-top: 8px;
  font-size: 14px;
  color: var(--green-dark);
  font-weight: 600;
}

.quiz__points-info--no-points {
  color: var(--gray-dark);
  font-weight: 500;
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
