#!/usr/bin/env python3
"""
Test database connection for ESG Sentiment Scorer
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings

def test_database_connection():
    """Test PostgreSQL database connection"""
    
    print("🔍 Testing PostgreSQL Database Connection...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        # Test with SQLAlchemy
        engine = create_engine(settings.database_url)
        
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            
            # Test our tables exist
            result = connection.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"))
            table_count = result.fetchone()[0]
            print(f"✅ Found {table_count} tables in the database")
            
            # Test sample data
            result = connection.execute(text("SELECT COUNT(*) FROM esg_keywords;"))
            keyword_count = result.fetchone()[0]
            print(f"✅ Found {keyword_count} ESG keywords")
            
            result = connection.execute(text("SELECT COUNT(*) FROM news_sources;"))
            source_count = result.fetchone()[0]
            print(f"✅ Found {source_count} news sources")
            
            # Test inserting a sample company
            test_company_query = text("""
                INSERT INTO companies (name, ticker, sector) 
                VALUES ('Test Company Inc.', 'TEST', 'Technology') 
                ON CONFLICT DO NOTHING
                RETURNING id;
            """)
            
            try:
                result = connection.execute(test_company_query)
                connection.commit()
                print("✅ Successfully inserted test company")
            except Exception as e:
                print(f"⚠️  Test company insert: {e}")
            
            # Test querying companies
            result = connection.execute(text("SELECT COUNT(*) FROM companies;"))
            company_count = result.fetchone()[0]
            print(f"✅ Found {company_count} companies in database")
            
    except SQLAlchemyError as e:
        print(f"❌ SQLAlchemy Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False
    
    print("🎉 Database connection test completed successfully!")
    return True

def test_psycopg2_connection():
    """Test direct psycopg2 connection"""
    print("\n🔍 Testing direct psycopg2 connection...")
    
    try:
        # Parse connection parameters from URL
        import urllib.parse
        
        url_parts = urllib.parse.urlparse(settings.database_url)
        
        conn = psycopg2.connect(
            host=url_parts.hostname or 'localhost',
            port=url_parts.port or 5432,
            database=url_parts.path[1:],  # Remove leading '/'
            user=url_parts.username,
            password=url_parts.password
        )
        
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user;")
        db_name, user_name = cur.fetchone()
        
        print(f"✅ Connected to database '{db_name}' as user '{user_name}'")
        
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ psycopg2 Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def main():
    """Run all database tests"""
    print("=" * 50)
    print("🌍 ESG Sentiment Scorer Database Tests")
    print("=" * 50)
    
    success1 = test_database_connection()
    success2 = test_psycopg2_connection()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All database tests passed! Your scraper should work now.")
        print("💡 You can now run your news scraper to populate the database.")
    else:
        print("❌ Some tests failed. Please check your database configuration.")
    print("=" * 50)

if __name__ == "__main__":
    main()
