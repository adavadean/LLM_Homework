import React, { useState } from 'react'
import ChatBox from './components/ChatBox'
import RecommendationCard from './components/RecommendationCard'

export default function App() {
  const [data, setData] = useState<any | null>(null)

  return (
    <div style={{ maxWidth: 900, margin: '40px auto', padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1>📚 Smart Librarian</h1>
      <p>Scrie ce te interesează (ex: <i>Vreau o carte despre prietenie și magie</i>).</p>
      <ChatBox onResult={setData} />
      {data && <RecommendationCard data={data} />}
    </div>
  )
}
