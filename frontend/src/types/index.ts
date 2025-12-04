// brandguard/frontend/src/types/index.ts
export interface Company {
  id: number
  name: string
  legal_name?: string
  industry: string
  website?: string
  country: string
  description?: string
  reputation_score: number
  reputation_trend: number
  total_mentions: number
  positive_mentions: number
  negative_mentions: number
  neutral_mentions: number
  risk_score: number
  risk_factors: string[]
  sources_config: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
  last_analyzed?: string
}

export interface CompanyCreate {
  name: string
  legal_name?: string
  industry: string
  website?: string
  country: string
  description?: string
  sources_config?: Record<string, any>
}

export interface CompanyUpdate {
  name?: string
  legal_name?: string
  industry?: string
  website?: string
  country?: string
  description?: string
  sources_config?: Record<string, any>
}

export interface Article {
  id: number
  company_id: number
  source_id: number
  title: string
  content: string
  url: string
  published_date: string
  author?: string
  sentiment: 'positive' | 'negative' | 'neutral'
  confidence_score: number
  keywords: string[]
  entities: Array<{
    text: string
    label: string
  }>
  relevance_score: number
  is_public: boolean
  created_at: string
  source?: string
}

export interface Alert {
  id: number
  company_id: number
  alert_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  message: string
  is_read: boolean
  is_resolved: boolean
  created_at: string
  resolved_at?: string
}

export interface TrendAnalysis {
  trend: 'improving' | 'declining' | 'stable'
  momentum: number
  predictions: Array<{
    date: string
    predicted_score: number
    confidence: number
  }>
  seasonal_patterns: Array<{
    type: 'weekly' | 'monthly'
    period: string
    score: number
    significance: 'high' | 'medium' | 'low'
  }>
  volatility: number
  summary: string
  time_labels?: string[]
  scores?: number[]
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}