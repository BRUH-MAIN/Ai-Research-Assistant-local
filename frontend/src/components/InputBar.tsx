import BarTools from "./BarTools"
import { useEffect, useRef } from "react"

type InputBarProps = {
  onSendMessage?: (message:string) => void;  
}

function InputBar({ onSendMessage }: InputBarProps) {
  const inputbarRef = useRef<HTMLTextAreaElement>(null)

  const handleClick = () => {
    inputbarRef.current?.focus()
  }

  useEffect(() => {
    const textarea = inputbarRef.current;
    if (textarea) {
      textarea.focus();

      const handleInput = () => {
        textarea.style.height = 'auto'; // Reset height
        textarea.style.height = `${textarea.scrollHeight}px`; // Set to scrollHeight
      }
      textarea.addEventListener('input', handleInput);

      // Initial height adjustment
      handleInput();
      return () => {
        textarea.removeEventListener('input', handleInput);
      }
    }
  }, [])

  const handleSend = () => {
    if (inputbarRef.current) {
      const message = inputbarRef.current.value.trim();
      if (message && onSendMessage) {
        onSendMessage(message);
        inputbarRef.current.value = ''; // Clear the input after sending
        inputbarRef.current.style.height = 'auto';
      }
    }
  }

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div 
      className="cursor-text max-w-3xl w-full bg-sky-900 p-3 rounded-3xl flex flex-col items-center justify-between"
      onClick={handleClick}
    >
      <textarea
        ref = {inputbarRef}
        className="flex-grow overflow-y-auto max-h-40 w-full p-2 bg-transparent text-white border-none focus:outline-none rounded resize-none"
        placeholder="Type your message here..."
        onKeyDown={handleKeyDown}
      ></textarea>
      <BarTools onSend={handleSend}/>
    </div>
  )
}

export default InputBar
