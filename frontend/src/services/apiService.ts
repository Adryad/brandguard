// brandguard/frontend/src/services/apiService.ts
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import type { Company, CompanyCreate, TrendAnalysis, Alert } from '@/types'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Company endpoints
  async getCompanies(page = 1, limit = 20, search = '', industry = ''): Promise<{
    companies: Company[]
    total: number
  }> {
    const params = new URLSearchParams({
      skip: ((page - 1) * limit).toString(),
      limit: limit.toString()
    })
    
    if (search) params.append('search', search)
    if (industry) params.append('industry', industry)

    const response = await this.api.get(`/companies?${params}`)
    return {
      companies: response.data,
      total: parseInt(response.headers['x-total-count'] || '0')
    }
  }

  async getCompany(id: number): Promise<Company> {
    const response = await this.api.get(`/companies/${id}`)
    return response.data
  }

  async createCompany(company: CompanyCreate): Promise<Company> {
    const response = await this.api.post('/companies', company)
    return response.data
  }

  async updateCompany(id: number, company: Partial<Company>): Promise<Company> {
    const response = await this.api.put(`/companies/${id}`, company)
    return response.data
  }

  async deleteCompany(id: number): Promise<void> {
    await this.api.delete(`/companies/${id}`)
  }

  // Analysis endpoints
  async getCompanyTrends(id: number, days = 90): Promise<TrendAnalysis> {
    const response = await this.api.get(`/companies/${id}/trends?days=${days}`)
    return response.data
  }

  async refreshCompanyData(id: number, days = 30): Promise<{
    message: string
    new_articles: number
    total_mentions: number
  }> {
    const response = await this.api.post(`/companies/${id}/refresh?days_back=${days}`)
    return response.data
  }

  // Alert endpoints
  async getAlerts(companyId?: number, unread = false): Promise<Alert[]> {
    const params = new URLSearchParams()
    if (companyId) params.append('company_id', companyId.toString())
    if (unread) params.append('unread', 'true')

    const response = await this.api.get(`/alerts?${params}`)
    return response.data
  }

  async markAlertRead(id: number): Promise<void> {
    await this.api.patch(`/alerts/${id}`, { is_read: true })
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get('/health')
    return response.data
  }
}

export default new ApiService()