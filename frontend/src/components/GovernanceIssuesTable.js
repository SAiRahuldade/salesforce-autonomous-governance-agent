function GovernanceIssuesTable({ governanceIssues }) {
  const issues = governanceIssues?.data?.issues || governanceIssues?.issues || [];

  const getSeverityStyle = (severity) => {
    const styles = {
      critical: { background: "#7f1d1d", color: "#ef4444" },
      high: { background: "#7c2d12", color: "#fb923c" },
      medium: { background: "#713f12", color: "#f59e0b" },
      low: { background: "#1e3a5f", color: "#60a5fa" },
    };
    return styles[severity?.toLowerCase()] || styles.medium;
  };

  const getApprovalStatusStyle = (status) => {
    const styles = {
      pending: { background: "#713f12", color: "#f59e0b" },
      approved: { background: "#14532d", color: "#4ade80" },
      approved_automatically: { background: "#14532d", color: "#4ade80" },
      rejected: { background: "#7f1d1d", color: "#ef4444" },
    };
    return styles[status?.toLowerCase()] || styles.pending;
  };

  const formatDate = (dateString) => {
    if (!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
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
        ⚖️ Governance Issues ({issues.length} found)
      </h2>

      {issues.length === 0 ? (
        <div style={{ color: "#f59e0b", padding: "20px", textAlign: "center" }}>
          No governance issues found
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #334155" }}>
                {[
                  "Issue Name",
                  "Severity",
                  "Approval Status",
                  "Approved",
                  "Related Object",
                  "Related Record ID",
                  "Description",
                  "Created Date"
                ].map((h) => (
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
                  <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>
                    {issue.name || issue.Name || "Unnamed Issue"}
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      ...getSeverityStyle(issue.severity || issue.Severity || issue.Severity__c),
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: 500
                    }}>
                      {issue.severity || issue.Severity || issue.Severity__c || "Medium"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px" }}>
                    <span style={{
                      ...getApprovalStatusStyle(issue.approval_status || issue.Approval_Status || issue.Approval_Status__c),
                      padding: "2px 8px",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: 500
                    }}>
                      {issue.approval_status || issue.Approval_Status || issue.Approval_Status__c || "Pending"}
                    </span>
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8" }}>
                    {issue.approved || issue.Approved || issue.Approved__c ? "✓ Yes" : "✗ No"}
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8" }}>
                    {issue.related_object || issue.Related_Object || issue.Object_Type__c || issue.related_object__c || "-"}
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8", fontFamily: "monospace", fontSize: "12px" }}>
                    {issue.related_record_id || issue.Related_Record_ID || issue.Record_Id__c || issue.related_record_id__c || "-"}
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8" }}>
                    {issue.description || issue.Description || issue.Issue__c || "-"}
                  </td>
                  <td style={{ padding: "10px 12px", color: "#94a3b8", fontFamily: "monospace", fontSize: "12px" }}>
                    {formatDate(issue.created_date || issue.Created_Date || issue.CreatedDate)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default GovernanceIssuesTable;