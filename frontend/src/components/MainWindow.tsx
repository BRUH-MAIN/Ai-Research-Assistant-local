import TopBar from '../components/TopBar'
import InputBar from "../components/InputBar"
import useHandleInput from '../hooks/useHandleInput'
import Chat from './Chat';  
import { useState, useEffect } from 'react';

function MainWindow() {
  const { messages, onSendMessage } = useHandleInput();
  const [isChatVisible, setIsChatVisible] = useState(false);

  useEffect(() => {
    if (messages.length > 0 && !isChatVisible) {
      const timer = setTimeout(() => {
        setIsChatVisible(true);
      }, 500); // 500ms delay
      return () => clearTimeout(timer);
    }
  }, [messages, isChatVisible]);

  return (
    <div className="bg-transparent h-screen w-full flex flex-col items-center">
      <TopBar />
      {isChatVisible && <div className='flex-1 w-full flex items-start pt-4 justify-center overflow-y-auto'>
        <Chat messages={messages} />
      </div>}
      <div className={`flex items-center justify-center w-full translation-transformation duration-200 ease-in-out ${messages.length > 0 ? 'mt-1 mb-5' : 'flex-1'}`}>
        <InputBar onSendMessage={onSendMessage}/>
      </div>
    </div>
  )
}

export default MainWindow
