import React from 'react'

function page() {
  return (
    <div className="min-h-screen bg-gray-950">
      {/* Top navigation with sign up and login buttons */}
      <nav className="flex justify-end p-6">
        <div className="space-x-4">
          <button className="px-6 py-2 text-white bg-transparent border-2 border-white">
            Sign Up
          </button>
          <button className="px-6 py-2 text-black bg-white border-2 border-white">
            Login
          </button>
        </div>
      </nav>

      {/* Center content with app name and catchphrase */}
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)] px-4 ">
        <div className="text-center border-2 border-white p-12">
          <h1 className="text-6xl md:text-7xl text-gray-800 dark:text-white mb-6 tracking-tight">
            AI Research
            <span className="block text-white">
              Assistant
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Unlock the power of intelligent research with AI-driven insights and seamless knowledge discovery
          </p>
        </div>
      </div>
    </div>
  )
}

export default page