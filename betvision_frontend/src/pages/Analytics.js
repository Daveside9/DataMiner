import React from 'react';
import styled from 'styled-components';
import Layout from '../components/Layout';

const AnalyticsContainer = styled.div`
  padding: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 2rem;
`;

const Analytics = () => {
  return (
    <Layout>
      <AnalyticsContainer>
        <PageTitle>Analytics Dashboard</PageTitle>
        <p>View your monitoring analytics and statistics here.</p>
      </AnalyticsContainer>
    </Layout>
  );
};

export default Analytics;