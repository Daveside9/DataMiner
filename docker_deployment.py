#!/usr/bin/env python3
"""
DataMiner Pro - Docker Deployment System
Deploy autonomous AI agent in Docker containers for 24/7 operation
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def create_dockerfile():
    """Create Dockerfile for the autonomous agent"""
    dockerfile_content = '''
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    unzip \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \\
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \\
    && apt-get update \\
    && apt-get install -y google-chrome-stable \\
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \\
    && mkdir -p /opt/chromedriver-$CHROMEDRIVER_VERSION \\
    && curl -sS -o /tmp/chromedriver_linux64.zip http://chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip \\
    && unzip -qq /tmp/chromedriver_linux64.zip -d /opt/chromedriver-$CHROMEDRIVER_VERSION \\
    && rm /tmp/chromedriver_linux64.zip \\
    && chmod +x /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver \\
    && ln -fs /opt/chromedriver-$CHROMEDRIVER_VERSION/chromedriver /usr/local/bin/chromedriver

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Expose monitoring port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import sqlite3; conn = sqlite3.connect('autonomous_agent.db'); cursor = conn.cursor(); cursor.execute('SELECT status FROM agent_status WHERE id = 1'); result = cursor.fetchone(); conn.close(); exit(0 if result and result[0] == 'running' else 1)"

# Run the autonomous agent
CMD ["python", "autonomous_ai_agent.py"]
'''
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Dockerfile created")

def create_docker_compose():
    """Create docker-compose.yml for multi-service deployment"""
    compose_content = '''
version: '3.8'

services:
  dataminer-agent:
    build: .
    container_name: dataminer-autonomous-agent
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./agent_config.json:/app/agent_config.json
    ports:
      - "8080:8080"
    environment:
      - PYTHONUNBUFFERED=1
      - TZ=UTC
    networks:
      - dataminer-network
    depends_on:
      - redis
      - postgres
    
  redis:
    image: redis:7-alpine
    container_name: dataminer-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - dataminer-network
  
  postgres:
    image: postgres:15-alpine
    container_name: dataminer-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: dataminer
      POSTGRES_USER: dataminer
      POSTGRES_PASSWORD: dataminer_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - dataminer-network
  
  monitoring:
    image: prom/prometheus:latest
    container_name: dataminer-monitoring
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - dataminer-network
  
  grafana:
    image: grafana/grafana:latest
    container_name: dataminer-grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - dataminer-network

volumes:
  redis_data:
  postgres_data:
  grafana_data:

networks:
  dataminer-network:
    driver: bridge
'''
    
    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)
    
    print("✅ docker-compose.yml created")

def create_requirements():
    """Create requirements.txt for Docker"""
    requirements = '''
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.0
webdriver-manager==4.0.1
schedule==1.2.0
flask==2.3.3
flask-cors==4.0.0
pillow==10.0.1
pandas==2.1.1
numpy==1.24.3
scikit-learn==1.3.0
openai==0.28.1
boto3==1.29.7
redis==5.0.1
psycopg2-binary==2.9.7
prometheus-client==0.17.1
'''
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ requirements.txt created")

def create_kubernetes_deployment():
    """Create Kubernetes deployment files"""
    k8s_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dataminer-agent
  labels:
    app: dataminer-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dataminer-agent
  template:
    metadata:
      labels:
        app: dataminer-agent
    spec:
      containers:
      - name: dataminer-agent
        image: dataminer/autonomous-agent:latest
        ports:
        - containerPort: 8080
        env:
        - name: PYTHONUNBUFFERED
          value: "1"
        volumeMounts:
        - name: config-volume
          mountPath: /app/agent_config.json
          subPath: agent_config.json
        - name: data-volume
          mountPath: /app/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: config-volume
        configMap:
          name: dataminer-config
      - name: data-volume
        persistentVolumeClaim:
          claimName: dataminer-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: dataminer-agent-service
spec:
  selector:
    app: dataminer-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dataminer-data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
'''
    
    with open('k8s-deployment.yaml', 'w') as f:
        f.write(k8s_deployment)
    
    print("✅ Kubernetes deployment files created")

def create_cloud_deployment_scripts():
    """Create cloud deployment scripts"""
    
    # AWS deployment script
    aws_script = '''#!/bin/bash
# AWS ECS Deployment Script for DataMiner Autonomous Agent

# Variables
CLUSTER_NAME="dataminer-cluster"
SERVICE_NAME="dataminer-agent"
TASK_DEFINITION="dataminer-agent-task"
IMAGE_URI="your-account.dkr.ecr.us-east-1.amazonaws.com/dataminer-agent:latest"

echo "🚀 Deploying DataMiner Agent to AWS ECS..."

# Create ECS cluster
aws ecs create-cluster --cluster-name $CLUSTER_NAME

# Register task definition
aws ecs register-task-definition \\
    --family $TASK_DEFINITION \\
    --network-mode awsvpc \\
    --requires-compatibilities FARGATE \\
    --cpu 512 \\
    --memory 1024 \\
    --execution-role-arn arn:aws:iam::your-account:role/ecsTaskExecutionRole \\
    --container-definitions '[
        {
            "name": "dataminer-agent",
            "image": "'$IMAGE_URI'",
            "portMappings": [
                {
                    "containerPort": 8080,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/dataminer-agent",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]'

# Create service
aws ecs create-service \\
    --cluster $CLUSTER_NAME \\
    --service-name $SERVICE_NAME \\
    --task-definition $TASK_DEFINITION \\
    --desired-count 1 \\
    --launch-type FARGATE \\
    --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"

echo "✅ Deployment completed!"
'''
    
    with open('deploy-aws.sh', 'w') as f:
        f.write(aws_script)
    
    # Make executable
    os.chmod('deploy-aws.sh', 0o755)
    
    print("✅ AWS deployment script created")

def create_monitoring_dashboard():
    """Create monitoring dashboard"""
    dashboard_code = '''#!/usr/bin/env python3
"""
DataMiner Pro - Monitoring Dashboard
Web dashboard to monitor autonomous agent status
"""

from flask import Flask, render_template, jsonify
import sqlite3
import json
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    conn = sqlite3.connect('autonomous_agent.db')
    cursor = conn.cursor()
    
    # Get agent status
    cursor.execute('SELECT * FROM agent_status WHERE id = 1')
    status_row = cursor.fetchone()
    
    # Get active tasks
    cursor.execute('SELECT COUNT(*) FROM scraping_tasks WHERE active = 1')
    active_tasks = cursor.fetchone()[0]
    
    # Get recent results
    cursor.execute('''
        SELECT COUNT(*) FROM scraping_results 
        WHERE created_at > datetime('now', '-1 hour')
    ''')
    recent_results = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'status': status_row[1] if status_row else 'unknown',
        'last_heartbeat': status_row[2] if status_row else None,
        'active_tasks': active_tasks,
        'recent_results': recent_results,
        'uptime': 'Running' if status_row and status_row[1] == 'running' else 'Stopped'
    })

@app.route('/api/tasks')
def get_tasks():
    conn = sqlite3.connect('autonomous_agent.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scraping_tasks')
    tasks = cursor.fetchall()
    
    conn.close()
    
    task_list = []
    for task in tasks:
        task_list.append({
            'id': task[0],
            'name': task[1],
            'url': task[2],
            'category': task[3],
            'interval_minutes': task[4],
            'active': bool(task[6]),
            'last_run': task[7],
            'next_run': task[8]
        })
    
    return jsonify(task_list)

@app.route('/api/results/<task_id>')
def get_task_results(task_id):
    conn = sqlite3.connect('autonomous_agent.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM scraping_results 
        WHERE task_id = ? 
        ORDER BY created_at DESC 
        LIMIT 50
    ''', (task_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    result_list = []
    for result in results:
        result_list.append({
            'timestamp': result[2],
            'status': result[5],
            'changes_detected': bool(result[7]),
            'ai_insights': result[8]
        })
    
    return jsonify(result_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
'''
    
    with open('monitoring_dashboard.py', 'w') as f:
        f.write(dashboard_code)
    
    print("✅ Monitoring dashboard created")

def main():
    """Main deployment setup function"""
    print("🐳 DataMiner Pro - Docker Deployment Setup")
    print("=" * 50)
    
    # Create all deployment files
    create_dockerfile()
    create_docker_compose()
    create_requirements()
    create_kubernetes_deployment()
    create_cloud_deployment_scripts()
    create_monitoring_dashboard()
    
    print("\n🎯 Deployment Options Created:")
    print("  📦 Docker: Use 'docker-compose up -d'")
    print("  ☸️  Kubernetes: Use 'kubectl apply -f k8s-deployment.yaml'")
    print("  ☁️  AWS ECS: Run './deploy-aws.sh'")
    print("  📊 Monitoring: Access dashboard at http://localhost:8080")
    
    print("\n🚀 Quick Start:")
    print("  1. Configure agent_config.json with your settings")
    print("  2. Run: docker-compose up -d")
    print("  3. Access monitoring at http://localhost:8080")
    print("  4. View logs: docker-compose logs -f dataminer-agent")
    
    print("\n✅ All deployment files created successfully!")

if __name__ == "__main__":
    main()