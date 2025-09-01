import React from 'react'

export default function RecommendationCard({ data }: { data: any }) {
  if (data?.error) {
    return <div style={{ marginTop: 24, color: 'crimson' }}>Eroare: {String(data.error)}</div>
  }
  return (
    <div style={{ marginTop: 24, border: '1px solid #eee', borderRadius: 12, padding: 16 }}>
      <h2 style={{ marginTop: 0 }}>Recomandare: {data.recommendation_title}</h2>
      <p><b>De ce:</b> {data.rationale}</p>
      <p><b>Rezumat detaliat:</b> {data.detailed_summary}</p>
      {Array.isArray(data?.hits) && data.hits.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <b>Top potriviri (RAG):</b>
          <ul>
            {data.hits.map((h: any, idx: number) => (
              <li key={idx}>
                <b>{h.title}</b> — scor: {h.score.toFixed(2)}; taguri: {(h.tags || []).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}
      {Array.isArray(data?.used_tools) && data.used_tools.length > 0 && (
        <p style={{ opacity: 0.7 }}><i>Tools folosite: {data.used_tools.join(', ')}</i></p>
      )}
    </div>
  )
}
