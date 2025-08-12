from typing import Dict, List, Optional
from pdf_generator import ProfessionalPDFGenerator as AdvancedPDFGenerator, PaperMetadata, PDFStyles, PDFStyle, pdf_generator
from datetime import datetime
import streamlit as st
import logging
import re
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

class PDFIntegration:
    """Integration class to connect PDF generation with Streamlit app"""
    def __init__(self):
        self.generator = pdf_generator  # Use the singleton instance
        self.logger = logging.getLogger(__name__)
    
    def format_metadata(self, paper_data: Dict) -> PaperMetadata:
        return PaperMetadata(
            title=paper_data.get('title', ''),
            authors=paper_data.get('authors', []),
            publication_year=paper_data.get('publication_year', ''),
            abstract="",  # Skip including in metadata if minimal format desired
            keywords=[],  # Remove keyword clutter from metadata
            doi="",
            journal="",
            university=""
    )
    
    def create_single_paper_pdf(self, paper_data: Dict, style_preset: str = "academic") -> bytes:
        """Generate PDF for a single paper analysis"""
        try:
            metadata = self.format_metadata(paper_data)
            # Format content with sections
            content = self._format_paper_content(paper_data)
            
            # Generate PDF - style presets are now handled internally
            pdf_bytes = self.generator.create_pdf(
                summary_text=content,
                metadata=metadata.__dict__
            )
            
            return pdf_bytes
        
        except Exception as e:
            self.logger.error(f"PDF generation failed: {str(e)}")
            raise
    
    def create_comparison_pdf(self, papers_data: List[Dict], comparison_data: Dict, style_preset: str = "modern") -> bytes:
        """Generate PDF for paper comparison analysis"""
        try:
            # Create comparison content
            content = self._format_comparison_content(papers_data, comparison_data)
            
            # Create metadata for comparison
            metadata = PaperMetadata(
                title="Research Papers Comparative Analysis",
                authors=["AI Research Paper Analyzer"],
                publication_year=str(datetime.now().year),
                abstract=f"Comparative analysis of {len(papers_data)} research papers using AI-powered analysis",
                keywords=self._extract_common_keywords(papers_data),
                doi="",
                journal="",
                university=""
            )
            
            return self.generator.create_pdf(
                summary_text=content,
                metadata=metadata.__dict__
            )
        
        except Exception as e:
            self.logger.error(f"Comparison PDF generation failed: {str(e)}")
            raise
    
    def _format_paper_content(self, paper_data: Dict) -> str:
        """Format content for PDF: summary only, strictly no extracted sections"""
        sections = []
        
        # Title and author block
        title = paper_data.get("title", "Untitled Paper")
        authors = paper_data.get("authors", [])
        year = paper_data.get("publication_year", "")
        abstract = paper_data.get("abstract", "")
        summary = paper_data.get("summary", "")

        # Authors and metadata
        author_line = ", ".join(paper_data.get("authors", []))
        pub_year = paper_data.get("publication_year", "")
        if author_line or pub_year:
            sections.append(f"**Authors**: {author_line if author_line else 'Unknown'}")
            if pub_year:
                sections[-1] += f" | **Year**: {pub_year}"
        
        # Abstract (optional but recommended for context)
        if paper_data.get("abstract"):
            sections.append(f"\n## Abstract\n{paper_data['abstract']}\n")
        
        # Final Summary
        if paper_data.get("summary"):
            sections.append("## AI-Generated Summary\n")
            sections.append(paper_data["summary"])

        
        return "\n\n".join(sections)
    
    def _format_comparison_content(self, papers_data: List[Dict], comparison_data: Dict) -> str:
        """Format comparison data into structured markdown"""
        sections = ["# Comparative Summary of Research Papers\n"]
        
        # Overview
        sections.append("# Research Papers Comparative Analysis\n")
        sections.append("## Overview\n")
        sections.append(f"Analysis of {len(papers_data)} research papers using AI-powered processing.\n")
        
        # Statistics
        sections.append("## Processing Statistics\n")
        stats = comparison_data.get('summary_stats', {})
        sections.append(f"- **Total Papers**: {stats.get('total_papers', len(papers_data))}")
        sections.append(f"- **Average Processing Time**: {stats.get('avg_processing_time', 0):.2f} seconds")
        sections.append(f"- **Total Keywords**: {stats.get('total_keywords', 0)}")
        sections.append(f"- **Average Chunks**: {stats.get('avg_chunks', 0):.1f}\n")
        
        # Papers comparison
        sections.append("## Individual Papers Summary\n")
        for paper in papers_data:
            sections.append(f"### {paper.get('title', 'Untitled')}\n")
            sections.append(f"**Authors**: {', '.join(paper.get('authors', ['Unknown']))}")
            sections.append(f"**Year**: {paper.get('publication_year', 'Unknown')}")
            if paper.get('abstract'):
                sections.append(f"\n**Abstract**: {paper['abstract'][:300]}...")
            sections.append("\n**Key Points**:")
            sections.append(paper.get('summary', 'No summary available')[:500] + "...\n")
        
        # Keyword overlap analysis
        if comparison_data.get('keyword_overlap'):
            sections.append("## Common Themes and Keywords\n")
            for keyword, papers in comparison_data['keyword_overlap'].items():
                sections.append(f"- **{keyword}**: Found in {len(papers)} papers")
        
        return "\n\n".join(sections)
    
    def _extract_common_keywords(self, papers_data: List[Dict]) -> List[str]:
        """Extract common keywords across papers"""
        all_keywords = set()
        for paper in papers_data:
            all_keywords.update(paper.get('keywords', []))
        return list(all_keywords)[:10]  # Return top 10 keywords

# Streamlit UI integration components
def pdf_export_ui(paper_data: Dict) -> None:
    """Add PDF export UI elements to Streamlit"""
    st.markdown("### 📑 PDF Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        style_preset = st.selectbox(
            "PDF Style",
            ["academic", "modern", "minimal", "colorful"],
            index=0,
            help="Select the visual style for your PDF export"
        )
    
    with col2:
        include_details = st.checkbox(
            "Include Detailed Analysis",
            value=True,
            help="Include section-by-section analysis in the PDF"
        )
    
    if st.button("🔄 Generate PDF Report", type="primary"):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_integration = PDFIntegration()
                pdf_bytes = pdf_integration.create_single_paper_pdf(
                    paper_data,
                    style_preset=style_preset
                )
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = re.sub(r'[^\w\-_\.]', '_', paper_data['title'])
                filename = f"{safe_title}_{timestamp}.pdf"

                
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )
                st.success("✅ PDF report generated successfully!")
            
            except Exception as e:
                st.error(f"Failed to generate PDF: {str(e)}")

def comparison_pdf_export_ui(papers_data: List[Dict], comparison_data: Dict) -> None:
    """Add comparison PDF export UI elements to Streamlit"""
    st.markdown("### 📊 Comparison Report Export")
    
    style_preset = st.selectbox(
        "Report Style",
        ["modern", "academic"],
        index=0,
        help="Select the style for your comparison report"
    )
    
    if st.button("🔄 Generate Comparison Report", type="primary"):
        with st.spinner("Generating comparison report..."):
            try:
                pdf_integration = PDFIntegration()
                pdf_bytes = pdf_integration.create_comparison_pdf(
                    papers_data,
                    comparison_data,
                    style_preset=style_preset
                )
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📥 Download Comparison Report",
                    data=pdf_bytes,
                    file_name=f"research_papers_comparison_{timestamp}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Comparison report generated successfully!")
            
            except Exception as e:
                st.error(f"Failed to generate comparison report: {str(e)}")
