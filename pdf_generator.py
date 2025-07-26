# pdf_generator.py — Enhanced with IEEE-style 2-Column Layout

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.platypus import Table, TableStyle, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.units import inch, cm
from io import BytesIO
import os
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# Get Unicode font from font manager
from font_manager import UNICODE_FONT_PATH

if UNICODE_FONT_PATH and os.path.exists(UNICODE_FONT_PATH):
    font_name = os.path.splitext(os.path.basename(UNICODE_FONT_PATH))[0]
    pdfmetrics.registerFont(TTFont(font_name, UNICODE_FONT_PATH))
    FONT_NAME = font_name
else:
    FONT_NAME = 'Helvetica'

@dataclass
class PDFStyle:
    font_name: str
    font_size: int
    font_color: str
    alignment: str
    spacing_before: int = 0
    spacing_after: int = 0

@dataclass
class PDFStyles:
    title: PDFStyle
    authors: PDFStyle
    abstract: PDFStyle
    heading1: PDFStyle
    heading2: PDFStyle
    body: PDFStyle
    bullet_point: PDFStyle

@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    publication_year: str
    abstract: str = ""
    keywords: List[str] = None
    doi: str = ""

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

class ConferencePDFTemplate(BaseDocTemplate):
    def __init__(self, filename, title="", authors=[], conference_info="", two_column=False, **kwargs):
        super().__init__(filename, **kwargs)
        self.title = title
        self.authors = authors
        self.conference_info = conference_info
        self.page_count = 0

        if two_column:
            frame1 = Frame(self.leftMargin, self.bottomMargin + 0.7*inch,
                           self.width/2 - 6, self.height - 1.2*inch, id='col1')
            frame2 = Frame(self.leftMargin + self.width/2 + 6, self.bottomMargin + 0.7*inch,
                           self.width/2 - 6, self.height - 1.2*inch, id='col2')
            template = PageTemplate(id='2col', frames=[frame1, frame2], onPage=self.add_header_footer)
        else:
            frame = Frame(self.leftMargin, self.bottomMargin + 0.7*inch,
                          self.width, self.height - 1.2*inch, id='normal')
            template = PageTemplate(id='default', frames=frame, onPage=self.add_header_footer)

        self.addPageTemplates([template])

    def add_header_footer(self, canvas, doc):
        canvas.saveState()

        if doc.page != 1:
            canvas.setFont(FONT_NAME, 9)
            canvas.setFillColor(colors.grey)
            header_text = f"{self.title[:60]}..." if len(self.title) > 60 else self.title
            canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 12, header_text)
            canvas.line(doc.leftMargin, doc.height + doc.topMargin - 20,
                        doc.width + doc.leftMargin, doc.height + doc.topMargin - 20)

            canvas.line(doc.leftMargin, doc.bottomMargin - 30,
                        doc.width + doc.leftMargin, doc.bottomMargin - 30)

            canvas.drawString(doc.width/2 + doc.leftMargin, doc.bottomMargin - 45,
                              str(doc.page))

            canvas.drawString(doc.leftMargin, doc.bottomMargin - 45,
                              self.conference_info)

            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 45,
                                   current_date)

        canvas.restoreState()

class ProfessionalPDFGenerator:
    def __init__(self, font_name=FONT_NAME):
        self.font_name = font_name

        styles = getSampleStyleSheet()
        self.styles = {
            'Title': ParagraphStyle(
                'Title', parent=styles['Normal'], fontName=self.font_name,
                fontSize=24, spaceAfter=30, alignment=TA_CENTER
            ),
            'Authors': ParagraphStyle(
                'Authors', parent=styles['Normal'], fontName=self.font_name,
                fontSize=12, spaceAfter=20, alignment=TA_CENTER
            ),
            'Abstract': ParagraphStyle(
                'Abstract', parent=styles['Normal'], fontName=self.font_name,
                fontSize=10, leftIndent=72, rightIndent=72, spaceBefore=20,
                spaceAfter=20, alignment=TA_JUSTIFY
            ),
            'Heading1': ParagraphStyle(
                'Heading1', parent=styles['Normal'], fontName=self.font_name,
                fontSize=16, spaceBefore=24, spaceAfter=12, keepWithNext=True
            ),
            'Heading2': ParagraphStyle(
                'Heading2', parent=styles['Normal'], fontName=self.font_name,
                fontSize=14, spaceBefore=18, spaceAfter=10, keepWithNext=True
            ),
            'Body': ParagraphStyle(
                'Body', parent=styles['Normal'], fontName=self.font_name,
                fontSize=11, leading=14, alignment=TA_JUSTIFY, spaceBefore=8,
                spaceAfter=8, firstLineIndent=24
            ),
            'BulletPoint': ParagraphStyle(
                'BulletPoint', parent=styles['Normal'], fontName=self.font_name,
                fontSize=11, leading=14, leftIndent=36, bulletIndent=20,
                spaceBefore=4, spaceAfter=4
            )
        }

    def create_pdf(self, summary_text, metadata=None):
        try:
            buffer = BytesIO()
            metadata = metadata or {}
            title = metadata.get('title', 'Research Paper Analysis')
            authors = metadata.get('authors', [])
            year = metadata.get('publication_year', '')

            doc = ConferencePDFTemplate(
                buffer,
                title=title,
                authors=authors,
                conference_info='AI Research Paper Analysis Report',
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                two_column=True
            )

            elements = []
            elements.append(Paragraph(title, self.styles['Title']))
            if authors:
                elements.append(Paragraph('by', self.styles['Authors']))
                elements.append(Paragraph(', '.join(authors), self.styles['Authors']))
            if year:
                elements.append(Paragraph(year, self.styles['Authors']))

            elements.append(Spacer(1, 60))
            elements.append(Paragraph('Abstract', self.styles['Heading1']))

            if summary_text:
                paragraphs = summary_text.split('\n\n')
                current_list_items = []

                if paragraphs:
                    elements.append(Paragraph(paragraphs[0], self.styles['Abstract']))
                    elements.append(PageBreak())

                for paragraph in paragraphs[1:]:
                    paragraph = paragraph.strip()
                    if not paragraph:
                        continue

                    if paragraph.startswith('# '):
                        if current_list_items:
                            for item in current_list_items:
                                elements.append(Paragraph(item, self.styles['BulletPoint']))
                            current_list_items = []
                        header = paragraph.replace('# ', '')
                        elements.append(Paragraph(header, self.styles['Heading1']))

                    elif paragraph.startswith('## '):
                        if current_list_items:
                            for item in current_list_items:
                                elements.append(Paragraph(item, self.styles['BulletPoint']))
                            current_list_items = []
                        header = paragraph.replace('## ', '')
                        elements.append(Paragraph(header, self.styles['Heading2']))

                    elif paragraph.startswith('- ') or paragraph.startswith('• '):
                        item = paragraph.replace('- ', '').replace('• ', '')
                        item = f'• {item}'
                        current_list_items.append(item)

                    else:
                        if current_list_items:
                            for item in current_list_items:
                                elements.append(Paragraph(item, self.styles['BulletPoint']))
                            current_list_items = []
                        paragraph = paragraph.replace('**', '').replace('*', '')
                        elements.append(Paragraph(paragraph, self.styles['Body']))

            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = [
                Paragraph(f"Error creating PDF: {str(e)}", self.styles['Body'])
            ]
            doc.build(elements)
            buffer.seek(0)
            return buffer.getvalue()

# Create a singleton instance
pdf_generator = ProfessionalPDFGenerator()
