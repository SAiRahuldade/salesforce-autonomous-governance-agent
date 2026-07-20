# Governor Limit Stress Test Report

## Summary

This report captures a bulk governance run against synthetic data to quantify the performance characteristics of the governance agent pipeline.

| Metric | Result |
| --- | ---: |
| Synthetic Accounts | 5,000 |
| Synthetic Contacts | 5,000 |
| Total execution time | Pending local execution |
| SOQL queries used | Pending local execution |
| CPU time used | Pending local execution |
| DML statements | Pending local execution |
| Governor limits hit | Pending local execution |

## How to Run

1. Install the required dependency:
   ```bash
   pip install simple-salesforce
   ```
2. Populate your local `.env` with Salesforce credentials.
3. Run the data generation script:
   ```bash
   python scripts/generate_bulk_governance_data.py
   ```
4. Execute the batch governance job in your scratch org / sandbox:
   ```apex
   Database.executeBatch(new DuplicateDetectionBatch('Contact'), 200);
   Database.executeBatch(new DuplicateDetectionBatch('Account'), 200);
   ```
5. Capture the debug log and enter the metrics into this table.

## Notes

- The current batch and queueable implementations are already bulkified around batch scopes and avoid obvious SOQL-inside-loops patterns in the Python and Apex code paths.
- The generated data intentionally includes missing required values, malformed emails/phones, and placeholder-like values to stress validation and remediation behavior.
