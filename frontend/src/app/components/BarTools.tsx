import UploadButton from "../assets/UploadButton"
import SendButton from "../assets/SendButton"

type BarToolsProps = {
  onSend?: () => void;
  disabled?: boolean;
}

function BarTools({ onSend, disabled = false }: BarToolsProps) {
  return (
    <div className="rounded-4xl bg-transparent w-full p-1 flex justify-between">
      <button 
        className={`cursor-pointer h-10 w-10 rounded-4xl bg-transparent flex items-center justify-center ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-800'
        }`}
        disabled={disabled}
      >
        <UploadButton className="h-5 w-5 text-gray-500"/>
      </button>
      <button 
        className={`cursor-pointer h-10 w-10 rounded-4xl bg-transparent flex items-center justify-center ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-800'
        }`}
        onClick={disabled ? undefined : onSend}
        disabled={disabled}
      >
        <SendButton className="h-9 w-9 text-gray-500"/>
      </button>
    </div>
  )
}

export default BarTools
