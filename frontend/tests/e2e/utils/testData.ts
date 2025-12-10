export const testCompanies = {
  validCompany: {
    name: 'Test Corporation',
    industry: 'technology',
    country: 'USA',
    website: 'https://testcorp.com'
  },
  invalidCompany: {
    name: '',
    industry: '',
    country: '',
    website: 'invalid-url'
  },
  edgeCaseCompany: {
    name: 'A'.repeat(100), // Long name
    industry: 'other',
    country: 'Test Country with very long name that might overflow',
    website: 'https://very-long-subdomain.another-long-subdomain.example.com'
  }
};

export const industryOptions = [
  'technology',
  'finance',
  'healthcare',
  'retail',
  'manufacturing',
  'energy',
  'other'
];

export const alertSeverities = [
  'low',
  'medium',
  'high',
  'critical'
];