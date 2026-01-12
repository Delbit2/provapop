import { defineStore } from 'pinia'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    score: 0,
    currentQuestion: 0
  }),
  actions: {
    incrementScore() {
      this.score++
    },
    nextQuestion() {
      this.currentQuestion++
    },
    reset() {
      this.score = 0
      this.currentQuestion = 0
    }
  }
})

