import UploadButton from "../assets/UploadButton"
import SendButton from "../assets/SendButton"

type BarToolsProps = {
  onSend?: () => void;
}

function BarTools({ onSend }: BarToolsProps) {
  return (
    <div className="bg-transparent w-full p-1 flex justify-between">
      <button 
        className="cursor-pointer h-12 w-12 rounded-2xl bg-transparent hover:bg-sky-700 flex items-center justify-center"
      >
        <UploadButton className="h-7 w-7 text-gray-400"/>
      </button>
      <button 
        className="cursor-pointer h-12 w-12 rounded-2xl bg-transparent hover:bg-sky-700 flex items-center justify-center"
        onClick={onSend}
      >
        <SendButton className="h-13 w-13 text-gray-400"/>
      </button>
    </div>
  )
}

export default BarTools
