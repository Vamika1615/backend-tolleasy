import os
import sqlite3
import datetime
from database import SessionLocal

def export_database_to_sql():
    """
    Export the in-memory SQLite database to a SQL file for backup
    """
    # Create a directory for exports if it doesn't exist
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # Create a filename with the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = os.path.join(export_dir, f"tolleasy_dump_{timestamp}.sql")
    
    # Get the SQLite database file path from connection string
    # Note: For in-memory database, we'll create a temp file
    db_file = "temp_db.sqlite"

    try:
        # Get a database session and connection info
        db = SessionLocal()
        db_url = db.bind.url
        db.close()
        
        # For in-memory database, we need to create a temp file
        conn = sqlite3.connect(db_file)
        
        # Execute the dump command
        with open(export_file, 'w') as f:
            for line in conn.iterdump():
                f.write(f"{line}\n")
        
        # Close connection
        conn.close()
        
        # Remove temporary database file
        if os.path.exists(db_file):
            os.remove(db_file)
        
        print(f"Database exported successfully to {export_file}")
        return f"Database exported successfully to {export_file}"
    except Exception as e:
        print(f"Error exporting database: {e}")
        return f"Error exporting database: {e}"

if __name__ == "__main__":
    export_database_to_sql() 