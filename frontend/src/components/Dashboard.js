import StatCards from "./StatCards";
import DuplicatesTable from "./DuplicatesTable";
import ValidationTable from "./ValidationTable";
import GovernancePanel from "./GovernancePanel";
import RemediationTable from "./RemediationTable";

function Dashboard({ report, onApplyRemediation }) {
  return (
    <div>
      {/* STAT CARDS */}
      <StatCards report={report} />

      {/* GOVERNANCE HEALTH */}
      <GovernancePanel governance={report.governance} />

      {/* DUPLICATES */}
      <DuplicatesTable duplicates={report.duplicate_detection} />

      {/* VALIDATION ISSUES */}
      <ValidationTable validation={report.data_validation} />

      {/* REMEDIATION */}
      <RemediationTable
        remediation={report.remediation}
        onApplyRemediation={onApplyRemediation}
      />
    </div>
  );
}

export default Dashboard;
