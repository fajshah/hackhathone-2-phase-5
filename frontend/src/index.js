import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to Phase 5 Frontend</h1>
        <p>Your application is running successfully!</p>
      </header>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);