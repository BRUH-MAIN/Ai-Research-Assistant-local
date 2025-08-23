import { useState } from 'react';
import axios from 'axios';
import type { Message } from '../types/types';

function useHandleInput() {
  const [messages, setMessages] = useState<Message[]>([]);

  const onSendMessage = async (text: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: text,
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      const res = await axios.post('http://localhost:8000/api/chat', {
        prompt: text,
      });

      const aiMessage: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        content: res.data.response,
      };

      setMessages((prevMessages) => [...prevMessages, aiMessage]);
    }
    
    catch(err: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        sender: 'ai',
        content: 'Error: ' + (err.response?.data || err.message),
    }

    setMessages((prevMessages) => [...prevMessages, errorMessage]);
  }


}
return {
    messages,
    onSendMessage,
  };
}

export default useHandleInput
