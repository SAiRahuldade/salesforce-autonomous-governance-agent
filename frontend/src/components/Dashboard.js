import StatCards from "./StatCards";
import RecordsTable from "./RecordsTable";
import GovernanceIssuesTable from "./GovernanceIssuesTable";
import DuplicatesTable from "./DuplicatesTable";
import ValidationTable from "./ValidationTable";
import GovernancePanel from "./GovernancePanel";
import RemediationTable from "./RemediationTable";

function Dashboard({ report, onApplyRemediation }) {
  return (
    <div>
      {/* STAT CARDS */}
      <StatCards report={report} />

      {/* SOURCE RECORDS */}
      <RecordsTable records={report.source_records} />

      {/* GOVERNANCE ISSUES */}
      <GovernanceIssuesTable governanceIssues={report.governance_issues} />

      {/* GOVERNANCE HEALTH */}
      <GovernancePanel governance={report.governance} summaryMetrics={report.summary_metrics} />

      {/* DUPLICATES */}
      <DuplicatesTable duplicates={report.duplicate_detection} />

      {/* VALIDATION ISSUES */}
      <ValidationTable validation={report.data_validation} />

      {/* REMEDIATION */}
      <RemediationTable
        remediation={report.remediation}
        governanceIssues={report.governance_issues}
        onApplyRemediation={onApplyRemediation}
      />
    </div>
  );
}

export default Dashboard;
