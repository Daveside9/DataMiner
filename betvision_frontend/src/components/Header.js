import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
`;

const TopHeader = styled.div`
  padding: 1rem 0;
`;

const HeaderContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;

  @media (max-width: 768px) {
    padding: 0 1rem;
  }
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  
  &:hover {
    color: white;
  }
`;

const TopicsNav = styled.nav`
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255,255,255,0.1);
`;

const TopicsContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;

  @media (max-width: 768px) {
    padding: 0 1rem;
  }
`;

const TopicsGrid = styled.div`
  display: flex;
  gap: 0;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  
  &::-webkit-scrollbar {
    display: none;
  }

  @media (max-width: 768px) {
    gap: 0;
  }
`;

const TopicCard = styled.div`
  min-width: 140px;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-right: 1px solid rgba(255,255,255,0.1);
  background: ${props => props.active ? 'rgba(255,255,255,0.2)' : 'transparent'};
  
  &:hover {
    background: rgba(255,255,255,0.1);
    transform: translateY(-2px);
  }

  &:last-child {
    border-right: none;
  }

  @media (max-width: 768px) {
    min-width: 120px;
    padding: 0.8rem;
  }
`;

const TopicIcon = styled.div`
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #fff;

  @media (max-width: 768px) {
    font-size: 1.2rem;
  }
`;

const TopicTitle = styled.div`
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.2rem;

  @media (max-width: 768px) {
    font-size: 0.8rem;
  }
`;

const TopicDescription = styled.div`
  font-size: 0.7rem;
  opacity: 0.8;
  line-height: 1.2;

  @media (max-width: 768px) {
    font-size: 0.65rem;
  }
`;

const SportsContent = styled.div`
  background: white;
  color: #333;
  padding: 2rem;
  border-top: 1px solid rgba(255,255,255,0.1);
`;

const SportsGrid = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
`;

const SportsCard = styled.div`
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  border: 2px solid transparent;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
  }
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const CardIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
`;

const CardTitle = styled.h3`
  margin: 0;
  color: #2c3e50;
`;

const CardDescription = styled.p`
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
`;

const UrlInput = styled.input`
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 1rem;
`;

const ActionButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-1px);
  }
`;

const UserMenu = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;

  @media (max-width: 768px) {
    gap: 0.5rem;
  }
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

const LogoutButton = styled.button`
  background: rgba(255,255,255,0.2);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s ease;

  &:hover {
    background: rgba(255,255,255,0.3);
  }

  @media (max-width: 768px) {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
`;

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTopic, setActiveTopic] = useState(null);
  const [sportsUrls, setSportsUrls] = useState({
    betting: '',
    livescore: '',
    basketball: '',
    football: ''
  });

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const topics = [
    {
      icon: 'fas fa-futbol',
      title: 'Sports',
      description: 'Live scores & betting odds',
      category: 'sports'
    },
    {
      icon: 'fas fa-cloud-sun',
      title: 'Weather',
      description: 'Forecasts & climate data',
      category: 'weather'
    },
    {
      icon: 'fas fa-chart-line',
      title: 'Forex Trading',
      description: 'Currency rates & trends',
      category: 'forex'
    },
    {
      icon: 'fas fa-bitcoin',
      title: 'Cryptocurrency',
      description: 'Crypto prices & analysis',
      category: 'crypto'
    },
    {
      icon: 'fas fa-shopping-cart',
      title: 'E-commerce',
      description: 'Product prices & deals',
      category: 'ecommerce'
    },
    {
      icon: 'fas fa-newspaper',
      title: 'News',
      description: 'Breaking news & updates',
      category: 'news'
    },
    {
      icon: 'fas fa-home',
      title: 'Real Estate',
      description: 'Property listings & prices',
      category: 'realestate'
    },
    {
      icon: 'fas fa-briefcase',
      title: 'Jobs',
      description: 'Job listings & salaries',
      category: 'jobs'
    }
  ];

  const handleTopicClick = (category) => {
    if (category === 'sports') {
      setActiveTopic(activeTopic === 'sports' ? null : 'sports');
    } else {
      setActiveTopic(null);
      navigate(`/monitoring?category=${category}`);
    }
  };

  const handleUrlChange = (type, value) => {
    setSportsUrls(prev => ({
      ...prev,
      [type]: value
    }));
  };

  const startMonitoring = (type, url) => {
    if (!url) {
      alert('Please enter a URL first');
      return;
    }
    // Navigate to monitoring with the URL
    navigate(`/monitoring?category=sports&url=${encodeURIComponent(url)}&type=${type}`);
  };

  const sportsCategories = [
    {
      id: 'betting',
      title: 'Betting Sites',
      icon: 'fas fa-chart-line',
      description: 'Monitor betting odds and predictions',
      placeholder: 'https://bet365.com or https://bet9ja.com',
      features: ['Odds tracking', 'Bet predictor', 'Screen monitor']
    },
    {
      id: 'livescore',
      title: 'Live Scores',
      icon: 'fas fa-futbol',
      description: 'Track live football matches and scores',
      placeholder: 'https://livescore.com or https://flashscore.com',
      features: ['Live scores', 'Match analysis', 'Team stats']
    },
    {
      id: 'basketball',
      title: 'Basketball',
      icon: 'fas fa-basketball-ball',
      description: 'Monitor NBA, EuroLeague and other leagues',
      placeholder: 'https://nba.com or https://espn.com/nba',
      features: ['Game scores', 'Player stats', 'Team analysis']
    },
    {
      id: 'football',
      title: 'Football/Soccer',
      icon: 'fas fa-futbol',
      description: 'Premier League, Champions League coverage',
      placeholder: 'https://premierleague.com or https://uefa.com',
      features: ['Match results', 'League tables', 'Player data']
    }
  ];

  return (
    <HeaderContainer>
      <TopHeader>
        <HeaderContent>
          <Logo to="/dashboard">
            <i className="fas fa-database"></i>
            DataMiner Pro
          </Logo>
          
          {user && (
            <UserMenu>
              <UserInfo>
                <i className="fas fa-user-circle"></i>
                <span>{user.full_name}</span>
              </UserInfo>
              <LogoutButton onClick={handleLogout}>
                <i className="fas fa-sign-out-alt"></i>
                Logout
              </LogoutButton>
            </UserMenu>
          )}
        </HeaderContent>
      </TopHeader>

      {user && (
        <TopicsNav>
          <TopicsContainer>
            <TopicsGrid>
              {topics.map((topic, index) => (
                <TopicCard 
                  key={index}
                  active={activeTopic === topic.category}
                  onClick={() => handleTopicClick(topic.category)}
                >
                  <TopicIcon>
                    <i className={topic.icon}></i>
                  </TopicIcon>
                  <TopicTitle>{topic.title}</TopicTitle>
                  <TopicDescription>{topic.description}</TopicDescription>
                </TopicCard>
              ))}
            </TopicsGrid>
          </TopicsContainer>
        </TopicsNav>
      )}

      {activeTopic === 'sports' && (
        <SportsContent>
          <SportsGrid>
            {sportsCategories.map((category) => (
              <SportsCard key={category.id}>
                <CardHeader>
                  <CardIcon>
                    <i className={category.icon}></i>
                  </CardIcon>
                  <CardTitle>{category.title}</CardTitle>
                </CardHeader>
                <CardDescription>{category.description}</CardDescription>
                
                <UrlInput
                  type="url"
                  placeholder={category.placeholder}
                  value={sportsUrls[category.id]}
                  onChange={(e) => handleUrlChange(category.id, e.target.value)}
                />
                
                <div>
                  <ActionButton onClick={() => startMonitoring(category.id, sportsUrls[category.id])}>
                    <i className="fas fa-play"></i> Start Monitoring
                  </ActionButton>
                  <ActionButton onClick={() => startMonitoring('screen', sportsUrls[category.id])}>
                    <i className="fas fa-camera"></i> Screen Monitor
                  </ActionButton>
                  <ActionButton onClick={() => startMonitoring('predictor', sportsUrls[category.id])}>
                    <i className="fas fa-crystal-ball"></i> Bet Predictor
                  </ActionButton>
                  <ActionButton onClick={() => navigate('/betting-visual-extractor')}>
                    <i className="fas fa-robot"></i> Visual History Extractor
                  </ActionButton>
                </div>
                
                <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#666' }}>
                  <strong>Features:</strong> {category.features.join(', ')}
                </div>
              </SportsCard>
            ))}
          </SportsGrid>
        </SportsContent>
      )}
    </HeaderContainer>
  );
};

export default Header;