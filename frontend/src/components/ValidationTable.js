function ValidationTable({ validation }) {
  const issues = validation?.data?.issues || [];

  return (
    <div style={{
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "24px"
    }}>
      <h2 style={{ margin: "0 0 16px", fontSize: "16px", color: "#f1f5f9" }}>
        ❌ Validation Issues ({issues.length} found)
      </h2>

      {issues.length === 0 ? (
        <div style={{ color: "#22c55e", padding: "20px", textAlign: "center" }}>
          ✅ All records pass validation
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              {["Object", "Record", "Field", "Issue", "Severity"].map(h => (
                <th key={h} style={{
                  textAlign: "left",
                  padding: "8px 12px",
                  color: "#64748b",
                  fontWeight: 500
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {issues.map((issue, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #0f172a" }}>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    background: "#33415533",
                    color: "#94a3b8",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "11px"
                  }}>{issue.object}</span>
                </td>
                <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>{issue.record_name}</td>
                <td style={{ padding: "10px 12px", color: "#60a5fa" }}>{issue.field}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{issue.issue}</td>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    background: issue.severity === 'critical' ? "#7f1d1d" : "#78350f",
                    color: issue.severity === 'critical' ? "#ef4444" : "#f59e0b",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "11px",
                    fontWeight: 500
                  }}>{issue.severity}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default ValidationTable;