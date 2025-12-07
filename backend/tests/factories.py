# brandguard/backend/tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from datetime import datetime
from app.models.company import Company, DataSource
from app.models.sentiment import Article, Review

class CompanyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Company
    
    name = factory.Faker('company')
    legal_name = factory.Faker('company_suffix')
    industry = factory.Faker('industry')
    website = factory.Faker('url')
    country = factory.Faker('country')
    description = factory.Faker('text', max_nb_chars=200)
    reputation_score = factory.Faker('pyfloat', min_value=0, max_value=100)
    total_mentions = factory.Faker('pyint', min_value=0, max_value=10000)
    positive_mentions = factory.Faker('pyint', min_value=0, max_value=5000)
    negative_mentions = factory.Faker('pyint', min_value=0, max_value=1000)
    neutral_mentions = factory.Faker('pyint', min_value=0, max_value=5000)

class ArticleFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Article
    
    title = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('text', max_nb_chars=500)
    url = factory.Faker('url')
    published_date = factory.Faker('date_time_between', start_date='-30d', end_date='now')
    sentiment = factory.Iterator(['positive', 'negative', 'neutral'])
    confidence_score = factory.Faker('pyfloat', min_value=0.5, max_value=1.0)
    relevance_score = factory.Faker('pyfloat', min_value=0.0, max_value=1.0)