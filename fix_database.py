import sqlite3

DB_PATH = 'database.db'

def fix_applications_table():
    """Add missing columns to applications table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute('PRAGMA table_info(applications)')
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns: {columns}")
    
    # Add user_id column if not exists
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE applications ADD COLUMN user_id INTEGER')
        print("✓ Added user_id column")
    else:
        print("✓ user_id column already exists")
    
    # Add company_name column if not exists
    if 'company_name' not in columns:
        cursor.execute('ALTER TABLE applications ADD COLUMN company_name TEXT')
        print("✓ Added company_name column")
    else:
        print("✓ company_name column already exists")
    
    # Add status column if not exists
    if 'status' not in columns:
        cursor.execute("ALTER TABLE applications ADD COLUMN status TEXT DEFAULT 'Pending'")
        print("✓ Added status column")
    else:
        print("✓ status column already exists")
    
    conn.commit()
    
    # Verify final structure
    cursor.execute('PRAGMA table_info(applications)')
    print(f"\nUpdated columns:")
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")
    
    conn.close()
    print("\n✅ Database schema fixed successfully!")

if __name__ == "__main__":
    fix_applications_table()

