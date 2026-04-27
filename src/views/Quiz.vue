<template>
  <div class="quiz">
    <div class="quiz__container animate-fade-down">
      <Card variant="elevated" class="quiz__card">
        <div v-if="loading" class="quiz__loading">
          <div class="quiz__loading-spinner"></div>
          <p>Preparando a arena...</p>
        </div>

        <div v-else-if="error" class="quiz__error">
          <font-awesome-icon icon="exclamation-triangle" class="quiz__error-icon" />
          <p>{{ error }}</p>
          <Button variant="primary" @click="loadQuestions(true)">Tentar Novamente</Button>
        </div>

        <div v-else-if="allQuestions.length === 0" class="quiz__empty">
          <font-awesome-icon icon="inbox" class="quiz__empty-icon" />
          <p>Nenhuma missão disponível aqui.</p>
          <p class="quiz__empty-hint">Aguardando o Diretor adicionar questões na base.</p>
          <Button variant="primary" @click="goToHome">Voltar ao Camarim</Button>
        </div>

        <template v-else-if="currentQuestion">
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

          <div class="quiz__progress-container animate-slide-up" style="animation-delay: 0.1s;">
            <div class="quiz__progress-header">
              <span class="quiz__progress-text">Questão {{ currentQuestionIndex + 1 }} de {{ allQuestions.length }}</span>
              <span class="quiz__progress-percentage">{{ porcentagemProgresso }}%</span>
            </div>
            <div class="quiz__progress-bar-bg">
              <div class="quiz__progress-bar-fill" :style="{ width: porcentagemProgresso + '%' }"></div>
            </div>
          </div>

          <div class="quiz__content animate-slide-up" style="animation-delay: 0.2s;">
            <div class="quiz__music-info">
              <div class="quiz__audio-section">
                <button
                  class="quiz__play-btn"
                  @click="playYoutube"
                  :class="{ 'quiz__play-btn--playing': isPlaying }"
                  :disabled="!youtubeVideoId || isPlaying"
                >
                  <font-awesome-icon
                    :icon="isPlaying ? 'music' : 'play'"
                    class="quiz__play-icon"
                    :class="{ 'fa-beat': isPlaying }"
                  />
                </button>

                <div class="quiz__audio-info">
                  <div class="quiz__audio-title">
                    {{ currentQuestion.autor }} - {{ currentQuestion.titulo }}
                  </div>

                  <span v-if="isPlaying" class="quiz__playing-text">
                    Tocando agora...
                  </span>

                  <div class="quiz__audio-progress" v-if="isPlaying && audioDuration > 0">
                    <div class="quiz__audio-progress-bar" :style="{ width: `${audioProgress}%` }"></div>
                  </div>

                  <iframe
                    ref="youtubeIframe"
                    v-show="youtubeVideoId"
                    :src="youtubeUrl"
                    allow="autoplay; encrypted-media"
                    style="width: 200px; height: 150px; opacity: 0.01; position: absolute; top: 0; left: 0; pointer-events: none;"
                  ></iframe>
                </div>
              </div>

              <div class="quiz__years-info" v-if="currentQuestion.ano_lancamento || currentQuestion.ano_prova">
                <div class="quiz__year-badge" v-if="currentQuestion.ano_lancamento">
                  <font-awesome-icon icon="calendar-alt" />
                  <span class="quiz__year-label">Lançamento:</span>
                  <span class="quiz__year-value">{{ currentQuestion.ano_lancamento }}</span>
                </div>

                <div class="quiz__year-badge quiz__year-badge--enem" v-if="currentQuestion.ano_prova">
                  <font-awesome-icon icon="graduation-cap" />
                  <span class="quiz__year-label">Prova:</span>
                  <span class="quiz__year-value">{{ currentQuestion.ano_prova }}</span>
                </div>
              </div>
            </div>

            <div class="quiz__lyrics" v-if="currentQuestion.trecho_letra">
              <font-awesome-icon icon="quote-left" class="quiz__quote-icon" />
              <div class="quiz__lyrics-text">
                <p v-for="(line, index) in lyricsLines" :key="index">{{ line }}</p>
              </div>
            </div>

            <div class="quiz__credits animate-slide-up" v-if="currentQuestion.creditos">
              <div class="quiz__credits-pill">
                {{ currentQuestion.creditos }}
              </div>
            </div>

            <div class="quiz__statement" v-if="currentQuestion.enunciado">
              <p class="quiz__statement-text">{{ currentQuestion.enunciado }}</p>
            </div>

            <div class="quiz__options">
              <OptionButton
                v-for="(option, index) in questionOptions"
                :key="option.label"
                :label="option.label"
                :selected="selectedOption === index"
                @click="selectOption(index)"
                :disabled="answered || isChecking || limiteDiarioAtingido"
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
              class="btn-turquesa"
              :disabled="isChecking"
            >
              {{ isChecking ? 'Conferindo a partitura... 🎼' : 'Confirmar Resposta' }}
            </Button>
          </div>

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
            <div
              v-if="limiteDiarioAtingido"
              class="quiz__already-answered-warning"
              style="background-color: #FFF3CD; color: #856404; border: 1px solid #FFEEBA; margin-bottom: 16px;"
            >
              <font-awesome-icon icon="lock" class="quiz__warning-icon" />
              <p>
                <strong>Missão do dia concluída! 🛑</strong><br>
                Siga para o <strong>Estúdio</strong> para continuar sua experiência. Volte amanhã para novos shows!
              </p>
            </div>

            <div v-if="alreadyAnswered && !limiteDiarioAtingido" class="quiz__already-answered-warning">
              <font-awesome-icon icon="info-circle" class="quiz__warning-icon" />
              <p>
                <strong>Modo Revisão Ativo (Estúdio)</strong><br>
                Sua resposta original foi <strong>{{ previousResult ? 'correta' : 'incorreta' }}</strong>.
                Esta tentativa serve para você treinar e consolidar seu repertório.
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

            <div class="quiz__comment-section" v-if="isCorrect && currentQuestion.comentario">
              <div class="quiz__comment-header">
                <div class="icon-wrapper">
                  <font-awesome-icon icon="key" class="quiz__comment-icon" />
                </div>
                <h3 class="quiz__comment-title">Chave da Questão</h3>
              </div>
              <div class="quiz__comment-content">
                <p>{{ currentQuestion.comentario }}</p>
              </div>
            </div>

            <div class="quiz__curiosity-section" v-if="isCorrect && currentQuestion.curiosidade">
              <div class="quiz__curiosity-header">
                <div class="icon-wrapper-gold">
                  <font-awesome-icon icon="lightbulb" class="quiz__curiosity-icon" />
                </div>
                <h3 class="quiz__curiosity-title">Você Sabia?</h3>
              </div>
              <div class="quiz__curiosity-content">
                <p>{{ currentQuestion.curiosidade }}</p>
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
                :disabled="isFinishing"
              >
                {{ isFinishing ? 'Salvando...' : 'Finalizar Desafio' }}
                <font-awesome-icon icon="flag-checkered" v-if="!isFinishing" />
              </Button>
            </div>
          </div>
        </template>
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
import { api, type DailyQuestionResponse, type CheckAnswerResponse } from '@/services/api'
import { useQuizStore } from '@/stores/quiz'
import { useAuthStore } from '@/stores/auth'

type ApiQuestion = {
  id: number
  titulo: string
  autor: string
  musica_url: string
  ano_lancamento?: number | null
  ano_prova?: number | null
  trecho_letra?: string | null
  enunciado: string
  a?: string | null
  b?: string | null
  c?: string | null
  d?: string | null
  e?: string | null
  alternativa_correta?: string | null
  comentario?: string | null
  curiosidade?: string | null
  creditos?: string | null
  matriz_enem?: string | null
  prova?: string | null
  disciplina?: string | null
  already_answered?: boolean
  previous_result?: boolean | null
  previous_answer?: string | null
}

const router = useRouter()
const route = useRoute()
const quizStore = useQuizStore()
const authStore = useAuthStore()

const category = computed(() => (route.params.prova as string) || 'enem')

const categoryNames: Record<string, string> = {
  enem: 'Missão ENEM',
  fuvest: 'Missão FUVEST',
  unicamp: 'Missão UNICAMP',
  outros: 'Treino Livre',
  foco: 'Da Terra à Lua'
}

const categoryName = computed(() => categoryNames[category.value] || 'Desafio Diário')

const loading = ref(true)
const error = ref<string | null>(null)
const allQuestions = ref<ApiQuestion[]>([])
const currentQuestionIndex = ref(0)
const selectedOption = ref<number | null>(null)
const answered = ref(false)
const isCorrect = ref(false)
const correctAnswer = ref('')
const isFinishing = ref(false)
const isChecking = ref(false)
const limiteDiarioAtingido = ref(false)

const isPlaying = ref(false)
const youtubeIframe = ref<HTMLIFrameElement | null>(null)
const audioProgress = ref(0)
const audioDuration = ref(0)
let progressInterval: ReturnType<typeof setInterval> | null = null

const alreadyAnswered = ref(false)
const previousResult = ref<boolean | null>(null)
const pointsEarned = ref(false)
const pointsValue = ref(0)
const sessionScore = ref(0)
const displayedQuestion = ref<ApiQuestion | null>(null)
const partidaId = ref<number | null>(null)

const currentQuestion = computed(() => {
  if (allQuestions.value.length === 0) return null

  const index = Math.min(currentQuestionIndex.value, allQuestions.value.length - 1)
  const question = allQuestions.value[index] || null

  if (answered.value && displayedQuestion.value) {
    return displayedQuestion.value
  }

  return question
})

const porcentagemProgresso = computed(() => {
  if (allQuestions.value.length === 0) return 0
  return Math.round(((currentQuestionIndex.value + 1) / allQuestions.value.length) * 100)
})

const hasNextQuestion = computed(() => currentQuestionIndex.value < allQuestions.value.length - 1)

const lyricsLines = computed(() => {
  if (!currentQuestion.value?.trecho_letra) return []
  return currentQuestion.value.trecho_letra
    .split('\n')
    .filter((line: string) => line.trim())
})

const questionOptions = computed(() => {
  if (!currentQuestion.value) return []

  const q = currentQuestion.value
  const options = [
    { label: 'A', text: q.a || '', isCorrect: false },
    { label: 'B', text: q.b || '', isCorrect: false },
    { label: 'C', text: q.c || '', isCorrect: false },
    { label: 'D', text: q.d || '', isCorrect: false },
    { label: 'E', text: q.e || '', isCorrect: false }
  ].filter((opt) => opt.text !== '')

  if (answered.value && correctAnswer.value) {
    return options.map((opt) => ({
      ...opt,
      isCorrect: opt.label === correctAnswer.value
    }))
  }

  return options
})

const youtubeVideoId = computed(() => {
  const rawData = currentQuestion.value?.musica_url
  if (!rawData) return null

  const firstPart = rawData.split(',')[0].trim()

  if (firstPart.includes('youtu')) {
    const regExp = /^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/
    const match = firstPart.match(regExp)
    return match && match[2].length === 11 ? match[2] : null
  }

  return firstPart.length === 11 ? firstPart : null
})

const youtubeStartTime = computed(() => {
  const rawData = currentQuestion.value?.musica_url
  if (!rawData) return ''
  const parts = rawData.split(',')
  return parts[1] ? parts[1].trim() : ''
})

const youtubeEndTime = computed(() => {
  const rawData = currentQuestion.value?.musica_url
  if (!rawData) return ''
  const parts = rawData.split(',')
  return parts[2] ? parts[2].trim() : ''
})

const youtubeUrl = computed(() => {
  if (!youtubeVideoId.value) return 'about:blank'
  return `https://www.youtube.com/embed/${youtubeVideoId.value}?enablejsapi=1&controls=0&playsinline=1&start=${youtubeStartTime.value}&end=${youtubeEndTime.value}`
})

function mapQuestion(q: any): ApiQuestion {
  return {
    id: q.id,
    titulo: q.titulo,
    autor: q.autor,
    musica_url: q.musica_url,
    ano_lancamento: q.ano_lancamento,
    ano_prova: q.ano_prova,
    trecho_letra: q.trecho_letra,
    enunciado: q.enunciado,
    a: q.a,
    b: q.b,
    c: q.c,
    d: q.d,
    e: q.e,
    alternativa_correta: q.alternativa_correta,
    comentario: q.comentario,
    curiosidade: q.curiosidade,
    creditos: q.creditos,
    matriz_enem: q.matriz_enem,
    prova: q.prova,
    disciplina: q.disciplina,
    already_answered: q.already_answered,
    previous_result: q.previous_result,
    previous_answer: q.previous_answer
  }
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function scrollToBottom() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

function resetAudioState() {
  if (youtubeIframe.value && isPlaying.value) {
    youtubeIframe.value.contentWindow?.postMessage(
      JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }),
      '*'
    )
  }

  isPlaying.value = false
  audioProgress.value = 0
  audioDuration.value = 0

  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

function resetQuestionState() {
  selectedOption.value = null
  answered.value = false
  isCorrect.value = false
  correctAnswer.value = ''
  limiteDiarioAtingido.value = false
  alreadyAnswered.value = false
  previousResult.value = null
  pointsEarned.value = false
  pointsValue.value = 0
  displayedQuestion.value = null

  resetAudioState()

  const question = allQuestions.value[currentQuestionIndex.value]
  if (question?.already_answered) {
    alreadyAnswered.value = true
    previousResult.value = question.previous_result ?? null
  }
}

function syncAuthScore(totalScore: number | null | undefined) {
  if (typeof totalScore !== 'number' || !authStore.user) return
  authStore.user.pontuacao = Math.max(0, Number(totalScore))
}

async function syncProfileSafely() {
  try {
    await authStore.fetchUserProfile()
  } catch (err) {
    console.error('[QUIZ] Falha ao sincronizar perfil:', err)
  }
}

async function loadQuestions(forceRefresh = false) {
  loading.value = true
  error.value = null
  sessionScore.value = 0
  partidaId.value = null

  try {
    if (forceRefresh) {
      await new Promise((resolve) => setTimeout(resolve, 300))
    }

    const data = await api.daily.getQuestions() as DailyQuestionResponse

    if (data?.status === 'vazio') {
      allQuestions.value = []
      error.value = data.mensagem || 'Nenhuma missão disponível no momento.'
      return
    }

    if (data?.status === 'sucesso' && Array.isArray(data.questoes) && data.questoes.length > 0) {
      partidaId.value = typeof data.partida_id === 'number' ? data.partida_id : null
      allQuestions.value = data.questoes.map(mapQuestion)
      currentQuestionIndex.value = 0
      resetQuestionState()

      if (quizStore.iniciarPartida) {
        quizStore.iniciarPartida()
      }

      return
    }

    allQuestions.value = []
    error.value = 'Nenhuma questão encontrada no momento.'
  } catch (err: any) {
    console.error('[QUIZ] Erro em loadQuestions:', err)
    error.value = err.message || 'Erro ao carregar missão do dia.'
  } finally {
    loading.value = false
  }
}

function playYoutube() {
  if (!youtubeVideoId.value || !youtubeIframe.value) return

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

    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }

    setTimeout(() => {
      if (!isPlaying.value) return

      progressInterval = setInterval(() => {
        audioProgress.value += step

        if (audioProgress.value >= 100) {
          audioProgress.value = 100
          isPlaying.value = false

          youtubeIframe.value?.contentWindow?.postMessage(
            JSON.stringify({ event: 'command', func: 'pauseVideo', args: [] }),
            '*'
          )

          if (progressInterval) {
            clearInterval(progressInterval)
            progressInterval = null
          }
        }
      }, intervalMs)
    }, 1000)
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

  const interval = setInterval(() => {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      clearInterval(interval)
      return
    }

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
  if (!answered.value && !isChecking.value && !limiteDiarioAtingido.value) {
    selectedOption.value = index
  }
}

async function confirmAnswer() {
  if (selectedOption.value === null || !currentQuestion.value || isChecking.value) return

  isChecking.value = true
  error.value = null

  const selectedLabel = questionOptions.value[selectedOption.value]?.label
  if (!selectedLabel) {
    isChecking.value = false
    error.value = 'Alternativa inválida.'
    return
  }

  try {
    const data = await api.questions.checkAnswerDetailed(currentQuestion.value.id, {
      partida_id: partidaId.value,
      alternativa_selecionada: selectedLabel,
      time_spent: 15
    }) as CheckAnswerResponse

    displayedQuestion.value = currentQuestion.value ? { ...currentQuestion.value } : null
    answered.value = true

    if (data?.limit_reached) {
      limiteDiarioAtingido.value = true
      isCorrect.value = false

      correctAnswer.value =
        data.correct_answer ||
        (currentQuestion.value.alternativa_correta
          ? String(currentQuestion.value.alternativa_correta).toUpperCase()
          : '')

      alreadyAnswered.value = false
      previousResult.value = null
      pointsEarned.value = false
      pointsValue.value = 0

      if (typeof data.partida_id === 'number') {
        partidaId.value = data.partida_id
      }

      await syncProfileSafely()

      setTimeout(() => {
        scrollToBottom()
      }, 300)

      return
    }

    isCorrect.value = !!data?.is_correct

    correctAnswer.value =
      data?.correct_answer ||
      (currentQuestion.value.alternativa_correta
        ? String(currentQuestion.value.alternativa_correta).toUpperCase()
        : '')

    limiteDiarioAtingido.value = !!data?.limite_diario_atingido

    if (typeof data?.partida_id === 'number') {
      partidaId.value = data.partida_id
    }

    if (quizStore.registrarResposta) {
      quizStore.registrarResposta(
        isCorrect.value,
        currentQuestion.value.matriz_enem || ''
      )
    }

    alreadyAnswered.value = !!data?.already_answered
    previousResult.value = typeof data?.previous_result === 'boolean' ? data.previous_result : null
    pointsEarned.value = !!data?.points_earned
    pointsValue.value = Number(data?.points ?? 0)

    // ====================================================================
    // 🛠️ MODO DEV: ALIMENTANDO AS PASTAS DO ESTÚDIO AUTOMATICAMENTE!
    // Se não for modo revisão e for uma jogada válida, salva no Estúdio
    // ====================================================================
    if (!alreadyAnswered.value && !limiteDiarioAtingido.value) {
      if (isCorrect.value) {
        const atualBis = Number(localStorage.getItem('dev_bis_count')) || 0
        localStorage.setItem('dev_bis_count', (atualBis + 1).toString())
      } else {
        const atualRiscado = Number(localStorage.getItem('dev_riscado_count')) || 0
        localStorage.setItem('dev_riscado_count', (atualRiscado + 1).toString())
      }
    }

    if (typeof data?.total_score === 'number') {
      syncAuthScore(data.total_score)
    } else if (authStore.user) {
      authStore.user.pontuacao = Math.max(
        0,
        Number(authStore.user.pontuacao ?? 0) + pointsValue.value
      )
    }

    sessionScore.value = Math.max(0, sessionScore.value + pointsValue.value)

    await syncProfileSafely()

    if (isCorrect.value && pointsEarned.value) {
      setTimeout(() => {
        triggerConfetti()
      }, 300)
    }

    setTimeout(() => {
      scrollToBottom()
    }, 300)
  } catch (err: any) {
    console.error('[QUIZ] Erro em confirmAnswer:', err)
    error.value = err.message || 'Cabo desconectado! Plugue novamente!'
  } finally {
    isChecking.value = false
  }
}

function nextQuestion() {
  if (!hasNextQuestion.value) return

  currentQuestionIndex.value++
  resetQuestionState()
  scrollToTop()
}

async function finishQuiz() {
  if (isFinishing.value) return

  isFinishing.value = true

  try {
    if (quizStore.finalizarPartida) {
      quizStore.finalizarPartida(sessionScore.value)
    }

    await syncProfileSafely()
  } catch (err) {
    console.error('[QUIZ] Erro ao atualizar perfil do jogador:', err)
  } finally {
    isFinishing.value = false
  }

  router.push({
    path: '/missao-cumprida',
    query: { pontos: sessionScore.value }
  })
}

function goToHome() {
  router.push('/')
}

onMounted(() => {
  loadQuestions(true)
})

onUnmounted(() => {
  resetAudioState()
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

.quiz__lyrics {
  padding: 32px 20px;
  background: #FFFAF0; 
  background-image: linear-gradient(135deg, #FFFAF0 0%, #FFF0D4 100%);
  border-radius: 20px;
  border: 1px solid rgba(226, 88, 34, 0.15);
  border-left: 6px solid var(--secondary); 
  position: relative;
  text-align: center;
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

.quiz__credits {
  display: flex;
  justify-content: flex-end; 
  padding: 0; 
  margin-top: -6px; 
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

.quiz__actions,
.quiz__skip-action {
  margin-top: 24px;
}

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

.quiz__comment-section,
.quiz__curiosity-section {
  padding: 20px;
  border-radius: 20px;
  margin-bottom: 16px;
  background: #fff;
  box-shadow: 0 4px 15px rgba(0,0,0,0.02);
  border: 1px solid var(--border-light);
}

.quiz__comment-header,
.quiz__curiosity-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.icon-wrapper,
.icon-wrapper-gold {
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

.quiz__comment-title,
.quiz__curiosity-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--text-main);
  margin: 0;
}

.quiz__comment-content,
.quiz__curiosity-content {
  font-size: 16px; 
  line-height: 1.6;
  color: #1a1412;
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
  width: 50px;
  height: 50px;
  border: 4px solid rgba(163, 42, 82, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
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

  .quiz__credits-pill { font-size: 14px; padding: 8px 18px; }

  .quiz__statement { padding: 32px; }
  .quiz__statement-text { font-size: 24px; }

  .quiz__options :deep(button),
  .quiz__options :deep(.option-content) {
    font-size: 20px !important;
  }

  .quiz__audio-section { padding: 20px 24px; }
  .quiz__play-btn { width: 70px; height: 70px; }
  .quiz__play-icon { font-size: 26px; }
}
</style>
