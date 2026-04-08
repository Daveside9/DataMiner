import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import re

class PatternAnalyzer:
    def __init__(self):
        self.analysis_types = [
            'trend_analysis',
            'frequency_analysis',
            'pattern_detection',
            'anomaly_detection',
            'correlation_analysis'
        ]
    
    def analyze_trends(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in historical data"""
        if not historical_data:
            return {"error": "No data provided for analysis"}
        
        try:
            # Convert to DataFrame for easier analysis
            df = self._prepare_dataframe(historical_data)
            
            analysis_results = {
                "summary": self._generate_summary(df),
                "trends": self._analyze_trends(df),
                "patterns": self._detect_patterns(df),
                "anomalies": self._detect_anomalies(df),
                "insights": self._generate_insights(df),
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis_results
        
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _prepare_dataframe(self, historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert historical data to pandas DataFrame"""
        records = []
        
        for entry in historical_data:
            record = {
                'timestamp': pd.to_datetime(entry['timestamp']),
                'success': entry['success'],
                'method': entry['method']
            }
            
            # Extract numeric values from scraped data
            data = entry.get('data', {})
            if isinstance(data, dict):
                numeric_values = self._extract_numeric_values(data)
                record.update(numeric_values)
                
                # Extract text metrics
                text_metrics = self._extract_text_metrics(data)
                record.update(text_metrics)
            
            records.append(record)
        
        df = pd.DataFrame(records)
        df = df.sort_values('timestamp')
        return df
    
    def _extract_numeric_values(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract numeric values from scraped data"""
        numeric_values = {}
        
        def extract_numbers(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}_{key}" if prefix else key
                    extract_numbers(value, new_prefix)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_numbers(item, f"{prefix}_{i}")
            elif isinstance(obj, str):
                # Try to extract numbers from strings
                numbers = re.findall(r'-?\d+\.?\d*', obj)
                if numbers:
                    try:
                        numeric_values[f"{prefix}_value"] = float(numbers[0])
                        if len(numbers) > 1:
                            numeric_values[f"{prefix}_count"] = len(numbers)
                    except ValueError:
                        pass
            elif isinstance(obj, (int, float)):
                numeric_values[prefix] = float(obj)
        
        extract_numbers(data)
        return numeric_values
    
    def _extract_text_metrics(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Extract text-based metrics from scraped data"""
        metrics = {}
        
        def count_text_elements(obj, prefix=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}_{key}" if prefix else key
                    count_text_elements(value, new_prefix)
            elif isinstance(obj, list):
                metrics[f"{prefix}_list_length"] = len(obj)
                for item in obj:
                    count_text_elements(item, prefix)
            elif isinstance(obj, str):
                metrics[f"{prefix}_text_length"] = len(obj)
                metrics[f"{prefix}_word_count"] = len(obj.split())
        
        count_text_elements(data)
        return metrics
    
    def _generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            "total_records": len(df),
            "date_range": {
                "start": df['timestamp'].min().isoformat() if not df.empty else None,
                "end": df['timestamp'].max().isoformat() if not df.empty else None,
                "days": (df['timestamp'].max() - df['timestamp'].min()).days if not df.empty else 0
            },
            "success_rate": df['success'].mean() if 'success' in df.columns else 1.0,
            "scraping_methods": df['method'].value_counts().to_dict() if 'method' in df.columns else {}
        }
        
        # Add numeric column statistics
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            summary["numeric_stats"] = {}
            for col in numeric_columns:
                if col != 'success':  # Skip boolean success column
                    summary["numeric_stats"][col] = {
                        "mean": df[col].mean(),
                        "std": df[col].std(),
                        "min": df[col].min(),
                        "max": df[col].max(),
                        "trend": self._calculate_trend(df[col])
                    }
        
        return summary
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in the data"""
        trends = {}
        
        # Time-based trends
        if not df.empty:
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['day'] = df['timestamp'].dt.date
            
            trends["hourly_distribution"] = df['hour'].value_counts().sort_index().to_dict()
            trends["daily_distribution"] = df['day_of_week'].value_counts().sort_index().to_dict()
            
            # Daily aggregation for trend analysis
            daily_counts = df.groupby('day').size()
            if len(daily_counts) > 1:
                trends["daily_trend"] = self._calculate_trend(daily_counts.values)
                trends["daily_pattern"] = daily_counts.to_dict()
        
        # Numeric column trends
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['success'] and not df[col].isna().all():
                trends[f"{col}_trend"] = {
                    "direction": self._calculate_trend(df[col]),
                    "volatility": df[col].std() / df[col].mean() if df[col].mean() != 0 else 0,
                    "recent_change": self._calculate_recent_change(df[col])
                }
        
        return trends
    
    def _detect_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect patterns in the data"""
        patterns = {}
        
        if df.empty:
            return patterns
        
        # Seasonal patterns
        if len(df) > 7:  # Need at least a week of data
            patterns["weekly_pattern"] = self._detect_weekly_pattern(df)
        
        # Recurring values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['success'] and not df[col].isna().all():
                value_counts = df[col].value_counts()
                if len(value_counts) > 1:
                    patterns[f"{col}_recurring_values"] = value_counts.head(5).to_dict()
        
        # Success/failure patterns
        if 'success' in df.columns:
            patterns["success_patterns"] = {
                "success_rate_by_hour": df.groupby('hour')['success'].mean().to_dict(),
                "success_rate_by_day": df.groupby('day_of_week')['success'].mean().to_dict()
            }
        
        return patterns
    
    def _detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect anomalies in the data"""
        anomalies = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['success'] and not df[col].isna().all():
                # Use IQR method for anomaly detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomaly_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index
                
                if len(anomaly_indices) > 0:
                    anomalies[col] = {
                        "count": len(anomaly_indices),
                        "percentage": len(anomaly_indices) / len(df) * 100,
                        "values": df.loc[anomaly_indices, col].tolist()
                    }
        
        return anomalies
    
    def _generate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate human-readable insights"""
        insights = []
        
        if df.empty:
            insights.append("No data available for analysis")
            return insights
        
        # Data collection insights
        total_records = len(df)
        date_range = (df['timestamp'].max() - df['timestamp'].min()).days
        
        insights.append(f"Collected {total_records} data points over {date_range} days")
        
        if 'success' in df.columns:
            success_rate = df['success'].mean()
            insights.append(f"Data collection success rate: {success_rate:.1%}")
        
        # Trend insights
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['success'] and not df[col].isna().all():
                trend = self._calculate_trend(df[col])
                if trend > 0.1:
                    insights.append(f"{col} shows an increasing trend")
                elif trend < -0.1:
                    insights.append(f"{col} shows a decreasing trend")
                else:
                    insights.append(f"{col} remains relatively stable")
        
        # Pattern insights
        if len(df) > 7:
            most_active_hour = df['hour'].mode().iloc[0] if 'hour' in df.columns else None
            if most_active_hour is not None:
                insights.append(f"Most data collection activity occurs at hour {most_active_hour}")
        
        return insights
    
    def _calculate_trend(self, series: pd.Series) -> float:
        """Calculate trend direction (-1 to 1)"""
        if len(series) < 2:
            return 0
        
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        if mask.sum() < 2:
            return 0
        
        x = x[mask]
        y = y[mask]
        
        # Calculate correlation coefficient as trend indicator
        correlation = np.corrcoef(x, y)[0, 1]
        return correlation if not np.isnan(correlation) else 0
    
    def _calculate_recent_change(self, series: pd.Series) -> float:
        """Calculate recent change percentage"""
        if len(series) < 2:
            return 0
        
        recent_values = series.tail(min(7, len(series)))  # Last 7 values or all if less
        older_values = series.head(min(7, len(series)))   # First 7 values or all if less
        
        recent_mean = recent_values.mean()
        older_mean = older_values.mean()
        
        if older_mean == 0:
            return 0
        
        return ((recent_mean - older_mean) / older_mean) * 100
    
    def _detect_weekly_pattern(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect weekly patterns"""
        weekly_counts = df.groupby('day_of_week').size()
        
        # Calculate coefficient of variation to measure pattern strength
        cv = weekly_counts.std() / weekly_counts.mean()
        
        return {
            "pattern_strength": cv,
            "most_active_day": weekly_counts.idxmax(),
            "least_active_day": weekly_counts.idxmin(),
            "daily_distribution": weekly_counts.to_dict()
        }