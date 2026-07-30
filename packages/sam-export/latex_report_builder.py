"""
LaTeX Engineering Report Generator
Populates engineering report LaTeX templates with calculated feasibility & SAM output data.
"""

def build_latex_report(project_name: str, dc_capacity_kw: float, annual_kwh: float) -> str:
    """
    Renders a formatted LaTeX report string for the PV project.
    """
    latex_code = rf"""\documentclass{{article}}
\title{{{project_name} Solar PV Engineering Feasibility Report}}
\author{{SolarScan Automated Design Engine}}
\date{{\today}}
\begin{document}
\maketitle

\section{{Executive Summary}}
The proposed solar photovoltaic system has a target capacity of \textbf{{{dc_capacity_kw:.2f} kWp}}.
Estimated annual energy yield is \textbf{{{annual_kwh:,.0f} kWh/year}}.

\section{{System Sizing Parameters}}
\begin{itemize}
    \item System Capacity: {dc_capacity_kw:.2f} kWp
    \item Expected Energy Yield: {annual_kwh:,.0f} kWh
\end{itemize}

\end{document}
"""
    return latex_code
