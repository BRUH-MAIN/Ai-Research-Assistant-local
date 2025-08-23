import React from 'react'

function page() {
  return (
    <div className='flex flex-col gap-10 h-screen items-center justify-center bg-gray-800'>
      
      <div className='w-96  bg-gray-700 shadow-lg p-0 flex flex-col justify-end'>
        <div className="space-y-4">
          {/* User message */}
          <div className="flex justify-end">
            <div className="bg-blue-600 text-white px-4 py-2 rounded-2xl max-w-[75%]">
              Hello, ChatGPT!
            </div>
          </div>

          {/* Bot message */}
          <div className="flex justify-start">
            <div className="bg-transparent text-white px-4 py-2 rounded-2xl rounded-bl-none max-w-[75%]">
              Hi! How can I help you today?
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

export default page
