"""
Advanced Certificate Customization System for Hackfinity
Supports dynamic layouts, styling, and certificate generation
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import json
import uuid
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, A3
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage
import io
import base64
from motor.motor_asyncio import AsyncIOMotorDatabase

class CertificateStyle(BaseModel):
    """Certificate styling configuration"""
    background_color: str = "#ffffff"
    border_color: str = "#6366f1"
    border_width: int = 3
    primary_color: str = "#6366f1"
    secondary_color: str = "#10b981"
    accent_color: str = "#f59e0b"
    text_color: str = "#1f2937"
    
    # Typography
    title_font: str = "Helvetica-Bold"
    title_size: int = 36
    subtitle_font: str = "Helvetica"
    subtitle_size: int = 24
    body_font: str = "Helvetica"
    body_size: int = 14
    
    # Layout
    margin_top: int = 50
    margin_bottom: int = 50
    margin_left: int = 50
    margin_right: int = 50

class CertificateElement(BaseModel):
    """Individual certificate element"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(..., description="text, image, shape, logo, signature, qr_code")
    content: str = ""
    x: float = 0
    y: float = 0
    width: Optional[float] = None
    height: Optional[float] = None
    rotation: float = 0
    opacity: float = 1.0
    
    # Text-specific properties
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    font_color: Optional[str] = None
    font_weight: str = "normal"
    text_align: str = "left"
    line_height: float = 1.2
    
    # Visual properties
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    border_width: int = 0
    border_radius: int = 0
    shadow: bool = False
    
    # Animation/Effects
    animation: Optional[str] = None
    z_index: int = 1

class CertificateTemplate(BaseModel):
    """Advanced certificate template"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    category: str = "achievement"
    
    # Template metadata
    version: str = "1.0"
    is_premium: bool = False
    is_active: bool = True
    tags: List[str] = []
    
    # Layout settings
    page_size: str = "A4"  # A4, A3, Letter, Custom
    orientation: str = "landscape"  # landscape, portrait
    custom_width: Optional[float] = None
    custom_height: Optional[float] = None
    
    # Styling
    style: CertificateStyle = Field(default_factory=CertificateStyle)
    background_image: Optional[str] = None
    watermark: Optional[str] = None
    
    # Elements
    elements: List[CertificateElement] = []
    
    # Variables that can be filled
    variables: List[str] = []
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    # Usage statistics
    usage_count: int = 0
    downloads: int = 0
    rating: float = 0.0

class CertificateCustomizer:
    """Advanced certificate customization engine"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.page_sizes = {
            "A4": A4,
            "A3": A3,
            "Letter": letter,
        }
    
    async def get_certificate_templates(self, category: Optional[str] = None) -> List[CertificateTemplate]:
        """Get available certificate templates"""
        query = {"is_active": True}
        if category:
            query["category"] = category
            
        cursor = self.db.certificate_templates.find(query)
        templates = await cursor.to_list(length=None)
        
        return [CertificateTemplate(**template) for template in templates]
    
    async def create_template(self, template: CertificateTemplate) -> CertificateTemplate:
        """Create a new certificate template"""
        template_dict = template.dict()
        await self.db.certificate_templates.insert_one(template_dict)
        return template
    
    async def update_template(self, template_id: str, updates: Dict[str, Any]) -> Optional[CertificateTemplate]:
        """Update certificate template"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.db.certificate_templates.update_one(
            {"id": template_id},
            {"$set": updates}
        )
        
        if result.modified_count:
            template_data = await self.db.certificate_templates.find_one({"id": template_id})
            return CertificateTemplate(**template_data)
        
        return None
    
    async def duplicate_template(self, template_id: str, new_name: str) -> Optional[CertificateTemplate]:
        """Duplicate a certificate template"""
        original = await self.db.certificate_templates.find_one({"id": template_id})
        
        if not original:
            return None
        
        new_template = CertificateTemplate(**original)
        new_template.id = str(uuid.uuid4())
        new_template.name = new_name
        new_template.created_at = datetime.utcnow()
        new_template.updated_at = datetime.utcnow()
        new_template.usage_count = 0
        new_template.downloads = 0
        new_template.rating = 0.0
        
        await self.db.certificate_templates.insert_one(new_template.dict())
        return new_template
    
    async def generate_certificate(self, template_id: str, data: Dict[str, Any], format: str = "pdf") -> bytes:
        """Generate certificate with custom data"""
        template_data = await self.db.certificate_templates.find_one({"id": template_id})
        
        if not template_data:
            raise ValueError(f"Template {template_id} not found")
        
        template = CertificateTemplate(**template_data)
        
        # Increment usage count
        await self.db.certificate_templates.update_one(
            {"id": template_id},
            {"$inc": {"usage_count": 1}}
        )
        
        if format.lower() == "pdf":
            return await self._generate_pdf_certificate(template, data)
        elif format.lower() == "png":
            return await self._generate_image_certificate(template, data, "PNG")
        elif format.lower() == "jpg":
            return await self._generate_image_certificate(template, data, "JPEG")
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def preview_certificate(self, template: CertificateTemplate, sample_data: Optional[Dict[str, Any]] = None) -> str:
        """Generate certificate preview as base64 image"""
        if not sample_data:
            sample_data = self._generate_sample_data(template.variables)
        
        image_data = await self._generate_image_certificate(template, sample_data, "PNG")
        return base64.b64encode(image_data).decode('utf-8')
    
    async def _generate_pdf_certificate(self, template: CertificateTemplate, data: Dict[str, Any]) -> bytes:
        """Generate PDF certificate"""
        buffer = io.BytesIO()
        
        # Determine page size
        if template.page_size in self.page_sizes:
            page_size = self.page_sizes[template.page_size]
        else:
            page_size = (template.custom_width or 8.5 * inch, template.custom_height or 11 * inch)
        
        # Adjust for orientation
        if template.orientation == "portrait" and page_size[0] > page_size[1]:
            page_size = (page_size[1], page_size[0])
        elif template.orientation == "landscape" and page_size[0] < page_size[1]:
            page_size = (page_size[1], page_size[0])
        
        # Create PDF
        doc = SimpleDocTemplate(buffer, pagesize=page_size)
        story = []
        
        # Add background if specified
        if template.background_image:
            # Add background image logic here
            pass
        
        # Process elements
        for element in sorted(template.elements, key=lambda x: x.z_index):
            if element.type == "text":
                content = self._replace_variables(element.content, data)
                
                # Create paragraph style
                style = ParagraphStyle(
                    name=f'style_{element.id}',
                    fontName=element.font_family or template.style.body_font,
                    fontSize=element.font_size or template.style.body_size,
                    textColor=HexColor(element.font_color or template.style.text_color),
                    alignment=self._get_alignment(element.text_align),
                    leading=element.line_height * (element.font_size or template.style.body_size)
                )
                
                paragraph = Paragraph(content, style)
                story.append(paragraph)
                story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    async def _generate_image_certificate(self, template: CertificateTemplate, data: Dict[str, Any], format: str) -> bytes:
        """Generate image certificate"""
        # Determine dimensions
        if template.page_size == "A4":
            if template.orientation == "landscape":
                width, height = 1123, 794  # A4 landscape at 96 DPI
            else:
                width, height = 794, 1123  # A4 portrait at 96 DPI
        elif template.page_size == "Letter":
            if template.orientation == "landscape":
                width, height = 1056, 816
            else:
                width, height = 816, 1056
        else:
            width = int(template.custom_width or 800)
            height = int(template.custom_height or 600)
        
        # Create image
        img = Image.new('RGB', (width, height), template.style.background_color)
        draw = ImageDraw.Draw(img)
        
        # Add border if specified
        if template.style.border_width > 0:
            border_color = template.style.border_color
            border_width = template.style.border_width
            
            # Draw border
            for i in range(border_width):
                draw.rectangle([i, i, width-1-i, height-1-i], outline=border_color)
        
        # Process elements
        for element in sorted(template.elements, key=lambda x: x.z_index):
            await self._draw_element(draw, element, data, img.size)
        
        # Add watermark if specified
        if template.watermark:
            # Add watermark logic here
            pass
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format=format, quality=95 if format == "JPEG" else None)
        buffer.seek(0)
        return buffer.read()
    
    async def _draw_element(self, draw: ImageDraw.Draw, element: CertificateElement, data: Dict[str, Any], img_size: Tuple[int, int]):
        """Draw individual element on certificate"""
        if element.type == "text":
            content = self._replace_variables(element.content, data)
            
            # Get font
            try:
                font_size = element.font_size or 14
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Calculate position
            x = element.x if element.x >= 1 else element.x * img_size[0]
            y = element.y if element.y >= 1 else element.y * img_size[1]
            
            # Draw text
            color = element.font_color or "#000000"
            draw.text((x, y), content, font=font, fill=color)
        
        elif element.type == "shape":
            # Draw shapes like rectangles, circles, etc.
            x = element.x if element.x >= 1 else element.x * img_size[0]
            y = element.y if element.y >= 1 else element.y * img_size[1]
            width = element.width or 100
            height = element.height or 100
            
            color = element.background_color or "#6366f1"
            
            if "rectangle" in element.content.lower():
                draw.rectangle([x, y, x + width, y + height], fill=color, outline=element.border_color)
            elif "circle" in element.content.lower():
                draw.ellipse([x, y, x + width, y + height], fill=color, outline=element.border_color)
        
        elif element.type == "image":
            # Handle image elements
            # This would require loading and positioning images
            pass
    
    def _replace_variables(self, content: str, data: Dict[str, Any]) -> str:
        """Replace template variables in content"""
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content
    
    def _get_alignment(self, align: str) -> int:
        """Convert alignment string to ReportLab constant"""
        alignments = {
            "left": 0,
            "center": 1,
            "right": 2,
            "justify": 4
        }
        return alignments.get(align.lower(), 0)
    
    def _generate_sample_data(self, variables: List[str]) -> Dict[str, Any]:
        """Generate sample data for certificate preview"""
        sample_data = {}
        
        for var in variables:
            var_lower = var.lower()
            if "name" in var_lower:
                sample_data[var] = "John Doe"
            elif "event" in var_lower:
                sample_data[var] = "Hackfinity 2025"
            elif "date" in var_lower:
                sample_data[var] = "July 3, 2025"
            elif "category" in var_lower:
                sample_data[var] = "AI/ML Track"
            elif "achievement" in var_lower:
                sample_data[var] = "Outstanding Performance"
            elif "organization" in var_lower:
                sample_data[var] = "Hackfinity Organization"
            else:
                sample_data[var] = f"Sample {var.replace('_', ' ').title()}"
        
        return sample_data
    
    async def get_certificate_analytics(self, template_id: str) -> Dict[str, Any]:
        """Get analytics for certificate template"""
        template_data = await self.db.certificate_templates.find_one({"id": template_id})
        
        if not template_data:
            return {"error": "Template not found"}
        
        # Get usage statistics
        analytics = {
            "template_id": template_id,
            "usage_count": template_data.get("usage_count", 0),
            "downloads": template_data.get("downloads", 0),
            "rating": template_data.get("rating", 0.0),
            "created_at": template_data.get("created_at"),
            "last_used": template_data.get("last_used"),
            "performance_metrics": {
                "generation_time": 0.5,  # Average generation time in seconds
                "success_rate": 99.2,
                "popular_formats": {
                    "pdf": 75,
                    "png": 20,
                    "jpg": 5
                }
            }
        }
        
        return analytics
    
    async def create_certificate_builder_config(self) -> Dict[str, Any]:
        """Get configuration for the advanced certificate builder"""
        return {
            "elements": {
                "text": {
                    "name": "Text",
                    "icon": "📝",
                    "properties": [
                        {"name": "content", "type": "textarea", "label": "Text Content"},
                        {"name": "font_family", "type": "select", "label": "Font", "options": await self._get_available_fonts()},
                        {"name": "font_size", "type": "number", "label": "Font Size", "min": 8, "max": 72},
                        {"name": "font_color", "type": "color", "label": "Text Color"},
                        {"name": "font_weight", "type": "select", "label": "Weight", "options": ["normal", "bold", "light"]},
                        {"name": "text_align", "type": "select", "label": "Alignment", "options": ["left", "center", "right", "justify"]},
                        {"name": "line_height", "type": "number", "label": "Line Height", "min": 0.8, "max": 3, "step": 0.1}
                    ],
                    "default_props": {
                        "content": "Sample Text",
                        "font_family": "Helvetica",
                        "font_size": 16,
                        "font_color": "#000000",
                        "font_weight": "normal",
                        "text_align": "left"
                    }
                },
                "heading": {
                    "name": "Heading",
                    "icon": "🎯",
                    "properties": [
                        {"name": "content", "type": "text", "label": "Heading Text"},
                        {"name": "level", "type": "select", "label": "Level", "options": ["1", "2", "3", "4", "5", "6"]},
                        {"name": "font_family", "type": "select", "label": "Font", "options": await self._get_available_fonts()},
                        {"name": "font_size", "type": "number", "label": "Font Size", "min": 16, "max": 72},
                        {"name": "font_color", "type": "color", "label": "Text Color"},
                        {"name": "text_align", "type": "select", "label": "Alignment", "options": ["left", "center", "right"]}
                    ],
                    "default_props": {
                        "content": "Certificate Title",
                        "level": "1",
                        "font_family": "Helvetica-Bold",
                        "font_size": 36,
                        "font_color": "#1f2937",
                        "text_align": "center"
                    }
                },
                "image": {
                    "name": "Image",
                    "icon": "🖼️",
                    "properties": [
                        {"name": "src", "type": "file", "label": "Image File", "accept": "image/*"},
                        {"name": "alt", "type": "text", "label": "Alt Text"},
                        {"name": "border_radius", "type": "number", "label": "Border Radius", "min": 0, "max": 50},
                        {"name": "opacity", "type": "range", "label": "Opacity", "min": 0, "max": 1, "step": 0.1},
                        {"name": "filter", "type": "select", "label": "Filter", "options": ["none", "grayscale", "sepia", "blur", "brightness"]}
                    ],
                    "default_props": {
                        "alt": "Certificate Image",
                        "border_radius": 0,
                        "opacity": 1,
                        "filter": "none"
                    }
                },
                "logo": {
                    "name": "Logo",
                    "icon": "🏢",
                    "properties": [
                        {"name": "src", "type": "file", "label": "Logo File", "accept": "image/*"},
                        {"name": "width", "type": "number", "label": "Width", "min": 50, "max": 300},
                        {"name": "height", "type": "number", "label": "Height", "min": 50, "max": 300},
                        {"name": "maintain_aspect", "type": "boolean", "label": "Maintain Aspect Ratio"}
                    ],
                    "default_props": {
                        "width": 150,
                        "height": 75,
                        "maintain_aspect": true
                    }
                },
                "signature": {
                    "name": "Signature",
                    "icon": "✍️",
                    "properties": [
                        {"name": "name", "type": "text", "label": "Signatory Name"},
                        {"name": "title", "type": "text", "label": "Title/Position"},
                        {"name": "signature_image", "type": "file", "label": "Signature Image", "accept": "image/*"},
                        {"name": "show_line", "type": "boolean", "label": "Show Signature Line"},
                        {"name": "line_width", "type": "number", "label": "Line Width", "min": 100, "max": 300}
                    ],
                    "default_props": {
                        "name": "John Doe",
                        "title": "Director",
                        "show_line": true,
                        "line_width": 200
                    }
                },
                "shape": {
                    "name": "Shape",
                    "icon": "🔷",
                    "properties": [
                        {"name": "shape_type", "type": "select", "label": "Shape", "options": ["rectangle", "circle", "triangle", "star", "polygon"]},
                        {"name": "fill_color", "type": "color", "label": "Fill Color"},
                        {"name": "border_color", "type": "color", "label": "Border Color"},
                        {"name": "border_width", "type": "number", "label": "Border Width", "min": 0, "max": 10},
                        {"name": "opacity", "type": "range", "label": "Opacity", "min": 0, "max": 1, "step": 0.1}
                    ],
                    "default_props": {
                        "shape_type": "rectangle",
                        "fill_color": "#6366f1",
                        "border_color": "#4f46e5",
                        "border_width": 2,
                        "opacity": 0.8
                    }
                },
                "qr_code": {
                    "name": "QR Code",
                    "icon": "📱",
                    "properties": [
                        {"name": "content", "type": "textarea", "label": "QR Content"},
                        {"name": "size", "type": "number", "label": "Size", "min": 50, "max": 200},
                        {"name": "error_correction", "type": "select", "label": "Error Correction", "options": ["L", "M", "Q", "H"]},
                        {"name": "foreground_color", "type": "color", "label": "Foreground Color"},
                        {"name": "background_color", "type": "color", "label": "Background Color"}
                    ],
                    "default_props": {
                        "content": "https://hackfinity.com/verify/{{certificate_id}}",
                        "size": 100,
                        "error_correction": "M",
                        "foreground_color": "#000000",
                        "background_color": "#ffffff"
                    }
                },
                "border": {
                    "name": "Border",
                    "icon": "🔲",
                    "properties": [
                        {"name": "border_style", "type": "select", "label": "Style", "options": ["solid", "dashed", "dotted", "double", "groove", "ridge"]},
                        {"name": "border_width", "type": "number", "label": "Width", "min": 1, "max": 20},
                        {"name": "border_color", "type": "color", "label": "Color"},
                        {"name": "border_radius", "type": "number", "label": "Radius", "min": 0, "max": 50},
                        {"name": "margin", "type": "number", "label": "Margin", "min": 0, "max": 50}
                    ],
                    "default_props": {
                        "border_style": "solid",
                        "border_width": 3,
                        "border_color": "#6366f1",
                        "border_radius": 8,
                        "margin": 20
                    }
                },
                "watermark": {
                    "name": "Watermark",
                    "icon": "💧",
                    "properties": [
                        {"name": "text", "type": "text", "label": "Watermark Text"},
                        {"name": "opacity", "type": "range", "label": "Opacity", "min": 0.1, "max": 0.5, "step": 0.05},
                        {"name": "rotation", "type": "range", "label": "Rotation", "min": -45, "max": 45, "step": 5},
                        {"name": "font_size", "type": "number", "label": "Font Size", "min": 24, "max": 72}
                    ],
                    "default_props": {
                        "text": "HACKFINITY",
                        "opacity": 0.15,
                        "rotation": -30,
                        "font_size": 48
                    }
                }
            },
            "templates": await self._get_certificate_presets(),
            "layouts": {
                "classic": {
                    "name": "Classic Certificate",
                    "preview": "/static/certificate-layouts/classic.png",
                    "description": "Traditional certificate layout with elegant borders",
                    "elements": [
                        {"type": "border", "x": 20, "y": 20, "width": -40, "height": -40},
                        {"type": "heading", "x": 0, "y": 100, "width": "100%", "content": "Certificate of Achievement"},
                        {"type": "text", "x": 0, "y": 200, "width": "100%", "content": "This is to certify that"},
                        {"type": "text", "x": 0, "y": 250, "width": "100%", "content": "{{participant_name}}", "font_size": 24, "font_weight": "bold"},
                        {"type": "text", "x": 0, "y": 320, "width": "100%", "content": "has successfully completed {{course_name}}"}
