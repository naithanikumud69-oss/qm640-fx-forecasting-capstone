# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image as PILImage
import os

PAGE_W, PAGE_H = 13.333 * inch, 7.5 * inch
ASSETS = "assets"

NAVY = HexColor("#0B2E4F")
NAVY_DK = HexColor("#071E36")
TEAL = HexColor("#1C7293")
GOLD = HexColor("#C8963E")
SLATE = HexColor("#5C6B7A")
LIGHT_BG = HexColor("#F7F9FB")
CARD_BG = HexColor("#FFFFFF")
DARK_TEXT = HexColor("#16213E")
MUTED = HexColor("#7A8699")
GOOD = HexColor("#2C7A4B")
WARN = HexColor("#B8863B")

F_BOLD = "Helvetica-Bold"
F_REG = "Helvetica"
F_IT = "Helvetica-Oblique"
F_BOLD_IT = "Helvetica-BoldOblique"

MARGIN_X = 0.65 * inch
TITLE_BAND_H = 1.25 * inch
FOOTER_Y = 0.32 * inch

c = canvas.Canvas("QM640_Final_Presentation_Group8.pdf", pagesize=(PAGE_W, PAGE_H))
SLIDE_NUM = [1]  # slide 1 is the title page (no footer drawn on it)
TOTAL_SLIDES = 14


def wrap_text(text, font, size, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if stringWidth(trial, font, size) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def footer(section_label):
    SLIDE_NUM[0] += 1
    c.setFont(F_REG, 9)
    c.setFillColor(MUTED)
    c.drawString(MARGIN_X, FOOTER_Y, "QM640 Data Analytics Capstone  |  Group 8  |  Kumud Naithani")
    c.drawRightString(PAGE_W - MARGIN_X, FOOTER_Y, f"{section_label}   ·   {SLIDE_NUM[0]} / {TOTAL_SLIDES}")


def title_band(kicker, title, band_color=NAVY, title_size=32):
    c.setFillColor(band_color)
    c.rect(0, PAGE_H - TITLE_BAND_H, PAGE_W, TITLE_BAND_H, stroke=0, fill=1)
    c.setFont(F_BOLD, 12)
    c.setFillColor(GOLD)
    spaced = " ".join(list(kicker.upper()))
    c.drawString(MARGIN_X, PAGE_H - 0.42 * inch, spaced)
    c.setFont(F_BOLD, title_size)
    c.setFillColor(white)
    c.drawString(MARGIN_X, PAGE_H - TITLE_BAND_H + 0.32 * inch, title)


def bg(color=LIGHT_BG):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def bullet_list(items, x, y_top, max_width, font=F_REG, size=17, leading=26, color=DARK_TEXT,
                 marker_color=TEAL, gap_after=10, bold_lead=None):
    y = y_top
    for item in items:
        lead = ""
        text = item
        if isinstance(item, tuple):
            lead, text = item
        c.setFillColor(marker_color)
        c.circle(x + 4, y - size * 0.32, 3.2, stroke=0, fill=1)
        tx = x + 18
        avail = max_width - 18
        if lead:
            lw = stringWidth(lead + "  ", F_BOLD, size)
            c.setFont(F_BOLD, size)
            c.setFillColor(NAVY)
            c.drawString(tx, y, lead)
            lines = wrap_text(text, font, size, avail - lw)
            c.setFont(font, size)
            c.setFillColor(color)
            if lines:
                c.drawString(tx + lw, y, lines[0])
                for extra in lines[1:]:
                    y -= leading
                    c.drawString(tx, y, extra)
        else:
            lines = wrap_text(text, font, size, avail)
            c.setFont(font, size)
            c.setFillColor(color)
            for li in lines:
                c.drawString(tx, y, li)
                if li != lines[-1]:
                    y -= leading
        y -= (leading + gap_after)
    return y


def draw_image_fit(path, x, y, max_w, max_h, align="center"):
    with PILImage.open(os.path.join(ASSETS, path)) as im:
        iw, ih = im.size
    aspect = ih / iw
    w = max_w
    h = w * aspect
    if h > max_h:
        h = max_h
        w = h / aspect
    if align == "center":
        x = x + (max_w - w) / 2
    c.drawImage(os.path.join(ASSETS, path), x, y + (max_h - h), width=w, height=h,
                preserveAspectRatio=True, mask="auto")
    return w, h


def card(x, y, w, h, color=CARD_BG, radius=8, border=None):
    c.setFillColor(color)
    if border:
        c.setStrokeColor(border)
        c.setLineWidth(1)
        c.roundRect(x, y, w, h, radius, stroke=1, fill=1)
    else:
        c.roundRect(x, y, w, h, radius, stroke=0, fill=1)


def stat_card(x, y, w, h, number, label, color=NAVY, num_size=30, label_size=11):
    card(x, y, w, h, color=CARD_BG, border=HexColor("#E1E7ED"))
    c.setFont(F_BOLD, num_size)
    c.setFillColor(color)
    c.drawCentredString(x + w / 2, y + h * 0.52, number)
    c.setFont(F_REG, label_size)
    c.setFillColor(SLATE)
    lines = []
    for seg in label.split("\n"):
        lines.extend(wrap_text(seg, F_REG, label_size, w - 14))
    ly = y + h * 0.30
    for ln in lines:
        c.drawCentredString(x + w / 2, ly, ln)
        ly -= (label_size + 2)


def table_grid(x, y_top, col_widths, rows, header=True, row_h=0.42*inch, font_size=11,
               header_bg=NAVY, header_fg=white, zebra=HexColor("#EFF3F7")):
    total_w = sum(col_widths)
    y = y_top
    for ri, row in enumerate(rows):
        is_header = header and ri == 0
        rh = row_h * (1.15 if is_header else 1.0)
        if is_header:
            c.setFillColor(header_bg)
            c.rect(x, y - rh, total_w, rh, stroke=0, fill=1)
        elif zebra and ri % 2 == 0:
            c.setFillColor(zebra)
            c.rect(x, y - rh, total_w, rh, stroke=0, fill=1)
        cx = x
        for ci, cell in enumerate(row):
            cw = col_widths[ci]
            c.setFont(F_BOLD if is_header else F_REG, font_size + (1 if is_header else 0))
            c.setFillColor(header_fg if is_header else DARK_TEXT)
            lines = wrap_text(str(cell), F_BOLD if is_header else F_REG, font_size + (1 if is_header else 0), cw - 12)
            ty = y - rh/2 + (len(lines)-1)*(font_size+2)/2 + 3
            for ln in lines:
                c.drawString(cx + 8, ty, ln)
                ty -= (font_size + 2)
            cx += cw
        c.setStrokeColor(HexColor("#D7DEE6"))
        c.setLineWidth(0.6)
        c.line(x, y - rh, x + total_w, y - rh)
        y -= rh
    c.setStrokeColor(HexColor("#D7DEE6"))
    cx = x
    for cw in col_widths[:-1]:
        cx += cw
        c.line(cx, y_top, cx, y)
    c.rect(x, y, total_w, y_top - y, stroke=1, fill=0)
    return y


# ============================================================
# SLIDE 1: TITLE
# ============================================================
bg(NAVY)
c.setFillColor(GOLD)
c.setFont(F_BOLD, 13)
c.drawCentredString(PAGE_W/2, PAGE_H - 1.5*inch, "D A T A   A N A L Y T I C S   C A P S T O N E   ·   F I N A L   P R E S E N T A T I O N")
c.setFont(F_BOLD, 30)
c.setFillColor(white)
title_lines = [
    "Forecasting Short-Term Exchange Rate Movements",
    "and Volatility in Major Currency Pairs Using",
    "Macroeconomic Indicators and Machine Learning",
]
ty = PAGE_H - 2.35*inch
for ln in title_lines:
    c.drawCentredString(PAGE_W/2, ty, ln)
    ty -= 0.52*inch
c.setStrokeColor(TEAL)
c.setLineWidth(1.2)
c.line(PAGE_W/2 - 1.1*inch, ty - 0.05*inch, PAGE_W/2 + 1.1*inch, ty - 0.05*inch)
ty -= 0.55*inch
c.setFont(F_REG, 16)
c.setFillColor(HexColor("#CADCFC"))
c.drawCentredString(PAGE_W/2, ty, "Kumud Naithani  ·  Group 8")
ty -= 0.34*inch
c.setFont(F_IT, 13)
c.setFillColor(HexColor("#9FB4CC"))
c.drawCentredString(PAGE_W/2, ty, "Mentor: Abhay Poddar")
ty -= 0.5*inch
c.setFont(F_REG, 12)
c.setFillColor(HexColor("#7C93AC"))
c.drawCentredString(PAGE_W/2, ty, "Walsh College  ·  QM640: Data Analytics Capstone  ·  Fall 2026 Term")
c.showPage()

# ============================================================
# SLIDE 2: EXECUTIVE SUMMARY
# ============================================================
bg()
title_band("Executive Summary", "Executive Summary")
items = [
    ("Objective & Scope.", "Compare macroeconomic, machine-learning, sentiment, and policy-event approaches "
     "to forecasting short-term direction and volatility for USD/INR, EUR/USD, GBP/USD, and USD/JPY."),
    ("Why it matters.", "The FX market moves USD 7T+ daily; treasuries, traders, and importers/exporters need "
     "reliable short-term signals to hedge risk, yet the “Meese-Rogoff puzzle” shows this is genuinely hard."),
    ("Data.", "2,143 real daily observations per pair (2018-2026) from FRED, plus verified macro series "
     "(interest rates, inflation) across 4 economies — 8,572 pooled currency-day records."),
    ("Key results.", "RQ1 full 4-predictor model: R² reaches 12.4% for EUR/USD (3 of 4 coefficients "
     "significant), while USD/INR, GBP/USD, and USD/JPY stay non-significant (R² 3.5-5.0%). RQ2: "
     "walk-forward GARCH and Random Forest both beat a naive baseline by ~22-25%. RQ4: no significant "
     "average volatility spike, but a surprise-magnitude split shows the expected directional pattern."),
    ("Usage.", "Findings feed a practical early-warning dashboard for treasury teams, flagging elevated "
     "volatility risk ahead of scheduled policy announcements."),
]
y = PAGE_H - TITLE_BAND_H - 0.55*inch
bullet_list(items, MARGIN_X, y, PAGE_W - 2*MARGIN_X, size=16.5, leading=22, gap_after=14)
footer("Executive Summary")
c.showPage()

# ============================================================
# SLIDE 3: GAP ANALYSIS
# ============================================================
bg()
title_band("Gap Analysis", "Gap Analysis")
c.setFont(F_BOLD, 17)
c.setFillColor(NAVY)
c.drawString(MARGIN_X, PAGE_H - TITLE_BAND_H - 0.55*inch, "What the literature establishes")
lit_items = [
    "Meese & Rogoff (1983): structural macro models fail to beat a random walk short-term — the "
    "“Meese-Rogoff puzzle” that still motivates this field.",
    "Separate literatures address each piece: econometric volatility (Engle 1982; Bollerslev 1986), ML "
    "forecasting (Breiman 2001; Chen & Guestrin 2016; Hochreiter & Schmidhuber 1997), sentiment (Tetlock "
    "2007; Hutto & Gilbert 2014; Araci 2019), and policy surprises (Kuttner 2001).",
]
y = PAGE_H - TITLE_BAND_H - 0.85*inch
y = bullet_list(lit_items, MARGIN_X, y, PAGE_W - 2*MARGIN_X, size=15, leading=20, gap_after=10)
card(MARGIN_X, y - 1.55*inch, PAGE_W - 2*MARGIN_X, 1.55*inch, color=HexColor("#EFF3F7"))
c.setFont(F_BOLD, 15)
c.setFillColor(NAVY)
c.drawString(MARGIN_X + 0.3*inch, y - 0.42*inch, "The Gap")
c.setFont(F_REG, 14.5)
c.setFillColor(DARK_TEXT)
gap_text = ("No study evaluates macro-fundamental, ML, sentiment, and policy-event approaches together, "
            "on the same currency pairs — including an emerging-market pair (USD/INR) alongside major "
            "developed pairs — leaving practitioners without comparative evidence on which model family "
            "actually helps.")
lines = wrap_text(gap_text, F_REG, 14.5, PAGE_W - 2*MARGIN_X - 0.6*inch)
ly = y - 0.75*inch
for ln in lines:
    c.drawString(MARGIN_X + 0.3*inch, ly, ln)
    ly -= 20
footer("Gap Analysis")
c.showPage()

# ============================================================
# SLIDE 4: RESEARCH QUESTIONS I (RQ1, RQ2)
# ============================================================
bg()
title_band("Research Questions (1/2)", "Research Questions & Hypotheses")


def rq_card(x, y, w, h, tag, question, h0, ha, method, result, result_color):
    card(x, y, w, h, color=CARD_BG, border=HexColor("#E1E7ED"))
    c.setFillColor(NAVY)
    c.roundRect(x + 14, y + h - 34, 46, 22, 4, stroke=0, fill=1)
    c.setFont(F_BOLD, 12)
    c.setFillColor(white)
    c.drawCentredString(x + 37, y + h - 27, tag)
    c.setFont(F_BOLD, 12.5)
    c.setFillColor(DARK_TEXT)
    qlines = wrap_text(question, F_BOLD, 12.5, w - 90)
    qy = y + h - 26
    for ln in qlines:
        c.drawString(x + 72, qy, ln)
        qy -= 15
    yy = y + h - 34 - max(1, len(qlines)) * 15 - 12
    c.setFont(F_BOLD_IT, 10.5)
    c.setFillColor(SLATE)
    c.drawString(x + 14, yy, "H0:")
    h0lines = wrap_text(h0, F_REG, 10.5, w - 50)
    c.setFont(F_REG, 10.5)
    c.drawString(x + 40, yy, h0lines[0])
    yy -= 14
    for ln in h0lines[1:]:
        c.drawString(x + 14, yy, ln)
        yy -= 14
    yy -= 2
    c.setFont(F_BOLD_IT, 10.5)
    c.setFillColor(TEAL)
    c.drawString(x + 14, yy, "Ha:")
    c.setFont(F_REG, 10.5)
    c.setFillColor(SLATE)
    halines = wrap_text(ha, F_REG, 10.5, w - 50)
    c.drawString(x + 40, yy, halines[0])
    yy -= 14
    for ln in halines[1:]:
        c.drawString(x + 14, yy, ln)
        yy -= 14
    yy -= 8
    c.setStrokeColor(HexColor("#E1E7ED"))
    c.line(x + 14, yy, x + w - 14, yy)
    yy -= 16
    c.setFont(F_BOLD, 10.5)
    c.setFillColor(NAVY)
    c.drawString(x + 14, yy, "Method: ")
    c.setFont(F_REG, 10.5)
    c.setFillColor(DARK_TEXT)
    mlines = wrap_text(method, F_REG, 10.5, w - 90)
    c.drawString(x + 72, yy, mlines[0])
    yy -= 14
    for ln in mlines[1:]:
        c.drawString(x + 14, yy, ln)
        yy -= 14
    yy -= 4
    c.setFillColor(result_color)
    c.circle(x + 20, yy - 2, 3.5, stroke=0, fill=1)
    c.setFont(F_BOLD, 10.5)
    c.drawString(x + 32, yy, "Result: ")
    c.setFont(F_REG, 10.5)
    c.setFillColor(DARK_TEXT)
    rlines = wrap_text(result, F_REG, 10.5, w - 100)
    c.drawString(x + 88, yy, rlines[0])
    yy -= 14
    for ln in rlines[1:]:
        c.drawString(x + 14, yy, ln)
        yy -= 14


card_w = (PAGE_W - 2*MARGIN_X - 0.4*inch) / 2
card_h = 3.55*inch
card_y = PAGE_H - TITLE_BAND_H - 0.35*inch - card_h
rq_card(MARGIN_X, card_y, card_w, card_h, "RQ1",
        "Do macro indicators (rate & inflation differentials, trade balance, GDP growth) predict short-term FX direction?",
        "None of the macro predictors is significantly associated with directional movement.",
        "At least one predictor is significantly associated with directional movement.",
        "Full 4-predictor OLS + Random Forest robustness check, VIF-screened, 4 pairs",
        "Mixed. Reject H0 for EUR/USD (R²=12.4%, 3 predictors sig.); fail to reject for the other "
        "three pairs (R² 3.5-5.0%).",
        GOOD)
rq_card(MARGIN_X + card_w + 0.4*inch, card_y, card_w, card_h, "RQ2",
        "Do ML models (Random Forest) forecast volatility significantly better than GARCH(1,1)?",
        "ML forecast error is not significantly different from the GARCH baseline.",
        "ML achieves significantly lower forecast error than GARCH.",
        "GARCH(1,1) vs. Random Forest on lagged returns, walk-forward re-estimation, paired-loss t-test",
        "Fail to reject H0 (p = 0.78). Walk-forward GARCH RMSE 0.231 vs. RF 0.227 — both beat the naive "
        "baseline (0.298) by ~22-25%.",
        WARN)
note_y = card_y - 0.55*inch
note_w = PAGE_W - 2*MARGIN_X
c.setFillColor(HexColor("#EFF3F7"))
c.roundRect(MARGIN_X, note_y - 0.62*inch, note_w, 0.62*inch, 6, stroke=0, fill=1)
c.setFont(F_BOLD_IT, 12.5)
c.setFillColor(NAVY)
note1_lines = wrap_text("RQ1 is no longer a clean null — EUR/USD rejects H0 while the other three pairs "
                         "don't. RQ2 still fails to reject, but cuts real forecast error by ~22-25% vs. "
                         "naive (see Results).", F_BOLD_IT, 12.5, note_w - 0.4*inch)
n1y = note_y - 0.24*inch
for ln in note1_lines:
    c.drawString(MARGIN_X + 0.2*inch, n1y, ln)
    n1y -= 16
footer("Research Questions")
c.showPage()

# (placeholder marker retained)
# ============================================================
# SLIDE 5: RESEARCH QUESTIONS II (RQ3, RQ4)
# ============================================================
bg()
title_band("Research Questions (2/2)", "Research Questions & Hypotheses")
card_y2 = PAGE_H - TITLE_BAND_H - 0.35*inch - card_h
rq_card(MARGIN_X, card_y2, card_w, card_h, "RQ3",
        "Does financial-news sentiment (GDELT/VADER/FinBERT) improve directional accuracy beyond macro indicators?",
        "Adding sentiment does not significantly improve directional accuracy.",
        "Adding sentiment improves directional accuracy by ≥ 5 points.",
        "VADER + FinBERT sentiment index added to best RQ2 model, McNemar's test (planned)",
        "In progress. Architecture defined; GDELT collection is the critical remaining data-engineering step.",
        SLATE)
rq_card(MARGIN_X + card_w + 0.4*inch, card_y2, card_w, card_h, "RQ4",
        "Do FOMC policy announcements cause a significant spike in USD/INR volatility?",
        "Post-announcement volatility is not significantly different from the pre-announcement baseline.",
        "Post-announcement volatility is significantly higher.",
        "Event study: 71 real FOMC dates (2018-2026), paired t-test on |return|, days -10..-6 vs. 0..+1; "
        "split by |3-month T-bill yield change| as a surprise-size proxy",
        "Fail to reject H0 overall (p=.84). High-surprise half: +2.2% post-jump; low-surprise half: "
        "-6.3% — right direction, underpowered at n=36/35.",
        WARN)
note_y2 = card_y2 - 0.55*inch
note_w2 = PAGE_W - 2*MARGIN_X
c.setFillColor(HexColor("#EFF3F7"))
c.roundRect(MARGIN_X, note_y2 - 0.62*inch, note_w2, 0.62*inch, 6, stroke=0, fill=1)
c.setFont(F_BOLD_IT, 12.5)
c.setFillColor(NAVY)
note2_lines = wrap_text("RQ3 is the one open thread (sentiment pipeline in progress); RQ4's surprise-size "
                         "split (see Results) points the right way but needs more data to confirm.",
                         F_BOLD_IT, 12.5, note_w2 - 0.4*inch)
n2y = note_y2 - 0.24*inch
for ln in note2_lines:
    c.drawString(MARGIN_X + 0.2*inch, n2y, ln)
    n2y -= 16
footer("Research Questions")
c.showPage()

# ============================================================
# SLIDE 6: DATA DESCRIPTION & EDA
# ============================================================
bg()
title_band("Data Description & EDA", "Data Description & EDA")
top_y = PAGE_H - TITLE_BAND_H - 0.3*inch

# --- Left column: indexed-levels chart ---
img_w = 5.35*inch
chart1_h = 2.5*inch
draw_image_fit("fig_indexed.png", MARGIN_X, top_y - chart1_h, img_w, chart1_h)
c.setFont(F_IT, 10)
c.setFillColor(MUTED)
c.drawCentredString(MARGIN_X + img_w/2, top_y - chart1_h - 0.20*inch, "Indexed FX levels, 4 pairs, 2018-2026 (source: FRED)")

# --- Right column: stat cards + headline (budgeted to end above row 2) ---
stats_x = MARGIN_X + img_w + 0.35*inch
stats_w = PAGE_W - MARGIN_X - stats_x
sc_w = (stats_w - 0.2*inch) / 2
sc_h = 0.8*inch
row1_y = top_y - sc_h
row2_y = row1_y - sc_h - 0.15*inch
stat_card(stats_x, row1_y, sc_w, sc_h, "8,572", "pooled currency-day observations")
stat_card(stats_x + sc_w + 0.2*inch, row1_y, sc_w, sc_h, "2018-26", "8+ years, all non-Kaggle sources")
stat_card(stats_x, row2_y, sc_w, sc_h, "5.0-8.9%", "annualized volatility range")
stat_card(stats_x + sc_w + 0.2*inch, row2_y, sc_w, sc_h, "4.3%", "missing data (structural)")

c.setFont(F_BOLD, 12.5)
c.setFillColor(NAVY)
ny = row2_y - 0.32*inch
c.drawString(stats_x, ny, "EDA headline:")
c.setFont(F_REG, 11.5)
c.setFillColor(DARK_TEXT)
insight = ("All four pairs show excess kurtosis (fat tails), motivating GARCH over "
           "constant-variance models for RQ2.")
lines = wrap_text(insight, F_REG, 11.5, stats_w)
ny -= 19
for ln in lines:
    c.drawString(stats_x, ny, ln)
    ny -= 15.5

# --- Row 2: four-panel return-distribution histogram, full width ---
row2_top = 3.05*inch
hist_h = 2.2*inch
draw_image_fit("fig_hist4.png", MARGIN_X, row2_top - hist_h, PAGE_W - 2*MARGIN_X, hist_h)
c.setFont(F_IT, 10)
c.setFillColor(MUTED)
c.drawCentredString(PAGE_W/2, row2_top - hist_h - 0.18*inch, "Daily log-return distributions, all 4 pairs — fat tails visible in every panel")
footer("Data Description & EDA")
c.showPage()

# ============================================================
# SLIDE 7: ARCHITECTURE / WORKFLOW
# ============================================================
bg()
title_band("Architecture & Workflow", "Architecture Diagram / Workflow")
stages = [
    ("1", "Data Sources", "FRED, RBI DBIE, ECB\nSDW, BoE, IMF IFS,\nWorld Bank, GDELT"),
    ("2", "Clean & Engineer", "Drop non-trading gaps,\nlog returns, rate/inflation\ndifferentials, VIF checks"),
    ("3", "Model per RQ", "RQ1 OLS+RF · RQ2\nGARCH+RF · RQ3 VADER/\nFinBERT · RQ4 Event study"),
    ("4", "Evaluate", "R², RMSE, paired t-test /\nWilcoxon, Diebold-Mariano,\nMcNemar's test"),
    ("5", "Recommend", "Early-warning dashboard\nfor treasury & trading\ndecisions"),
]
n = len(stages)
top_y = PAGE_H - TITLE_BAND_H - 0.75*inch
box_w = 1.95*inch
box_h = 2.55*inch
gap = (PAGE_W - 2*MARGIN_X - n*box_w) / (n - 1)
colors_cycle = [NAVY, TEAL, GOLD, TEAL, NAVY]
for i, (num, head, desc) in enumerate(stages):
    x = MARGIN_X + i * (box_w + gap)
    y = top_y - box_h
    card(x, y, box_w, box_h, color=CARD_BG, border=HexColor("#E1E7ED"))
    c.setFillColor(colors_cycle[i])
    c.circle(x + box_w/2, y + box_h - 0.42*inch, 0.26*inch, stroke=0, fill=1)
    c.setFont(F_BOLD, 15)
    c.setFillColor(white)
    c.drawCentredString(x + box_w/2, y + box_h - 0.42*inch - 5, num)
    c.setFont(F_BOLD, 12.5)
    c.setFillColor(NAVY)
    c.drawCentredString(x + box_w/2, y + box_h - 0.85*inch, head)
    c.setFont(F_REG, 10)
    c.setFillColor(SLATE)
    dy = y + box_h - 1.15*inch
    for ln in desc.split("\n"):
        c.drawCentredString(x + box_w/2, dy, ln)
        dy -= 13
    if i < n - 1:
        ax = x + box_w + gap/2
        ay = y + box_h/2
        c.setFillColor(GOLD)
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.line(x + box_w + 4, ay, x + box_w + gap - 8, ay)
        c.line(x + box_w + gap - 8, ay, x + box_w + gap - 14, ay + 5)
        c.line(x + box_w + gap - 8, ay, x + box_w + gap - 14, ay - 5)

legend_y = top_y - box_h - 0.45*inch
c.setFont(F_BOLD, 11.5)
c.setFillColor(NAVY)
c.drawString(MARGIN_X, legend_y, "Legend:")
c.setFont(F_REG, 11)
c.setFillColor(DARK_TEXT)
c.drawString(MARGIN_X + 0.75*inch, legend_y,
             "Sequential pipeline, left to right. Each stage's output feeds the next; RQ1-RQ4 run in parallel within Stage 3 "
             "using a shared, cleaned data foundation from Stage 2.")
footer("Architecture Diagram / Workflow")
c.showPage()

# ============================================================
# SLIDE 8: MODEL BUILDING
# ============================================================
bg()
title_band("Model Building", "Model Building")
rows = [
    ["RQ", "Baseline / Comparator", "Justification"],
    ["RQ1", "OLS (linear) vs. Random Forest (nonlinear check)", "Tests the linear UIP/PPP relationship directly; RF checks for nonlinearity theory may miss. VIF-screened for multicollinearity."],
    ["RQ2", "GARCH(1,1) vs. Random Forest (5 lagged returns)", "GARCH is the finance-standard volatility-clustering model; RF tests whether nonlinear ML adds value over it."],
    ["RQ3", "Best RQ2 model vs. + VADER/FinBERT sentiment", "Isolates the incremental value of news sentiment, holding the base model fixed (planned)."],
    ["RQ4", "Pre- vs. post-announcement paired comparison", "Standard event-study design; mirrors Kuttner (2001)'s framework for policy-surprise effects."],
]
col_w = [0.7*inch, 3.5*inch, PAGE_W - 2*MARGIN_X - 0.7*inch - 3.5*inch]
y0 = PAGE_H - TITLE_BAND_H - 0.4*inch
table_grid(MARGIN_X, y0, col_w, rows, row_h=0.62*inch, font_size=11.5)

c.setFont(F_BOLD, 13.5)
c.setFillColor(NAVY)
ny = y0 - 0.62*inch*4.6 - 0.35*inch
c.drawString(MARGIN_X, ny, "Rigor built into every model:")
rigor = [
    "5-fold CV (RQ1) and time-series CV with no shuffling (RQ2) to prevent look-ahead leakage",
    "80/20 train-test split; GARCH walk-forward refitting (no look-ahead) rather than a single in-sample fit",
    "RMSE, R-squared, and paired-loss t-tests for honest comparison; VIF < 10 threshold for RQ1 predictors",
]
bullet_list(rigor, MARGIN_X, ny - 0.35*inch, PAGE_W - 2*MARGIN_X, size=13, leading=17, gap_after=8, marker_color=GOLD)
footer("Model Building")
c.showPage()

# ============================================================
# SLIDE 9: RESULTS & INTERPRETATION I (RQ1)
# ============================================================
bg()
title_band("Results & Interpretation (1/2)", "Results: RQ1 Multi-Predictor Model")
top_y = PAGE_H - TITLE_BAND_H - 0.35*inch
img_w = 4.9*inch
draw_image_fit("fig_rq1_r2_v2.png", MARGIN_X, top_y - 3.5*inch, img_w, 3.5*inch)

panel_x = MARGIN_X + img_w + 0.35*inch
panel_w = PAGE_W - MARGIN_X - panel_x
rq1_rows = [
    ["Pair", "n", "R²", "Sig. predictors?"],
    ["USD/INR", "89", "5.0%", "No (best p = 0.17)"],
    ["EUR/USD", "89", "12.4%", "Yes — infl., trade bal., GDP (p < .04)"],
    ["GBP/USD", "89", "3.5%", "No (best p = 0.19)"],
    ["USD/JPY", "89", "3.7%", "No (best p = 0.33)"],
]
table_grid(panel_x, top_y - 0.05*inch, [panel_w*0.24, panel_w*0.13, panel_w*0.15, panel_w*0.48],
           rq1_rows, row_h=0.34*inch, font_size=10)

c.setFont(F_BOLD, 12.5)
c.setFillColor(NAVY)
ny = top_y - 0.05*inch - 5*0.34*inch - 0.3*inch
c.drawString(panel_x, ny, "Interpretation")
interp = ("Expanding to the full 4-predictor specification (rate, inflation, trade balance, and GDP-growth "
          "differentials — restoring Japan's inflation term via World Bank annual CPI) raises R² for every "
          "pair. For EUR/USD, three of four coefficients are significant (inflation p=.023, trade balance "
          "p=.017, GDP growth p=.039) — the project's first significant RQ1 result. VIF stayed low "
          "(1.0-1.8) across all pairs — multicollinearity is not the cause.")
lines = wrap_text(interp, F_REG, 11.5, panel_w)
c.setFont(F_REG, 11.5)
c.setFillColor(DARK_TEXT)
ny -= 20
for ln in lines:
    c.drawString(panel_x, ny, ln)
    ny -= 15.5
ny -= 6
c.setFillColor(HexColor("#EFF3F7"))
c.roundRect(panel_x, ny - 0.75*inch, panel_w, 0.7*inch, 6, stroke=0, fill=1)
c.setFont(F_BOLD_IT, 11)
c.setFillColor(NAVY)
tk = wrap_text("Takeaway: the Meese-Rogoff puzzle still holds for USD/INR, GBP/USD, and USD/JPY — but "
               "EUR/USD's deep, liquid market shows real, statistically significant sensitivity to macro "
               "fundamentals at a monthly horizon.", F_BOLD_IT, 11, panel_w - 0.3*inch)
ty2 = ny - 0.22*inch
for ln in tk:
    c.drawString(panel_x + 0.15*inch, ty2, ln)
    ty2 -= 14.5
footer("Results & Interpretation")
c.showPage()

# ============================================================
# SLIDE 10: RESULTS & INTERPRETATION II (RQ2, RQ4)
# ============================================================
bg()
title_band("Results & Interpretation (2/2)", "Results: RQ2 Volatility & RQ4 Event Study")
top_y = PAGE_H - TITLE_BAND_H - 0.3*inch
half_w = (PAGE_W - 2*MARGIN_X - 0.35*inch) / 2
draw_image_fit("fig_rq2_vol_forecast_v2.png", MARGIN_X, top_y - 2.55*inch, half_w, 2.55*inch)
c.setFont(F_BOLD, 12)
c.setFillColor(NAVY)
c.drawString(MARGIN_X, top_y - 2.75*inch, "RQ2 — GARCH (walk-forward) 0.231  |  RF 0.227  |  Naive 0.298")
c.setFont(F_REG, 10.5)
c.setFillColor(DARK_TEXT)
t1 = wrap_text("Re-estimated with true walk-forward refitting (23 refits, no look-ahead) rather than a "
               "single in-sample fit — both real models still beat the naive baseline by ~22-25%, and the "
               "GARCH-vs-RF gap remains non-significant (paired t, p = 0.78).", F_REG, 10.5, half_w)
ty3 = top_y - 2.95*inch
for ln in t1:
    c.drawString(MARGIN_X, ty3, ln)
    ty3 -= 14

x2 = MARGIN_X + half_w + 0.35*inch
draw_image_fit("fig_rq4_event_study_v2.png", x2, top_y - 2.55*inch, half_w, 2.55*inch)
c.setFont(F_BOLD, 12)
c.setFillColor(NAVY)
c.drawString(x2, top_y - 2.75*inch, "RQ4 — n = 71 dates, split by surprise size (T-bill proxy)")
c.setFont(F_REG, 10.5)
c.setFillColor(DARK_TEXT)
t2 = wrap_text("Splitting on |3-month T-bill yield change| (a Kuttner-style surprise proxy): the "
               "high-surprise half shows a +2.2% post-announcement volatility rise vs. -6.3% for the "
               "low-surprise half — the expected direction, but n=36/35 is too small to reach significance.",
               F_REG, 10.5, half_w)
ty4 = top_y - 2.95*inch
for ln in t2:
    c.drawString(x2, ty4, ln)
    ty4 -= 14

ny = top_y - 2.55*inch - 1.3*inch - 0.35*inch
box_w = PAGE_W - 2*MARGIN_X
c.setFillColor(HexColor("#EFF3F7"))
c.roundRect(MARGIN_X, ny - 0.62*inch, box_w, 0.62*inch, 6, stroke=0, fill=1)
c.setFont(F_BOLD_IT, 12)
c.setFillColor(NAVY)
cc_lines = wrap_text("Cross-cutting takeaway: volatility is more forecastable than direction — and surprise "
                      "size, not meeting occurrence, drives the (directional, not-yet-significant) reaction.",
                      F_BOLD_IT, 12, box_w - 0.4*inch)
cy = ny - 0.24*inch
for ln in cc_lines:
    c.drawString(MARGIN_X + 0.2*inch, cy, ln)
    cy -= 15
footer("Results & Interpretation")
c.showPage()

# ============================================================
# SLIDE 11: IMPLEMENTATION & USER BENEFIT
# ============================================================
bg()
title_band("Implementation & User Benefit", "Implementation & User Benefit")
users = [
    ("Corporate Treasury", "Time FX hedges around scheduled policy dates using event-study risk flags"),
    ("FX Traders / PMs", "Short-term volatility forecasts (GARCH/RF) as a tactical risk-sizing input"),
    ("Import/Export Firms", "Early-warning signal on elevated volatility risk before it hits margins"),
]
top_y = PAGE_H - TITLE_BAND_H - 0.4*inch
uc_w = (PAGE_W - 2*MARGIN_X - 0.6*inch) / 3
uc_h = 1.55*inch
for i, (who, benefit) in enumerate(users):
    x = MARGIN_X + i * (uc_w + 0.3*inch)
    card(x, top_y - uc_h, uc_w, uc_h, border=HexColor("#E1E7ED"))
    c.setFillColor(TEAL if i != 1 else GOLD)
    c.circle(x + 0.32*inch, top_y - 0.32*inch, 0.18*inch, stroke=0, fill=1)
    c.setFont(F_BOLD, 12)
    c.setFillColor(white)
    c.drawCentredString(x + 0.32*inch, top_y - 0.37*inch, str(i+1))
    c.setFont(F_BOLD, 12)
    c.setFillColor(NAVY)
    c.drawString(x + 0.6*inch, top_y - 0.32*inch, who)
    c.setFont(F_REG, 10.5)
    c.setFillColor(DARK_TEXT)
    bl = wrap_text(benefit, F_REG, 10.5, uc_w - 0.3*inch)
    by = top_y - 0.62*inch
    for ln in bl:
        c.drawString(x + 0.15*inch, by, ln)
        by -= 14

y2 = top_y - uc_h - 0.5*inch
c.setFont(F_BOLD, 15)
c.setFillColor(NAVY)
c.drawString(MARGIN_X, y2, "Proposed Deliverable")
items = [
    "A dashboard-style early-warning summary built directly from model outputs — not a raw academic forecast.",
    "Flags elevated volatility risk ahead of scheduled central-bank announcements (RQ4) for the currency pairs a user holds exposure in.",
    "Surfaces the RQ1/RQ2 model outputs (direction tendency, volatility forecast) side by side so users can weigh macro-driven vs. statistical signals.",
    "Recommends model family by decision horizon: macro regression for medium-term hedging, GARCH/ML for short-term tactical calls.",
]
bullet_list(items, MARGIN_X, y2 - 0.4*inch, PAGE_W - 2*MARGIN_X, size=13.5, leading=18, gap_after=9)
footer("Implementation & User Benefit")
c.showPage()

# ============================================================
# SLIDE 12: CONCLUSION
# ============================================================
bg(NAVY_DK)
c.setFillColor(GOLD)
c.setFont(F_BOLD, 13)
c.drawString(MARGIN_X, PAGE_H - 1.0*inch, "C O N C L U S I O N")
c.setFont(F_BOLD, 26)
c.setFillColor(white)
c.drawString(MARGIN_X, PAGE_H - 1.65*inch, "Short-term FX direction resists prediction —")
c.drawString(MARGIN_X, PAGE_H - 2.15*inch, "but volatility itself is a tractable, actionable signal.")

concl = [
    "RQ1, RQ2, and RQ4 mostly fail to reject their null hypotheses — a coherent, literature-consistent "
    "pattern — but the full 4-predictor RQ1 model breaks that pattern for EUR/USD (R²=12.4%, 3 of 4 "
    "coefficients significant), showing the null is not universal.",
    "For USD/INR, GBP/USD, and USD/JPY, RQ1 + RQ4 still confirm the Meese-Rogoff / Kuttner picture: "
    "fundamentals and scheduled events alone don't move short-term FX in a statistically detectable way.",
    "RQ2 shows real practical value under a genuine walk-forward test: both GARCH and Random Forest cut "
    "volatility-forecast error by ~22-25% versus a naive baseline — this is the actionable core of the project.",
    "The honest, rigorously-tested results — including the null ones — are themselves the deliverable "
    "expected of a capstone at this stage; they sharpen, rather than undermine, the recommendation ahead.",
]
y = PAGE_H - 2.75*inch
c.setFillColor(HexColor("#CADCFC"))
bullet_list(concl, MARGIN_X, y, PAGE_W - 2*MARGIN_X, size=15, leading=20, gap_after=14,
            color=HexColor("#DCE6F5"), marker_color=GOLD)
footer("Conclusion")
c.showPage()

# ============================================================
# SLIDE 13: LIMITATIONS & FUTURE WORK
# ============================================================
bg()
title_band("Limitations & Future Work", "Limitations & Future Work")
lim_x = MARGIN_X
lim_w = (PAGE_W - 2*MARGIN_X - 0.4*inch) / 2
top_y = PAGE_H - TITLE_BAND_H - 0.35*inch
c.setFont(F_BOLD, 15)
c.setFillColor(WARN)
c.drawString(lim_x, top_y, "Limitations")
lims = [
    "RQ3 (sentiment) is architecturally defined but not yet executed — GDELT collection remains.",
    "Eurozone has no native monthly trade-balance aggregate; it is built by summing 20 euro-area members' "
    "annual balances (Eurostat), forward-filled monthly.",
    "India/UK/Japan inflation now uses World Bank annual CPI (current through 2025, replacing FRED series "
    "stale since Mar 2025 / dead since Jun 2021) — real and current, but coarser than a monthly series.",
    "RQ4's surprise-magnitude split (3-month T-bill yield proxy, not true consensus data) shows the "
    "expected direction, but the n=36/35 halves are too small to reach significance.",
    "Walk-forward GARCH refits every 20 trading days for tractability; a daily-refit cadence was not "
    "attempted due to compute cost.",
]
bullet_list(lims, lim_x, top_y - 0.45*inch, lim_w, size=11.5, leading=15, gap_after=9, marker_color=WARN)

fut_x = MARGIN_X + lim_w + 0.4*inch
c.setFont(F_BOLD, 15)
c.setFillColor(GOOD)
c.drawString(fut_x, top_y, "Future Work")
futs = [
    "Complete GDELT sentiment pipeline (VADER + FinBERT) and run the RQ3 comparison.",
    "Acquire a true survey-based policy-surprise series (e.g., Bloomberg/Reuters consensus) to replace "
    "the T-bill-yield proxy used here, and re-run RQ4 with adequate power.",
    "Source a native monthly Eurozone trade-balance series (e.g., ECB SDW) to replace the member-state "
    "aggregation used here.",
    "Extend RQ2 to all four pairs and add XGBoost/LSTM to the comparison, as originally scoped.",
    "Deploy the recommended early-warning dashboard as a live internal tool for pilot users.",
]
bullet_list(futs, fut_x, top_y - 0.45*inch, lim_w, size=12, leading=16, gap_after=10, marker_color=GOOD)
footer("Limitations & Future Work")
c.showPage()

# ============================================================
# SLIDE 14: BIBLIOGRAPHY
# ============================================================
bg()
title_band("Bibliography", "Bibliography (APA 7)")
refs = [
    "Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. arXiv.",
    "Bank for International Settlements. (2022). Triennial Central Bank Survey: OTC foreign exchange turnover in 2022.",
    "Bender, E. M., & Friedman, B. (2018). Data statements for NLP. TACL, 6, 587-604.",
    "Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. J. of Econometrics, 31(3), 307-327.",
    "Breiman, L. (2001). Random forests. Machine Learning, 45(1), 5-32.",
    "Button, K. S. et al. (2013). Power failure: Why small sample size undermines neuroscience. Nat. Rev. Neurosci., 14(5), 365-376.",
    "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. KDD 2016, 785-794.",
    "Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. JBES, 13(3), 253-263.",
    "Engle, R. F. (1982). Autoregressive conditional heteroscedasticity. Econometrica, 50(4), 987-1007.",
    "Federal Reserve Bank of St. Louis. (n.d.). FRED economic data [Data set]. fred.stlouisfed.org",
    "Gebru, T. et al. (2018). Datasheets for datasets. arXiv.",
    "Gelman, A., & Hill, J. (2007). Data analysis using regression and multilevel/hierarchical models. Cambridge Univ. Press.",
    "Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. Neural Computation, 9(8), 1735-1780.",
    "Hutto, C., & Gilbert, E. (2014). VADER: A parsimonious rule-based sentiment model. ICWSM 2014, 216-225.",
    "Kuttner, K. N. (2001). Monetary policy surprises and interest rates. J. of Monetary Economics, 47(3), 523-544.",
    "Meese, R. A., & Rogoff, K. (1983). Empirical exchange rate models of the seventies. J. of Int'l Economics, 14(1-2), 3-24.",
    "O'Brien, T., Sukumar, A., & Helfert, M. (2013). The value of good data - A quality perspective. ICEIS 2013, 555-562.",
    "Rahm, E., & Do, H. H. (2000). Data cleaning: Problems and current approaches. IEEE Data Eng. Bulletin, 23(4), 3-13.",
    "Tetlock, P. C. (2007). Giving content to investor sentiment. The Journal of Finance, 62(3), 1139-1168.",
    "Torralba, A., & Efros, A. A. (2011). Unbiased look at dataset bias. CVPR 2011, 1521-1528.",
]
y = PAGE_H - TITLE_BAND_H - 0.4*inch
col_w2 = (PAGE_W - 2*MARGIN_X - 0.4*inch) / 2
half = (len(refs) + 1) // 2
for col, chunk in enumerate([refs[:half], refs[half:]]):
    x = MARGIN_X + col * (col_w2 + 0.4*inch)
    yy = y
    for r in chunk:
        c.setFont(F_REG, 9.3)
        c.setFillColor(DARK_TEXT)
        lines = wrap_text(r, F_REG, 9.3, col_w2)
        for j, ln in enumerate(lines):
            c.drawString(x + (14 if j == 0 else 14), yy, ln if j > 0 else ln)
            yy -= 12.5
        yy -= 5.5
footer("Bibliography")
c.showPage()

c.save()
print("Deck built:", "QM640_Final_Presentation_Group8.pdf")




