import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import Layout from '../components/Layout';
import toast from 'react-hot-toast';

const SportsContainer = styled.div`
  padding: 2rem;
`;

const PageHeader = styled.div`
  margin-bottom: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const PageSubtitle = styled.p`
  color: #666;
  font-size: 1.1rem;
`;

const SportsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const SportsCard = styled(motion.div)`
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
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
  margin-bottom: 1.5rem;
`;

const CardIcon = styled.div`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
`;

const CardTitle = styled.h3`
  color: #2c3e50;
  margin: 0;
`;

const CardDescription = styled.p`
  color: #666;
  margin: 0;
  font-size: 0.9rem;
`;

const QuickActions = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
`;

const ActionButton = styled.button`
  background: ${props => props.primary ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#f8f9fa'};
  color: ${props => props.primary ? 'white' : '#333'};
  border: 1px solid ${props => props.primary ? 'transparent' : '#e1e8ed'};
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const LiveDataSection = styled.div`
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
`;

const LiveHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
`;

const LiveTitle = styled.h2`
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const LiveIndicator = styled.div`
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: ${props => props.active ? '#28a745' : '#dc3545'};
  animation: ${props => props.active ? 'pulse 2s infinite' : 'none'};

  @keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
  }
`;

const MatchesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

const MatchCard = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  background: #f8f9fa;
`;

const MatchTeams = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const TeamName = styled.span`
  font-weight: 500;
  min-width: 100px;
`;

const MatchScore = styled.div`
  font-size: 1.2rem;
  font-weight: bold;
  color: #667eea;
  min-width: 60px;
  text-align: center;
`;

const MatchTime = styled.div`
  font-size: 0.9rem;
  color: #666;
`;

const PredictionCard = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
`;

const PredictionTitle = styled.h4`
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const PredictionText = styled.p`
  margin: 0;
  opacity: 0.9;
`;

const ConfigPanel = styled.div`
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
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

const Sports = () => {
  const [liveMatches, setLiveMatches] = useState([]);
  const [predictions, setPredictions] = useState({});
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [historicalData, setHistoricalData] = useState([]);
  const [teamAnalysis, setTeamAnalysis] = useState(null);
  const [screenMonitoring, setScreenMonitoring] = useState(false);
  const [monitoringConfig, setMonitoringConfig] = useState({
    source: 'flashscore',
    teams: '',
    interval: 60,
    duration: 30,
    enableScreenCapture: false,
    enableHistoryMining: true
  });

  const sportsCategories = [
    {
      id: 'football',
      title: 'Football/Soccer',
      icon: 'fas fa-futbol',
      description: 'Premier League, Champions League, World Cup',
      sources: ['flashscore.com', 'livescore.com', 'bbc.com/sport'],
      features: ['Live scores', 'Team analysis', 'Match predictions', 'Historical data mining']
    },
    {
      id: 'basketball',
      title: 'Basketball',
      icon: 'fas fa-basketball-ball',
      description: 'NBA, EuroLeague, NCAA',
      sources: ['espn.com', 'nba.com', 'flashscore.com'],
      features: ['Live scores', 'Player stats', 'Game predictions', 'Season analysis']
    },
    {
      id: 'tennis',
      title: 'Tennis',
      icon: 'fas fa-table-tennis',
      description: 'ATP, WTA, Grand Slams',
      sources: ['flashscore.com', 'atptour.com', 'wtatennis.com'],
      features: ['Live scores', 'Rankings', 'Match analysis', 'Tournament tracking']
    },
    {
      id: 'data_mining',
      title: 'Sports Data Mining',
      icon: 'fas fa-database',
      description: 'Historical data extraction and analysis',
      sources: ['Multiple sports sites', 'Historical databases'],
      features: ['Pattern analysis', 'Historical trends', 'Performance metrics', 'Predictive modeling']
    }
  ];

  const comprehensiveAnalysis = async () => {
    if (!monitoringConfig.bet9jaUrl) {
      toast.error('Please enter a Bet9ja URL');
      return;
    }

    try {
      toast.loading('Performing comprehensive team analysis... This may take a moment.');
      
      const response = await fetch('http://localhost:5003/api/analyze-teams-comprehensive', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: monitoringConfig.bet9jaUrl
        })
      });

      const result = await response.json();

      if (result.success) {
        const analysis = result.analysis;
        const match = analysis.match_info;
        const predictions = analysis.predictions;
        
        toast.success(`Complete analysis ready: ${match.home_team} vs ${match.away_team}`);
        
        // Store comprehensive analysis
        setTeamAnalysis(analysis);
        
        // Show key insights
        const homeWin = predictions.match_result?.home_win || 0;
        const draw = predictions.match_result?.draw || 0;
        const awayWin = predictions.match_result?.away_win || 0;
        
        console.log('Comprehensive Analysis:', analysis);
        
        // You could show a modal or update UI with detailed analysis
        alert(`Analysis Complete!\n\n${match.home_team} vs ${match.away_team}\n\nPredictions:\nHome Win: ${homeWin}%\nDraw: ${draw}%\nAway Win: ${awayWin}%\n\nCheck console for full details!`);
        
      } else {
        toast.error(result.error || 'Failed to perform comprehensive analysis');
      }
    } catch (error) {
      console.error('Comprehensive analysis error:', error);
      toast.error('Failed to perform comprehensive analysis');
    }
  };

  const predictBet9jaScore = async () => {
    if (!monitoringConfig.bet9jaUrl) {
      toast.error('Please enter a Bet9ja URL');
      return;
    }

    try {
      toast.loading('Predicting match score using AI...');
      
      const response = await fetch('http://localhost:5003/api/predict-from-bet9ja', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: monitoringConfig.bet9jaUrl
        })
      });

      const result = await response.json();

      if (result.success) {
        const prediction = result.prediction;
        const teams = result.bet9ja_data.teams;
        
        toast.success(`AI Prediction: ${teams.home_team} ${prediction.predicted_score} ${teams.away_team} (${prediction.confidence}% confidence)`);
        
        // Update predictions state
        setPredictions(prev => ({
          ...prev,
          [teams.home_team + '_vs_' + teams.away_team]: prediction
        }));
        
        console.log('AI Prediction:', prediction);
      } else {
        toast.error(result.error || 'Failed to predict score');
      }
    } catch (error) {
      console.error('Score prediction error:', error);
      toast.error('Failed to predict score');
    }
  };

  const extractBet9jaHistory = async () => {
    if (!monitoringConfig.bet9jaUrl) {
      toast.error('Please enter a Bet9ja URL');
      return;
    }

    try {
      toast.loading('Extracting Bet9ja match history...');
      
      const response = await fetch('http://localhost:5003/api/extract-bet9ja-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: monitoringConfig.bet9jaUrl
        })
      });

      const result = await response.json();

      if (result.success) {
        toast.success(`Bet9ja history extracted! Found ${result.teams_found?.home_team} vs ${result.teams_found?.away_team}`);
        
        // Update UI with extracted data
        setTeamAnalysis(result.data);
        
        // Show results
        console.log('Bet9ja Data:', result.data);
      } else {
        toast.error(result.error || 'Failed to extract Bet9ja history');
      }
    } catch (error) {
      console.error('Bet9ja extraction error:', error);
      toast.error('Failed to extract Bet9ja history');
    }
  };

  const startLiveMonitoring = async (category) => {
    try {
      setIsMonitoring(true);
      toast.loading('Starting comprehensive sports monitoring...');

      // Start multiple monitoring services
      const promises = [];

      // 1. Real-time sports system
      promises.push(
        fetch('http://localhost:5001/api/start-monitoring', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: getSportsUrl(category),
            duration: monitoringConfig.duration,
            interval: monitoringConfig.interval,
            specific_teams: monitoringConfig.teams ? monitoringConfig.teams.split(',').map(t => t.trim()) : []
          })
        })
      );

      // 2. Screen monitoring if enabled
      if (monitoringConfig.enableScreenCapture) {
        promises.push(
          fetch('http://localhost:5002/api/start-visual-monitoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: getSportsUrl(category),
              interval: monitoringConfig.interval,
              duration: monitoringConfig.duration
            })
          })
        );
        setScreenMonitoring(true);
      }

      // 3. Historical data mining if enabled
      if (monitoringConfig.enableHistoryMining && monitoringConfig.teams) {
        promises.push(startHistoricalDataMining());
      }

      const responses = await Promise.all(promises);
      const allSuccessful = responses.every(response => response.ok);

      if (allSuccessful) {
        toast.success('Comprehensive monitoring started!');
        startPollingLiveData();
      } else {
        throw new Error('Some monitoring services failed to start');
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
      toast.error('Failed to start monitoring');
      setIsMonitoring(false);
      setScreenMonitoring(false);
    }
  };

  const stopLiveMonitoring = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/stop-monitoring', {
        method: 'POST'
      });

      if (response.ok) {
        setIsMonitoring(false);
        toast.success('Monitoring stopped');
      }
    } catch (error) {
      console.error('Error stopping monitoring:', error);
      toast.error('Failed to stop monitoring');
    }
  };

  const startPollingLiveData = () => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5001/api/live-matches');
        if (response.ok) {
          const data = await response.json();
          setLiveMatches(Object.values(data.matches || {}));
          setPredictions(data.predictions || {});
          
          if (!data.monitoring_active) {
            setIsMonitoring(false);
            clearInterval(pollInterval);
          }
        }
      } catch (error) {
        console.error('Error polling live data:', error);
      }
    }, 5000); // Poll every 5 seconds

    // Store interval ID for cleanup
    window.sportsPollingInterval = pollInterval;
  };

  const getSportsUrl = (category) => {
    const urls = {
      football: 'https://www.flashscore.com/football/',
      basketball: 'https://www.flashscore.com/basketball/',
      tennis: 'https://www.flashscore.com/tennis/',
      betting: 'https://www.bet9ja.com/sport/football'
    };
    return urls[category] || urls.football;
  };

  const generatePrediction = async (matchId) => {
    try {
      const response = await fetch('http://localhost:5001/api/predict-score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ match_id: matchId })
      });

      if (response.ok) {
        const result = await response.json();
        setPredictions(prev => ({
          ...prev,
          [matchId]: result.prediction
        }));
        toast.success('Prediction generated!');
      }
    } catch (error) {
      console.error('Error generating prediction:', error);
      toast.error('Failed to generate prediction');
    }
  };

  const startHistoricalDataMining = async () => {
    try {
      const teams = monitoringConfig.teams.split(',').map(t => t.trim());
      
      for (const team of teams) {
        const response = await fetch('http://localhost:8000/api/sports/analyze-team/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            team_name: team,
            sport: 'football'
          })
        });

        if (response.ok) {
          const analysis = await response.json();
          setTeamAnalysis(prev => ({
            ...prev,
            [team]: analysis.analysis
          }));
        }
      }
    } catch (error) {
      console.error('Error mining historical data:', error);
    }
  };

  const mineTeamHistory = async (teamName) => {
    try {
      toast.loading(`Mining ${teamName} historical data...`);
      
      // Call the Arsenal analyzer or similar for comprehensive analysis
      const response = await fetch('http://localhost:5001/api/mine-team-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_name: teamName,
          analysis_period: '6_months',
          include_patterns: true,
          include_predictions: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        setHistoricalData(prev => [...prev, data]);
        toast.success(`${teamName} history analysis complete!`);
        
        // Show detailed analysis modal or update UI
        displayTeamAnalysis(data);
      } else {
        throw new Error('Failed to mine historical data');
      }
    } catch (error) {
      console.error('Error mining team history:', error);
      toast.error(`Failed to analyze ${teamName}`);
    }
  };

  const displayTeamAnalysis = (analysisData) => {
    // This would show a detailed modal or update the UI with analysis
    console.log('Team Analysis:', analysisData);
    setTeamAnalysis(analysisData);
  };

  useEffect(() => {
    // Cleanup polling on unmount
    return () => {
      if (window.sportsPollingInterval) {
        clearInterval(window.sportsPollingInterval);
      }
    };
  }, []);

  return (
    <Layout>
      <SportsContainer>
        <PageHeader>
          <PageTitle>
            <i className="fas fa-futbol"></i>
            Sports Data Collection
          </PageTitle>
          <PageSubtitle>
            Real-time sports data monitoring, analysis, and predictions
          </PageSubtitle>
        </PageHeader>

        <SportsGrid>
          {sportsCategories.map((category, index) => (
            <SportsCard
              key={category.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <CardHeader>
                <CardIcon>
                  <i className={category.icon}></i>
                </CardIcon>
                <div>
                  <CardTitle>{category.title}</CardTitle>
                  <CardDescription>{category.description}</CardDescription>
                </div>
              </CardHeader>

              <div>
                <h4>Data Sources:</h4>
                <ul>
                  {category.sources.map((source, idx) => (
                    <li key={idx}>{source}</li>
                  ))}
                </ul>

                <h4>Features:</h4>
                <ul>
                  {category.features.map((feature, idx) => (
                    <li key={idx}>{feature}</li>
                  ))}
                </ul>
              </div>

              <QuickActions>
                <ActionButton 
                  primary 
                  onClick={() => startLiveMonitoring(category.id)}
                  disabled={isMonitoring}
                >
                  <i className="fas fa-play"></i>
                  Start Live Monitoring
                </ActionButton>
                <ActionButton onClick={() => mineTeamHistory('Arsenal')}>
                  <i className="fas fa-database"></i>
                  Mine Data
                </ActionButton>
                {category.id === 'data_mining' && (
                  <ActionButton onClick={() => {
                    // Open data mining interface
                    window.open('/historical-pattern-scraper.html', '_blank');
                  }}>
                    <i className="fas fa-external-link-alt"></i>
                    Open Data Miner
                  </ActionButton>
                )}
              </QuickActions>
            </SportsCard>
          ))}
        </SportsGrid>

        <LiveDataSection>
          <LiveHeader>
            <LiveTitle>
              <LiveIndicator active={isMonitoring} />
              Live Sports Data
            </LiveTitle>
            {isMonitoring && (
              <ActionButton onClick={stopLiveMonitoring}>
                <i className="fas fa-stop"></i>
                Stop Monitoring
              </ActionButton>
            )}
          </LiveHeader>

          {liveMatches.length > 0 ? (
            <MatchesList>
              {liveMatches.map((match, index) => (
                <MatchCard key={index}>
                  <MatchTeams>
                    <TeamName>{match.home_team}</TeamName>
                    <span>vs</span>
                    <TeamName>{match.away_team}</TeamName>
                  </MatchTeams>
                  
                  <MatchScore>
                    {match.history && match.history.length > 0 
                      ? `${match.history[match.history.length - 1].home_score}-${match.history[match.history.length - 1].away_score}`
                      : '0-0'
                    }
                  </MatchScore>
                  
                  <div>
                    <ActionButton onClick={() => generatePrediction(match.match_id || index)}>
                      <i className="fas fa-crystal-ball"></i>
                      Predict
                    </ActionButton>
                  </div>
                </MatchCard>
              ))}
            </MatchesList>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
              {isMonitoring ? (
                <div>
                  <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', marginBottom: '1rem' }}></i>
                  <p>Searching for live matches...</p>
                </div>
              ) : (
                <div>
                  <i className="fas fa-futbol" style={{ fontSize: '2rem', marginBottom: '1rem', opacity: 0.3 }}></i>
                  <p>Start monitoring to see live sports data</p>
                </div>
              )}
            </div>
          )}

          {Object.keys(predictions).length > 0 && (
            <div>
              <h3>AI Predictions</h3>
              {Object.entries(predictions).map(([matchId, prediction]) => (
                <PredictionCard key={matchId}>
                  <PredictionTitle>
                    <i className="fas fa-crystal-ball"></i>
                    Match Prediction
                  </PredictionTitle>
                  <PredictionText>
                    Predicted Score: {prediction.predicted_score} | 
                    Confidence: {prediction.confidence}% | 
                    Reasoning: {prediction.reasoning}
                  </PredictionText>
                </PredictionCard>
              ))}
            </div>
          )}
        </LiveDataSection>

        <ConfigPanel>
          <h3>Advanced Sports Monitoring Configuration</h3>
          
          <FormGroup>
            <Label>Data Source</Label>
            <Select
              value={monitoringConfig.source}
              onChange={(e) => setMonitoringConfig(prev => ({ ...prev, source: e.target.value }))}
            >
              <option value="flashscore">Flashscore.com (Recommended)</option>
              <option value="livescore">Livescore.com</option>
              <option value="bbc">BBC Sport</option>
              <option value="bet9ja">Bet9ja (Nigeria)</option>
              <option value="espn">ESPN Sports</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Bet9ja URL (for specific match history)</Label>
            <Input
              type="text"
              value={monitoringConfig.bet9jaUrl || ''}
              onChange={(e) => setMonitoringConfig(prev => ({ ...prev, bet9jaUrl: e.target.value }))}
              placeholder="https://sports.bet9ja.com/mobile/eventdetail/..."
            />
          </FormGroup>

          <FormGroup>
            <Label>Monitoring Features</Label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={monitoringConfig.enableScreenCapture}
                  onChange={(e) => setMonitoringConfig(prev => ({ 
                    ...prev, 
                    enableScreenCapture: e.target.checked 
                  }))}
                />
                Enable Screen Capture & Visual Monitoring
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={monitoringConfig.enableHistoryMining}
                  onChange={(e) => setMonitoringConfig(prev => ({ 
                    ...prev, 
                    enableHistoryMining: e.target.checked 
                  }))}
                />
                Enable Historical Data Mining
              </label>
            </div>
          </FormGroup>

          <FormGroup>
            <Label>Update Interval</Label>
            <Select
              value={monitoringConfig.interval}
              onChange={(e) => setMonitoringConfig(prev => ({ ...prev, interval: parseInt(e.target.value) }))}
            >
              <option value={15}>15 seconds (High frequency)</option>
              <option value={30}>30 seconds (Recommended)</option>
              <option value={60}>1 minute</option>
              <option value={120}>2 minutes</option>
              <option value={300}>5 minutes</option>
            </Select>
          </FormGroup>

          <FormGroup>
            <Label>Monitoring Duration</Label>
            <Select
              value={monitoringConfig.duration}
              onChange={(e) => setMonitoringConfig(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
            >
              <option value={10}>10 minutes (Quick test)</option>
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes (Recommended)</option>
              <option value={60}>1 hour</option>
              <option value={120}>2 hours</option>
              <option value={240}>4 hours (Extended)</option>
            </Select>
          </FormGroup>

          <div style={{ marginTop: '1.5rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#2c3e50' }}>Quick Actions</h4>
            <QuickActions>
              <ActionButton 
                primary 
                onClick={() => startLiveMonitoring('football')}
                disabled={isMonitoring}
              >
                <i className="fas fa-play"></i>
                Start Full Monitoring
              </ActionButton>
              <ActionButton onClick={() => mineTeamHistory('Arsenal')}>
                <i className="fas fa-database"></i>
                Mine Arsenal Data
              </ActionButton>
              <ActionButton onClick={() => mineTeamHistory('Chelsea')}>
                <i className="fas fa-chart-line"></i>
                Analyze Chelsea
              </ActionButton>
              <ActionButton 
                primary 
                onClick={extractBet9jaHistory}
                disabled={!monitoringConfig.bet9jaUrl}
              >
                <i className="fas fa-external-link-alt"></i>
                Extract Bet9ja History
              </ActionButton>
              <ActionButton 
                onClick={predictBet9jaScore}
                disabled={!monitoringConfig.bet9jaUrl}
              >
                <i className="fas fa-crystal-ball"></i>
                Predict Score
              </ActionButton>
              <ActionButton 
                primary
                onClick={comprehensiveAnalysis}
                disabled={!monitoringConfig.bet9jaUrl}
              >
                <i className="fas fa-chart-line"></i>
                Full Team Analysis
              </ActionButton>
            </QuickActions>
          </div>
        </ConfigPanel>
      </SportsContainer>
    </Layout>
  );
};

export default Sports;