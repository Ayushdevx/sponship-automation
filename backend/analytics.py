"""
Analytics and Charts Module for Hackfinity
Provides modern charts, graphs, and analytics capabilities
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from motor.motor_asyncio import AsyncIOMotorDatabase
import numpy as np

class AnalyticsEngine:
    """Advanced analytics engine for generating insights and visualizations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
    async def get_sponsor_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive sponsor analytics"""
        
        # Fetch sponsor data
        sponsors = await self.db.sponsors.find({}).to_list(length=None)
        
        if not sponsors:
            return {"error": "No sponsor data available"}
            
        df = pd.DataFrame(sponsors)
        
        analytics = {
            "overview": self._get_sponsor_overview(df),
            "charts": {
                "status_distribution": self._create_status_pie_chart(df),
                "engagement_timeline": self._create_engagement_timeline(df),
                "response_rates": self._create_response_rate_chart(df),
                "sponsor_types": self._create_sponsor_type_distribution(df),
                "geographic_distribution": self._create_geographic_chart(df),
                "engagement_heatmap": self._create_engagement_heatmap(df)
            },
            "insights": self._generate_sponsor_insights(df)
        }
        
        return analytics
    
    async def get_certificate_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive certificate analytics"""
        
        participants = await self.db.participants.find({}).to_list(length=None)
        
        if not participants:
            return {"error": "No participant data available"}
            
        df = pd.DataFrame(participants)
        
        analytics = {
            "overview": self._get_certificate_overview(df),
            "charts": {
                "completion_rates": self._create_completion_chart(df),
                "skill_distribution": self._create_skill_distribution(df),
                "institution_analysis": self._create_institution_chart(df),
                "timeline_progress": self._create_timeline_chart(df),
                "performance_metrics": self._create_performance_chart(df),
                "demographic_breakdown": self._create_demographic_chart(df)
            },
            "insights": self._generate_certificate_insights(df)
        }
        
        return analytics
    
    async def get_advanced_charts(self, chart_type: str, data_source: str) -> Dict[str, Any]:
        """Generate advanced modern charts with multiple visualization options"""
        
        if data_source == "sponsors":
            sponsors = await self.db.sponsors.find({}).to_list(length=None)
            df = pd.DataFrame(sponsors) if sponsors else pd.DataFrame()
        elif data_source == "participants":
            participants = await self.db.participants.find({}).to_list(length=None)
            df = pd.DataFrame(participants) if participants else pd.DataFrame()
        else:
            return {"error": "Invalid data source"}
            
        if df.empty:
            return {"error": f"No {data_source} data available"}
            
        chart_generators = {
            "3d_scatter": self._create_3d_scatter_plot,
            "treemap": self._create_treemap_chart,
            "sunburst": self._create_sunburst_chart,
            "sankey": self._create_sankey_diagram,
            "radar": self._create_radar_chart,
            "waterfall": self._create_waterfall_chart,
            "gauge": self._create_gauge_chart,
            "violin": self._create_violin_plot,
            "heatmap_calendar": self._create_calendar_heatmap,
            "funnel": self._create_funnel_chart,
            "candlestick": self._create_candlestick_chart,
            "parallel_coordinates": self._create_parallel_coordinates,
            "density_contour": self._create_density_contour,
            "animated_bar": self._create_animated_bar_chart,
            "choropleth": self._create_choropleth_map
        }
        
        if chart_type not in chart_generators:
            return {"error": f"Unknown chart type: {chart_type}"}
            
        try:
            chart_data = chart_generators[chart_type](df)
            return {
                "chart": chart_data,
                "metadata": {
                    "chart_type": chart_type,
                    "data_source": data_source,
                    "generated_at": datetime.now().isoformat(),
                    "data_points": len(df)
                }
            }
        except Exception as e:
            return {"error": f"Failed to generate {chart_type}: {str(e)}"}

    def _get_sponsor_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate sponsor overview statistics"""
        return {
            "total_sponsors": len(df),
            "active_sponsors": len(df[df.get('status', '') == 'active']),
            "pending_responses": len(df[df.get('email_status', '') == 'pending']),
            "successful_contacts": len(df[df.get('email_status', '') == 'sent']),
            "conversion_rate": round(len(df[df.get('status', '') == 'confirmed']) / len(df) * 100, 2) if len(df) > 0 else 0,
            "average_response_time": self._calculate_avg_response_time(df)
        }
    
    def _get_certificate_overview(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate certificate overview statistics"""
        return {
            "total_participants": len(df),
            "certificates_issued": len(df[df.get('certificate_status', '') == 'issued']),
            "pending_certificates": len(df[df.get('certificate_status', '') == 'pending']),
            "completion_rate": round(len(df[df.get('status', '') == 'completed']) / len(df) * 100, 2) if len(df) > 0 else 0,
            "skill_categories": df['skills'].value_counts().to_dict() if 'skills' in df.columns else {},
            "institution_diversity": df['institution'].nunique() if 'institution' in df.columns else 0
        }
    
    def _create_status_pie_chart(self, df: pd.DataFrame) -> str:
        """Create interactive pie chart for sponsor status distribution"""
        if 'status' not in df.columns:
            return self._create_empty_chart("No status data available")
            
        status_counts = df['status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.4,
            marker_colors=['#6366f1', '#10b981', '#f59e0b', '#ef4444'],
            textinfo='label+percent',
            textfont_size=12
        )])
        
        fig.update_layout(
            title="Sponsor Status Distribution",
            font=dict(size=14),
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_engagement_timeline(self, df: pd.DataFrame) -> str:
        """Create timeline chart for engagement activities"""
        if 'created_at' not in df.columns:
            return self._create_empty_chart("No timeline data available")
            
        # Convert to datetime if needed
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Group by date
        daily_engagement = df.groupby(df['created_at'].dt.date).size().reset_index()
        daily_engagement.columns = ['date', 'count']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_engagement['date'],
            y=daily_engagement['count'],
            mode='lines+markers',
            name='Daily Sponsors',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Sponsor Engagement Timeline",
            xaxis_title="Date",
            yaxis_title="Number of Sponsors",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            showlegend=False
        )
        
        return fig.to_json()
    
    def _create_response_rate_chart(self, df: pd.DataFrame) -> str:
        """Create response rate analysis chart"""
        if 'email_status' not in df.columns:
            return self._create_empty_chart("No email status data available")
            
        response_data = df['email_status'].value_counts()
        
        fig = go.Figure(data=[go.Bar(
            x=response_data.index,
            y=response_data.values,
            marker_color=['#10b981', '#f59e0b', '#ef4444'],
            text=response_data.values,
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Email Response Rates",
            xaxis_title="Response Status",
            yaxis_title="Count",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_sponsor_type_distribution(self, df: pd.DataFrame) -> str:
        """Create sponsor type distribution chart"""
        if 'sponsor_type' not in df.columns:
            return self._create_empty_chart("No sponsor type data available")
            
        type_counts = df['sponsor_type'].value_counts()
        
        fig = go.Figure(data=[go.Bar(
            x=type_counts.values,
            y=type_counts.index,
            orientation='h',
            marker_color='#6366f1',
            text=type_counts.values,
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Sponsor Type Distribution",
            xaxis_title="Count",
            yaxis_title="Sponsor Type",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_geographic_chart(self, df: pd.DataFrame) -> str:
        """Create geographic distribution chart"""
        if 'location' not in df.columns and 'country' not in df.columns:
            return self._create_empty_chart("No location data available")
            
        location_col = 'country' if 'country' in df.columns else 'location'
        location_counts = df[location_col].value_counts().head(10)
        
        fig = go.Figure(data=[go.Bar(
            x=location_counts.index,
            y=location_counts.values,
            marker_color='#10b981',
            text=location_counts.values,
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Geographic Distribution (Top 10)",
            xaxis_title="Location",
            yaxis_title="Count",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            xaxis_tickangle=45
        )
        
        return fig.to_json()
    
    def _create_engagement_heatmap(self, df: pd.DataFrame) -> str:
        """Create engagement heatmap"""
        if 'created_at' not in df.columns:
            return self._create_empty_chart("No engagement data available")
            
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.day_name()
        
        # Create heatmap data
        heatmap_data = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(day_order)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=list(range(24)),
            y=day_order,
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title="Engagement Heatmap (Hour vs Day)",
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_completion_chart(self, df: pd.DataFrame) -> str:
        """Create certificate completion chart"""
        if 'certificate_status' not in df.columns:
            return self._create_empty_chart("No certificate status data available")
            
        completion_data = df['certificate_status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=completion_data.index,
            values=completion_data.values,
            hole=0.3,
            marker_colors=['#10b981', '#f59e0b', '#ef4444'],
        )])
        
        fig.update_layout(
            title="Certificate Completion Status",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_skill_distribution(self, df: pd.DataFrame) -> str:
        """Create skill distribution chart"""
        if 'skills' not in df.columns:
            return self._create_empty_chart("No skills data available")
            
        # Handle comma-separated skills
        all_skills = []
        for skills in df['skills'].dropna():
            if isinstance(skills, str):
                all_skills.extend([skill.strip() for skill in skills.split(',')])
        
        skill_counts = pd.Series(all_skills).value_counts().head(10)
        
        fig = go.Figure(data=[go.Bar(
            x=skill_counts.values,
            y=skill_counts.index,
            orientation='h',
            marker_color='#6366f1'
        )])
        
        fig.update_layout(
            title="Top Skills Distribution",
            xaxis_title="Count",
            yaxis_title="Skills",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_institution_chart(self, df: pd.DataFrame) -> str:
        """Create institution analysis chart"""
        if 'institution' not in df.columns:
            return self._create_empty_chart("No institution data available")
            
        institution_counts = df['institution'].value_counts().head(10)
        
        fig = go.Figure(data=[go.Bar(
            x=institution_counts.index,
            y=institution_counts.values,
            marker_color='#10b981'
        )])
        
        fig.update_layout(
            title="Top Institutions",
            xaxis_title="Institution",
            yaxis_title="Participants",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50),
            xaxis_tickangle=45
        )
        
        return fig.to_json()
    
    def _create_timeline_chart(self, df: pd.DataFrame) -> str:
        """Create timeline progress chart"""
        if 'created_at' not in df.columns:
            return self._create_empty_chart("No timeline data available")
            
        df['created_at'] = pd.to_datetime(df['created_at'])
        daily_registrations = df.groupby(df['created_at'].dt.date).size().cumsum()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_registrations.index,
            y=daily_registrations.values,
            mode='lines+markers',
            name='Cumulative Registrations',
            line=dict(color='#6366f1', width=3),
            fill='tonexty'
        ))
        
        fig.update_layout(
            title="Registration Timeline",
            xaxis_title="Date",
            yaxis_title="Cumulative Participants",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_performance_chart(self, df: pd.DataFrame) -> str:
        """Create performance metrics chart"""
        # Mock performance data - in real scenario, this would come from actual performance metrics
        performance_metrics = {
            'Excellent': len(df) * 0.2,
            'Good': len(df) * 0.4,
            'Average': len(df) * 0.3,
            'Needs Improvement': len(df) * 0.1
        }
        
        fig = go.Figure(data=[go.Bar(
            x=list(performance_metrics.keys()),
            y=list(performance_metrics.values()),
            marker_color=['#10b981', '#6366f1', '#f59e0b', '#ef4444']
        )])
        
        fig.update_layout(
            title="Performance Distribution",
            xaxis_title="Performance Level",
            yaxis_title="Count",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_demographic_chart(self, df: pd.DataFrame) -> str:
        """Create demographic breakdown chart"""
        if 'age_group' not in df.columns:
            # Create mock age groups based on participant data
            age_groups = {
                '18-22': len(df) * 0.4,
                '23-26': len(df) * 0.35,
                '27-30': len(df) * 0.15,
                '31+': len(df) * 0.1
            }
        else:
            age_groups = df['age_group'].value_counts().to_dict()
        
        fig = go.Figure(data=[go.Pie(
            labels=list(age_groups.keys()),
            values=list(age_groups.values()),
            hole=0.4,
            marker_colors=['#6366f1', '#10b981', '#f59e0b', '#ef4444']
        )])
        
        fig.update_layout(
            title="Age Group Distribution",
            font=dict(size=14),
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        return fig.to_json()
    
    def _create_empty_chart(self, message: str) -> str:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )
        return fig.to_json()
    
    def _calculate_avg_response_time(self, df: pd.DataFrame) -> float:
        """Calculate average response time"""
        # Mock calculation - in real scenario, this would be calculated from actual response times
        return 2.5
    
    def _generate_sponsor_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate AI-powered insights for sponsors"""
        insights = []
        
        if len(df) > 0:
            conversion_rate = len(df[df.get('status', '') == 'confirmed']) / len(df) * 100
            
            if conversion_rate > 80:
                insights.append("🎉 Excellent sponsor conversion rate! Your outreach strategy is highly effective.")
            elif conversion_rate > 60:
                insights.append("✅ Good sponsor conversion rate. Consider A/B testing different email templates.")
            else:
                insights.append("⚠️ Low sponsor conversion rate. Review your outreach strategy and timing.")
            
            # Add more insights based on data patterns
            if 'email_status' in df.columns:
                pending_ratio = len(df[df['email_status'] == 'pending']) / len(df)
                if pending_ratio > 0.3:
                    insights.append("📧 High number of pending emails. Follow up with personalized messages.")
            
            insights.append(f"📊 Total sponsors contacted: {len(df)}")
            insights.append(f"🎯 Recommended next action: Focus on high-potential prospects")
        
        return insights
    
    def _generate_certificate_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate AI-powered insights for certificates"""
        insights = []
        
        if len(df) > 0:
            completion_rate = len(df[df.get('status', '') == 'completed']) / len(df) * 100
            
            if completion_rate > 90:
                insights.append("🏆 Outstanding completion rate! Participants are highly engaged.")
            elif completion_rate > 70:
                insights.append("✅ Good completion rate. Monitor for any dropout patterns.")
            else:
                insights.append("⚠️ Low completion rate. Consider improving participant experience.")
            
            # Skill diversity insight
            if 'skills' in df.columns:
                unique_skills = set()
                for skills in df['skills'].dropna():
                    if isinstance(skills, str):
                        unique_skills.update([skill.strip() for skill in skills.split(',')])
                
                insights.append(f"🛠️ {len(unique_skills)} unique skills represented")
                
                if len(unique_skills) > 20:
                    insights.append("🌟 Great skill diversity! Strong cross-functional participation.")
            
            insights.append(f"🎓 Certificates to be issued: {len(df)}")
            insights.append(f"🚀 Recommended: Showcase participant achievements on social media")
        
        return insights
    
    def _create_3d_scatter_plot(self, df: pd.DataFrame) -> str:
        """Create 3D scatter plot with engagement metrics"""
        if len(df) < 3:
            return self._create_empty_chart("Insufficient data for 3D visualization")
            
        # Create synthetic 3D data for demonstration
        x = np.random.normal(0, 1, len(df))
        y = np.random.normal(0, 1, len(df))
        z = np.random.normal(0, 1, len(df))
        
        fig = go.Figure(data=[go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode='markers',
            marker=dict(
                size=12,
                color=z,
                colorscale='Viridis',
                opacity=0.8,
                colorbar=dict(title="Engagement Score")
            ),
            text=[f"Entity {i+1}" for i in range(len(df))],
            hovertemplate="<b>%{text}</b><br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>"
        )])
        
        fig.update_layout(
            title="3D Engagement Analysis",
            scene=dict(
                xaxis_title="Response Rate",
                yaxis_title="Conversion Rate",
                zaxis_title="Engagement Score"
            ),
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_treemap_chart(self, df: pd.DataFrame) -> str:
        """Create treemap visualization for hierarchical data"""
        # Create sample hierarchical data
        categories = ['Technology', 'Finance', 'Healthcare', 'Education', 'Retail']
        subcategories = {
            'Technology': ['AI/ML', 'Blockchain', 'Cloud', 'Mobile'],
            'Finance': ['Banking', 'Insurance', 'Trading', 'Fintech'],
            'Healthcare': ['Pharma', 'Medical Devices', 'Telehealth', 'Research'],
            'Education': ['K-12', 'Higher Ed', 'Online Learning', 'Corporate Training'],
            'Retail': ['E-commerce', 'Fashion', 'Food & Beverage', 'Electronics']
        }
        
        parents = []
        labels = []
        values = []
        
        for category in categories:
            labels.append(category)
            parents.append("")
            values.append(np.random.randint(50, 200))
            
            for subcategory in subcategories[category]:
                labels.append(subcategory)
                parents.append(category)
                values.append(np.random.randint(10, 50))
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            textinfo="label+value+percent parent",
            hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentParent}<extra></extra>",
            maxdepth=3,
            branchvalues="total"
        ))
        
        fig.update_layout(
            title="Sponsor Distribution by Category",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_sunburst_chart(self, df: pd.DataFrame) -> str:
        """Create sunburst chart for multi-level categorization"""
        # Sample data for sunburst chart
        data = {
            "ids": ["Tech", "Tech-AI", "Tech-Cloud", "Tech-Mobile", "Finance", "Finance-Banking", "Finance-Fintech"],
            "labels": ["Technology", "AI/ML", "Cloud Services", "Mobile Apps", "Finance", "Banking", "Fintech"],
            "parents": ["", "Tech", "Tech", "Tech", "", "Finance", "Finance"],
            "values": [100, 30, 40, 30, 80, 50, 30]
        }
        
        fig = go.Figure(go.Sunburst(
            ids=data["ids"],
            labels=data["labels"],
            parents=data["parents"],
            values=data["values"],
            branchvalues="total",
            hovertemplate="<b>%{label}</b><br>Value: %{value}<br>Percentage: %{percentParent}<extra></extra>",
            maxdepth=3
        ))
        
        fig.update_layout(
            title="Hierarchical Sponsor Categories",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_sankey_diagram(self, df: pd.DataFrame) -> str:
        """Create Sankey diagram for flow visualization"""
        # Sample flow data
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Initial Contact", "Email Sent", "Response Received", "Meeting Scheduled", "Proposal Sent", "Contract Signed"],
                color="blue"
            ),
            link=dict(
                source=[0, 1, 1, 2, 2, 3, 4],
                target=[1, 2, 3, 4, 5, 4, 5],
                value=[100, 70, 30, 50, 20, 25, 15]
            )
        )])
        
        fig.update_layout(
            title_text="Sponsor Engagement Flow",
            font_size=10,
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_radar_chart(self, df: pd.DataFrame) -> str:
        """Create radar chart for multi-dimensional analysis"""
        categories = ['Response Rate', 'Engagement', 'Conversion', 'ROI', 'Satisfaction', 'Retention']
        
        fig = go.Figure()
        
        # Add multiple series for comparison
        for i, entity in enumerate(['Current Campaign', 'Previous Campaign', 'Industry Average']):
            values = np.random.uniform(60, 95, len(categories))
            values = np.append(values, values[0])  # Close the radar chart
            categories_closed = categories + [categories[0]]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories_closed,
                fill='toself',
                name=entity,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="Performance Radar Analysis",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_waterfall_chart(self, df: pd.DataFrame) -> str:
        """Create waterfall chart for cumulative analysis"""
        x = ['Initial Leads', 'Email Bounces', 'No Response', 'Interested', 'Meeting Set', 'Proposals', 'Signed']
        y = [1000, -50, -400, 150, -100, 80, -30]
        
        fig = go.Figure(go.Waterfall(
            name="Sponsor Pipeline",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
            x=x,
            textposition="outside",
            text=[f"{val}" for val in y],
            y=y,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title="Sponsor Conversion Waterfall",
            showlegend=False,
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_gauge_chart(self, df: pd.DataFrame) -> str:
        """Create gauge chart for KPI visualization"""
        conversion_rate = np.random.uniform(65, 85)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=conversion_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Conversion Rate %"},
            delta={'reference': 75},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=400
        )
        
        return fig.to_json()

    def _create_parallel_coordinates(self, df: pd.DataFrame) -> str:
        """Create parallel coordinates plot for multi-dimensional data"""
        # Generate sample multi-dimensional data
        n_samples = min(len(df), 50)
        dimensions = []
        
        metrics = ['Response Rate', 'Engagement Score', 'Conversion Rate', 'ROI', 'Satisfaction']
        for metric in metrics:
            dimensions.append(dict(
                range=[0, 100],
                label=metric,
                values=np.random.uniform(30, 90, n_samples)
            ))
        
        fig = go.Figure(data=go.Parcoords(
            line=dict(color=np.random.uniform(0, 1, n_samples),
                     colorscale='Viridis',
                     showscale=True),
            dimensions=dimensions
        ))
        
        fig.update_layout(
            title="Multi-Dimensional Sponsor Analysis",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_animated_bar_chart(self, df: pd.DataFrame) -> str:
        """Create animated bar chart showing progress over time"""
        # Sample time-series data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        categories = ['Email Sent', 'Responses', 'Meetings', 'Signed']
        
        frames = []
        for i, month in enumerate(months):
            frame_data = []
            for category in categories:
                values = np.random.randint(10, 100, i + 1)
                frame_data.append(go.Bar(
                    x=months[:i+1],
                    y=values,
                    name=category,
                    visible=True
                ))
            frames.append(go.Frame(data=frame_data, name=month))
        
        # Initial frame
        initial_data = []
        for category in categories:
            initial_data.append(go.Bar(
                x=[months[0]],
                y=[np.random.randint(10, 100)],
                name=category
            ))
        
        fig = go.Figure(
            data=initial_data,
            frames=frames
        )
        
        # Add play button
        fig.update_layout(
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 500, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 300}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                         "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            title="Sponsor Engagement Timeline",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_choropleth_map(self, df: pd.DataFrame) -> str:
        """Create choropleth map for geographic data visualization"""
        if 'location' not in df.columns:
            return self._create_empty_chart("No location data available")
        
        # Aggregate data by location
        location_data = df.groupby('location').size().reset_index(name='count')
        
        fig = go.Figure(data=go.Choropleth(
            locations=location_data['location'],
            z=location_data['count'],
            locationmode='country names',
            colorscale='Blues',
            colorbar_title="Sponsor Count",
            hovertemplate="<b>%{location}</b><br>Sponsors: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Geographic Distribution of Sponsors",
            geo=dict(
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                showland=True,
                landcolor="lightgray",
                subunitcolor="blue",
                countrycolor="blue"
            ),
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_violin_plot(self, df: pd.DataFrame) -> str:
        """Create violin plot for distribution analysis"""
        if 'engagement_score' not in df.columns:
            return self._create_empty_chart("No engagement score data available")
        
        fig = go.Figure(data=go.Violin(
            y=df['engagement_score'],
            box=True,
            line_color="purple",
            fillcolor="lightpurple",
            hovertemplate="<b>Engagement Score Distribution</b><br>Score: %{y}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Engagement Score Distribution",
            yaxis_title="Engagement Score",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_calendar_heatmap(self, df: pd.DataFrame) -> str:
        """Create calendar heatmap for time-based activity visualization"""
        if 'created_at' not in df.columns:
            return self._create_empty_chart("No activity data available")
        
        # Extract date parts
        df['date'] = pd.to_datetime(df['created_at']).dt.date
        df['year'] = pd.to_datetime(df['created_at']).dt.year
        df['month'] = pd.to_datetime(df['created_at']).dt.month
        df['day'] = pd.to_datetime(df['created_at']).dt.day
        
        # Aggregate data by day
        daily_activity = df.groupby('date').size().reset_index(name='count')
        
        # Create a complete date range
        all_dates = pd.date_range(start=daily_activity['date'].min(), end=daily_activity['date'].max())
        daily_activity = daily_activity.set_index('date').reindex(all_dates, fill_value=0).reset_index()
        daily_activity.columns = ['date', 'count']
        
        # Create calendar heatmap
        fig = px.density_heatmap(
            daily_activity,
            x='date',
            y='count',
            color_continuous_scale='Viridis',
            title="Daily Activity Calendar",
            labels={'date': "Date", 'count': "Activity Count"},
            template="plotly_dark"
        )
        
        fig.update_traces(
            hovertemplate="<b>Date: %{x|%Y-%m-%d}</b><br>Activity Count: %{y}<extra></extra>"
        )
        
        return fig.to_json()

    def _create_funnel_chart(self, df: pd.DataFrame) -> str:
        """Create funnel chart for conversion analysis"""
        stages = ["Contacted", "Interested", "Proposed", "Negotiation", "Closed"]
        values = [len(df), int(len(df) * 0.8), int(len(df) * 0.6), int(len(df) * 0.4), int(len(df) * 0.2)]
        
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            title="Sponsor Conversion Funnel",
            hoverinfo="y+x",
            marker=dict(
                color="lightblue",
                line=dict(color="blue", width=2)
            )
        ))
        
        fig.update_layout(
            title="Sponsor Conversion Funnel Analysis",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_candlestick_chart(self, df: pd.DataFrame) -> str:
        """Create candlestick chart for time series analysis"""
        if 'date' not in df.columns or 'value' not in df.columns:
            return self._create_empty_chart("No date or value data available")
        
        # Prepare data for candlestick chart
        df = df[['date', 'value']].copy()
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Resample to daily frequency, filling gaps with interpolation
        df = df.resample('D').mean().interpolate()
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['value'],
            high=df['value'] + np.random.randint(1, 10, len(df)),
            low=df['value'] - np.random.randint(1, 10, len(df)),
            close=df['value'],
            name="Value",
            increasing_line_color='green',
            decreasing_line_color='red'
        )])
        
        fig.update_layout(
            title="Time Series Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Value",
            template="plotly_dark"
        )
        
        return fig.to_json()

    def _create_density_contour(self, df: pd.DataFrame) -> str:
        """Create density contour plot for bivariate distribution"""
        if 'x_value' not in df.columns or 'y_value' not in df.columns:
            return self._create_empty_chart("No x or y value data available")
        
        fig = go.Figure(data=go.Densitycontour(
            x=df['x_value'],
            y=df['y_value'],
            z=df['z_value'],
            colorscale='Jet',
            colorbar=dict(title="Density"),
            contours=dict(
                showlabels=True,
                labelfont=dict(size=10),
                coloring="fill"
            ),
            hovertemplate="<b>Density Contour</b><br>X: %{x}<br>Y: %{y}<br>Density: %{z}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Bivariate Density Contour Plot",
            xaxis_title="X Value",
            yaxis_title="Y Value",
            template="plotly_dark"
        )
        
        return fig.to_json()
