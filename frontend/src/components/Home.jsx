import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Search, Sparkles, ArrowRight, Github, Linkedin, BrainCircuit, Workflow } from 'lucide-react';
import CodeBackground from './CodeBackground';

const Home = () => {
  return (
    <div className="home-layout">
      <CodeBackground />
      <h3 className="top-right-header"> Scam Undoo?  </h3>
      {/* Main Content Area */}
      <main className="home-main">
        <div className="clean-card">
          <div className="badge">
            <Sparkles size={16} />
            <span>AI POWERED</span>
          </div>
          
          <div className="card-icon">
            <div className="shield-outline">
              <Search size={32} />
            </div>
          </div>

          <h1>URL Phishing Detection System</h1>
          
          <div className="separator"></div>

          <p>
            Detect phishing URLs in real-time using advanced
            machine learning models. Stay safe while browsing
            and protect yourself from online threats.
          </p>

          <Link to="/dashboard" className="btn-black">
            Start Scan <ArrowRight size={18} />
          </Link>
        </div>
      </main>

      {/* Info Section */}
      <section className="info-section">
        <div className="info-box">
          <div className="info-box-header">
            <div className="info-box-icon">
              <BrainCircuit size={22} />
            </div>
            <h3>Model Algorithm</h3>
          </div>
          <p className="info-box-text">
            Scam Undoo uses <strong>XGBoost</strong> (Extreme Gradient Boosting),
            an ensemble learning algorithm that combines hundreds of weak decision
            trees into a single powerful classifier. Each tree is trained
            sequentially to correct the mistakes of the previous ones, so the
            ensemble converges on highly accurate predictions.
          </p>
          <ul className="info-list">
            <li>
              <strong>Input:</strong> 17 numeric features extracted from the URL,
              including length, digits, special characters, IP host, HTTPS,
              domain age, TLD reputation, hostname entropy, suspicious keywords,
              and brand keywords.
            </li>
            <li>
              <strong>Prediction:</strong> the model outputs the probability that
              the URL is phishing, which is converted into a threat category and
              a confidence score.
            </li>
            <li>
              <strong>Explainability:</strong> each prediction is accompanied by a
              breakdown of the features that increased or decreased the risk.
            </li>
          </ul>
        </div>

        <div className="info-box">
          <div className="info-box-header">
            <div className="info-box-icon">
              <Workflow size={22} />
            </div>
            <h3>Detection Workflow</h3>
          </div>
          <ol className="info-list steps">
            <li>
              <strong>URL Input</strong> — you submit a URL in the scanner dashboard.
            </li>
            <li>
              <strong>Feature Extraction</strong> — the backend parses the URL and
              computes 17 features combining lexical signals with domain age and
              TLD reputation.
            </li>
            <li>
              <strong>Model Prediction</strong> — the trained XGBoost model scores the
              feature vector and outputs a phishing probability.
            </li>
            <li>
              <strong>Classification</strong> — the probability is mapped to a threat
              category (<em>Legitimate</em> or <em>High Threat</em>) with a confidence
              score.
            </li>
            <li>
              <strong>Explanation</strong> — the backend identifies which features most
              influenced the prediction.
            </li>
            <li>
              <strong>Result Display</strong> — the dashboard renders the category,
              confidence, extracted features, and explanation.
            </li>
          </ol>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-left">
          <div className="footer-logo">
            <ShieldCheck size={24} strokeWidth={2} />
            <span>Scam Undoo</span>
          </div>
          <p>Stay safe. Browse smart.</p>
        </div>

        <div className="footer-right">
          <p className="copyright-text">&copy; 2026 Scam Undoo. All rights reserved.</p>
          <div className="developer-info">
            <p>Meet the developer <strong>Deon George</strong></p>
            <div className="social-links">
              <a href="https://github.com/deon-george" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                <Github size={20} />
              </a>
              <a href="https://www.linkedin.com/in/deon-george-vadakkel/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <Linkedin size={20} />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home;
