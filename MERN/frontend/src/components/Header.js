import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { Sparkles, Home, BarChart3 } from 'lucide-react';

const HeaderContainer = styled.header`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 1000;
  padding: 0 2rem;
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
`;

const Logo = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #333;
  font-size: 1.5rem;
  font-weight: 700;
  
  &:hover {
    color: #667eea;
  }
`;

const Nav = styled.nav`
  display: flex;
  gap: 2rem;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: #666;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    color: #667eea;
    background: rgba(102, 126, 234, 0.1);
  }
  
  ${props => props.$active && `
    color: #667eea;
    background: rgba(102, 126, 234, 0.1);
  `}
`;

const Header = () => {
  const location = useLocation();

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo to="/">
          <Sparkles size={24} />
          AdGen
        </Logo>
        
        <Nav>
          <NavLink to="/" $active={location.pathname === '/'}>
            <Home size={18} />
            Home
          </NavLink>
          <NavLink to="/dashboard" $active={location.pathname === '/dashboard'}>
            <BarChart3 size={18} />
            Dashboard
          </NavLink>
        </Nav>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header;
