"""
Configuration and setup verification script
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_configuration():
    """Check if all required configuration is present"""
    print("🔍 Checking Configuration")
    print("=" * 40)
    
    required_vars = [
        "REDIS_HOST",
        "REDIS_PORT", 
        "REDIS_USERNAME",
        "REDIS_PASSWORD",
        "REDIS_SESSION_TTL_HOURS"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print sensitive values like passwords
            if "PASSWORD" in var:
                print(f"✅ {var}: *** (set)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nPlease create a .env file with the following variables:")
        for var in missing_vars:
            print(f"{var}=your_value_here")
        return False
    else:
        print("✅ All configuration variables are set!")
        return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n🐍 Checking Dependencies")
    print("=" * 40)
    
    required_packages = [
        "fastapi",
        "redis", 
        "sqlalchemy",
        "psycopg2",
        "pydantic",
        "uvicorn"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "psycopg2":
                import psycopg2
            else:
                __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\nInstall them with:")
        print("pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required packages are installed!")
        return True

def check_database_connections():
    """Test database connections"""
    print("\n🔗 Testing Database Connections")
    print("=" * 40)
    
    # Test Redis connection
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.db.redis_client import redis_client
        
        if redis_client.is_connected():
            print("✅ Redis: Connected")
            redis_ok = True
        else:
            print("❌ Redis: Connection failed")
            redis_ok = False
    except Exception as e:
        print(f"❌ Redis: Error - {e}")
        redis_ok = False
    
    # Test PostgreSQL connection (if configured)
    try:
        from app.db.postgres_manager.db import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ PostgreSQL: Connected")
        pg_ok = True
    except Exception as e:
        print(f"❌ PostgreSQL: Error - {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is configured")
        pg_ok = False
    
    return redis_ok and pg_ok

if __name__ == "__main__":
    print("🚀 Redis-PostgreSQL Sync Setup Verification")
    print("=" * 50)
    
    config_ok = check_configuration()
    deps_ok = check_dependencies() 
    db_ok = check_database_connections()
    
    print("\n📋 Summary")
    print("=" * 20)
    
    if config_ok and deps_ok and db_ok:
        print("🎉 All checks passed! You're ready to run the sync service.")
        print("\nTo start the application:")
        print("  cd backend && uvicorn app.main:app --reload")
        print("\nTo test the sync:")
        print("  cd backend && python test_sync.py")
    else:
        print("❌ Some checks failed. Please fix the issues above before proceeding.")
        
        if not config_ok:
            print("  - Fix configuration issues")
        if not deps_ok:
            print("  - Install missing dependencies")
        if not db_ok:
            print("  - Check database connections")
