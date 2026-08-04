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


def generate_svg_footprint(meter_coords):
    """
    Generates an inline SVG polygon string from meter_coords.
    Uses blue color scheme (#1e3a8a stroke, #3b82f6 fill) matching generate_footprint_diagram.
    """
    if not meter_coords:
        return '<svg viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg"></svg>'

    xs = [c[0] for c in meter_coords]
    ys = [c[1] for c in meter_coords]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    w = max_x - min_x
    h = max_y - min_y
    if w == 0:
        w = 1.0
    if h == 0:
        h = 1.0

    margin = max(w, h) * 0.1
    vb_min_x = min_x - margin
    vb_min_y = min_y - margin
    vb_w = w + 2 * margin
    vb_h = h + 2 * margin

    points_str = " ".join(
        f"{x:.2f},{(max_y + min_y - y):.2f}" for x, y in meter_coords
    )

    stroke_width = max(w, h) * 0.01

    svg = (
        f'<svg viewBox="{vb_min_x:.2f} {vb_min_y:.2f} {vb_w:.2f} {vb_h:.2f}" '
        f'xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: auto; max-height: 400px;">\n'
        f'  <polygon points="{points_str}" fill="#3b82f6" fill-opacity="0.35" '
        f'stroke="#1e3a8a" stroke-width="{stroke_width:.2f}" stroke-linejoin="round" />\n'
        f'</svg>'
    )
    return svg


def generate_html_report(report_data, output_html_path):
    """
    Generates a single self-contained HTML report (inline CSS and SVG, no external network calls).
    """
    os.makedirs(os.path.dirname(output_html_path) if os.path.dirname(output_html_path) else '.', exist_ok=True)

    svg_code = generate_svg_footprint(report_data.get("meter_coords", []))

    address = report_data.get("address", "N/A")
    raw_area = report_data.get("raw_area", 0.0)
    usable_area = report_data.get("usable_area", 0.0)
    setback_m = report_data.get("setback_m", 1.5)
    module_eff = report_data.get("module_efficiency", 0.20)
    dc_capacity_kw = report_data.get("dc_capacity_kw", 0.0)
    ac_capacity_kw = report_data.get("ac_capacity_kw", 0.0)
    azimuth_deg = report_data.get("azimuth_deg", 180.0)
    tilt_deg = report_data.get("tilt_deg", 15)
    annual_kwh = report_data.get("annual_kwh", 0.0)
    rate_aed = report_data.get("rate_aed", 0.38)
    payback_years = report_data.get("payback_years", 0.0)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolarScan Feasibility Report - {address}</title>
    <style>
        :root {{
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent: #1e3a8a;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text-primary);
            margin: 0;
            padding: 2rem 1rem;
            display: flex;
            justify-content: center;
        }}
        .container {{
            max-width: 800px;
            width: 100%;
            background: var(--card-bg);
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
            padding: 2rem;
            border: 1px solid var(--border);
        }}
        h1 {{
            color: var(--text-primary);
            font-size: 1.5rem;
            text-align: center;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }}
        .address-box {{
            background: #f1f5f9;
            padding: 0.75rem 1rem;
            border-radius: 6px;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }}
        .diagram-container {{
            background: #f8fafc;
            border: 1px dashed var(--border);
            border-radius: 8px;
            padding: 1rem;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 2rem;
        }}
        h2 {{
            color: var(--accent);
            font-size: 1.2rem;
            margin-top: 0;
            margin-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 0.5rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0.5rem;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background-color: var(--text-primary);
            color: #ffffff;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SolarScan Rooftop Solar Feasibility Report</h1>
        <div class="address-box">
            Address: {address}
        </div>
        <div class="diagram-container">
            {svg_code}
        </div>
        <h2>System Sizing & Yield Analysis</h2>
        <table>
            <thead>
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Raw Roof Footprint Area</td>
                    <td>{raw_area:,.2f} m²</td>
                </tr>
                <tr>
                    <td>Usable Roof Area (after Setback)</td>
                    <td>{usable_area:,.2f} m²</td>
                </tr>
                <tr>
                    <td>Fire-Code Setback Distance</td>
                    <td>{setback_m:.2f} m</td>
                </tr>
                <tr>
                    <td>Module Efficiency</td>
                    <td>{module_eff*100:.1f}%</td>
                </tr>
                <tr>
                    <td>Recommended DC Capacity</td>
                    <td>{dc_capacity_kw:,.2f} kW DC</td>
                </tr>
                <tr>
                    <td>Recommended Inverter Band (AC)</td>
                    <td>{ac_capacity_kw:,.2f} kW AC</td>
                </tr>
                <tr>
                    <td>Dominant Roof Azimuth</td>
                    <td>{azimuth_deg:.1f}°</td>
                </tr>
                <tr>
                    <td>Assumed Panel Tilt</td>
                    <td>{tilt_deg}°</td>
                </tr>
                <tr>
                    <td>Estimated Annual Energy Yield</td>
                    <td>{annual_kwh:,.2f} kWh/yr</td>
                </tr>
                <tr>
                    <td>Utility Rate</td>
                    <td>{rate_aed:.2f} AED/kWh</td>
                </tr>
                <tr>
                    <td>Estimated Simple Payback</td>
                    <td>{payback_years:.2f} years</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

