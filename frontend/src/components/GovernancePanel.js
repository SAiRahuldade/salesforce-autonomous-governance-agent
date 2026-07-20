function GovernancePanel({ governance, summaryMetrics }) {
  const score = governance?.data?.health_score || 0;
  const grade = governance?.summary?.health_grade || 'N/A';
  const recommendations = governance?.data?.recommendations || [];
  const stats = governance?.data?.org_stats || {};

  const scoreColor = score >= 90 ? "#22c55e" : score >= 75 ? "#f59e0b" : "#ef4444";

  const criticalCount = summaryMetrics?.critical_count ?? 0;
  const pendingCount = summaryMetrics?.pending_approval_count ?? 0;
  const approvedCount = summaryMetrics?.approved_count ?? 0;

  return (
    <div style={{
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "24px"
    }}>
      <h2 style={{ margin: "0 0 20px", fontSize: "16px", color: "#f1f5f9" }}>
        📊 Governance Health Overview
      </h2>

      <div style={{ display: "grid", gridTemplateColumns: "200px 1fr", gap: "32px" }}>

        {/* SCORE CIRCLE */}
        <div style={{ textAlign: "center" }}>
          <div style={{
            width: "140px",
            height: "140px",
            borderRadius: "50%",
            border: `8px solid ${scoreColor}`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            margin: "0 auto"
          }}>
            <div style={{ fontSize: "40px", fontWeight: 700, color: scoreColor }}>{score}</div>
            <div style={{ fontSize: "14px", color: "#94a3b8" }}>Grade {grade}</div>
          </div>
          <div style={{ marginTop: "12px", fontSize: "13px", color: "#64748b" }}>
            Overall Health Score
          </div>

          {/* ── Summary pill row ── */}
          {summaryMetrics && (
            <div style={{ marginTop: "16px", display: "flex", flexDirection: "column", gap: "6px", alignItems: "center" }}>
              <div style={{
                background: criticalCount > 0 ? "#7f1d1d" : "#1e293b",
                border: `1px solid ${criticalCount > 0 ? "#ef4444" : "#334155"}`,
                borderRadius: "9999px",
                padding: "4px 12px",
                fontSize: "12px",
                fontWeight: 600,
                color: criticalCount > 0 ? "#ef4444" : "#64748b",
                minWidth: "140px"
              }}>
                🚨 {criticalCount} Critical
              </div>
              <div style={{
                background: pendingCount > 0 ? "#713f12" : "#1e293b",
                border: `1px solid ${pendingCount > 0 ? "#f59e0b" : "#334155"}`,
                borderRadius: "9999px",
                padding: "4px 12px",
                fontSize: "12px",
                fontWeight: 600,
                color: pendingCount > 0 ? "#f59e0b" : "#64748b",
                minWidth: "140px"
              }}>
                ⏳ {pendingCount} Pending Approval
              </div>
              <div style={{
                background: "#14532d",
                border: "1px solid #22c55e44",
                borderRadius: "9999px",
                padding: "4px 12px",
                fontSize: "12px",
                fontWeight: 600,
                color: "#4ade80",
                minWidth: "140px"
              }}>
                ✅ {approvedCount} Approved
              </div>
            </div>
          )}
        </div>

        {/* STATS + RECOMMENDATIONS */}
        <div>
          {/* ORG STATS */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "12px",
            marginBottom: "20px"
          }}>
            {Object.entries(stats).map(([key, value]) => (
              <div key={key} style={{
                background: "#0f172a",
                borderRadius: "8px",
                padding: "12px"
              }}>
                <div style={{ fontSize: "20px", fontWeight: 600, color: "#3b82f6" }}>{value}</div>
                <div style={{ fontSize: "11px", color: "#64748b" }}>
                  {key.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </div>

          {/* RECOMMENDATIONS */}
          <div>
            {recommendations.map((rec, i) => (
              <div key={i} style={{
                background: "#0f172a",
                borderRadius: "8px",
                padding: "12px",
                marginBottom: "8px",
                borderLeft: `3px solid ${rec.priority === 'critical' ? '#ef4444' : rec.priority === 'high' ? '#f59e0b' : '#3b82f6'}`
              }}>
                <div style={{ fontSize: "13px", color: "#f1f5f9", fontWeight: 500 }}>
                  {rec.recommendation}
                </div>
                <div style={{ fontSize: "11px", color: "#64748b", marginTop: "4px" }}>
                  {rec.business_impact} • {rec.affected_records} records affected
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default GovernancePanel;