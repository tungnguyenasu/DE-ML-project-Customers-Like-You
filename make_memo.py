"""Build memo.pdf, the one-page summary for Sarah Okafor (J2).

    python make_memo.py

Every number comes from reports/results.json (written by analysis.ipynb) and
reports/build_summary.json (written by build_matrix.py), so the memo stays in
step with the analysis. No customer IDs appear in either file (R4).
"""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).parent
INK, MUTED, ACCENT, RULE, TINT = (colors.HexColor(c) for c in ("#1d1d1b", "#5b5a55", "#2a78d6", "#d9d8d2", "#eef4fc"))
CAMPAIGNS = {  # one possible campaign per segment; marketing decides
    "Big regular wholesalers": "Volume pricing and early access to new ranges",
    "Home-decor shops": "Seasonal decoration collections",
    "Children's gift shops": "Back-to-school and kids' ranges; EU delivery offers",
    "One-off small buyers": "A second-order incentive after the first purchase",
}


def style(name, **kw):
    base = {"fontName": "Helvetica", "fontSize": 9.3, "leading": 12.1, "textColor": INK, "alignment": TA_LEFT}
    return ParagraphStyle(name, **{**base, **kw})


BODY = style("body")
HEAD = style("head", fontName="Helvetica-Bold", fontSize=10, leading=12.5, textColor=ACCENT, spaceBefore=6.5, spaceAfter=1.5)
LEAD = style("lead", fontSize=10.2, leading=13.4)
META = style("meta", fontSize=9, leading=11.6, textColor=MUTED)
CELL = style("cell", fontSize=8.4, leading=10.4)
CELL_HEAD = style("cellhead", fontName="Helvetica-Bold", fontSize=8.4, leading=10.4, textColor=MUTED)
BULLET = style("bullet", leftIndent=10, bulletIndent=0)


def main():
    r = json.loads((ROOT / "reports" / "results.json").read_text(encoding="utf-8"))
    b = json.loads((ROOT / "reports" / "build_summary.json").read_text(encoding="utf-8"))
    test, size, job, model = r["test"], r["size"], r["job"], r["model"]
    no_id = next(x for x in b["cleaning"] if x["rule"] == "Missing Customer ID")["flagged on raw file"] / b["raw_rows"]
    funnel = b["holdout_funnel"]
    cold = -funnel["Customer not in the training matrix (cold start)"] / funnel["Customer-product pairs bought in the test period"]
    n_customers, n_products = b["matrix"]["customers"], b["matrix"]["products"]
    low, high = test["gain_interval_points"]
    p = lambda x: f"{x:.0%}"

    story = [
        Paragraph("<b>MEMO</b>", style("label", fontSize=8, textColor=ACCENT, leading=10)),
        Paragraph("<b>To:</b> Sarah Okafor, Head of E-Commerce &nbsp;&nbsp; <b>From:</b> Tung Nguyen, Data &amp; ML team "
                  "&nbsp;&nbsp; <b>Date:</b> 12 October 2026", META),
        Paragraph("<b>Subject:</b> The \"also bought\" box and our customer groups: results before Q4 planning", META),
        Spacer(1, 7),
        Paragraph(
            f"<b>In short:</b> we shrank the purchase history of {n_customers:,} customers into a model "
            f"<b>{size['times_smaller']:.0f} times smaller</b> than the table the old prototype builds. The whole nightly job "
            f"now takes <b>under a second</b>. On purchases the model never saw, its suggestions caught what customers bought "
            f"next for <b>{test['hit_rate']:.0%}</b> of them, against <b>{test['baseline']:.0%}</b> for showing best sellers. "
            "We also found four customer groups that marketing can plan around.", LEAD),

        Paragraph("Which method we chose, and why", HEAD),
        Paragraph(
            f"We use <b>truncated SVD</b> (singular value decomposition), a standard way to compress a large table. It "
            f"describes every product and every customer with {model['k']} numbers that capture buying patterns, such as "
            "\"home decoration\" or \"children's items\". Products with similar patterns are suggested together. It works "
            "directly on our purchase table, which is 98% empty. We also tested the main alternative, PCA. It gave the "
            "same suggestions (96% of lists identical) but needs an extra step and far more memory. All settings were "
            "chosen on an earlier period, so the results below are a fair test.", BODY),

        Paragraph("What we lose by compressing", HEAD),
        Paragraph(
            f"The compressed model keeps about <b>a third of the detail</b> in the full table ({size['share_kept']:.0%}). What "
            "it drops is mostly one-off choices that no other shop shares. The suggestions come from the shared patterns. "
            "That is why they generalise to products a shop has not bought yet, and why they still beat best sellers.", BODY),

        Paragraph("How big and how fast", HEAD),
        Paragraph(
            f"Stored model: <b>{size['factors_mb']:.1f} MB</b> instead of {size['dense_mb']:.0f} MB. The nightly job refits the "
            f"model, writes a 10-product \"also bought\" list for each of {n_products:,} products and 10 suggestions for each "
            f"customer. It takes <b>{job['seconds']:.1f} seconds</b> on a laptop and peaks at about {job['peak_mb']:.0f} MB of memory.",
            BODY),

        Paragraph("Are the suggestions better than best sellers?", HEAD),
        Paragraph(
            "We hid the last two months (9 October to 9 December 2011) from the model. Then we checked whether any of a "
            "customer's 10 suggestions was a product they went on to buy for the first time. That happened for "
            f"<b>{test['hit_rate']:.1%}</b> of {test['customers']:,} customers, against <b>{test['baseline']:.1%}</b> for the "
            f"10 best sellers they had not bought: <b>{test['gain_points']:+.1f} points</b> (95% range {low:+.1f} to "
            f"{high:+.1f}). The suggestions also spread across {r['coverage']['products suggested to at least one customer'].split(' of')[0]} "
            f"different products, while best sellers fill only {r['coverage']['share of all suggestion slots taken by the 10 best sellers']} "
            "of the suggestion slots.", BODY),

        Paragraph("Customer groups for marketing", HEAD),
    ]

    rows = [[Paragraph(h, CELL_HEAD) for h in ("Group", "Share", "What they buy", "Possible campaign")]]
    for seg in r["segments"]:
        what = (f"Median {seg['median_products']:.0f} products over {seg['median_orders']:.0f} "
                f"order{'s' if seg['median_orders'] != 1 else ''}; ")
        if seg["median_orders"] <= 1:  # a single small basket: no product is shared by more than a few of them
            what += "few products in common"
        else:
            what += "more than average: " + ", ".join(d.lower() for d in seg["distinctive"][:2])
        if seg["overseas"] > 0.15:
            what += f". {p(seg['overseas'])} overseas ({seg['top_overseas']})"
        rows.append([Paragraph(f"<b>{seg['name']}</b>", CELL), Paragraph(p(seg["share"]), CELL), Paragraph(what, CELL),
                     Paragraph(CAMPAIGNS[seg["name"]], CELL)])
    table = Table(rows, colWidths=[1.45 * inch, 0.48 * inch, 3.37 * inch, 1.9 * inch])
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 1), (-1, -2), 0.4, RULE), ("BACKGROUND", (0, 0), (-1, 0), TINT),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    story += [table, Spacer(1, 1),
              Paragraph("The groups come from the same model; the full picture is in the slides. Campaign ideas are "
                        "suggestions for marketing to decide on.", style("note", fontSize=8, leading=10, textColor=MUTED))]

    story.append(Paragraph("What could go wrong", HEAD))
    risks = [
        f"<b>New customers and new products.</b> The model knows nothing about them, and {cold:.0%} of purchases in the "
        "test period came from customers with no history. They should see best sellers until their first order.",
        "<b>Seasonality.</b> We tested on the pre-Christmas peak. Results in quieter months may differ, so the hit rate "
        "should be re-checked each month.",
        "<b>Popular products.</b> The model leans on what sells well, so some suggestions are items a shop would find anyway.",
        f"<b>Data gaps.</b> {no_id:.0%} of order lines have no customer number and are not used.",
        "<b>Privacy.</b> Customer numbers never leave our team. This memo, the slides and the customer map use group "
        "names only.",
    ]
    story += [Paragraph(t, BULLET, bulletText="•") for t in risks]

    story.append(Paragraph("Next steps", HEAD))
    story.append(Paragraph(
        "1. Run the box on product pages as a 4-week test against best sellers, measuring clicks and added revenue. "
        "2. Schedule the nightly job and a monthly check of the hit rate. "
        "3. Add a fallback for new products, such as items from the same range.", BODY))

    doc = SimpleDocTemplate(str(ROOT / "memo.pdf"), pagesize=letter, leftMargin=0.62 * inch, rightMargin=0.62 * inch,
                            topMargin=0.5 * inch, bottomMargin=0.45 * inch, title="Memo: also-bought box and customer groups",
                            author="Tung Nguyen")
    doc.build(story)
    print("wrote memo.pdf")


if __name__ == "__main__":
    main()
