function StatCard({ title, value, subtitle, color, icon }) {
  return (
    <div style={{
      background: "#1e293b",
      border: `1px solid ${color}33`,
      borderRadius: "12px",
      padding: "20px",
      borderLeft: `4px solid ${color}`
    }}>
      <div style={{ fontSize: "28px", marginBottom: "4px" }}>{icon}</div>
      <div style={{ fontSize: "32px", fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: "14px", color: "#f1f5f9", fontWeight: 500 }}>{title}</div>
      <div style={{ fontSize: "12px", color: "#64748b", marginTop: "4px" }}>{subtitle}</div>
    </div>
  );
}

function StatCards({ report }) {
  const dup = report.duplicate_detection?.summary || {};
  const val = report.data_validation?.summary || {};
  const comp = report.compliance?.summary || {};
  const gov = report.governance?.summary || {};
  const rem = report.remediation?.summary || {};

  const govIssuesCount = report.governance_issues?.data?.issues?.length || 0;
  const govCritical = report.governance_issue_counts?.critical || 0;
  const govPending = report.governance_approval_counts?.pending_approval || 0;

  // Combined aggregate metrics from backend summary_metrics
  const metrics = report.summary_metrics || {};
  const combinedCritical = metrics.critical_count ?? (
    (val.critical || 0) + (comp.critical || 0) + govCritical
  );
  const pendingApproval = metrics.pending_approval_count ?? govPending;
  const approvedCount = metrics.approved_count ?? 0;

  return (
    <div>
      {/* ── Top summary row: critical & approval counts ── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
        gap: "16px",
        marginBottom: "16px"
      }}>
        <StatCard
          icon="🚨"
          title="Critical Issues"
          value={combinedCritical}
          subtitle="Combined across all agents & governance"
          color="#ef4444"
        />
        <StatCard
          icon="⏳"
          title="Pending Approval"
          value={pendingApproval}
          subtitle={`${approvedCount} already approved`}
          color="#f59e0b"
        />
      </div>

      {/* ── Main stat cards grid ── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
        gap: "16px",
        marginBottom: "24px"
      }}>
        <StatCard
          icon="⚠️"
          title="Duplicates Found"
          value={dup.total_duplicates_found || 0}
          subtitle={`${dup.account_duplicates || 0} accounts, ${dup.contact_duplicates || 0} contacts`}
          color="#f59e0b"
        />
        <StatCard
          icon="❌"
          title="Validation Issues"
          value={val.total_issues || 0}
          subtitle={`${val.critical || 0} critical, ${val.warnings || 0} warnings`}
          color="#ef4444"
        />
        <StatCard
          icon="📋"
          title="Compliance Violations"
          value={comp.total_violations || 0}
          subtitle={`${comp.critical || 0} critical, ${comp.warnings || 0} warnings`}
          color="#8b5cf6"
        />
        <StatCard
          icon="💚"
          title="Health Score"
          value={`${gov.health_score || 0}`}
          subtitle={`Grade: ${gov.health_grade || 'N/A'}`}
          color="#22c55e"
        />
        <StatCard
          icon="🔧"
          title="Fixes Recommended"
          value={rem.total_fixes || 0}
          subtitle={`${rem.manual_review || 0} need manual review`}
          color="#3b82f6"
        />
        <StatCard
          icon="⚖️"
          title="Native Governance"
          value={govIssuesCount}
          subtitle={`${govCritical} critical, ${govPending} pending approval`}
          color="#fb7185"
        />
      </div>
    </div>
  );
}

export default StatCards;