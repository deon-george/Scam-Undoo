import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, ShieldAlert, ShieldCheck, AlertTriangle, ArrowLeft, ArrowDownRight, ArrowUpRight, Sparkles } from 'lucide-react';

const ExplanationSection = ({ explanation }) => {
  const maxImpact = Math.max(
    ...explanation.factors.map((factor) => Math.abs(factor.impact))
  );

  return (
    <div className="explanation-section">
      <div className="explanation-header">
        <Sparkles size={18} />
        <h4>Why this prediction?</h4>
      </div>
      <p className="explanation-summary">{explanation.summary}</p>

      <div className="factor-list">
        {explanation.factors.slice(0, 6).map((factor) => {
          const positive = factor.impact >= 0;
          const width = Math.min(
            (Math.abs(factor.impact) / Math.max(maxImpact, 0.0001)) * 100,
            100
          );
          return (
            <div key={factor.feature} className="factor-row">
              <div className="factor-main">
                <div className="factor-info">
                  <span className="factor-label">{factor.label}</span>
                  <span className="factor-value">{factor.value}</span>
                </div>
                <div className="factor-bar-track">
                  <div
                    className={`factor-bar ${positive ? 'risk-up' : 'risk-down'}`}
                    style={{ width: `${width}%` }}
                  ></div>
                </div>
              </div>
              <span className={`factor-impact ${positive ? 'risk-up' : 'risk-down'}`}>
                {positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                {positive ? '+' : ''}
                {factor.impact.toFixed(2)}
              </span>
            </div>
          );
        })}
      </div>

      <div className="explanation-footer">
        <div className="explanation-legend">
          <span>
            <span className="legend-dot risk-up"></span> Increases risk
          </span>
          <span>
            <span className="legend-dot risk-down"></span> Decreases risk
          </span>
        </div>
        <span className="explanation-method">{explanation.method}</span>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const [url, setUrl] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleScan = async (e) => {
    e.preventDefault();
    if (!url) return;

    setIsScanning(true);
    setError(null);
    setResult(null);

    try {
      const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const response = await fetch(`${apiBaseUrl.replace(/\/$/, '')}/api/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to scan URL');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred during scanning');
    } finally {
      setIsScanning(false);
    }
  };

  const getThreatClass = (category) => {
    switch (category) {
      case 'High Threat': return 'high-threat';
      case 'Medium Threat': return 'medium-threat';
      default: return 'legitimate';
    }
  };

  const getThreatIcon = (category) => {
    switch (category) {
      case 'High Threat': return <ShieldAlert size={28} />;
      case 'Medium Threat': return <AlertTriangle size={28} />;
      default: return <ShieldCheck size={28} />;
    }
  };

  const getConfidenceMessage = (confidence) => {
    if (confidence < 0.9) {
      return 'You are safe to browse but be cautious.';
    }
    if (confidence <= 0.95) {
      return 'This site may have serious threats it is recommended not to visit it';
    }
    return "You are at very high risk, don't visit the site.";
  };

  return (
    <div className="dashboard-container">
      <Link to="/" className="back-link">
        <ArrowLeft size={20} /> Back to Home
      </Link>
      
      <div className="dashboard-header">
        <h2>Scanner Dashboard</h2>
        <p>Enter a URL to analyze its threat level using our XGBoost model.</p>
      </div>

      <div className="scanner-box">
        <form onSubmit={handleScan}>
          <div className="input-group">
            <input
              type="url"
              className="url-input"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
            <button type="submit" className="btn-scan" disabled={isScanning || !url}>
              {isScanning ? <div className="loader"></div> : <Search size={20} />}
              {isScanning ? 'Scanning...' : 'Scan URL'}
            </button>
          </div>
        </form>

        {error && (
          <div style={{ color: 'var(--threat-high)', marginTop: '1rem' }}>
            {error}
          </div>
        )}

        {result && (
          <div className={`result-card ${getThreatClass(result.category)}`}>
            <div className="result-header">
              <div className="result-icon">
                {getThreatIcon(result.category)}
              </div>
              <div className="result-title">
                <h3>
                  {result.category === 'High Threat'
                    ? getConfidenceMessage(result.confidence)
                    : result.category}
                </h3>
                <p>{result.url}</p>
              </div>
            </div>

            <p style={{ color: 'var(--text-secondary)' }}>
              Confidence Score: {(result.confidence * 100).toFixed(1)}%
            </p>
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${result.confidence * 100}%` }}
              ></div>
            </div>

            {result.features && (
              <div className="features-grid">
                {Object.entries(result.features).map(([key, value]) => (
                  <div key={key} className="feature-item">
                    <div className="label">{key.replace(/_/g, ' ').toUpperCase()}</div>
                    <div className="value">{value.toString()}</div>
                  </div>
                ))}
              </div>
            )}

            {result.explanation && result.explanation.factors && (
              <ExplanationSection explanation={result.explanation} />
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
