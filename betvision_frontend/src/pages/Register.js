import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const RegisterContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
`;

const RegisterCard = styled(motion.div)`
  background: white;
  border-radius: 15px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  overflow: hidden;
  width: 100%;
  max-width: 500px;
`;

const RegisterHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;

  h1 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
  }

  p {
    opacity: 0.9;
  }
`;

const RegisterBody = styled.div`
  padding: 2rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-weight: 600;
  color: #2c3e50;
`;

const Input = styled.input`
  padding: 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;

  &:focus {
    outline: none;
    border-color: #667eea;
  }

  &.error {
    border-color: #dc3545;
  }
`;

const ErrorMessage = styled.span`
  color: #dc3545;
  font-size: 0.875rem;
`;

const SubmitButton = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const AuthSwitch = styled.div`
  text-align: center;
  margin-top: 1rem;

  a {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const BackToHome = styled(Link)`
  position: absolute;
  top: 2rem;
  left: 2rem;
  color: white;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  transition: opacity 0.3s ease;

  &:hover {
    opacity: 0.8;
  }

  @media (max-width: 768px) {
    top: 1rem;
    left: 1rem;
  }
`;

const Register = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    password: '',
    password_confirm: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.full_name) {
      newErrors.full_name = 'Full name is required';
    }

    if (!formData.username) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (!formData.password_confirm) {
      newErrors.password_confirm = 'Please confirm your password';
    } else if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      const result = await register(formData);
      
      if (result.success) {
        navigate('/dashboard');
      } else {
        if (result.errors) {
          // Handle Django validation errors
          const formattedErrors = {};
          Object.keys(result.errors).forEach(key => {
            if (Array.isArray(result.errors[key])) {
              formattedErrors[key] = result.errors[key][0];
            } else {
              formattedErrors[key] = result.errors[key];
            }
          });
          setErrors(formattedErrors);
        } else {
          toast.error('Registration failed. Please try again.');
        }
      }
    } catch (error) {
      toast.error('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <RegisterContainer>
      <BackToHome to="/">
        <i className="fas fa-arrow-left"></i>
        Back to Home
      </BackToHome>
      
      <RegisterCard
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <RegisterHeader>
          <h1>Join BetVision Pro</h1>
          <p>Create your free account and start monitoring</p>
        </RegisterHeader>
        
        <RegisterBody>
          <Form onSubmit={handleSubmit}>
            <FormGroup>
              <Label htmlFor="full_name">Full Name</Label>
              <Input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                className={errors.full_name ? 'error' : ''}
                placeholder="Enter your full name"
              />
              {errors.full_name && <ErrorMessage>{errors.full_name}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="username">Username</Label>
              <Input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className={errors.username ? 'error' : ''}
                placeholder="Choose a username"
              />
              {errors.username && <ErrorMessage>{errors.username}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="email">Email Address</Label>
              <Input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter your email"
              />
              {errors.email && <ErrorMessage>{errors.email}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="password">Password</Label>
              <Input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={errors.password ? 'error' : ''}
                placeholder="Create a password"
              />
              {errors.password && <ErrorMessage>{errors.password}</ErrorMessage>}
            </FormGroup>

            <FormGroup>
              <Label htmlFor="password_confirm">Confirm Password</Label>
              <Input
                type="password"
                id="password_confirm"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleChange}
                className={errors.password_confirm ? 'error' : ''}
                placeholder="Confirm your password"
              />
              {errors.password_confirm && <ErrorMessage>{errors.password_confirm}</ErrorMessage>}
            </FormGroup>

            <SubmitButton type="submit" disabled={loading}>
              {loading && <i className="fas fa-spinner fa-spin"></i>}
              Create Account
            </SubmitButton>
          </Form>

          <AuthSwitch>
            Already have an account? <Link to="/login">Sign In</Link>
          </AuthSwitch>
        </RegisterBody>
      </RegisterCard>
    </RegisterContainer>
  );
};

export default Register;