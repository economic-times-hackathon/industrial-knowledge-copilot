"""
Synthetic Centrifugal Pump O&M Manuals — 2 documents
1. Flowserve ANSI Process Pump Model 3910 IOM Manual
2. Goulds Water Technology 3196 STX ANSI Process Pump IOM Manual
Structured to mimic real OEM manuals (Emerson/Atlas Copco style).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os

OUT = r"C:\Users\hp859\Desktop\economic_times_hack\corpus\oem_manuals"
os.makedirs(OUT, exist_ok=True)

styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kwargs):
    s = ParagraphStyle(name, parent=styles[parent], **kwargs)
    return s

H1   = make_style("H1",   "Heading1", fontSize=16, textColor=HexColor("#003366"), spaceAfter=6)
H2   = make_style("H2",   "Heading2", fontSize=13, textColor=HexColor("#003366"), spaceAfter=4)
H3   = make_style("H3",   "Heading3", fontSize=11, textColor=HexColor("#005588"), spaceAfter=3)
BODY = make_style("BODY", "Normal",   fontSize=9,  leading=14, spaceAfter=4, alignment=TA_JUSTIFY)
NOTE = make_style("NOTE", "Normal",   fontSize=8,  leading=12, textColor=HexColor("#555555"), spaceAfter=4, leftIndent=10)
WARN = make_style("WARN", "Normal",   fontSize=9,  leading=13, textColor=HexColor("#8b0000"), spaceAfter=6, leftIndent=10, borderPad=4)
CODE = make_style("CODE", "Normal",   fontSize=8,  fontName="Courier", leading=11, spaceAfter=4, leftIndent=12)
CENT = make_style("CENT", "Normal",   fontSize=9,  alignment=TA_CENTER, spaceAfter=4)
TITL = make_style("TITL", "Normal",   fontSize=22, textColor=HexColor("#003366"), alignment=TA_CENTER, spaceAfter=8, fontName="Helvetica-Bold")
SUBT = make_style("SUBT", "Normal",   fontSize=13, textColor=HexColor("#005588"), alignment=TA_CENTER, spaceAfter=6)
DISC = make_style("DISC", "Normal",   fontSize=7,  textColor=HexColor("#888888"), alignment=TA_CENTER, spaceAfter=4)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=HexColor("#003366"), spaceAfter=6)
def sp(h=6): return Spacer(1, h)
def p(text, style=BODY): return Paragraph(text, style)
def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)

def tbl(data, col_widths=None, header_bg=HexColor("#003366"), header_fg=colors.white):
    t = Table(data, colWidths=col_widths)
    style = TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  header_bg),
        ("TEXTCOLOR",   (0,0), (-1,0),  header_fg),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("ALIGN",       (0,0), (-1,-1), "LEFT"),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, HexColor("#f0f4f8")]),
        ("GRID",        (0,0), (-1,-1), 0.4, HexColor("#aaaaaa")),
        ("TOPPADDING",  (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
    ])
    t.setStyle(style)
    return t

# ═══════════════════════════════════════════════════════════════════════════
# MANUAL 1 — Flowserve ANSI Process Pump Model 3910
# ═══════════════════════════════════════════════════════════════════════════
def build_flowserve_manual():
    path = os.path.join(OUT, "Flowserve_3910_ANSI_CentrifugalPump_IOM.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=20*mm, rightMargin=20*mm,
                             topMargin=20*mm,  bottomMargin=20*mm)
    story = []

    # ── Cover ──────────────────────────────────────────────────────────────
    story += [sp(30),
              p("FLOWSERVE CORPORATION", TITL),
              p("Installation, Operation & Maintenance Manual", SUBT),
              hr(),
              p("Mark 3™ ANSI Process Pump  |  Model 3910 Series", make_style("M",parent="Normal",fontSize=15,alignment=TA_CENTER,spaceAfter=6,fontName="Helvetica-Bold",textColor=HexColor("#005588"))),
              sp(8),
              tbl([["Parameter","Value"],
                   ["Document Number","FLS-IOM-3910-EN-Rev05"],
                   ["Pump Family","Mark 3 ANSI B73.1 Process Pump"],
                   ["Applicable Models","3910-1×1.5-6, 3910-1.5×3-8, 3910-2×3-10, 3910-3×4-13"],
                   ["Design Standard","ANSI/HI 1.3, ASME B73.1"],
                   ["Max Operating Pressure","275 psig (19 barg)"],
                   ["Temperature Range","-40°F to 500°F  (-40°C to 260°C)"],
                   ["Revision","Rev 05 — March 2023"],
                   ["Language","English"],
                  ], col_widths=[80*mm, 90*mm]),
              sp(10),
              p("⚠  WARNING — Read this manual completely before installing or operating the pump. Failure to follow instructions may result in personal injury, equipment damage, or process upset.", WARN),
              sp(8),
              p("SYNTHETIC DOCUMENT — Generated for hackathon demonstration purposes. Not a real Flowserve publication. Equipment tags, specifications, and procedures are representative only.", DISC),
              PageBreak()]

    # ── TOC ────────────────────────────────────────────────────────────────
    story += [h1("Table of Contents"), hr(),
              tbl([["Section","Title","Page"],
                   ["1","Safety Precautions","3"],
                   ["2","Product Description & Nomenclature","4"],
                   ["3","Specifications & Performance Data","5"],
                   ["4","Installation","6"],
                   ["5","Commissioning & Start-Up","8"],
                   ["6","Operation","9"],
                   ["7","Maintenance","10"],
                   ["8","Troubleshooting","13"],
                   ["9","Parts List & Ordering","14"],
                   ["10","Appendices","15"],
                  ], col_widths=[20*mm, 120*mm, 20*mm]),
              PageBreak()]

    # ── Section 1: Safety ──────────────────────────────────────────────────
    story += [h1("1. Safety Precautions"), hr(),
              h2("1.1 Signal Words"),
              tbl([["Signal Word","Meaning"],
                   ["⛔ DANGER","Imminent hazard — will cause death or serious injury if not avoided"],
                   ["⚠ WARNING","Potential hazard — could cause death or serious injury"],
                   ["⚡ CAUTION","Potential hazard — could cause minor injury or equipment damage"],
                   ["📋 NOTE","Important information, not hazard-related"],
                  ], col_widths=[40*mm, 130*mm]),
              sp(4),
              h2("1.2 General Safety"),
              p("Before performing any work on the pump: <b>isolate the pump from all energy sources</b> (electrical, hydraulic, pneumatic). Apply lockout/tagout (LOTO) per OSHA 29 CFR 1910.147. Ensure the pump is fully depressurised and drained. Allow sufficient cool-down time for hot fluid services."),
              p("Personal Protective Equipment (PPE) requirements: safety glasses, chemical-resistant gloves, steel-toed footwear, and hearing protection when operating near running equipment."),
              h2("1.3 Hazardous Fluids"),
              p("When pumping flammable, toxic, or corrosive fluids, additional precautions apply. Consult the relevant Material Safety Data Sheet (MSDS/SDS). Ensure adequate ventilation. Provide appropriate emergency eyewash and shower facilities within 10 seconds of travel."),
              h2("1.4 Rotating Equipment"),
              p("Never operate the pump with guards removed. Keep hands, tools, and loose clothing away from rotating shafts and couplings. The pump may restart automatically if equipped with an automatic start system — confirm the system is in manual/off mode before working on the pump."),
              PageBreak()]

    # ── Section 2: Product Description ─────────────────────────────────────
    story += [h1("2. Product Description & Nomenclature"), hr(),
              h2("2.1 Design Overview"),
              p("The Mark 3 Model 3910 is a single-stage, end-suction, back-pullout centrifugal process pump conforming to ANSI/ASME B73.1 dimensional standards. The back-pullout design allows the rotating element (impeller, shaft, bearings, and seal) to be withdrawn without disturbing the pump casing or process piping."),
              p("Key design features include: heavy-duty, back-pullout construction; single-piece power frame for rigidity; replaceable wear rings; large-diameter shaft for minimum deflection; and a seal chamber designed for all mechanical seal types and packing."),
              h2("2.2 Model Nomenclature"),
              p("Model number format: <b>3910 — [suction size] × [discharge size] — [max impeller diameter, inches]</b>"),
              tbl([["Model","Suction (in)","Discharge (in)","Max Imp. Dia (in)","Flow Range (GPM)","Head Range (ft)"],
                   ["3910-1×1.5-6","1.0","1.5","6","10-120","10-160"],
                   ["3910-1.5×3-8","1.5","3.0","8","30-400","20-250"],
                   ["3910-2×3-10","2.0","3.0","10","60-700","30-350"],
                   ["3910-3×4-13","3.0","4.0","13","150-1500","40-460"],
                  ], col_widths=[35*mm, 20*mm, 22*mm, 25*mm, 28*mm, 28*mm]),
              h2("2.3 Major Components"),
              tbl([["Item No.","Component","Material (Standard)","Notes"],
                   ["100","Casing","ASTM A48 Class 40 Cast Iron","CS or SS optional"],
                   ["101","Impeller","ASTM A48 Class 40 Cast Iron","Trimmed to duty"],
                   ["105","Wear Ring — Casing","Cast Iron","Replaceable"],
                   ["106","Wear Ring — Impeller","Cast Iron","Replaceable"],
                   ["122","Shaft","AISI 4140 Alloy Steel","17-4 PH optional"],
                   ["126","Bearing — Radial","Conrad deep groove ball","SKF 6309"],
                   ["127","Bearing — Thrust","Angular contact pair","SKF 7309"],
                   ["136","Mechanical Seal","John Crane Type 21","Single unbalanced"],
                   ["184","Backplate / Stuffing Box","Cast Iron","Seal chamber ASME B73.1"],
                   ["228","Coupling","Rexnord Omega Flexible","Grid type, elastomeric"],
                  ], col_widths=[18*mm, 42*mm, 45*mm, 50*mm]),
              PageBreak()]

    # ── Section 3: Specifications ───────────────────────────────────────────
    story += [h1("3. Specifications & Performance Data"), hr(),
              h2("3.1 Design Limits"),
              tbl([["Parameter","Imperial","Metric"],
                   ["Max Working Pressure","275 psig","19.0 barg"],
                   ["Hydrotest Pressure","413 psig","28.5 barg"],
                   ["Max Operating Temperature","500°F","260°C"],
                   ["Min Operating Temperature","-40°F","-40°C"],
                   ["Max Casing Nozzle Load (Suction)","Per HI 1.3.4.1","Per HI 1.3.4.1"],
                   ["Bearing L10 Life (design)","25,000 hours","—"],
                   ["Seal Flush — Std","Plan 11 (discharge recirculation)","—"],
                  ], col_widths=[65*mm, 45*mm, 45*mm]),
              h2("3.2 Lubrication Data"),
              tbl([["Location","Lubricant Type","Grade","Quantity","Interval"],
                   ["Radial bearing","Mineral oil","ISO VG 68","Fill to centre of sight glass","6 months or 2000 h"],
                   ["Thrust bearing","Mineral oil","ISO VG 68","Fill to centre of sight glass","6 months or 2000 h"],
                   ["Coupling (grid)","Coupling grease","Shell Alvania EP2","Per coupling mfr. data","12 months"],
                  ], col_widths=[32*mm, 30*mm, 22*mm, 42*mm, 33*mm]),
              h2("3.3 Allowable Operating Region"),
              p("The pump must be operated within the Allowable Operating Region (AOR): <b>0.6 × Q_BEP to 1.2 × Q_BEP</b> for continuous duty. Operating below minimum continuous stable flow (MCSF) generates recirculation, cavitation, and premature seal and bearing wear."),
              p("Preferred Operating Region (POR) for maximum reliability: <b>0.8 × Q_BEP to 1.1 × Q_BEP</b>."),
              PageBreak()]

    # ── Section 4: Installation ─────────────────────────────────────────────
    story += [h1("4. Installation"), hr(),
              h2("4.1 Receiving & Storage"),
              p("Inspect the pump on receipt. Verify all items against the packing list. Report visible shipping damage to the carrier within 48 hours. If the pump is to be stored for more than 6 weeks before installation: remove the coupling half; coat exposed machined surfaces with rust-preventive oil; rotate the shaft quarterly; and drain and dry all water-wetted components."),
              h2("4.2 Foundation & Baseplate"),
              p("The pump shall be mounted on a rigid, level concrete foundation. Minimum foundation mass: <b>5× the combined pump-motor weight</b>. Baseplate grouting: non-shrink epoxy grout (e.g., Chockfast Orange) to a minimum depth of 25 mm. Allow full cure before final alignment."),
              h2("4.3 Piping Connections"),
              p("SUCTION PIPING: Keep suction pipe as short as possible with minimum elbows. Suction pipe diameter shall be one size larger than the pump suction nozzle. Install an eccentric reducer (flat side up) immediately upstream of the suction nozzle to prevent air pockets. Minimum straight run upstream: <b>5 × pipe diameters</b>."),
              p("DISCHARGE PIPING: Install a non-slam check valve and a gate/butterfly isolation valve on the discharge. Discharge pipe shall be supported independently — do not allow piping weight to bear on pump nozzles."),
              h2("4.4 Alignment Procedure"),
              tbl([["Step","Procedure","Tolerance"],
                   ["1","Rough align pump to motor using straightedge across coupling halves","Within 3 mm"],
                   ["2","Attach dial indicators to coupling — check angular misalignment","<0.05 mm/100 mm"],
                   ["3","Check parallel (offset) misalignment at 0°, 90°, 180°, 270°","<0.05 mm TIR"],
                   ["4","Adjust shims under motor feet to achieve tolerances","—"],
                   ["5","Re-check after grouting and after connecting piping","Same tolerances"],
                   ["6","Re-check alignment after first thermal soak at operating temp","<0.10 mm TIR hot"],
                  ], col_widths=[12*mm, 110*mm, 38*mm]),
              PageBreak()]

    # ── Section 5: Commissioning ────────────────────────────────────────────
    story += [h1("5. Commissioning & Start-Up"), hr(),
              h2("5.1 Pre-Start Checks"),
              p("Complete the following before initial start-up or after extended shutdown:"),
              tbl([["#","Check Item","Action if Not Met"],
                   ["1","Pump rotates freely by hand","Investigate — check for mechanical contact, seized bearing"],
                   ["2","Bearing housing oil level at centre of sight glass","Top up with correct grade lubricant"],
                   ["3","Mechanical seal flush line (Plan 11) open and clear","Open valve, flush with clean fluid"],
                   ["4","Coupling guard installed and secured","Install before energising motor"],
                   ["5","Motor rotation correct (momentary jog test)","Swap two motor supply phases"],
                   ["6","Suction valve fully open","Open fully before start"],
                   ["7","Pump and suction line fully primed (no air)","Re-prime using vent connections"],
                   ["8","Discharge valve closed (for initial start)","Close before starting"],
                   ["9","Cooling water to seal/bearing housing (if equipped)","Open cooling water supply"],
                  ], col_widths=[8*mm, 90*mm, 60*mm]),
              h2("5.2 Start-Up Sequence"),
              p("1. Confirm all pre-start checks complete.  2. Start the motor.  3. When pump reaches full speed, <b>slowly open the discharge valve</b> to the duty flow point (do not operate against closed discharge for more than 30 seconds — overheating will occur).  4. Monitor discharge pressure, flow, and bearing temperature for the first 30 minutes.  5. Check for vibration or unusual noise."),
              PageBreak()]

    # ── Section 6: Operation ────────────────────────────────────────────────
    story += [h1("6. Operation"), hr(),
              h2("6.1 Normal Operating Parameters"),
              tbl([["Parameter","Normal Range","Alarm","Trip"],
                   ["Discharge pressure","Per duty curve ±10%","±15% of design","—"],
                   ["Flow rate","Q_BEP × 0.8-1.1","<Q_MCSF","—"],
                   ["Bearing temp (DE radial)","Amb +25°C","Amb +40°C or 80°C","90°C"],
                   ["Bearing temp (NDE thrust)","Amb +25°C","Amb +40°C or 80°C","90°C"],
                   ["Vibration (velocity RMS)","<2.8 mm/s","4.5 mm/s","7.1 mm/s"],
                   ["Seal leakage (mech seal)","Vapour only — no visible drops","Visible drips","Stream"],
                  ], col_widths=[50*mm, 40*mm, 35*mm, 30*mm]),
              h2("6.2 Shutdown"),
              p("Planned shutdown: slowly close discharge valve → stop motor → close suction valve (for long-term shutdown) → depressurise and drain if maintenance required. For standby pumps, stroke the suction/discharge valves weekly and jog the motor monthly to prevent seizure."),
              PageBreak()]

    # ── Section 7: Maintenance ──────────────────────────────────────────────
    story += [h1("7. Maintenance"), hr(),
              h2("7.1 Preventive Maintenance Schedule"),
              tbl([["Frequency","Task","Reference"],
                   ["Daily","Check bearing temperature and vibration (running units)","Sec 6.1"],
                   ["Daily","Check seal leakage — zero visible liquid drops acceptable","Sec 6.1"],
                   ["Weekly","Check oil level in bearing housing","Sec 7.2"],
                   ["Monthly","Grease coupling (grid type — 1 grease gun shot per fitting)","Sec 7.3"],
                   ["3 Months","Check alignment (thermal cycles loosen shims)","Sec 4.4"],
                   ["6 Months","Change bearing housing oil — or at 2000 running hours","Sec 7.2"],
                   ["12 Months","Full mechanical inspection: impeller clearance, wear rings, seal","Sec 7.4"],
                   ["3 Years","Overhaul: replace bearings, mechanical seal, wear rings","Sec 7.5"],
                   ["As required","Replace mechanical seal on confirmed failure","Sec 7.6"],
                  ], col_widths=[28*mm, 100*mm, 25*mm]),
              h2("7.2 Bearing Lubrication"),
              p("Oil-lubricated bearing frame: use ISO VG 68 premium mineral oil (or equivalent synthetic). Check oil level weekly with pump stopped. Oil should sit at the centre of the sight glass. Drain, flush, and refill every 6 months or 2000 hours, whichever comes first. Use a clean, dry funnel — moisture contamination is the leading cause of premature bearing failure."),
              p("Oil analysis programme: sample bearing oil every 3 months. Condemn oil if: viscosity deviation >15% from new oil, water content >0.1%, Fe particle count >50 ppm (indicating wear)."),
              h2("7.3 Mechanical Seal Inspection"),
              p("John Crane Type 21 — single unbalanced, inside mounted. Flush: API Plan 11 (discharge recirculation). Normal leakage: vapour or occasional droplets only. Replace seal immediately if: continuous liquid dripping is observed; seal face temperature exceeds 120°C; seal spring is damaged or corroded; or rotating face shows circumferential scoring."),
              p("Seal replacement requires removal of the rotating element. Refer to separate Seal Installation Drawing SID-3910-21."),
              h2("7.4 Impeller Clearance Check"),
              tbl([["Pump Size","Nominal Clearance (new)","Max Allowable Clearance","Adjustment Method"],
                   ["3910-1×1.5-6","0.35 mm","0.75 mm","Axial adjustment via shims at backplate"],
                   ["3910-1.5×3-8","0.40 mm","0.80 mm","Axial adjustment via shims at backplate"],
                   ["3910-2×3-10","0.45 mm","0.90 mm","Axial adjustment via shims at backplate"],
                   ["3910-3×4-13","0.50 mm","1.00 mm","Axial adjustment via shims at backplate"],
                  ], col_widths=[38*mm, 42*mm, 42*mm, 55*mm]),
              p("Check clearance annually. Excessive clearance reduces pump efficiency and increases NPSH required. Replace wear rings when clearance exceeds maximum allowable."),
              PageBreak()]

    # ── Section 8: Troubleshooting ──────────────────────────────────────────
    story += [h1("8. Troubleshooting"), hr(),
              tbl([["Symptom","Probable Cause","Corrective Action"],
                   ["Pump fails to deliver flow","Air lock in suction\nInsufficient NPSH\nWrong rotation","Re-prime pump\nCheck NPSHA vs NPSHR\nSwap 2 motor phases"],
                   ["Low flow / low head","Impeller worn or damaged\nWear rings worn\nPartly closed suction valve\nImpeller diameter too small","Inspect and replace impeller\nCheck/replace wear rings\nOpen suction valve fully\nVerify impeller trim vs curve"],
                   ["Excessive vibration","Misalignment\nCavitation\nImbalanced impeller\nBent shaft\nLoose foundation bolts","Re-align to tolerance\nCheck NPSHA, throttle flow\nBalance or replace impeller\nReplace shaft\nTorque foundation bolts"],
                   ["Bearing overheating","Over/under lubrication\nContaminated oil\nBearing failure\nPipe strain on casing","Correct oil level\nDrain and refill oil\nReplace bearing\nCheck nozzle loads"],
                   ["Mechanical seal leaking","Seal face worn\nSeal spring broken\nWrong flush pressure\nProcess fluid crystallising","Replace seal faces or seal\nReplace spring\nAdjust Plan 11 flow\nIncrease flush flow / change plan"],
                   ["Excessive power draw","Liquid SG higher than design\nOperating far right of curve\nMechanical friction","Re-evaluate motor sizing\nThrottle or trim impeller\nCheck bearing/seal drag"],
                  ], col_widths=[42*mm, 60*mm, 60*mm]),
              PageBreak()]

    # ── Section 9: Parts List ───────────────────────────────────────────────
    story += [h1("9. Spare Parts & Ordering"), hr(),
              h2("9.1 Recommended Commissioning Spares"),
              tbl([["Item","Part No.","Description","Qty","Notes"],
                   ["Mechanical Seal","3910-MS-21-1.5","John Crane Type 21, 1.5\" shaft","1 set","Size per pump order"],
                   ["Bearing — Radial","3910-BRG-6309","SKF 6309 deep groove ball bearing","1","Standard for 1.5–2\" shaft"],
                   ["Bearing — Thrust","3910-BRG-7309","SKF 7309 angular contact pair","1 pair","Matched, DB arrangement"],
                   ["Wear Ring Set","3910-WR-SET","Casing + impeller wear rings","1 set","Per pump model"],
                   ["Gasket Set","3910-GSK-SET","Full pump gasket set (casing, backplate)","2 sets",""],
                   ["Oil Seal","3910-OS-SET","Bearing housing lip seals","2","Inboard and outboard"],
                  ], col_widths=[35*mm, 30*mm, 65*mm, 12*mm, 30*mm]),
              h2("9.2 Two-Year Operating Spares (per HI 1.3.3)"),
              p("For critical service pumps (>8760 h/year): maintain one complete rotating element (impeller + shaft + bearings + seal) as an assembled unit ready for exchange. This minimises MTTR from days to hours."),
              PageBreak()]

    # ── Appendix ────────────────────────────────────────────────────────────
    story += [h1("Appendix A — Torque Values"), hr(),
              tbl([["Fastener Location","Bolt Size","Torque (Nm)","Torque (ft·lb)"],
                   ["Casing split flange bolts","M16 / ⅝\"","110","81"],
                   ["Backplate to casing bolts","M12 / ½\"","55","41"],
                   ["Impeller lock nut","M20 LH thread","135","100"],
                   ["Bearing housing end cap","M10","28","21"],
                   ["Foundation anchor bolts","M24","250","184"],
                   ["Coupling hub to shaft","Per coupling mfr.","—","—"],
                  ], col_widths=[65*mm, 30*mm, 30*mm, 30*mm]),
              sp(6),
              h1("Appendix B — Seal Flush Plans Reference"), hr(),
              tbl([["API Plan","Description","Typical Application"],
                   ["Plan 11","Recirculation from pump discharge to seal chamber","Clean, non-polymerising fluids >15°C above ambient"],
                   ["Plan 13","Recirculation from seal chamber to pump suction","Fluids where discharge pressure needed for cooling"],
                   ["Plan 21","Discharge recirculation via cooler","Hot fluid services above 80°C"],
                   ["Plan 23","Seal chamber circulation with integral heat exchanger","High temperature services (>120°C)"],
                   ["Plan 32","External clean flush injection","Dirty or abrasive process fluids"],
                   ["Plan 52","Unpressurised buffer fluid reservoir","Toxic/hazardous fluid double seal"],
                   ["Plan 53A","Pressurised barrier fluid reservoir","Toxic/hazardous fluid double seal, API 682 Cat 3"],
                  ], col_widths=[22*mm, 90*mm, 55*mm]),
              sp(12),
              p("END OF DOCUMENT — Flowserve 3910 Mark 3 ANSI Pump IOM  |  Doc: FLS-IOM-3910-EN-Rev05  |  SYNTHETIC — For demonstration only.", DISC)]

    doc.build(story)
    print("  Generated: Flowserve_3910_ANSI_CentrifugalPump_IOM.pdf")

build_flowserve_manual()

# ═══════════════════════════════════════════════════════════════════════════
# MANUAL 2 — Goulds 3196 STX ANSI Process Pump
# ═══════════════════════════════════════════════════════════════════════════
def build_goulds_manual():
    path = os.path.join(OUT, "Goulds_3196STX_ANSI_CentrifugalPump_IOM.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=20*mm, rightMargin=20*mm,
                             topMargin=20*mm,  bottomMargin=20*mm)
    story = []

    GBLU = HexColor("#00447c")
    H1g  = make_style("H1g","Heading1",fontSize=15,textColor=GBLU,spaceAfter=5)
    H2g  = make_style("H2g","Heading2",fontSize=12,textColor=GBLU,spaceAfter=4)
    def h1g(t): return Paragraph(t, H1g)
    def h2g(t): return Paragraph(t, H2g)
    def tblg(data, cw=None): return tbl(data, col_widths=cw, header_bg=GBLU)

    # Cover
    story += [sp(30),
              p("GOULDS WATER TECHNOLOGY  |  A Xylem Brand", make_style("GT",parent="Normal",fontSize=20,alignment=TA_CENTER,spaceAfter=6,fontName="Helvetica-Bold",textColor=GBLU)),
              p("Installation, Operation & Maintenance Manual", SUBT),
              hr(),
              p("3196 STX — ANSI B73.1 Chemical Process Pump", make_style("GM",parent="Normal",fontSize=14,alignment=TA_CENTER,spaceAfter=8,fontName="Helvetica-Bold",textColor=HexColor("#005a9e"))),
              sp(8),
              tblg([["Parameter","Value"],
                    ["Document No.","GWT-IOM-3196-STX-EN-Rev04"],
                    ["Pump Family","3196 Series ANSI B73.1 Chemical Process Pump"],
                    ["Frame Sizes","STX (Small), MTX (Medium), LTX (Large)"],
                    ["This Manual Covers","3196 STX — shaft size 1.125\" (28.6 mm)"],
                    ["Max Working Pressure","285 psig (19.7 barg)"],
                    ["Temperature Range","-65°F to 550°F  (-54°C to 288°C)"],
                    ["Standards","ANSI/HI 1.3, ASME B73.1, API 610 (optional upgrade)"],
                    ["Revision","Rev 04 — November 2022"],
                   ], cw=[80*mm, 90*mm]),
              sp(10),
              p("⚠  WARNING — Hazardous voltage and rotating equipment. Always comply with applicable safety regulations and plant LOTO procedures before performing any work.", WARN),
              sp(6),
              p("SYNTHETIC DOCUMENT — Representative IOM generated for hackathon corpus. Not a genuine Goulds/Xylem publication.", DISC),
              PageBreak()]

    # TOC
    story += [h1g("Table of Contents"), hr(),
              tblg([["Sec","Title","Pg"],
                    ["1","Safety & Regulatory Compliance","3"],
                    ["2","Pump Description & Materials of Construction","4"],
                    ["3","Technical Specifications","5"],
                    ["4","Receiving, Storage & Handling","6"],
                    ["5","Installation — Mechanical","6"],
                    ["6","Installation — Piping & Connections","7"],
                    ["7","Electrical & Instrumentation Connections","8"],
                    ["8","Pre-Start & Commissioning","8"],
                    ["9","Normal Operation","9"],
                    ["10","Preventive Maintenance","10"],
                    ["11","Corrective Maintenance — Disassembly & Reassembly","11"],
                    ["12","Troubleshooting Guide","13"],
                    ["13","Spare Parts","14"],
                    ["App A","Dimensional Data & Nozzle Loads","15"],
                    ["App B","Typical Performance Curves","15"],
                   ], cw=[15*mm, 125*mm, 15*mm]),
              PageBreak()]

    # Section 1
    story += [h1g("1. Safety & Regulatory Compliance"), hr(),
              h2g("1.1 Applicable Regulations"),
              p("This equipment shall be installed and operated in compliance with all applicable national and local regulations including but not limited to: OSHA 29 CFR 1910 (General Industry Standards); NFPA 70 (National Electrical Code) for electrical connections; ASME B31.3 (Process Piping) for piping connections; and EPA 40 CFR Part 63 (NESHAP) for hazardous air pollutant emission controls where applicable."),
              h2g("1.2 Pressure Equipment Directive (India)"),
              p("For installations in India, this pump is subject to the Static and Mobile Pressure Vessels (Unfired) Rules, 2016 under PESO (Petroleum and Explosives Safety Organisation) where the pump handles fluids above 1 barg. Ensure certification documentation is filed with the local PESO Controller of Explosives prior to commissioning."),
              h2g("1.3 Chemical Handling"),
              p("When handling chemicals classified as Schedule 1 substances under the Manufacture, Storage and Import of Hazardous Chemicals Rules 1989 (India), a Major Accident Hazard (MAH) site assessment must be conducted. MSDS/SDS for all process fluids must be immediately accessible in the pump area."),
              PageBreak()]

    # Section 2
    story += [h1g("2. Pump Description & Materials of Construction"), hr(),
              h2g("2.1 Design Features"),
              p("The Goulds 3196 STX is a single-stage, end-suction, back-pullout centrifugal pump. Distinctive features include: <b>CorroPro™ fibre-reinforced polymer (FRP) impeller option</b> for highly corrosive services; heavy-duty one-piece power frame with patented i-FRAME® bearing housing; PowerEnd™ design for sub-30-minute seal replacement; and ANSI B73.1 dimensional interchangeability."),
              h2g("2.2 Materials of Construction"),
              tblg([["Component","Standard Material","Optional Materials"],
                    ["Casing","ASTM A48 Cl.30 Cast Iron","316 SS, Alloy 20, Hastelloy C"],
                    ["Impeller","ASTM A48 Cl.30 Cast Iron","316 SS, FRP, CD4MCu Duplex"],
                    ["Shaft","AISI 4140 Alloy Steel","316 SS, Titanium"],
                    ["Wear Ring — Casing","Cast Iron","316 SS, Bronze"],
                    ["Stuffing Box Cover","Cast Iron","316 SS"],
                    ["Shaft Sleeve","316 SS (std)","Hastelloy C, Ceramic"],
                    ["Frame Adapter","Ductile Iron","—"],
                    ["Bearing Frame","Cast Iron","—"],
                   ], cw=[45*mm, 55*mm, 60*mm]),
              PageBreak()]

    # Section 3
    story += [h1g("3. Technical Specifications"), hr(),
              h2g("3.1 Performance Envelope — 3196 STX"),
              tblg([["Parameter","Value"],
                    ["Flow Range","5 to 700 GPM  (1.1 to 159 m³/h)"],
                    ["Head Range","10 to 440 ft  (3 to 134 m)"],
                    ["Speed","1450 or 2900 RPM (50 Hz); 1750 or 3500 RPM (60 Hz)"],
                    ["Max Sphere Passage","0.25\" (6.4 mm) — open impeller option 0.5\""],
                    ["NPSHR (min)","2.5 ft (0.76 m) at Q_BEP — see performance curve"],
                    ["Efficiency (peak, typical)","72-78% depending on model & trim"],
                   ], cw=[70*mm, 100*mm]),
              h2g("3.2 Mechanical Seal Options"),
              tblg([["Seal Type","API Plan","Service","Notes"],
                    ["Single inside — John Crane 8B1","Plan 11","General chemical","Standard supply"],
                    ["Single inside — Flowserve RBSC","Plan 11 or 21","Hot/abrasive fluid","SiC/SiC faces"],
                    ["Double (tandem) — JC 5860","Plan 52","Toxic / hazardous","Requires seal pot"],
                    ["Double (pressurised) — JC 5610","Plan 53A","High-hazard toxic","API 682 Cat III"],
                    ["Packing — PTFE chevron","None","Low-pressure utility","10 rings, lantern ring"],
                   ], cw=[48*mm, 22*mm, 45*mm, 50*mm]),
              PageBreak()]

    # Sections 4-9 condensed
    story += [h1g("4–6. Receiving, Storage & Installation"), hr(),
              h2g("4.1 Receiving Inspection"),
              p("Check for transit damage. Verify nameplate data against purchase order. Retain all shipping documentation. Preserve protective coatings and pipe-end covers until installation."),
              h2g("5.1 Foundation Requirements"),
              p("Minimum foundation mass: 3× combined wet pump and motor weight. Epoxy grout baseplate — minimum 50 mm depth. Use precision laser alignment tool (preferred) or dial indicators. Alignment tolerance: angular <0.05 mm per 100 mm; parallel offset <0.05 mm TIR cold."),
              h2g("6.1 Piping — Critical Requirements"),
              p("SUCTION: Eccentric reducer flat-side-up within 2 pipe diameters of suction nozzle. No elbows within 5 pipe diameters. Suction pipe must be independently supported — zero load on pump nozzle. Install isolation valve and strainer (40 mesh temporary startup strainer)."),
              p("DISCHARGE: Gate or butterfly isolation valve then non-slam check valve. Discharge pipe support within 300 mm of pump discharge nozzle."),
              PageBreak()]

    story += [h1g("7–9. Electrical, Pre-Start & Commissioning"), hr(),
              h2g("7.1 Motor & Electrical"),
              p("Motor must be certified for the area classification of the installation (Zone 1 or 2 for hazardous areas per IS/IEC 60079). Verify motor supply voltage and frequency against nameplate. Connect per motor terminal diagram. Verify overload relay setting: 100–105% of motor FLA."),
              h2g("8.1 Pre-Start Checklist"),
              tblg([["#","Item","Accept Criteria"],
                    ["1","Pump rotates freely by hand","No binding — one full revolution"],
                    ["2","Bearing lubrication","Oil at midpoint of sight glass"],
                    ["3","Mechanical seal flush operative","Plan 11 valve open, flow observed"],
                    ["4","Rotation direction (jog test)","CW viewed from motor — anti-CW from pump end"],
                    ["5","Suction valve open, pump primed","No air vent — liquid at pump casing vent"],
                    ["6","Discharge valve closed","Fully closed for start"],
                    ["7","All coupling guards in place","Secure — no gaps"],
                    ["8","Instrument connections complete","All PT, TT, flow transmitters connected"],
                   ], cw=[8*mm, 80*mm, 65*mm]),
              h2g("9.1 Operating Envelope"),
              p("Operate within <b>0.7-1.2 × Q_BEP</b>. Minimum continuous flow (MCF): 0.25 × Q_BEP for standard impeller. Install minimum-flow bypass if process turns down below MCF. Monitor bearing temperature: normal <70°C; alarm 80°C; trip 90°C."),
              PageBreak()]

    story += [h1g("10. Preventive Maintenance Schedule"), hr(),
              tblg([["Frequency","Task","Acceptance Criteria"],
                    ["Daily","Bearing temp (running)","<70°C or <Amb+30°C"],
                    ["Daily","Vibration check (hand/instrument)","<4.5 mm/s RMS"],
                    ["Daily","Seal leakage visual","No visible liquid drips"],
                    ["Weekly","Oil level check","Midpoint sight glass"],
                    ["Monthly","Coupling inspection — grid type","No grid wear, correct grease"],
                    ["3 months","Shaft alignment re-check","<0.05 mm TIR"],
                    ["6 months","Oil change — bearing frame","ISO VG 68, clean container"],
                    ["6 months","Strainer screen clean (if fitted)","Pressure drop <0.2 bar across clean screen"],
                    ["Annual","Impeller clearance check","See Sec 3 — Table 3.1"],
                    ["Annual","Mechanical seal inspection","No face wear, spring intact"],
                    ["Annual","Full vibration spectrum analysis","No discrete frequency peaks >6 mm/s"],
                    ["3 years","Full overhaul — replace bearings, seal, wear rings","Per design clearances"],
                   ], cw=[28*mm, 95*mm, 48*mm]),
              PageBreak()]

    story += [h1g("11. Disassembly & Reassembly — Back-Pullout"), hr(),
              h2g("11.1 Back-Pullout Procedure"),
              p("The 3196 STX back-pullout design allows removal of the rotating element (impeller, shaft, seal, bearings) without disturbing the casing or process piping. Estimated time: 45–90 minutes with trained technician."),
              tblg([["Step","Action","Special Tools"],
                    ["1","Isolate pump, LOTO, depressurise, drain, allow to cool","Lockout device"],
                    ["2","Disconnect coupling spacer (do NOT move motor)","Coupling wrench"],
                    ["3","Remove coupling guard and coupling hub from pump shaft","Puller 3196-PULL-1"],
                    ["4","Disconnect mechanical seal flush pipework (Plan 11)","—"],
                    ["5","Remove 4 frame adapter-to-casing bolts","24 mm socket"],
                    ["6","Slide complete power end (frame + shaft + impeller) rearward","Slide plate 3196-SLD"],
                    ["7","Remove impeller lock nut (LH thread) and impeller","Spanner, impeller wrench"],
                    ["8","Remove seal from shaft — note spring hand orientation","—"],
                    ["9","Press bearings off shaft using hydraulic press","100 kN press, brass drift"],
                    ["10","Inspect all components — replace wear items per Sec 13","—"],
                    ["11","Reassemble in reverse order — note torques per App A","Torque wrench"],
                    ["12","Re-check alignment before restart","Dial indicators or laser"],
                   ], cw=[10*mm, 100*mm, 45*mm]),
              PageBreak()]

    story += [h1g("12. Troubleshooting"), hr(),
              tblg([["Problem","Likely Cause(s)","Action"],
                    ["No flow on start","Pump not primed; wrong rotation; blocked suction strainer","Prime pump; check rotation; clean strainer"],
                    ["Low flow/head","Worn impeller or wear rings; air entrainment; system resistance higher than design","Inspect internals; check for vortex at suction; verify system curve"],
                    ["Cavitation noise","NPSHA < NPSHR; suction valve not fully open; fluid near boiling point","Increase suction pressure; open valve; reduce fluid temperature"],
                    ["High bearing temp","Low or contaminated oil; overloaded bearing; coupling misalignment","Change oil; re-align; check axial thrust load"],
                    ["Vibration","Misalignment; cavitation; impeller imbalance; worn bearings; resonance","Align; check NPSHA; balance impeller; replace bearings; check base stiffness"],
                    ["Seal leaking","Worn faces; improper installation; flush failure; chemical attack","Replace seal; verify flush plan; review materials compatibility"],
                    ["Excessive power","SG higher than design; wrong impeller diameter; mechanical friction","Re-check duty; trim impeller; inspect bearings and seal"],
                   ], cw=[38*mm, 68*mm, 58*mm]),
              PageBreak()]

    story += [h1g("13. Spare Parts"), hr(),
              h2g("13.1 Recommended Spares — 3196 STX"),
              tblg([["Part","Part No. (STX)","Qty (Commissioning)","Qty (2-Year)"],
                    ["Mechanical seal complete","3196-STX-SEAL-8B1","1 set","2 sets"],
                    ["Radial bearing","3196-STX-BRG-RAD","1","2"],
                    ["Thrust bearing pair","3196-STX-BRG-THR","1 pair","2 pairs"],
                    ["Impeller wear ring","3196-STX-WR-IMP","1","2"],
                    ["Casing wear ring","3196-STX-WR-CAS","1","2"],
                    ["Shaft sleeve","3196-STX-SLEEVE","1","2"],
                    ["Full gasket set","3196-STX-GSK","2","4"],
                    ["Complete rotating element","3196-STX-ROTEL","0","1"],
                   ], cw=[60*mm, 38*mm, 30*mm, 30*mm]),
              sp(12),
              h1g("Appendix A — Maximum Allowable Nozzle Loads (ANSI B73.1)"), hr(),
              tblg([["Nozzle","Force Fx (N)","Force Fy (N)","Force Fz (N)","Moment Mx (Nm)","Moment My (Nm)","Moment Mz (Nm)"],
                    ["Suction (3\")","1780","890","1340","610","305","460"],
                    ["Discharge (2\")","1070","535","800","305","150","230"],
                   ], cw=[28*mm, 20*mm, 20*mm, 20*mm, 22*mm, 22*mm, 22*mm]),
              sp(12),
              p("END OF DOCUMENT — Goulds 3196 STX IOM  |  Doc: GWT-IOM-3196-STX-EN-Rev04  |  SYNTHETIC — For demonstration only.", DISC)]

    doc.build(story)
    print("  Generated: Goulds_3196STX_ANSI_CentrifugalPump_IOM.pdf")

build_goulds_manual()
print("\nBoth pump manuals generated successfully.")
