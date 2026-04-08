import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import Layout from '../components/Layout';
import toast from 'react-hot-toast';

const ExtractorContainer = styled.div`
  padding: 2rem;
`;

const PageHeader = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const PageTitle = styled.h1`
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
`;

const PageSubtitle = styled.p`
  color: #666;
  font-size: 1.1rem;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const StatCard = styled(motion.div)`
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  border: 2px solid transparent;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
  }
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 0.5rem;
`;

const StatLabel = styled.div`
  color: #666;
  font-size: 0.9rem;
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 2rem;
  margin-bottom: 2rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const ControlPanel = styled.div`
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  height: fit-content;
`;

const ResultsPanel = styled.div`
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
`;

const SectionTitle = styled.h2`
  color: #2c3e50;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
`;

const Select = styled.select`
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.3s ease;
  width: 100%;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover {
    transform: translateY(-2px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const SecondaryButton = styled(Button)`
  background: #6c757d;
`;

const StatusIndicator = styled.div`
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  display: ${props => props.show ? 'block' : 'none'};
  
  &.success {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }
  
  &.error {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }
  
  &.info {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  display: ${props => props.show ? 'block' : 'none'};
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const ResultsGrid = styled.div`
  display: grid;
  gap: 1rem;
  max-height: 600px;
  overflow-y: auto;
`;

const MatchCard = styled.div`
  border: 1px solid #e1e8ed;
  border-radius: 10px;
  padding: 1rem;
  transition: all 0.3s ease;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  }
`;

const MatchHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
`;

const MatchTeams = styled.div`
  font-weight: 600;
  color: #2c3e50;
`;

const MatchScore = styled.div`
  font-size: 1.2rem;
  font-weight: bold;
  color: #667eea;
`;

const MatchDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
`;

const ConfidenceBadge = styled.span`
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  
  &.high {
    background: #d4edda;
    color: #155724;
  }
  
  &.medium {
    background: #fff3cd;
    color: #856404;
  }
  
  &.low {
    background: #f8d7da;
    color: #721c24;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const BettingVisualExtractor = () => {
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractedMatches, setExtractedMatches] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [status, setStatus] = useState({ show: false, message: '', type: 'info' });
  const [progress, setProgress] = useState(0);
  const [stats, setStats] = useState({
    totalMatches: 0,
    successRate: 0,
    avgConfidence: 0,
    sitesSupported: 5
  });

  const [formData, setFormData] = useState({
    bettingSite: '',
    username: '',
    password: '',
    maxMatches: 25,
    ocrEngine: 'easyocr',
    enhanceContrast: true,
    denoise: true,
    sharpen: true,
    threshold: true,
    headlessMode: false,
    saveScreenshots: true
  });

  const bettingSites = [
    { id: 'flashscore', name: 'FlashScore', loginRequired: false },
    { id: 'livescore', name: 'LiveScore', loginRequired: false },
    { id: 'bet365', name: 'Bet365', loginRequired: true },
    { id: 'bet9ja', name: 'Bet9ja', loginRequired: false },
    { id: 'betway', name: 'Betway', loginRequired: true }
  ];

  useEffect(() => {
    loadStats();
    loadPreviousResults();
  }, []);

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/betting-extractor/stats/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const loadPreviousResults = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/betting-extractor/results/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setExtractedMatches(data.results || []);
      }
    } catch (error) {
      console.error('Error loading results:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const showStatus = (message, type) => {
    setStatus({ show: true, message, type });
    setTimeout(() => {
      setStatus(prev => ({ ...prev, show: false }));
    }, 5000);
  };

  const startExtraction = async () => {
    if (!formData.bettingSite) {
      showStatus('Please select a betting site', 'error');
      return;
    }

    setIsExtracting(true);
    setProgress(0);

    try {
      const response = await fetch('http://localhost:8000/api/betting-extractor/extract/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          site: formData.bettingSite,
          username: formData.username,
          password: formData.password,
          max_matches: formData.maxMatches,
          ocr_engine: formData.ocrEngine,
          enhance_contrast: formData.enhanceContrast,
          denoise: formData.denoise,
          sharpen: formData.sharpen,
          threshold: formData.threshold,
          headless_mode: formData.headlessMode,
          save_screenshots: formData.saveScreenshots
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSession(data.session_id);
        showStatus('Extraction started successfully!', 'success');
        
        // Start polling for progress
        pollProgress(data.session_id);
      } else {
        throw new Error('Failed to start extraction');
      }
    } catch (error) {
      showStatus(`Error starting extraction: ${error.message}`, 'error');
      setIsExtracting(false);
    }
  };

  const pollProgress = async (sessionId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/betting-extractor/status/${sessionId}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });
        if (response.ok) {
          const data = await response.json();
          
          setProgress(data.progress || 0);
          
          if (data.status === 'completed') {
            clearInterval(pollInterval);
            setIsExtracting(false);
            setProgress(100);
            showStatus(data.message, 'success');
            
            if (data.results) {
              setExtractedMatches(data.results);
            }
            
            loadStats();
            toast.success(`Extraction completed! Found ${data.matches_found} matches.`);
          } else if (data.status === 'error') {
            clearInterval(pollInterval);
            setIsExtracting(false);
            showStatus(data.message, 'error');
            toast.error('Extraction failed');
          } else if (data.status === 'stopped') {
            clearInterval(pollInterval);
            setIsExtracting(false);
            showStatus('Extraction stopped', 'info');
          }
        }
      } catch (error) {
        console.error('Error polling progress:', error);
      }
    }, 2000);
  };

  const stopExtraction = async () => {
    if (currentSession) {
      try {
        await fetch(`http://localhost:8000/api/betting-extractor/stop/${currentSession}/`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });
        showStatus('Stopping extraction...', 'info');
      } catch (error) {
        console.error('Error stopping extraction:', error);
      }
    }
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };

  const selectedSite = bettingSites.find(site => site.id === formData.bettingSite);

  return (
    <Layout>
      <ExtractorContainer>
        <PageHeader>
          <PageTitle>
            <i className="fas fa-robot"></i>
            Betting Visual History Extractor
          </PageTitle>
          <PageSubtitle>
            Advanced AI-powered system to extract visual betting history from any betting site
          </PageSubtitle>
        </PageHeader>

        <StatsGrid>
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatNumber>{stats.totalMatches}</StatNumber>
            <StatLabel>Total Matches</StatLabel>
          </StatCard>
          
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatNumber>{stats.successRate}%</StatNumber>
            <StatLabel>Success Rate</StatLabel>
          </StatCard>
          
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatNumber>{stats.avgConfidence}%</StatNumber>
            <StatLabel>Avg Confidence</StatLabel>
          </StatCard>
          
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatNumber>{stats.sitesSupported}</StatNumber>
            <StatLabel>Sites Supported</StatLabel>
          </StatCard>
        </StatsGrid>

        <MainContent>
          <ControlPanel>
            <SectionTitle>
              <i className="fas fa-cogs"></i>
              Extraction Settings
            </SectionTitle>

            <StatusIndicator show={status.show} className={status.type}>
              {status.message}
            </StatusIndicator>

            <ProgressBar show={isExtracting}>
              <ProgressFill progress={progress} />
            </ProgressBar>

            <FormGroup>
              <Label>Betting Site</Label>
              <Select
                value={formData.bettingSite}
                onChange={(e) => handleInputChange('bettingSite', e.target.value)}
              >
                <option value="">Select a betting site</option>
                {bettingSites.map(site => (
                  <option key={site.id} value={site.id}>
                    {site.name} {site.loginRequired ? '(Login Required)' : ''}
                  </option>
                ))}
              </Select>
            </FormGroup>

            {selectedSite?.loginRequired && (
              <>
                <FormGroup>
                  <Label>Username</Label>
                  <Input
                    type="text"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    placeholder="Enter username"
                  />
                </FormGroup>

                <FormGroup>
                  <Label>Password</Label>
                  <Input
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    placeholder="Enter password"
                  />
                </FormGroup>
              </>
            )}

            <FormGroup>
              <Label>Maximum Matches to Extract</Label>
              <Select
                value={formData.maxMatches}
                onChange={(e) => handleInputChange('maxMatches', parseInt(e.target.value))}
              >
                <option value={10}>10 matches</option>
                <option value={25}>25 matches</option>
                <option value={50}>50 matches</option>
                <option value={100}>100 matches</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>OCR Engine</Label>
              <Select
                value={formData.ocrEngine}
                onChange={(e) => handleInputChange('ocrEngine', e.target.value)}
              >
                <option value="easyocr">EasyOCR (Recommended)</option>
                <option value="tesseract">Tesseract OCR</option>
              </Select>
            </FormGroup>

            <FormGroup>
              <Label>Image Processing Options</Label>
              <CheckboxGroup>
                <input
                  type="checkbox"
                  checked={formData.enhanceContrast}
                  onChange={(e) => handleInputChange('enhanceContrast', e.target.checked)}
                />
                <Label>Enhance Contrast</Label>
              </CheckboxGroup>
              <CheckboxGroup>
                <input
                  type="checkbox"
                  checked={formData.denoise}
                  onChange={(e) => handleInputChange('denoise', e.target.checked)}
                />
                <Label>Denoise Images</Label>
              </CheckboxGroup>
              <CheckboxGroup>
                <input
                  type="checkbox"
                  checked={formData.sharpen}
                  onChange={(e) => handleInputChange('sharpen', e.target.checked)}
                />
                <Label>Sharpen Images</Label>
              </CheckboxGroup>
              <CheckboxGroup>
                <input
                  type="checkbox"
                  checked={formData.headlessMode}
                  onChange={(e) => handleInputChange('headlessMode', e.target.checked)}
                />
                <Label>Headless Mode</Label>
              </CheckboxGroup>
            </FormGroup>

            <Button onClick={startExtraction} disabled={isExtracting}>
              {isExtracting ? (
                <>
                  <LoadingSpinner />
                  Extracting...
                </>
              ) : (
                <>
                  <i className="fas fa-play"></i>
                  Start Extraction
                </>
              )}
            </Button>

            <SecondaryButton onClick={stopExtraction} disabled={!isExtracting}>
              <i className="fas fa-stop"></i>
              Stop Extraction
            </SecondaryButton>
          </ControlPanel>

          <ResultsPanel>
            <SectionTitle>
              <i className="fas fa-chart-bar"></i>
              Extraction Results
              <span style={{ fontSize: '0.9rem', color: '#666', marginLeft: '0.5rem' }}>
                ({extractedMatches.length} matches)
              </span>
            </SectionTitle>

            <ResultsGrid>
              {extractedMatches.length === 0 ? (
                <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                  <i className="fas fa-search" style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }}></i>
                  <p>No matches extracted yet. Start an extraction to see results here.</p>
                </div>
              ) : (
                extractedMatches.map((match, index) => (
                  <MatchCard key={match.match_id || index}>
                    <MatchHeader>
                      <MatchTeams>{match.home_team} vs {match.away_team}</MatchTeams>
                      <MatchScore>{match.home_score} - {match.away_score}</MatchScore>
                    </MatchHeader>
                    <MatchDetails>
                      <div>
                        <i className="fas fa-calendar"></i> {match.date}
                      </div>
                      <div>
                        <i className="fas fa-trophy"></i> {match.competition}
                      </div>
                      <div>
                        <i className="fas fa-chart-line"></i> {match.result_type?.replace('_', ' ').toUpperCase()}
                      </div>
                      <div>
                        <ConfidenceBadge className={getConfidenceClass(match.confidence_score)}>
                          {Math.round((match.confidence_score || 0) * 100)}% confidence
                        </ConfidenceBadge>
                      </div>
                    </MatchDetails>
                  </MatchCard>
                ))
              )}
            </ResultsGrid>
          </ResultsPanel>
        </MainContent>
      </ExtractorContainer>
    </Layout>
  );
};

export default BettingVisualExtractor;