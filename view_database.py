#!/usr/bin/env python3
"""
Database Viewer for ESG Sentiment Scorer
View and analyze scraped data in the database
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import argparse

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings

class DatabaseViewer:
    def __init__(self):
        self.engine = create_engine(settings.database_url)
    
    def get_table_stats(self):
        """Get statistics for all tables"""
        query = text("""
            SELECT 
                schemaname,
                relname as table_name,
                n_live_tup as row_count,
                n_tup_ins as total_inserts,
                n_tup_upd as total_updates,
                n_tup_del as total_deletes
            FROM pg_stat_user_tables 
            ORDER BY n_live_tup DESC;
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_companies(self, limit=10):
        """Get companies in the database"""
        query = text(f"""
            SELECT 
                name,
                ticker,
                sector,
                industry,
                country,
                created_at
            FROM companies 
            ORDER BY created_at DESC
            LIMIT {limit};
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_news_articles(self, limit=10, company_name=None, hours_back=24):
        """Get recent news articles"""
        where_clause = f"WHERE scraped_date > NOW() - INTERVAL '{hours_back} hours'"
        
        if company_name:
            where_clause += f" AND EXISTS (SELECT 1 FROM companies c WHERE c.id = na.company_id AND c.name ILIKE '%{company_name}%')"
        
        query = text(f"""
            SELECT 
                na.title,
                na.source,
                na.published_date,
                na.scraped_date,
                na.language,
                na.word_count,
                c.name as company_name,
                c.ticker,
                LENGTH(na.content) as content_length
            FROM news_articles na
            LEFT JOIN companies c ON na.company_id = c.id
            {where_clause}
            ORDER BY na.scraped_date DESC
            LIMIT {limit};
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_esg_analysis(self, limit=10, company_name=None):
        """Get ESG sentiment analysis results"""
        where_clause = ""
        if company_name:
            where_clause = f"WHERE c.name ILIKE '%{company_name}%'"
        
        query = text(f"""
            SELECT 
                c.name as company_name,
                c.ticker,
                esa.overall_sentiment,
                esa.confidence_score,
                esa.environmental_score,
                esa.social_score,
                esa.governance_score,
                esa.key_themes,
                esa.risk_indicators,
                esa.analyzed_at,
                na.title as article_title
            FROM esg_sentiment_analysis esa
            JOIN companies c ON esa.company_id = c.id
            LEFT JOIN news_articles na ON esa.article_id = na.id
            {where_clause}
            ORDER BY esa.analyzed_at DESC
            LIMIT {limit};
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_analysis_logs(self, limit=10):
        """Get analysis processing logs"""
        query = text(f"""
            SELECT 
                al.search_query,
                al.articles_found,
                al.articles_analyzed,
                al.processing_time_ms,
                al.status,
                al.error_message,
                al.created_at,
                c.name as company_name
            FROM analysis_logs al
            LEFT JOIN companies c ON al.company_id = c.id
            ORDER BY al.created_at DESC
            LIMIT {limit};
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_daily_summary(self, days_back=7):
        """Get daily summary of activity"""
        query = text(f"""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total_articles,
                COUNT(DISTINCT company_id) as unique_companies,
                AVG(word_count) as avg_word_count
            FROM news_articles 
            WHERE created_at > NOW() - INTERVAL '{days_back} days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC;
        """)
        
        df = pd.read_sql(query, self.engine)
        return df
    
    def get_company_esg_scores(self, company_name=None):
        """Get latest ESG scores by company"""
        where_clause = ""
        if company_name:
            where_clause = f"WHERE c.name ILIKE '%{company_name}%'"
        
        query = text(f"""
            SELECT 
                c.name as company_name,
                c.ticker,
                c.sector,
                ces.environmental_score,
                ces.social_score,
                ces.governance_score,
                ces.overall_score,
                ces.confidence_score,
                ces.articles_analyzed,
                ces.risk_level,
                ces.date as score_date
            FROM companies c
            LEFT JOIN company_esg_scores ces ON c.id = ces.company_id
            {where_clause}
            ORDER BY ces.date DESC, ces.overall_score DESC;
        """)
        
        df = pd.read_sql(query, self.engine)
        return df

def main():
    parser = argparse.ArgumentParser(description='View ESG Sentiment Scorer Database')
    parser.add_argument('--company', '-c', help='Filter by company name')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Limit results (default: 10)')
    parser.add_argument('--hours', type=int, default=24, help='Hours back to search (default: 24)')
    parser.add_argument('--section', '-s', choices=['all', 'stats', 'companies', 'articles', 'analysis', 'logs', 'summary'], 
                       default='all', help='Which section to show')
    
    args = parser.parse_args()
    
    viewer = DatabaseViewer()
    
    print("=" * 80)
    print("🌍 ESG SENTIMENT SCORER DATABASE VIEWER")
    print("=" * 80)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        if args.section in ['all', 'stats']:
            print("📊 TABLE STATISTICS")
            print("-" * 40)
            stats = viewer.get_table_stats()
            if not stats.empty:
                print(stats.to_string(index=False))
            else:
                print("No data found")
            print()
        
        if args.section in ['all', 'companies']:
            print("🏢 COMPANIES")
            print("-" * 40)
            companies = viewer.get_companies(limit=args.limit)
            if not companies.empty:
                print(companies.to_string(index=False))
            else:
                print("No companies found")
            print()
        
        if args.section in ['all', 'articles']:
            print(f"📰 NEWS ARTICLES (Last {args.hours} hours)")
            print("-" * 40)
            articles = viewer.get_news_articles(limit=args.limit, company_name=args.company, hours_back=args.hours)
            if not articles.empty:
                print(articles.to_string(index=False))
            else:
                print(f"No articles found in the last {args.hours} hours")
            print()
        
        if args.section in ['all', 'analysis']:
            print("🧠 ESG ANALYSIS RESULTS")
            print("-" * 40)
            analysis = viewer.get_esg_analysis(limit=args.limit, company_name=args.company)
            if not analysis.empty:
                print(analysis.to_string(index=False))
            else:
                print("No ESG analysis results found")
            print()
        
        if args.section in ['all', 'logs']:
            print("📋 PROCESSING LOGS")
            print("-" * 40)
            logs = viewer.get_analysis_logs(limit=args.limit)
            if not logs.empty:
                print(logs.to_string(index=False))
            else:
                print("No processing logs found")
            print()
        
        if args.section in ['all', 'summary']:
            print("📈 DAILY SUMMARY (Last 7 days)")
            print("-" * 40)
            summary = viewer.get_daily_summary()
            if not summary.empty:
                print(summary.to_string(index=False))
            else:
                print("No daily activity found")
            print()
            
            # ESG Scores
            print("🎯 ESG SCORES BY COMPANY")
            print("-" * 40)
            scores = viewer.get_company_esg_scores(company_name=args.company)
            if not scores.empty:
                print(scores.to_string(index=False))
            else:
                print("No ESG scores calculated yet")
            print()
    
    except Exception as e:
        print(f"❌ Error viewing database: {e}")
        return 1
    
    print("=" * 80)
    print("💡 Usage examples:")
    print("  python view_database.py --section articles --hours 1    # Recent articles")
    print("  python view_database.py --company Apple --limit 5       # Apple-related data")
    print("  python view_database.py --section stats                 # Just table stats")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
