"""
Populate the companies table from config.companies.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.db.models import get_database_session, Company
from config.companies import COMPANIES

def main():
    session = get_database_session()
    for c in COMPANIES:
        company = Company(
            name=c["name"],
            ticker=c["ticker"],
            sector=c["sector"],
            country=c.get("region", "Unknown")
        )
        session.add(company)
    session.commit()
    print(f"Inserted {len(COMPANIES)} companies.")
    session.close()

if __name__ == "__main__":
    main()
