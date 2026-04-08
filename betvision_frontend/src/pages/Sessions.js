import React from 'react';
import styled from 'styled-components';
import Layout from '../components/Layout';

const SessionsContainer = styled.div`
  padding: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 2rem;
`;

const Sessions = () => {
  return (
    <Layout>
      <SessionsContainer>
        <PageTitle>Monitoring Sessions</PageTitle>
        <p>View and manage your monitoring sessions here.</p>
      </SessionsContainer>
    </Layout>
  );
};

export default Sessions;