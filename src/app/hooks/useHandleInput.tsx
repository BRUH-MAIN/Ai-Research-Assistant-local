import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Message, MessageBlock } from '../types/types';

function useHandleInput() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageBlocks, setMessageBlocks] = useState<MessageBlock[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Initialize session on component mount
  useEffect(() => {
    const initializeSession = async () => {
      try {
        const response = await axios.post('http://localhost:8000/api/chat/sessions');
        setSessionId(response.data.session_id);
        
        // Load existing chat history if any
        const historyResponse = await axios.get(`http://localhost:8000/api/chat/${response.data.session_id}/history`);
        if (historyResponse.data.messages) {
          setMessages(historyResponse.data.messages);
          // Convert to message blocks if needed
        }
      } catch (error) {
        console.error('Failed to initialize chat session:', error);
      }
    };

    initializeSession();
  }, []);

  const onSendMessage = async (text: string) => {
    if (!sessionId) {
      console.error('No active session');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: text,
    };

    const block: MessageBlock = {
      id: Date.now().toString(),
      userMessage: text,
      aiResponse: '',
      timestamp: new Date(),
      isLoading: true,
    };

    // Optimistically update UI
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setMessageBlocks((prevBlocks) => [...prevBlocks, block]);

    try {
      // Send message to session-specific endpoint
      const res = await axios.post(`http://localhost:8000/api/chat/${sessionId}`, {
        id: userMessage.id,
        sender: userMessage.sender,
        content: userMessage.content,
        timestamp: new Date(),
      });

      const aiMessage: Message = {
        id: res.data.aiMessage.id,
        sender: 'ai',
        content: res.data.aiMessage.content,
      };

      // Update both messages and blocks
      setMessages((prevMessages) => [...prevMessages, aiMessage]);
      setMessageBlocks((prevBlocks) => {
        const updatedBlocks = [...prevBlocks];
        const lastBlock = updatedBlocks[updatedBlocks.length - 1];
        if (lastBlock) {
          lastBlock.aiResponse = aiMessage.content;
          lastBlock.isLoading = false;
        }
        return updatedBlocks;
      });

    } catch(err: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        content: 'Error: ' + (err.response?.data?.detail || err.message),
      };

      setMessages((prevMessages) => [...prevMessages, errorMessage]);
      
      // Update the loading state of the last block
      setMessageBlocks((prevBlocks) => {
        const updatedBlocks = [...prevBlocks];
        const lastBlock = updatedBlocks[updatedBlocks.length - 1];
        if (lastBlock) {
          lastBlock.aiResponse = errorMessage.content;
          lastBlock.isLoading = false;
        }
        return updatedBlocks;
      });
    }
  };

  // Function to clear chat history
  const clearChatHistory = async () => {
    if (sessionId) {
      try {
        await axios.delete(`http://localhost:8000/api/chat/${sessionId}`);
        setMessages([]);
        setMessageBlocks([]);
        // Create new session
        const response = await axios.post('http://localhost:8000/api/chat/sessions');
        setSessionId(response.data.session_id);
      } catch (error) {
        console.error('Failed to clear chat history:', error);
      }
    }
  };

  return {
    messages,
    onSendMessage,
    messageBlocks,
    sessionId,
    clearChatHistory,
  };
}

export default useHandleInput
