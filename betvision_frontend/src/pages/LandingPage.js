import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const LandingContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
`;

const Header = styled.header`
  padding: 1rem 0;
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
  background: rgba(102, 126, 234, 0.9);
`;

const NavContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;

  @media (max-width: 768px) {
    padding: 0 1rem;
  }
`;

const Logo = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const NavButtons = styled.div`
  display: flex;
  gap: 1rem;

  @media (max-width: 768px) {
    gap: 0.5rem;
  }
`;

const HeroSection = styled.section`
  padding: 120px 0 80px;
  text-align: center;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
    opacity: 0.3;
  }
`;

const HeroContent = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
`;

const HeroTitle = styled(motion.h1)`
  font-size: 3.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #fff, #f0f8ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;

  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const HeroSubtitle = styled(motion.p)`
  font-size: 1.3rem;
  margin-bottom: 2rem;
  opacity: 0.9;

  @media (max-width: 768px) {
    font-size: 1.1rem;
  }
`;

const HeroButtons = styled(motion.div)`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
  }
`;

const FeaturesSection = styled.section`
  padding: 80px 0;
  background: #f8f9fa;
  color: #333;
`;

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const SectionTitle = styled.div`
  text-align: center;
  margin-bottom: 3rem;

  h2 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
  }

  p {
    font-size: 1.2rem;
    color: #666;
  }
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
`;

const FeatureCard = styled(motion.div)`
  background: white;
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  text-align: center;
  transition: transform 0.3s ease;

  &:hover {
    transform: translateY(-5px);
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const PricingSection = styled.section`
  padding: 80px 0;
  background: white;
`;

const PricingGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
`;

const PricingCard = styled(motion.div)`
  background: white;
  border: 2px solid #e1e8ed;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  position: relative;
  transition: all 0.3s ease;

  &.featured {
    border-color: #28a745;
    transform: scale(1.05);
  }

  &:hover {
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  }

  @media (max-width: 768px) {
    &.featured {
      transform: none;
    }
  }
`;

const PlanName = styled.h3`
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: #2c3e50;
`;

const PlanPrice = styled.div`
  font-size: 3rem;
  font-weight: bold;
  color: #28a745;
  margin-bottom: 0.5rem;
`;

const PlanPeriod = styled.p`
  color: #6c757d;
  margin-bottom: 2rem;
`;

const PlanFeatures = styled.ul`
  list-style: none;
  margin-bottom: 2rem;

  li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #f1f3f4;

    &:last-child {
      border-bottom: none;
    }

    i {
      color: #28a745;
      margin-right: 0.5rem;
    }

    &.unavailable i {
      color: #dc3545;
    }
  }
`;

const LandingPage = () => {
  const features = [
    {
      icon: 'fas fa-camera',
      title: 'Website Screenshots',
      description: 'Capture high-quality screenshots from any website at custom intervals with enhanced quality and thumbnail generation.'
    },
    {
      icon: 'fas fa-eye',
      title: 'Change Detection',
      description: 'Advanced algorithms detect visual changes, content updates, and data modifications with precision and reliability.'
    },
    {
      icon: 'fas fa-chart-bar',
      title: 'Data Extraction',
      description: 'Automatically extract and analyze data from websites using AI-powered pattern recognition and custom selectors.'
    },
    {
      icon: 'fas fa-brain',
      title: 'AI Analysis',
      description: 'Get intelligent insights and predictions based on collected data analysis and historical patterns.'
    },
    {
      icon: 'fas fa-bell',
      title: 'Smart Alerts',
      description: 'Receive instant notifications for data changes, new content, and important information updates.'
    },
    {
      icon: 'fas fa-shield-alt',
      title: 'Secure & Reliable',
      description: 'Enterprise-grade security with reliable monitoring that works 24/7 without interruption.'
    }
  ];

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'per month',
      features: [
        { text: '5 monitoring sessions', available: true },
        { text: 'Basic screenshot capture', available: true },
        { text: 'Change detection', available: true },
        { text: 'Email support', available: true },
        { text: 'Advanced analytics', available: false },
        { text: 'API access', available: false }
      ]
    },
    {
      name: 'Pro',
      price: '$29',
      period: 'per month',
      featured: true,
      features: [
        { text: '50 monitoring sessions', available: true },
        { text: 'High-quality screenshots', available: true },
        { text: 'Advanced change detection', available: true },
        { text: 'Data extraction tools', available: true },
        { text: 'Advanced analytics', available: true },
        { text: 'Priority support', available: true }
      ]
    },
    {
      name: 'Enterprise',
      price: '$99',
      period: 'per month',
      features: [
        { text: '200 monitoring sessions', available: true },
        { text: 'Ultra-quality screenshots', available: true },
        { text: 'Custom integrations', available: true },
        { text: 'API access', available: true },
        { text: 'White-label options', available: true },
        { text: 'Dedicated support', available: true }
      ]
    }
  ];

  return (
    <LandingContainer>
      <Header>
        <NavContainer>
          <Logo>
            <i className="fas fa-database"></i>
            DataMiner Pro
          </Logo>
          <NavButtons>
            <Link to="/login" className="btn btn-secondary">
              <i className="fas fa-sign-in-alt"></i>
              Login
            </Link>
            <Link to="/register" className="btn btn-primary">
              <i className="fas fa-user-plus"></i>
              Sign Up
            </Link>
          </NavButtons>
        </NavContainer>
      </Header>

      <HeroSection>
        <HeroContent>
          <HeroTitle
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            Professional Data Collection Platform
          </HeroTitle>
          <HeroSubtitle
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            Collect, monitor, and analyze data from any website in real-time. Capture screenshots, detect changes, and extract valuable information with DataMiner Pro's advanced monitoring system.
          </HeroSubtitle>
          <HeroButtons
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <Link to="/register" className="btn btn-primary btn-large">
              <i className="fas fa-rocket"></i>
              Start Collecting Data
            </Link>
            <a href="#features" className="btn btn-secondary btn-large">
              <i className="fas fa-play"></i>
              Learn More
            </a>
          </HeroButtons>
        </HeroContent>
      </HeroSection>

      <FeaturesSection id="features">
        <Container>
          <SectionTitle>
            <h2>Powerful Data Collection Features</h2>
            <p>Everything you need to monitor and collect data from any website</p>
          </SectionTitle>
          <FeaturesGrid>
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <FeatureIcon>
                  <i className={feature.icon}></i>
                </FeatureIcon>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </FeatureCard>
            ))}
          </FeaturesGrid>
        </Container>
      </FeaturesSection>

      <FeaturesSection style={{ background: 'white', color: '#333' }}>
        <Container>
          <SectionTitle>
            <h2>Data Collection Use Cases</h2>
            <p>Perfect for various data monitoring and collection activities</p>
          </SectionTitle>
          <FeaturesGrid>
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-shopping-cart"></i>
              </FeatureIcon>
              <h3>E-commerce Monitoring</h3>
              <p>Track product prices, availability, and competitor analysis across multiple online stores.</p>
            </FeatureCard>
            
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-newspaper"></i>
              </FeatureIcon>
              <h3>News & Content Tracking</h3>
              <p>Monitor news websites, blogs, and social media for content changes and updates.</p>
            </FeatureCard>
            
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-chart-line"></i>
              </FeatureIcon>
              <h3>Financial Data</h3>
              <p>Collect stock prices, cryptocurrency rates, and financial market data in real-time.</p>
            </FeatureCard>
            
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-home"></i>
              </FeatureIcon>
              <h3>Real Estate Listings</h3>
              <p>Monitor property listings, price changes, and new listings across real estate platforms.</p>
            </FeatureCard>
            
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-briefcase"></i>
              </FeatureIcon>
              <h3>Job Market Analysis</h3>
              <p>Track job postings, salary trends, and employment opportunities across job boards.</p>
            </FeatureCard>
            
            <FeatureCard
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              viewport={{ once: true }}
            >
              <FeatureIcon>
                <i className="fas fa-gamepad"></i>
              </FeatureIcon>
              <h3>Sports & Gaming</h3>
              <p>Monitor sports scores, betting odds, and gaming statistics from various platforms.</p>
            </FeatureCard>
          </FeaturesGrid>
        </Container>
      </FeaturesSection>

      <PricingSection id="pricing">
        <Container>
          <SectionTitle>
            <h2>Choose Your Plan</h2>
            <p>Start free and upgrade as you grow</p>
          </SectionTitle>
          <PricingGrid>
            {plans.map((plan, index) => (
              <PricingCard
                key={index}
                className={plan.featured ? 'featured' : ''}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <PlanName>{plan.name}</PlanName>
                <PlanPrice>{plan.price}</PlanPrice>
                <PlanPeriod>{plan.period}</PlanPeriod>
                <PlanFeatures>
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className={!feature.available ? 'unavailable' : ''}>
                      <i className={feature.available ? 'fas fa-check' : 'fas fa-times'}></i>
                      {feature.text}
                    </li>
                  ))}
                </PlanFeatures>
                <Link to="/register" className="btn btn-primary" style={{ width: '100%' }}>
                  Get Started
                </Link>
              </PricingCard>
            ))}
          </PricingGrid>
        </Container>
      </PricingSection>
    </LandingContainer>
  );
};

export default LandingPage;