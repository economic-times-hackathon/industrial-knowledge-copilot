"""
Synthetic Inspection Checklists, Work Orders, and Maintenance Records
Generates 8 documents (mix of PDFs and CSVs) for corpus/maintenance_data/
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import csv, os, random, datetime

OUT_M = r"C:\Users\hp859\Desktop\economic_times_hack\corpus\maintenance_data"
os.makedirs(OUT_M, exist_ok=True)

styles = getSampleStyleSheet()
def ms(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=styles[parent], **kw)

TITL = ms("TI", fontSize=16, fontName="Helvetica-Bold", textColor=HexColor("#003366"), alignment=TA_CENTER, spaceAfter=4)
SUBT = ms("SU", fontSize=10, textColor=HexColor("#005588"), alignment=TA_CENTER, spaceAfter=6)
H2   = ms("H2", "Heading2", fontSize=11, textColor=HexColor("#003366"), spaceAfter=3)
BODY = ms("BD", fontSize=8, leading=12, spaceAfter=3)
DISC = ms("DC", fontSize=7, textColor=HexColor("#888888"), alignment=TA_CENTER, spaceAfter=3)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=HexColor("#003366"), spaceAfter=5)
def sp(h=5): return Spacer(1, h)
def p(t, s=BODY): return Paragraph(t, s)

HDR_BG  = HexColor("#003366")
HDR_FG  = colors.white
ALT_BG  = HexColor("#f0f4f8")
WARN_BG = HexColor("#fff3cd")
PASS_BG = HexColor("#d4edda")
FAIL_BG = HexColor("#f8d7da")

def make_table(data, col_widths=None, header=True):
    t = Table(data, colWidths=col_widths)
    s = TableStyle([
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("GRID",          (0,0), (-1,-1), 0.4, HexColor("#aaaaaa")),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
    ])
    if header:
        s.add("BACKGROUND",  (0,0), (-1,0), HDR_BG)
        s.add("TEXTCOLOR",   (0,0), (-1,0), HDR_FG)
        s.add("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold")
        s.add("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ALT_BG])
    t.setStyle(s)
    return t

# ── DOC 1: Centrifugal Pump Inspection Checklist ────────────────────────────
def doc1_pump_inspection():
    path = os.path.join(OUT_M, "CHK-001-Centrifugal-Pump-Inspection-Checklist.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []

    story += [p("SYNTH-REFINERY-01  |  MAINTENANCE DEPARTMENT", TITL),
              p("CENTRIFUGAL PUMP — MONTHLY INSPECTION CHECKLIST", SUBT), hr(),
              make_table([
                  ["Equipment Tag","P-101A / P-101B","Work Order No.","WO-2024-03-1147"],
                  ["Equipment Desc.","Crude Charge Pump — CDU Feed","Inspection Date","15-Mar-2024"],
                  ["Location","CDU Pump House — Row A","Inspector","R. Sharma (E-4521)"],
                  ["Service","Crude Oil  95°C  8 barg","Next Due","15-Apr-2024"],
              ], col_widths=[38*mm, 55*mm, 38*mm, 44*mm], header=False),
              sp(5), hr(),
              p("SECTION A — RUNNING CHECKS (pump in service)", H2),
              make_table([
                  ["#","Check Item","Measurement / Observation","Limit","Status","Remarks"],
                  ["A1","Discharge pressure (PI-101)","8.4 barg","7.8–9.2 barg","✓ PASS",""],
                  ["A2","Flow rate (FI-101)","182 m³/h","160–210 m³/h","✓ PASS",""],
                  ["A3","Suction pressure (PI-100)","1.2 barg",">0.5 barg","✓ PASS",""],
                  ["A4","DE bearing temperature","54°C","<80°C","✓ PASS",""],
                  ["A5","NDE bearing temperature","51°C","<80°C","✓ PASS",""],
                  ["A6","Vibration — DE (velocity RMS)","2.1 mm/s","<4.5 mm/s","✓ PASS",""],
                  ["A7","Vibration — NDE","1.9 mm/s","<4.5 mm/s","✓ PASS",""],
                  ["A8","Mechanical seal leakage","Nil visible","No liquid drops","✓ PASS",""],
                  ["A9","Bearing oil level (sight glass)","Mid-level","Mid ±10 mm","✓ PASS",""],
                  ["A10","Motor current (A-phase)","38 A","≤42 A (FLA)","✓ PASS",""],
                  ["A11","Motor body temperature","52°C","<80°C","✓ PASS",""],
                  ["A12","Abnormal noise (cavitation/rattle)","None","None","✓ PASS",""],
                  ["A13","Coupling guard secure","Secure","Secure","✓ PASS",""],
                  ["A14","Seal flush Plan 11 flow","Visible","Visible","✓ PASS",""],
              ], col_widths=[10*mm, 60*mm, 40*mm, 28*mm, 22*mm, 25*mm]),
              sp(5),
              p("SECTION B — STANDBY PUMP CHECKS (P-101B)", H2),
              make_table([
                  ["#","Check Item","Finding","Status","Remarks"],
                  ["B1","Suction valve position","OPEN","✓ PASS",""],
                  ["B2","Discharge valve position","CLOSED (1 turn off seat)","✓ PASS",""],
                  ["B3","Vent valve — drain check","No leakage","✓ PASS",""],
                  ["B4","Auto-start signal available","DCS indication — READY","✓ PASS",""],
                  ["B5","Bearing oil level","Mid-level","✓ PASS",""],
                  ["B6","Visual — no leaks or corrosion","Minor surface rust on drain plug","⚠ NOTE","Clean and apply rust-preventive"],
              ], col_widths=[10*mm, 70*mm, 50*mm, 22*mm, 38*mm]),
              sp(5),
              p("SECTION C — GENERAL OBSERVATIONS", H2),
              make_table([
                  ["Item","Description"],
                  ["Housekeeping","Oil drip tray clean. Pump area clear of debris."],
                  ["Insulation","Suction pipe insulation intact. Discharge flange insulation — minor damage at east side flange, repair required."],
                  ["Earthing/Bonding","Earth strap intact on pump body and motor."],
                  ["Nameplate","P-101A nameplate legible and correctly tagged."],
                  ["Previous WO follow-up","WO-2024-02-1089 (bearing oil change) — completed and closed."],
              ], col_widths=[45*mm, 140*mm]),
              sp(5),
              make_table([
                  ["Action Items","Owner","Target Date","Priority"],
                  ["Repair discharge flange insulation — P-101A","Insulation Contractor","30-Mar-2024","Medium"],
                  ["Apply rust preventive to P-101B drain plug","Maint. Tech R. Kumar","20-Mar-2024","Low"],
              ], col_widths=[80*mm, 45*mm, 30*mm, 25*mm]),
              sp(5),
              make_table([
                  ["Inspector Signature","R. Sharma","Date","15-Mar-2024","Overall Result","✓ ACCEPTABLE"],
                  ["Supervisor Review","D. Patel (Maint Supv)","Date","16-Mar-2024","",""],
              ], col_widths=[40*mm, 40*mm, 15*mm, 28*mm, 28*mm, 34*mm], header=False),
              sp(6),
              p("SYNTHETIC DOCUMENT — For hackathon demonstration. Form Ref: MAINT-FORM-CHK-001 Rev 3.", DISC)]
    doc.build(story)
    print("  Generated: CHK-001-Centrifugal-Pump-Inspection-Checklist.pdf")

doc1_pump_inspection()

# ── DOC 2: Heat Exchanger Tube Bundle Inspection ────────────────────────────
def doc2_hex_inspection():
    path = os.path.join(OUT_M, "CHK-002-HeatExchanger-TubeBundle-Inspection.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story += [p("SYNTH-REFINERY-01  |  INSPECTION & INTEGRITY DEPARTMENT", TITL),
              p("HEAT EXCHANGER — TUBE BUNDLE INSPECTION RECORD", SUBT), hr(),
              make_table([
                  ["Equipment Tag","E-101","Work Order No.","WO-2024-01-0892"],
                  ["Service","Crude/Kero Preheat","Inspection Date","10-Jan-2024"],
                  ["TEMA Type","AEL  Shell-and-Tube","Inspector","A. Verma (NDE-L2)"],
                  ["Design Press (S/T)","12 / 10 barg","Design Temp (S/T)","200°C / 180°C"],
                  ["Tube Material","CS ASTM A179","No. of Tubes","196  (2 passes)"],
                  ["Last Inspection","Jan-2022","Inspection Interval","24 months"],
              ], col_widths=[35*mm, 50*mm, 38*mm, 52*mm], header=False),
              sp(5), hr(),
              p("SECTION 1 — VISUAL INSPECTION", H2),
              make_table([
                  ["#","Item","Finding","Status"],
                  ["1.1","Tube sheet face — pitting/corrosion","Minor pitting on peripheral tubes, depth <0.5 mm","ACCEPTABLE"],
                  ["1.2","Tube ends — erosion/thinning","3 tubes show inlet erosion (NE quadrant)","MONITOR"],
                  ["1.3","Baffle plates — condition","Intact, no cracks, minor fouling deposit","ACCEPTABLE"],
                  ["1.4","Shell interior — corrosion","Light scale, no pitting","ACCEPTABLE"],
                  ["1.5","Expansion joint (if any)","N/A — fixed tubesheet design","N/A"],
                  ["1.6","Nozzle bore / flange faces","Clean, no damage","ACCEPTABLE"],
                  ["1.7","Fouling — tube side","Light hydrocarbon deposit, cleaned by hydrojetting","ACCEPTABLE"],
                  ["1.8","Fouling — shell side","Light scale removed during turnaround","ACCEPTABLE"],
              ], col_widths=[12*mm, 75*mm, 70*mm, 25*mm]),
              sp(4),
              p("SECTION 2 — NDE RESULTS — EDDY CURRENT TESTING", H2),
              make_table([
                  ["Parameter","Value"],
                  ["NDE Method","Eddy Current Testing (ECT) — rotary probe"],
                  ["Instrument","Olympus Nortec 600D  (Cal. cert: EC-2024-0145)"],
                  ["Calibration Standard","20% notch, 40% notch, 80% notch in CS reference tube"],
                  ["Total Tubes Tested","196 of 196  (100%)"],
                  ["Tubes with <20% wall loss","187 tubes",""],
                  ["Tubes with 20-40% wall loss","7 tubes (IDs: T-14, T-27, T-55, T-88, T-102, T-134, T-167)",""],
                  ["Tubes with 40-80% wall loss","2 tubes (IDs: T-73, T-112)","PLUG RECOMMENDED"],
                  ["Tubes with >80% wall loss","0",""],
              ], col_widths=[80*mm, 95*mm]),
              sp(4),
              p("SECTION 3 — HYDROTEST RESULTS", H2),
              make_table([
                  ["Test","Pressure","Duration","Result","Witnessed By"],
                  ["Shell side hydrotest","18 barg (1.5× DP)","30 min","No leaks — PASS","D. Patel (Supv)"],
                  ["Tube side hydrotest","15 barg (1.5× DP)","30 min","No leaks — PASS","D. Patel (Supv)"],
              ], col_widths=[40*mm, 28*mm, 25*mm, 38*mm, 44*mm]),
              sp(5),
              p("SECTION 4 — RECOMMENDATIONS & ACTIONS", H2),
              make_table([
                  ["Action","Details","Priority","By","Date"],
                  ["Plug tubes T-73 and T-112","Wall loss >40% — plug with SS plugs per TEMA","HIGH","A. Verma","15-Jan-2024"],
                  ["Monitor tube group NE quadrant","Erosion pattern — re-inspect at 12 months","MEDIUM","Inspection","Jan-2025"],
                  ["Update tube condition map","Add ECT results to E-101 equipment record","Low","Doc Control","31-Jan-2024"],
              ], col_widths=[50*mm, 65*mm, 20*mm, 25*mm, 25*mm]),
              sp(5),
              make_table([["Inspector","A. Verma (NDE Level II)","Approval","D. Patel, Maint Supv","Date","10-Jan-2024"]], col_widths=[25*mm, 55*mm, 25*mm, 55*mm, 15*mm, 30*mm], header=False),
              sp(4),
              p("SYNTHETIC DOCUMENT — For hackathon demonstration. Form Ref: INSP-FORM-HEX-002 Rev 2.", DISC)]
    doc.build(story)
    print("  Generated: CHK-002-HeatExchanger-TubeBundle-Inspection.pdf")

doc2_hex_inspection()

# ── DOC 3: Relief Valve Test Record ─────────────────────────────────────────
def doc3_relief_valve():
    path = os.path.join(OUT_M, "CHK-003-Relief-Valve-Test-Record.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story += [p("SYNTH-REFINERY-01  |  SAFETY & RELIABILITY DEPARTMENT", TITL),
              p("PRESSURE RELIEF VALVE — BENCH TEST & RECERTIFICATION RECORD", SUBT), hr(),
              make_table([
                  ["PSV Tag","PSV-101","Work Order","WO-2024-01-0901"],
                  ["Manufacturer","Emerson / Crosby","Model","Series 900"],
                  ["Valve Size","3\" × 4\"  (inlet × outlet)","Type","Conventional spring-loaded"],
                  ["Protected Equipment","V-101 — Atmospheric Distillation Column","Set Pressure","8.0 barg"],
                  ["Back Pressure","0.3 barg (constant)","Inlet Connection","3\" ANSI 150 RF"],
                  ["Process Fluid","Hydrocarbon vapour  (MW 85)","Temp at Inlet","180°C"],
                  ["Last Test Date","Jan-2022","Test Interval","24 months (OISD requirement)"],
                  ["Test Date","22-Jan-2024","Test Location","Certified Valve Shop — MV Services Pvt Ltd"],
              ], col_widths=[40*mm, 55*mm, 35*mm, 45*mm], header=False),
              sp(5), hr(),
              p("AS-FOUND TEST RESULTS (before any adjustment)", H2),
              make_table([
                  ["Test","Specified","As-Found","Deviation","Status"],
                  ["Set pressure (opening)","8.0 barg","8.35 barg","+4.4%","⚠ FAIL — exceeds +3% tolerance"],
                  ["Seat leak test (10% below set)","Bubble-tight at 7.2 barg","1 bubble/min at 7.2 barg","Minor","MARGINAL"],
                  ["Full lift (at 110% set pressure)","Confirm full lift at 8.8 barg","Full lift at 8.8 barg","—","✓ PASS"],
                  ["Blowdown","10–15%","12%","—","✓ PASS"],
              ], col_widths=[55*mm, 38*mm, 38*mm, 22*mm, 32*mm]),
              sp(4),
              p("FINDINGS & CORRECTIVE WORK", H2),
              make_table([
                  ["Finding","Spring set drift +4.4% due to corrosion deposits on spring. Seat lapping required for bubble-tight seal."],
                  ["Work Performed","1. Disassembled valve completely.\n2. Inspected all parts — spring in tolerance (free length 148 mm vs 149 mm new).\n3. Lapped inlet seat and disc — achieved bubble-tight seal.\n4. Adjusted spring compression to achieve 8.0 barg set pressure.\n5. Replaced body/bonnet gasket and stem guide O-ring.\n6. Reassembled, tested, tagged."],
                  ["Parts Replaced","Body-bonnet gasket (Grafoil), stem guide O-ring (Viton), spring saddle pin"],
              ], col_widths=[38*mm, 147*mm]),
              sp(4),
              p("AS-LEFT TEST RESULTS (after servicing)", H2),
              make_table([
                  ["Test","Specified","As-Left","Status"],
                  ["Set pressure","8.0 barg","8.02 barg (+0.25%)","✓ PASS"],
                  ["Seat leak at 10% below set","Bubble-tight","Zero bubbles at 7.2 barg","✓ PASS"],
                  ["Blowdown","10–15%","11%","✓ PASS"],
                  ["Visual — bore clear, no damage","Clear","Clear — no blockage","✓ PASS"],
              ], col_widths=[55*mm, 40*mm, 50*mm, 30*mm]),
              sp(4),
              make_table([
                  ["Valve Disposition","RETURN TO SERVICE — After-left test satisfactory"],
                  ["Next Test Due","January 2026 (24-month interval per OISD STD-140)"],
                  ["Test Certificate No.","MV-TEST-2024-0147"],
              ], col_widths=[45*mm, 140*mm]),
              sp(5),
              make_table([["Tested By","S. Khan, Senior Valve Tech","Certified By","MV Services Pvt Ltd (PESO Approved)","Date","22-Jan-2024"]], col_widths=[22*mm, 55*mm, 22*mm, 65*mm, 15*mm, 30*mm], header=False),
              sp(4),
              p("SYNTHETIC DOCUMENT — For hackathon demonstration. Form Ref: SAFETY-FORM-PSV-003 Rev 4.", DISC)]
    doc.build(story)
    print("  Generated: CHK-003-Relief-Valve-Test-Record.pdf")

doc3_relief_valve()

# ── DOC 4: Rotating Equipment Work Order ────────────────────────────────────
def doc4_work_order():
    path = os.path.join(OUT_M, "WO-2024-03-1201-Pump-Bearing-Replacement.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story += [p("SYNTH-REFINERY-01  |  CMMS WORK ORDER", TITL),
              p("CORRECTIVE MAINTENANCE — PUMP BEARING REPLACEMENT", SUBT), hr(),
              make_table([
                  ["WO Number","WO-2024-03-1201","Priority","HIGH — Equipment failure"],
                  ["Equipment Tag","P-201A","Equipment Desc","Reflux Pump — CDU Overhead"],
                  ["Location","CDU Pump House Row B","System","Crude Distillation Unit"],
                  ["Failure Reported By","Control Room Operator","Reported Date/Time","18-Mar-2024  02:35"],
                  ["Failure Mode","High bearing temperature alarm (TT-201: 88°C)","Work Type","Corrective Maintenance"],
                  ["Assigned To","B. Nair, Mech Tech Grade 3","Supervisor","D. Patel"],
                  ["Target Start","18-Mar-2024  06:00","Target Completion","18-Mar-2024  14:00"],
                  ["Actual Start","18-Mar-2024  06:15","Actual Completion","18-Mar-2024  13:45"],
              ], col_widths=[40*mm, 55*mm, 38*mm, 52*mm], header=False),
              sp(5), hr(),
              p("FAILURE DESCRIPTION & DIAGNOSIS", H2),
              make_table([
                  ["Parameter","Value"],
                  ["Alarm Received","18-Mar-2024 02:35 — TT-201 bearing temp HIGH alarm (88°C, set 80°C)"],
                  ["Operator Action","Switched to standby pump P-201B at 02:40. P-201A isolated."],
                  ["Initial Finding","DE bearing temperature 88°C (Amb = 35°C, normal = 55°C)"],
                  ["Vibration Trend","Vibration trended from 3.2 mm/s to 6.8 mm/s over 72 hours (OSA trend data)"],
                  ["Root Cause (Preliminary)","Bearing oil contaminated with water — oil emulsification observed on inspection"],
                  ["Contributing Factor","Seal plan 11 cooler tube leak allowing cooling water into oil cavity (confirmed)"],
              ], col_widths=[55*mm, 130*mm]),
              sp(4),
              p("WORK STEPS — LOTO & MAINTENANCE", H2),
              make_table([
                  ["Step","Task Description","Craftsperson","Start","End","Status"],
                  ["1","Apply LOTO — E/I isolation, pressure zero verify","B. Nair + E/I Tech","06:15","06:45","DONE"],
                  ["2","Remove coupling guard, disconnect coupling spacer","B. Nair","06:45","07:00","DONE"],
                  ["3","Back-pullout rotating element (back-pullout design)","B. Nair + helper","07:00","07:40","DONE"],
                  ["4","Inspect bearings — DE radial & NDE thrust","B. Nair","07:40","08:10","DONE"],
                  ["5","Confirm bearing damage — DE ball bearing inner race spalling","B. Nair","08:10","08:20","DONE"],
                  ["6","Replace DE radial bearing SKF 6309 and NDE thrust pair 7309","B. Nair","08:20","09:30","DONE"],
                  ["7","Replace bearing housing oil seals (both sides)","B. Nair","09:30","09:50","DONE"],
                  ["8","Inspect / replace mechanical seal — faces OK, O-rings replaced","B. Nair","09:50","10:30","DONE"],
                  ["9","Repair plan 11 cooler tube leak — E-201 tube plugged (1 tube)","E/I + Mech","10:30","11:45","DONE"],
                  ["10","Reassemble pump, fill bearing housing ISO VG 68 oil","B. Nair","11:45","12:30","DONE"],
                  ["11","Re-align pump to motor — laser alignment tool","B. Nair + Supv","12:30","13:00","DONE"],
                  ["12","Remove LOTO, cold run test — 10 min at low flow","B. Nair + Oper","13:00","13:30","DONE"],
                  ["13","Return to service, monitor for 1 hour","Operator","13:30","14:30","DONE"],
              ], col_widths=[10*mm, 68*mm, 28*mm, 14*mm, 14*mm, 16*mm]),
              sp(4),
              p("POST-MAINTENANCE TEST RESULTS", H2),
              make_table([
                  ["Parameter","Before Shutdown","After Repair","Status"],
                  ["Bearing temp DE","88°C (alarm)","52°C","✓ NORMAL"],
                  ["Bearing temp NDE","76°C (high)","49°C","✓ NORMAL"],
                  ["Vibration DE","6.8 mm/s","1.8 mm/s","✓ NORMAL"],
                  ["Seal leakage","Nil","Nil","✓ NORMAL"],
                  ["Alignment — angular","Not checked","0.03 mm/100 mm","✓ PASS"],
                  ["Alignment — parallel","Not checked","0.04 mm TIR","✓ PASS"],
              ], col_widths=[50*mm, 40*mm, 40*mm, 30*mm]),
              sp(4),
              p("MATERIALS USED", H2),
              make_table([
                  ["Material","Part No.","Qty","Store Issue No."],
                  ["SKF 6309 Deep Groove Ball Bearing","SKF-6309-2RS","1","SI-2024-0892"],
                  ["SKF 7309 Angular Contact Pair (DB)","SKF-7309-BECBP-PAIR","1 pr","SI-2024-0892"],
                  ["Oil seal — inboard","3196-OS-IB","1","SI-2024-0892"],
                  ["Oil seal — outboard","3196-OS-OB","1","SI-2024-0892"],
                  ["O-ring set — mechanical seal","JC21-OR-SET-1.5","1 set","SI-2024-0892"],
                  ["ISO VG 68 bearing oil","SHELL TELLUS S2 V68","0.8 L","SI-2024-0892"],
              ], col_widths=[65*mm, 38*mm, 15*mm, 42*mm]),
              sp(4),
              p("ROOT CAUSE & CORRECTIVE ACTIONS", H2),
              make_table([
                  ["Root Cause","Seal plan 11 cooler (tube E-201) developed a pinhole tube leak allowing cooling water into bearing housing oil. Oil emulsification reduced lubrication film leading to bearing spalling."],
                  ["Immediate CA","Plugged leaking tube in E-201. Replaced bearings and oil."],
                  ["Systemic CA","1. Revise PM schedule: oil sample analysis quarterly for all plan-11-cooled pumps.\n2. Add oil moisture check to monthly pump inspection form.\n3. Engineering to evaluate plan 21 (cooler after measurement point) for P-201A/B."],
              ], col_widths=[38*mm, 147*mm]),
              sp(5),
              make_table([["Technician","B. Nair","Supervisor Sign-off","D. Patel","WO Close Date","18-Mar-2024"]], col_widths=[28*mm, 40*mm, 38*mm, 40*mm, 30*mm, 34*mm], header=False),
              sp(4),
              p("SYNTHETIC DOCUMENT — For hackathon demonstration. CMMS Form Ref: WO-CORRECTIVE-MECH Rev 5.", DISC)]
    doc.build(story)
    print("  Generated: WO-2024-03-1201-Pump-Bearing-Replacement.pdf")

doc4_work_order()

# ── DOC 5: Instrument Calibration Record ────────────────────────────────────
def doc5_calibration():
    path = os.path.join(OUT_M, "CHK-004-Instrument-Calibration-Record.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story += [p("SYNTH-REFINERY-01  |  INSTRUMENT & CONTROL DEPARTMENT", TITL),
              p("INSTRUMENT CALIBRATION RECORD — QUARTERLY", SUBT), hr(),
              make_table([
                  ["Instrument Tag","TIC-205","Description","Crude Furnace Outlet Temp Controller"],
                  ["Instrument Type","Thermocouple + Temp Transmitter + Controller","Make/Model","ABB TTF300 Transmitter"],
                  ["Range","0-400°C","Output","4-20 mA"],
                  ["Process","CDU Crude Furnace F-101 Outlet","Location","CDU Control Room (DCS)"],
                  ["Calibration Date","20-Mar-2024","Next Due","20-Jun-2024"],
                  ["Calibrated By","P. Singh (I&C Tech)","Certificate","CAL-2024-0345"],
              ], col_widths=[40*mm, 65*mm, 32*mm, 48*mm], header=False),
              sp(5), hr(),
              p("AS-FOUND CALIBRATION (before adjustment)", H2),
              make_table([
                  ["Test Point (°C)","Applied Input (mV — J-type)","DCS Reading (°C)","Error (°C)","Pass/Fail (±1°C)"],
                  ["0","0.000 mV","0.3°C","+0.3","✓ PASS"],
                  ["100","5.269 mV","100.8°C","+0.8","✓ PASS"],
                  ["200","10.779 mV","201.2°C","+1.2","⚠ FAIL — marginally out"],
                  ["300","16.327 mV","301.5°C","+1.5","⚠ FAIL"],
                  ["350","19.090 mV","351.9°C","+1.9","⚠ FAIL"],
                  ["400","21.848 mV","402.3°C","+2.3","⚠ FAIL"],
              ], col_widths=[32*mm, 38*mm, 38*mm, 24*mm, 45*mm]),
              sp(3),
              p("As-Found: Transmitter zero OK, span drift of +0.5% of span (2°C at 400°C). Adjustment required.", BODY),
              sp(4),
              p("AS-LEFT CALIBRATION (after zero and span adjustment)", H2),
              make_table([
                  ["Test Point (°C)","Applied Input (mV)","DCS Reading (°C)","Error (°C)","Pass/Fail (±1°C)"],
                  ["0","0.000 mV","0.0°C","0.0","✓ PASS"],
                  ["100","5.269 mV","100.1°C","+0.1","✓ PASS"],
                  ["200","10.779 mV","200.1°C","+0.1","✓ PASS"],
                  ["300","16.327 mV","300.0°C","0.0","✓ PASS"],
                  ["350","19.090 mV","350.2°C","+0.2","✓ PASS"],
                  ["400","21.848 mV","400.0°C","0.0","✓ PASS"],
              ], col_widths=[32*mm, 38*mm, 38*mm, 24*mm, 45*mm]),
              sp(4),
              make_table([
                  ["Calibration Equipment","Fluke 724 Temperature Calibrator — Cal cert FC-2024-0189 (valid to Sep-2024)"],
                  ["Reference Standard","NIST traceable — uncertainty ±0.05°C"],
                  ["Adjustment Made","Span adjustment — trim factor changed from 1.0000 to 0.9950 in ABB TTF300 configuration"],
                  ["Result","AS-LEFT — ALL POINTS WITHIN ±1°C TOLERANCE — INSTRUMENT IN SERVICE"],
              ], col_widths=[45*mm, 140*mm]),
              sp(5),
              make_table([["Technician","P. Singh","Reviewer","K. Mehta (I&C Lead)","Date","20-Mar-2024"]], col_widths=[28*mm, 45*mm, 28*mm, 55*mm, 15*mm, 34*mm], header=False),
              sp(4),
              p("SYNTHETIC DOCUMENT — Hackathon demonstration. Form Ref: IC-FORM-CAL-004 Rev 3.", DISC)]
    doc.build(story)
    print("  Generated: CHK-004-Instrument-Calibration-Record.pdf")

doc5_calibration()

# ── DOC 6: Near-Miss Incident Report ────────────────────────────────────────
def doc6_near_miss():
    path = os.path.join(OUT_M, "IR-2024-NM-047-HotOil-LeakNearMiss.pdf")
    doc  = SimpleDocTemplate(path, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    story = []
    story += [p("SYNTH-REFINERY-01  |  HEALTH, SAFETY & ENVIRONMENT", TITL),
              p("NEAR-MISS INCIDENT INVESTIGATION REPORT", SUBT), hr(),
              make_table([
                  ["Report No.","IR-2024-NM-047","Incident Date","05-Feb-2024"],
                  ["Time","14:22 hrs","Location","CDU Unit — E-103 Area"],
                  ["Incident Type","Near-Miss — Hot Oil Leak","Potential Severity","HIGH (potential fire / burn injury)"],
                  ["Reported By","A. Kumar (Operator)","Supervisor","D. Patel"],
                  ["Investigation Lead","M. Reddy (HSE Officer)","Report Date","07-Feb-2024"],
              ], col_widths=[38*mm, 57*mm, 38*mm, 52*mm], header=False),
              sp(4), hr(),
              p("1. INCIDENT DESCRIPTION", H2),
              p("During routine unit inspection at 14:22 on 05-Feb-2024, Operator A. Kumar discovered a small weeping flange leak on the crude outlet nozzle of heat exchanger E-103. The leak was observed as a slow drip of hot crude oil (estimated 150°C) onto the concrete plinth below. No fire or injury occurred. The operator immediately informed the control room, and the unit was placed on reduced throughput pending repair."),
              p("Estimated leak rate: 2-5 drops per minute. The leak was from the south nozzle flange (100 NB ANSI 150 RF). The drip was falling onto the concrete plinth approximately 1.2 m below the flange and 0.4 m from a cable tray containing instrument signal cables."),
              sp(3),
              p("2. IMMEDIATE ACTIONS TAKEN", H2),
              make_table([
                  ["#","Action","By","Time"],
                  ["1","Control room notified — throughput reduced to 60%","A. Kumar","14:25"],
                  ["2","Portable steam smothering hose positioned at leak point","Fire watch team","14:35"],
                  ["3","Fire watch assigned — continuous manning until repair","Contractor A","14:40"],
                  ["4","LOTO initiated for E-103 flange repair","Maintenance","15:30"],
                  ["5","Flange retorqued — 4 bolts found 15% under torque","B. Nair, Mech","16:15"],
                  ["6","Leak stopped after retorque — unit returned to normal","—","17:00"],
              ], col_widths=[10*mm, 90*mm, 42*mm, 28*mm]),
              sp(3),
              p("3. ROOT CAUSE ANALYSIS", H2),
              make_table([
                  ["Category","Finding"],
                  ["Immediate Cause","Flange joint insufficiently torqued — 4 of 8 studs at 82–85% of specified torque"],
                  ["Contributing — Physical","Gasket (Grafoil spiral wound) had undergone minor creep relaxation after last turnaround installation (Jan-2022)"],
                  ["Contributing — Human","No hot retorque procedure performed at turnaround handback — not included in post-turnaround checklist"],
                  ["Root Cause — System","Turnaround completion checklist (TAR-CHK-004) does not include hot retorque step for critical flanges in hot oil service"],
                  ["Root Cause — Organisational","Hot retorque requirement of OISD STD-144 Section 7.3 not translated into plant procedures"],
              ], col_widths=[48*mm, 137*mm]),
              sp(3),
              p("4. CORRECTIVE & PREVENTIVE ACTIONS", H2),
              make_table([
                  ["Action","Owner","Target","Status"],
                  ["Update TAR-CHK-004 to include hot retorque at 8h, 24h, and 72h after restart for all flanges DN50+ in hot oil service","M. Reddy + Process Eng","28-Feb-2024","IN PROGRESS"],
                  ["Issue toolbox talk to all operators on hot flange leak identification and immediate response protocol","HSE Officer","15-Feb-2024","CLOSED"],
                  ["Review all E-series exchangers in CDU for post-turnaround retorque status — physical check","Maintenance","20-Feb-2024","CLOSED"],
                  ["Revise Permit-to-Work procedure to require fire watch for any hot oil flange work above 100°C","M. Reddy","28-Feb-2024","IN PROGRESS"],
                  ["Share lessons learned at refinery HSE meeting and submit to OISD incident database","HSE Dept","07-Mar-2024","PLANNED"],
              ], col_widths=[90*mm, 32*mm, 28*mm, 28*mm]),
              sp(4),
              p("5. LESSONS LEARNED", H2),
              p("Hot oil flange leaks have high fire potential. The proximity of this leak to instrument cable trays could have resulted in cable damage, false instrument readings, and loss of process control in addition to a potential fire. Post-turnaround hot retorque of flanged joints in hot service is mandatory per OISD STD-144 and must be formalised in plant procedures. Near-misses must be treated with the same rigour as recordable incidents — this event had potential for an OSHA recordable fire."),
              sp(5),
              make_table([["Prepared By","M. Reddy (HSE)","Approved By","V. Singh (Plant Manager)","Date","07-Feb-2024"]], col_widths=[25*mm, 50*mm, 25*mm, 55*mm, 15*mm, 35*mm], header=False),
              sp(4),
              p("SYNTHETIC DOCUMENT — Hackathon demonstration. Form Ref: HSE-FORM-NM-006 Rev 2.", DISC)]
    doc.build(story)
    print("  Generated: IR-2024-NM-047-HotOil-LeakNearMiss.pdf")

doc6_near_miss()

# ── DOC 7: Sensor readings CSV — Equipment history log ─────────────────────
def doc7_sensor_csv():
    path = os.path.join(OUT_M, "HIST-P101A-Sensor-Readings-2024-Q1.csv")
    random.seed(42)
    base_date = datetime.datetime(2024, 1, 1, 0, 0, 0)
    headers = [
        "timestamp","equipment_tag","equipment_desc",
        "discharge_pressure_barg","flow_rate_m3h","suction_pressure_barg",
        "bearing_temp_de_c","bearing_temp_nde_c",
        "vibration_de_mms","vibration_nde_mms",
        "motor_current_a","motor_temp_c","status"
    ]
    rows = []
    for hour in range(90*24):   # 90 days × 24 hours
        dt = base_date + datetime.timedelta(hours=hour)
        # Simulate gradual bearing degradation starting week 9
        deg = max(0, (hour - 1440) / (90*24 - 1440))  # 0 to 1 degradation factor
        btemp_de  = round(52 + deg*28 + random.gauss(0, 1.5), 1)
        btemp_nde = round(49 + deg*20 + random.gauss(0, 1.2), 1)
        vib_de    = round(1.8 + deg*4.5 + random.gauss(0, 0.2), 2)
        vib_nde   = round(1.6 + deg*3.0 + random.gauss(0, 0.15), 2)
        dp        = round(8.3 + random.gauss(0, 0.15), 2)
        flow      = round(185 + random.gauss(0, 5), 1)
        sp        = round(1.2 + random.gauss(0, 0.05), 2)
        amps      = round(38 + deg*2 + random.gauss(0, 0.5), 1)
        mtemp     = round(51 + random.gauss(0, 2), 1)
        # Status flags
        if btemp_de > 88 or vib_de > 6.5:
            status = "ALARM"
        elif btemp_de > 75 or vib_de > 4.5:
            status = "WARNING"
        else:
            status = "NORMAL"
        rows.append([
            dt.strftime("%Y-%m-%d %H:%M:%S"), "P-101A", "Crude Charge Pump CDU",
            dp, flow, sp, btemp_de, btemp_nde, vib_de, vib_nde, amps, mtemp, status
        ])
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"  Generated: HIST-P101A-Sensor-Readings-2024-Q1.csv  ({len(rows)} rows)")

doc7_sensor_csv()


# ── DOC 8: Equipment Failure History CSV ────────────────────────────────────
def doc8_failure_history():
    path = os.path.join(OUT_M, "HIST-EquipmentFailure-2019-2024.csv")
    headers = [
        "failure_id","date","equipment_tag","equipment_desc","unit","failure_mode",
        "failure_mechanism","component_failed","downtime_hours","repair_cost_inr",
        "root_cause_category","was_preventable","work_order","technician"
    ]
    records = [
        ["F-001","2019-03-12","P-101A","Crude Charge Pump","CDU","Mechanical Seal Failure","Dry running — loss of flush flow","Mechanical seal","6","45000","Human error — operator failed to open flush valve","Yes","WO-2019-03-0221","B. Nair"],
        ["F-002","2019-07-22","E-201","Overhead Condenser","CDU","Fouling — reduced heat transfer","Ammonium chloride salt deposition on tube side","Tube bundle","12","28000","Process — high chloride in crude","No","WO-2019-07-0567","A. Verma"],
        ["F-003","2019-11-05","K-601","H2 Recycle Compressor","HDS","High vibration trip","Impeller imbalance due to deposit buildup","Compressor impeller","24","380000","Process — catalyst fines carryover","Partially","WO-2019-11-0891","Ext: Siemens"],
        ["F-004","2020-02-14","PSV-101","Column Overhead Relief","CDU","Failure to reseat — passing valve","Seat erosion from previous lift","Valve disc/seat","4","35000","Mechanical wear","No","WO-2020-02-0113","S. Khan"],
        ["F-005","2020-08-30","P-201A","Reflux Pump","CDU","Bearing failure","Overgreasing — grease packing bearings","Radial bearing","8","32000","Maintenance error — PM procedure unclear","Yes","WO-2020-08-0643","R. Kumar"],
        ["F-006","2020-12-03","FCV-101","Crude Flow Control Valve","CDU","Control valve stuck open","Actuator diaphragm failure","Diaphragm","2","18000","Ageing — diaphragm beyond service life","Yes","WO-2020-12-0891","P. Singh"],
        ["F-007","2021-04-19","E-101","Crude/Kero Preheat","CDU","External corrosion — weld crack","Chloride SCC on SS shell nozzle weld","Shell nozzle weld","48","520000","Material — wrong alloy selected at design","No","WO-2021-04-0303","A. Verma"],
        ["F-008","2021-09-11","P-301A","BFW Pump","Utilities","Impeller erosion","Sand/particulate in BFW","Impeller","16","95000","Process — BFW filter bypassed during maintenance","Yes","WO-2021-09-0712","B. Nair"],
        ["F-009","2022-01-27","TIC-205","Crude Furnace Temp Controller","CDU","False high reading — instrument error","Thermowell erosion causing TC short to wall","Thermocouple","3","12000","Mechanical wear — beyond replacement interval","Partially","WO-2022-01-0044","P. Singh"],
        ["F-010","2022-06-14","B-101","Package Boiler","Utilities","High stack temperature alarm","Economiser fouling — ash deposit","Economiser tubes","6","55000","Process — high sulphur fuel oil","No","WO-2022-06-0489","Ext: Thermax"],
        ["F-011","2022-10-08","P-401A","CW Pump","Utilities","Motor burnt — single phasing","Loss of one supply phase — no phase loss relay","Motor windings","18","210000","Electrical — phase protection relay not commissioned","Yes","WO-2022-10-0723","Electrical Dept"],
        ["F-012","2023-02-22","V-601","HDS Feed Drum","HDS","High level trip — inlet valve stuck","Valve positioner failure — valve failed open","Positioner","4","22000","Ageing — positioner not in PM schedule","Yes","WO-2023-02-0178","P. Singh"],
        ["F-013","2023-07-05","R-601","HDS Reactor","HDS","High dp across bed","Catalyst channelling due to liquid maldistribution","Catalyst bed 1","36","180000","Process — high liquid entrainment from V-601","Partially","WO-2023-07-0534","Ext: Haldor Topsoe"],
        ["F-014","2023-11-19","P-101B","Crude Charge Pump Standby","CDU","Pump seized — standby failure","Standby pump not rotated — impeller seized in casing","Impeller + casing","72","680000","Maintenance — standby rotation PM not performed","Yes","WO-2023-11-0912","B. Nair"],
        ["F-015","2024-03-18","P-201A","Reflux Pump","CDU","Bearing failure — high temp alarm","Water contamination of bearing oil via plan 11 cooler leak","DE radial bearing","10","48000","Mechanical — E-201 tube leak (plan 11 cooler)","Partially","WO-2024-03-1201","B. Nair"],
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(records)
    print(f"  Generated: HIST-EquipmentFailure-2019-2024.csv  ({len(records)} records)")

doc8_failure_history()
print("\nAll 8 inspection/maintenance documents generated.")
