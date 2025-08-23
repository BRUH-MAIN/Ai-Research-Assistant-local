import SideBarExpandIcon from "../assets/SideBarExpand"

type SideNavProps = {
  toggleSidenav?: () => void;
}

function SideNav({toggleSidenav }: SideNavProps) {
  return (
    <div className="h-screen bg-transparent flex flex-col items-center justify-start p-5">
      <button className="cursor-pointer w-10 h-10 hover:bg-gray-700 flex items-center justify-center rounded-xl" onClick={toggleSidenav}>
        <SideBarExpandIcon className="w-8 h-8 text-gray-400"/>
      </button>
    </div>
  )
}

export default SideNav
