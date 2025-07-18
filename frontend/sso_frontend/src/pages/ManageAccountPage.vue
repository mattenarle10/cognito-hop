<template>
  <AuthBackground>
    <!-- Back Button - Top Left -->
    <div class="fixed top-4 left-4 z-50">
      <AuthButton 
        @click="goBack"
        class="!bg-transparent !border-zinc-700 !text-zinc-400 hover:!text-zinc-300 hover:!bg-zinc-800/50 !text-sm !px-3 !py-2"
      >
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
        back
      </AuthButton>
    </div>

    <AuthCard wide>
      <!-- Header -->
      <div class="mb-8 text-center">
        <h1 class="text-3xl font-bold tracking-tight mb-2">
          <span class="bg-gradient-to-r from-gray-200 via-gray-100 to-gray-300 bg-clip-text text-transparent">
            manage account
          </span>
        </h1>
        <p class="text-zinc-500 text-sm">
          account settings and app permissions
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block w-8 h-8 border-2 border-zinc-600 border-t-zinc-300 rounded-full animate-spin"></div>
        <p class="mt-4 text-zinc-400">loading account info...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-lg text-sm mb-6">
        {{ error }}
      </div>

      <!-- Account Info Section -->
      <div v-else class="space-y-6">
        <!-- User Profile Card -->
        <div class="bg-zinc-900/60 border border-zinc-700/60 rounded-lg p-6">
          <h3 class="text-lg font-medium text-zinc-200 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            account information
          </h3>
          
          <div class="space-y-4">
            <!-- Display Name -->
            <div class="flex items-center justify-between">
              <div>
                <label class="text-sm text-zinc-400 uppercase tracking-wide">display name</label>
                <p class="text-zinc-200 font-medium">{{ userInfo?.name || 'not set' }}</p>
              </div>
              <AuthButton 
                class="!bg-zinc-700 hover:!bg-zinc-600 !text-zinc-300 !text-sm !px-3 !py-1.5"
                disabled
              >
                coming soon
              </AuthButton>
            </div>
            
            <!-- Email -->
            <div>
              <label class="text-sm text-zinc-400 uppercase tracking-wide">email</label>
              <p class="text-zinc-200">{{ userInfo?.email || 'not available' }}</p>
            </div>
          </div>
        </div>

        <!-- Management Menu -->
        <div class="space-y-3">
          <h3 class="text-lg font-medium text-zinc-200 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"></path>
            </svg>
            settings & permissions
          </h3>
          
          <!-- App Authorizations Menu Item -->
          <div 
            @click="goToAuthorizations"
            class="bg-zinc-900/60 border border-zinc-700/60 rounded-lg p-4 hover:bg-zinc-800/60 transition-all duration-200 shadow-sm hover:shadow-md cursor-pointer group"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 bg-gradient-to-br from-zinc-800 to-zinc-900 border border-zinc-700/50 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-zinc-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <div>
                  <h4 class="font-medium text-zinc-200 group-hover:text-zinc-100">app authorizations</h4>
                  <p class="text-sm text-zinc-400">manage which apps can access your account</p>
                  <p class="text-xs text-zinc-500 mt-1">{{ authorizationCount }} authorized apps</p>
                </div>
              </div>
              <svg class="w-5 h-5 text-zinc-500 group-hover:text-zinc-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            </div>
          </div>
        </div>


      </div>
    </AuthCard>
  </AuthBackground>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useApi } from '../composables/useApi'
import { useToast } from 'vue-toastification'
import AuthBackground from '../components/ui/AuthBackground.vue'
import AuthCard from '../components/ui/AuthCard.vue'
import AuthButton from '../components/ui/AuthButton.vue'

// composables
const router = useRouter()
const route = useRoute()
const api = useApi()
const toast = useToast()

// state
const loading = ref(false)
const error = ref('')
const userInfo = ref<any>(null)
const authorizationCount = ref(0)
const currentTokens = ref<any>(null)

// load user data and authorization count
const loadUserData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // check if we have session_id in url params
    const sessionId = route.query.session_id as string
    
    if (sessionId) {
      // get session and tokens from sso backend
      const sessionData = await api.getSession(sessionId)
      if (sessionData && sessionData.tokens) {
        currentTokens.value = sessionData.tokens
        
        // extract user info from id_token
        if (sessionData.tokens.id_token) {
          const tokenPayload = parseJwt(sessionData.tokens.id_token)
          userInfo.value = {
            name: tokenPayload.name || tokenPayload.given_name || 'user',
            email: tokenPayload.email || 'not available'
          }
        }
      } else {
        error.value = 'failed to get session data - please try logging in again'
        return
      }
    } else {
      error.value = 'no session found - please access through your application'
      return
    }
    
    // get user authorizations to show count (passing token directly)
    const result = await api.getUserAuthorizations(currentTokens.value?.id_token)
    if (result) {
      authorizationCount.value = result.authorizations?.length || 0
    }
    
  } catch (err: any) {
    error.value = err.message || 'failed to load account information'
  } finally {
    loading.value = false
  }
}

// helper function to parse jwt token
function parseJwt(token: string) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    return JSON.parse(jsonPayload)
  } catch (e) {
    console.error('error parsing jwt token:', e)
    return {}
  }
}

// navigate to authorizations page with session context
const goToAuthorizations = () => {
  const sessionId = route.query.session_id as string
  if (sessionId) {
    router.push(`/authorizations?session_id=${sessionId}`)
  } else {
    router.push('/authorizations')
  }
}

// go back to profile page
const goBack = () => {
  // go back to the client app profile page
  const clientAppUrl = import.meta.env.VITE_CLIENT_APP_URL || 'http://localhost:8080'
  window.location.href = `${clientAppUrl}/profile`
}

// load data on mount
onMounted(() => {
  loadUserData()
})
</script> 