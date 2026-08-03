import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Search, Sparkles, ArrowRight, Github, Linkedin } from 'lucide-react';

const Home = () => {
  return (
    <div className="home-layout">
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

          <h1>URL Phishing<br/>Detection System</h1>
          
          <div className="separator"></div>

          <p>
            Detect phishing URLs in real-time using advanced<br/>
            machine learning models. Stay safe while browsing<br/>
            and protect yourself from online threats.
          </p>

          <Link to="/dashboard" className="btn-black">
            Start Scan <ArrowRight size={18} />
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-left">
          <div className="footer-logo">
            <ShieldCheck size={24} strokeWidth={2} />
            <span>PhishGuard</span>
          </div>
          <p>Stay safe. Browse smart.</p>
        </div>

        <div className="footer-right">
          <p className="copyright-text">&copy; 2025 PhishGuard. All rights reserved.</p>
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
