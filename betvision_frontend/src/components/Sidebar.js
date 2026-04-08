import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';

const SidebarContainer = styled.aside`
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  height: fit-content;
  min-width: 250px;

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavMenu = styled.ul`
  list-style: none;
`;

const NavItem = styled.li`
  margin-bottom: 0.5rem;
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  color: #666;
  text-decoration: none;
  border-radius: 5px;
  transition: all 0.3s ease;

  &:hover,
  &.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  i {
    width: 20px;
    text-align: center;
  }
`;

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/dashboard', icon: 'fas fa-tachometer-alt', label: 'Dashboard' },
    { path: '/virtual-sports', icon: 'fas fa-futbol', label: '⚽ Virtual Sports AI' },
    { path: '/monitoring', icon: 'fas fa-eye', label: 'Monitoring' },
    { path: '/sessions', icon: 'fas fa-list', label: 'Sessions' },
    { path: '/analytics', icon: 'fas fa-chart-bar', label: 'Analytics' },
    { path: '/profile', icon: 'fas fa-user', label: 'Profile' },
  ];

  return (
    <SidebarContainer>
      <nav>
        <NavMenu>
          {menuItems.map((item) => (
            <NavItem key={item.path}>
              <NavLink 
                to={item.path}
                className={location.pathname === item.path ? 'active' : ''}
              >
                <i className={item.icon}></i>
                {item.label}
              </NavLink>
            </NavItem>
          ))}
        </NavMenu>
      </nav>
    </SidebarContainer>
  );
};

export default Sidebar;