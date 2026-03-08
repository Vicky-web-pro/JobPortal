"""
Database Migration Script
Updates existing application statuses to new recruitment workflow:
- Pending -> Applied
- Under Review -> Shortlisted
- Accepted -> Selected
- Rejected -> Rejected (unchanged)
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def migrate_statuses():
    """Migrate old status values to new recruitment workflow"""
    
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run the app first to create the database.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current status distribution
    cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
    current_statuses = cursor.fetchall()
    print("\nCurrent status distribution:")
    for status, count in current_statuses:
        print(f"  {status}: {count}")
    
    # Update statuses
    migrations = [
        ('Pending', 'Applied'),
        ('Under Review', 'Shortlisted'),
        ('Accepted', 'Selected'),
        ('Rejected', 'Rejected'),  # Keep as is
    ]
    
    for old_status, new_status in migrations:
        cursor.execute(
            'UPDATE applications SET status = ? WHERE status = ?',
            (new_status, old_status)
        )
        if cursor.rowcount > 0:
            print(f"\nMigrated {cursor.rowcount} applications from '{old_status}' to '{new_status}'")
    
    conn.commit()
    
    # Verify new status distribution
    cursor.execute('SELECT status, COUNT(*) FROM applications GROUP BY status')
    new_statuses = cursor.fetchall()
    print("\nNew status distribution:")
    for status, count in new_statuses:
        print(f"  {status}: {count}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")

if __name__ == '__main__':
    migrate_statuses()

