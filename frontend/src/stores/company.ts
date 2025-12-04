// brandguard/frontend/src/stores/company.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiService from '@/services/apiService'
import type { Company } from '@/types'

export const useCompanyStore = defineStore('company', () => {
  // State
  const companies = ref<Company[]>([])
  const currentCompany = ref<Company | null>(null)
  const loading = ref(false)
  const totalCount = ref(0)
  const filters = ref({
    search: '',
    industry: '',
    country: ''
  })

  // Getters
  const filteredCompanies = computed(() => {
    let result = companies.value

    if (filters.value.search) {
      result = result.filter(c => 
        c.name.toLowerCase().includes(filters.value.search.toLowerCase()) ||
        c.industry.toLowerCase().includes(filters.value.search.toLowerCase())
      )
    }

    if (filters.value.industry) {
      result = result.filter(c => c.industry === filters.value.industry)
    }

    if (filters.value.country) {
      result = result.filter(c => c.country === filters.value.country)
    }

    return result
  })

  const industries = computed(() => {
    const unique = [...new Set(companies.value.map(c => c.industry))]
    return unique.sort()
  })

  const countries = computed(() => {
    const unique = [...new Set(companies.value.map(c => c.country))]
    return unique.sort()
  })

  const averageReputation = computed(() => {
    if (companies.value.length === 0) return 0
    const sum = companies.value.reduce((acc, c) => acc + c.reputation_score, 0)
    return sum / companies.value.length
  })

  // Actions
  async function fetchCompanies(page = 1, limit = 20, search = '', industry = '') {
    loading.value = true
    try {
      const response = await apiService.getCompanies(page, limit, search, industry)
      companies.value = response.companies
      totalCount.value = response.total
    } catch (error) {
      console.error('Failed to fetch companies:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchCompany(id: number) {
    loading.value = true
    try {
      const company = await apiService.getCompany(id)
      currentCompany.value = company
      return company
    } catch (error) {
      console.error('Failed to fetch company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function createCompany(companyData: Partial<Company>) {
    loading.value = true
    try {
      const newCompany = await apiService.createCompany(companyData)
      companies.value.unshift(newCompany)
      totalCount.value++
      return newCompany
    } catch (error) {
      console.error('Failed to create company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function updateCompany(id: number, updates: Partial<Company>) {
    loading.value = true
    try {
      const updatedCompany = await apiService.updateCompany(id, updates)
      const index = companies.value.findIndex(c => c.id === id)
      if (index !== -1) {
        companies.value[index] = updatedCompany
      }
      if (currentCompany.value?.id === id) {
        currentCompany.value = updatedCompany
      }
      return updatedCompany
    } catch (error) {
      console.error('Failed to update company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function deleteCompany(id: number) {
    loading.value = true
    try {
      await apiService.deleteCompany(id)
      companies.value = companies.value.filter(c => c.id !== id)
      totalCount.value--
      if (currentCompany.value?.id === id) {
        currentCompany.value = null
      }
    } catch (error) {
      console.error('Failed to delete company:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  function setFilters(newFilters: typeof filters.value) {
    filters.value = newFilters
  }

  function clearFilters() {
    filters.value = {
      search: '',
      industry: '',
      country: ''
    }
  }

  return {
    // State
    companies,
    currentCompany,
    loading,
    totalCount,
    filters,
    
    // Getters
    filteredCompanies,
    industries,
    countries,
    averageReputation,
    
    // Actions
    fetchCompanies,
    fetchCompany,
    createCompany,
    updateCompany,
    deleteCompany,
    setFilters,
    clearFilters
  }
})