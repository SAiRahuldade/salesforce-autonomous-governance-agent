import { useState } from "react";

function RemediationTable({ remediation, governanceIssues, onApplyRemediation }) {
  const fixes = remediation?.data?.fixes || [];
  const rawGovIssues = governanceIssues?.data?.issues || governanceIssues?.issues || [];

  // Filter out any issues that are approved
  const unapprovedGovIssues = rawGovIssues.filter(
    (issue) => !(issue.approved === true || issue.Approved__c === true)
  );

  // Map the native issues to match the shape of Python fixes
  const formattedGovIssues = unapprovedGovIssues.map((issue) => {
    const isCriticalOrDupe = (
      (issue.severity || issue.Severity__c || "").toLowerCase() === "critical" ||
      (issue.description || issue.Issue__c || "").toLowerCase() === "duplicate_merge" ||
      (issue.field || issue.Field__c || "").toLowerCase() === "duplicate"
    );
    const safeToAutomate = issue.safe_to_automate !== undefined ? issue.safe_to_automate : !isCriticalOrDupe;

    return {
      isNative: true,
      action: safeToAutomate ? "UPDATE" : "SF APPROVAL",
      object: issue.related_object || issue.Object_Type__c || "-",
      record_id: issue.related_record_id || issue.Record_Id__c || "-",
      record_name: issue.name || issue.Name || "Unnamed Issue",
      field: issue.field || issue.Field__c || "-",
      proposed_value: issue.proposed_value || issue.Proposed_Value__c || "Unknown",
      fix: issue.description || issue.Issue__c || "-",
      priority: (issue.severity || issue.Severity__c || "medium").toLowerCase(),
      approval_status: issue.approval_status || issue.Approval_Status__c || "Pending",
      safe_to_automate: safeToAutomate,
      gov_issue_id: issue.Id || issue.id,
      rawIssue: issue
    };
  });

  // Combine the lists
  const allRows = [...fixes, ...formattedGovIssues];

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

  const statusColor = (status, isNativeGated) => {
    // Only colour gated (SF APPROVAL) rows pink; safe native rows use normal colours
    if (isNativeGated) return "#fb7185";
    if (status === "applied") return "#22c55e";
    if (status === "manual_review_required") return "#f59e0b";
    if (status === "failed") return "#ef4444";
    return "#60a5fa";
  };

  const getStatusMessage = (fix, result, isNativeGated) => {
    // If there is a live result from an apply call, always show it
    if (result?.message) return result.message;
    // Gated native rows: show approval queue status
    if (isNativeGated) return getNativeStatusMessage(fix.approval_status);
    // Safe native rows (warning-level gov issues with Apply button)
    if (fix.isNative && fix.safe_to_automate) return "Ready";
    // Regular Python-agent rows
    return fix.safe_to_automate ? "Ready" : "Needs review";
  };

  const getNativeStatusMessage = (status) => {
    if (!status) return "Pending Approval";
    const statusLower = status.toLowerCase();
    if (statusLower === "submitted") return "Pending Approval in Data Stewards queue";
    if (statusLower === "not submitted" || statusLower === "not_submitted") return "Not submitted to queue";
    return `Approval: ${status}`;
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
        Remediation Recommendations ({allRows.length} fixes)
      </h2>

      {allRows.length === 0 ? (
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
            {allRows.map((fix, i) => {
              const result = results[i];
              const isApplying = applyingIndex === i;
              const isNativeGated = fix.isNative && !fix.safe_to_automate;

              return (
                <tr key={i} style={{
                  borderBottom: "1px solid #0f172a",
                  background: isNativeGated ? "#f43f5e08" : "transparent"
                }}>
                  <td style={{ padding: "10px 12px" }}>
                    {isNativeGated ? (
                      <span style={{
                        background: "#f43f5e22",
                        color: "#fb7185",
                        border: "1px solid #f43f5e44",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        fontSize: "11px",
                        fontWeight: 600
                      }}>{fix.action}</span>
                    ) : (
                      <span style={{
                        background: fix.action === "MERGE" ? "#4c1d9533" : "#14532d33",
                        color: fix.action === "MERGE" ? "#a78bfa" : "#4ade80",
                        padding: "2px 8px",
                        borderRadius: "4px",
                        fontSize: "11px",
                        fontWeight: 600
                      }}>{fix.action}</span>
                    )}
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
                    {isNativeGated ? (
                      <span style={{ color: "#94a3b8", fontStyle: "italic", fontSize: "12px" }}>
                        Salesforce Gated
                      </span>
                    ) : (
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
                    )}
                  </td>
                  <td style={{
                    padding: "10px 12px",
                    color: statusColor(result?.status, isNativeGated),
                    maxWidth: "260px"
                  }}>
                    {getStatusMessage(fix, result, isNativeGated)}
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
