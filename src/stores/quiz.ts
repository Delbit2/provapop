import { defineStore } from 'pinia'

type RespostaQuiz = {
  questao_id?: number | string
  correta: boolean
  matriz_enem?: string
  alternativa_selecionada?: string
  pontos_ganhos?: number
  respondida_em?: number
  ja_respondida?: boolean
}

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    totalPontos: 0,
    respostas: [] as RespostaQuiz[],
    tempoInicio: null as number | null,
    tempoFim: null as number | null,
    partidaId: null as number | string | null,
    categoria: null as string | null,
    totalQuestoes: 0,
    totalPuladas: 0,
  }),

  getters: {
    getTempoDecorridoSegundos(state): number {
      if (!state.tempoInicio) return 0

      const tempoFinal = state.tempoFim ?? Date.now()
      return Math.max(0, Math.floor((tempoFinal - state.tempoInicio) / 1000))
    },

    getAcertos(state): number {
      return state.respostas.filter((r) => r.correta).length
    },

    getTotalRespondidas(state): number {
      return state.respostas.length
    },

    getErros(state): number {
      return state.respostas.filter((r) => !r.correta).length
    },

    getTaxaAcerto(): number {
      if (this.getTotalRespondidas === 0) return 0
      return Math.round((this.getAcertos / this.getTotalRespondidas) * 100)
    },

    getQuestoesRestantes(state): number {
      return Math.max(0, state.totalQuestoes - state.respostas.length - state.totalPuladas)
    },

    partidaFinalizada(state): boolean {
      return state.tempoFim !== null
    },
  },

  actions: {
    reset() {
      this.totalPontos = 0
      this.respostas = []
      this.tempoInicio = null
      this.tempoFim = null
      this.partidaId = null
      this.categoria = null
      this.totalQuestoes = 0
      this.totalPuladas = 0
    },

    iniciarPartida(payload?: {
      partidaId?: number | string | null
      categoria?: string | null
      totalQuestoes?: number
    }) {
      this.reset()
      this.tempoInicio = Date.now()
      this.partidaId = payload?.partidaId ?? null
      this.categoria = payload?.categoria ?? null
      this.totalQuestoes = Math.max(0, Number(payload?.totalQuestoes ?? 0))
    },

    definirPartidaId(partidaId: number | string | null) {
      this.partidaId = partidaId
    },

    definirTotalQuestoes(total: number) {
      this.totalQuestoes = Math.max(0, Number(total || 0))
    },

    registrarResposta(payload: {
      correta: boolean
      matriz_enem?: string
      questao_id?: number | string
      alternativa_selecionada?: string
      pontos_ganhos?: number
      ja_respondida?: boolean
    }) {
      const novaResposta: RespostaQuiz = {
        correta: payload.correta,
        matriz_enem: payload.matriz_enem || '',
        questao_id: payload.questao_id,
        alternativa_selecionada: payload.alternativa_selecionada,
        pontos_ganhos: Math.max(0, Number(payload.pontos_ganhos ?? 0)),
        ja_respondida: !!payload.ja_respondida,
        respondida_em: Date.now(),
      }

      if (payload.questao_id !== undefined && payload.questao_id !== null) {
        const index = this.respostas.findIndex(
          (resposta) => resposta.questao_id === payload.questao_id
        )

        if (index !== -1) {
          this.respostas[index] = novaResposta
          return
        }
      }

      this.respostas.push(novaResposta)
    },

    registrarQuestaoPulada() {
      this.totalPuladas += 1
    },

    finalizarPartida(pontuacaoFinal?: number) {
      this.totalPontos = Math.max(0, Number(pontuacaoFinal ?? this.totalPontos ?? 0))
      this.tempoFim = Date.now()
    },
  },
})
