import SideBarCollapseIcon from "../assets/SideBarCollapse"

type SideBarProps = {
  toggleSidebar?: () => void;
}

function SideBar({ toggleSidebar }: SideBarProps) {
  return (
    <div className='bg-gray-900 h-screen w-80 p-5'>
        <div className="flex justify-end">
            <button className="w-10 h-10 hover:bg-gray-700 flex items-center justify-center rounded-xl" onClick={toggleSidebar}>
                <SideBarCollapseIcon className="w-8 h-8 text-gray-400 cursor-pointer"/>
            </button>
        </div>
    </div>
  )
}

export default SideBar
