import React from 'react';
import styled from 'styled-components';
import Header from './Header';
import Sidebar from './Sidebar';

const LayoutContainer = styled.div`
  min-height: 100vh;
  background: #f8f9fa;
`;

const MainContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
`;

const Content = styled.main`
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  min-height: 600px;

  @media (max-width: 768px) {
    padding: 1.5rem;
  }
`;

const Layout = ({ children }) => {
  return (
    <LayoutContainer>
      <Header />
      <MainContainer>
        <Sidebar />
        <Content>
          {children}
        </Content>
      </MainContainer>
    </LayoutContainer>
  );
};

export default Layout;