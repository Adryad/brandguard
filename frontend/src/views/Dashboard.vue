<template>
  <div class="dashboard">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">BrandGuard Dashboard</h1>
        <p class="mt-2 text-gray-600">Monitor your company's reputation across all channels</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Building2 class="h-8 w-8 text-blue-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Total Companies</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.totalCompanies }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <TrendingUp class="h-8 w-8 text-green-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Positive Trends</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.positiveTrends }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <AlertTriangle class="h-8 w-8 text-red-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Active Alerts</p>
              <p class="text-2xl font-semibold text-gray-900">{{ stats.activeAlerts }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <MessageSquare class="h-8 w-8 text-purple-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Total Mentions</p>
              <p class="text-2xl font-semibold text-gray-900">{{ formatNumber(stats.totalMentions) }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Company List -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex justify-between items-center">
                <h2 class="text-lg font-semibold text-gray-900">Monitored Companies</h2>
                <button
                  @click="showAddCompanyModal = true"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                >
                  <Plus class="h-4 w-4 mr-2" />
                  Add Company
                </button>
              </div>
            </div>

            <div class="divide-y divide-gray-200">
              <div v-if="loading" class="p-8 text-center">
                <div class="inline-flex items-center px-4 py-2 text-sm text-gray-500">
                  <Loader2 class="animate-spin h-4 w-4 mr-2" />
                  Loading companies...
                </div>
              </div>

              <div v-else-if="companies.length === 0" class="p-8 text-center text-gray-500">
                <Building2 class="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>No companies monitored yet</p>
                <p class="text-sm">Add your first company to start monitoring</p>
              </div>

              <CompanyCard
                v-else
                v-for="company in companies"
                :key="company.id"
                :company="company"
                @click="goToCompany(company.id)"
              />
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200">
              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalCompanies) }} of {{ totalCompanies }} results
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="currentPage--"
                    :disabled="currentPage === 1"
                    class="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span class="px-3 py-1 text-sm">
                    Page {{ currentPage }} of {{ totalPages }}
                  </span>
                  <button
                    @click="currentPage++"
                    :disabled="currentPage === totalPages"
                    class="px-3 py-1 text-sm border rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Recent Alerts -->
          <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-semibold text-gray-900">Recent Alerts</h2>
            </div>
            <div class="p-6">
              <div v-if="alerts.length === 0" class="text-gray-500 text-sm">
                No recent alerts
              </div>
              <div v-else class="space-y-4">
                <div
                  v-for="alert in alerts.slice(0, 5)"
                  :key="alert.id"
                  class="flex items-start space-x-3"
                >
                  <div :class="getAlertColor(alert.severity)" class="w-2 h-2 rounded-full mt-2"></div>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900">{{ alert.title }}</p>
                    <p class="text-xs text-gray-500">{{ formatDate(alert.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div class="space-y-3">
              <button
                @click="generateReport"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md flex items-center"
              >
                <FileText class="h-4 w-4 mr-3" />
                Generate Report
              </button>
              <button
                @click="exportData"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md flex items-center"
              >
                <Download class="h-4 w-4 mr-3" />
                Export Data
              </button>
              <button
                @click="showSettings"
                class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md flex items-center"
              >
                <Settings class="h-4 w-4 mr-3" />
                Settings
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Company Modal -->
    <AddCompanyModal
      v-if="showAddCompanyModal"
      @close="showAddCompanyModal = false"
      @company-added="loadCompanies"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCompanyStore } from '@/stores/company'
import { useAlertStore } from '@/stores/alert'
import CompanyCard from '@/components/CompanyCard.vue'
import AddCompanyModal from '@/components/AddCompanyModal.vue'
import {
  Building2,
  TrendingUp,
  AlertTriangle,
  MessageSquare,
  Plus,
  Loader2,
  FileText,
  Download,
  Settings
} from 'lucide-vue-next'

const router = useRouter()
const companyStore = useCompanyStore()
const alertStore = useAlertStore()

// State
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const showAddCompanyModal = ref(false)

// Computed
const companies = computed(() => companyStore.companies)
const alerts = computed(() => alertStore.alerts)
const totalCompanies = computed(() => companyStore.totalCount)
const totalPages = computed(() => Math.ceil(totalCompanies.value / pageSize.value))

const stats = computed(() => ({
  totalCompanies: totalCompanies.value,
  positiveTrends: companyStore.companies.filter(c => c.reputation_score > 70).length,
  activeAlerts: alerts.value.filter(a => !a.is_read).length,
  totalMentions: companyStore.companies.reduce((sum, c) => sum + c.total_mentions, 0)
}))

// Methods
const loadCompanies = async () => {
  loading.value = true
  try {
    await companyStore.fetchCompanies(currentPage.value, pageSize.value)
  } catch (error) {
    console.error('Failed to load companies:', error)
  } finally {
    loading.value = false
  }
}

const loadAlerts = async () => {
  try {
    await alertStore.fetchAlerts()
  } catch (error) {
    console.error('Failed to load alerts:', error)
  }
}

const goToCompany = (id: number) => {
  router.push(`/companies/${id}`)
}

const getAlertColor = (severity: string) => {
  const colors = {
    low: 'bg-gray-400',
    medium: 'bg-yellow-400',
    high: 'bg-orange-400',
    critical: 'bg-red-400'
  }
  return colors[severity] || colors.medium
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatNumber = (num: number) => {
  return new Intl.NumberFormat().format(num)
}

const generateReport = () => {
  // TODO: Implement report generation
  console.log('Generate report')
}

const exportData = () => {
  // TODO: Implement data export
  console.log('Export data')
}

const showSettings = () => {
  router.push('/settings')
}

// Lifecycle
onMounted(async () => {
  await loadCompanies()
  await loadAlerts()
})
</script>