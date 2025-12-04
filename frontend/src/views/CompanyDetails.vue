<template>
  <div class="company-detail">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700 flex items-center">
              <ArrowLeft class="h-4 w-4 mr-1" />
              Back to Dashboard
            </router-link>
            <div class="mt-4 flex items-center">
              <img
                v-if="company.website"
                :src="`https://www.google.com/s2/favicons?domain=${company.website}&sz=64`"
                class="h-12 w-12 rounded-lg"
                @error="handleImageError"
              />
              <div class="ml-4">
                <h1 class="text-3xl font-bold text-gray-900">{{ company.name }}</h1>
                <p class="text-lg text-gray-600">{{ company.industry }} • {{ company.country }}</p>
              </div>
            </div>
          </div>
          <div class="text-right">
            <div class="text-3xl font-bold" :class="getScoreColorClass(company.reputation_score)">
              {{ company.reputation_score }}
            </div>
            <div class="text-sm text-gray-500">Reputation Score</div>
            <button
              @click="refreshData"
              :disabled="refreshing"
              class="mt-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw class="h-3 w-3 mr-1" :class="{'animate-spin': refreshing}" />
              Refresh
            </button>
          </div>
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Total Mentions</p>
              <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(company.total_mentions) }}</p>
            </div>
            <div class="flex-shrink-0">
              <MessageSquare class="h-8 w-8 text-gray-400" />
            </div>
          </div>
          <div class="mt-4">
            <div class="flex text-xs text-gray-500">
              <span class="text-green-600">{{ company.positive_mentions }} positive</span>
              <span class="mx-2">•</span>
              <span class="text-red-600">{{ company.negative_mentions }} negative</span>
              <span class="mx-2">•</span>
              <span>{{ company.neutral_mentions }} neutral</span>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Trend</p>
              <p class="text-2xl font-semibold" :class="company.reputation_trend >= 0 ? 'text-green-600' : 'text-red-600'">
                {{ company.reputation_trend >= 0 ? '+' : '' }}{{ company.reputation_trend.toFixed(1) }}%
              </p>
            </div>
            <div class="flex-shrink-0">
              <TrendingUp class="h-8 w-8" :class="company.reputation_trend >= 0 ? 'text-green-400' : 'text-red-400'" />
            </div>
          </div>
          <p class="mt-4 text-xs text-gray-500">Last 30 days</p>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Risk Score</p>
              <p class="text-2xl font-semibold text-gray-900">{{ company.risk_score.toFixed(0) }}</p>
            </div>
            <div class="flex-shrink-0">
              <Shield class="h-8 w-8 text-orange-400" />
            </div>
          </div>
          <p class="mt-4 text-xs text-gray-500">0-100 scale</p>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-500">Last Analyzed</p>
              <p class="text-2xl font-semibold text-gray-900">
                {{ company.last_analyzed ? formatRelativeTime(company.last_analyzed) : 'Never' }}
              </p>
            </div>
            <div class="flex-shrink-0">
              <Clock class="h-8 w-8 text-blue-400" />
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Sentiment Trend Chart -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Sentiment Trend</h2>
          <div class="h-64">
            <LineChart
              v-if="chartData"
              :data="chartData"
              :options="chartOptions"
            />
          </div>
        </div>

        <!-- Sentiment Distribution -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Sentiment Distribution</h2>
          <div class="h-64">
            <DoughnutChart
              v-if="pieData"
              :data="pieData"
              :options="pieOptions"
            />
          </div>
        </div>
      </div>

      <!-- Recent Articles -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">Recent Mentions</h2>
        </div>
        <div class="divide-y divide-gray-200">
          <div
            v-for="article in recentArticles"
            :key="article.id"
            class="p-6 hover:bg-gray-50"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center mb-2">
                  <span
                    :class="getSentimentColor(article.sentiment)"
                    class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ article.sentiment }}
                  </span>
                  <span class="ml-2 text-xs text-gray-500">
                    {{ formatDate(article.published_date) }}
                  </span>
                  <span v-if="article.source" class="ml-2 text-xs text-gray-500">
                    • {{ article.source }}
                  </span>
                </div>
                <h3 class="text-base font-medium text-gray-900 mb-1">
                  <a :href="article.url" target="_blank" class="hover:text-blue-600">
                    {{ article.title }}
                  </a>
                </h3>
                <p class="text-sm text-gray-600 line-clamp-2">{{ article.content }}</p>
                <div class="mt-2 flex items-center text-xs text-gray-500">
                  <span>Confidence: {{ (article.confidence_score * 100).toFixed(0) }}%</span>
                  <span class="mx-2">•</span>
                  <span>Relevance: {{ (article.relevance_score * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Trend Analysis -->
      <div v-if="trends" class="bg-white rounded-lg shadow p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Trend Analysis</h2>
        <p class="text-gray-600 mb-4">{{ trends.summary }}</p>
        
        <div v-if="trends.predictions && trends.predictions.length > 0" class="mt-6">
          <h3 class="text-md font-medium text-gray-900 mb-3">7-Day Forecast</h3>
          <div class="grid grid-cols-7 gap-2">
            <div
              v-for="(prediction, index) in trends.predictions"
              :key="index"
              class="text-center"
            >
              <div class="text-xs text-gray-500">{{ formatDay(prediction.date) }}</div>
              <div class="mt-1 text-sm font-medium">{{ (prediction.predicted_score * 100).toFixed(0) }}</div>
              <div class="w-full bg-gray-200 rounded-full h-1 mt-1">
                <div
                  :style="{ width: (prediction.predicted_score * 100) + '%' }"
                  :class="prediction.predicted_score > 0.6 ? 'bg-green-500' : prediction.predicted_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'"
                  class="h-1 rounded-full"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-end space-x-4">
        <button
          @click="exportReport"
          class="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          <Download class="h-4 w-4 mr-2" />
          Export Report
        </button>
        <button
          @click="scheduleAlert"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <Bell class="h-4 w-4 mr-2" />
          Schedule Alert
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LineChart, DoughnutChart } from 'vue-chart-3'
import { Chart, registerables } from 'chart.js'
import {
  ArrowLeft,
  RefreshCw,
  MessageSquare,
  TrendingUp,
  Shield,
  Clock,
  Bell,
  Download
} from 'lucide-vue-next'
import apiService from '@/services/apiService'
import type { Company, Article, TrendAnalysis } from '@/types'

Chart.register(...registerables)

const route = useRoute()
const router = useRouter()

// State
const company = ref<Company>({} as Company)
const recentArticles = ref<Article[]>([])
const trends = ref<TrendAnalysis | null>(null)
const refreshing = ref(false)
const loading = ref(true)

// Chart data
const chartData = computed(() => {
  if (!trends.value) return null
  
  return {
    labels: trends.value.time_labels || [],
    datasets: [{
      label: 'Sentiment Score',
      data: trends.value.scores || [],
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      tension: 0.4
    }]
  }
})

const pieData = computed(() => {
  const total = company.value.total_mentions
  return {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [{
      data: [
        company.value.positive_mentions,
        company.value.neutral_mentions,
        company.value.negative_mentions
      ],
      backgroundColor: ['#10b981', '#6b7280', '#ef4444']
    }]
  }
})

// Methods
const loadCompanyData = async () => {
  try {
    const companyId = parseInt(route.params.id as string)
    company.value = await apiService.getCompany(companyId)
    
    // Load trends
    trends.value = await apiService.getCompanyTrends(companyId, 90)
    
    // Load recent articles
    const articles = await apiService.getCompanyArticles(companyId, 10)
    recentArticles.value = articles
    
  } catch (error) {
    console.error('Failed to load company data:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  try {
    await apiService.refreshCompanyData(company.value.id, 30)
    await loadCompanyData()
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    refreshing.value = false
  }
}

const exportReport = () => {
  // TODO: Implement report export
  console.log('Export report')
}

const scheduleAlert = () => {
  // TODO: Implement alert scheduling
  console.log('Schedule alert')
}

const getSentimentColor = (sentiment: string) => {
  const colors = {
    positive: 'bg-green-100 text-green-800',
    negative: 'bg-red-100 text-red-800',
    neutral: 'bg-gray-100 text-gray-800'
  }
  return colors[sentiment] || colors.neutral
}

const getScoreColorClass = (score: number) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatRelativeTime = (date: string) => {
  const now = new Date()
  const past = new Date(date)
  const diff = now.getTime() - past.getTime()
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}d ago`
  
  return new Date(date).toLocaleDateString()
}

const formatDay = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { weekday: 'short' })
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat().format(num)
}

const handleImageError = (event: Event) => {
  // Hide broken image
  (event.target as HTMLImageElement).style.display = 'none'
}

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 1
    }
  }
}

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

// Lifecycle
onMounted(() => {
  loadCompanyData()
})
</script>