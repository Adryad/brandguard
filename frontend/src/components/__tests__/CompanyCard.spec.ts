// brandguard/frontend/src/components/__tests__/CompanyCard.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/vue'
import CompanyCard from '@/components/CompanyCard.vue'
import type { Company } from '@/types'

describe('CompanyCard', () => {
  const mockCompany: Company = {
    id: 1,
    name: 'Tech Corp',
    industry: 'Technology',
    country: 'USA',
    reputation_score: 85,
    total_mentions: 1000,
    positive_mentions: 600,
    neutral_mentions: 350,
    negative_mentions: 50,
    reputation_trend: 5.5,
    risk_score: 25,
    sources_config: {},
    is_active: true,
    created_at: '2024-01-01',
    updated_at: '2024-01-01'
  }

  it('renders company information correctly', () => {
    render(CompanyCard, {
      props: { company: mockCompany }
    })

    expect(screen.getByText('Tech Corp')).toBeInTheDocument()
    expect(screen.getByText('Technology')).toBeInTheDocument()
  })

  it('displays correct sentiment distribution', () => {
    render(CompanyCard, {
      props: { company: mockCompany }
    })

    expect(screen.getByText('600')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
  })
})