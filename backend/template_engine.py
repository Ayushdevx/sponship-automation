"""
Advanced Template Management System for Hackfinity
Supports various template types, customization, and dynamic content
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import json
from jinja2 import Environment, BaseLoader, meta
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

class TemplateVariable(BaseModel):
    """Represents a template variable"""
    name: str
    type: str = Field(..., description="Type: text, email, date, number, boolean, select, image")
    label: str
    description: Optional[str] = None
    required: bool = True
    default_value: Optional[Any] = None
    options: Optional[List[str]] = None  # For select type
    validation_regex: Optional[str] = None

class TemplateCategory(BaseModel):
    """Template category for organization"""
    id: str
    name: str
    description: str
    icon: str
    color: str

class AdvancedTemplate(BaseModel):
    """Advanced template model with rich features"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category_id: str
    template_type: str = Field(..., description="email, certificate, letter, invoice, report")
    
    # Template content
    subject: Optional[str] = None  # For email templates
    content: str
    html_content: Optional[str] = None
    css_styles: Optional[str] = None
    
    # Template metadata
    variables: List[TemplateVariable] = []
    tags: List[str] = []
    version: str = "1.0"
    is_active: bool = True
    is_premium: bool = False
    
    # Template settings
    layout: str = "default"
    color_scheme: Dict[str, str] = {}
    fonts: Dict[str, str] = {}
    dimensions: Dict[str, Any] = {}
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Usage statistics
    usage_count: int = 0
    rating: float = 0.0
    reviews: List[Dict[str, Any]] = []

class TemplateEngine:
    """Advanced template engine with Jinja2 and custom features"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.jinja_env = Environment(loader=BaseLoader())
        
        # Add custom filters
        self.jinja_env.filters['format_date'] = self._format_date
        self.jinja_env.filters['format_currency'] = self._format_currency
        self.jinja_env.filters['capitalize_words'] = self._capitalize_words
        self.jinja_env.filters['truncate_text'] = self._truncate_text
    
    async def get_template_categories(self) -> List[TemplateCategory]:
        """Get all template categories"""
        categories = [
            TemplateCategory(
                id="sponsors",
                name="Sponsor Communications",
                description="Templates for sponsor outreach and engagement",
                icon="💼",
                color="#6366f1"
            ),
            TemplateCategory(
                id="certificates",
                name="Certificates & Awards",
                description="Certificate templates for participants and winners",
                icon="🏆",
                color="#10b981"
            ),
            TemplateCategory(
                id="marketing",
                name="Marketing Materials",
                description="Promotional emails and marketing content",
                icon="📢",
                color="#f59e0b"
            ),
            TemplateCategory(
                id="notifications",
                name="Notifications",
                description="System notifications and alerts",
                icon="🔔",
                color="#8b5cf6"
            ),
            TemplateCategory(
                id="reports",
                name="Reports & Analytics",
                description="Report templates and data presentations",
                icon="📊",
                color="#06b6d4"
            ),
            TemplateCategory(
                id="legal",
                name="Legal Documents",
                description="Contracts, agreements, and legal documents",
                icon="📜",
                color="#64748b"
            )
        ]
        return categories
    
    async def get_templates(self, category_id: Optional[str] = None, template_type: Optional[str] = None) -> List[AdvancedTemplate]:
        """Get templates with optional filtering"""
        query = {"is_active": True}
        
        if category_id:
            query["category_id"] = category_id
        if template_type:
            query["template_type"] = template_type
            
        cursor = self.db.templates.find(query)
        templates = await cursor.to_list(length=None)
        
        return [AdvancedTemplate(**template) for template in templates]
    
    async def create_template(self, template: AdvancedTemplate) -> AdvancedTemplate:
        """Create a new template"""
        # Extract variables from template content
        template.variables = self._extract_template_variables(template.content)
        
        # Save to database
        template_dict = template.dict()
        await self.db.templates.insert_one(template_dict)
        
        return template
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[AdvancedTemplate]:
        """Update an existing template"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.db.templates.update_one(
            {"id": template_id},
            {"$set": updates}
        )
        
        if result.modified_count:
            template_data = await self.db.templates.find_one({"id": template_id})
            return AdvancedTemplate(**template_data)
        
        return None
    
    async def delete_template(self, template_id: str) -> bool:
        """Soft delete a template"""
        result = await self.db.templates.update_one(
            {"id": template_id},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def create_advanced_template(self, template_data: Dict[str, Any]) -> AdvancedTemplate:
        """Create a new advanced template with rich features"""
        template = AdvancedTemplate(**template_data)
        
        # Auto-detect variables in template content
        if template.content:
            detected_vars = self._detect_template_variables(template.content)
            template.variables.extend(detected_vars)
        
        # Save to database
        template_dict = template.dict()
        await self.db.advanced_templates.insert_one(template_dict)
        
        return template
    
    async def get_template_builder_config(self) -> Dict[str, Any]:
        """Get configuration for the advanced template builder"""
        return {
            "components": {
                "text": {
                    "name": "Text Block",
                    "icon": "📝",
                    "properties": ["content", "font_size", "font_family", "color", "alignment", "line_height"],
                    "default_style": {"font_size": "14px", "color": "#333333", "line_height": "1.5"}
                },
                "heading": {
                    "name": "Heading",
                    "icon": "🎯",
                    "properties": ["content", "level", "font_size", "font_weight", "color", "alignment"],
                    "default_style": {"font_size": "24px", "font_weight": "bold", "color": "#1a1a1a"}
                },
                "image": {
                    "name": "Image",
                    "icon": "🖼️",
                    "properties": ["src", "alt", "width", "height", "alignment", "border_radius"],
                    "default_style": {"width": "100%", "height": "auto", "border_radius": "4px"}
                },
                "button": {
                    "name": "Button",
                    "icon": "🔘",
                    "properties": ["text", "url", "background_color", "text_color", "border_radius", "padding"],
                    "default_style": {"background_color": "#3b82f6", "text_color": "#ffffff", "border_radius": "6px", "padding": "12px 24px"}
                },
                "divider": {
                    "name": "Divider",
                    "icon": "➖",
                    "properties": ["height", "color", "style", "margin"],
                    "default_style": {"height": "1px", "color": "#e5e7eb", "style": "solid", "margin": "20px 0"}
                },
                "spacer": {
                    "name": "Spacer",
                    "icon": "⬜",
                    "properties": ["height"],
                    "default_style": {"height": "20px"}
                },
                "logo": {
                    "name": "Logo",
                    "icon": "🏢",
                    "properties": ["src", "width", "height", "alignment", "link"],
                    "default_style": {"width": "150px", "height": "auto", "alignment": "center"}
                },
                "social_links": {
                    "name": "Social Links",
                    "icon": "🔗",
                    "properties": ["platforms", "style", "size", "alignment"],
                    "default_style": {"style": "icons", "size": "24px", "alignment": "center"}
                },
                "qr_code": {
                    "name": "QR Code",
                    "icon": "📱",
                    "properties": ["content", "size", "color", "background", "alignment"],
                    "default_style": {"size": "150px", "color": "#000000", "background": "#ffffff"}
                },
                "variable": {
                    "name": "Dynamic Variable",
                    "icon": "🔀",
                    "properties": ["variable_name", "fallback_text", "format"],
                    "default_style": {"format": "text"}
                }
            },
            "layouts": {
                "single_column": {
                    "name": "Single Column",
                    "preview": "/static/layouts/single-column.png",
                    "structure": {"columns": 1, "max_width": "600px"}
                },
                "two_column": {
                    "name": "Two Column",
                    "preview": "/static/layouts/two-column.png",
                    "structure": {"columns": 2, "max_width": "800px", "column_ratio": "1:1"}
                },
                "sidebar": {
                    "name": "Sidebar Layout",
                    "preview": "/static/layouts/sidebar.png",
                    "structure": {"columns": 2, "max_width": "800px", "column_ratio": "2:1"}
                },
                "header_footer": {
                    "name": "Header & Footer",
                    "preview": "/static/layouts/header-footer.png",
                    "structure": {"sections": ["header", "content", "footer"], "max_width": "600px"}
                },
                "card_layout": {
                    "name": "Card Layout",
                    "preview": "/static/layouts/card.png",
                    "structure": {"style": "card", "padding": "40px", "border_radius": "12px", "shadow": true}
                }
            },
            "color_schemes": {
                "professional": {
                    "name": "Professional",
                    "primary": "#3b82f6",
                    "secondary": "#6b7280",
                    "accent": "#10b981",
                    "background": "#ffffff",
                    "text": "#1f2937"
                },
                "creative": {
                    "name": "Creative",
                    "primary": "#8b5cf6",
                    "secondary": "#ec4899",
                    "accent": "#f59e0b",
                    "background": "#fef3c7",
                    "text": "#374151"
                },
                "minimal": {
                    "name": "Minimal",
                    "primary": "#000000",
                    "secondary": "#6b7280",
                    "accent": "#3b82f6",
                    "background": "#ffffff",
                    "text": "#111827"
                },
                "tech": {
                    "name": "Tech",
                    "primary": "#06b6d4",
                    "secondary": "#64748b",
                    "accent": "#8b5cf6",
                    "background": "#0f172a",
                    "text": "#f1f5f9"
                }
            },
            "fonts": {
                "inter": {"name": "Inter", "category": "sans-serif", "weights": [300, 400, 500, 600, 700]},
                "roboto": {"name": "Roboto", "category": "sans-serif", "weights": [300, 400, 500, 700]},
                "poppins": {"name": "Poppins", "category": "sans-serif", "weights": [300, 400, 500, 600, 700]},
                "playfair": {"name": "Playfair Display", "category": "serif", "weights": [400, 500, 600, 700]},
                "merriweather": {"name": "Merriweather", "category": "serif", "weights": [300, 400, 700]},
                "source_code": {"name": "Source Code Pro", "category": "monospace", "weights": [400, 500, 600]}
            },
            "preset_templates": await self._get_preset_templates()
        }
    
    async def _get_preset_templates(self) -> List[Dict[str, Any]]:
        """Get preset templates for quick start"""
        return [
            {
                "id": "sponsor_welcome",
                "name": "Sponsor Welcome Email",
                "description": "Professional welcome email for new sponsors",
                "category": "sponsors",
                "preview": "/static/previews/sponsor-welcome.png",
                "components": [
                    {"type": "logo", "props": {"alignment": "center"}},
                    {"type": "heading", "props": {"content": "Welcome to Hackfinity!", "level": 1}},
                    {"type": "text", "props": {"content": "Thank you for partnering with us for this exciting journey."}},
                    {"type": "button", "props": {"text": "Get Started", "url": "https://hackfinity.com/sponsors"}}
                ]
            },
            {
                "id": "certificate_achievement",
                "name": "Achievement Certificate",
                "description": "Beautiful certificate for participants",
                "category": "certificates",
                "preview": "/static/previews/certificate-achievement.png",
                "components": [
                    {"type": "image", "props": {"src": "/static/certificate-border.png", "alt": "Certificate Border"}},
                    {"type": "heading", "props": {"content": "Certificate of Achievement", "level": 1}},
                    {"type": "text", "props": {"content": "This is to certify that {{participant_name}} has successfully completed {{course_name}}"}},
                    {"type": "qr_code", "props": {"content": "{{verification_url}}", "alignment": "right"}}
                ]
            },
            {
                "id": "sponsor_thank_you",
                "name": "Thank You Note",
                "description": "Appreciation message for sponsors",
                "category": "sponsors",
                "preview": "/static/previews/thank-you.png",
                "components": [
                    {"type": "heading", "props": {"content": "Thank You!", "level": 1}},
                    {"type": "text", "props": {"content": "Your support made Hackfinity {{year}} a huge success."}},
                    {"type": "divider"},
                    {"type": "text", "props": {"content": "Impact Statistics:", "font_weight": "bold"}},
                    {"type": "text", "props": {"content": "• {{participants_count}} participants\n• {{projects_count}} amazing projects\n• {{awards_count}} awards distributed"}}
                ]
            },
            {
                "id": "winner_certificate",
                "name": "Winner Certificate",
                "description": "Special certificate for competition winners",
                "category": "certificates",
                "preview": "/static/previews/winner-certificate.png",
                "components": [
                    {"type": "image", "props": {"src": "/static/winner-badge.png", "alignment": "center"}},
                    {"type": "heading", "props": {"content": "🏆 Winner Certificate", "level": 1}},
                    {"type": "text", "props": {"content": "Congratulations {{winner_name}}! You won {{award_category}} at Hackfinity {{year}}"}},
                    {"type": "text", "props": {"content": "Project: {{project_name}}", "font_style": "italic"}},
                    {"type": "spacer", "props": {"height": "40px"}},
                    {"type": "social_links", "props": {"platforms": ["twitter", "linkedin", "facebook"]}}
                ]
            }
        ]
    
    async def duplicate_template(self, template_id: str, new_name: str) -> AdvancedTemplate:
        """Duplicate an existing template"""
        original = await self.db.advanced_templates.find_one({"id": template_id})
        if not original:
            raise ValueError(f"Template {template_id} not found")
        
        # Create duplicate with new ID and name
        duplicate_data = original.copy()
        duplicate_data["id"] = str(uuid.uuid4())
        duplicate_data["name"] = new_name
        duplicate_data["created_at"] = datetime.utcnow()
        duplicate_data["updated_at"] = datetime.utcnow()
        duplicate_data["usage_count"] = 0
        duplicate_data["version"] = "1.0"
        
        await self.db.advanced_templates.insert_one(duplicate_data)
        return AdvancedTemplate(**duplicate_data)
    
    async def get_template_analytics(self, template_id: str) -> Dict[str, Any]:
        """Get analytics for a specific template"""
        template = await self.db.advanced_templates.find_one({"id": template_id})
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get usage statistics
        usage_stats = await self.db.template_usage.aggregate([
            {"$match": {"template_id": template_id}},
            {"$group": {
                "_id": "$template_id",
                "total_uses": {"$sum": 1},
                "unique_users": {"$addToSet": "$user_id"},
                "avg_generation_time": {"$avg": "$generation_time_ms"},
                "success_rate": {"$avg": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}}}
            }}
        ]).to_list(length=1)
        
        return {
            "template_id": template_id,
            "template_name": template["name"],
            "usage_statistics": usage_stats[0] if usage_stats else {},
            "performance_metrics": {
                "avg_rating": template.get("rating", 0),
                "total_reviews": len(template.get("reviews", [])),
                "last_used": await self._get_last_usage_date(template_id),
                "conversion_rate": await self._calculate_conversion_rate(template_id)
            },
            "popular_variables": await self._get_popular_variables(template_id),
            "geographic_usage": await self._get_geographic_usage(template_id)
        }
    
    async def export_template(self, template_id: str, format: str = "json") -> Dict[str, Any]:
        """Export template in various formats"""
        template = await self.db.advanced_templates.find_one({"id": template_id})
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        if format == "json":
            return template
        elif format == "html":
            return {"html": await self._render_template_html(template)}
        elif format == "pdf":
            return {"pdf_url": await self._generate_template_pdf(template)}
        else:
            raise ValueError(f"Unsupported export format: {format}")

    # ...existing helper methods continue...
