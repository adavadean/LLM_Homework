import React, { useState } from 'react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function ChatBox({ onResult }: { onResult: (data: any) => void }) {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [voice, setVoice] = useState(false)

  async function handleAsk() {
    if (!message.trim()) return
    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/chat`, { message })
      onResult(res.data)
      if (voice && 'speechSynthesis' in window) {
        const utter = new SpeechSynthesisUtterance(res.data.detailed_summary || '')
        window.speechSynthesis.speak(utter)
      }
    } catch (e: any) {
      onResult({ error: e?.message || String(e) })
    } finally {
      setLoading(false)
    }
  }

  function handleSTT() {
    const SR = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition
    if (!SR) {
      alert('SpeechRecognition API indisponibilă în acest browser.')
      return
    }
    const recog = new SR()
    recog.lang = 'ro-RO'
    recog.interimResults = false
    recog.maxAlternatives = 1
    recog.onresult = (ev: any) => {
      const t = ev.results[0][0].transcript
      setMessage(t)
    }
    recog.onerror = (e: any) => console.error(e)
    recog.start()
  }

  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 16 }}>
      <input
        value={message}
        onChange={e => setMessage(e.target.value)}
        placeholder="Întreabă despre o carte, o temă sau un gen..."
        style={{ flex: 1, padding: 10, borderRadius: 8, border: '1px solid #ddd' }}
      />
      <button onClick={handleSTT} title="Voice mode (STT)">🎙️</button>
      <label style={{ display: 'flex', alignItems: 'center', gap: 6 }} title="Text-to-Speech">
        <input type="checkbox" checked={voice} onChange={e => setVoice(e.target.checked)} />
        🔊
      </label>
      <button onClick={handleAsk} disabled={loading} style={{ padding: '10px 16px', borderRadius: 8 }}>
        {loading ? 'Caut...' : 'Trimite'}
      </button>
    </div>
  )
}
