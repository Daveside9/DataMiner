import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import styled from 'styled-components';
import Layout from '../components/Layout';

const MonitoringContainer = styled.div`
  padding: 2rem;
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 0.5rem;
`;

const PageSubtitle = styled.p`
  color: #666;
  font-size: 1.1rem;
`;

const CategorySelector = styled.div`
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
`;

const CategoryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
`;

const CategoryCard = styled.div`
  padding: 1rem;
  border: 2px solid ${props => props.selected ? '#667eea' : '#e1e8ed'};
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s ease;
  background: ${props => props.selected ? '#f8f9ff' : 'white'};

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
  }
`;

const CategoryIcon = styled.div`
  font-size: 2rem;
  color: ${props => props.selected ? '#667eea' : '#666'};
  margin-bottom: 0.5rem;
`;

const CategoryTitle = styled.h3`
  color: ${props => props.selected ? '#667eea' : '#2c3e50'};
  margin-bottom: 0.5rem;
`;

const CategoryDescription = styled.p`
  color: #666;
  font-size: 0.9rem;
`;

const MonitoringForm = styled.div`
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 5px;
  font-size: 1rem;
  background: white;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const StartButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const PresetUrls = styled.div`
  margin-top: 1rem;
`;

const PresetTitle = styled.h4`
  color: #2c3e50;
  margin-bottom: 0.5rem;
`;

const PresetList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const PresetUrl = styled.button`
  background: #f8f9fa;
  border: 1px solid #e1e8ed;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    background: #667eea;
    color: white;
    border-color: #667eea;
  }
`;

const Monitoring = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedCategory, setSelectedCategory] = useState('');
  const [monitoringUrl, setMonitoringUrl] = useState('');
  const [monitoringInterval, setMonitoringInterval] = useState(30);
  const [maxDuration, setMaxDuration] = useState(60);

  const categories = [
    {
      id: 'sports',
      icon: 'fas fa-futbol',
      title: 'Sports',
      description: 'Monitor live scores, betting odds, and sports statistics',
      presets: [
        'https://www.flashscore.com',
        'https://www.bet365.com',
        'https://www.espn.com/soccer',
        'https://www.premierleague.com'
      ]
    },
    {
      id: 'weather',
      icon: 'fas fa-cloud-sun',
      title: 'Weather',
      description: 'Track weather forecasts and climate data',
      presets: [
        'https://weather.com',
        'https://www.accuweather.com',
        'https://openweathermap.org',
        'https://www.weather.gov'
      ]
    },
    {
      id: 'forex',
      icon: 'fas fa-chart-line',
      title: 'Forex Trading',
      description: 'Monitor currency exchange rates and trading data',
      presets: [
        'https://www.xe.com',
        'https://www.investing.com/currencies',
        'https://www.forexfactory.com',
        'https://www.oanda.com'
      ]
    },
    {
      id: 'crypto',
      icon: 'fas fa-bitcoin',
      title: 'Cryptocurrency',
      description: 'Track cryptocurrency prices and market data',
      presets: [
        'https://coinmarketcap.com',
        'https://www.coingecko.com',
        'https://www.binance.com',
        'https://coinbase.com'
      ]
    },
    {
      id: 'ecommerce',
      icon: 'fas fa-shopping-cart',
      title: 'E-commerce',
      description: 'Monitor product prices and availability',
      presets: [
        'https://www.amazon.com',
        'https://www.ebay.com',
        'https://www.alibaba.com',
        'https://www.shopify.com'
      ]
    },
    {
      id: 'news',
      icon: 'fas fa-newspaper',
      title: 'News',
      description: 'Track breaking news and content updates',
      presets: [
        'https://www.cnn.com',
        'https://www.bbc.com/news',
        'https://www.reuters.com',
        'https://news.google.com'
      ]
    },
    {
      id: 'realestate',
      icon: 'fas fa-home',
      title: 'Real Estate',
      description: 'Monitor property listings and market prices',
      presets: [
        'https://www.zillow.com',
        'https://www.realtor.com',
        'https://www.redfin.com',
        'https://www.trulia.com'
      ]
    },
    {
      id: 'jobs',
      icon: 'fas fa-briefcase',
      title: 'Jobs',
      description: 'Track job listings and salary information',
      presets: [
        'https://www.linkedin.com/jobs',
        'https://www.indeed.com',
        'https://www.glassdoor.com',
        'https://stackoverflow.com/jobs'
      ]
    }
  ];

  useEffect(() => {
    const category = searchParams.get('category');
    const url = searchParams.get('url');
    const type = searchParams.get('type');
    
    if (category) {
      setSelectedCategory(category);
    }
    if (url) {
      setMonitoringUrl(decodeURIComponent(url));
    }
    if (type && category === 'sports') {
      // Set specific monitoring type for sports
      console.log(`Sports monitoring type: ${type}`);
    }
  }, [searchParams]);

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    setSearchParams({ category: categoryId });
  };

  const handlePresetClick = (url) => {
    setMonitoringUrl(url);
  };

  const handleStartMonitoring = () => {
    if (!monitoringUrl) {
      alert('Please enter a URL to monitor');
      return;
    }

    // Here you would typically make an API call to start monitoring
    console.log('Starting monitoring:', {
      url: monitoringUrl,
      category: selectedCategory,
      interval: monitoringInterval,
      duration: maxDuration
    });

    alert(`Starting monitoring for ${monitoringUrl}\nCategory: ${selectedCategory}\nInterval: ${monitoringInterval}s\nDuration: ${maxDuration}min`);
  };

  const selectedCategoryData = categories.find(cat => cat.id === selectedCategory);

  return (
    <Layout>
      <MonitoringContainer>
        <PageHeader>
          <PageTitle>Start Data Monitoring</PageTitle>
          <PageSubtitle>
            Select a category and configure your monitoring session to start collecting data
          </PageSubtitle>
        </PageHeader>

        <CategorySelector>
          <h3>Select Data Category</h3>
          <CategoryGrid>
            {categories.map((category) => (
              <CategoryCard
                key={category.id}
                selected={selectedCategory === category.id}
                onClick={() => handleCategorySelect(category.id)}
              >
                <CategoryIcon selected={selectedCategory === category.id}>
                  <i className={category.icon}></i>
                </CategoryIcon>
                <CategoryTitle selected={selectedCategory === category.id}>
                  {category.title}
                </CategoryTitle>
                <CategoryDescription>
                  {category.description}
                </CategoryDescription>
              </CategoryCard>
            ))}
          </CategoryGrid>
        </CategorySelector>

        {selectedCategory && (
          <MonitoringForm>
            <h3>Configure Monitoring Session</h3>
            
            <FormGroup>
              <Label>Website URL to Monitor</Label>
              <Input
                type="url"
                value={monitoringUrl}
                onChange={(e) => setMonitoringUrl(e.target.value)}
                placeholder="Enter the website URL you want to monitor"
              />
              
              {selectedCategoryData && (
                <PresetUrls>
                  <PresetTitle>Popular {selectedCategoryData.title} Sites:</PresetTitle>
                  <PresetList>
                    {selectedCategoryData.presets.map((url, index) => (
                      <PresetUrl
                        key={index}
                        onClick={() => handlePresetClick(url)}
                      >
                        {url.replace('https://www.', '').replace('https://', '')}
                      </PresetUrl>
                    ))}
                  </PresetList>
                </PresetUrls>
              )}
            </FormGroup>

            <FormGroup>
              <Label>Monitoring Interval (seconds)</Label>
              <Select
                value={monitoringInterval}
                onChange={(e) => setMonitoringInterval(parseInt(e.target.value))}
              >
                <option value={15}>15 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
                <option value={300}>5 minutes</option>
                <option value={600}>10 minutes</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Maximum Duration (minutes)</Label>
              <Select
                value={maxDuration}
                onChange={(e) => setMaxDuration(parseInt(e.target.value))}
              >
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={120}>2 hours</option>
                <option value={360}>6 hours</option>
                <option value={720}>12 hours</option>
                <option value={1440}>24 hours</option>
              </Select>
            </FormGroup>

            <StartButton
              onClick={handleStartMonitoring}
              disabled={!monitoringUrl}
            >
              <i className="fas fa-play"></i>
              Start Monitoring Session
            </StartButton>
          </MonitoringForm>
        )}
      </MonitoringContainer>
    </Layout>
  );
};

export default Monitoring;