<!-- brandguard/frontend/src/components/CompanyCard.vue -->
<template>
  <div
    @click="$emit('click')"
    class="p-6 hover:bg-gray-50 cursor-pointer transition-colors duration-200"
  >
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <div class="flex items-center">
          <h3 class="text-lg font-semibold text-gray-900">{{ company.name }}</h3>
          <span class="ml-2 px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-700">
            {{ company.industry }}
          </span>
        </div>
        
        <p v-if="company.description" class="mt-1 text-sm text-gray-600">
          {{ company.description }}
        </p>
        
        <div class="mt-3 flex items-center space-x-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <span
                :class="getScoreColor(company.reputation_score)"
                class="inline-flex items-center justify-center w-10 h-10 rounded-full text-white font-semibold"
              >
                {{ company.reputation_score }}
              </span>
            </div>
            <div class="ml-3">
              <p class="text-xs text-gray-500">Reputation Score</p>
              <p class="text-sm font-medium text-gray-900">{{ getScoreLabel(company.reputation_score) }}</p>
            </div>
          </div>
          
          <div class="text-sm">
            <p class="text-gray-500">Mentions</p>
            <p class="font-medium text-gray-900">{{ formatNumber(company.total_mentions) }}</p>
          </div>
          
          <div class="text-sm">
            <p class="text-gray-500">Trend</p>
            <p
              :class="company.reputation_trend >= 0 ? 'text-green-600' : 'text-red-600'"
              class="font-medium"
            >
              {{ company.reputation_trend >= 0 ? '+' : '' }}{{ company.reputation_trend.toFixed(1) }}%
            </p>
          </div>
        </div>
      </div>
      
      <div class="ml-6 flex-shrink-0">
        <ChevronRight class="h-5 w-5 text-gray-400" />
      </div>
    </div>
    
    <!-- Sentiment Distribution -->
    <div v-if="company.total_mentions > 0" class="mt-4">
      <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
        <span>Sentiment Distribution</span>
        <span>Last 30 days</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="flex h-2 rounded-full overflow-hidden">
          <div
            :style="{ width: positivePercentage + '%' }"
            class="bg-green-500"
          ></div>
          <div
            :style="{ width: neutralPercentage + '%' }"
            class="bg-gray-400"
          ></div>
          <div
            :style="{ width: negativePercentage + '%' }"
            class="bg-red-500"
          ></div>
        </div>
      </div>
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>+{{ company.positive_mentions }}</span>
        <span>{{ company.neutral_mentions }}</span>
        <span>-{{ company.negative_mentions }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ChevronRight } from 'lucide-vue-next'
import type { Company } from '@/types'

interface Props {
  company: Company
}

const props = defineProps<Props>()
defineEmits(['click'])

// Computed
const positivePercentage = computed(() => {
  if (props.company.total_mentions === 0) return 0
  return (props.company.positive_mentions / props.company.total_mentions) * 100
})

const neutralPercentage = computed(() => {
  if (props.company.total_mentions === 0) return 0
  return (props.company.neutral_mentions / props.company.total_mentions) * 100
})

const negativePercentage = computed(() => {
  if (props.company.total_mentions === 0) return 0
  return (props.company.negative_mentions / props.company.total_mentions) * 100
})

// Methods
const getScoreColor = (score: number): string => {
  if (score >= 80) return 'bg-green-500'
  if (score >= 60) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getScoreLabel = (score: number): string => {
  if (score >= 80) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'Fair'
  return 'Poor'
}

const formatNumber = (num: number): string => {
  return new Intl.NumberFormat().format(num)
}
</script>