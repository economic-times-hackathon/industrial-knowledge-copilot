"""
Synthetic P&ID Generator — ISA-5.1 style
Generates 12 production-style P&IDs as PDFs with realistic equipment tags,
instrument loops, and control annotations.
"""
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os

OUT = r"C:\Users\hp859\Desktop\economic_times_hack\corpus\pids"
os.makedirs(OUT, exist_ok=True)

# ── Colour palette ──────────────────────────────────────────────────────────
C_LINE   = colors.black
C_INST   = HexColor("#1a1a6e")   # dark blue  – instrument circles
C_VALVE  = HexColor("#8b0000")   # dark red   – valves
C_EQUIP  = HexColor("#003300")   # dark green – vessels/exchangers
C_ANNOT  = HexColor("#555555")   # grey       – annotations
C_BG     = HexColor("#fafafa")
C_TITLE  = HexColor("#003366")

W, H = landscape(A3)            # 420 × 297 mm

# ── Low-level drawing helpers ────────────────────────────────────────────────
def new_canvas(filename):
    c = canvas.Canvas(os.path.join(OUT, filename), pagesize=landscape(A3))
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    return c

def title_block(c, dwg_no, title, rev="A", plant="SYNTH-REFINERY-01"):
    # border
    c.setStrokeColor(C_TITLE); c.setLineWidth(2)
    c.rect(10*mm, 10*mm, W-20*mm, H-20*mm, fill=0)
    # title box bottom-right
    bx, by, bw, bh = W-130*mm, 10*mm, 120*mm, 30*mm
    c.setStrokeColor(C_TITLE); c.setLineWidth(1)
    c.rect(bx, by, bw, bh, fill=0)
    c.setFillColor(C_TITLE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(bx+3*mm, by+20*mm, plant)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(bx+3*mm, by+12*mm, title)
    c.setFont("Helvetica", 8)
    c.drawString(bx+3*mm, by+5*mm,  f"DWG: {dwg_no}   REV: {rev}   SCALE: NTS")
    # legend box top-left
    lx, ly = 12*mm, H-55*mm
    c.setStrokeColor(C_ANNOT); c.setLineWidth(0.5)
    c.rect(lx, ly, 80*mm, 42*mm, fill=0)
    c.setFillColor(C_ANNOT); c.setFont("Helvetica-Bold", 8)
    c.drawString(lx+2*mm, ly+35*mm, "LEGEND")
    legend = [
        ("——————", "PROCESS LINE (50 NB & ABOVE)"),
        ("- - - - - -",  "INSTRUMENT SIGNAL"),
        ("○ circle",     "INSTRUMENT (ISA-5.1)"),
        ("◇ diamond",   "CONTROL VALVE"),
        ("□ square",    "VESSEL / COLUMN"),
    ]
    c.setFont("Helvetica", 7)
    for i, (sym, desc) in enumerate(legend):
        c.setFillColor(C_INST)
        c.drawString(lx+2*mm,  ly+(27-i*6)*mm, sym)
        c.setFillColor(C_ANNOT)
        c.drawString(lx+22*mm, ly+(27-i*6)*mm, desc)

def pipe(c, x1, y1, x2, y2, lw=1.5):
    c.setStrokeColor(C_LINE); c.setLineWidth(lw)
    c.line(x1, y1, x2, y2)

def dashed_pipe(c, x1, y1, x2, y2):
    c.setStrokeColor(C_INST); c.setLineWidth(0.7)
    c.setDash(4, 3)
    c.line(x1, y1, x2, y2)
    c.setDash()

def vessel(c, cx, cy, w, h, tag, desc=""):
    c.setStrokeColor(C_EQUIP); c.setFillColor(colors.white); c.setLineWidth(1.5)
    c.rect(cx-w/2, cy-h/2, w, h, fill=1)
    c.setFillColor(C_EQUIP); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx, cy+h/2+3*mm, tag)
    if desc:
        c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
        c.drawCentredString(cx, cy-h/2-5*mm, desc)

def heat_exchanger(c, cx, cy, tag, desc=""):
    w, h = 22*mm, 12*mm
    c.setStrokeColor(C_EQUIP); c.setFillColor(colors.white); c.setLineWidth(1.5)
    c.ellipse(cx-w/2, cy-h/2, cx+w/2, cy+h/2, fill=1)
    # tube passes
    c.setLineWidth(0.8); c.setStrokeColor(C_EQUIP)
    c.line(cx-8*mm, cy, cx+8*mm, cy)
    c.setFillColor(C_EQUIP); c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(cx, cy+h/2+3*mm, tag)
    if desc:
        c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
        c.drawCentredString(cx, cy-h/2-5*mm, desc)

def pump(c, cx, cy, tag):
    r = 6*mm
    c.setStrokeColor(C_EQUIP); c.setFillColor(colors.white); c.setLineWidth(1.5)
    c.circle(cx, cy, r, fill=1)
    c.setLineWidth(1); c.setStrokeColor(C_EQUIP)
    c.line(cx, cy+r, cx+r, cy-r)
    c.line(cx, cy+r, cx-r, cy-r)
    c.setFillColor(C_EQUIP); c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(cx, cy-r-4*mm, tag)

def instrument(c, cx, cy, tag, shared=False):
    """ISA-5.1 circle — solid border=field, dashed=panel"""
    r = 5*mm
    c.setStrokeColor(C_INST); c.setFillColor(HexColor("#e8f0ff")); c.setLineWidth(1)
    if shared:
        c.setDash(3, 2)
    c.circle(cx, cy, r, fill=1)
    c.setDash()
    c.setFillColor(C_INST); c.setFont("Helvetica-Bold", 6)
    # top half = function letter(s), bottom = loop number
    parts = tag.split("-")
    top = parts[0] if parts else tag
    bot = parts[1] if len(parts) > 1 else ""
    c.drawCentredString(cx, cy+1.5*mm, top)
    c.drawCentredString(cx, cy-3*mm,   bot)

def control_valve(c, cx, cy, tag, orient="H"):
    """Diamond shape for control valve"""
    s = 5*mm
    c.setStrokeColor(C_VALVE); c.setFillColor(HexColor("#fff0f0")); c.setLineWidth(1.2)
    p = c.beginPath()
    if orient == "H":
        p.moveTo(cx-s, cy); p.lineTo(cx, cy+s); p.lineTo(cx+s, cy)
        p.lineTo(cx, cy-s); p.close()
    else:
        p.moveTo(cx, cy-s); p.lineTo(cx+s, cy); p.lineTo(cx, cy+s)
        p.lineTo(cx-s, cy); p.close()
    c.drawPath(p, fill=1)
    c.setFillColor(C_VALVE); c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(cx, cy-s-3.5*mm, tag)

def tag_label(c, x, y, text, size=7):
    c.setFillColor(C_ANNOT); c.setFont("Helvetica", size)
    c.drawString(x, y, text)

# ════════════════════════════════════════════════════════════════════════════
# P&ID 01 — Crude Distillation Unit (CDU) Feed Section
# ════════════════════════════════════════════════════════════════════════════
def pid_01_cdu_feed():
    c = new_canvas("PID-01-CDU-Feed-Section.pdf")
    title_block(c, "PID-01-CDU-001", "CRUDE DISTILLATION UNIT — FEED & PREHEAT SECTION")

    # ── Crude feed pump P-101A/B ──
    pump(c, 60*mm, 140*mm, "P-101A")
    pump(c, 60*mm, 115*mm, "P-101B")
    tag_label(c, 48*mm, 103*mm, "CRUDE CHARGE PUMPS\n2×100% DUTY/STANDBY", 6)

    # Suction header from storage
    pipe(c, 30*mm, 140*mm, 54*mm, 140*mm)
    tag_label(c, 12*mm, 142*mm, "FROM CRUDE\nSTORAGE TK-001", 6.5)
    pipe(c, 30*mm, 115*mm, 54*mm, 115*mm)
    pipe(c, 30*mm, 115*mm, 30*mm, 140*mm)  # common suction header

    # Discharge headers
    pipe(c, 66*mm, 140*mm, 95*mm, 140*mm)
    pipe(c, 66*mm, 115*mm, 95*mm, 115*mm)
    pipe(c, 95*mm, 115*mm, 95*mm, 140*mm)  # join to common discharge
    pipe(c, 95*mm, 140*mm, 120*mm, 140*mm)

    # Flow measurement FIC-101
    instrument(c, 108*mm, 153*mm, "FIC-101")
    dashed_pipe(c, 108*mm, 140*mm, 108*mm, 148*mm)
    control_valve(c, 120*mm, 140*mm, "FCV-101")
    pipe(c, 125*mm, 140*mm, 150*mm, 140*mm)

    # Preheat train E-101 / E-102 / E-103
    heat_exchanger(c, 165*mm, 140*mm, "E-101", "CRUDE/KERO PHE")
    pipe(c, 150*mm, 140*mm, 154*mm, 140*mm)
    pipe(c, 176*mm, 140*mm, 200*mm, 140*mm)
    heat_exchanger(c, 215*mm, 140*mm, "E-102", "CRUDE/LGO PHE")
    pipe(c, 226*mm, 140*mm, 250*mm, 140*mm)
    heat_exchanger(c, 265*mm, 140*mm, "E-103", "CRUDE/HGO PHE")
    pipe(c, 276*mm, 140*mm, 305*mm, 140*mm)

    # Temperature indicators on PHE outlets
    instrument(c, 183*mm, 153*mm, "TI-103")
    dashed_pipe(c, 183*mm, 146*mm, 183*mm, 148*mm)
    instrument(c, 233*mm, 153*mm, "TI-105")
    dashed_pipe(c, 233*mm, 146*mm, 233*mm, 148*mm)
    instrument(c, 283*mm, 153*mm, "TI-107")
    dashed_pipe(c, 283*mm, 146*mm, 283*mm, 148*mm)

    # Crude furnace feed
    vessel(c, 330*mm, 140*mm, 30*mm, 20*mm, "F-101", "CRUDE FURNACE\n(REF: PID-02)")
    pipe(c, 305*mm, 140*mm, 315*mm, 140*mm)
    instrument(c, 318*mm, 153*mm, "TIC-205")
    dashed_pipe(c, 318*mm, 147*mm, 318*mm, 146*mm)

    # Pressure indicator on pump discharge
    instrument(c, 80*mm, 153*mm, "PI-101")
    dashed_pipe(c, 80*mm, 140*mm, 80*mm, 148*mm)
    instrument(c, 80*mm, 127*mm, "PI-102")
    dashed_pipe(c, 80*mm, 120*mm, 80*mm, 122*mm)  # P-101B discharge

    # Line labels
    tag_label(c, 132*mm, 143*mm, '4"-CR-1001-A1A', 6)
    tag_label(c, 195*mm, 143*mm, '6"-CR-1002-A1A', 6)
    tag_label(c, 245*mm, 143*mm, '6"-CR-1003-A1A', 6)
    tag_label(c, 290*mm, 143*mm, '8"-CR-1004-A1A', 6)

    # Notes
    tag_label(c, 12*mm, 60*mm, "NOTES:", 8)
    notes = [
        "1. ALL PIPING CLASS A1A (CS, 150# ANSI) UNLESS NOTED OTHERWISE.",
        "2. MIN FLOW BYPASS PROVIDED ON CRUDE CHARGE PUMPS — REF PID-01A.",
        "3. HEAT EXCHANGER TUBE SIDE: CRUDE OIL.  SHELL SIDE: HOT PRODUCT STREAMS.",
        "4. ALL INSTRUMENTS PER ISA-5.1-1984 (R1992) STANDARD.",
        "5. TAGGED EQUIPMENT REFER TO EQUIPMENT LIST DOC: EL-CDU-001.",
        "6. SYNTHETIC DOCUMENT — FOR HACKATHON DEMONSTRATION PURPOSES.",
    ]
    c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
    for i, n in enumerate(notes):
        c.drawString(12*mm, (54 - i*5)*mm, n)

    c.save(); print("  Generated: PID-01-CDU-Feed-Section.pdf")

pid_01_cdu_feed()

# ════════════════════════════════════════════════════════════════════════════
# P&ID 02 — Atmospheric Distillation Column
# ════════════════════════════════════════════════════════════════════════════
def pid_02_atm_column():
    c = new_canvas("PID-02-CDU-Atm-Column.pdf")
    title_block(c, "PID-01-CDU-002", "CRUDE DISTILLATION UNIT — ATMOSPHERIC COLUMN V-101")

    # Main column
    vessel(c, 180*mm, 140*mm, 28*mm, 100*mm, "V-101", "ATMOS. COLUMN\n24 TRAYS")

    # Feed inlet from furnace
    pipe(c, 30*mm, 140*mm, 166*mm, 140*mm, 2)
    tag_label(c, 32*mm, 143*mm, '8"-CR-1004-A1A  (FROM F-101)', 7)
    instrument(c, 80*mm, 153*mm, "TI-201"); dashed_pipe(c, 80*mm, 148*mm, 80*mm, 140*mm)
    instrument(c, 100*mm, 153*mm, "PI-201"); dashed_pipe(c, 100*mm, 148*mm, 100*mm, 140*mm)

    # Overhead vapour line
    pipe(c, 180*mm, 190*mm, 180*mm, 210*mm)
    pipe(c, 180*mm, 210*mm, 270*mm, 210*mm)
    tag_label(c, 185*mm, 212*mm, '10"-OV-2001-A2B  OVERHEAD VAPOUR', 6.5)
    heat_exchanger(c, 290*mm, 210*mm, "E-201", "OVHD CONDENSER")
    instrument(c, 220*mm, 223*mm, "TIC-201"); dashed_pipe(c, 220*mm, 218*mm, 220*mm, 210*mm)

    # Reflux drum
    vessel(c, 350*mm, 210*mm, 28*mm, 16*mm, "V-102", "REFLUX DRUM")
    pipe(c, 301*mm, 210*mm, 336*mm, 210*mm)
    instrument(c, 340*mm, 223*mm, "LIC-201"); dashed_pipe(c, 340*mm, 218*mm, 340*mm, 210*mm)

    # Reflux pump and return
    pump(c, 350*mm, 175*mm, "P-102A")
    pipe(c, 350*mm, 194*mm, 350*mm, 181*mm)  # drum to pump suction
    pipe(c, 350*mm, 169*mm, 350*mm, 155*mm)
    pipe(c, 350*mm, 155*mm, 194*mm, 155*mm)  # reflux return to column top
    tag_label(c, 300*mm, 157*mm, "REFLUX RETURN", 6.5)
    control_valve(c, 340*mm, 155*mm, "FCV-201")
    instrument(c, 327*mm, 168*mm, "FIC-201"); dashed_pipe(c, 327*mm, 163*mm, 327*mm, 155*mm)

    # Naphtha side draw (tray 20)
    pipe(c, 194*mm, 170*mm, 240*mm, 170*mm)
    tag_label(c, 200*mm, 173*mm, '3"-NS-2010  NAPHTHA DRAW', 6.5)
    control_valve(c, 255*mm, 170*mm, "FCV-210"); instrument(c, 255*mm, 183*mm, "FIC-210")
    dashed_pipe(c, 255*mm, 178*mm, 255*mm, 175*mm)

    # Kerosene side draw (tray 14)
    pipe(c, 194*mm, 145*mm, 240*mm, 145*mm)
    tag_label(c, 200*mm, 148*mm, '4"-KS-2011  KEROSENE DRAW', 6.5)
    control_valve(c, 255*mm, 145*mm, "FCV-211"); instrument(c, 255*mm, 158*mm, "FIC-211")
    dashed_pipe(c, 255*mm, 153*mm, 255*mm, 150*mm)

    # AGO side draw (tray 8)
    pipe(c, 194*mm, 120*mm, 240*mm, 120*mm)
    tag_label(c, 200*mm, 123*mm, '6"-AG-2012  AGO DRAW', 6.5)
    control_valve(c, 255*mm, 120*mm, "FCV-212"); instrument(c, 255*mm, 133*mm, "FIC-212")
    dashed_pipe(c, 255*mm, 128*mm, 255*mm, 125*mm)

    # Bottom: Atmospheric Residue
    pipe(c, 180*mm, 90*mm, 180*mm, 65*mm)
    pipe(c, 180*mm, 65*mm, 240*mm, 65*mm)
    tag_label(c, 185*mm, 67*mm, '10"-AR-2099  ATM RESIDUE TO VDU', 6.5)
    pump(c, 210*mm, 52*mm, "P-103A")
    pipe(c, 210*mm, 65*mm, 210*mm, 58*mm)
    instrument(c, 195*mm, 78*mm, "LIC-203"); dashed_pipe(c, 195*mm, 90*mm, 195*mm, 83*mm)
    control_valve(c, 230*mm, 65*mm, "LCV-203"); instrument(c, 230*mm, 78*mm, "LIC-203", True)
    dashed_pipe(c, 230*mm, 78*mm, 230*mm, 70*mm)

    # Column pressure
    instrument(c, 155*mm, 195*mm, "PIC-201"); dashed_pipe(c, 163*mm, 190*mm, 158*mm, 190*mm)
    dashed_pipe(c, 158*mm, 190*mm, 158*mm, 195*mm); dashed_pipe(c, 158*mm, 195*mm, 155*mm, 195*mm)

    tag_label(c, 12*mm, 50*mm, "NOTES:", 8)
    notes = [
        "1. COLUMN INTERNALS: SIEVE TRAYS, 24 TOTAL, NUMBERED FROM BOTTOM.",
        "2. STEAM STRIPPERS ON KEROSENE AND AGO DRAWS — REF PID-02A.",
        "3. ALL TEMPERATURE AND PRESSURE TAPS ON COLUMN WALL — NOZZLE SCHEDULE REF: NS-V-101.",
        "4. SYNTHETIC DOCUMENT — FOR HACKATHON DEMONSTRATION PURPOSES.",
    ]
    c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
    for i, n in enumerate(notes):
        c.drawString(12*mm, (44 - i*5)*mm, n)

    c.save(); print("  Generated: PID-02-CDU-Atm-Column.pdf")

pid_02_atm_column()

# ════════════════════════════════════════════════════════════════════════════
# P&ID 03 — Utility Steam System
# ════════════════════════════════════════════════════════════════════════════
def pid_03_steam_system():
    c = new_canvas("PID-03-Utility-Steam-System.pdf")
    title_block(c, "PID-UT-003", "UTILITY STEAM SYSTEM — HP/MP/LP HEADERS")

    # Boiler drum
    vessel(c, 60*mm, 180*mm, 24*mm, 40*mm, "B-101", "PACKAGE BOILER\n15 TPH  15 barg")

    # HP steam header (15 barg)
    pipe(c, 72*mm, 185*mm, 380*mm, 185*mm, 2)
    tag_label(c, 75*mm, 188*mm, "HP STEAM HEADER  15 barg  — 2\"-SS-HP-3001", 7)
    instrument(c, 100*mm, 198*mm, "PI-301"); dashed_pipe(c, 100*mm, 193*mm, 100*mm, 185*mm)
    instrument(c, 130*mm, 198*mm, "TI-301"); dashed_pipe(c, 130*mm, 193*mm, 130*mm, 185*mm)
    instrument(c, 160*mm, 198*mm, "FI-301"); dashed_pipe(c, 160*mm, 193*mm, 160*mm, 185*mm)

    # HP PRV → MP header (7 barg)
    pipe(c, 200*mm, 185*mm, 200*mm, 155*mm)
    control_valve(c, 200*mm, 163*mm, "PCV-301")
    instrument(c, 213*mm, 175*mm, "PIC-301"); dashed_pipe(c, 208*mm, 170*mm, 205*mm, 167*mm)
    pipe(c, 200*mm, 155*mm, 380*mm, 155*mm, 1.5)
    tag_label(c, 205*mm, 158*mm, "MP STEAM HEADER  7 barg  — 2\"-SS-MP-3002", 7)
    instrument(c, 240*mm, 165*mm, "PI-302"); dashed_pipe(c, 240*mm, 160*mm, 240*mm, 155*mm)
    instrument(c, 270*mm, 165*mm, "TI-302"); dashed_pipe(c, 270*mm, 160*mm, 270*mm, 155*mm)

    # MP PRV → LP header (3 barg)
    pipe(c, 310*mm, 155*mm, 310*mm, 125*mm)
    control_valve(c, 310*mm, 133*mm, "PCV-302")
    instrument(c, 323*mm, 145*mm, "PIC-302"); dashed_pipe(c, 318*mm, 140*mm, 315*mm, 137*mm)
    pipe(c, 200*mm, 125*mm, 380*mm, 125*mm, 1.5)
    pipe(c, 200*mm, 125*mm, 200*mm, 155*mm, 0.5)  # LP header starts here too
    pipe(c, 310*mm, 125*mm, 380*mm, 125*mm)
    tag_label(c, 205*mm, 128*mm, "LP STEAM HEADER  3.5 barg  — 2\"-SS-LP-3003", 7)
    instrument(c, 250*mm, 135*mm, "PI-303"); dashed_pipe(c, 250*mm, 130*mm, 250*mm, 125*mm)

    # Steam traps on HP header branches
    for i, (xb, label) in enumerate([(120*mm,"TO F-101 ATOMISING"), (220*mm,"TO V-101 STRIPPING"), (320*mm,"TO TRACING RING MAIN")]):
        pipe(c, xb, 185*mm, xb, 215*mm)
        tag_label(c, xb+2*mm, 205*mm, label, 6)
        # steam trap symbol (small box)
        c.setStrokeColor(C_EQUIP); c.setFillColor(colors.white); c.setLineWidth(1)
        c.rect(xb-3*mm, 218*mm, 6*mm, 6*mm, fill=1)
        c.setFillColor(C_EQUIP); c.setFont("Helvetica-Bold", 5)
        c.drawCentredString(xb, 220*mm, "ST")
        pipe(c, xb, 224*mm, xb, 240*mm)
        tag_label(c, xb+2*mm, 235*mm, "CONDENSATE\nRETURN", 5.5)

    # Boiler feedwater pump
    pump(c, 60*mm, 120*mm, "P-301A")
    pipe(c, 60*mm, 126*mm, 60*mm, 140*mm)
    pipe(c, 60*mm, 140*mm, 48*mm, 140*mm)
    tag_label(c, 30*mm, 142*mm, "BFW FROM\nDA-301", 6)
    pipe(c, 60*mm, 114*mm, 60*mm, 100*mm)
    pipe(c, 60*mm, 100*mm, 50*mm, 100*mm)
    pipe(c, 50*mm, 100*mm, 50*mm, 175*mm)
    pipe(c, 50*mm, 175*mm, 48*mm, 175*mm)
    instrument(c, 72*mm, 108*mm, "FIC-301"); dashed_pipe(c, 66*mm, 100*mm, 67*mm, 103*mm)
    control_valve(c, 60*mm, 90*mm, "FCV-301")

    tag_label(c, 12*mm, 55*mm, "NOTES:", 8)
    notes = [
        "1. ALL STEAM HEADERS INSULATED — 65mm MINERAL WOOL, AL CLADDING.",
        "2. SAFETY VALVES ON ALL HEADERS — REF SAFETY VALVE SCHEDULE SV-UT-001.",
        "3. PRESSURE REDUCING VALVES PCV-301 AND PCV-302: FISHER TYPE 627.",
        "4. BFW QUALITY: CONDUCTIVITY <0.5 µS/cm, O2 <10 ppb, SILICA <0.02 ppm.",
        "5. SYNTHETIC DOCUMENT — FOR HACKATHON DEMONSTRATION PURPOSES.",
    ]
    c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
    for i, n in enumerate(notes):
        c.drawString(12*mm, (49 - i*5)*mm, n)

    c.save(); print("  Generated: PID-03-Utility-Steam-System.pdf")

pid_03_steam_system()

# ════════════════════════════════════════════════════════════════════════════
# P&ID 04 — Cooling Water System
# ════════════════════════════════════════════════════════════════════════════
def pid_04_cooling_water():
    c = new_canvas("PID-04-Cooling-Water-System.pdf")
    title_block(c, "PID-UT-004", "COOLING WATER SYSTEM — SUPPLY & RETURN HEADERS")

    # Cooling tower
    vessel(c, 55*mm, 175*mm, 30*mm, 35*mm, "CT-401", "COOLING TOWER\n500 m³/h")
    tag_label(c, 30*mm, 155*mm, "INDUCED DRAFT\nFAN TOWER", 6)

    # CW supply pump
    pump(c, 55*mm, 120*mm, "P-401A")
    pump(c, 80*mm, 120*mm, "P-401B")
    tag_label(c, 42*mm, 108*mm, "CWS PUMPS 2×100%", 6)
    pipe(c, 55*mm, 157*mm, 55*mm, 126*mm)  # tower basin to pump suction
    pipe(c, 55*mm, 114*mm, 55*mm, 95*mm)   # pump discharge

    # CW Supply header
    pipe(c, 55*mm, 95*mm, 380*mm, 95*mm, 2)
    tag_label(c, 60*mm, 98*mm, "CW SUPPLY HEADER  3.5 barg  33°C  — 12\"-CWS-4001", 7)
    instrument(c, 90*mm, 108*mm,  "PI-401"); dashed_pipe(c, 90*mm, 103*mm, 90*mm, 95*mm)
    instrument(c, 120*mm, 108*mm, "TI-401"); dashed_pipe(c, 120*mm, 103*mm, 120*mm, 95*mm)
    instrument(c, 150*mm, 108*mm, "FI-401"); dashed_pipe(c, 150*mm, 103*mm, 150*mm, 95*mm)

    # CW consumers (heat exchangers) branching off supply header
    consumers = [
        (190*mm, "E-101\nCRUDE PHE", "FI-411"),
        (240*mm, "E-201\nOVHD COND", "FI-412"),
        (290*mm, "E-301\nHVGO COOL", "FI-413"),
        (340*mm, "E-401\nBFW PREH",  "FI-414"),
    ]
    for xc, eq_tag, fi_tag in consumers:
        pipe(c, xc, 95*mm, xc, 70*mm)   # supply branch down
        heat_exchanger(c, xc, 58*mm, eq_tag.split("\n")[0], eq_tag.split("\n")[1])
        instrument(c, xc+13*mm, 83*mm, fi_tag)
        dashed_pipe(c, xc+8*mm, 83*mm, xc+8*mm, 95*mm)
        pipe(c, xc, 46*mm, xc, 35*mm)   # return branch up to return header

    # CW Return header
    pipe(c, 55*mm, 35*mm, 380*mm, 35*mm, 2)
    tag_label(c, 60*mm, 37*mm, "CW RETURN HEADER  0.5 barg  43°C  — 12\"-CWR-4002", 7)
    instrument(c, 200*mm, 25*mm, "TI-402"); dashed_pipe(c, 200*mm, 30*mm, 200*mm, 35*mm)
    instrument(c, 300*mm, 25*mm, "TI-403"); dashed_pipe(c, 300*mm, 30*mm, 300*mm, 35*mm)

    # Return to tower
    pipe(c, 55*mm, 35*mm, 55*mm, 157*mm)

    # Chemical dosing
    vessel(c, 370*mm, 140*mm, 16*mm, 20*mm, "T-401", "BIOCIDE TANK")
    pump(c, 370*mm, 108*mm, "P-402")
    pipe(c, 370*mm, 120*mm, 370*mm, 114*mm)
    pipe(c, 370*mm, 102*mm, 370*mm, 95*mm)
    tag_label(c, 355*mm, 88*mm, "BIOCIDE\nDOSING", 6)

    # Make-up water
    pipe(c, 30*mm, 175*mm, 40*mm, 175*mm)
    tag_label(c, 12*mm, 177*mm, "MAKE-UP\nWATER", 6.5)
    control_valve(c, 35*mm, 175*mm, "LCV-401")
    instrument(c, 35*mm, 188*mm, "LIC-401"); dashed_pipe(c, 35*mm, 183*mm, 35*mm, 180*mm)

    tag_label(c, 12*mm, 20*mm, "NOTE: COOLING WATER SYSTEM DESIGN TEMP 45°C MAX RETURN.  BLOWDOWN CONTROLLED BY CONDUCTIVITY ANALYSER AT-401.  SYNTHETIC DOCUMENT.", 6.5)
    c.save(); print("  Generated: PID-04-Cooling-Water-System.pdf")

pid_04_cooling_water()

# ════════════════════════════════════════════════════════════════════════════
# P&ID 05 — Flare & Relief System
# ════════════════════════════════════════════════════════════════════════════
def pid_05_flare():
    c = new_canvas("PID-05-Flare-Relief-System.pdf")
    title_block(c, "PID-UT-005", "FLARE & RELIEF SYSTEM — FLARE KO DRUM & HEADER")

    # Flare stack
    vessel(c, 350*mm, 190*mm, 12*mm, 60*mm, "FL-501", "FLARE STACK\n30m HIGH")
    pipe(c, 350*mm, 160*mm, 350*mm, 155*mm, 2.5)

    # KO drum
    vessel(c, 270*mm, 145*mm, 32*mm, 20*mm, "V-501", "FLARE KO DRUM\nH=3m  D=1.2m")
    pipe(c, 286*mm, 145*mm, 350*mm, 155*mm, 2)
    tag_label(c, 295*mm, 150*mm, '8"-FG-5001  VAPOUR TO FLARE', 6.5)
    instrument(c, 270*mm, 168*mm, "LI-501"); dashed_pipe(c, 270*mm, 163*mm, 270*mm, 155*mm)
    instrument(c, 290*mm, 168*mm, "PI-501"); dashed_pipe(c, 290*mm, 163*mm, 290*mm, 155*mm)

    # KO drum liquid leg — pump-out
    pump(c, 270*mm, 112*mm, "P-501")
    pipe(c, 270*mm, 135*mm, 270*mm, 118*mm)
    pipe(c, 270*mm, 106*mm, 270*mm, 90*mm)
    tag_label(c, 272*mm, 85*mm, "TO SLOP TANK\nTK-501", 6.5)
    control_valve(c, 270*mm, 95*mm, "LCV-501")
    instrument(c, 283*mm, 108*mm, "LIC-501"); dashed_pipe(c, 278*mm, 103*mm, 275*mm, 100*mm)

    # HP relief header (from CDU, HDS, etc.)
    pipe(c, 30*mm, 145*mm, 254*mm, 145*mm, 2)
    tag_label(c, 35*mm, 148*mm, "HP RELIEF HEADER  — 8\"-RH-HP-5001", 7)

    # Individual relief valve feeds
    rv_feeds = [
        (70*mm,  "PSV-101\nV-101 OVHD"),
        (120*mm, "PSV-201\nE-201 SH"),
        (170*mm, "PSV-301\nHP STM HDR"),
        (220*mm, "PSV-401\nP-103 DISC"),
    ]
    for xr, tag in rv_feeds:
        pipe(c, xr, 175*mm, xr, 145*mm)
        # relief valve symbol (spring loaded)
        c.setStrokeColor(C_VALVE); c.setFillColor(HexColor("#fff0f0")); c.setLineWidth(1)
        c.rect(xr-4*mm, 175*mm, 8*mm, 8*mm, fill=1)
        c.setLineWidth(0.8); c.line(xr-4*mm, 183*mm, xr+4*mm, 179*mm)
        c.setFillColor(C_VALVE); c.setFont("Helvetica-Bold", 5.5)
        line1, line2 = tag.split("\n")
        c.drawCentredString(xr, 188*mm, line1)
        c.drawCentredString(xr, 183*mm, line2)
        pipe(c, xr, 193*mm, xr, 210*mm)  # inlet from vessel/line

    # Purge nitrogen to flare header
    pipe(c, 30*mm, 160*mm, 60*mm, 160*mm)
    tag_label(c, 12*mm, 162*mm, "N₂ PURGE\n0.5 barg", 6.5)
    control_valve(c, 50*mm, 160*mm, "PCV-501")
    pipe(c, 55*mm, 160*mm, 55*mm, 145*mm)

    tag_label(c, 12*mm, 50*mm, "NOTES:", 8)
    notes = [
        "1. RELIEF VALVES SIZED PER API 520/521.  PSV SCHEDULE REF: SV-SCHED-001.",
        "2. FLARE KO DRUM SIZED FOR 10 MIN HOLDUP AT DESIGN RELIEF RATE.",
        "3. CONTINUOUS N₂ PURGE PREVENTS FLASHBACK — MIN FLOW 5 Nm³/h.",
        "4. LIQUID LEVEL IN KO DRUM: ALARM AT 40%, TRIP AT 70% (ESD-501).",
        "5. SYNTHETIC DOCUMENT — FOR HACKATHON DEMONSTRATION PURPOSES.",
    ]
    c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
    for i, n in enumerate(notes):
        c.drawString(12*mm, (44 - i*5)*mm, n)
    c.save(); print("  Generated: PID-05-Flare-Relief-System.pdf")

pid_05_flare()

# ════════════════════════════════════════════════════════════════════════════
# P&ID 06 — HDS Reactor Feed / Effluent Section
# ════════════════════════════════════════════════════════════════════════════
def pid_06_hds_reactor():
    c = new_canvas("PID-06-HDS-Reactor-Feed-Effluent.pdf")
    title_block(c, "PID-HDS-006", "HYDRODESULPHURISATION UNIT — REACTOR FEED & EFFLUENT")

    # Feed surge drum
    vessel(c, 55*mm, 165*mm, 22*mm, 28*mm, "V-601", "FEED SURGE DRUM\nD=1.0m  L=3m")
    instrument(c, 55*mm, 188*mm, "LIC-601"); dashed_pipe(c, 55*mm, 183*mm, 55*mm, 179*mm)

    # Charge pump
    pump(c, 55*mm, 128*mm, "P-601A")
    pump(c, 80*mm, 128*mm, "P-601B")
    pipe(c, 55*mm, 151*mm, 55*mm, 134*mm)
    pipe(c, 55*mm, 122*mm, 55*mm, 105*mm)

    # Recycle hydrogen compressor
    vessel(c, 130*mm, 128*mm, 20*mm, 18*mm, "K-601", "H₂ RECYCLE\nCOMPRESSOR")
    pipe(c, 55*mm, 105*mm, 120*mm, 105*mm)
    pipe(c, 120*mm, 105*mm, 120*mm, 128*mm)
    pipe(c, 140*mm, 128*mm, 160*mm, 128*mm)
    tag_label(c, 60*mm, 107*mm, '3"-LGO-6001', 6)
    instrument(c, 90*mm, 115*mm, "FIC-601"); dashed_pipe(c, 90*mm, 110*mm, 90*mm, 105*mm)
    control_valve(c, 105*mm, 105*mm, "FCV-601")

    # Mix point and reactor feed furnace
    pipe(c, 160*mm, 128*mm, 185*mm, 128*mm)
    tag_label(c, 162*mm, 131*mm, "COMBINED FEED", 6.5)
    vessel(c, 205*mm, 128*mm, 22*mm, 16*mm, "F-601", "REACTOR\nFURNACE")
    pipe(c, 216*mm, 128*mm, 240*mm, 128*mm)
    instrument(c, 228*mm, 141*mm, "TIC-601"); dashed_pipe(c, 228*mm, 136*mm, 228*mm, 128*mm)

    # HDS Reactor
    vessel(c, 285*mm, 148*mm, 26*mm, 55*mm, "R-601", "HDS REACTOR\nCat: Co-Mo/Al₂O₃\n330°C  40 barg")
    pipe(c, 240*mm, 128*mm, 272*mm, 128*mm)
    pipe(c, 272*mm, 128*mm, 272*mm, 158*mm)
    pipe(c, 272*mm, 158*mm, 272*mm, 148*mm)  # reactor inlet nozzle
    instrument(c, 285*mm, 193*mm, "TI-605"); dashed_pipe(c, 285*mm, 188*mm, 285*mm, 175*mm)
    instrument(c, 300*mm, 183*mm, "TI-606"); dashed_pipe(c, 298*mm, 180*mm, 298*mm, 175*mm)
    instrument(c, 285*mm, 208*mm, "PI-601"); dashed_pipe(c, 285*mm, 203*mm, 285*mm, 175*mm)

    # Reactor effluent
    pipe(c, 298*mm, 148*mm, 340*mm, 148*mm, 2)
    tag_label(c, 305*mm, 151*mm, '6"-PE-6002  EFFLUENT TO E-601', 6.5)
    heat_exchanger(c, 360*mm, 148*mm, "E-601", "FEED/EFFLUENT")
    instrument(c, 342*mm, 160*mm, "TI-610"); dashed_pipe(c, 342*mm, 154*mm, 342*mm, 148*mm)

    # H₂S scrubber
    vessel(c, 370*mm, 100*mm, 22*mm, 32*mm, "V-602", "H₂S ABSORBER\nAmine Wash")
    pipe(c, 371*mm, 148*mm, 371*mm, 116*mm)

    tag_label(c, 12*mm, 50*mm, "NOTES:", 8)
    notes = [
        "1. REACTOR DESIGN: 50 barg, 400°C.  OPERATING: 40 barg, 330°C.",
        "2. H₂ PURITY TO REACTOR: MIN 85 mol%.  MAKEUP H₂ FROM REFORMER — REF PID-07.",
        "3. CATALYST: Co-Mo/Al₂O₃.  REGENERATION INTERVAL: 2 YEARS TYP.",
        "4. QUENCH H₂ INJECTION BETWEEN BED 1 AND BED 2 — REF PID-06A.",
        "5. SYNTHETIC DOCUMENT — FOR HACKATHON DEMONSTRATION PURPOSES.",
    ]
    c.setFont("Helvetica", 6.5); c.setFillColor(C_ANNOT)
    for i, n in enumerate(notes):
        c.drawString(12*mm, (44 - i*5)*mm, n)
    c.save(); print("  Generated: PID-06-HDS-Reactor-Feed-Effluent.pdf")

pid_06_hds_reactor()

# ════════════════════════════════════════════════════════════════════════════
# P&IDs 07-12 — Compact versions (each a focused sub-system)
# ════════════════════════════════════════════════════════════════════════════
def pid_compact(filename, dwg_no, title, systems):
    """
    Generic compact P&ID generator.
    systems: list of dicts describing vessels/pumps/instruments to draw
    """
    c = new_canvas(filename)
    title_block(c, dwg_no, title)

    y_base = 160*mm
    x_cur  = 50*mm

    for sys in systems:
        t = sys["type"]
        x, y = sys.get("x", x_cur), sys.get("y", y_base)

        if t == "vessel":
            vessel(c, x, y, sys.get("w", 24*mm), sys.get("h", 30*mm), sys["tag"], sys.get("desc", ""))
        elif t == "pump":
            pump(c, x, y, sys["tag"])
        elif t == "hex":
            heat_exchanger(c, x, y, sys["tag"], sys.get("desc",""))
        elif t == "inst":
            instrument(c, x, y, sys["tag"])
            if "from" in sys:
                dashed_pipe(c, sys["from"][0], sys["from"][1], x, y)
        elif t == "cv":
            control_valve(c, x, y, sys["tag"])
        elif t == "pipe":
            pipe(c, sys["x1"], sys["y1"], sys["x2"], sys["y2"], sys.get("lw", 1.5))
        elif t == "label":
            tag_label(c, x, y, sys["text"], sys.get("size", 7))

    tag_label(c, 12*mm, 20*mm, "SYNTHETIC DOCUMENT — GENERATED FOR HACKATHON DEMONSTRATION. NOT FOR CONSTRUCTION.", 7)
    c.save(); print(f"  Generated: {filename}")


# P&ID 07 — Instrument Air System
pid_compact("PID-07-Instrument-Air-System.pdf", "PID-UT-007", "INSTRUMENT AIR SYSTEM — GENERATION & DISTRIBUTION", [
    {"type":"vessel","x":60*mm, "y":170*mm, "w":20*mm,"h":28*mm,"tag":"K-701A","desc":"AIR COMPRESSOR\n7 barg 50 Nm³/h"},
    {"type":"vessel","x":90*mm, "y":170*mm, "w":20*mm,"h":28*mm,"tag":"K-701B","desc":"AIR COMPRESSOR\nSTANDBY"},
    {"type":"vessel","x":60*mm, "y":120*mm, "w":22*mm,"h":18*mm,"tag":"D-701", "desc":"AIR RECEIVER\n2.0 m³  8 barg"},
    {"type":"vessel","x":110*mm,"y":120*mm, "w":22*mm,"h":18*mm,"tag":"D-702", "desc":"AIR DRYER\nDew Pt -40°C"},
    {"type":"pipe","x1":60*mm,"y1":156*mm,"x2":60*mm,"y2":129*mm},
    {"type":"pipe","x1":60*mm,"y1":111*mm,"x2":110*mm,"y2":111*mm},
    {"type":"inst","x":75*mm,"y":145*mm,"tag":"PI-701","from":(68*mm,140*mm)},
    {"type":"inst","x":95*mm,"y":100*mm,"tag":"PI-702","from":(100*mm,110*mm)},
    {"type":"inst","x":125*mm,"y":100*mm,"tag":"TI-701","from":(118*mm,110*mm)},
    {"type":"pipe","x1":121*mm,"y1":120*mm,"x2":200*mm,"y2":120*mm},
    {"type":"label","x":130*mm,"y":123*mm,"text":"IA DIST. HEADER  7 barg  — 2\"-IA-7001"},
    {"type":"inst","x":150*mm,"y":133*mm,"tag":"PI-703","from":(150*mm,128*mm)},
    {"type":"label","x":12*mm,"y":80*mm,"text":"HEADER FEEDS: CDU CONTROL VALVES / HDS UNIT / FLARE PILOTS / UTILITY STATIONS"},
])

# P&ID 08 — Nitrogen Blanket System
pid_compact("PID-08-Nitrogen-Blanket-System.pdf", "PID-UT-008", "NITROGEN BLANKET SYSTEM — TANK AND VESSEL BLANKETING", [
    {"type":"vessel","x":60*mm, "y":175*mm,"w":18*mm,"h":24*mm,"tag":"V-801","desc":"N₂ BUFFER VESSEL\n10 barg 1.5 m³"},
    {"type":"vessel","x":150*mm,"y":175*mm,"w":22*mm,"h":20*mm,"tag":"TK-101","desc":"CRUDE TANK\nFLOATING ROOF"},
    {"type":"vessel","x":250*mm,"y":175*mm,"w":22*mm,"h":20*mm,"tag":"TK-102","desc":"NAPHTHA TANK\nFIXED ROOF"},
    {"type":"vessel","x":350*mm,"y":175*mm,"w":22*mm,"h":20*mm,"tag":"TK-103","desc":"KERO TANK\nFIXED ROOF"},
    {"type":"pipe","x1":69*mm,"y1":175*mm,"x2":380*mm,"y2":175*mm},
    {"type":"label","x":75*mm,"y":178*mm,"text":"N₂ BLANKET HEADER  0.03-0.05 barg  — 1½\"-NB-8001"},
    {"type":"cv","x":130*mm,"y":175*mm,"tag":"PCV-801"},
    {"type":"cv","x":230*mm,"y":175*mm,"tag":"PCV-802"},
    {"type":"cv","x":330*mm,"y":175*mm,"tag":"PCV-803"},
    {"type":"inst","x":150*mm,"y":160*mm,"tag":"PI-801","from":(150*mm,165*mm)},
    {"type":"inst","x":250*mm,"y":160*mm,"tag":"PI-802","from":(250*mm,165*mm)},
    {"type":"inst","x":350*mm,"y":160*mm,"tag":"PI-803","from":(350*mm,165*mm)},
    {"type":"label","x":12*mm,"y":80*mm,"text":"N₂ SUPPLY: ONSITE PSA UNIT OR BULK LIQUID NITROGEN — MIN PURITY 99.9 vol%."},
])

# P&ID 09 — Crude Storage / Tank Farm
pid_compact("PID-09-Tank-Farm-Crude-Storage.pdf", "PID-TF-009", "TANK FARM — CRUDE OIL RECEIVING & STORAGE", [
    {"type":"vessel","x":80*mm, "y":165*mm,"w":35*mm,"h":45*mm,"tag":"TK-001","desc":"CRUDE STORAGE\n50,000 m³\nFLOATING ROOF"},
    {"type":"vessel","x":180*mm,"y":165*mm,"w":35*mm,"h":45*mm,"tag":"TK-002","desc":"CRUDE STORAGE\n50,000 m³\nFLOATING ROOF"},
    {"type":"vessel","x":280*mm,"y":165*mm,"w":22*mm,"h":30*mm,"tag":"TK-003","desc":"SLOP TANK\n5,000 m³"},
    {"type":"pump","x":80*mm,"y":108*mm,"tag":"P-001A"},
    {"type":"pump","x":105*mm,"y":108*mm,"tag":"P-001B"},
    {"type":"pipe","x1":80*mm,"y1":142*mm,"x2":80*mm,"y2":114*mm},
    {"type":"pipe","x1":80*mm,"y1":102*mm,"x2":80*mm,"y2":85*mm},
    {"type":"pipe","x1":80*mm,"y1":85*mm,"x2":350*mm,"y2":85*mm},
    {"type":"label","x":85*mm,"y":88*mm,"text":"CRUDE TRANSFER HEADER — 16\"-CR-0001  TO CDU FEED SECTION (REF PID-01)"},
    {"type":"inst","x":130*mm,"y":95*mm,"tag":"FIC-001","from":(130*mm,85*mm)},
    {"type":"cv","x":150*mm,"y":85*mm,"tag":"FCV-001"},
    {"type":"inst","x":80*mm,"y":130*mm,"tag":"LI-001","from":(63*mm,155*mm)},
    {"type":"inst","x":180*mm,"y":130*mm,"tag":"LI-002","from":(163*mm,155*mm)},
    {"type":"label","x":12*mm,"y":60*mm,"text":"TANK PROTECTION: FOAM SYSTEM PER OISD STD-117.  DYKE VOLUME: 110% LARGEST TANK."},
])

# P&ID 10 — Produced Water Treatment
pid_compact("PID-10-Produced-Water-Treatment.pdf", "PID-WT-010", "PRODUCED WATER TREATMENT — API SEPARATOR & DAF", [
    {"type":"vessel","x":70*mm,"y":165*mm,"w":45*mm,"h":22*mm,"tag":"S-1001","desc":"API OIL-WATER SEPARATOR\nL=12m  W=4m"},
    {"type":"vessel","x":200*mm,"y":165*mm,"w":40*mm,"h":20*mm,"tag":"T-1001","desc":"DAF UNIT\nDISSO. AIR FLOTATION"},
    {"type":"vessel","x":330*mm,"y":165*mm,"w":30*mm,"h":28*mm,"tag":"T-1002","desc":"EQUALI- SATION\nTANK"},
    {"type":"pipe","x1":30*mm,"y1":165*mm,"x2":47*mm,"y2":165*mm},
    {"type":"label","x":12*mm,"y":168*mm,"text":"OILY WATER IN"},
    {"type":"pipe","x1":92*mm,"y1":165*mm,"x2":180*mm,"y2":165*mm},
    {"type":"pipe","x1":220*mm,"y1":165*mm,"x2":315*mm,"y2":165*mm},
    {"type":"inst","x":120*mm,"y":178*mm,"tag":"FI-1001","from":(120*mm,165*mm)},
    {"type":"inst","x":270*mm,"y":178*mm,"tag":"TI-1001","from":(270*mm,165*mm)},
    {"type":"inst","x":200*mm,"y":150*mm,"tag":"LI-1001","from":(185*mm,155*mm)},
    {"type":"label","x":12*mm,"y":80*mm,"text":"EFFLUENT QUALITY TARGET: OIL <15 ppm, TSS <30 ppm.  DISCHARGE PER MARPOL / CPCB NORMS."},
])

# P&ID 11 — Fire Water System
pid_compact("PID-11-Fire-Water-System.pdf", "PID-FW-011", "FIRE WATER SYSTEM — PUMP HOUSE & RING MAIN", [
    {"type":"vessel","x":60*mm,"y":175*mm,"w":22*mm,"h":25*mm,"tag":"TK-FW","desc":"FIRE WATER\nSTORAGE 1000 m³"},
    {"type":"pump","x":60*mm,"y":130*mm,"tag":"P-FW-A"},
    {"type":"pump","x":85*mm,"y":130*mm,"tag":"P-FW-B"},
    {"type":"pump","x":110*mm,"y":130*mm,"tag":"P-FW-D"},
    {"type":"label","x":40*mm,"y":118*mm,"text":"ELECTRIC (2×) + DIESEL JOCKEY PUMP"},
    {"type":"pipe","x1":60*mm,"y1":150*mm,"x2":60*mm,"y2":136*mm},
    {"type":"pipe","x1":60*mm,"y1":124*mm,"x2":60*mm,"y2":105*mm},
    {"type":"pipe","x1":60*mm,"y1":105*mm,"x2":380*mm,"y2":105*mm},
    {"type":"label","x":65*mm,"y":108*mm,"text":"FIRE WATER RING MAIN  10 barg  — 10\"-FW-1001"},
    {"type":"inst","x":90*mm,"y":95*mm,"tag":"PI-FW1","from":(90*mm,100*mm)},
    {"type":"inst","x":180*mm,"y":95*mm,"tag":"PI-FW2","from":(180*mm,100*mm)},
    {"type":"inst","x":280*mm,"y":95*mm,"tag":"PI-FW3","from":(280*mm,100*mm)},
    {"type":"label","x":12*mm,"y":70*mm,"text":"HYDRANT OFFTAKES AT 45m INTERVALS PER OISD STD-116.  MONITOR NOZZLE AT TANK BUND CORNERS."},
])

# P&ID 12 — Drain & Blow-down System
pid_compact("PID-12-Drain-Blowdown-System.pdf", "PID-UT-012", "CLOSED DRAIN & BLOWDOWN SYSTEM", [
    {"type":"vessel","x":200*mm,"y":165*mm,"w":30*mm,"h":35*mm,"tag":"V-1201","desc":"CLOSED DRAIN\nDRUM  5 m³"},
    {"type":"vessel","x":320*mm,"y":165*mm,"w":28*mm,"h":30*mm,"tag":"V-1202","desc":"BLOWDOWN\nDRUM  3 m³"},
    {"type":"pump","x":200*mm,"y":118*mm,"tag":"P-1201"},
    {"type":"pump","x":320*mm,"y":118*mm,"tag":"P-1202"},
    {"type":"pipe","x1":200*mm,"y1":147*mm,"x2":200*mm,"y2":124*mm},
    {"type":"pipe","x1":200*mm,"y1":112*mm,"x2":200*mm,"y2":95*mm},
    {"type":"label","x":205*mm,"y":90*mm,"text":"TO SLOP TK-003"},
    {"type":"pipe","x1":30*mm,"y1":165*mm,"x2":185*mm,"y2":165*mm},
    {"type":"label","x":35*mm,"y":168*mm,"text":"CLOSED DRAIN HEADER — 4\"-CD-1201  (GRAVITY FLOW)"},
    {"type":"pipe","x1":30*mm,"y1":145*mm,"x2":305*mm,"y2":145*mm},
    {"type":"label","x":35*mm,"y":148*mm,"text":"BLOWDOWN HEADER — 4\"-BD-1202"},
    {"type":"inst","x":200*mm,"y":188*mm,"tag":"LI-1201","from":(188*mm,178*mm)},
    {"type":"inst","x":320*mm,"y":188*mm,"tag":"LI-1202","from":(308*mm,178*mm)},
    {"type":"inst","x":200*mm,"y":200*mm,"tag":"PI-1201","from":(210*mm,178*mm)},
    {"type":"label","x":12*mm,"y":70*mm,"text":"CLOSED DRAIN SYSTEM UNDER N₂ BLANKET.  VENT TO FLARE — REF PID-05.  NO OPEN DRAIN CONNECTIONS."},
])

print("\nAll 12 P&IDs generated successfully.")
