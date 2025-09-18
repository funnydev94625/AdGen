import React from 'react';
import { Routes, Route } from 'react-router-dom';
import styled from 'styled-components';
import Header from './components/Header';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import { WebSocketProvider } from './contexts/WebSocketContext';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const MainContent = styled.main`
  padding-top: 80px; /* Account for fixed header */
`;

function App() {
  return (
    <WebSocketProvider>
      <AppContainer>
        <Header />
        <MainContent>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </MainContent>
      </AppContainer>
    </WebSocketProvider>
  );
}

export default App;
