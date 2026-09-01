import RiskBadge from './RiskBadge'

export default function AIRecommendation({ recommendation }) {
  if (!recommendation) return <div className="subtle-panel"><p className="muted">Analyze this transaction to generate a recommendation.</p></div>
  return <div className="recommendation"><div className="recommendation-head"><div><span className="eyebrow">AI recommendation</span><h3>{recommendation.recommended_action.replaceAll('_', ' ')}</h3></div><RiskBadge value={recommendation.risk_level} /></div><p>{recommendation.diagnosis}</p><div className="recommendation-grid"><div><span>Risk score</span><strong>{recommendation.risk_score.toFixed(2)}</strong></div><div><span>Recovery probability</span><strong>{Math.round(recommendation.recovery_probability * 100)}%</strong></div><div><span>Confidence</span><strong>{Math.round(recommendation.confidence * 100)}%</strong></div><div><span>Approval</span><strong>{recommendation.requires_human_approval ? 'Required' : 'Not required'}</strong></div></div><div className="reasoning"><span>Decision factors</span><p>{recommendation.reasoning}</p></div></div>
}
