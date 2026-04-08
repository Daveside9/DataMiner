import React from 'react';
import styled from 'styled-components';
import Layout from '../components/Layout';

const ProfileContainer = styled.div`
  padding: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 2rem;
`;

const Profile = () => {
  return (
    <Layout>
      <ProfileContainer>
        <PageTitle>Profile Settings</PageTitle>
        <p>Manage your account settings and preferences here.</p>
      </ProfileContainer>
    </Layout>
  );
};

export default Profile;