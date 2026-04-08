#!/usr/bin/env python3
"""
DataMiner Pro - Cloud Scheduler
Deploy autonomous agent to cloud platforms with advanced scheduling
"""

import os
import sys
import json
import boto3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

class CloudScheduler:
    """Manages cloud-based scheduling and deployment"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.config = self.load_config(config_file)
        self.cloud_provider = self.config.get('deployment', {}).get('cloud_provider', 'aws')
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration"""
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def deploy_to_aws_lambda(self):
        """Deploy autonomous agent as AWS Lambda functions"""
        print("🚀 Deploying to AWS Lambda...")
        
        # Create Lambda deployment package
        lambda_code = '''
import json
import boto3
import requests
from datetime import datetime
import os

def lambda_handler(event, context):
    """AWS Lambda handler for autonomous scraping"""
    
    # Get task configuration from event
    task_config = event.get('task_config', {})
    
    # Perform scraping
    try:
        url = task_config['url']
        selectors = task_config['selectors']
        
        # Simple scraping logic
        response = requests.get(url, timeout=30)
        
        # Store results in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('dataminer-results')
        
        table.put_item(
            Item={
                'task_id': task_config['id'],
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'status': 'success',
                'data': response.text[:1000]  # First 1000 chars
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Scraping completed successfully',
                'task_id': task_config['id']
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'task_id': task_config.get('id', 'unknown')
            })
        }
'''
        
        # Create deployment package
        with open('lambda_function.py', 'w') as f:
            f.write(lambda_code)
        
        print("✅ Lambda function code created")
        
        # Create CloudFormation template
        cloudformation_template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "DataMiner Autonomous Agent - Serverless",
            "Resources": {
                "DataMinerScrapingFunction": {
                    "Type": "AWS::Lambda::Function",
                    "Properties": {
                        "FunctionName": "dataminer-autonomous-scraper",
                        "Runtime": "python3.9",
                        "Handler": "lambda_function.lambda_handler",
                        "Code": {
                            "ZipFile": lambda_code
                        },
                        "Timeout": 300,
                        "MemorySize": 512,
                        "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]}
                    }
                },
                "LambdaExecutionRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [{
                                "Effect": "Allow",
                                "Principal": {"Service": "lambda.amazonaws.com"},
                                "Action": "sts:AssumeRole"
                            }]
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
                        ]
                    }
                },
                "DataMinerResultsTable": {
                    "Type": "AWS::DynamoDB::Table",
                    "Properties": {
                        "TableName": "dataminer-results",
                        "AttributeDefinitions": [{
                            "AttributeName": "task_id",
                            "AttributeType": "S"
                        }, {
                            "AttributeName": "timestamp",
                            "AttributeType": "S"
                        }],
                        "KeySchema": [{
                            "AttributeName": "task_id",
                            "KeyType": "HASH"
                        }, {
                            "AttributeName": "timestamp",
                            "KeyType": "RANGE"
                        }],
                        "BillingMode": "PAY_PER_REQUEST"
                    }
                },
                "ScheduledRule": {
                    "Type": "AWS::Events::Rule",
                    "Properties": {
                        "Description": "Trigger DataMiner scraping every 5 minutes",
                        "ScheduleExpression": "rate(5 minutes)",
                        "State": "ENABLED",
                        "Targets": [{
                            "Arn": {"Fn::GetAtt": ["DataMinerScrapingFunction", "Arn"]},
                            "Id": "DataMinerScrapingTarget",
                            "Input": json.dumps({
                                "task_config": {
                                    "id": "scheduled_task_1",
                                    "url": "https://example.com",
                                    "selectors": {"title": "h1"}
                                }
                            })
                        }]
                    }
                },
                "PermissionForEventsToInvokeLambda": {
                    "Type": "AWS::Lambda::Permission",
                    "Properties": {
                        "FunctionName": {"Ref": "DataMinerScrapingFunction"},
                        "Action": "lambda:InvokeFunction",
                        "Principal": "events.amazonaws.com",
                        "SourceArn": {"Fn::GetAtt": ["ScheduledRule", "Arn"]}
                    }
                }
            },
            "Outputs": {
                "LambdaFunctionArn": {
                    "Description": "ARN of the Lambda function",
                    "Value": {"Fn::GetAtt": ["DataMinerScrapingFunction", "Arn"]}
                },
                "DynamoDBTableName": {
                    "Description": "Name of the DynamoDB table",
                    "Value": {"Ref": "DataMinerResultsTable"}
                }
            }
        }
        
        with open('cloudformation-template.json', 'w') as f:
            json.dump(cloudformation_template, f, indent=2)
        
        print("✅ CloudFormation template created")
        print("📋 Deploy with: aws cloudformation create-stack --stack-name dataminer-autonomous --template-body file://cloudformation-template.json")
    
    def deploy_to_google_cloud(self):
        """Deploy to Google Cloud Functions"""
        print("🚀 Deploying to Google Cloud Functions...")
        
        # Create Cloud Function code
        cloud_function_code = '''
import functions_framework
import requests
from google.cloud import firestore
from datetime import datetime
import json

@functions_framework.http
def dataminer_scraper(request):
    """Google Cloud Function for autonomous scraping"""
    
    try:
        # Get task configuration
        request_json = request.get_json(silent=True)
        task_config = request_json.get('task_config', {})
        
        # Perform scraping
        url = task_config['url']
        response = requests.get(url, timeout=30)
        
        # Store in Firestore
        db = firestore.Client()
        doc_ref = db.collection('scraping_results').document()
        doc_ref.set({
            'task_id': task_config['id'],
            'timestamp': datetime.now(),
            'url': url,
            'status': 'success',
            'data': response.text[:1000]
        })
        
        return {
            'message': 'Scraping completed successfully',
            'task_id': task_config['id']
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'status': 'failed'
        }, 500

@functions_framework.cloud_event
def scheduled_scraper(cloud_event):
    """Scheduled Cloud Function triggered by Cloud Scheduler"""
    
    # Default task configuration
    task_config = {
        'id': 'scheduled_task_gcp',
        'url': 'https://example.com'
    }
    
    # Perform scraping
    try:
        response = requests.get(task_config['url'], timeout=30)
        
        # Store results
        db = firestore.Client()
        doc_ref = db.collection('scraping_results').document()
        doc_ref.set({
            'task_id': task_config['id'],
            'timestamp': datetime.now(),
            'url': task_config['url'],
            'status': 'success',
            'data': response.text[:1000]
        })
        
        print(f"Scheduled scraping completed for {task_config['url']}")
        
    except Exception as e:
        print(f"Scheduled scraping failed: {e}")
'''
        
        with open('main.py', 'w') as f:
            f.write(cloud_function_code)
        
        # Create requirements.txt for Cloud Functions
        gcp_requirements = '''
functions-framework==3.4.0
requests==2.31.0
google-cloud-firestore==2.13.1
'''
        
        with open('requirements.txt', 'w') as f:
            f.write(gcp_requirements)
        
        print("✅ Google Cloud Function code created")
        print("📋 Deploy with: gcloud functions deploy dataminer-scraper --runtime python39 --trigger-http")
    
    def deploy_to_azure(self):
        """Deploy to Azure Functions"""
        print("🚀 Deploying to Azure Functions...")
        
        # Create Azure Function code
        azure_function_code = '''
import logging
import json
import requests
from datetime import datetime
import azure.functions as func
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    """Azure Function for autonomous scraping"""
    
    logging.info('DataMiner scraping function triggered')
    
    try:
        # Get task configuration
        req_body = req.get_json()
        task_config = req_body.get('task_config', {})
        
        # Perform scraping
        url = task_config['url']
        response = requests.get(url, timeout=30)
        
        # Store in Cosmos DB
        cosmos_client = CosmosClient.from_connection_string(
            os.environ['COSMOS_CONNECTION_STRING']
        )
        database = cosmos_client.get_database_client('dataminer')
        container = database.get_container_client('scraping_results')
        
        container.create_item({
            'id': f"{task_config['id']}_{datetime.now().isoformat()}",
            'task_id': task_config['id'],
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'status': 'success',
            'data': response.text[:1000]
        })
        
        return func.HttpResponse(
            json.dumps({
                'message': 'Scraping completed successfully',
                'task_id': task_config['id']
            }),
            status_code=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logging.error(f'Scraping failed: {e}')
        return func.HttpResponse(
            json.dumps({'error': str(e)}),
            status_code=500,
            mimetype='application/json'
        )
'''
        
        with open('__init__.py', 'w') as f:
            f.write(azure_function_code)
        
        # Create function.json
        function_config = {
            "scriptFile": "__init__.py",
            "bindings": [
                {
                    "authLevel": "function",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["get", "post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "$return"
                }
            ]
        }
        
        with open('function.json', 'w') as f:
            json.dump(function_config, f, indent=2)
        
        print("✅ Azure Function code created")
        print("📋 Deploy with: func azure functionapp publish your-function-app")
    
    def create_cron_scheduler(self):
        """Create advanced cron-based scheduler"""
        cron_script = '''#!/bin/bash
# DataMiner Pro - Advanced Cron Scheduler
# Add to crontab with: crontab -e

# Run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/dataminer/autonomous_ai_agent.py >> /var/log/dataminer.log 2>&1

# Run sports scraping every minute during game hours (14:00-22:00 UTC)
* 14-22 * * * /usr/bin/python3 /path/to/dataminer/sports_scraper.py >> /var/log/dataminer_sports.log 2>&1

# Run crypto scraping every 30 seconds (using sleep)
* * * * * /usr/bin/python3 /path/to/dataminer/crypto_scraper.py >> /var/log/dataminer_crypto.log 2>&1
* * * * * sleep 30; /usr/bin/python3 /path/to/dataminer/crypto_scraper.py >> /var/log/dataminer_crypto.log 2>&1

# Daily cleanup at 2 AM
0 2 * * * /usr/bin/python3 /path/to/dataminer/cleanup_old_data.py >> /var/log/dataminer_cleanup.log 2>&1

# Weekly backup at Sunday 3 AM
0 3 * * 0 /usr/bin/python3 /path/to/dataminer/backup_data.py >> /var/log/dataminer_backup.log 2>&1

# Health check every minute
* * * * * /usr/bin/python3 /path/to/dataminer/health_check.py >> /var/log/dataminer_health.log 2>&1
'''
        
        with open('dataminer_crontab.sh', 'w') as f:
            f.write(cron_script)
        
        os.chmod('dataminer_crontab.sh', 0o755)
        print("✅ Cron scheduler created")
    
    def create_systemd_service(self):
        """Create systemd service for Linux systems"""
        service_content = '''[Unit]
Description=DataMiner Pro Autonomous AI Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=dataminer
Group=dataminer
WorkingDirectory=/opt/dataminer
ExecStart=/usr/bin/python3 /opt/dataminer/autonomous_ai_agent.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=dataminer-agent

# Environment variables
Environment=PYTHONPATH=/opt/dataminer
Environment=DATAMINER_CONFIG=/opt/dataminer/agent_config.json

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/dataminer/data /opt/dataminer/logs

[Install]
WantedBy=multi-user.target
'''
        
        with open('dataminer-agent.service', 'w') as f:
            f.write(service_content)
        
        print("✅ Systemd service created")
        print("📋 Install with:")
        print("  sudo cp dataminer-agent.service /etc/systemd/system/")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable dataminer-agent")
        print("  sudo systemctl start dataminer-agent")

def main():
    """Main function"""
    print("☁️ DataMiner Pro - Cloud Scheduler Setup")
    print("=" * 50)
    
    scheduler = CloudScheduler()
    
    print("🎯 Available Deployment Options:")
    print("  1. AWS Lambda (Serverless)")
    print("  2. Google Cloud Functions")
    print("  3. Azure Functions")
    print("  4. Cron Scheduler (Linux/Unix)")
    print("  5. Systemd Service (Linux)")
    print("  6. All Options")
    
    choice = input("\nSelect deployment option (1-6): ").strip()
    
    if choice == '1':
        scheduler.deploy_to_aws_lambda()
    elif choice == '2':
        scheduler.deploy_to_google_cloud()
    elif choice == '3':
        scheduler.deploy_to_azure()
    elif choice == '4':
        scheduler.create_cron_scheduler()
    elif choice == '5':
        scheduler.create_systemd_service()
    elif choice == '6':
        print("🚀 Creating all deployment options...")
        scheduler.deploy_to_aws_lambda()
        scheduler.deploy_to_google_cloud()
        scheduler.deploy_to_azure()
        scheduler.create_cron_scheduler()
        scheduler.create_systemd_service()
    else:
        print("❌ Invalid choice")
        return
    
    print("\n✅ Cloud deployment files created successfully!")
    print("\n🎯 Next Steps:")
    print("  1. Configure your cloud credentials")
    print("  2. Update agent_config.json with your settings")
    print("  3. Deploy using the provided scripts")
    print("  4. Monitor your autonomous agent")

if __name__ == "__main__":
    main()