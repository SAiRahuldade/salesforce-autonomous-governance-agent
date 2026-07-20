import { useState } from "react";
import axios from "axios";
import Dashboard from "./components/Dashboard";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/analyze/full`);
      setReport(response.data.report);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        detail
          ? `Backend error: ${detail}`
          : "Failed to connect to backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const applyRemediation = async (fix) => {
    const response = await axios.post(`${API_URL}/remediation/apply`, { fix });
    return response.data;
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f172a",
      color: "#f1f5f9",
      fontFamily: "'Inter', sans-serif"
    }}>
      {/* HEADER */}
      <div style={{
        background: "#1e293b",
        borderBottom: "1px solid #334155",
        padding: "16px 32px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "20px", fontWeight: 600, color: "#f1f5f9" }}>
            🛡️ Salesforce Data Governance Agent
          </h1>
          <p style={{ margin: 0, fontSize: "12px", color: "#94a3b8" }}>
            Powered by AMD MI300X + Multi-Agent AI
          </p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={loading}
          style={{
            background: loading ? "#334155" : "#3b82f6",
            color: "white",
            border: "none",
            padding: "10px 24px",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "14px",
            fontWeight: 500
          }}
        >
          {loading ? "⏳ Analyzing..." : "🚀 Run Analysis"}
        </button>
      </div>

      {/* CONTENT */}
      <div style={{ padding: "32px" }}>
        {error && (
          <div style={{
            background: "#7f1d1d",
            border: "1px solid #ef4444",
            borderRadius: "8px",
            padding: "16px",
            marginBottom: "24px"
          }}>
            ❌ {error}
          </div>
        )}

        {!report && !loading && (
          <div style={{
            textAlign: "center",
            padding: "80px",
            color: "#64748b"
          }}>
            <div style={{ fontSize: "64px", marginBottom: "16px" }}>🔍</div>
            <h2 style={{ color: "#94a3b8" }}>Ready to analyze your Salesforce org</h2>
            <p>Click "Run Analysis" to start all 5 AI agents</p>
          </div>
        )}

        {report && <Dashboard report={report} onApplyRemediation={applyRemediation} />}
      </div>
    </div>
  );
}

export default App;
