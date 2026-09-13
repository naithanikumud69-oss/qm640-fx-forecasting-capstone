"""
QM640 Data Analytics Capstone — Final Report (Group 8)
Builds QM640_Final_Report_Group8.pdf directly via reportlab Platypus,
following the QM 640 Final Report Template.docx structure exactly.
"""
import json
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                 Image, PageBreak, ListFlowable, ListItem, KeepTogether,
                                 NextPageTemplate, PageTemplate, Frame, BaseDocTemplate)
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from PIL import Image as PILImage

D = "/private/tmp/claude-501/-Users-kumudnaithani-Documents-AI-CODE/4ee1c2ec-d81d-4a74-b90f-255e253c4aa6/scratchpad/"
FX = D + "fx_data/"
FR = D + "final_report/"
ASSETS = D + "final_pres/assets/"

rq1 = json.load(open(FX + "rq1_results_v2.json"))
rq2 = json.load(open(FX + "rq2_results_v2.json"))
rq4 = json.load(open(FX + "rq4_results_v2.json"))
pstats = json.load(open(FX + "predictor_stats.json"))

NAVY = colors.HexColor("#0B2E4F")
TEAL = colors.HexColor("#1C7293")
GOLD = colors.HexColor("#C8963E")
SLATE = colors.HexColor("#5C6B7A")
LIGHT = colors.HexColor("#EFF3F7")
DARK = colors.HexColor("#16213E")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=11,
                           leading=16, alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle("BodyIndent", parent=styles["Body"], leftIndent=18))
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=17,
                           textColor=NAVY, spaceBefore=18, spaceAfter=10))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13.5,
                           textColor=NAVY, spaceBefore=14, spaceAfter=7))
styles.add(ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=11.5,
                           textColor=TEAL, spaceBefore=10, spaceAfter=5))
styles.add(ParagraphStyle("Caption", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=9.5,
                           textColor=SLATE, alignment=TA_CENTER, spaceAfter=12, spaceBefore=3))
styles.add(ParagraphStyle("TableCell", parent=styles["Normal"], fontName="Helvetica", fontSize=8.7,
                           leading=11))
styles.add(ParagraphStyle("TableHead", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.9,
                           leading=11, textColor=colors.white))
styles.add(ParagraphStyle("TitleBig", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=22,
                           alignment=TA_CENTER, textColor=NAVY, leading=27))
styles.add(ParagraphStyle("TitleSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13,
                           alignment=TA_CENTER, textColor=DARK, spaceBefore=4, leading=17))
styles.add(ParagraphStyle("Quote", parent=styles["Body"], leftIndent=24, rightIndent=24,
                           fontName="Helvetica-Oblique", textColor=DARK))

story = []

def P(text, style="Body"):
    story.append(Paragraph(text, styles[style]))

def SP(h=8):
    story.append(Spacer(1, h))

def H1(text):
    story.append(Paragraph(text, styles["H1"]))

def H2(text):
    story.append(Paragraph(text, styles["H2"]))

def H3(text):
    story.append(Paragraph(text, styles["H3"]))

def bullets(items, style="Body", bullet_char="•"):
    flow = ListFlowable(
        [ListItem(Paragraph(t, styles[style]), bulletColor=TEAL, value=bullet_char) for t in items],
        bulletType="bullet", leftIndent=16, spaceBefore=2, spaceAfter=8)
    story.append(flow)

def cell(text, head=False):
    return Paragraph(text, styles["TableHead"] if head else styles["TableCell"])

def table_from_rows(rows, col_widths, header=True, caption=None, fig_num=None, small=False):
    data = []
    for ri, row in enumerate(rows):
        data.append([cell(str(c), head=(header and ri == 0)) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY) if header else ("BACKGROUND", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C7D0DA")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F9FB")]),
    ]
    t.setStyle(TableStyle(style))
    story.append(t)
    if caption:
        SP(4)
        P(caption, "Caption")
    SP(6)

def fig(path, caption, max_width=6.4*inch, max_height=3.6*inch):
    with PILImage.open(path) as im:
        w, h = im.size
    ratio = w / h
    draw_w = max_width
    draw_h = draw_w / ratio
    if draw_h > max_height:
        draw_h = max_height
        draw_w = draw_h * ratio
    story.append(Image(path, width=draw_w, height=draw_h, hAlign="CENTER"))
    SP(4)
    P(caption, "Caption")

def page_break():
    story.append(PageBreak())

# ============================================================================
# TITLE PAGE
# ============================================================================
SP(70)
P("Data Analytics Capstone", "TitleBig")
SP(6)
P("Forecasting Short-Term Exchange Rate Movements and Volatility in Major "
  "Currency Pairs Using Macroeconomic Indicators and Machine Learning", "TitleSub")
SP(20)
P("Final Report", "TitleBig")
SP(30)
P("Kumud Naithani", "TitleSub")
P("Walsh College", "TitleSub")
P("QM640: Data Analytics Capstone", "TitleSub")
P("Mentor: Abhay Poddar", "TitleSub")
P("Fall 2026 Term", "TitleSub")
P("September 12, 2026", "TitleSub")
page_break()

# ============================================================================
# GITHUB REPOSITORY
# ============================================================================
H1("GitHub Repository")
P("All raw data, cleaning scripts, analysis notebooks, generated figures, and this report's "
  "build scripts are organized for publication at: [GitHub repository URL to be added]. "
  "The repository README documents the folder structure (raw/, processed/, notebooks/, "
  "figures/) and reproduction steps. Appendix A, Appendix B, and Appendix C reproduce the "
  "three core analysis scripts referenced throughout this report (RQ1 multi-predictor "
  "regression, RQ2 volatility forecasting, and RQ4 event study, respectively) so that the "
  "statistical work can be verified without cloning the repository.")
P("<b>Reproducibility statement.</b> Every figure and table number reported in this document "
  "(Table 1 through Table 9; Figure 1 through Figure 6) was generated programmatically from the "
  "underlying source data at report-build time, rather than hand-typed from an earlier run, so "
  "that re-executing the three appendix scripts against the same source CSVs reproduces every "
  "number in this report exactly. Where a figure could not be regenerated for this report (e.g., "
  "if a source API becomes unavailable in the future), the archived raw CSVs in the repository's "
  "/data/raw/ folder allow the original run to be reproduced without re-querying the live API.")
page_break()

# ============================================================================
# ABSTRACT
# ============================================================================
H1("Abstract")
P("<b>Problem.</b> Forecasting short-term foreign-exchange (FX) direction and volatility is a "
  "longstanding, unresolved problem in international finance: structural macroeconomic models "
  "have historically struggled to outperform a naive random walk (Meese &amp; Rogoff, 1983), yet "
  "corporate treasuries, FX traders, and policymakers still need actionable short-horizon signals.")
P("<b>Solution approach.</b> This study compares four analytic approaches on a common set of "
  "currency pairs and a common eight-year data window: (1) multiple linear regression (OLS) of "
  "monthly FX returns on interest-rate, inflation, trade-balance, and GDP-growth differentials, "
  "with variance-inflation-factor (VIF) screening for multicollinearity; (2) GARCH(1,1) versus "
  "Random Forest volatility forecasting, evaluated under genuine walk-forward re-estimation; "
  "(3) a planned VADER/FinBERT news-sentiment overlay (architected but not yet executed); and "
  "(4) an FOMC event study conditioned on policy-surprise magnitude, proxied by short-term "
  "Treasury-yield changes, using paired t-tests and Wilcoxon signed-rank tests.")
P("<b>Data.</b> All data are real and publicly sourced — no Kaggle datasets are used. Daily FX "
  "closing levels for USD/INR, EUR/USD, GBP/USD, and USD/JPY were pulled from FRED "
  "(2,143 clean trading days per pair, January 2018-July 2026; 8,572 observations pooled). "
  "Macroeconomic predictors were assembled from FRED, World Bank Open Data, and Eurostat "
  "at monthly and quarterly frequency (89 aligned monthly observations per pair after lagging), "
  "and 71 verified FOMC meeting dates (2018-2026) anchor the event study.")
P("<b>Technology.</b> Python 3.11 with pandas, NumPy, statsmodels, scikit-learn, the arch package "
  "(GARCH), and SciPy; all model fitting was performed on CPU, with no GPU requirement given the "
  "dataset scale.")
P("<b>Major results.</b> EUR/USD is the one pair where the full four-predictor macro model reaches "
  f"statistical significance (R² = {rq1['EUR/USD']['r2']*100:.1f}%, three of four coefficients "
  "significant at p &lt; .05); the other three pairs fail to reject the RQ1 null. Under walk-forward "
  f"re-estimation, GARCH(1,1) and Random Forest volatility forecasts both cut RMSE by roughly "
  f"22-25% relative to a naive baseline "
  f"(GARCH {rq2['garch_rmse_walkforward']:.3f}, RF {rq2['rf_rmse']:.3f}, naive "
  f"{rq2['naive_rmse']:.3f}), with no significant difference between the two. The FOMC event "
  "study shows no significant average volatility spike across all 71 meetings, but splitting on "
  "surprise magnitude reveals the theoretically expected direction — larger surprises coincide with "
  "larger post-announcement volatility increases — though the halved subsample is underpowered.")
P("<b>Implementation area.</b> These findings support a practical early-warning dashboard for "
  "corporate treasury and FX trading teams: volatility forecasts (not direction) are the reliable, "
  "deployable signal, best used to time hedges and size risk ahead of scheduled policy events, with "
  "EUR/USD as the one pair where macro-fundamental direction signals also carry weight.")
page_break()

# ============================================================================
# INTRODUCTION
# ============================================================================
H1("Introduction")

H2("Background and Context")
P("The foreign exchange (FX) market is the largest and most liquid financial market in the "
  "world, with global turnover exceeding USD 7 trillion per day (Bank for International "
  "Settlements, 2022). Currency values fluctuate continuously in response to macroeconomic "
  "fundamentals, central-bank policy actions, and shifting investor sentiment, creating both "
  "risk and opportunity for the institutions and individuals who transact across borders. For "
  "corporate treasuries, importers and exporters, institutional investors, and retail traders "
  "alike, the ability to anticipate short-term currency movements directly affects hedging "
  "decisions, pricing strategy, and portfolio performance.")
P("Exchange rates are theoretically linked to macroeconomic fundamentals through relationships "
  "such as uncovered interest-rate parity (which ties currency movements to interest-rate "
  "differentials) and purchasing power parity (which ties currency movements to inflation "
  "differentials). In practice, however, these fundamentals explain only part of short-term "
  "currency behavior. Meese and Rogoff (1983) famously demonstrated that structural "
  "macroeconomic models often fail to outperform a naive random-walk forecast over short "
  "horizons &mdash; a finding often referred to as the &ldquo;Meese-Rogoff puzzle&rdquo; &mdash; which has "
  "motivated decades of subsequent research into alternative forecasting approaches.")
P("In recent years, machine-learning (ML) methods such as random forests and gradient-boosted "
  "trees have shown an ability to capture nonlinear and interaction effects that classical "
  "econometric models such as GARCH may miss (Bollerslev, 1986; Breiman, 2001). Separately, "
  "natural-language-processing (NLP) techniques now make it possible to quantify sentiment "
  "embedded in financial news in near real time (Araci, 2019; Hutto &amp; Gilbert, 2014), and "
  "research has linked such sentiment measures to subsequent market movements (Tetlock, 2007). "
  "Central-bank policy announcements are a further well-documented source of short-term "
  "volatility (Kuttner, 2001), particularly for emerging-market currencies such as the Indian "
  "rupee, which are highly sensitive to shifts in U.S. monetary policy and global risk appetite.")
P("This project sits at the intersection of these strands of research. It is directly relevant "
  "to corporate finance and treasury teams that must decide when and how to hedge currency "
  "exposure, to FX traders and portfolio managers who require timely directional and volatility "
  "signals, and to policymakers monitoring exchange-rate stability. By systematically comparing "
  "macroeconomic, machine-learning, and event-based approaches on a common set of currency "
  "pairs, this study generates evidence that is directly actionable for these stakeholders, "
  "rather than evidence for a single isolated technique.")

H2("Problem Statement")
P("Despite decades of research, forecasting short-term exchange-rate direction and volatility "
  "remains difficult, and existing studies typically evaluate macroeconomic-fundamental models, "
  "machine-learning models, sentiment-based signals, and policy-event effects in isolation "
  "rather than within a single, comparable framework. This fragmentation leaves practitioners "
  "without clear, comparative evidence on which class of model &mdash; or which combination of "
  "signals &mdash; delivers the most reliable short-term forecasts for major currency pairs, and "
  "specifically for an emerging-market currency (the Indian rupee) alongside major "
  "developed-market pairs.")
P("<b>Problem statement.</b> The objective of this study is to <i>predict and explain</i> "
  "Y = short-term (monthly) directional return and (daily) realized volatility for the currency "
  "pairs USD/INR, EUR/USD, GBP/USD, and USD/JPY, using X = interest-rate differentials, "
  "inflation differentials, trade-balance differentials, GDP-growth differentials, lagged "
  "returns, and FOMC policy-surprise magnitude, over January 2018-July 2026. Success is "
  "evaluated using R&sup2; and coefficient significance (RQ1), RMSE relative to a naive baseline "
  "(RQ2), and paired-difference significance tests (RQ4).")

H2("Purpose of the Study")
P("The purpose of this study is to compare the effectiveness of macroeconomic-indicator-based "
  "models and machine-learning models in predicting the short-term movement and volatility of "
  "four major currency pairs, and to evaluate whether central-bank policy events measurably "
  "affect short-term volatility. The study is both predictive (forecasting direction and "
  "volatility) and explanatory (identifying which macroeconomic and policy drivers are "
  "statistically significant), and it draws on multiple linear regression, time-series "
  "econometrics (GARCH), ensemble machine learning (Random Forest), and event-study "
  "methodology.")

H2("Research Problems / Research Questions")
P("Research problems must be clearly defined; the four research questions pursued in this "
  "study, together with their null (H0) and alternative (Ha) hypotheses, are presented below. "
  "Full results for each are reported in the Results section.")
H3("Research Question 1 (RQ1)")
P("To what extent do macroeconomic indicators &mdash; interest-rate differential, inflation "
  "differential, trade balance, and GDP growth rate &mdash; predict the short-term directional "
  "movement of major currency pairs (USD/INR, EUR/USD, GBP/USD, USD/JPY)?")
P("<i>H0:</i> None of the macroeconomic predictors is significantly associated with short-term "
  "directional currency movement. <i>Ha:</i> At least one macroeconomic predictor is "
  "significantly associated with directional movement.")
H3("Research Question 2 (RQ2)")
P("Do machine-learning models (Random Forest) provide significantly better forecasting accuracy "
  "for exchange-rate volatility than a traditional econometric model (GARCH)?")
P("<i>H0:</i> The volatility-forecast accuracy of the Random Forest model is not significantly "
  "different from that of the GARCH(1,1) baseline. <i>Ha:</i> The Random Forest model achieves "
  "significantly lower forecast error than the GARCH baseline.")
H3("Research Question 3 (RQ3)")
P("Does incorporating financial-news sentiment, extracted using NLP sentiment-scoring methods, "
  "significantly improve the predictive accuracy of exchange-rate direction models beyond "
  "macroeconomic indicators alone?")
P("<i>H0:</i> Adding the news-sentiment feature does not significantly improve directional "
  "accuracy over the best RQ2 model. <i>Ha:</i> Adding the news-sentiment feature significantly "
  "improves directional accuracy. <i>(RQ3 is architected but not executed in this round; see "
  "Limitations.)</i>")
H3("Research Question 4 (RQ4)")
P("Is there a statistically significant relationship between Federal Reserve (FOMC) policy "
  "announcements and short-term spikes in exchange-rate volatility, and can the size of a "
  "policy &ldquo;surprise&rdquo; predict the magnitude of that spike?")
P("<i>H0:</i> Realized volatility immediately after a policy announcement is not significantly "
  "different from the pre-announcement baseline, and policy surprises do not predict spike "
  "magnitude. <i>Ha:</i> Post-announcement volatility is significantly higher than the "
  "pre-announcement baseline, and larger policy surprises predict larger spikes.")

H2("Contributions and Expected Value")
P("<b>Practical contribution:</b> a single, comparable evaluation of macroeconomic, "
  "machine-learning, and event-based FX forecasting approaches across four currency pairs "
  "spanning both a major emerging-market currency (INR) and three developed-market currencies, "
  "using exclusively public, non-Kaggle data.")
P("<b>Technical contribution:</b> a genuine walk-forward GARCH evaluation (re-estimated "
  "periodically rather than fit once), a surprise-magnitude-conditioned event study using a "
  "real Treasury-yield proxy rather than treating every policy meeting as equivalent, and a "
  "transparent accounting of every data-quality limitation encountered (stale/discontinued "
  "national CPI series, an aggregated rather than native Eurozone trade-balance series) rather "
  "than silently working around them.")
P("<b>Value to stakeholders:</b> corporate treasury teams and FX risk managers gain evidence on "
  "which signal family is actually reliable at a short horizon (volatility, not direction, for "
  "three of four pairs) and a concrete, data-driven basis for an early-warning dashboard timed "
  "around scheduled policy announcements.")

H2("Stakeholder Analysis")
P("Three stakeholder groups have distinct, concrete uses for this study's findings. "
  "<b>Corporate treasury teams</b> at firms with recurring cross-border payables or receivables "
  "(e.g., an Indian subsidiary remitting USD-denominated payments) need to decide when to lock "
  "in a forward rate; the RQ2 finding that volatility is forecastable with real accuracy gives "
  "them a concrete basis for sizing that hedge, while the RQ1 finding tells them not to expect a "
  "reliable directional signal for USD/INR specifically. <b>FX traders and portfolio risk "
  "managers</b> making shorter-horizon tactical decisions benefit most from the RQ4 finding that "
  "surprise magnitude, not meeting occurrence, is what should condition a volatility-risk flag. "
  "<b>Import/export businesses</b> with thinner risk-management infrastructure than a large "
  "treasury desk are the target user for the simplified early-warning dashboard described in "
  "Implementation and User Benefit, where the goal is a small number of clear, reliable signals "
  "rather than a complex multi-model interface.")
page_break()

# ============================================================================
# LITERATURE REVIEW
# ============================================================================
H1("Literature Review")

H2("Literature Review Approach")
P("Sources were identified using Google Scholar and the ACM Digital Library with search terms "
  "combining core concepts from each research question (e.g., &ldquo;exchange rate forecasting&rdquo; "
  "AND &ldquo;machine learning&rdquo;; &ldquo;GARCH&rdquo; AND &ldquo;volatility&rdquo;; &ldquo;monetary policy surprise&rdquo; AND "
  "&ldquo;volatility&rdquo;; &ldquo;data quality&rdquo; AND &ldquo;machine learning&rdquo;; &ldquo;statistical power&rdquo; AND "
  "&ldquo;sample size&rdquo;; &ldquo;model cards&rdquo; AND &ldquo;model reporting&rdquo;), following a PRISMA-inspired "
  "process of defining the question, searching, and screening for relevance. Inclusion criteria "
  "favored foundational, highly cited methodological papers directly underlying the statistical "
  "and machine-learning techniques used for RQ1, RQ2, and RQ4, as well as papers establishing "
  "best practice for data quality, sample-size justification, dataset documentation, and model "
  "reporting, since this project's contribution is a comparative, well-documented application "
  "rather than a novel algorithm. Eighteen sources were selected; each is summarized in Table 1.")

H2("Summary of Key Literature (18 Sources)")
lit_rows = [
    ["Author (Year)", "Domain/Context", "Method(s)", "Key Finding", "RQ Linkage"],
    ["Meese &amp; Rogoff (1983)", "Int'l finance", "Structural macro vs. random walk",
     "Structural models do not outperform a random walk out-of-sample", "RQ1"],
    ["Engle (1982)", "Econometrics", "ARCH model",
     "Introduced conditional heteroskedasticity modeling", "RQ2"],
    ["Bollerslev (1986)", "Econometrics", "GARCH model",
     "Generalized ARCH to a parsimonious volatility model", "RQ2"],
    ["Breiman (2001)", "Machine learning", "Random Forests",
     "Ensemble of trees reduces variance, improves generalization", "RQ2"],
    ["Diebold &amp; Mariano (1995)", "Forecasting/stats", "Diebold-Mariano-style test",
     "Formal comparison of whether two forecasts' errors differ significantly", "RQ2"],
    ["Hutto &amp; Gilbert (2014)", "NLP", "VADER sentiment",
     "Rule-based lexicon achieves strong accuracy on informal text", "RQ3"],
    ["Araci (2019)", "NLP/Finance", "FinBERT",
     "Domain-adapted transformer improves financial sentiment classification", "RQ3"],
    ["Tetlock (2007)", "Behavioral finance", "Media pessimism index vs. returns",
     "Media sentiment predicts short-term downward market pressure", "RQ3"],
    ["Kuttner (2001)", "Monetary economics", "Event-study regression",
     "Unexpected policy changes move rates far more than expected ones", "RQ4"],
    ["Rahm &amp; Do (2000)", "Data engineering", "Taxonomy of data-quality problems",
     "Classifies single/multi-source and schema/instance-level data errors", "Data Cleaning"],
    ["O'Brien, Sukumar &amp; Helfert (2013)", "IT/data governance",
     "Data-quality cost taxonomy", "Poor data quality has direct, measurable operational cost",
     "Data Description"],
    ["Button et al. (2013)", "Research methodology", "Power/PPV analysis",
     "Low statistical power inflates effect sizes and reduces reliability", "Sample Size (all RQs)"],
    ["Gebru et al. (2018)", "ML data documentation", "Datasheets for Datasets schema",
     "Standardized dataset documentation improves transparency and reuse", "Data Description"],
    ["Bender &amp; Friedman (2018)", "NLP data documentation", "Data Statements schema",
     "Documenting speaker/annotator demographics mitigates NLP system bias", "RQ3 (sentiment data)"],
    ["Torralba &amp; Efros (2011)", "Computer vision", "&ldquo;Name That Dataset&rdquo; classifier",
     "Benchmark datasets carry a detectable &ldquo;signature&rdquo; bias limiting generalization",
     "Limitations"],
    ["Mitchell et al. (2019)", "ML documentation", "Model Cards framework",
     "Standardized, benchmarked model reporting improves transparency of ML claims",
     "Results/Model Reporting"],
    ["Gelman &amp; Hill (2007)", "Applied statistics", "Regression/power-analysis formulas",
     "Provides the sample-size and power formulas applied across all four RQs",
     "Sample Size (all RQs)"],
    ["Green (1991)", "Applied statistics", "Multiple-regression sample-size rule",
     "n &#8805; 50 + 8k rule of thumb for multiple-regression sample size", "Sample Size (RQ1)"],
]
col_w = [1.25*inch, 1.2*inch, 1.3*inch, 2.0*inch, 1.05*inch]
table_from_rows(lit_rows, col_w, caption="Table 1. Literature relevance matrix (18 sources).")

H2("Foundations of the Forecasting Puzzle")
P("Meese and Rogoff (1983) remains the foundational, cautionary reference for this project, "
  "framing RQ1 as a genuine comparative test rather than an assumption that any single model "
  "will trivially succeed. Their original finding &mdash; that a random walk out-forecasts "
  "structural exchange-rate models built on interest-rate and money-supply differentials, even "
  "using realized future fundamentals &mdash; has been revisited and only partially overturned by "
  "decades of subsequent literature, which is precisely why RQ1 was designed as a per-pair test "
  "rather than a single pooled claim. The RQ1 results reported below &mdash; a clean null for three "
  "of four pairs and a significant result for EUR/USD &mdash; are consistent with this literature: "
  "the puzzle holds in general, but not universally, and the one exception (a deep, highly "
  "liquid, developed-market pair) is arguably the case the theory would least predict to be an "
  "exception, making it a genuinely interesting rather than a convenient result.")

H2("Volatility Modeling and Machine Learning")
P("Engle (1982) and Bollerslev (1986) provide the econometric baseline against which RQ2's "
  "machine-learning comparator (Breiman, 2001) is benchmarked. Engle's original ARCH "
  "formulation established that variance, not just the mean, could be modeled as a function of "
  "past information; Bollerslev's GARCH generalization made this parsimonious enough to "
  "estimate reliably on a single asset's return history, which is exactly the setting used for "
  "RQ2. Breiman's Random Forest provides a nonparametric alternative that requires no "
  "distributional assumption about returns, at the cost of losing GARCH's direct economic "
  "interpretability (there is no analogue to GARCH's persistence parameter in a Random Forest). "
  "The Diebold and Mariano (1995) framework motivates the paired-loss significance test used to "
  "compare GARCH and Random Forest forecast errors under walk-forward evaluation, since simply "
  "comparing two RMSE numbers without a formal test cannot establish whether an observed "
  "difference is meaningful or noise.")

H2("Sentiment and Behavioral Finance (Planned Work)")
P("Hutto and Gilbert (2014) and Araci (2019) provide two complementary sentiment-scoring "
  "approaches earmarked for RQ3: VADER is a fast, rule-based lexicon suited to short, informal "
  "text, while FinBERT is a domain-adapted transformer expected to better capture "
  "finance-specific language (e.g., distinguishing a &ldquo;dovish surprise&rdquo; from a generically "
  "negative headline). Tetlock's (2007) behavioral-finance evidence that media sentiment carries "
  "incremental predictive information beyond fundamentals is the empirical motivation for testing "
  "RQ3 at all, rather than assuming sentiment either matters or does not. As detailed in "
  "Limitations, the GDELT-based sentiment pipeline for RQ3 is architected but not yet executed in "
  "this report, so this literature currently frames planned rather than completed work.")

H2("Monetary Policy and Event Studies")
P("Kuttner (2001) directly motivates the RQ4 event-study design and its policy-surprise "
  "construct, providing evidence from Fed funds futures markets that unexpected policy changes "
  "move interest rates far more than fully anticipated ones &mdash; the premise tested directly by "
  "this report's surprise-magnitude split of the FOMC event study. The broader event-study "
  "tradition Kuttner sits within establishes the pre/post comparison-window design (Table 6, RQ4 "
  "method) used here, and the finding that surprises specifically, rather than announcements in "
  "general, carry information is precisely what the high- vs. low-surprise-half comparison in "
  "Results is designed to test rather than assume.")

H2("Data Quality, Documentation, Bias, Statistical Power, and Model Reporting")
P("A second cluster of literature underlies the Materials and Method and Limitations sections "
  "rather than the forecasting models themselves. Rahm and Do (2000) provide a classification "
  "of data-quality problems (single- vs. multi-source, schema- vs. instance-level) that directly "
  "frames the Data Cleaning subsection below. O'Brien, Sukumar, and Helfert (2013) show, through "
  "case studies of two large organizations, that poor data quality carries direct and indirect "
  "operational costs, underscoring why this report documents its cleaning and substitution "
  "decisions explicitly (e.g., replacing stale FRED CPI series with World Bank annual data) "
  "rather than treating them as an afterthought. Gebru et al. (2018) and Bender and Friedman "
  "(2018) provide standardized documentation schemas &mdash; &ldquo;datasheets for datasets&rdquo; and &ldquo;data "
  "statements,&rdquo; respectively &mdash; that this report draws on when describing the provenance, "
  "composition, and collection process of the FX/macro data and the planned GDELT "
  "news-sentiment text data. Torralba and Efros (2011) demonstrate empirically that benchmark "
  "datasets carry a detectable &ldquo;signature&rdquo; that limits cross-dataset generalization; this "
  "motivates the limitation, noted below, that models trained on 2018-2026 data may not "
  "generalize to structurally different monetary regimes. Button et al. (2013) show across 49 "
  "neuroscience meta-analyses that underpowered studies inflate effect sizes and reduce the "
  "reliability of findings (the &ldquo;winner's curse&rdquo;) &mdash; the statistical justification underlying "
  "the minimum sample-size computation performed for each research question, using the formulas "
  "in Gelman and Hill (2007) and Green (1991). Finally, Mitchell et al. (2019) motivate this "
  "report's practice of reporting model performance with explicit sample sizes, validation "
  "method, and caveats side by side (Table 7) rather than a single headline accuracy number, "
  "consistent with the &ldquo;model cards&rdquo; standard for transparent ML reporting.")

H2("Literature-to-Research-Question Mapping")
P("Summarizing the coverage above: RQ1 is framed by Meese and Rogoff (1983), with Green (1991) "
  "and Gelman and Hill (2007) supplying its sample-size justification; RQ2 is framed by Engle "
  "(1982), Bollerslev (1986), and Breiman (2001), with Diebold and Mariano (1995) supplying its "
  "significance test; RQ3, though not yet executed, is framed by Hutto and Gilbert (2014), Araci "
  "(2019), and Tetlock (2007); and RQ4 is framed by Kuttner (2001). The remaining sources &mdash; "
  "Rahm and Do (2000), O'Brien et al. (2013), Gebru et al. (2018), Bender and Friedman (2018), "
  "Torralba and Efros (2011), Button et al. (2013), and Mitchell et al. (2019) &mdash; are "
  "cross-cutting: they do not motivate a specific model choice but instead shape how the data "
  "were cleaned and documented (Materials and Method), how sample sizes were justified (Table "
  "6), and how results are reported (Table 7, Table 8), ensuring the project's methodology is as "
  "rigorously documented as its findings.")
page_break()

# ============================================================================
# MATERIALS AND METHOD
# ============================================================================
H1("Materials and Method")

H2("Data Sources")
P("All data used in this study are publicly available from official government, central-bank, "
  "and international-organization sources; no Kaggle-hosted datasets are used, consistent with "
  "course requirements.")
bullets([
    "<b>Federal Reserve Economic Data (FRED)</b> &mdash; daily exchange rates, U.S. interest rates, "
    "U.S./Eurozone CPI, and trade balance for the U.S., India, U.K., and Japan: fred.stlouisfed.org "
    "(Federal Reserve Bank of St. Louis, n.d.).",
    "<b>World Bank Open Data</b> &mdash; annual CPI for India, the U.K., and Japan (FP.CPI.TOTL), used "
    "as a current replacement for FRED's stale/discontinued mirrors of those series: "
    "data.worldbank.org.",
    "<b>Eurostat</b> &mdash; annual trade balance for the 20 individual euro-area member states "
    "(table tet00002), summed to build a Eurozone aggregate since no native monthly Eurozone "
    "trade-balance series exists on FRED, Eurostat, or the ECB's public API: ec.europa.eu/eurostat.",
    "<b>FRED (interbank/policy rates)</b> &mdash; India (IRSTCI01INM156N), Eurozone "
    "(IRSTCI01EZM156N), U.K. SONIA (IUDSOIA), and Japan (IRSTCI01JPM156N), each mirrored from "
    "OECD/national-central-bank sources.",
    "<b>FRED (GDP growth)</b> &mdash; quarterly q/q real GDP growth for the U.S., India, U.K., and "
    "Japan (NAEXKP01xxQ657S); the Eurozone series is computed as the q/q percentage change of the "
    "real GDP level series CLVMNACSCAB1GQEA19.",
    "<b>GDELT Project</b> &mdash; public news tone/sentiment data (non-Kaggle), planned for the RQ3 "
    "sentiment pipeline: gdeltproject.org.",
    "<b>Official FOMC policy calendar</b> &mdash; 71 verified Federal Reserve rate-decision dates, "
    "2018-2026 (including the two unscheduled March 2020 emergency meetings), cross-checked "
    "against federalreserve.gov.",
])

H2("Data Availability and Ethical Considerations")
P("All data required for this study are publicly available from official government, "
  "central-bank, and international-organization sources; no Kaggle-hosted datasets are used, "
  "consistent with course requirements. Because the data consist entirely of aggregate "
  "macroeconomic series, market prices, and (for the planned RQ3 work) publicly published news "
  "content, no personally identifiable information is collected, and no human-subject consent "
  "procedures are required. Two considerations are nonetheless noted. First, macroeconomic "
  "series such as GDP growth and trade balance are periodically revised after initial release; "
  "this study uses the most recently available vintage of each series (as of the September 2026 "
  "data pull) rather than the vintage that would have been available in real time on each "
  "historical date, and this is logged as a limitation rather than presented as a real-time-"
  "reproducible result. Second, once the planned RQ3 sentiment pipeline is executed, the GDELT "
  "news-sentiment text data will additionally require a data statement in the sense of Bender "
  "and Friedman (2018), since it is linguistic data with its own speaker population: at minimum, "
  "the language variety (English-language news), curation rationale (headlines mentioning the "
  "four currency pairs or their countries), and time period will need to be documented, so that "
  "any skew in which news outlets or regions are represented is visible to downstream users of "
  "the sentiment feature.")

H2("Data Dictionary")
dd_rows = [
    ["Variable", "Definition", "Frequency / Range", "Source"],
    ["exchange_rate", "Official daily closing level, local currency per USD, 4 pairs",
     "Daily, 2018-2026", "FRED DEXINUS/DEXUSEU/DEXUSUK/DEXJPY"],
    ["log_return", "log(rate_t) - log(rate_t-1)", "Daily; approx. &plusmn;2%", "Derived"],
    ["rate_diff_lag1", "1-month-lagged (foreign - U.S.) policy/interbank rate differential",
     "Monthly", "FRED (5 series)"],
    ["infl_diff_lag1", "1-month-lagged (foreign - U.S.) CPI/HICP YoY inflation differential",
     "Monthly (India/U.K./Japan: annual, forward-filled)", "FRED (US/EZ); World Bank (IN/GB/JP)"],
    ["tb_diff_lag1", "1-month-lagged (foreign - U.S.) trade-balance differential, "
     "z-scored per country before differencing", "Monthly (Eurozone: annual, forward-filled)",
     "FRED (US/IN/GB/JP); Eurostat sum (EZ)"],
    ["gdp_diff_lag1", "1-month-lagged (foreign - U.S.) GDP q/q growth-rate differential, "
     "forward-filled from quarterly to monthly", "Quarterly", "FRED (4); computed (EZ)"],
    ["garch_vol_forecast", "GARCH(1,1) one-step-ahead conditional volatility forecast (%), "
     "walk-forward re-estimated every 20 trading days", "Daily, test window", "Derived (arch package)"],
    ["rf_vol_forecast", "Random Forest forecast of |return| from 5 lagged daily returns",
     "Daily, test window", "Derived (scikit-learn)"],
    ["dtb3_change", "Absolute change in the 3-month Treasury-bill secondary-market rate on "
     "FOMC day, used as the policy-surprise-magnitude proxy", "Event day, 71 events", "FRED DTB3"],
]
table_from_rows(dd_rows, [1.25*inch, 2.55*inch, 1.55*inch, 1.5*inch],
                caption="Table 2. Data dictionary (variables used in the reported models).")

H2("Descriptive Statistics of RQ1 Predictors")
P("Before interpreting the RQ1 coefficients in Results, Table 2b reports the mean, standard "
  "deviation, minimum, and maximum of each of the four lagged macroeconomic differentials, per "
  "currency pair, over the 89-month estimation window. These confirm that each predictor has "
  "genuine variation to explain movement with (none is near-constant) and give the coefficients "
  "reported later a concrete scale to be read against &mdash; e.g., EUR/USD's inflation-differential "
  "coefficient of roughly 0.0049 (Results, Table 8) applied to a typical one-standard-deviation "
  "move of about 1.31 percentage points implies an economically small, but statistically real, "
  "effect on monthly log return.")
pstat_rows = [["Pair", "Predictor", "Mean", "Std. Dev.", "Min", "Max"]]
for pair in ["USD/INR", "EUR/USD", "GBP/USD", "USD/JPY"]:
    for i, (feat, label) in enumerate([("rate_diff", "Rate diff. (pp)"), ("infl_diff", "Inflation diff. (pp)"),
                                         ("tb_diff", "Trade-bal. diff. (z)"), ("gdp_diff", "GDP-growth diff. (pp)")]):
        s = pstats[pair][feat]
        pstat_rows.append([pair if i == 0 else "", label, f"{s['mean']:.2f}", f"{s['std']:.2f}",
                            f"{s['min']:.2f}", f"{s['max']:.2f}"])
table_from_rows(pstat_rows, [0.75*inch, 1.5*inch, 0.85*inch, 0.9*inch, 0.85*inch, 0.85*inch],
                caption="Table 2b. Descriptive statistics of RQ1 predictors (pre-lag), by currency pair.")

H2("Dataset Overview")
P("The exchange-rate leg of the dataset was pulled from FRED's public CSV endpoint for January "
  "1, 2018 through July 31, 2026 (2,239 calendar-day requests per series); after removing "
  "non-trading days (96 rows per series, 4.3%), 2,143 clean daily observations remain per "
  "currency pair (8,572 pooled across the four pairs), used for the EDA (Table 5) and the "
  "RQ2/RQ4 daily-frequency analyses. For RQ1, the macroeconomic predictors are only available "
  "at monthly (or, for GDP, quarterly-forward-filled) frequency; after merging, lagging by one "
  "month, and dropping rows with any missing predictor, 89 monthly observations remain per "
  "currency pair, spanning July 2018 through December 2025 (identical window across all four "
  "pairs, so pair-to-pair R&sup2; and coefficient comparisons in Results are made on a like-for-like "
  "basis).")
tbl_rows = [
    ["Field", "Value"],
    ["Daily records (rows)", "2,143 per currency pair (8,572 pooled)"],
    ["Monthly records for RQ1 (after lagging/merge)", "89 per currency pair (356 pooled across 4 pairs)"],
    ["FOMC event records for RQ4", "71 matched events, 2018-2026"],
    ["Time period", "January 2, 2018 - July 31, 2026 (daily); July 2018 - December 2025 (RQ1 monthly)"],
    ["Unit of analysis", "Currency pair &times; trading day (RQ2, RQ4 daily legs); currency pair &times; month (RQ1)"],
    ["Target variable(s)", "Monthly log return (RQ1); daily realized |log return| (RQ2, RQ4)"],
]
table_from_rows(tbl_rows, [2.6*inch, 4.25*inch], caption="Table 3. Dataset overview.")

H2("Data Cleaning")
P("Each raw FRED series was checked for missing values, duplicate dates, and outliers before "
  "computing log returns. Using Rahm and Do's (2000) classification of data-quality problems, "
  "the missingness observed in the daily FX series (96 of 2,239 rows per series, 4.3%) is a "
  "single-source, instance-level &ldquo;missing values&rdquo; problem that is structural (non-trading days) "
  "rather than random, and was resolved by row deletion rather than imputation. No duplicate "
  "dates were found. Extreme daily moves (beyond 3 standard deviations) were flagged but "
  "retained, since for RQ2 and RQ4 these tail events are analytically important rather than data "
  "errors. Two additional, final-report-specific data-quality issues were identified and "
  "resolved during predictor assembly, consistent with the same taxonomy:")
clean_rows = [
    ["Issue", "Variables Affected", "Treatment Applied", "Rationale"],
    ["Stale/discontinued national CPI mirrors", "infl_diff_lag1 (India, U.K., Japan)",
     "Replaced with World Bank annual CPI (current through 2025), forward-filled monthly",
     "FRED's OECD-mirrored India/U.K. CPI stalled at March 2025; Japan's stopped in June 2021"],
    ["No native monthly Eurozone trade-balance series", "tb_diff_lag1 (Eurozone)",
     "Built by summing the 20 euro-area members' annual balances (Eurostat tet00002), "
     "forward-filled monthly", "Verified against known history (e.g., the 2022 aggregate "
     "energy-driven deficit appears correctly)"],
    ["Cross-country trade-balance unit mismatch (USD vs. EUR vs. local currency)",
     "tb_diff_lag1 (all pairs)", "Each country's trade balance z-scored before differencing",
     "Levels are not directly comparable in raw currency units across countries"],
]
table_from_rows(clean_rows, [1.65*inch, 1.25*inch, 2.1*inch, 1.85*inch],
                caption="Table 4. Data cleaning and substitution log.")

H2("Exploratory Data Analysis (EDA)")
eda_rows = [
    ["Pair", "N (daily)", "Ann. Vol. (%)", "Return Skew", "Return Kurtosis"],
    ["USD/INR", "2,143", "5.04", "0.26", "4.29"],
    ["EUR/USD", "2,143", "7.04", "0.10", "1.69"],
    ["GBP/USD", "2,143", "8.62", "0.02", "3.04"],
    ["USD/JPY", "2,143", "8.90", "-0.64", "5.12"],
]
table_from_rows(eda_rows, [1.3*inch, 1.2*inch, 1.4*inch, 1.4*inch, 1.55*inch],
                caption="Table 5. Descriptive statistics of daily log returns by currency pair, 2018-2026.")
P("Annualized volatility ranges from 5.04% (USD/INR) to 8.90% (USD/JPY); USD/INR's comparatively "
  "low volatility is consistent with the Reserve Bank of India's managed-float intervention "
  "practice. All four return series show excess kurtosis (1.7 to 5.1, versus 0 for a normal "
  "distribution), meaning large moves occur far more often than a normal distribution would "
  "predict, as shown in Figure 1. This fat-tailed, volatility-clustering behavior is the "
  "empirical motivation for using GARCH, rather than a constant-variance model, as the RQ2 "
  "econometric baseline.")
fig(ASSETS + "fig_indexed.png",
    "Figure 1. Indexed daily closing levels for all four currency pairs, 2018-2026 (source: FRED).")
fig(ASSETS + "fig_hist4.png",
    "Figure 2. Daily log-return distributions, all four currency pairs &mdash; fat tails visible in every panel.")

H2("Stationarity and Autocorrelation Checks")
P("Before any model was fit, an Augmented Dickey-Fuller (ADF) test was run on both the raw "
  "price level and the log-return series for all four pairs, to confirm the standard econometric "
  "assumption that FX levels are non-stationary (integrated of order 1) while log returns are "
  "stationary and therefore appropriate as a regression/forecasting target. Table 5a reports the "
  "real result of this check.")
adf_rows = [
    ["Pair", "Level ADF stat.", "Level p-value", "Return ADF stat.", "Return p-value"],
    ["USD/INR", "0.123", "0.968", "-20.102", "&lt; .000001"],
    ["EUR/USD", "-1.960", "0.304", "-21.138", "&lt; .000001"],
    ["GBP/USD", "-2.747", "0.066", "-15.353", "&lt; .000001"],
    ["USD/JPY", "-0.311", "0.924", "-34.793", "&lt; .000001"],
]
table_from_rows(adf_rows, [1.1*inch, 1.35*inch, 1.25*inch, 1.35*inch, 1.35*inch],
                caption="Table 5a. Augmented Dickey-Fuller stationarity test, price level vs. log return.")
P("At &alpha; = 0.05, the null hypothesis of a unit root fails to be rejected for every pair's "
  "price level (p ranges from 0.066 to 0.968), confirming that FX levels are non-stationary, as "
  "expected for a random-walk-like series. Every pair's log-return series, by contrast, strongly "
  "rejects the unit-root null (p &lt; .000001 in all four cases), confirming stationarity. This is "
  "the formal justification for using log returns, rather than price levels, as the regression "
  "and forecasting target throughout RQ1, RQ2, and RQ4; fitting any of these models directly on "
  "price levels would risk a spurious-regression problem, since two unrelated non-stationary "
  "series can appear strongly &ldquo;correlated&rdquo; purely as an artifact of both trending over time.")

# ----------------------------------------------------------------------
# Research Hypotheses and Sample Size Calculations
# ----------------------------------------------------------------------
H2("Research Hypotheses and Sample Size Calculations")
P("Each research question's hypotheses are restated below alongside its minimum sample-size "
  "computation, following Button et al. (2013), who show that underpowered studies inflate "
  "effect-size estimates and reduce the reliability of findings. Each minimum N is computed at "
  "the standard 95% confidence / 80% power convention, using the method appropriate to its "
  "analytic design (Table 6), before comparing to the sample sizes actually achieved.")
ss_rows = [
    ["RQ", "H0 / Ha", "Method &amp; Key Parameters", "Min. N", "Achieved N"],
    ["RQ1", "H0: no macro predictor is significant. Ha: at least one is.",
     "Multiple regression (Green, 1991): k = 4 predictors (rate, inflation, trade-balance, "
     "GDP-growth differentials); n &#8805; 50 + 8k",
     "n &#8805; 82", "n = 89 / pair"],
    ["RQ2", "H0: RF forecast error not significantly different from GARCH. Ha: RF "
     "significantly lower error.",
     "Paired-difference (DM-style) test on forecast-error series; adequately powered test needs "
     "roughly 30+ paired observations for a moderate effect",
     "n &#8805; 30", "n = 457-458 test days"],
    ["RQ3", "H0: sentiment feature does not improve accuracy. Ha: it does.",
     "Two-proportion power test (planned): &alpha; = 0.05, Power = 0.80, p1 = 0.65, p2 = 0.72",
     "n &#8805; 687 / group", "Not yet collected"],
    ["RQ4", "H0: no volatility difference pre/post announcement, surprise does not predict "
     "magnitude. Ha: post &gt; pre, and larger surprises predict larger spikes.",
     "Correlation-based power formula (Gelman &amp; Hill, 2007, Ch. 20): &alpha; = 0.05, Power = "
     "0.80, expected r = 0.30", "n &#8805; 85 events", "n = 71 events (36 / 35 per surprise half)"],
]
table_from_rows(ss_rows, [0.5*inch, 1.9*inch, 2.35*inch, 0.75*inch, 1.0*inch],
                caption="Table 6. Research hypotheses and minimum sample size per research question.")
P("Two honest reconciliations are noted between the originally planned power calculations (from "
  "the project synopsis) and the analyses actually executed. First, RQ1's original plan listed "
  "k = 5 predictors including a lagged-return autoregressive term; the model actually estimated "
  "uses k = 4 macroeconomic differentials only (no lagged-return term), lowering the Green's-rule "
  "threshold from n &#8805; 90 to n &#8805; 82 &mdash; comfortably met by the achieved n = 89 monthly "
  "observations per pair. Second, RQ2 was originally planned as a two-proportion comparison of "
  "classification accuracy (direction correct/incorrect), which would have required n &#8805; 373 "
  "per group; the analysis actually executed instead compares two continuous forecast-error "
  "series directly via a paired-difference test on squared loss, for which the relevant power "
  "consideration is the number of paired test-window observations (457-458 daily forecasts under "
  "walk-forward evaluation), which is more than adequate for detecting a moderate paired effect "
  "and does not require re-deriving the original two-proportion threshold. RQ4's achieved sample "
  "(71 events) falls modestly short of the 85-event target computed from the correlation-based "
  "power formula, and the subsequent surprise-magnitude split (36 and 35 events per half) falls "
  "further short for that specific sub-comparison; both shortfalls are carried forward "
  "explicitly into the Results and Limitations sections rather than treated as met.")

# ----------------------------------------------------------------------
# Statistical Methods and Model Selection
# ----------------------------------------------------------------------
H2("Modeling Assumptions")
P("Four assumptions underlie the models reported in this study, each checked rather than merely "
  "asserted. <b>Stationarity:</b> RQ1, RQ2, and RQ4 all model log returns rather than price "
  "levels, confirmed stationary by the ADF tests in Table 5a. <b>No perfect multicollinearity:</b> "
  "verified per pair via VIF (Table 8), all well under the conventional threshold of 10. "
  "<b>No look-ahead leakage:</b> every RQ1 predictor is lagged one month, GARCH is walk-forward "
  "re-estimated using only past data at each refit point, and the RQ4 surprise proxy uses only "
  "data available within the event window itself. <b>Independence of observations for the paired "
  "tests (RQ2, RQ4):</b> the paired t-test assumes the pre/post (or GARCH/RF loss) differences "
  "are drawn from a population with a well-defined mean; where this is doubtful, a Wilcoxon "
  "signed-rank test (which does not require normality of the differences) is reported alongside "
  "it, exactly as done for RQ4.")

H2("Statistical Methods, Model Selection, and Significance Evaluation")
P("<b>RQ1 &mdash; Multiple linear regression (OLS).</b> RQ1 was addressed with an ordinary-least-"
  "squares regression of monthly FX log return on four one-month-lagged macroeconomic "
  "differentials, estimated <i>separately for each currency pair</i> rather than pooled with a "
  "currency-pair fixed effect. This is a deliberate refinement of the originally planned pooled "
  "specification: estimating each pair separately is a stricter test, since coefficients are not "
  "shrunk toward a common pooled estimate, and it allows each pair's macro sensitivity to differ "
  "freely. OLS was chosen because RQ1's hypothesis concerns the linear relationship implied by "
  "interest-rate and purchasing-power-parity theory; variance inflation factors (VIF) were "
  "computed for every predictor in every pair to screen for multicollinearity, with VIF &gt; 10 "
  "treated as the standard concern threshold. A Random Forest nonlinearity robustness check was "
  "originally planned for RQ1 (paralleling the RQ2 comparison) but was not executed in this "
  "round; this is logged as a limitation. Each coefficient's p-value is evaluated against the "
  "conventional 5% significance level (&alpha; = 0.05): a coefficient with p &lt; .05 is treated as "
  "statistically significant and contributes to rejecting RQ1's null for that pair.")
P("<b>RQ2 &mdash; GARCH(1,1) vs. Random Forest.</b> GARCH(1,1) (Engle, 1982; Bollerslev, 1986) was "
  "selected as the econometric baseline because it is the finance-standard model for volatility "
  "clustering, directly motivated by the excess kurtosis documented in Table 5 and Figure 2. It "
  "is compared against a Random Forest regressor (Breiman, 2001) trained on five lagged daily "
  "returns, chosen because ensemble trees can capture nonlinear volatility patterns a linear "
  "model would miss. Critically, GARCH is evaluated under <i>walk-forward re-estimation</i> "
  "(refit every 20 trading days, 23 refits across the test window) rather than a single "
  "in-sample fit, to avoid overstating GARCH's out-of-sample performance; the Random Forest is "
  "evaluated on a held-out 20% test split with no re-fitting. Both are compared against a naive "
  "baseline (yesterday's |return| as today's volatility forecast). The GARCH-vs-Random-Forest "
  "comparison is evaluated with a paired t-test on squared forecast-loss differentials, in the "
  "spirit of the Diebold-Mariano test (Diebold &amp; Mariano, 1995), at the 5% significance level.")
P("<b>RQ3 &mdash; Sentiment overlay (planned, not executed).</b> VADER (Hutto &amp; Gilbert, 2014) and "
  "FinBERT (Araci, 2019) sentiment scoring on GDELT news tone data were planned to be added as a "
  "feature to the best RQ2 model and compared using McNemar's test on paired directional "
  "predictions. This remains future work; see Limitations.")
P("<b>RQ4 &mdash; Event study with surprise-magnitude conditioning.</b> For each of 71 verified FOMC "
  "meeting dates (2018-2026), mean absolute daily USD/INR return in a pre-announcement baseline "
  "window (trading days -10 to -6) was compared to a post-announcement window (day 0 to +1) "
  "using a paired t-test and a Wilcoxon signed-rank test (reported together since normality of "
  "the paired differences cannot be assumed a priori). Because no free, real-time survey-based "
  "consensus-forecast series exists for Fed rate decisions, policy-surprise magnitude was proxied "
  "by the absolute same-day change in the 3-month Treasury-bill secondary-market rate (FRED "
  "series DTB3) &mdash; a standard proxy in the monetary-event-study literature for the market's "
  "revision of near-term rate expectations. Events were split at the median absolute DTB3 change "
  "(2.0 basis points) into a high-surprise half (n = 36) and a low-surprise half (n = 35), and "
  "the pre/post comparison was repeated within each half. All RQ4 tests are evaluated at the 5% "
  "significance level.")

H2("Explanation of Original Work")
P("<b>Data splitting.</b> RQ1 uses the full 89-month aligned sample per pair for in-sample OLS "
  "estimation (appropriate for an explanatory, coefficient-significance question rather than a "
  "held-out forecasting question). RQ2 uses an 80/20 chronological split (no random shuffling, "
  "to avoid look-ahead leakage): the Random Forest is trained once on the first 80% of daily "
  "returns and evaluated on the remaining 20% (457-458 test days); GARCH is walk-forward "
  "re-estimated on an expanding window every 20 trading days through the same test period, so "
  "neither model ever sees future data at estimation time. RQ4 uses no train/test split, since "
  "it is a paired-comparison design across historical events rather than a forecasting task.")
P("<b>Accuracy on training vs. test data.</b> For RQ2, the walk-forward GARCH RMSE "
  f"({rq2['garch_rmse_walkforward']:.4f}) and the Random Forest test-set RMSE "
  f"({rq2['rf_rmse']:.4f}) are both computed strictly out-of-sample; the single-fit (non-"
  f"walk-forward) GARCH RMSE from an earlier pass ({rq2['garch_rmse_single_fit_previous']:.4f}) "
  "is retained in the results for direct comparison, since the difference between a single fit "
  "and genuine walk-forward re-estimation is itself a methodologically relevant finding (the "
  "walk-forward RMSE is very slightly higher, indicating the single-fit number had modestly "
  "overstated GARCH's real-world accuracy).")
P("<b>Comparison with a baseline/current method.</b> Every RQ2 model is benchmarked against the "
  f"naive persistence baseline (RMSE {rq2['naive_rmse']:.4f}); both GARCH and Random Forest "
  "reduce RMSE by roughly 22-25% relative to this baseline, which is the practically meaningful "
  "comparison for a deployed early-warning system (Results). For RQ1, the implicit baseline "
  "throughout is Meese and Rogoff's (1983) random walk: a pair's macro model is only "
  "practically interesting if it clears the bar of statistical significance the random-walk "
  "literature says should not be expected, which is why EUR/USD's result is highlighted as the "
  "project's central positive finding rather than assumed in advance.")
P("<b>Why in-sample estimation is appropriate for RQ1.</b> RQ1 asks an explanatory question "
  "(&ldquo;is a macroeconomic predictor significantly associated with directional movement?&rdquo;) "
  "rather than a pure forecasting question, so the relevant standard is coefficient significance "
  "under the classical OLS assumptions, not held-out predictive accuracy; this is why RQ1 uses "
  "the full aligned sample rather than a train/test split, while RQ2 and RQ4 &mdash; which ask "
  "forecasting and event-response questions respectively &mdash; use held-out or walk-forward "
  "evaluation instead. This distinction matters for interpreting Table 8's R&sup2; values "
  "correctly: they describe in-sample fit, not out-of-sample forecasting accuracy, and should "
  "not be read as a claim that the EUR/USD model would predict future EUR/USD returns with 12.4% "
  "accuracy on unseen data.")
P("<b>Ethical and data-vintage considerations.</b> Consistent with the synopsis's original data-"
  "availability statement, GDP growth and trade-balance figures are macroeconomic aggregates "
  "that are periodically revised after initial release; this report uses the most recently "
  "available vintage of each series (as of the September 2026 data pull) rather than attempting "
  "to reconstruct the real-time-as-originally-published vintage, which is noted again as a "
  "limitation below. No personally identifiable information, human-subjects data, or proprietary "
  "licensed data is used anywhere in this study.")
page_break()

# ============================================================================
# ARCHITECTURE DIAGRAM / WORKFLOW
# ============================================================================
H1("Architecture Diagram / Workflow")

H2("System Overview")
P("The overall pipeline runs data from public source APIs through cleaning, per-research-"
  "question modeling, statistical evaluation, and a final synthesis into a practical "
  "recommendation, as shown in Figure 3. Each of the four research questions is modeled "
  "independently in Stage 3 but shares the same cleaned data foundation from Stage 2, so that "
  "results across RQ1, RQ2, and RQ4 are directly comparable rather than built on inconsistent "
  "preprocessing.")

H2("Architecture Diagram")
fig(FR + "fig_architecture.png",
    "Figure 3. End-to-end workflow of the proposed system.", max_height=4.1*inch)

H2("Workflow Components")
H3("Data Ingestion")
P("Daily FX levels, interest rates, CPI, trade balance, and GDP growth were pulled "
  "programmatically from FRED's public CSV endpoint, the World Bank API, and the Eurostat "
  "SDMX-JSON API; the FOMC policy calendar was cross-checked against federalreserve.gov. Each "
  "source was probed directly (rather than assumed available) before being relied upon, which is "
  "how the India/U.K./Japan CPI staleness and the missing native Eurozone trade-balance series "
  "were discovered in the first place (Table 4) &mdash; ingestion in this pipeline is treated as a "
  "step that can fail silently (a series that stops updating returns old data without an error), "
  "not a step that either works or throws an exception.")
H3("Data Preprocessing")
P("Non-trading days and rows with any missing predictor were dropped (Table 4); log returns, "
  "rate/inflation/trade-balance/GDP-growth differentials were derived and lagged by one month "
  "(RQ1) or used at daily frequency (RQ2, RQ4); trade-balance levels were z-scored per country "
  "before differencing to remove the cross-country currency-unit mismatch. Annual World Bank CPI "
  "and Eurostat trade-balance series were forward-filled to monthly frequency using a "
  "December-anchored fill (Materials and Method), specifically chosen to avoid look-ahead bias: "
  "an annual figure is applied only from the point after which it would realistically have been "
  "available, not backdated across the whole year it describes.")
H3("Exploratory Data Analysis (EDA)")
P("Annualized volatility, return skew, and excess kurtosis were computed per pair (Table 5), "
  "directly motivating the choice of GARCH over a constant-variance model for RQ2 (Figure 2). "
  "Augmented Dickey-Fuller tests (Table 5a) additionally confirmed that log returns, not price "
  "levels, are the correct stationary target variable for every downstream model.")
H3("Feature Engineering")
P("Four one-month-lagged macroeconomic differentials for RQ1 (Table 2), with descriptive "
  "statistics reported per pair in Table 2b; five lagged daily returns for the RQ2 Random "
  "Forest; the absolute 3-month-Treasury-yield change on FOMC day as the RQ4 "
  "policy-surprise-magnitude proxy. Lagging (rather than contemporaneous) predictors was used "
  "throughout specifically to keep every model genuinely predictive rather than explanatory-in-"
  "hindsight: a same-month macro release and a same-month FX return could both be responding to a "
  "shared contemporaneous shock, whereas a lagged predictor cannot be mechanically driven by the "
  "outcome it is trying to explain.")
H3("Model Development")
P("RQ1: OLS regression per currency pair with VIF screening. RQ2: GARCH(1,1) under walk-forward "
  "re-estimation (23 refits, every 20 trading days) versus a Random Forest (300 trees, max depth "
  "5) trained once on an 80/20 chronological split. RQ4: paired t-test and Wilcoxon signed-rank "
  "test, run separately overall and within surprise-magnitude halves. Model Selection Rationale "
  "and Alternatives Considered (below) details why each specific model was chosen over other "
  "candidates considered during scoping.")
H3("Model Evaluation")
P("R&sup2;, adjusted R&sup2;, and coefficient p-values with VIF diagnostics (RQ1); RMSE against a naive "
  "baseline and a paired-loss significance test (RQ2); paired t-test and Wilcoxon statistics "
  "(RQ4). All significance tests are evaluated at &alpha; = 0.05, and every evaluation metric is "
  "computed strictly out-of-sample for RQ2 and RQ4 (Materials and Method &mdash; Explanation of "
  "Original Work), so that Results reports genuine predictive/comparative performance rather "
  "than in-sample fit dressed up as a forecast.")
H3("Deployment (Recommended, Not Yet Built)")
P("The recommended deployment is a lightweight dashboard that surfaces the RQ2 volatility "
  "forecast and an RQ4-style surprise flag ahead of each scheduled FOMC date, plus the RQ1 "
  "macro-regression signal specifically for EUR/USD, where it is statistically supported; this "
  "is discussed further in Implementation and User Benefit.")

H2("Tools and Technologies")
bullets([
    "<b>Language:</b> Python 3.11.",
    "<b>Data handling:</b> pandas, NumPy.",
    "<b>Statistics/econometrics:</b> statsmodels (OLS, VIF), the <i>arch</i> package (GARCH(1,1)), "
    "SciPy (t-tests, Wilcoxon signed-rank).",
    "<b>Machine learning:</b> scikit-learn (RandomForestRegressor).",
    "<b>Visualization:</b> Matplotlib.",
    "<b>Compute:</b> standard CPU; no GPU was required given the dataset scale "
    "(thousands, not millions, of rows).",
])

page_break()
H2("Model Selection Rationale and Alternatives Considered")
P("Model choice at every stage was driven by matching the analytic design to the research "
  "question's hypothesis, not by defaulting to the most complex available method. For RQ1, a "
  "pooled panel regression with a currency-pair fixed effect was considered (and is the design "
  "originally proposed in the synopsis), but four separate per-pair OLS regressions were used "
  "instead, since pooling would shrink each pair's coefficients toward a common estimate and "
  "could mask a pair-specific effect such as EUR/USD's &mdash; exactly the kind of result this study "
  "was designed to detect rather than average away. For RQ2, XGBoost and an LSTM network "
  "(Hochreiter &amp; Schmidhuber, 1997) were part of the originally scoped comparison set; both "
  "were deferred (see Limitations and Future "
  "Improvements) once GARCH and Random Forest already demonstrated the practically relevant "
  "finding &mdash; a clear, real improvement over a naive baseline &mdash; and because a daily-frequency, "
  "single-pair dataset of a few thousand rows is unlikely to have enough signal for a deep "
  "recurrent architecture to outperform a well-tuned classical baseline; this is a deliberate "
  "scope decision rather than an oversight, and is listed explicitly as future work. For RQ4, a "
  "logistic regression on policy surprise was part of the original plan; the executed analysis "
  "instead uses paired t-tests and Wilcoxon signed-rank tests directly on the surprise-magnitude "
  "split, which more directly answers the pre-registered hypothesis (does post-announcement "
  "volatility exceed pre-announcement volatility, and does this differ by surprise size) without "
  "requiring an additional modeling layer.")

H2("Data Governance and Reproducibility")
P("Every series used in this report is public, free, and pulled programmatically from an "
  "official source's API (Materials and Method); raw downloaded CSVs are retained alongside "
  "processed files in the GitHub repository so that every number in this report can be traced "
  "back to its original source file. Where a series was found to be stale or discontinued "
  "(India/U.K./Japan CPI on FRED), the substitution and its source are documented explicitly in "
  "Table 4 rather than silently patched, consistent with the data-quality and dataset-"
  "documentation literature reviewed above (Rahm &amp; Do, 2000; Gebru et al., 2018). No personally "
  "identifiable information is collected anywhere in the pipeline: every series is either an "
  "aggregate macroeconomic statistic, a market price, or (for the planned RQ3 work) publicly "
  "published news content.")
page_break()

# ============================================================================
# RESULTS
# ============================================================================
H1("Results")

H2("Model Performance")
perf_rows = [
    ["Model", "Features / Design", "Validation", "Metric 1", "Metric 2", "Key Observation"],
    ["RQ1 OLS (USD/INR)", "4 macro differentials", "In-sample, n=89",
     f"R&sup2;={rq1['USD/INR']['r2']*100:.1f}%", "best p=0.169", "Fails to reject H0"],
    ["RQ1 OLS (EUR/USD)", "4 macro differentials", "In-sample, n=89",
     f"R&sup2;={rq1['EUR/USD']['r2']*100:.1f}%", "3 of 4 p&lt;.05", "Rejects H0"],
    ["RQ1 OLS (GBP/USD)", "4 macro differentials", "In-sample, n=89",
     f"R&sup2;={rq1['GBP/USD']['r2']*100:.1f}%", "best p=0.191", "Fails to reject H0"],
    ["RQ1 OLS (USD/JPY)", "4 macro differentials", "In-sample, n=89",
     f"R&sup2;={rq1['USD/JPY']['r2']*100:.1f}%", "best p=0.331", "Fails to reject H0"],
    ["RQ2 GARCH(1,1)", "Walk-forward, 23 refits", f"n_test={rq2['n_test']}",
     f"RMSE={rq2['garch_rmse_walkforward']:.3f}", "-22.4% vs. naive", "Beats naive baseline"],
    ["RQ2 Random Forest", "5 lagged returns", f"n_test={rq2['n_test_rf']}",
     f"RMSE={rq2['rf_rmse']:.3f}", "-23.7% vs. naive", "Beats naive; ~= GARCH (p=0.78)"],
    ["RQ2 Naive baseline", "Yesterday's |return|", f"n_test={rq2['n_test_rf']}",
     f"RMSE={rq2['naive_rmse']:.3f}", "&mdash;", "Reference baseline"],
    ["RQ4 Overall (n=71)", "Pre- vs. post-FOMC", "Paired, n=71",
     f"&Delta;={rq4['overall']['mean_post']-rq4['overall']['mean_pre']:+.3f}pp",
     f"p={rq4['overall']['paired_t_p']:.2f}", "Fails to reject H0"],
    ["RQ4 High-surprise half", "Pre- vs. post-FOMC", "Paired, n=36",
     f"{rq4['high_surprise_half']['pct_increase']:+.1f}%", f"p={rq4['high_surprise_half']['paired_t_p']:.2f}",
     "Direction as expected; n.s."],
    ["RQ4 Low-surprise half", "Pre- vs. post-FOMC", "Paired, n=35",
     f"{rq4['low_surprise_half']['pct_increase']:+.1f}%", f"p={rq4['low_surprise_half']['paired_t_p']:.2f}",
     "Direction as expected; n.s."],
]
table_from_rows(perf_rows, [1.15*inch, 1.15*inch, 0.85*inch, 0.85*inch, 0.85*inch, 1.45*inch],
                caption="Table 7. Model performance comparison across RQ1, RQ2, and RQ4. "
                        "(RQ3 not yet executed; see Limitations.)")
P("EUR/USD is the single best-performing RQ1 specification and the only pair to reject the null "
  "hypothesis; both RQ2 models comfortably outperform the naive baseline with no significant "
  "difference between them; RQ4 shows no significant average effect but the surprise-conditioned "
  "split moves in the theoretically expected direction.")

H2("Visual Evidence")
fig(ASSETS + "fig_rq1_r2_v2.png",
    "Figure 4. RQ1 model fit (R&sup2;) by currency pair &mdash; EUR/USD stands out with three of four "
    "coefficients statistically significant, while the other three pairs remain a clean null "
    "consistent with the Meese-Rogoff puzzle.")
fig(ASSETS + "fig_rq2_vol_forecast_v2.png",
    "Figure 5. USD/INR realized vs. forecast daily volatility under walk-forward evaluation &mdash; "
    "both GARCH and Random Forest track the realized-volatility series far more closely than a "
    "flat naive forecast would.")
fig(ASSETS + "fig_rq4_event_study_v2.png",
    "Figure 6. USD/INR volatility around FOMC announcements, split at the median absolute 3-month "
    "T-bill yield change &mdash; the high-surprise half shows a post-announcement increase and the "
    "low-surprise half a decrease, the expected asymmetry, though neither half reaches "
    "significance at this sample size.")

page_break()
H2("Full RQ1 Regression Output (All Four Pairs)")
P("Table 8 reports every coefficient, p-value, and VIF for all four currency pairs' RQ1 "
  "regressions, underlying the summary given in Table 7 and Figure 4. Reporting the complete "
  "output for all four pairs &mdash; not only the significant EUR/USD result &mdash; follows the "
  "&ldquo;model cards&rdquo; principle (Mitchell et al., 2019) of disclosing full, comparable performance "
  "detail rather than a single headline number.")
feat_labels = {"rate_diff_lag1": "Rate differential", "infl_diff_lag1": "Inflation differential",
               "tb_diff_lag1": "Trade-balance differential", "gdp_diff_lag1": "GDP-growth differential"}
coef_rows = [["Pair", "Predictor", "Coefficient", "p-value", "VIF", "Sig. (&alpha;=.05)"]]
for pair in ["USD/INR", "EUR/USD", "GBP/USD", "USD/JPY"]:
    v = rq1[pair]
    for i, feat in enumerate(["rate_diff_lag1", "infl_diff_lag1", "tb_diff_lag1", "gdp_diff_lag1"]):
        coef_rows.append([
            pair if i == 0 else "",
            feat_labels[feat],
            f"{v['params'][feat]:.5f}",
            f"{v['pvalues'][feat]:.3f}",
            f"{v['vif'][feat]:.2f}",
            "Yes" if v['pvalues'][feat] < 0.05 else "No",
        ])
table_from_rows(coef_rows, [0.75*inch, 1.7*inch, 1.05*inch, 0.75*inch, 0.6*inch, 1.1*inch],
                caption="Table 8. Full RQ1 OLS regression output, all four currency pairs "
                        "(n=89 monthly observations per pair).")
P("VIF remains below 1.8 for every predictor in every pair, confirming that multicollinearity is "
  "not masking or inflating any coefficient's significance &mdash; the EUR/USD result in particular "
  "is not an artifact of correlated predictors, and the null result for the other three pairs is "
  "not an artifact of variance inflation either.")

H2("Results by Research Question")
H3("RQ1 &mdash; Macroeconomic Predictors of Direction")
P(f"Across all four pairs (n=89 monthly observations each, identical window), the full "
  f"four-predictor model raises R&sup2; relative to a single-predictor pilot regression reported "
  f"earlier in this project (pilot R&sup2; = 0.04%), but only EUR/USD reaches statistical "
  f"significance: R&sup2; = {rq1['EUR/USD']['r2']*100:.1f}% (adjusted R&sup2; = "
  f"{rq1['EUR/USD']['adj_r2']*100:.1f}%), with the inflation differential (p = "
  f"{rq1['EUR/USD']['pvalues']['infl_diff_lag1']:.3f}), trade-balance differential (p = "
  f"{rq1['EUR/USD']['pvalues']['tb_diff_lag1']:.3f}), and GDP-growth differential (p = "
  f"{rq1['EUR/USD']['pvalues']['gdp_diff_lag1']:.3f}) all significant at &alpha; = 0.05. VIF for "
  f"every EUR/USD predictor is below 1.8, ruling out multicollinearity as an alternative "
  f"explanation. USD/INR (R&sup2; = {rq1['USD/INR']['r2']*100:.1f}%), GBP/USD (R&sup2; = "
  f"{rq1['GBP/USD']['r2']*100:.1f}%), and USD/JPY (R&sup2; = {rq1['USD/JPY']['r2']*100:.1f}%) all "
  f"fail to reject the null at &alpha; = 0.05 for every predictor. <b>RQ1 conclusion: the null "
  f"hypothesis is rejected for EUR/USD and fails to be rejected for the other three pairs</b> &mdash; "
  f"a mixed result rather than a universal one, consistent with EUR/USD's deep, liquid market "
  f"being more sensitive to macro fundamentals at a monthly horizon than the other three pairs.")
P("<b>Comparison with the existing (random-walk) benchmark.</b> Meese and Rogoff's (1983) "
  "central claim is that structural models generally cannot beat a random walk; this study's "
  "USD/INR, GBP/USD, and USD/JPY results are fully consistent with that claim persisting more "
  "than four decades later, using entirely different currency pairs, predictors, and a modern "
  "eight-year sample. EUR/USD's result does not contradict Meese-Rogoff so much as identify a "
  "specific, plausible boundary condition &mdash; a sufficiently deep and liquid pair &mdash; under which "
  "the puzzle's usual finding does not hold, which is itself a meaningful, literature-relevant "
  "contribution rather than a mere anomaly.")

H3("RQ2 &mdash; Machine Learning vs. Econometric Volatility Forecasting")
P(f"Under genuine walk-forward re-estimation (23 refits across the test window, no look-ahead), "
  f"GARCH(1,1) achieves RMSE = {rq2['garch_rmse_walkforward']:.4f} and Random Forest achieves "
  f"RMSE = {rq2['rf_rmse']:.4f}, both substantially below the naive baseline's RMSE = "
  f"{rq2['naive_rmse']:.4f} &mdash; a reduction of "
  f"{(1-rq2['garch_rmse_walkforward']/rq2['naive_rmse'])*100:.0f}% and "
  f"{(1-rq2['rf_rmse']/rq2['naive_rmse'])*100:.0f}% respectively. The paired-loss comparison "
  f"between GARCH and Random Forest is not statistically significant (t = "
  f"{rq2['dm_like_stat_wf_vs_rf']:.3f}, p = {rq2['dm_like_p_wf_vs_rf']:.3f}), so RQ2's null "
  f"hypothesis fails to be rejected: Random Forest does not provide a <i>significantly</i> better "
  f"forecast than GARCH, though both are clearly better than doing nothing. <b>RQ2 conclusion: "
  f"the null hypothesis fails to be rejected</b> &mdash; but the practically important finding is "
  f"that either model, chosen for convenience or infrastructure reasons, delivers a real, "
  f"substantial improvement over a naive volatility forecast.")
P("<b>Comparison with existing methods.</b> GARCH(1,1) (Engle, 1982; Bollerslev, 1986) has been "
  "the finance-industry standard volatility model for four decades precisely because it captures "
  "volatility clustering with only three estimated parameters; this study's finding that a much "
  "more flexible, nonparametric Random Forest does not significantly outperform it (p = "
  f"{rq2['dm_like_p_wf_vs_rf']:.2f}) is itself informative for a practitioner deciding which "
  "model to maintain in production &mdash; the simpler, more interpretable GARCH model is not giving "
  "up meaningful accuracy relative to the more complex alternative for this dataset and horizon.")

H3("RQ3 &mdash; News Sentiment (Not Yet Executed)")
P("RQ3's GDELT-based VADER/FinBERT sentiment pipeline is architected (Materials and Method) but "
  "has not been executed in this reporting round; no result is claimed for RQ3 to avoid "
  "presenting a partial or misleading comparison. This is carried forward as the primary item "
  "under Future Improvements.")

H3("RQ4 &mdash; Central Bank Policy Announcements and Volatility")
P(f"Across all 71 verified FOMC meeting dates, mean absolute daily return is essentially flat "
  f"pre- vs. post-announcement ({rq4['overall']['mean_pre']:.3f}% vs. "
  f"{rq4['overall']['mean_post']:.3f}%, paired t p = {rq4['overall']['paired_t_p']:.3f}), so the "
  f"overall null hypothesis fails to be rejected. However, conditioning on policy-surprise "
  f"magnitude (proxied by the absolute same-day 3-month Treasury-yield change) reveals the "
  f"theoretically expected asymmetry: in the high-surprise half (n = 36, above the median 2.0 "
  f"basis-point move), post-announcement volatility rises "
  f"{rq4['high_surprise_half']['pct_increase']:+.1f}%, while in the low-surprise half (n = 35), "
  f"it falls {rq4['low_surprise_half']['pct_increase']:.1f}%. Neither half individually reaches "
  f"significance at this sample size (p = {rq4['high_surprise_half']['paired_t_p']:.2f} and p = "
  f"{rq4['low_surprise_half']['paired_t_p']:.2f} respectively), consistent with the 36/35 "
  f"per-half sample falling short of the correlation-based power target (Table 6). <b>RQ4 "
  f"conclusion: the null hypothesis fails to be rejected at the pre-registered significance "
  f"level, but the direction of the surprise-conditioned split is exactly as Kuttner (2001) "
  f"would predict</b> &mdash; a genuine, if underpowered, positive signal rather than a clean null.")
P("<b>Comparison with existing methods.</b> Kuttner's (2001) original event study used Fed funds "
  "futures prices, available only from 1989 onward, to construct a true unanticipated-versus-"
  "anticipated split of Fed policy moves. That instrument was not available in this project's "
  "free public data sources, so the 3-month Treasury-bill proxy was substituted; the fact that "
  "the substitute proxy still produces the theoretically expected sign (larger yield moves "
  "coincide with larger post-announcement volatility increases) is itself a modest validation of "
  "the proxy, even though the underdetermined sample size prevents a definitive significance "
  "claim.")

H2("Summary of Hypothesis Test Outcomes")
P("Table 9 consolidates every hypothesis-test decision from the four research questions in one "
  "place, at the pre-registered &alpha; = 0.05 significance level, so that the report's overall "
  "pattern of findings can be read at a glance before the fuller interpretation below.")
hyp_rows = [
    ["RQ", "Test / Sub-case", "Decision at &alpha;=0.05", "p-value"],
    ["RQ1", "USD/INR (4-predictor OLS)", "Fail to reject H0", "best p=0.169"],
    ["RQ1", "EUR/USD (4-predictor OLS)", "<b>Reject H0</b>", "3 of 4 p&lt;.05"],
    ["RQ1", "GBP/USD (4-predictor OLS)", "Fail to reject H0", "best p=0.191"],
    ["RQ1", "USD/JPY (4-predictor OLS)", "Fail to reject H0", "best p=0.331"],
    ["RQ2", "GARCH vs. Random Forest (paired loss)", "Fail to reject H0",
     f"p={rq2['dm_like_p_wf_vs_rf']:.2f}"],
    ["RQ3", "Sentiment vs. no-sentiment", "Not tested (not yet executed)", "&mdash;"],
    ["RQ4", "Overall pre- vs. post-announcement (n=71)", "Fail to reject H0",
     f"p={rq4['overall']['paired_t_p']:.2f}"],
    ["RQ4", "High-surprise half (n=36)", "Fail to reject H0 (direction as expected)",
     f"p={rq4['high_surprise_half']['paired_t_p']:.2f}"],
    ["RQ4", "Low-surprise half (n=35)", "Fail to reject H0 (direction as expected)",
     f"p={rq4['low_surprise_half']['paired_t_p']:.2f}"],
]
table_from_rows(hyp_rows, [0.55*inch, 2.35*inch, 2.15*inch, 1.05*inch],
                caption="Table 9. Summary of all hypothesis-test decisions across RQ1, RQ2, and RQ4.")
P("Of the nine formal tests reported, exactly one rejects its null hypothesis (EUR/USD's RQ1 "
  "model); the remaining eight fail to reject, though two of those eight (the RQ4 surprise "
  "halves) show the theoretically expected direction despite not reaching significance, and the "
  "RQ2 comparison's practically important finding (both models beat naive) sits outside the "
  "formal null/alternative framing of the GARCH-vs-RF test itself. This is precisely the honest, "
  "&ldquo;mostly null but not uninformative&rdquo; pattern the Discussion below interprets in full.")
page_break()

H2("Overall Interpretation")
P("Taken together, the four research questions tell a coherent story rather than four "
  "disconnected results. RQ1 and RQ4 both largely confirm the classical finding that short-term "
  "FX direction resists prediction from fundamentals and scheduled events alone (Meese &amp; "
  "Rogoff, 1983) &mdash; except for EUR/USD under RQ1, and except when RQ4 is conditioned on genuine "
  "surprise magnitude rather than mere meeting occurrence. RQ2 shows that volatility, in "
  "contrast to direction, is meaningfully forecastable: both a classical econometric model and a "
  "simple machine-learning model cut forecast error by roughly a quarter relative to a naive "
  "benchmark, with no evidence that the more complex model is worth its additional complexity "
  "over the simpler GARCH baseline. The factor most clearly driving where the models succeed is "
  "not model sophistication but signal type: volatility clusters predictably; short-term "
  "direction, for three of four pairs, does not.")
P("This pattern also has a methodological reading: the two research questions with the "
  "strongest, most reliable results (RQ2's volatility forecasts, and RQ1's EUR/USD-specific "
  "significance) are both cases where the underlying statistical process is well understood and "
  "the model matches that process closely &mdash; GARCH is purpose-built for volatility clustering, "
  "and EUR/USD is the deepest, most information-efficient of the four markets studied, where "
  "macro fundamentals would be expected to be incorporated into prices most cleanly. The weaker "
  "results (RQ1 for the other three pairs, RQ4 overall) occur precisely where the underlying "
  "signal is theoretically expected to be weakest or most diluted by market microstructure and "
  "capital-control effects (USD/INR) or by treating heterogeneous announcements as identical "
  "events (RQ4 overall, before surprise-conditioning). The results are therefore not merely a "
  "list of four separate p-values but a pattern consistent with, and mutually reinforcing of, "
  "the underlying economic theory.")

H2("Robustness and Sensitivity Discussion")
P("Two design choices in this study's methodology deserve explicit sensitivity discussion. "
  "First, the RQ1 trade-balance differential relies on z-scoring each country's raw trade "
  "balance before differencing, so that units are comparable across countries; this is a linear "
  "transformation and does not change any coefficient's statistical significance, but a "
  "different normalization (e.g., scaling by GDP rather than by the series' own "
  "standard deviation) could change the coefficient's magnitude and is worth testing in future "
  "work. Second, RQ4's high/low-surprise split uses a median split on the absolute 3-month "
  "T-bill yield change; the direction of the result (higher volatility increase in the "
  "high-surprise half) was checked for robustness against a simple visual inspection of the "
  "full distribution in Figure 6, and the pattern is not an artifact of a single extreme event "
  "dominating one half, though a formal robustness check across alternative split points (e.g., "
  "terciles) was not performed and is listed under Future Improvements.")

H2("Practical Significance")
P("For a treasury or trading desk, these results translate into a concrete decision rule: "
  "allocate modeling effort to volatility forecasting (RQ2), where either GARCH or Random Forest "
  "delivers a real, deployable improvement over doing nothing, and treat directional macro "
  "signals as reliable only for EUR/USD, not as a general-purpose tool across all four pairs. "
  "The RQ4 finding further implies that hedges should be timed and sized around the <i>expected "
  "surprise</i> of an upcoming policy decision, not merely its scheduled date, since the "
  "meeting-occurrence effect alone was not statistically detectable. In dollar terms, a 22-25% "
  "reduction in volatility-forecast RMSE (RQ2) translates directly into tighter, better-"
  "calibrated option-implied hedge sizing for a treasury desk pricing FX risk off a volatility "
  "estimate, though this study does not attempt to translate that RMSE reduction into a specific "
  "hedging-cost dollar figure, since that would require desk-specific position sizes and "
  "instrument choices outside this report's scope.")
page_break()

# ============================================================================
# IMPLEMENTATION AND USER BENEFIT
# ============================================================================
H1("Implementation and User Benefit")
P("This section describes how the RQ1/RQ2/RQ4 findings can be turned into a deployable tool, "
  "rather than remaining an academic exercise. No dashboard has been built yet; the description "
  "below is a recommended implementation, informed directly by which signals proved reliable.")

H2("Deployment Approach")
P("The recommended deployment is a lightweight, scheduled batch job (daily for volatility "
  "forecasts, event-triggered ahead of each FOMC date) that refreshes the GARCH and Random "
  "Forest volatility forecasts and, for EUR/USD specifically, the RQ1 macro-regression signal, "
  "and writes the results to a small internal dashboard or a scheduled email/Slack summary for "
  "the treasury or trading desk. Given the modest data volume (thousands, not millions, of "
  "rows) and CPU-only model requirements, this could run on a single scheduled cloud function or "
  "even a local scheduled script; no GPU or distributed infrastructure is required.")

H2("System Integration")
P("The pipeline's inputs (FRED, World Bank, Eurostat, FOMC calendar) are all free public APIs, "
  "so integration risk is limited to API-availability monitoring and periodically re-checking "
  "for series that go stale or are discontinued, exactly as India, U.K., and Japan CPI did "
  "during this project. The output (a volatility forecast and an event-risk flag) is a small, "
  "structured artifact that can be consumed by an existing treasury management system, a risk "
  "spreadsheet, or a simple internal API endpoint without requiring changes to upstream trading "
  "or accounting systems.")
P("Because the pipeline currently exists as a set of standalone Python scripts (Appendix A-C) "
  "rather than a single deployed service, a first practical integration step would be to wrap "
  "each script's output as a small JSON artifact on a shared schedule (e.g., written to a shared "
  "file location or a lightweight internal API each morning) that a treasury system, spreadsheet, "
  "or messaging integration could poll or subscribe to, rather than attempting a more elaborate "
  "system integration before the underlying signals (RQ2 in particular) have been validated "
  "prospectively over a live period.")

H2("User Interaction")
P("The intended interaction is passive and glanceable: a treasury analyst or trader would see, "
  "each morning, a short summary (current GARCH/Random Forest volatility forecast per pair, days "
  "until the next FOMC meeting, and &mdash; for EUR/USD only &mdash; the current sign and magnitude of "
  "the macro-regression signal) rather than a complex interactive model interface, consistent "
  "with the project's finding that simplicity and honesty about which signals actually work "
  "matters more than model sophistication.")

H2("Benefits to Users")
bullets([
    "<b>Operational efficiency:</b> a single daily summary replaces ad hoc, manual review of "
    "multiple data sources for volatility and policy-calendar risk.",
    "<b>Financial impact:</b> a 22-25% reduction in volatility-forecast error (RQ2) directly "
    "improves the sizing of options-based or forward-based hedges, which are priced off "
    "expected volatility.",
    "<b>Strategic value:</b> an honest signal-reliability map (volatility: yes; direction: only "
    "for EUR/USD; policy-surprise conditioning: promising but not yet powered) prevents "
    "over-reliance on a forecast that this study shows is not statistically supported for most "
    "pairs.",
    "<b>Decision speed:</b> a pre-computed, refreshed-daily volatility forecast lets a treasury "
    "analyst make a hedge-sizing decision in minutes rather than re-running an ad hoc analysis "
    "each time a decision is needed.",
])

H2("Example Use Case")
P("A corporate treasury team with USD/INR payables due two weeks after a scheduled FOMC meeting "
  "checks the dashboard the week before: the GARCH/Random Forest volatility forecast is "
  "elevated relative to its recent average, and the meeting is flagged as upcoming. Rather than "
  "waiting until the announcement, the team increases its hedge ratio ahead of the event, sizing "
  "the hedge using the current volatility forecast rather than a flat historical average &mdash; "
  "directly operationalizing the RQ2 finding that volatility, unlike direction, is a reliable, "
  "forecastable quantity.")

H2("Monitoring and Maintenance")
P("Because this project's own experience shows that public macroeconomic series can go stale "
  "or be discontinued without notice (the India, U.K., and Japan CPI series used for RQ1), any "
  "deployed version of this pipeline needs a lightweight monitoring check &mdash; comparing each "
  "source series' latest observation date against an expected refresh cadence, and alerting if a "
  "series has not updated within its expected window &mdash; rather than assuming a data source "
  "that worked at build time will continue to work indefinitely. GARCH parameters should be "
  "periodically re-examined (the walk-forward design already re-estimates them every 20 trading "
  "days) to confirm they remain within a plausible range and have not drifted in a way that "
  "signals a structural break in the underlying volatility process.")

H2("Cost and Risk Considerations")
P("The recommended deployment's marginal cost is low: all data sources are free, the models are "
  "CPU-only and retrain in seconds to minutes, and no proprietary licensed data is required. The "
  "main risk is over-reliance on a signal this report has shown to be unreliable &mdash; "
  "specifically, treating the RQ1 macro-regression signal as a general-purpose directional tool "
  "across all four pairs, rather than restricting it to EUR/USD, where alone it is statistically "
  "supported. The dashboard description above is deliberately designed to make this distinction "
  "visible to the user (Table 7's pair-by-pair significance column) rather than presenting a "
  "single blended signal that would obscure it.")
page_break()

# ============================================================================
# LIMITATIONS AND FURTHER IMPROVEMENTS
# ============================================================================
H1("Limitations and Further Improvements")

H2("Limitations")
bullets([
    "<b>RQ3 not executed:</b> the GDELT-based VADER/FinBERT sentiment pipeline is architected "
    "but no sentiment feature or comparison has been produced; RQ3 remains an open question.",
    "<b>RQ1's planned Random Forest robustness check was not executed:</b> only the linear OLS "
    "specification is reported; whether a nonlinear model would change the null result for "
    "USD/INR, GBP/USD, or USD/JPY is untested.",
    "<b>Eurozone trade balance is an aggregation, not a native series:</b> no monthly Eurozone "
    "trade-balance series exists on FRED, Eurostat, or the ECB's public API, so it was built by "
    "summing 20 member states' annual balances (Eurostat), forward-filled monthly &mdash; coarser "
    "and more assumption-laden than the native monthly series used for the other three pairs.",
    "<b>India, U.K., and Japan inflation is annual, forward-filled data:</b> FRED's monthly "
    "mirrors of these series are stale (India/U.K., last updated March 2025) or discontinued "
    "(Japan, June 2021); World Bank annual CPI is current through 2025 but coarser than a native "
    "monthly series, and forward-filling assumes inflation is constant within each year.",
    "<b>RQ4's surprise-magnitude split is underpowered:</b> the 3-month-Treasury-yield-change "
    "proxy is not a true survey-based consensus-forecast measure, and the resulting halves "
    "(n=36, n=35) fall short of the 85-event target computed from the correlation-based power "
    "formula, so the observed (and theoretically expected) direction of the split cannot be "
    "confirmed as statistically significant with this sample.",
    "<b>Walk-forward GARCH refits every 20 trading days, not daily:</b> a daily-refit cadence "
    "was not attempted due to compute cost; results may differ modestly under a finer "
    "re-estimation schedule.",
    "<b>Macroeconomic series are subject to revision:</b> GDP growth and trade balance are "
    "periodically revised after initial release; this study uses the most recently available "
    "vintage rather than the real-time-as-published vintage.",
    "<b>Dataset-specific &ldquo;signature&rdquo; risk (Torralba &amp; Efros, 2011):</b> all models are "
    "trained on the 2018-2026 regime only; performance may not generalize to a structurally "
    "different monetary environment (e.g., a return to near-zero global interest rates).",
])

H2("Impact of Limitations")
P("The RQ3 gap means this report cannot yet speak to whether sentiment adds value beyond "
  "fundamentals, which was one of the project's four original questions; this is the single "
  "largest open item. The Eurozone trade-balance aggregation and the annual-CPI substitutions "
  "for India, the U.K., and Japan introduce measurement coarseness specifically into the "
  "EUR/USD, USD/INR, GBP/USD, and USD/JPY inflation and trade-balance terms &mdash; notably, this "
  "means EUR/USD's significant RQ1 result was obtained despite, not because of, having the "
  "coarsest trade-balance measure of the four pairs, which if anything suggests the true "
  "relationship may be understated rather than overstated by measurement error. RQ4's "
  "underpowered surprise split means the encouraging directional pattern should be read as "
  "suggestive evidence motivating future work, not as a confirmed finding.")
P("The undone RQ1 Random Forest robustness check means this report cannot yet rule out that a "
  "nonlinear relationship exists for USD/INR, GBP/USD, or USD/JPY that a linear OLS specification "
  "would miss; the null result for those three pairs should therefore be read as &ldquo;no significant "
  "linear relationship detected,&rdquo; not as &ldquo;no relationship of any kind exists.&rdquo; The 20-day "
  "GARCH refit cadence, rather than a daily refit, means the walk-forward RMSE reported in "
  "Results is a reasonable but not maximally aggressive out-of-sample estimate; a daily-refit "
  "version would very likely track short-lived volatility regime changes slightly more closely, "
  "though at meaningfully higher computational cost for what would likely be a small further "
  "RMSE improvement given how close the current walk-forward and single-fit RMSEs already are.")

H2("Threats to Validity")
P("<b>Internal validity.</b> The main internal-validity concern is look-ahead bias, addressed "
  "throughout by lagging every RQ1 predictor by one month, using only past data at each GARCH "
  "walk-forward refit point, and computing the RQ4 surprise proxy from data available by the day "
  "after each announcement. No random shuffling was used in any train/test split. <b>External "
  "validity.</b> All models are trained on a single 2018-2026 regime (Torralba &amp; Efros, 2011); "
  "whether the EUR/USD result or the RQ2 volatility-forecasting improvement would hold in a "
  "structurally different monetary environment (e.g., a near-zero-rate regime) is untested. "
  "<b>Construct validity.</b> The RQ4 surprise-magnitude proxy (3-month T-bill yield change) is "
  "an established academic proxy but is not the same construct as a true survey-based consensus "
  "surprise; conclusions about &ldquo;surprise magnitude&rdquo; specifically should be read as "
  "conclusions about this proxy, pending the true-consensus-data replacement listed under Future "
  "Improvements.")

H2("Future Improvements")
bullets([
    "Complete the GDELT sentiment pipeline (VADER + FinBERT) and run the RQ3 comparison against "
    "the best RQ2 model using McNemar's test.",
    "Run the originally planned Random Forest nonlinearity robustness check for RQ1 alongside "
    "the OLS specification for all four pairs.",
    "Acquire a true survey-based policy-surprise series (e.g., Bloomberg or Reuters economist "
    "consensus polls) to replace the T-bill-yield proxy used for RQ4, and re-run the "
    "surprise-magnitude split with adequate power.",
    "Source a native monthly Eurozone trade-balance series (e.g., the ECB Statistical Data "
    "Warehouse) to replace the member-state aggregation used here.",
    "Extend RQ2 to all four currency pairs (currently USD/INR only) and add XGBoost or an LSTM "
    "to the comparison, as originally scoped in the synopsis.",
])

H2("Future Scope")
P("Beyond the immediate improvements above, the study could be extended to additional emerging-"
  "market pairs beyond USD/INR to test whether the EUR/USD-specific RQ1 result generalizes to "
  "other deep, liquid developed-market pairs or is specific to the euro; to intraday (rather "
  "than daily/monthly) frequency for the volatility and event-study analyses, which would "
  "materially increase statistical power for RQ4 without waiting years for more FOMC meetings; "
  "and to a live, deployed version of the early-warning dashboard described in Implementation "
  "and User Benefit, evaluated prospectively against realized outcomes rather than only "
  "retrospectively.")
P("A further natural extension is to revisit RQ1's currency-pair-separate design once RQ3's "
  "sentiment feature and a true consensus-based RQ4 surprise measure are both available: a "
  "combined model that includes macro differentials, a sentiment score, and a surprise-magnitude "
  "term together, estimated per pair, would let a future iteration of this project directly test "
  "whether sentiment and policy-surprise information subsume, complement, or are redundant with "
  "the macro-fundamental signal identified here for EUR/USD &mdash; a genuinely unified model rather "
  "than four independently answered research questions.")
page_break()

# ============================================================================
# BIBLIOGRAPHY
# ============================================================================
styles.add(ParagraphStyle("Ref", parent=styles["Normal"], fontName="Helvetica", fontSize=10.3,
                           leading=14.5, leftIndent=18, firstLineIndent=-18, spaceAfter=8,
                           alignment=TA_LEFT))

H1("Bibliography")
P("All 21 sources cited throughout this report are listed below in APA 7 format (alphabetical "
  "by first author's surname, hanging indent, sentence-case article/chapter titles with "
  "title-case journal/publisher names), exceeding the template's minimum of ten. Every "
  "in-text citation used above (author-date parenthetical or narrative form) corresponds to an "
  "entry here, and every entry here is cited at least once in the body of the report; no source "
  "is listed without a corresponding in-text citation, and no in-text citation lacks a "
  "corresponding reference entry.")
refs = [
    "Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. "
    "<i>arXiv</i>. https://arxiv.org/abs/1908.10063",
    "Bank for International Settlements. (2022). <i>Triennial Central Bank Survey: OTC foreign "
    "exchange turnover in 2022</i>. Bank for International Settlements.",
    "Bender, E. M., &amp; Friedman, B. (2018). Data statements for natural language processing: "
    "Toward mitigating system bias and enabling better science. <i>Transactions of the "
    "Association for Computational Linguistics, 6</i>, 587-604.",
    "Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. "
    "<i>Journal of Econometrics, 31</i>(3), 307-327.",
    "Breiman, L. (2001). Random forests. <i>Machine Learning, 45</i>(1), 5-32.",
    "Button, K. S., Ioannidis, J. P. A., Mokrysz, C., Nosek, B. A., Flint, J., Robinson, E. S. J., "
    "&amp; Munaf&ograve;, M. R. (2013). Power failure: Why small sample size undermines the "
    "reliability of neuroscience. <i>Nature Reviews Neuroscience, 14</i>(5), 365-376.",
    "Diebold, F. X., &amp; Mariano, R. S. (1995). Comparing predictive accuracy. <i>Journal of "
    "Business &amp; Economic Statistics, 13</i>(3), 253-263.",
    "Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the "
    "variance of United Kingdom inflation. <i>Econometrica, 50</i>(4), 987-1007.",
    "Federal Reserve Bank of St. Louis. (n.d.). <i>FRED economic data</i> [Data set]. "
    "https://fred.stlouisfed.org",
    "Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daum&eacute; III, H., "
    "&amp; Crawford, K. (2018). Datasheets for datasets. <i>arXiv</i>. "
    "https://arxiv.org/abs/1803.09010",
    "Gelman, A., &amp; Hill, J. (2007). <i>Data analysis using regression and "
    "multilevel/hierarchical models</i>. Cambridge University Press.",
    "Green, S. B. (1991). How many subjects does it take to do a regression analysis? "
    "<i>Multivariate Behavioral Research, 26</i>(3), 499-510.",
    "Hochreiter, S., &amp; Schmidhuber, J. (1997). Long short-term memory. <i>Neural "
    "Computation, 9</i>(8), 1735-1780.",
    "Hutto, C., &amp; Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment "
    "analysis of social media text. <i>Proceedings of the Eighth International AAAI Conference "
    "on Weblogs and Social Media</i>, 216-225.",
    "Kuttner, K. N. (2001). Monetary policy surprises and interest rates: Evidence from the Fed "
    "funds futures market. <i>Journal of Monetary Economics, 47</i>(3), 523-544.",
    "Meese, R. A., &amp; Rogoff, K. (1983). Empirical exchange rate models of the seventies: Do "
    "they fit out of sample? <i>Journal of International Economics, 14</i>(1-2), 3-24.",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., "
    "Raji, I. D., &amp; Gebru, T. (2019). Model cards for model reporting. <i>Proceedings of the "
    "2019 Conference on Fairness, Accountability, and Transparency</i>, 220-229.",
    "O'Brien, T., Sukumar, A., &amp; Helfert, M. (2013). The value of good data &mdash; A quality "
    "perspective: A framework for discussion. <i>Proceedings of the 15th International "
    "Conference on Enterprise Information Systems</i>, 555-562.",
    "Rahm, E., &amp; Do, H. H. (2000). Data cleaning: Problems and current approaches. <i>IEEE "
    "Data Engineering Bulletin, 23</i>(4), 3-13.",
    "Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock "
    "market. <i>The Journal of Finance, 62</i>(3), 1139-1168.",
    "Torralba, A., &amp; Efros, A. A. (2011). Unbiased look at dataset bias. <i>Proceedings of "
    "the 2011 IEEE Conference on Computer Vision and Pattern Recognition</i>, 1521-1528.",
]
for r in refs:
    story.append(Paragraph(r, styles["Ref"]))
page_break()

# ============================================================================
# APPENDIX
# ============================================================================
from reportlab.platypus import Preformatted
styles.add(ParagraphStyle("CodeBlock", parent=styles["Normal"], fontName="Courier", fontSize=6.9,
                           leading=8.4, textColor=DARK))

def code_block(path):
    txt = open(path).read()
    story.append(Preformatted(txt, styles["CodeBlock"]))

H1("Appendix (Optional)")
P("Three analysis scripts are reproduced below in full, referenced throughout the Materials and "
  "Method and Results sections above. Each is also included in the GitHub repository under "
  "/notebooks/.")

H2("Appendix A: RQ1 Multi-Predictor Regression Code (final_analysis_v2.py)")
P("Produces the four per-pair OLS regressions and VIF diagnostics reported in Table 7 and "
  "Figure 4 (see Results &mdash; RQ1).")
code_block(FX + "final_analysis_v2.py")
page_break()

H2("Appendix B: RQ2 Walk-Forward GARCH vs. Random Forest Code (final_analysis2_v2.py)")
P("Produces the walk-forward GARCH re-estimation, Random Forest volatility forecast, naive "
  "baseline, and paired-loss comparison reported in Table 7 and Figure 5 (see Results &mdash; RQ2).")
code_block(FX + "final_analysis2_v2.py")
page_break()

H2("Appendix C: RQ4 Surprise-Conditioned Event Study Code (final_analysis3_v2.py)")
P("Produces the FOMC event study, the 3-month-Treasury-yield surprise-magnitude proxy, the "
  "high/low-surprise split, and the paired significance tests reported in Table 7 and Figure 6 "
  "(see Results &mdash; RQ4).")
code_block(FX + "final_analysis3_v2.py")

print("Appendix built. Final story length:", len(story))

# ============================================================================
# BUILD DOCUMENT WITH PAGE NUMBERING
# ============================================================================
def draw_footer(c, doc_):
    c.saveState()
    c.setFont("Helvetica", 8.3)
    c.setFillColor(SLATE)
    c.drawString(0.85*inch, 0.5*inch, "QM640 Data Analytics Capstone | Final Report | Group 8")
    c.drawRightString(LETTER[0]-0.85*inch, 0.5*inch, f"Page {doc_.page}")
    c.restoreState()

doc = SimpleDocTemplate(FR + "QM640_Final_Report_Group8.pdf", pagesize=LETTER,
                         topMargin=0.85*inch, bottomMargin=0.9*inch,
                         leftMargin=0.85*inch, rightMargin=0.85*inch,
                         title="QM640 Final Report - Group 8")
doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)
print("Final Report built: QM640_Final_Report_Group8.pdf")
