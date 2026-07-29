import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_footprint_diagram(meter_coords, output_png_path):
    """
    Generates a matplotlib plot of the building footprint polygon and saves it to PNG.
    """
    if not meter_coords:
        return
    
    x = [c[0] for c in meter_coords] + [meter_coords[0][0]]
    y = [c[1] for c in meter_coords] + [meter_coords[0][1]]
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.plot(x, y, color='#1e3a8a', linewidth=2, label='OSM Building Footprint')
    ax.fill(x, y, color='#3b82f6', alpha=0.3)
    ax.set_title("Building Footprint & Roof Orientation", fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    ax.set_aspect('equal', 'box')
    
    plt.tight_layout()
    plt.savefig(output_png_path, format='png')
    plt.close(fig)


def generate_pdf_report(report_data, output_pdf_path):
    """
    Generates a client-ready PDF report containing footprint diagram, system specs,
    annual kWh yield, and payback estimate.
    """
    os.makedirs(os.path.dirname(output_pdf_path) if os.path.dirname(output_pdf_path) else '.', exist_ok=True)
    
    diagram_png = output_pdf_path.replace('.pdf', '_diagram.png')
    generate_footprint_diagram(report_data.get("meter_coords", []), diagram_png)
    
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=8
    )

    story = []
    
    # Header
    story.append(Paragraph("☀️ SolarScan Rooftop Solar Feasibility Report", title_style))
    story.append(Spacer(1, 10))
    
    # Address & System Summary
    address = report_data.get("address", "N/A")
    story.append(Paragraph(f"<b>Address:</b> {address}", styles['Normal']))
    story.append(Spacer(1, 10))
    
    # Footprint Image
    if os.path.exists(diagram_png):
        story.append(Image(diagram_png, width=400, height=250))
        story.append(Spacer(1, 15))
        
    # Sizing & Financial Summary Table
    story.append(Paragraph("System Sizing & Yield Analysis", h2_style))
    
    table_data = [
        ["Parameter", "Value"],
        ["Raw Roof Footprint Area", f"{report_data.get('raw_area', 0):.2f} m²"],
        ["Usable Roof Area (after Setback)", f"{report_data.get('usable_area', 0):.2f} m²"],
        ["Fire-Code Setback Distance", f"{report_data.get('setback_m', 1.5):.2f} m"],
        ["Module Efficiency", f"{report_data.get('module_efficiency', 0.20)*100:.1f}%"],
        ["Recommended DC Capacity", f"{report_data.get('dc_capacity_kw', 0):.2f} kW DC"],
        ["Recommended Inverter Band (AC)", f"{report_data.get('ac_capacity_kw', 0):.2f} kW AC"],
        ["Dominant Roof Azimuth", f"{report_data.get('azimuth_deg', 180):.1f}°"],
        ["Assumed Panel Tilt", f"{report_data.get('tilt_deg', 15)}°"],
        ["Estimated Annual Energy Yield", f"{report_data.get('annual_kwh', 0):,.2f} kWh/yr"],
        ["Utility Rate", f"{report_data.get('rate_aed', 0.38):.2f} / kWh"],
        ["Estimated Simple Payback", f"{report_data.get('payback_years', 0):.2f} years"],
    ]
    
    t = Table(table_data, colWidths=[240, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    
    story.append(t)
    doc.build(story)
    
    # Clean up temporary diagram image
    if os.path.exists(diagram_png):
        try:
            os.remove(diagram_png)
        except Exception:
            pass
