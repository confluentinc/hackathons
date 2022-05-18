import logo from './logo.svg';
import './App.css';
import { useState, useEffect } from 'react';

const WS_URL = "ws://localhost:8080/websocket";

function App() {
  const [websocket, _] = useState(new WebSocket(WS_URL));
  const [message, setMessage] = useState(null);

  useEffect(() => {
    websocket.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      const formatted = JSON.stringify(payload);
      setMessage(formatted);
    };
  }, [websocket]);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h2>{message || "...waiting..."}</h2>
      </header>
    </div>
  );
}

export default App;
