import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, ShieldAlert, ShieldCheck, AlertTriangle, ArrowLeft } from 'lucide-react';

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
      const response = await fetch('http://localhost:5000/api/scan', {
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

  return (
    <div className="dashboard-container">
      <Link to="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem' }}>
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
                <h3>{result.category}</h3>
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
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
