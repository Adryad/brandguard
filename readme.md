# 📊 BrandGuard - Company Reputation Analysis System

**BrandGuard** is a comprehensive, open-source SaaS platform for **legally monitoring and analyzing company reputation** using only public data sources. Built with modern full-stack technologies, it provides real-time insights into how your brand is perceived across news, reviews, and social media.

---

## 🌟 Key Features

| **Feature** | **Description** |
|-------------|-----------------|
| **📡 Legal Data Collection** | Harvests data from public RSS feeds, APIs, and websites only |
| **🤖 AI Sentiment Analysis** | Uses open-source transformers (DistilBERT) for accurate sentiment detection |
| **📈 Trend Analysis** | Predicts reputation trends using linear regression and seasonal analysis |
| **⚠️ Risk Scoring** | Multi-factor risk assessment with detailed explanations |
| **📊 Interactive Dashboard** | Real-time charts, metrics, and company cards |
| **🔔 Smart Alerts** | Configurable alerts for reputation changes |
| **📄 Export Reports** | Download PDF/Excel reports with visualizations |
| **🔐 GDPR Compliance** | Built-in privacy and data retention management |

---

## 🏗️ Tech Stack

### **Backend**
- **Framework:** Python 3.11 + FastAPI
- **Database:** PostgreSQL 15 + Elasticsearch 8
- **Cache:** Redis 7
- **Task Queue:** Celery with Redis
- **ML:** Transformers + Scikit-learn

### **Frontend**
- **Framework:** Vue 3 + TypeScript
- **Styling:** TailwindCSS 3
- **Charts:** Chart.js + Vue Chart 3
- **State:** Pinia
- **Icons:** Lucide Vue

### **Infrastructure**
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx
- **Monitoring:** Built-in health checks

---

## 📦 Installation Guide

### **1. Prerequisites**
Install the following tools:

| Tool | Download | Version |
|------|----------|---------|
| **Python** | https://www.python.org/downloads/ | 3.11+ |
| **Node.js** | https://nodejs.org/en/ | 18+ LTS |
| **Docker** | https://docs.docker.com/get-docker/ | Latest |
| **Docker Compose** | https://docs.docker.com/compose/install/ | V2+ |
| **Git** | https://git-scm.com/downloads | Any |

```bash
# Verify installations
python3 --version      # → 3.11+
node --version         # → v18+
docker --version       # → 24+
docker-compose --version
```

### **2. Quick Start (5 minutes)**

```bash
# Clone repository
git clone https://github.com/your-org/brandguard.git
cd brandguard

# 🔧 Option A: Docker Compose (Recommended)
cp .env.example .env
docker-compose up -d

# 🏗️ Option B: Development setup
./scripts/setup.sh
```

### **3. Verify Installation**

```bash
# Check services
docker-compose ps
# Navigate to:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000/docs
# - Elasticsearch: http://localhost:9200
```

---

## 🎯 Usage Guide

### **First-Time Setup**

1. **Access Dashboard**
   ```bash
   # Open in browser
   http://localhost:3000
   ```

2. **Add Your First Company**
   ```bash
   curl -X POST http://localhost:8000/api/v1/companies \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Tesla",
       "industry": "automotive",
       "country": "USA",
       "website": "https://tesla.com"
     }'
   ```

3. **Watch the Magic**
   - Data collection starts automatically
   - Check dashboard after 5-10 minutes
   - Configure alerts for changes

---

## ⚙️ Configuration

### **Environment Variables**
Edit `.env`:

```bash
# Required
POSTGRES_PASSWORD=your_secure_password123
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://redis:6379/0

# Optional APIs
NEWS_API_KEY=your_rss_api_key
ALPHA_VANTAGE_API_KEY=your_financial_api_key

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
```

### **Database Setup**
```bash
# Auto-migrate
docker-compose exec backend alembic upgrade head

# Manual migration (if needed)
cd backend
alembic revision --autogenerate -m "add_notifications"
alembic upgrade head
```

---

## 🧪 Development Commands

### **🔧 Backend Development**
```bash
# Activate virtual environment
cd backend && source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0

# Run tests
pytest tests/
```

### **⚛️ Frontend Development**
```bash
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### **🔄 Background Tasks**
```bash
# Manual data refresh
docker-compose exec backend python -c "
from app.services.data_collectors import LegalNewsCollector
collector = LegalNewsCollector()
collector.collect_company_news(1, days_back=7)
"

# View Celery tasks
docker-compose logs -f celery-worker
```

---

## 🔐 Security & Compliance

### **GDPR Compliance Checklist**
- ✅ Only collects **publicly available** data
- ✅ **12-month** automatic data retention
- ✅ **Anonymizes** personal information
- ✅ **Right to be forgotten** implemented
- ✅ **Clear privacy policy** required

### **Robots.txt Respect**
All data collectors automatically respect `robots.txt` and follow rate limits.

---

## 📊 Adding Data Sources

### **Add New News Source**
```python
# Add to data_sources table
POST /api/v1/sources
{
  "name": "NewSource",
  "source_type": "news",
  "url": "https://rss.newsource.com",
  "credibility_score": 0.8
}
```

### **Configure Alert Rules**
```json
{
  "company_id": 1,
  "rule": "reputation_score < 50",
  "email": "alerts@yourcompany.com",
  "frequency": "immediate"
}
```

---

## 🐛 Troubleshooting

| **Issue** | **Solution** |
|-----------|--------------|
| **Postgres won't start** | `sudo chmod 777 pgdata/` (Mac/Linux) |
| **Container errors** | `docker-compose down -v` and restart |
| **Rate limits** | Check `.env` for API keys |
| **Build errors** | Ensure Node.js 18+ and Python 3.11+ |

---

## 📞 Support

### **Community Resources**
- 📖 [**Documentation**](https://brandguard.docs.com)
- 💬 [**Discord**](https://discord.gg/brandguard) 
- 📧 [**Issues**](https://github.com/your-org/brandguard/issues)
- 🧑‍💻 [**Discussions**](https://github.com/your-org/brandguard/discussions)

### **Getting Help**
```bash
# Quick diagnostic
./scripts/diagnose.sh

# Logs
docker-compose logs -f [service]
```

---

## 🏆 What's Next?

### **🚀 Roadmap**
- [ ] **Slack/Teams Integration**
- [ ] **Advanced Predictive Models**
- [ ] **Competitor Analysis**
- [ ] **Mobile App**
- [ ] **Market Intelligence Dashboard**

### **Contributing Guide**
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## 🎉 License

```text
Copyright (c) 2025 Adryad

All rights reserved.

This software and associated documentation files (the "Software") are the property of Adryad.  
Unauthorized copying, modification, distribution, or use of the Software, in whole or in part, is strictly prohibited without prior written consent from the copyright holder.

You may not:
- Copy, modify, merge, publish, distribute, sublicense, or sell copies of the Software.
- Use the Software for commercial purposes without a valid license agreement.
- Reverse engineer, decompile, or disassemble the Software.

The Software is provided "AS IS", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability arising from the use of the Software.

For licensing inquiries, please contact: Adhamryad8@gmail.com.

```

---

**⭐ Star our repo if you find this helpful!**