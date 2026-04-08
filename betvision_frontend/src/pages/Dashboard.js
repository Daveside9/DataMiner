import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const DashboardContainer = styled.div`
  h1 {
    margin-bottom: 2rem;
    color: #2c3e50;
  }
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(motion.div)`
  background: ${props => props.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'};
  color: white;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: center;
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  opacity: 0.9;
`;

const QuickActions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const ActionCard = styled(motion.div)`
  background: white;
  border: 2px solid #e1e8ed;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: #333;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }

  i {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    color: #667eea;
  }

  h3 {
    margin-bottom: 0.5rem;
  }
`;

const RecentActivity = styled.div`
  h2 {
    margin-bottom: 1rem;
    color: #2c3e50;
  }
`;

const ActivityList = styled.ul`
  list-style: none;
`;

const ActivityItem = styled.li`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f1f3f4;

  &:last-child {
    border-bottom: none;
  }
`;

const ActivityIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  color: #667eea;
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 600;
  margin-bottom: 0.25rem;
`;

const ActivityTime = styled.div`
  font-size: 0.875rem;
  color: #666;
`;

const LoadingCard = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #666;
`;

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Simulate loading dashboard data
      setTimeout(() => {
        setDashboardData({
          quick_stats: {
            total_sessions: 5,
            active_sessions: 2,
            total_screenshots: 150,
            unread_alerts: 3
          },
          recent_sessions: []
        });
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load dashboard data');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <LoadingCard>
          <div className="spinner"></div>
          <span style={{ marginLeft: '1rem' }}>Loading dashboard...</span>
        </LoadingCard>
      </Layout>
    );
  }

  const stats = dashboardData?.quick_stats || {};
  const recentSessions = dashboardData?.recent_sessions || [];

  return (
    <Layout>
      <DashboardContainer>
        <h1>Welcome back, {user?.full_name}!</h1>
        
        <StatsGrid>
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatNumber>{stats.total_sessions || 0}</StatNumber>
            <StatLabel>Total Sessions</StatLabel>
          </StatCard>
          
          <StatCard
            gradient="linear-gradient(135deg, #28a745 0%, #20c997 100%)"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatNumber>{stats.active_sessions || 0}</StatNumber>
            <StatLabel>Active Sessions</StatLabel>
          </StatCard>
          
          <StatCard
            gradient="linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatNumber>{stats.total_screenshots || 0}</StatNumber>
            <StatLabel>Screenshots</StatLabel>
          </StatCard>
          
          <StatCard
            gradient="linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%)"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatNumber>{stats.unread_alerts || 0}</StatNumber>
            <StatLabel>Unread Alerts</StatLabel>
          </StatCard>
        </StatsGrid>

        <h2>Quick Actions</h2>
        <QuickActions>
          <ActionCard
            as="a"
            href="/monitoring"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <i className="fas fa-play"></i>
            <h3>Start Monitoring</h3>
            <p>Begin monitoring any website</p>
          </ActionCard>
          
          <ActionCard
            as="a"
            href="/sessions"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <i className="fas fa-list"></i>
            <h3>View Sessions</h3>
            <p>Manage your monitoring sessions</p>
          </ActionCard>
          
          <ActionCard
            as="a"
            href="/analytics"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <i className="fas fa-chart-line"></i>
            <h3>View Analytics</h3>
            <p>Check your monitoring statistics</p>
          </ActionCard>
          
          <ActionCard
            as="a"
            href="/betting-visual-extractor"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <i className="fas fa-robot"></i>
            <h3>Visual History Extractor</h3>
            <p>Extract betting history with AI</p>
          </ActionCard>
          
          <ActionCard
            as="a"
            href="/profile"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <i className="fas fa-user"></i>
            <h3>Profile Settings</h3>
            <p>Manage your account</p>
          </ActionCard>
        </QuickActions>

        <RecentActivity>
          <h2>Recent Activity</h2>
          <ActivityList>
            {recentSessions.length === 0 ? (
              <ActivityItem>
                <ActivityIcon>
                  <i className="fas fa-info"></i>
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>No recent activity</ActivityTitle>
                  <ActivityTime>Start your first monitoring session to see activity here</ActivityTime>
                </ActivityContent>
              </ActivityItem>
            ) : (
              recentSessions.map((session, index) => (
                <ActivityItem key={session.id}>
                  <ActivityIcon>
                    <i className="fas fa-eye"></i>
                  </ActivityIcon>
                  <ActivityContent>
                    <ActivityTitle>{session.site_name || 'Monitoring Session'}</ActivityTitle>
                    <ActivityTime>
                      {session.status} • {session.screenshots_count} screenshots • 
                      {new Date(session.start_time).toLocaleString()}
                    </ActivityTime>
                  </ActivityContent>
                </ActivityItem>
              ))
            )}
          </ActivityList>
        </RecentActivity>
      </DashboardContainer>
    </Layout>
  );
};

export default Dashboard;