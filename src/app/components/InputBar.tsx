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
      className="bg-transparent relative cursor-text max-w-3xl w-full p-[1px] rounded-4xl overflow-hidden flex flex-col items-center justify-between"
      onClick={handleClick}
    >
        <div className="absolute inset-[-1000%] animate-[spin_2s_linear_infinite] bg-[conic-gradient(from_90deg_at_50%_50%,#E2CBFF_0%,#393BB2_50%,#E2CBFF_100%)]" />
        <div className="p-0 relative w-full h-full bg-slate-950 rounded-4xl flex items-center justify-center">
            <div className="gap-1 p-2 h-full w-full bg-transparent rounded-3xl flex flex-col items-center justify-between">
                <textarea
                    ref={inputbarRef}
                    className="rounded-4xl  flex-grow overflow-y-auto max-h-40 w-full p-2 bg-transparent text-white border-none focus:outline-none resize-none"
                    placeholder="Type your message here..."
                    onKeyDown={handleKeyDown}
                />
                <BarTools onSend={handleSend}/>
            </div>
        </div>
    </div>
  )
}

export default InputBar
