import sqlite3

DB_PATH = 'database.db'

def test_my_applications_query():
    """Test the query used in my_applications() route"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Test query with user_id = 1 (simulating logged-in user)
    try:
        cursor.execute('''
            SELECT a.*, j.title as job_title, j.location as job_location, j.salary as job_salary
            FROM applications a
            LEFT JOIN jobs j ON a.job_id = j.id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        ''', (1,))
        results = cursor.fetchall()
        print(f"✅ Query executed successfully! Found {len(results)} applications for user_id=1")
        for row in results:
            print(f"  - {row}")
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")
    
    # Also test with NULL user_id to see existing applications
    cursor.execute('SELECT * FROM applications')
    all_apps = cursor.fetchall()
    print(f"\nAll applications in database: {len(all_apps)}")
    for app in all_apps:
        print(f"  ID: {app[0]}, Name: {app[1]}, user_id: {app[10]}, status: {app[12]}")
    
    conn.close()

if __name__ == "__main__":
    test_my_applications_query()

