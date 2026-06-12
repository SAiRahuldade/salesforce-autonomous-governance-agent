import { useState } from "react";

function RemediationTable({ remediation, onApplyRemediation }) {
  const fixes = remediation?.data?.fixes || [];
  const [applyingIndex, setApplyingIndex] = useState(null);
  const [results, setResults] = useState({});

  const handleApply = async (fix, index) => {
    setApplyingIndex(index);
    setResults((current) => ({
      ...current,
      [index]: { status: "pending", message: "Applying action..." }
    }));

    try {
      const result = await onApplyRemediation(fix);
      setResults((current) => ({ ...current, [index]: result }));
    } catch (err) {
      setResults((current) => ({
        ...current,
        [index]: {
          status: "failed",
          message: formatErrorMessage(err)
        }
      }));
    } finally {
      setApplyingIndex(null);
    }
  };

  const formatErrorMessage = (err) => {
    const detail = err.response?.data?.detail || "";

    if (detail.includes("timed out") || detail.includes("ConnectTimeout")) {
      return "Salesforce timed out. Check your connection or VPN, then try again.";
    }

    return detail || "Failed to apply this action.";
  };

  const statusColor = (status) => {
    if (status === "applied") return "#22c55e";
    if (status === "manual_review_required") return "#f59e0b";
    if (status === "failed") return "#ef4444";
    return "#60a5fa";
  };

  return (
    <div style={{
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "24px"
    }}>
      <h2 style={{ margin: "0 0 16px", fontSize: "16px", color: "#f1f5f9" }}>
        Remediation Recommendations ({fixes.length} fixes)
      </h2>

      {fixes.length === 0 ? (
        <div style={{ color: "#22c55e", padding: "20px", textAlign: "center" }}>
          No fixes required
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              {["Action", "Object", "Record", "Fix", "Priority", "Run", "Status"].map(h => (
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
            {fixes.map((fix, i) => {
              const result = results[i];
              const isApplying = applyingIndex === i;

              return (
                <tr key={i} style={{ borderBottom: "1px solid #0f172a" }}>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      background: fix.action === "MERGE" ? "#4c1d9533" : "#14532d33",
                      color: fix.action === "MERGE" ? "#a78bfa" : "#4ade80",
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: 600
                    }}>{fix.action}</span>
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{fix.object}</td>
                  <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>
                    {fix.record_name || fix.record1_name}
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{fix.fix}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      color: fix.priority === "critical" ? "#ef4444" :
                             fix.priority === "high" ? "#f59e0b" : "#60a5fa",
                      fontWeight: 500
                    }}>{fix.priority}</span>
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <button
                      onClick={() => handleApply(fix, i)}
                      disabled={isApplying}
                      style={{
                        background: fix.safe_to_automate ? "#2563eb" : "#475569",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        cursor: isApplying ? "not-allowed" : "pointer",
                        fontSize: "12px",
                        fontWeight: 600,
                        minWidth: "92px",
                        padding: "7px 10px"
                      }}
                    >
                      {isApplying ? "Running..." : fix.safe_to_automate ? "Apply" : "Review"}
                    </button>
                  </td>
                  <td style={{
                    padding: "10px 12px",
                    color: statusColor(result?.status),
                    maxWidth: "260px"
                  }}>
                    {result?.message || (fix.safe_to_automate ? "Ready" : "Needs review")}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default RemediationTable;
