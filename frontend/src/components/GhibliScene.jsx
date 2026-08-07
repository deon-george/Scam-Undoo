import React from 'react';

const Cloud = ({ x, y, scale, className, delay }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`}>
    <g className={className} style={{ animationDelay: delay }}>
      <ellipse cx="0" cy="0" rx="70" ry="28" fill="#f4feff" opacity="0.92" />
      <ellipse cx="48" cy="-10" rx="46" ry="24" fill="#f4feff" opacity="0.95" />
      <ellipse cx="-48" cy="-8" rx="40" ry="20" fill="#f0fdff" opacity="0.9" />
      <ellipse cx="12" cy="-24" rx="42" ry="27" fill="#f4feff" opacity="0.95" />
      <ellipse cx="72" cy="-4" rx="34" ry="18" fill="#f0fdff" opacity="0.9" />
      <ellipse cx="-72" cy="2" rx="30" ry="16" fill="#f0fdff" opacity="0.85" />
      <line x1="-90" y1="28" x2="112" y2="28" stroke="#8fd8f0" strokeWidth="1.5" strokeDasharray="4 6" opacity="0.6" />
      <circle className="ghibli-node" cx="-42" cy="6" r="2.2" fill="#9ff6e8" style={{ animationDelay: '0s' }} />
      <circle className="ghibli-node" cx="30" cy="-2" r="2.2" fill="#9ff6e8" style={{ animationDelay: '1.5s' }} />
      <circle className="ghibli-node" cx="80" cy="4" r="2.2" fill="#9ff6e8" style={{ animationDelay: '3s' }} />
    </g>
  </g>
);

const Drone = ({ x, y, scale, delay }) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`}>
    <g className="ghibli-drone" style={{ animationDelay: delay }}>
      <line x1="-11" y1="0" x2="-6" y2="0" stroke="#2f4f5f" strokeWidth="2" />
      <line x1="6" y1="0" x2="11" y2="0" stroke="#2f4f5f" strokeWidth="2" />
      <line x1="-11" y1="-6" x2="-6" y2="-6" stroke="#2f4f5f" strokeWidth="2" />
      <line x1="6" y1="-6" x2="11" y2="-6" stroke="#2f4f5f" strokeWidth="2" />
      <rect x="-10" y="-9" width="20" height="9" rx="4.5" fill="#2f4f5f" />
      <circle cx="0" cy="-4" r="2" fill="#37e0b8" />
      <g className="ghibli-rotor">
        <circle cx="-11" cy="0" r="3.2" fill="none" stroke="#8fc4d8" strokeWidth="1.6" />
        <line x1="-11" y1="0" x2="-8" y2="0" stroke="#8fc4d8" strokeWidth="1.2" />
      </g>
      <g className="ghibli-rotor">
        <circle cx="11" cy="0" r="3.2" fill="none" stroke="#8fc4d8" strokeWidth="1.6" />
        <line x1="11" y1="0" x2="8" y2="0" stroke="#8fc4d8" strokeWidth="1.2" />
      </g>
      <g className="ghibli-rotor">
        <circle cx="-11" cy="-6" r="3.2" fill="none" stroke="#8fc4d8" strokeWidth="1.6" />
        <line x1="-11" y1="-6" x2="-8" y2="-6" stroke="#8fc4d8" strokeWidth="1.2" />
      </g>
      <g className="ghibli-rotor">
        <circle cx="11" cy="-6" r="3.2" fill="none" stroke="#8fc4d8" strokeWidth="1.6" />
        <line x1="11" y1="-6" x2="8" y2="-6" stroke="#8fc4d8" strokeWidth="1.2" />
      </g>
    </g>
  </g>
);

const DataParticle = ({ x, y, delay, duration }) => (
  <g transform={`translate(${x} ${y})`}>
    <g
      className="ghibli-seed"
      style={{ animationDelay: delay, animationDuration: duration }}
    >
      <circle cx="0" cy="0" r="7" fill="#9ff6e8" opacity="0.15" />
      <line x1="0" y1="5" x2="0" y2="22" stroke="#9ff6e8" strokeWidth="1.3" strokeOpacity="0.8" />
      <path d="M0 -5 L 4.5 0 L 0 5 L -4.5 0 Z" fill="#e2fdff" />
      <path d="M0 -3 L 2.6 0 L 0 3 L -2.6 0 Z" fill="#8ff0e0" />
    </g>
  </g>
);

const NodeDot = ({ x, y, delay }) => (
  <circle className="ghibli-node" cx={x} cy={y} r="3.2" fill="#d6fbff" style={{ animationDelay: delay }} />
);

const Sensor = ({ x, y, delay }) => (
  <g transform={`translate(${x} ${y})`}>
    <line x1="0" y1="0" x2="0" y2="-20" stroke="#3f8a6e" strokeWidth="2" strokeLinecap="round" />
    <circle className="ghibli-node" cx="0" cy="-22" r="2.6" fill="#7ff7e8" style={{ animationDelay: delay }} />
  </g>
);

const KeyFlower = ({ x, y }) => (
  <g transform={`translate(${x} ${y})`}>
    <circle cx="0" cy="-4" r="2.2" fill="#ffffff" />
    <circle cx="-3.5" cy="-2" r="2.2" fill="#ffffff" />
    <circle cx="3.5" cy="-2" r="2.2" fill="#ffffff" />
    <circle cx="-2" cy="2" r="2.2" fill="#ffffff" />
    <circle cx="2" cy="2" r="2.2" fill="#ffffff" />
    <circle cx="0" cy="0" r="2.4" fill="#3fd0c0" />
    <path d="M-1 1 L0 2.6 L1 1 Z" fill="#0f3f45" opacity="0.9" />
  </g>
);

const GhibliScene = () => {
  return (
    <div className="ghibli-scene" aria-hidden="true">
      <svg
        className="ghibli-svg"
        viewBox="0 0 1440 900"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#bfe0f7" />
            <stop offset="55%" stopColor="#e6f4f2" />
            <stop offset="100%" stopColor="#fbf1e0" />
          </linearGradient>
          <radialGradient id="sunGrad" cx="0.5" cy="0.5" r="0.5">
            <stop offset="0%" stopColor="#d9f7ff" stopOpacity="0.95" />
            <stop offset="60%" stopColor="#bfe8f5" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#bfe8f5" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="hillBackGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#b2dcd0" />
            <stop offset="100%" stopColor="#94c8b6" />
          </linearGradient>
          <linearGradient id="hillMidGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#7fcdb2" />
            <stop offset="100%" stopColor="#58aa8f" />
          </linearGradient>
          <linearGradient id="hillFrontGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#57b795" />
            <stop offset="100%" stopColor="#3b8f72" />
          </linearGradient>
          <pattern id="circuit" width="70" height="70" patternUnits="userSpaceOnUse">
            <path d="M5 35 H25 M25 35 V15 H45 V55 H65 M25 35 V55 H45" stroke="#2e7a5f" strokeWidth="1.3" fill="none" opacity="0.4" />
            <circle cx="25" cy="35" r="2.6" fill="#2e7a5f" opacity="0.5" />
            <circle cx="45" cy="15" r="2.6" fill="#2e7a5f" opacity="0.5" />
            <circle cx="45" cy="55" r="2.6" fill="#2e7a5f" opacity="0.5" />
            <circle cx="65" cy="55" r="2.6" fill="#2e7a5f" opacity="0.5" />
          </pattern>
          <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="7" />
          </filter>
        </defs>

        <rect x="0" y="0" width="1440" height="900" fill="url(#skyGrad)" />

        <g className="ghibli-sun-glow">
          <circle cx="1150" cy="170" r="190" fill="url(#sunGrad)" />
        </g>
        <g className="ghibli-sun">
          <circle cx="1150" cy="170" r="60" fill="#e9fbff" />
          <circle cx="1150" cy="170" r="60" fill="none" stroke="#7cc8e8" strokeWidth="2" strokeDasharray="3 6" opacity="0.7" />
          <circle cx="1150" cy="170" r="34" fill="none" stroke="#5cb8e8" strokeWidth="2.5" opacity="0.8" />
          <path d="M1138 170 a12 12 0 1 1 24 0" fill="none" stroke="#4a9fc8" strokeWidth="3" strokeLinecap="round" />
          <rect x="1142" y="168" width="16" height="14" rx="3" fill="#e9fbff" stroke="#4a9fc8" strokeWidth="2.5" />
        </g>
        <g className="ghibli-radar">
          <circle cx="1150" cy="170" r="84" fill="none" stroke="#5cb8e8" strokeWidth="1.5" strokeDasharray="6 10" opacity="0.7" />
          <path d="M1150 170 L 1216 132" stroke="#5cb8e8" strokeWidth="2.5" opacity="0.8" strokeLinecap="round" />
        </g>

        <Cloud x={180} y={150} scale={1} className="ghibli-cloud-1" delay="-12s" />
        <Cloud x={560} y={330} scale={0.8} className="ghibli-cloud-2" delay="-38s" />
        <Cloud x={920} y={120} scale={0.6} className="ghibli-cloud-3" delay="-22s" />
        <Cloud x={340} y={430} scale={0.7} className="ghibli-cloud-4" delay="-55s" />

        <g className="ghibli-wind-wrap" transform="translate(140 300)">
          <path
            className="ghibli-wind"
            d="M0 0 C 80 -20 160 18 240 0"
            fill="none"
            stroke="#b6ecff"
            strokeOpacity="0.7"
            strokeWidth="2"
            strokeDasharray="7 11"
            strokeLinecap="round"
          />
        </g>
        <g className="ghibli-wind-wrap" transform="translate(760 210)">
          <path
            className="ghibli-wind-2"
            d="M0 0 C 60 -16 120 14 180 -4"
            fill="none"
            stroke="#b6ecff"
            strokeOpacity="0.55"
            strokeWidth="2"
            strokeDasharray="5 9"
            strokeLinecap="round"
          />
        </g>
        <g className="ghibli-glyph" transform="translate(500 265)">
          <text x="0" y="0" fontSize="13" fill="#7fd8f0" opacity="0.6" fontFamily="monospace">01</text>
        </g>
        <g className="ghibli-glyph" transform="translate(980 180)">
          <text x="0" y="0" fontSize="13" fill="#7fd8f0" opacity="0.55" fontFamily="monospace">1 0</text>
        </g>
        <g className="ghibli-glyph" transform="translate(220 340)">
          <text x="0" y="0" fontSize="13" fill="#7fd8f0" opacity="0.5" fontFamily="monospace">()</text>
        </g>

        <Drone x={520} y={200} scale={1} delay="0s" />
        <Drone x={780} y={150} scale={1.15} delay="-5s" />
        <Drone x={980} y={240} scale={0.9} delay="-9s" />

        <path d="M0 640 C 240 520 480 600 720 610 C 960 620 1200 560 1440 620 L1440 900 L0 900 Z" fill="url(#hillBackGrad)" />
        <path d="M180 900 C 400 560 900 560 1440 660 L1440 900 Z" fill="#a9dcc9" opacity="0.8" />
        <path d="M0 640 C 240 520 480 600 720 610 C 960 620 1200 560 1440 620" fill="none" stroke="#d9f8e8" strokeWidth="20" opacity="0.45" strokeDasharray="20 14" filter="url(#soft)" />

        <path d="M0 760 C 300 640 640 700 960 760 C 1120 780 1320 740 1440 770 L1440 900 L0 900 Z" fill="url(#hillMidGrad)" />
        <path d="M600 900 C 900 640 1240 700 1440 800 L1440 900 Z" fill="#7cc9a8" opacity="0.85" />
        <path d="M0 760 C 300 640 640 700 960 760 C 1120 780 1320 740 1440 770" fill="none" stroke="#c2f2dc" strokeWidth="16" opacity="0.45" strokeDasharray="18 12" filter="url(#soft)" />

        <path d="M0 850 C 320 770 700 820 1040 860 C 1200 872 1360 850 1440 868 L1440 900 L0 900 Z" fill="url(#hillFrontGrad)" />
        <path d="M0 900 L0 880 C 240 830 480 860 720 880 C 960 892 1200 872 1440 890 L1440 900 Z" fill="#4f9f7e" />
        <path d="M0 850 C 320 770 700 820 1040 860 C 1200 872 1360 850 1440 868 L1440 900 L0 900 Z" fill="url(#circuit)" opacity="0.4" />
        <path d="M0 850 C 320 770 700 820 1040 860 C 1200 872 1360 850 1440 868" fill="none" stroke="#c8f5e0" strokeWidth="14" opacity="0.4" strokeDasharray="14 10" filter="url(#soft)" />

        <g transform="translate(330 700)">
          <g className="ghibli-tree-sway">
            <path d="M-10 100 C -8 55 -6 20 0 -8 C 6 20 8 55 10 100 Z" fill="#33505c" />
            <path d="M-4 40 C -30 30 -62 28 -76 16" stroke="#33505c" strokeWidth="11" strokeLinecap="round" fill="none" />
            <path d="M6 30 C 30 22 52 18 64 8" stroke="#33505c" strokeWidth="9" strokeLinecap="round" fill="none" />

            <path
              d="M-72 -88 L -42 -104 L 0 -134 L 42 -114 L 72 -94 M -42 -104 L -36 -64 M 42 -114 L 36 -66 M 0 -134 L 0 -92"
              stroke="#c2f2ff"
              strokeWidth="1.6"
              opacity="0.85"
              fill="none"
            />
            <NodeDot x={-72} y={-88} delay="0s" />
            <NodeDot x={-42} y={-104} delay="1s" />
            <NodeDot x={0} y={-134} delay="2s" />
            <NodeDot x={42} y={-114} delay="0.6s" />
            <NodeDot x={72} y={-94} delay="1.6s" />
            <NodeDot x={-36} y={-64} delay="2.6s" />
            <NodeDot x={36} y={-66} delay="0.2s" />
            <NodeDot x={0} y={-92} delay="1.2s" />

            <ellipse cx="-72" cy="-32" rx="46" ry="40" fill="#4f9c8a" />
            <ellipse cx="72" cy="-36" rx="46" ry="40" fill="#4f9c8a" />
            <ellipse cx="0" cy="-92" rx="54" ry="48" fill="#5cb3a0" />
            <ellipse cx="-36" cy="-64" rx="44" ry="38" fill="#6cc2a8" />
            <ellipse cx="36" cy="-66" rx="44" ry="38" fill="#63b89e" />
            <circle cx="-30" cy="-100" r="15" fill="#a9e8d2" opacity="0.6" />
            <circle cx="34" cy="-112" r="11" fill="#a9e8d2" opacity="0.5" />
          </g>

          <g transform="translate(34 -80)">
            <g className="ghibli-shield">
              <line x1="0" y1="0" x2="0" y2="12" stroke="#33505c" strokeWidth="2.5" />
              <path
                d="M0 16 C -14 12 -16 0 -16 -10 C -16 -16 -8 -18 0 -20 C 8 -18 16 -16 16 -10 C 16 0 14 12 0 16 Z"
                fill="#dfeaf0"
                stroke="#33505c"
                strokeWidth="2"
              />
              <circle cx="0" cy="-4" r="2.6" fill="none" stroke="#33505c" strokeWidth="1.5" />
              <path d="M-1.8 -1 L0 3 L1.8 -1 Z" fill="#33505c" />
            </g>
          </g>

          <g transform="translate(6 -120)">
            <g className="ghibli-spirit">
              <line x1="-14" y1="-16" x2="-16" y2="-30" stroke="#7f8b9e" strokeWidth="4" strokeLinecap="round" />
              <circle className="ghibli-node" cx="-16" cy="-33" r="3" fill="#37e0b8" style={{ animationDelay: '0.5s' }} />
              <line x1="14" y1="-16" x2="16" y2="-30" stroke="#7f8b9e" strokeWidth="4" strokeLinecap="round" />
              <circle className="ghibli-node" cx="16" cy="-33" r="3" fill="#37e0b8" style={{ animationDelay: '1.5s' }} />
              <line x1="0" y1="-24" x2="0" y2="-34" stroke="#7f8b9e" strokeWidth="2" />
              <circle className="ghibli-node" cx="0" cy="-37" r="3.2" fill="#37e0b8" style={{ animationDelay: '1s' }} />
              <ellipse cx="0" cy="0" rx="26" ry="24" fill="#7f8b9e" />
              <ellipse cx="0" cy="6" rx="15" ry="13" fill="#c9d4e0" opacity="0.95" />
              <circle cx="-9" cy="-5" r="3" fill="#2b3340" />
              <circle cx="9" cy="-5" r="3" fill="#2b3340" />
              <ellipse cx="0" cy="1" rx="3" ry="2.4" fill="#2b3340" />
              <path d="M-4 0 L -17 -3 M-4 3 L -16 6" stroke="#2b3340" strokeWidth="1.4" strokeLinecap="round" />
              <path d="M4 0 L 17 -3 M4 3 L 16 6" stroke="#2b3340" strokeWidth="1.4" strokeLinecap="round" />
            </g>
          </g>

          <g className="ghibli-leaf-wrap" transform="translate(20 -60)">
            <g className="ghibli-leaf" style={{ animationDelay: '2s' }}>
              <rect x="-5" y="-5" width="10" height="10" rx="2" fill="#7fd8f0" stroke="#3f8a9e" strokeWidth="1" />
              <path d="M-2.5 0 L 2.5 0 M-1.5 -1.5 L 0 0 L -1.5 1.5" stroke="#ffffff" strokeWidth="1.2" fill="none" />
            </g>
          </g>
          <g className="ghibli-leaf-wrap" transform="translate(-30 -80)">
            <g className="ghibli-leaf" style={{ animationDelay: '7s' }}>
              <rect x="-5" y="-5" width="10" height="10" rx="2" fill="#a5e8d8" stroke="#3f8a9e" strokeWidth="1" />
              <path d="M-2.5 0 L 2.5 0 M-1.5 -1.5 L 0 0 L -1.5 1.5" stroke="#ffffff" strokeWidth="1.2" fill="none" />
            </g>
          </g>
        </g>

        <Sensor x={190} y={830} delay="0s" />
        <Sensor x={430} y={812} delay="1.5s" />
        <Sensor x={1050} y={862} delay="0.8s" />
        <Sensor x={1320} y={858} delay="2.2s" />
        <Sensor x={820} y={840} delay="0.3s" />

        <KeyFlower x={220} y={818} />
        <KeyFlower x={400} y={800} />
        <KeyFlower x={1010} y={850} />
        <KeyFlower x={1120} y={860} />
        <KeyFlower x={1380} y={846} />

        <DataParticle x={300} y={640} delay="0s" duration="14s" />
        <DataParticle x={390} y={600} delay="3s" duration="16s" />
        <DataParticle x={330} y={560} delay="6s" duration="12s" />
        <DataParticle x={440} y={660} delay="9s" duration="15s" />
        <DataParticle x={250} y={700} delay="1.5s" duration="17s" />
        <DataParticle x={500} y={640} delay="5s" duration="13s" />
        <DataParticle x={620} y={560} delay="8s" duration="14s" />
        <DataParticle x={180} y={600} delay="4s" duration="16s" />
        <DataParticle x={820} y={500} delay="2s" duration="15s" />
        <DataParticle x={980} y={450} delay="7s" duration="13s" />
      </svg>
    </div>
  );
};

export default GhibliScene;
