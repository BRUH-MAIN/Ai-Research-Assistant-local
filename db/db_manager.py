import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
import json

class DatabaseHandler:
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 5432):
        """Initialize database connection parameters"""
        self.connection_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.autocommit = True
            print("✅ Database connected successfully")
            return True
        except psycopg2.Error as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("📝 Database connection closed")
    
    def get_cursor(self):
        """Get database cursor with dictionary support"""
        if not self.connection:
            if not self.connect():
                return None
        return self.connection.cursor(cursor_factory=RealDictCursor)
    
    # =========================
    # USER MANAGEMENT
    # =========================
    
    def create_user(self, email: str, password: str, first_name: str = None, 
                   last_name: str = None, role: str = 'scholar') -> Optional[str]:
        """Create a new user and return user_id"""
        try:
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_id = str(uuid.uuid4())
            
            cursor = self.get_cursor()
            cursor.execute("""
                INSERT INTO users (user_id, email, password_hash, first_name, last_name, role, email_verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING user_id
            """, (user_id, email, password_hash, first_name, last_name, role, True))
            
            result = cursor.fetchone()
            cursor.close()
            
            print(f"✅ User created: {email}")
            return result['user_id'] if result else None
            
        except psycopg2.IntegrityError:
            print(f"❌ User with email {email} already exists")
            return None
        except psycopg2.Error as e:
            print(f"❌ Error creating user: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT user_id, email, password_hash, first_name, last_name, role, status
                FROM users 
                WHERE email = %s AND status = 'active'
            """, (email,))
            
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                print("❌ User not found or inactive")
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # Update last login
                self.update_last_login(user['user_id'])
                
                # Return user info without password hash
                user_dict = dict(user)
                del user_dict['password_hash']
                print(f"✅ User authenticated: {email}")
                return user_dict
            else:
                print("❌ Invalid password")
                return None
                
        except psycopg2.Error as e:
            print(f"❌ Error authenticating user: {e}")
            return None
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                UPDATE users 
                SET last_login = NOW() 
                WHERE user_id = %s
            """, (user_id,))
            cursor.close()
        except psycopg2.Error as e:
            print(f"❌ Error updating last login: {e}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user information by user_id"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT user_id, email, first_name, last_name, role, status, created_at, last_login
                FROM users 
                WHERE user_id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            cursor.close()
            
            return dict(user) if user else None
            
        except psycopg2.Error as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    # =========================
    # PROJECT MANAGEMENT
    # =========================
    
    def create_project(self, name: str, description: str, created_by_user_id: str, 
                      is_private: bool = False) -> Optional[str]:
        """Create a new project"""
        try:
            project_id = str(uuid.uuid4())
            
            cursor = self.get_cursor()
            cursor.execute("""
                INSERT INTO projects (project_id, name, description, created_by_user_id, is_private)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING project_id
            """, (project_id, name, description, created_by_user_id, is_private))
            
            result = cursor.fetchone()
            
            # Add creator as owner
            if result:
                cursor.execute("""
                    INSERT INTO project_members (project_id, user_id, role)
                    VALUES (%s, %s, 'owner')
                """, (result['project_id'], created_by_user_id))
            
            cursor.close()
            
            print(f"✅ Project created: {name}")
            return result['project_id'] if result else None
            
        except psycopg2.Error as e:
            print(f"❌ Error creating project: {e}")
            return None
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT p.project_id, p.name, p.description, p.is_private, p.created_at,
                       pm.role as member_role,
                       u.first_name || ' ' || u.last_name as created_by_name
                FROM projects p
                JOIN project_members pm ON p.project_id = pm.project_id
                LEFT JOIN users u ON p.created_by_user_id = u.user_id
                WHERE pm.user_id = %s
                ORDER BY p.created_at DESC
            """, (user_id,))
            
            projects = cursor.fetchall()
            cursor.close()
            
            return [dict(project) for project in projects]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting user projects: {e}")
            return []
    
    # =========================
    # CHAT MANAGEMENT
    # =========================
    
    def create_chat_session(self, user_id: str, project_id: str = None, 
                           title: str = None, model_id: int = 1) -> Optional[str]:
        """Create a new chat session"""
        try:
            session_id = str(uuid.uuid4())
            
            cursor = self.get_cursor()
            cursor.execute("""
                INSERT INTO chat_sessions (session_id, user_id, project_id, title, model_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING session_id
            """, (session_id, user_id, project_id, title, model_id))
            
            result = cursor.fetchone()
            cursor.close()
            
            print(f"✅ Chat session created: {session_id}")
            return result['session_id'] if result else None
            
        except psycopg2.Error as e:
            print(f"❌ Error creating chat session: {e}")
            return None
    
    def add_chat_message(self, session_id: str, role: str, content: str, 
                        metadata: Dict = None) -> Optional[str]:
        """Add a message to chat session"""
        try:
            message_id = str(uuid.uuid4())
            
            cursor = self.get_cursor()
            cursor.execute("""
                INSERT INTO chat_messages (message_id, session_id, role, content, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING message_id
            """, (message_id, session_id, role, content, json.dumps(metadata) if metadata else None))
            
            result = cursor.fetchone()
            cursor.close()
            
            return result['message_id'] if result else None
            
        except psycopg2.Error as e:
            print(f"❌ Error adding chat message: {e}")
            return None
    
    def get_chat_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat messages for a session"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT message_id, role, content, metadata, created_at
                FROM chat_messages 
                WHERE session_id = %s
                ORDER BY created_at ASC
                LIMIT %s
            """, (session_id, limit))
            
            messages = cursor.fetchall()
            cursor.close()
            
            return [dict(message) for message in messages]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting chat messages: {e}")
            return []
    
    def get_user_chat_sessions(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get user's chat sessions"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT cs.session_id, cs.title, cs.status, cs.created_at, cs.updated_at,
                       p.name as project_name,
                       COUNT(cm.message_id) as message_count
                FROM chat_sessions cs
                LEFT JOIN projects p ON cs.project_id = p.project_id
                LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
                WHERE cs.user_id = %s AND cs.status = 'active'
                GROUP BY cs.session_id, cs.title, cs.status, cs.created_at, cs.updated_at, p.name
                ORDER BY cs.updated_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            sessions = cursor.fetchall()
            cursor.close()
            
            return [dict(session) for session in sessions]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting chat sessions: {e}")
            return []
    
    # =========================
    # AI MODELS
    # =========================
    
    def get_available_models(self) -> List[Dict]:
        """Get all active AI models"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT model_id, name, version, description, provider, model_type
                FROM ai_models 
                WHERE is_active = TRUE
                ORDER BY name
            """)
            
            models = cursor.fetchall()
            cursor.close()
            
            return [dict(model) for model in models]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting AI models: {e}")
            return []
    
    # =========================
    # ANALYTICS
    # =========================
    
    def log_usage_event(self, user_id: str, event_type: str, event_data: Dict = None,
                       session_id: str = None, project_id: str = None, 
                       ip_address: str = None, user_agent: str = None):
        """Log a usage analytics event"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                INSERT INTO usage_analytics 
                (user_id, event_type, event_data, session_id, project_id, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, event_type, json.dumps(event_data) if event_data else None,
                  session_id, project_id, ip_address, user_agent))
            
            cursor.close()
            
        except psycopg2.Error as e:
            print(f"❌ Error logging usage event: {e}")
    
    # =========================
    # UTILITY METHODS
    # =========================
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            cursor = self.get_cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except psycopg2.Error as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def get_table_info(self) -> List[Dict]:
        """Get information about all tables"""
        try:
            cursor = self.get_cursor()
            cursor.execute("""
                SELECT table_name, 
                       (SELECT count(*) FROM information_schema.columns 
                        WHERE table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = cursor.fetchall()
            cursor.close()
            
            return [dict(table) for table in tables]
            
        except psycopg2.Error as e:
            print(f"❌ Error getting table info: {e}")
            return []