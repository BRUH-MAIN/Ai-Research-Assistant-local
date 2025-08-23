import TopBar from '../components/TopBar'
import InputBar from "../components/InputBar"
import useHandleInput from '../hooks/useHandleInput'
import Chat from './Chat';  
import { useState, useEffect } from 'react';

function MainWindow() {
  const { messages, onSendMessage, messageBlocks } = useHandleInput();
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
    <div className="rounded-2xl h-full w-full flex flex-col items-center relative bg-gray-950">
      <TopBar />
      {isChatVisible && <div className='flex-1 w-full flex items-start pt-4 justify-center overflow-y-auto pb-50'>
        <Chat messages={messageBlocks} />
      </div>}
      <div className={`z-10 bg-transparent  flex items-center justify-center w-full translation-transformation duration-200 ease-in-out absolute left-0 right-0 ${
        messages.length > 0 
          ? 'bottom-0 mb-5' 
          : 'top-1/2 transform -translate-y-1/2'
      }`}>
        <InputBar onSendMessage={onSendMessage}/>
      </div>
      <div className='absolute bottom-0 max-w-3xl w-full h-11  bg-gray-950 backdrop-blur-sm'/>
    </div>
  )
}

export default MainWindow
