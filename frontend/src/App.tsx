import { useState } from 'react'
import SideNav from './components/SideNav'
import SideBar from './components/SideBar'  
import MainWindow from './components/MainWindow'  

function App() {
  
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false)
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }
  return (
    <div className='h-screen bg-gray-800 flex '>
      <div 
        className={`transition-transformation duration-400  
        ${!isSidebarOpen ? 'w-16 opacity-100' : 'w-0 opacity-0 overflow-hidden'}`}
      >
        <SideNav toggleSidenav={toggleSidebar}/>
      </div>

      <div
        className={`transition-transformation duration-400  
        ${isSidebarOpen ? 'w-80 opacity-100' : 'w-0 opacity-0 overflow-hidden'}`}
      >
        <SideBar toggleSidebar={toggleSidebar}/>
      </div>
      

      <MainWindow />
    </div>
  )
}

export default App
