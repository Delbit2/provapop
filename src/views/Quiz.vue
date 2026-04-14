<template>
  <div class="quiz">
    <div class="quiz__container animate-fade-down">
      <Card variant="elevated" class="quiz__card">
        <!-- Loading State -->
        <div v-if="loading" class="quiz__loading">
          <div class="quiz__loading-spinner"></div>
          <p>Preparando a arena...</p>
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
          <p>Nenhuma missão disponível aqui.</p>
          <p class="quiz__empty-hint">Aguardando o Diretor adicionar questões na base.</p>
          <Button variant="primary" @click="goToHome">Voltar ao QG</Button>
        </div>

        <!-- Empty Filter State -->
        <div v-else-if="filteredQuestions.length === 0 && allQuestions.length > 0" class="quiz__empty-filter">
          <font-awesome-icon 
            :icon="viewMode === 'unanswered' ? 'trophy' : 'question-circle'" 
            class="quiz__empty-filter-icon" 
            :class="{ 'gold-icon': viewMode === 'unanswered' }"
          />
          <p>
            <strong class="quiz__empty-title">
              {{ viewMode === 'unanswered' ? 'Missão Cumprida!' : 'Área Limpa' }}
            </strong>
          </p>
          <p class="quiz__empty-subtitle">
            {{ viewMode === 'unanswered' 
              ? 'Você gabaritou todas as questões disponíveis desta categoria!' 
              : 'Você ainda não respondeu nenhuma questão. Que tal começar agora?' 
            }}
          </p>
          <div class="quiz__empty-filter-actions">
            <Button 
              v-if="viewMode === 'unanswered' && answeredQuestions.length > 0"
              variant="primary" 
              @click="setViewMode('answered')"
            >
              Revisar Questões
            </Button>
            <Button 
              v-else-if="viewMode === 'answered' && unansweredQuestions.length > 0"
              variant="primary" 
              @click="setViewMode('unanswered')"
            >
              Ir para as Inéditas
            </Button>
            <Button 
              variant="secondary" 
              @click="goToHome"
            >
              Voltar ao Início
            </Button>
          </div>
        </div>

        <!-- Quiz Content -->
        <template v-else-if="currentQuestion">
          <!-- CABEÇALHO MAIS COMPACTO -->
          <div class="quiz__header animate-slide-up">
            <button class="quiz__back-btn" @click="goToHome" title="Voltar">
              <font-awesome-icon icon="arrow-left" />
            </button>
            <div class="quiz__header-content">
              <h2 class="quiz__title">{{ categoryName }}</h2>
              <div class="quiz__header-info">
                <div v-if="currentQuestion?.already_answered" class="quiz__already-answered-badge">
                  <font-awesome-icon icon="check-double" />
                  Revisão
                </div>
              </div>
            </div>
          </div>

          <!-- 🚀 BARRA DE PROGRESSO PREMIUM -->
          <div class="quiz__progress-container animate-slide-up" style="animation-delay: 0.1s;">
            <div class="quiz__progress-header">
              <span class="quiz__progress-text">Questão {{ currentQuestionIndex + 1 }} de {{ filteredQuestions.length }}</span>
              <span class="quiz__progress-percentage">{{ porcentagemProgresso }}%</span>
            </div>
            <div class="quiz__progress-bar-bg">
              <div class="quiz__progress-bar-fill" :style="{ width: porcentagemProgresso + '%' }"></div>
            </div>
          </div>

          <!-- Question Filter Tabs -->
          <div class="quiz__filter-tabs animate-slide-up" style="animation-delay: 0.15s;">
            <button
              class="quiz__filter-tab"
              :class="{ 'quiz__filter-tab--active': viewMode === 'unanswered' }"
              @click="setViewMode('unanswered')"
            >
              <font-awesome-icon icon="compass" />
              Inéditas
              <span class="quiz__filter-count">{{ unansweredQuestions.length }}</span>
            </button>
            <button
              class="quiz__filter-tab"
              :class="{ 'quiz__filter-tab--active': viewMode === 'answered' }"
              @click="setViewMode('answered')"
            >
              <font-awesome-icon icon="history" />
              Respondidas
              <span class="quiz__filter-count">{{ answeredQuestions.length }}</span>
            </button>
          </div>

          <!-- Navigation Controls -->
          <div class="quiz__navigation animate-slide-up" style="animation-delay: 0.2s;">
            <button
              class="quiz__nav-btn"
              :disabled="currentQuestionIndex === 0"
              @click="previousQuestion"
            >
              <font-awesome-icon icon="chevron-left" />
            </button>
            <div class="quiz__nav-info">
              {{ currentQuestionIndex + 1 }} / {{ filteredQuestions.length }}
            </div>
            <button
              class="quiz__nav-btn"
              :disabled="currentQuestionIndex >= filteredQuestions.length - 1"
              @click="nextQuestion"
            >
              <font-awesome-icon icon="chevron-right" />
            </button>
          </div>

          <div class="quiz__content animate-slide-up" style="animation-delay: 0.25s;">
            <!-- Music Info Section -->
            <div class="quiz__music-info">
              <div class="quiz__audio-section">
                <button 
                  class="quiz__play-btn" 
                  @click="playYoutube" 
                  :class="{ 'quiz__play-btn--playing': isPlaying }"
                  :disabled="!youtubeVideoId || isPlaying"
                >
                  <font-awesome-icon :icon="isPlaying ? 'music' : 'play'" class="quiz__play-icon" :class="{ 'fa-beat': isPlaying }" />
                </button>
                <div class="quiz__audio-info">
                  <!-- 🎯 TÍTULO DA MÚSICA -->
                  <div class="quiz__audio-title">
                    {{ currentQuestion.artist }} - {{ currentQuestion.song_title }}
                  </div>
                  <span v-if="isPlaying" class="quiz__playing-text">
                    Tocando agora...
                  </span>
                  
                  <!-- BARRINHA DE PROGRESSO DO AUDIO -->
                  <div class="quiz__audio-progress" v-if="isPlaying && audioDuration > 0">
                    <div class="quiz__audio-progress-bar" :style="{ width: `${audioProgress}%` }"></div>
                  </div>

                   <!-- Player do YouTube -->
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
                  <span class="quiz__year-label">Lançamento:</span>
                  <span class="quiz__year-value">{{ currentQuestion.composition_year }}</span>
                </div>
                <div class="quiz__year-badge quiz__year-badge--enem" v-if="currentQuestion.enem_year">
                  <font-awesome-icon icon="graduation-cap" />
                  <span class="quiz__year-label">ENEM:</span>
                  <span class="quiz__year-value">{{ currentQuestion.enem_year }}</span>
                </div>
              </div>
            
            <!-- 📖 LETRA DA MÚSICA - PAPEL PÓLEN PREMIUM -->
            <div class="quiz__lyrics" v-if="currentQuestion.lyrics">
              <font-awesome-icon icon="quote-left" class="quiz__quote-icon" />
              <div class="quiz__lyrics-text">
                <p v-for="(line, index) in lyricsLines" :key="index">{{ line }}</p>
              </div>
            </div>

            <!-- 📝 CRÉDITOS DA CANÇÃO (FLUTUANTES PREMIUM) -->
            <div class="quiz__credits animate-slide-up" v-if="currentQuestion.credits">
              <div class="quiz__credits-pill">
                {{ currentQuestion.credits }}
              </div>
            </div>

            <!-- 🎯 ENUNCIADO -->
            <div class="quiz__statement">
              <p class="quiz__statement-text">{{ currentQuestion.statement }}</p>
            </div>

            <!-- 🎯 ALTERNATIVAS -->
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
            <!-- BOTÃO TURQUESA SURPRESA -->
            <Button 
              variant="primary" 
              size="lg" 
              full-width 
              @click="confirmAnswer"
              class="btn-turquesa"
            >
              Confirmar Resposta
            </Button>
          </div>

          <!-- Skip Button - LARANJINHA CLARO -->
          <div class="quiz__skip-action" v-if="!answered && selectedOption === null">
            <Button 
              variant="secondary" 
              size="md" 
              full-width 
              @click="nextQuestion"
              class="btn-ghost-orange"
            >
              Pular Questão
              <font-awesome-icon icon="arrow-right" />
            </Button>
          </div>

            <div class="quiz__feedback" v-if="answered">
              <div v-if="alreadyAnswered" class="quiz__already-answered-warning">
                <font-awesome-icon icon="info-circle" class="quiz__warning-icon" />
                <p>
                  <strong>Modo Revisão Ativo</strong><br>
                  Sua resposta original foi <strong>{{ previousResult ? 'correta' : 'incorreta' }}</strong>.
                  Esta tentativa não altera sua pontuação no ranking.
                </p>
              </div>
              
              <div class="quiz__feedback-content" :class="isCorrect ? 'quiz__feedback--correct' : 'quiz__feedback--wrong'">
                <font-awesome-icon 
                  :icon="isCorrect ? 'check-circle' : 'times-circle'" 
                  class="quiz__feedback-icon"
                />
                <div class="quiz__feedback-text">
                  <strong>{{ isCorrect ? 'Excelente! 🎉' : 'Quase lá!' }}</strong>
                  <p v-if="!isCorrect">A resposta certa era a alternativa <b>{{ correctAnswer }}</b>.</p>
                  
                  <div class="quiz__points-badge" v-if="pointsEarned && pointsValue !== 0">
                    <font-awesome-icon icon="star" class="star-icon" />
                    <span>{{ pointsValue > 0 ? '+' : '' }}{{ pointsValue }} pontos conquistados!</span>
                  </div>
                </div>
              </div>

            <!-- Comment Section -->
            <div class="quiz__comment-section" v-if="isCorrect && currentQuestion.comment">
              <div class="quiz__comment-header">
                <div class="icon-wrapper">
                  <font-awesome-icon icon="key" class="quiz__comment-icon" />
                </div>
                <h3 class="quiz__comment-title">Chave da Questão</h3>
              </div>
              <div class="quiz__comment-content">
                <p>{{ currentQuestion.comment }}</p>
              </div>
            </div>

              <!-- Curiosidade Section -->
              <div class="quiz__curiosity-section" v-if="isCorrect && currentQuestion.curiosity">
                <div class="quiz__curiosity-header">
                  <div class="icon-wrapper-gold">
                    <font-awesome-icon icon="lightbulb" class="quiz__curiosity-icon" />
                  </div>
                  <h3 class="quiz__curiosity-title">Você Sabia?</h3>
                </div>
                <div class="quiz__curiosity-content">
                  <p>{{ currentQuestion.curiosity }}</p>
                </div>
              </div>
            <div class="quiz__feedback-actions">
              <Button 
                v-if="hasNextQuestion"
                variant="primary" 
                size="lg" 
                full-width 
                @click="nextQuestion" 
                class="quiz__next-btn btn-premium"
              >
                Próxima Questão <font-awesome-icon icon="arrow-right" />
              </Button>
              <Button 
                v-else
                variant="primary" 
                size="lg" 
                full-width 
                @click="finishQuiz" 
                class="quiz__finish-btn btn-premium"
              >
                Finalizar Desafio <font-awesome-icon icon="flag-checkered" />
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
  'enem': 'Missão ENEM',
  'fuvest': 'Missão FUVEST',
  'unicamp': 'Missão UNICAMP',
  'outros': 'Treino Livre',
  'foco': 'Da Terra à Lua'
}

const categoryName = computed(() => categoryNames[category.value] || 'Desafio')

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

const porcentagemProgresso = computed(() => {
  if (filteredQuestions.value.length === 0) return 0
  return Math.round(((currentQuestionIndex.value + 1) / filteredQuestions.value.length) * 100)
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

// 🚀 O ELEVADOR DE QUESTÕES
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

async function loadQuestions(forceRefresh = false) {
  loading.value = true
  error.value = null
  try {
    if (forceRefresh) {
      await new Promise(resolve => setTimeout(resolve, 1000))
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
    
    console.log("🕵️‍♂️ DADOS QUE CHEGARAM DO BACKEND:", data[0])

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
      
      setTimeout(() => {
        if (isPlaying.value) {
          progressInterval = setInterval(() => {
            audioProgress.value += step
            if (audioProgress.value >= 100) {
              audioProgress.value = 100
              isPlaying.value = false 
              youtubeIframe.value?.contentWindow?.postMessage(
                JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }), 
                '*'
              )
              clearInterval(progressInterval)
            }
          }, intervalMs)
        }
      }, 1000) 
    }
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
    colors: ['#A32A52', '#E25822', '#D4AF37', '#2ACEA4', '#f39c12', '#f7dc6f']
  })

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now()
    if (timeLeft <= 0) return clearInterval(interval)

    const particleCount = 50 * (timeLeft / duration)
    
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
      colors: ['#A32A52', '#E25822', '#D4AF37', '#2ACEA4']
    })
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
      colors: ['#A32A52', '#E25822', '#D4AF37', '#2ACEA4']
    })
  }, 250)
}

function selectOption(index: number) {
  if (!answered.value) {
    selectedOption.value = index
  }
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

// O Elevador age ao avançar
function nextQuestion() {
  if (hasNextQuestion.value) {
    currentQuestionIndex.value++
    resetQuestionState()
    scrollToTop()
  } else if (viewMode.value === 'unanswered' && answeredQuestions.value.length > 0) {
    viewMode.value = 'answered'
    currentQuestionIndex.value = 0
    resetQuestionState()
    scrollToTop()
  }
}

// O Elevador age ao voltar
function previousQuestion() {
  if (hasPreviousQuestion.value) {
    currentQuestionIndex.value--
    resetQuestionState()
    scrollToTop()
  }
}

// O Elevador age ao alternar as abas
function setViewMode(mode: 'unanswered' | 'answered') {
  viewMode.value = mode
  currentQuestionIndex.value = 0
  resetQuestionState()
  scrollToTop()
}

// 👇 A MÁGICA FOI FEITA AQUI! O TELETRANSPORTE PARA O TROFÉU! 🏆
function finishQuiz() {
  router.push('/missao-cumprida')
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
  --primary: #A32A52; 
  --primary-dark: #7A1E3B;
  --secondary: #E25822;
  --text-main: #2d2422;
  --text-muted: #665651;
  --border-light: rgba(163, 42, 82, 0.1);
  --success: #2e7d32;
  --success-bg: #e8f5e9;
  --error: #c62828;
  --error-bg: #ffebee;
  --gold: #D4AF37;
  --gold-bg: #fefcf5;

  min-height: 100vh;
  padding: 16px;
  background-color: #FFF4EF;
  background-image: linear-gradient(180deg, #FFF4EF 0%, #FFFFFF 35%, #FCF2EE 80%, #EBD2CB 100%);
  overflow-x: hidden;
}

.quiz__container {
  max-width: 100%;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

:deep(.quiz__card) {
  background: rgba(255, 255, 255, 0.94) !important;
  backdrop-filter: blur(15px) !important;
  border-radius: 24px !important;
  border: 1px solid rgba(255, 255, 255, 0.8) !important;
  box-shadow: 0 15px 35px rgba(163, 42, 82, 0.08) !important;
  padding: 20px;
}

.animate-slide-up {
  opacity: 0;
  transform: translateY(20px);
  animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-fade-down {
  opacity: 0;
  transform: translateY(-15px);
  animation: fadeDown 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUpFade {
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeDown {
  to { opacity: 1; transform: translateY(0); }
}

.quiz__content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quiz__header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px; 
  padding-bottom: 12px; 
  border-bottom: 2px solid var(--border-light);
}

.quiz__back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #fdf5f3;
  color: var(--primary);
  border: 1px solid rgba(163, 42, 82, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 18px;
  flex-shrink: 0;
}

.quiz__back-btn:hover {
  background: var(--primary);
  color: #fff;
  transform: scale(1.05);
  box-shadow: 0 4px 10px rgba(163, 42, 82, 0.2);
}

.quiz__header-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.quiz__title {
  font-size: 22px;
  font-weight: 900;
  color: var(--primary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.quiz__header-info {
  margin-top: 4px;
}

.quiz__already-answered-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: rgba(163, 42, 82, 0.05);
  color: var(--primary);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.quiz__progress-container {
  margin-bottom: 16px; 
}

.quiz__progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.quiz__progress-text {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.quiz__progress-percentage {
  font-size: 16px;
  font-weight: 900;
  color: var(--secondary);
}

.quiz__progress-bar-bg {
  height: 14px;
  background-color: rgba(163, 42, 82, 0.05);
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(163, 42, 82, 0.1);
}

.quiz__progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--secondary), var(--primary));
  border-radius: 14px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.quiz__progress-bar-fill::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.quiz__filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  background: #FDF5F2; 
  padding: 6px;
  border-radius: 16px;
  border: 1px solid rgba(226, 88, 34, 0.08);
}

.quiz__filter-tab {
  flex: 1;
  padding: 10px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.quiz__filter-tab--active {
  background: #fff;
  color: var(--primary);
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  font-weight: 800;
}

.quiz__filter-count {
  background: rgba(0,0,0,0.05);
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
}

.quiz__filter-tab--active .quiz__filter-count {
  background: rgba(163, 42, 82, 0.1);
  color: var(--primary);
}

.quiz__navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px; 
}

.quiz__nav-btn {
  width: 40px;
  height: 40px;
  background: #fff;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  color: var(--primary);
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

.quiz__nav-btn:not(:disabled):hover {
  background: var(--primary);
  color: #fff;
  transform: translateY(-2px);
}

.quiz__nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  background: transparent;
}

.quiz__nav-info {
  font-size: 14px;
  font-weight: 800;
  color: var(--text-muted);
}

.quiz__audio-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px; 
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.8);
  box-shadow: 0 8px 20px rgba(163, 42, 82, 0.04);
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}

.quiz__play-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: var(--white);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 6px 15px rgba(163, 42, 82, 0.25);
  flex-shrink: 0;
}

.quiz__play-btn:active {
  transform: scale(0.95);
}

.quiz__play-btn--playing {
  background: linear-gradient(135deg, var(--secondary) 0%, #b84112 100%);
  box-shadow: 0 6px 15px rgba(226, 88, 34, 0.25);
}

.quiz__play-icon {
  font-size: 22px;
  color: #fff;
  margin-left: 4px; 
}

.quiz__play-btn--playing .quiz__play-icon {
  margin-left: 0;
}

.quiz__audio-info {
  flex: 1;
  min-width: 0;
}

.quiz__audio-title {
  font-size: 20px;
  font-weight: 700; 
  color: #1a1412; 
  margin-bottom: 6px;
  line-height: 1.4;
  letter-spacing: -0.3px;
}

.quiz__playing-text {
  font-size: 12px;
  color: var(--secondary);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  animation: pulse-text 1.5s infinite;
}

.quiz__audio-progress {
  height: 4px;
  background: rgba(163, 42, 82, 0.1);
  border-radius: 4px;
  margin-top: 8px;
  overflow: hidden;
}

.quiz__audio-progress-bar {
  height: 100%;
  background: var(--secondary);
  border-radius: 4px;
  transition: width 0.1s linear;
}

.quiz__years-info {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.quiz__year-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #FFF4EF; 
  border-radius: 16px;
  border: 1px solid rgba(226, 88, 34, 0.2);
  font-size: 12px;
  box-shadow: 0 2px 8px rgba(226, 88, 34, 0.05);
}

.quiz__year-label {
  font-weight: 600;
  color: var(--text-muted);
}

.quiz__year-value {
  font-weight: 900;
  color: var(--primary);
}

.quiz__year-badge--enem {
  background: #FFFBEA; 
  border: 1px solid rgba(212, 175, 55, 0.3);
  box-shadow: 0 2px 8px rgba(212, 175, 55, 0.05);
}

.quiz__year-badge--enem .quiz__year-value {
  color: #B58500; 
}

/* 📖 LETRA DA MÚSICA */
.quiz__lyrics {
  padding: 32px 20px;
  background: #FFFAF0; 
  background-image: linear-gradient(135deg, #FFFAF0 0%, #FFF0D4 100%);
  border-radius: 20px;
  border: 1px solid rgba(226, 88, 34, 0.15);
  border-left: 6px solid var(--secondary); 
  position: relative;
  text-align: center;
  /* Margem reduzida para dar espaço aos créditos logo abaixo */
  margin-bottom: 8px; 
  box-shadow: 
    inset 2px 2px 5px rgba(255, 255, 255, 0.9),
    0 6px 15px rgba(163, 42, 82, 0.05); 
}

.quiz__quote-icon {
  font-size: 28px;
  color: rgba(226, 88, 34, 0.25);
  margin: 0 auto 16px auto;
  display: block;
}

.quiz__lyrics-text {
  font-size: 20px; 
  line-height: 1.7;
  color: #1a1412; 
  font-style: italic;
  font-weight: 600; 
  letter-spacing: 0.3px;
}

.quiz__lyrics-text p {
  margin: 10px 0;
}

/* 📝 CRÉDITOS DA MÚSICA (Totalmente colado à direita) */
.quiz__credits {
  display: flex;
  justify-content: flex-end; /* Alinha flexível à direita */
  padding: 0; /* Removido o padding lateral para encostar no card */
  margin-top: -6px; /* Puxa um pouco para ficar juntinho da letra */
  margin-bottom: 24px;
  position: relative;
  z-index: 2;
}

.quiz__credits-pill {
  font-size: 12px;
  font-style: italic;
  color: var(--text-muted);
  background: rgba(255, 250, 240, 0.85); 
  backdrop-filter: blur(4px);
  padding: 6px 14px;
  border-radius: 16px;
  border: 1px solid rgba(226, 88, 34, 0.15);
  box-shadow: 0 4px 10px rgba(163, 42, 82, 0.05);
  line-height: 1.5;
  max-width: 80%;
  text-align: right;
}

/* 🎯 ENUNCIADO */
.quiz__statement {
  padding: 24px;
  background: #F9F6F5; 
  border-radius: 20px;
  border-left: 6px solid var(--primary);
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  margin-bottom: 24px;
}

.quiz__statement-text {
  font-size: 20px; 
  line-height: 1.7;
  color: #1a1412; 
  font-weight: 600;
  margin: 0;
}

/* 🎯 ALTERNATIVAS */
.quiz__options {
  display: flex;
  flex-direction: column;
  gap: 16px; 
}

.quiz__options :deep(button),
.quiz__options :deep(.option-content) {
  font-size: 18px !important;
  line-height: 1.5 !important;
  color: #1a1412 !important;
  font-weight: 600 !important;
}

/* Ações / Botões */
.btn-premium {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
  border: none !important;
  border-radius: 16px !important;
  font-weight: 800 !important;
  font-size: 16px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 20px rgba(163, 42, 82, 0.2) !important;
  transition: all 0.3s ease !important;
}

.btn-premium:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(163, 42, 82, 0.3) !important;
}

.btn-turquesa {
  background: linear-gradient(135deg, #2ACEA4 0%, #179B78 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 16px !important;
  font-weight: 800 !important;
  font-size: 16px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 8px 20px rgba(42, 206, 164, 0.25) !important;
  transition: all 0.3s ease !important;
}

.btn-turquesa:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(42, 206, 164, 0.35) !important;
}

.btn-ghost-orange {
  background: #FFF0E6 !important; 
  border: 2px solid rgba(226, 88, 34, 0.2) !important;
  color: var(--secondary) !important; 
  border-radius: 16px !important;
  font-weight: 800 !important;
  font-size: 15px !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease !important;
}

.btn-ghost-orange:hover {
  background: #FFE4D6 !important; 
  border-color: rgba(226, 88, 34, 0.4) !important;
  transform: translateY(-1px);
}

.quiz__actions, .quiz__skip-action {
  margin-top: 24px;
}

/* Feedback Premium */
.quiz__feedback {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px dashed var(--border-light);
  animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.quiz__feedback-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-radius: 20px;
  margin-bottom: 16px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.04);
}

.quiz__feedback--correct {
  background: var(--success-bg);
  border: 1px solid rgba(46, 125, 50, 0.2);
}

.quiz__feedback--wrong {
  background: var(--error-bg);
  border: 1px solid rgba(198, 40, 40, 0.2);
}

.quiz__feedback-icon {
  font-size: 32px;
  margin-top: 2px;
}

.quiz__feedback--correct .quiz__feedback-icon { color: var(--success); }
.quiz__feedback--wrong .quiz__feedback-icon { color: var(--error); }

.quiz__feedback-text strong {
  display: block;
  font-size: 18px;
  margin-bottom: 4px;
  color: var(--text-main);
}

.quiz__points-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 6px 12px;
  background: var(--gold);
  color: #fff;
  border-radius: 12px;
  font-weight: 800;
  font-size: 13px;
  box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3);
}

.star-icon {
  color: #fff;
  animation: spin 3s linear infinite;
}

/* Sections Extras */
.quiz__comment-section, .quiz__curiosity-section {
  padding: 20px;
  border-radius: 20px;
  margin-bottom: 16px;
  background: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.02);
  border: 1px solid var(--border-light);
}

.quiz__comment-header, .quiz__curiosity-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.icon-wrapper, .icon-wrapper-gold {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.icon-wrapper { background: rgba(163, 42, 82, 0.1); color: var(--primary); }
.icon-wrapper-gold { background: rgba(212, 175, 55, 0.1); color: var(--gold); }

.quiz__comment-title, .quiz__curiosity-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
}

.quiz__comment-content, .quiz__curiosity-content {
  font-size: 16px; 
  line-height: 1.6;
  color: #1a1412;
}

/* Loading e Empty States Premium */
.quiz__loading, .quiz__error, .quiz__empty, .quiz__empty-filter {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  min-height: 400px;
}

.quiz__loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(163, 42, 82, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
}

.quiz__empty-filter-icon {
  font-size: 64px;
  color: var(--text-muted);
  opacity: 0.3;
  margin-bottom: 24px;
}

.quiz__empty-filter-icon.gold-icon {
  color: var(--gold);
  opacity: 1;
  filter: drop-shadow(0 4px 10px rgba(212, 175, 55, 0.3));
}

.quiz__empty-title {
  font-size: 22px;
  color: var(--primary);
  font-weight: 900;
}

@keyframes spin { 100% { transform: rotate(360deg); } }
@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (min-width: 768px) {
  .quiz { padding: 32px; }
  .quiz__container { max-width: 800px; }
  :deep(.quiz__card) { padding: 32px 40px; }
  .quiz__title { font-size: 26px; }
  
  .quiz__audio-title { font-size: 24px; }
  
  .quiz__lyrics { padding: 40px 32px; }
  .quiz__lyrics-text { font-size: 24px; }
  .quiz__lyrics-text p { margin: 12px 0; }
  
  /* Créditos no desktop também aumentam de leve */
  .quiz__credits-pill { font-size: 14px; padding: 8px 18px; }

  .quiz__statement { padding: 32px; }
  .quiz__statement-text { font-size: 24px; } 
  
  .quiz__options :deep(button),
  .quiz__options :deep(.option-content) { font-size: 20px !important; }
  
  .quiz__audio-section { padding: 20px 24px; }
  .quiz__play-btn { width: 70px; height: 70px; }
  .quiz__play-icon { font-size: 26px; }
}
</style>
