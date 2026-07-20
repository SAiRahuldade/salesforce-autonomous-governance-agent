function RecordsTable({ records }) {
  const accounts = records?.accounts || [];
  const contacts = records?.contacts || [];
  const leads = records?.leads || [];

  const rows = [
    ...accounts.map((account) => ({
      id: account.Id,
      type: "Account",
      name: account.Name || "Unnamed Account",
      detail: account.Industry || "No industry",
      phone: account.Phone || "-",
      related: account.BillingCity || "-",
    })),
    ...contacts.map((contact) => ({
      id: contact.Id,
      type: "Contact",
      name: `${contact.FirstName || ""} ${contact.LastName || ""}`.trim() || "Unnamed Contact",
      detail: contact.Email || "No email",
      phone: contact.Phone || "-",
      related: contact.AccountId || "No account",
    })),
    ...leads.map((lead) => ({
      id: lead.Id,
      type: "Lead",
      name: `${lead.FirstName || ""} ${lead.LastName || ""}`.trim() || "Unnamed Lead",
      detail: lead.Email || "No email",
      phone: "-",
      related: lead.Company || "No company",
    })),
  ];

  return (
    <div style={{
      background: "#1e293b",
      border: "1px solid #334155",
      borderRadius: "12px",
      padding: "24px",
      marginBottom: "24px"
    }}>
      <h2 style={{ margin: "0 0 16px", fontSize: "16px", color: "#f1f5f9" }}>
        Salesforce Records ({rows.length} loaded)
      </h2>

      {rows.length === 0 ? (
        <div style={{ color: "#f59e0b", padding: "20px", textAlign: "center" }}>
          No Account, Contact, or Lead records were returned by the backend query
        </div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #334155" }}>
              {["Object", "Name", "Detail", "Phone", "Related", "Salesforce Id"].map((h) => (
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
            {rows.map((row) => (
              <tr key={row.id} style={{ borderBottom: "1px solid #0f172a" }}>
                <td style={{ padding: "10px 12px" }}>
                  <span style={{
                    background: row.type === "Account" ? "#1d4ed833" : row.type === "Contact" ? "#14532d33" : "#78350f33",
                    color: row.type === "Account" ? "#60a5fa" : row.type === "Contact" ? "#4ade80" : "#f59e0b",
                    padding: "2px 8px",
                    borderRadius: "4px",
                    fontSize: "11px"
                  }}>{row.type}</span>
                </td>
                <td style={{ padding: "10px 12px", color: "#f1f5f9" }}>{row.name}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{row.detail}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{row.phone}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{row.related}</td>
                <td style={{ padding: "10px 12px", color: "#64748b", fontFamily: "monospace" }}>{row.id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default RecordsTable;
