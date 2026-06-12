function DuplicatesTable({ duplicates }) {
  const accountDupes = duplicates?.data?.account_duplicates || [];
  const contactDupes = duplicates?.data?.contact_duplicates || [];
  const allDupes = [...accountDupes, ...contactDupes];

  return (
    <div style={{
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "24px"
    }}>
      <h2 style={{ margin: "0 0 16px", fontSize: "16px", color: "#f1f5f9" }}>
        ⚠️ Duplicate Records ({allDupes.length} found)
      </h2>

      {allDupes.length === 0 ? (
        <div style={{ color: "#22c55e", padding: "20px", textAlign: "center" }}>
          ✅ No duplicates detected
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              {["Type", "Record 1", "Record 2", "Reason", "Confidence"].map(h => (
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
            {allDupes.map((dup, i) => (
              <tr key={i} style={{ borderBottom: "1px solid #1e293b" }}>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    background: "#1d4ed833",
                    color: "#60a5fa",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "11px"
                  }}>{dup.type}</span>
                </td>
                <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>{dup.record1_name}</td>
                <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>{dup.record2_name}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{dup.reason}</td>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    color: dup.confidence >= 90 ? "#ef4444" : dup.confidence >= 75 ? "#f59e0b" : "#22c55e",
                    fontWeight: 600
                  }}>{dup.confidence}%</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default DuplicatesTable;