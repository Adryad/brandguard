<!-- brandguard/frontend/src/views/CompanyView.vue -->
<template>
  <div class="company-view min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <router-link 
            to="/" 
            class="text-sm text-blue-600 hover:text-blue-500 flex items-center mb-4"
          >
            <ArrowLeft class="h-4 w-4 mr-1" />
            Back to Dashboard
          </router-link>
          
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <img
                v-if="company.website"
                :src="`https://www.google.com/s2/favicons?domain=${company.website}&sz=64`"
                class="h-16 w-16 rounded-lg shadow-sm"
                @error="loadDefaultIcon"
              />
              <div class="ml-4">
                <h1 class="text-3xl font-bold text-gray-900">{{ company.name }}</h1>
                <p class="text-lg text-gray-600">{{ company.industry }} • {{ company.country }}</p>
              </div>
            </div>
            
            <div class="text-right">
              <div 
                class="text-4xl font-bold"
                :class="getRiskColor(reputation_score)"
              >
                {{ company.reputation_score.toFixed(0) }}
              </div>
              <div class="text-sm text-gray-500 mt-1">
                Risk Level: <span class="font-medium">{{ risk_level }}</span>
              </div>
              <button
                @click="refreshData"
                :disabled="refreshing"
                class="mt-2 inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm rounded-md hover:bg-gray-50 disabled:opacity-50"
              >
                <RefreshCw class="h-3 w-3 mr-1" :class="{'animate-spin': refreshing}" />
                Refresh
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
        <StatCard
          label="Total Mentions"
          :value="company.total_mentions"
          :change="mention_change"
          :trend="mention_trend"
          icon="MessageSquare"
        />
        <StatCard
          label="Reputation Trend"
          :value="company.reputation_trend"
          :change="trend_change"
          :trend="trend_direction"
          icon="TrendingUp"
        />
        <StatCard
          label="Risk Score"
          :value="risk_score"
          :change="risk_change"
          :trend="risk_trend"
          icon="Shield"
        />
        <StatCard
          label="Alert Count"
          :value="active_alerts"
          change="0"
          trend="stable"
          icon="Bell"
        />
        <StatCard
          label="Last Updated"
          :value="last_updated"
          type="time"
          icon="Clock"
        />
      </div>

      <!-- Charts & Analytics -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Sentiment Trend -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Sentiment Trend (30 Days)</h2>
          <div class="h-64">
            <LineChart
              v-if="chartData"
              :data="sentimentChartData"
              :options="sentimentOptions"
            />
          </div>
        </div>

        <!-- Risk Breakdown -->
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Risk Factors</h2>
          <RiskBreakdown :risk_data="risk_factors" />
        </div>
      </div>

      <!-- Recent Mentions -->
      <div class="bg-white rounded-lg shadow mb-8">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-semibold text-gray-900">Recent Mentions</h2>
            <div class="flex space-x-2">
              <select v-model="filterSource" class="form-input text-sm">
                <option value="">All Sources</option>
                <option v-for="source in sources" :value="source">{{ source }}</option>
              </select>
              <select v-model="filterSentiment" class="form-input text-sm">
                <option value="">All Sentiments</option>
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="divide-y divide-gray-200">
          <ArticleCard
            v-for="article in filteredArticles"
            :key="article.id"
            :article="article"
          />
        </div>
        
        <div class="px-6 py-4">
          <button
            @click="loadMoreArticles"
            :disabled="loading"
            class="w-full btn-secondary"
          >
            Load More
          </button>
        </div>
      </div>

      <!-- Alert Configuration -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Alert Rules</h2>
        <AlertManager
          :company-id="company.id"
          @updated="loadAlerts"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Component setup with composition API
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import apiService from '@/services/apiService'
import { LineChart } from 'vue-chart-3'
import { Chart } from 'chart.js'
import type { Company, TrendAnalysis } from '@/types'

const route = useRoute()
const company = ref<Company>({} as Company)
const trends = ref<TrendAnalysis>({} as TrendAnalysis)
const articles = ref([])
const alerts = ref([])
const refreshing = ref(false)
const loading = ref(true)

const last_updated = computed(() => {
  return new Date(company.value.last_analyzed!).toLocaleString()
})

// Chart data
const sentimentChartData = computed(() => ({
  labels: trends.value.time_labels || [],
  datasets: [{
    label: 'Sentiment Score',
    data: trends.value.scores || [],
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

// Methods
const loadCompanyData = async () => {
  const companyId = parseInt(route.params.id as string)
  company.value = await apiService.getCompany(companyId)
  trends.value = await apiService.getCompanyTrends(companyId, 30)
}

// Component registrations
const components = {
  LineChart,
  StatCard,
  RiskBreakdown,
  ArticleCard,
  AlertManager
}
</script>