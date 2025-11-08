#!/usr/bin/env python3
"""
Clear all sessions from the VIRA database.

This script deletes all sessions, messages, business plans, and analyses
from the database. Use with caution as this operation cannot be undone.

Usage:
    python scripts/clear_sessions.py
    python scripts/clear_sessions.py --confirm  # Skip confirmation prompt
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path so we can import vira modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vira.ui.database.models import Analysis, BusinessPlan, Message, Session


def clear_all_sessions(db_url: str = "sqlite:///./data/vira_sessions.db", skip_confirm: bool = False) -> None:
    """
    Delete all sessions and related data from the database.
    
    Args:
        db_url: Database connection URL
        skip_confirm: If True, skip confirmation prompt
    """
    # Connect to database
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Count records before deletion
        session_count = db.query(Session).count()
        message_count = db.query(Message).count()
        plan_count = db.query(BusinessPlan).count()
        analysis_count = db.query(Analysis).count()
        
        print(f"\n📊 Current database state:")
        print(f"   Sessions: {session_count}")
        print(f"   Messages: {message_count}")
        print(f"   Business Plans: {plan_count}")
        print(f"   Analyses: {analysis_count}")
        print()
        
        if session_count == 0 and message_count == 0:
            print("✅ Database is already empty. Nothing to delete.")
            return
        
        # Confirmation prompt
        if not skip_confirm:
            response = input("⚠️  Are you sure you want to delete ALL sessions? This cannot be undone. (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ Deletion cancelled.")
                return
        
        # Delete all records (in correct order to handle foreign keys)
        print("\n🗑️  Deleting records...")
        db.query(Analysis).delete()
        db.query(Message).delete()
        db.query(BusinessPlan).delete()
        db.query(Session).delete()
        db.commit()
        
        print("✅ All session data deleted successfully!")
        print()
        print("📊 Final database state:")
        print(f"   Sessions: {db.query(Session).count()}")
        print(f"   Messages: {db.query(Message).count()}")
        print(f"   Business Plans: {db.query(BusinessPlan).count()}")
        print(f"   Analyses: {db.query(Analysis).count()}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clear all sessions from the VIRA database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--db-url",
        default="sqlite:///./data/vira_sessions.db",
        help="Database URL (default: sqlite:///./data/vira_sessions.db)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    args = parser.parse_args()
    
    print("🧹 VIRA Session Cleaner")
    print("=" * 50)
    
    clear_all_sessions(db_url=args.db_url, skip_confirm=args.confirm)


if __name__ == "__main__":
    main()

