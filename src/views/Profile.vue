<template>
  <div class="profile">
    <div class="profile__container">
      <Transition name="fade" appear>
        <div class="profile__content">
          
          <!-- CABEÇALHO COMPRIMIDO -->
          <div class="profile__header">
            <div class="profile__header-content">
              <h1 class="profile__title">Meu Perfil</h1>
              <p class="profile__subtitle">Área VIP • Gerencie seus dados</p>
            </div>
          </div>

          <!-- CARD DE PERFIL -->
          <Card variant="elevated" class="profile__card">
            
            <div class="profile__avatar-section">
              <div class="profile__avatar">
                <img src="@/assets/avatar-default.png" alt="Avatar VIP" class="profile__avatar-img" />
              </div>
            </div>

            <div class="profile__info-section">
              <div class="profile__info-item">
                <font-awesome-icon icon="user" class="profile__info-icon"></font-awesome-icon>
                <div class="profile__info-content">
                  <div class="profile__info-label">Nome Artístico</div>
                  <div class="profile__info-value">{{ form.nickname || 'Carregando...' }}</div>
                </div>
              </div>
            </div>

            <div v-if="error" class="profile__message profile__message--error">
              <font-awesome-icon icon="exclamation-circle"></font-awesome-icon>
              {{ error }}
            </div>

            <div v-if="success" class="profile__message profile__message--success">
              <font-awesome-icon icon="check-circle"></font-awesome-icon>
              {{ success }}
            </div>

            <form @submit.prevent="handleSave" class="profile__form">
              <div class="profile__field">
                <label class="profile__label">
                  <font-awesome-icon icon="envelope" class="profile__label-icon"></font-awesome-icon>
                  E-mail
                </label>
                <input
                  v-model="form.email"
                  type="email"
                  class="profile__input"
                  placeholder="ex: futuro.calouro@email.com"
                  required
                />
              </div>

              <div class="profile__field">
                <label class="profile__label">
                  <font-awesome-icon icon="lock" class="profile__label-icon"></font-awesome-icon>
                  Nova Senha Secreta
                </label>
                <div class="profile__password-wrapper">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    class="profile__input"
                    placeholder="Deixe em branco p/ manter"
                    :minlength="6"
                  />
                  <button
                    type="button"
                    class="profile__toggle-password"
                    @click="showPassword = !showPassword"
                  >
                    <font-awesome-icon :icon="showPassword ? 'eye-slash' : 'eye'"></font-awesome-icon>
                  </button>
                </div>
              </div>

              <div class="profile__actions">
                <button
                  type="submit"
                  :disabled="loading || !hasChanges"
                  class="profile__save-btn"
                >
                  <font-awesome-icon v-if="loading" icon="circle-notch" class="profile__spinner"></font-awesome-icon>
                  {{ loading ? 'Afinando...' : 'Salvar' }}
                </button>
                <button
                  type="button"
                  @click="handleCancel"
                  :disabled="loading"
                  class="profile__cancel-btn"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </Card>

          <!-- PILHA DE BANNERS (O Hub de Promoções) -->
          <div class="profile__banners-wrapper">
            
            <!-- 1. Banner Monetização (E-book) -->
            <div class="promo-banner promo-banner--ebook animate-slide-up" style="animation-delay: 0.1s">
              <div class="promo-banner__content">
                <div class="promo-banner__icon" style="filter: grayscale(0.2);">📚</div>
                <div class="promo-banner__text">
                  <h3>E-book ProvaPop!</h3>
                  <span class="badge-available">JÁ DISPONÍVEL</span>
                </div>
              </div>
              <button type="button" class="promo-banner__btn promo-banner__btn--ebook" @click="router.push('/ebook')">
                Garantir 🚀
              </button>
            </div>

            <!-- 2. Banner Ingresso (Marketing Orgânico) -->
            <div class="promo-banner promo-banner--ticket animate-slide-up" style="animation-delay: 0.2s">
              <div class="promo-banner__content">
                <div class="promo-banner__icon">🎸</div>
                <div class="promo-banner__text">
                  <h3>Ingresso VIP</h3>
                  <p>Quem você levaria pro show?</p>
                </div>
              </div>
              <button type="button" class="promo-banner__btn promo-banner__btn--primary" @click="router.push('/ingresso')">
                <font-awesome-icon icon="ticket-alt" /> Compartilhar
              </button>
            </div>

            <!-- 3. Banner Apoio / Café (Comunidade) -->
            <div class="promo-banner promo-banner--coffee animate-slide-up" style="animation-delay: 0.3s">
              <div class="promo-banner__content">
                <div class="promo-banner__icon float">☕</div>
                <div class="promo-banner__text">
                  <h3>Apoie o Projeto</h3>
                  <p>Pague um café aos devs.</p>
                </div>
              </div>
              <button type="button" class="promo-banner__btn promo-banner__btn--accent" @click="handleSupport">
                Apoiar 
                <font-awesome-icon icon="heart" class="heart-icon" />
              </button>
            </div>

          </div>

          <!-- ÁREA DE SEGURANÇA: LOGOUT DISCRETO -->
          <div class="profile__logout-wrapper animate-slide-up" style="animation-delay: 0.4s">
            <button type="button" class="profile__logout-btn" @click="handleLogout">
              <font-awesome-icon icon="power-off"></font-awesome-icon>
              Desconectar deste dispositivo
            </button>
          </div>

          <!-- REDES SOCIAIS (ACOMPANHE OS BASTIDORES) -->
          <div class="profile__social-wrapper animate-slide-up" style="animation-delay: 0.5s">
            <p class="social-title">Acompanhe os bastidores</p>
            <div class="social-links">
              <!-- INSTAGRAM -->
              <a href="https://www.instagram.com/provapop/" target="_blank" class="social-btn social-btn--insta" title="Siga no Instagram">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" width="20" height="20"><path d="M224.1 141c-63.6 0-114.9 51.3-114.9 114.9s51.3 114.9 114.9 114.9S339 319.5 339 255.9 287.7 141 224.1 141zm0 189.6c-41.1 0-74.7-33.5-74.7-74.7s33.5-74.7 74.7-74.7 74.7 33.5 74.7 74.7-33.6 74.7-74.7 74.7zm146.4-194.3c0 14.9-12 26.8-26.8 26.8-14.9 0-26.8-12-26.8-26.8s12-26.8 26.8-26.8 26.8 12 26.8 26.8zm76.1 27.2c-1.7-35.9-9.9-67.7-36.2-93.9-26.2-26.2-58-34.4-93.9-36.2-37-2.1-147.9-2.1-184.9 0-35.8 1.7-67.6 9.9-93.9 36.1s-34.4 58-36.2 93.9c-2.1 37-2.1 147.9 0 184.9 1.7 35.9 9.9 67.7 36.2 93.9s58 34.4 93.9 36.2c37 2.1 147.9 2.1 184.9 0 35.9-1.7 67.7-9.9 93.9-36.2 26.2-26.2 34.4-58 36.2-93.9 2.1-37 2.1-147.8 0-184.8zM398.8 388c-7.8 19.6-22.9 34.7-42.6 42.6-29.5 11.7-99.5 9-132.1 9s-102.7 2.6-132.1-9c-19.6-7.8-34.7-22.9-42.6-42.6-11.7-29.5-9-99.5-9-132.1s-2.6-102.7 9-132.1c7.8-19.6 22.9-34.7 42.6-42.6 29.5-11.7 99.5-9 132.1-9s102.7-2.6 132.1 9c19.6 7.8 34.7 22.9 42.6 42.6 11.7 29.5 9 99.5 9 132.1s2.7 102.7-9 132.1z"/></svg>
              </a>
              <!-- YOUTUBE (Acervo de Músicas) -->
              <a href="https://www.youtube.com/@provapop" target="_blank" class="social-btn social-btn--youtube" title="Acervo Musical Oficial">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" fill="currentColor" width="22" height="22"><path d="M549.655 124.083c-6.281-23.65-24.787-42.276-48.284-48.597C458.781 64 288 64 288 64S117.22 64 74.629 75.486c-23.497 6.322-42.003 24.947-48.284 48.597-11.412 42.867-11.412 132.305-11.412 132.305s0 89.438 11.412 132.305c6.281 23.65 24.787 41.5 48.284 47.821C117.22 448 288 448 288 448s170.78 0 213.371-11.486c23.497-6.321 42.003-24.171 48.284-47.821 11.412-42.867 11.412-132.305 11.412-132.305s0-89.438-11.412-132.305zm-317.51 213.508V175.185l142.739 81.205-142.739 81.201z"/></svg>
              </a>
            </div>
          </div>

        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
// @ts-nocheck
import { ref, computed, onMounted } from 'vue'
// ... resto do código continua normal
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  nickname: '',
  email: '',
  password: ''
})

const originalForm = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const showPassword = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

const hasChanges = computed(() => {
  return form.value.email !== originalForm.value.email ||
         (form.value.password !== '' && form.value.password.length >= 6)
})

async function loadUserData() {
  loading.value = true
  error.value = null
  
  try {
    const userData = await api.auth.me()
    if (userData.user) {
      form.value.nickname = userData.user.nickname || userData.user.nome || userData.user.name || userData.user.username || ''
      form.value.email = userData.user.email || ''
      originalForm.value.email = userData.user.email || ''
      
      authStore.user = userData.user
    }
  } catch (err: any) {
    if (!err.message?.includes('Sessão expirada') && 
        !err.message?.includes('Acesso negado') &&
        !err.message?.includes('Erro de conexão')) {
      error.value = err.message || 'Erro ao carregar dados do usuário'
    }
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  loading.value = true
  error.value = null
  success.value = null
  
  try {
    const updateData: { email?: string; password?: string } = {}
    
    if (form.value.email !== originalForm.value.email) {
      updateData.email = form.value.email
    }
    
    if (form.value.password && form.value.password.length >= 6) {
      updateData.password = form.value.password
    }
    
    if (Object.keys(updateData).length === 0) {
      error.value = 'Nenhuma alteração para salvar'
      loading.value = false
      return
    }
    
    const response = await api.users.updateProfile(updateData)
    
    if (response.user) {
      originalForm.value.email = response.user.email || form.value.email
      form.value.email = response.user.email || form.value.email
      form.value.password = ''
      
      authStore.user = response.user
      success.value = 'Conta VIP atualizada com sucesso!'
      
      setTimeout(() => {
        success.value = null
      }, 3000)
    }
  } catch (err: any) {
    error.value = err.message || 'Erro ao atualizar perfil'
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  form.value.email = originalForm.value.email
  form.value.password = ''
  error.value = null
  success.value = null
}

function handleSupport() {
  alert('Que demais! 🧡 Em breve lançaremos nossa campanha de financiamento coletivo. Guarde esse café para nós! ☕')
}

async function handleLogout() {
  const confirmed = confirm('Tem certeza que deseja desconectar deste dispositivo?')
  if (confirmed) {
    try {
      if (typeof authStore.logout === 'function') {
        await authStore.logout()
      } else {
        authStore.user = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
      router.push('/login')
    } catch (err) {
      console.error('Erro ao fazer logout:', err)
      localStorage.clear()
      router.push('/login')
    }
  }
}

onMounted(async () => {
  if (authStore.user) {
    form.value.nickname = authStore.user.nickname || authStore.user.nome || authStore.user.name || authStore.user.username || ''
    form.value.email = authStore.user.email || ''
    originalForm.value.email = authStore.user.email || ''
  }
  
  await loadUserData()
})
</script>

<style scoped>
/* =========================================
   ESTRUTURA PRINCIPAL
   ========================================= */
.profile {
  min-height: 100dvh; 
  padding: max(2vh, 16px) 20px 120px 20px; 
  background-color: #ffffff;
  background-image: linear-gradient(180deg, #ffffff 0%, #ffffff 40%, #fcf2ee 70%, #ebd2cb 100%);
  display: flex;
  flex-direction: column;
}

.profile__container {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  z-index: 10;
  position: relative;
  flex-grow: 1; 
  display: flex;
  flex-direction: column;
}

.profile__content {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  gap: 16px; 
}

/* =========================================
   CABEÇALHO
   ========================================= */
.profile__header {
  text-align: center;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile__title {
  font-size: 28px;
  font-weight: 900;
  color: #8B1E3F;
  margin: 0 0 2px 0;
  letter-spacing: -0.5px;
}

.profile__subtitle {
  font-size: 13px;
  font-weight: 600;
  color: #5a4a46;
  margin: 0;
}

/* =========================================
   CARD DE PERFIL
   ========================================= */
.profile__card {
  padding: 16px 20px 20px 20px; 
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(226, 88, 34, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
}

.profile__avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 16px; 
  position: relative;
}

.profile__avatar {
  width: 80px; 
  height: 80px;
  border-radius: 50%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px rgba(226, 88, 34, 0.2);
  border: 3px solid #ffffff;
  overflow: hidden; 
}

.profile__avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile__info-section {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #fdfaf9;
  border-radius: 14px;
  border: 1px solid #e8dedc;
}

.profile__info-item {
  display: flex;
  align-items: center;
  gap: 14px;
}

.profile__info-icon {
  font-size: 20px;
  color: #E25822;
  flex-shrink: 0;
}

.profile__info-content {
  flex: 1;
  min-width: 0;
}

.profile__info-label {
  font-size: 11px;
  color: #b5a9a7;
  font-weight: 700;
  margin-bottom: 2px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile__info-value {
  font-size: 16px;
  color: #8B1E3F;
  font-weight: 800;
  word-wrap: break-word;
}

/* =========================================
   FORMULÁRIO E BOTÕES
   ========================================= */
.profile__form { display: flex; flex-direction: column; gap: 14px; }
.profile__field { display: flex; flex-direction: column; gap: 6px; }

.profile__label {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 700; color: #5a4a46;
}
.profile__label-icon { font-size: 14px; color: #E25822; }

.profile__input {
  width: 100%; padding: 12px 14px; font-size: 14px;
  border: 2px solid #e8dedc; border-radius: 10px;
  background: #ffffff; color: #2d2422;
  transition: all 0.3s ease; font-family: inherit; outline: none;
}
.profile__input:focus {
  border-color: #8B1E3F; box-shadow: 0 0 0 4px rgba(139, 30, 63, 0.1);
  transform: translateY(-1px);
}
.profile__input::placeholder { color: #b5a9a7; font-weight: 500; }

.profile__password-wrapper { position: relative; display: flex; align-items: center; }
.profile__password-wrapper .profile__input { padding-right: 50px; }
.profile__toggle-password {
  position: absolute; right: 12px; background: none; border: none;
  color: #b5a9a7; cursor: pointer; padding: 8px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.3s ease;
}
.profile__toggle-password:hover { color: #E25822; background: rgba(226, 88, 34, 0.1); }

.profile__actions { display: flex; flex-direction: column; gap: 8px; margin-top: 6px; }
.profile__save-btn {
  order: 1; width: 100%; padding: 14px; border: none; border-radius: 10px;
  background: #E25822; color: #ffffff; font-size: 15px; font-weight: 800;
  cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px;
  transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(226, 88, 34, 0.3);
}
.profile__save-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(226, 88, 34, 0.4); }
.profile__save-btn:active:not(:disabled) { transform: translateY(1px); }
.profile__save-btn:disabled { opacity: 0.6; cursor: not-allowed; filter: grayscale(0.2); box-shadow: none; }

.profile__cancel-btn {
  order: 2; width: 100%; padding: 12px; border: 2px solid #e8dedc; border-radius: 10px;
  background: transparent; color: #5a4a46; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: all 0.3s ease;
}
.profile__cancel-btn:hover:not(:disabled) { border-color: #E25822; color: #E25822; background: rgba(226, 88, 34, 0.05); }

/* =========================================
   HUB DE BANNERS PROMOCIONAIS
   ========================================= */
.profile__banners-wrapper {
  margin-top: auto; 
  display: flex;
  flex-direction: column;
  gap: 10px; 
}

.promo-banner {
  border-radius: 16px;
  padding: 12px 14px; 
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px; 
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
}

.promo-banner__content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1; 
  min-width: 0; 
}

.promo-banner__icon { font-size: 24px; flex-shrink: 0; }
.promo-banner__icon.float { animation: float-icon 3s ease-in-out infinite; }

.promo-banner__text {
  flex: 1;
  min-width: 0;
}

.promo-banner__text h3 {
  font-size: 13px;
  font-weight: 900;
  margin: 0 0 2px 0;
  letter-spacing: -0.3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.promo-banner__text p {
  font-size: 11px;
  font-weight: 600;
  margin: 0;
  color: #5a4a46;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge-available {
  background: #179B78;
  color: white;
  font-size: 9px;
  font-weight: 800;
  padding: 3px 6px;
  border-radius: 6px;
  letter-spacing: 0.5px;
  display: inline-block;
}

.promo-banner__btn {
  border: none;
  width: 40%; 
  min-width: 100px;
  padding: 12px 10px; 
  border-radius: 10px;
  font-weight: 800;
  font-size: 12px;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center; 
  gap: 6px;
  transition: all 0.2s ease;
}

.promo-banner__btn:active { transform: scale(0.95); }

/* Variação 1: E-book Hotmart */
.promo-banner--ebook { background: rgba(255, 255, 255, 0.9); border: 1px solid rgba(226, 88, 34, 0.1); backdrop-filter: blur(10px); }
.promo-banner--ebook h3 { color: #2d2422; }
.promo-banner__btn--ebook { background: rgba(23, 155, 120, 0.15); color: #0c5c46; }
.promo-banner__btn--ebook:hover { background: rgba(23, 155, 120, 0.25); }

/* Variação 2: Ingresso */
.promo-banner--ticket { background: linear-gradient(135deg, #fffafa 0%, #fcedea 100%); border: 1px solid rgba(139, 30, 63, 0.15); }
.promo-banner--ticket h3 { color: #8B1E3F; }
.promo-banner__btn--primary { background: #8B1E3F; color: #fff; box-shadow: 0 4px 10px rgba(139, 30, 63, 0.2); }
.promo-banner__btn--primary:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(139, 30, 63, 0.3); }

/* Variação 3: Café */
.promo-banner--coffee { background: linear-gradient(135deg, #fff0eb 0%, #ffe4d6 100%); border: 1px solid rgba(226, 88, 34, 0.2); }
.promo-banner--coffee h3 { color: #E25822; }
.promo-banner__btn--accent { background: #E25822; color: #fff; box-shadow: 0 4px 10px rgba(226, 88, 34, 0.3); }
.promo-banner__btn--accent:hover { transform: translateY(-1px); box-shadow: 0 6px 15px rgba(226, 88, 34, 0.4); }

.heart-icon { font-size: 12px; }
.promo-banner__btn--accent:hover .heart-icon { animation: beat 1s infinite; }

/* =========================================
   LOGOUT
   ========================================= */
.profile__logout-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.profile__logout-btn {
  background: transparent;
  border: none;
  color: #b5a9a7;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.profile__logout-btn:hover {
  color: #8B1E3F;
  background: rgba(139, 30, 63, 0.05);
}

/* =========================================
   REDES SOCIAIS (BASTIDORES)
   ========================================= */
.profile__social-wrapper {
  margin-top: 24px;
  text-align: center;
}

.social-title {
  font-size: 11px;
  font-weight: 800;
  color: #b5a9a7;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 14px;
}

.social-links {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.social-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
}

.social-btn--insta {
  background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
  box-shadow: 0 4px 10px rgba(220, 39, 67, 0.3);
}

.social-btn--youtube {
  background: #FF0000;
  box-shadow: 0 4px 10px rgba(255, 0, 0, 0.3);
}

.social-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

/* =========================================
   ANIMAÇÕES E UTILITÁRIOS
   ========================================= */
@keyframes float-icon { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
@keyframes beat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.2); } }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes slideUpFade { to { opacity: 1; transform: translateY(0); } }

.profile__message { padding: 12px 14px; border-radius: 10px; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 700; }
.profile__message--error { background: #fdf2f2; border: 1px solid #e27d72; color: #d13d3d; }
.profile__message--success { background: #fdfaf9; border: 1px solid #e8dedc; color: #8B1E3F; }

.profile__spinner { animation: spin 1s linear infinite; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease, transform 0.5s ease; }
.fade-enter-from { opacity: 0; transform: translateY(15px); }
.fade-leave-to { opacity: 0; transform: translateY(-15px); }

@media (min-width: 768px) {
  .profile { padding: 40px 32px 140px 32px; } 
  .profile__container { max-width: 480px; } 
  .profile__title { font-size: 32px; }
}
</style>
