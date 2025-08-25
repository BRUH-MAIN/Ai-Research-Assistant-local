from db_manager import *
from dotenv import load_dotenv
load_dotenv()

class ChatApp:
    def __init__(self, db: ChatDatabase):
        self.db = db
    
    def start_conversation(self, user_id: str, role: str = 'user') -> str:
        """Start a new conversation"""
        session_id = self.db.create_session()
        self.db.add_participant(session_id, user_id, role)
        return session_id
    
    def join_conversation(self, session_id: str, user_id: str, role: str = 'user') -> str:
        """Join an existing conversation"""
        return self.db.add_participant(session_id, user_id, role)
    
    def send_chat_message(self, session_id: str, user_id: str, message: str, 
                         role: str = 'user', metadata: Optional[Dict] = None) -> str:
        """Send a chat message"""
        return self.db.send_message(session_id, user_id, message, role, metadata)
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        return self.db.get_messages(session_id, limit)

# Usage example
if __name__ == "__main__":
    # Initialize database connection using environment variable
    # Make sure DATABASE_URL is set in your .env file
    # Example: DATABASE_URL=postgresql://username:password@localhost:5432/database_name
    db = ChatDatabase()
    
    # Or you can pass the URL directly
    # db = ChatDatabase("postgresql://username:password@localhost:5432/database_name")
    
    # Initialize chat app
    chat_app = ChatApp(db)
    
    # Example usage
    try:
        # Start a new conversation
        session_id = chat_app.start_conversation(uuid.UUID("user123"), "user")
        print(f"Created session: {session_id}")
        
        # Send some messages
        msg_id1 = chat_app.send_chat_message(session_id, uuid.UUID("user123"), "Hello, world!")
        msg_id2 = chat_app.send_chat_message(session_id, uuid.UUID("bot456"), "Hi there! How can I help?", "bot")

        # Get conversation history
        history = chat_app.get_conversation_history(session_id)
        for msg in history:
            print(f"[{msg['sender_role']}] {msg['message_text']}")
        
        # Add conversation summary
        db.update_conversation_summary(session_id, "Greeting conversation", ["greeting", "introduction"])
        
        # Get session stats
        stats = db.get_session_stats(session_id)
        print(f"Session stats: {stats}")
        
    except Exception as e:
        print(f"Error: {e}")