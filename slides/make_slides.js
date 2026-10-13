// Builds ../slides.pptx, the 5-minute presentation (J3), from the numbers in ../reports.
//
//     cd slides && npm install && npm run build
//
// No customer IDs: every number comes from reports/*.json and *.csv (R4).
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const ROOT = path.join(__dirname, "..");
const read = (f) => JSON.parse(fs.readFileSync(path.join(ROOT, "reports", f), "utf8"));
const r = read("results.json");
const b = read("build_summary.json");
const sweep = fs.readFileSync(path.join(ROOT, "reports", "validation_sweep.csv"), "utf8").trim().split(/\r?\n/).slice(1)
  .map((line) => { const [value, k, rule, hit] = line.split(","); return { value, k: +k, rule, hit: +hit }; });

// Palette: navy ground, retrospot red for the dot motif, validated chart slots for data
const NAVY = "1F2A44", INK = "1D1D1B", MUTED = "5B5A55", SOFT = "C9D3E6", RED = "C8102E", TINT = "F3F5F9";
const BLUE = "2A78D6", ORANGE = "EB6834", AQUA = "1BAF7A", GREY = "898781", LIGHTGREY = "C3C2B7", GOOD = "006300";
const HEAD = "Cambria", BODY = "Calibri";
const W = 13.333, M = 0.6;

const pct = (x, d = 1) => `${(x * 100).toFixed(d)}%`;
const num = (x) => Math.round(x).toLocaleString("en-US");
const segs = r.segments;
const cleaning = Object.fromEntries(b.cleaning.map((c) => [c.rule, c]));
const funnel = b.holdout_funnel;
const coldShare = -funnel["Customer not in the training matrix (cold start)"] / funnel["Customer-product pairs bought in the test period"];
const noId = cleaning["Missing Customer ID"]["flagged on raw file"] / b.raw_rows;
const CAMPAIGNS = {
  "Big regular wholesalers": "Volume pricing, early access to new ranges",
  "Home-decor shops": "Seasonal decoration collections",
  "Children's gift shops": "Back-to-school and kids' ranges; EU delivery offers",
  "One-off small buyers": "A second-order incentive",
};
const WHAT = {
  "Big regular wholesalers": "Buy across the range: baking, bags, storage",
  "Home-decor shops": "Hanging hearts, antique-white wood, frames",
  "Children's gift shops": "Lunch boxes, plasters in tins, paint sets",
  "One-off small buyers": "One small order, few products in common",
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Customers Like You";
pres.author = "Tung Nguyen";

function dots(slide, x0, y0, cols, rows, size, gap) {
  // Retrospot polka dots, fading towards the slide centre
  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      if ((i + j) % 2) continue;
      slide.addShape(pres.shapes.OVAL, {
        x: x0 + i * gap, y: y0 + j * gap, w: size, h: size,
        fill: { color: RED, transparency: Math.min(85, 10 + (cols - 1 - i) * 14) }, line: { type: "none" },
      });
    }
  }
}

function header(slide, eyebrow, title) {
  slide.background = { color: "FFFFFF" };
  slide.addShape(pres.shapes.OVAL, { x: M, y: 0.52, w: 0.13, h: 0.13, fill: { color: RED }, line: { type: "none" } });
  slide.addText(eyebrow.toUpperCase(), { x: M + 0.22, y: 0.42, w: 9, h: 0.32, fontFace: BODY, fontSize: 11, bold: true,
    color: MUTED, charSpacing: 2, margin: 0, isTextBox: true });
  slide.addText(title, { x: M, y: 0.78, w: W - 2 * M, h: 0.85, fontFace: HEAD, fontSize: 32, bold: true, color: INK,
    margin: 0, valign: "top", isTextBox: true });
}

function points(slide, items, x, y, w, h, size = 14) {
  // Bold lead + plain explanation, one paragraph per item
  const runs = [];
  items.forEach(([lead, text], i) => {
    runs.push({ text: lead, options: { bold: true, color: INK, breakLine: true } });
    runs.push({ text, options: { color: MUTED, breakLine: i < items.length - 1, paraSpaceAfter: 12 } });
  });
  slide.addText(runs, { x, y, w, h, fontFace: BODY, fontSize: size, valign: "top", margin: 0, isTextBox: true });
}

// 1. Title -------------------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  dots(s, 9.0, 1.0, 7, 9, 0.34, 0.6);
  s.addText("DS 5020 MINI-PROJECT", { x: 0.8, y: 1.55, w: 7.5, h: 0.4, fontFace: BODY, fontSize: 13, bold: true,
    color: SOFT, charSpacing: 3, margin: 0, isTextBox: true });
  s.addText("Customers Like You", { x: 0.8, y: 2.0, w: 8, h: 1.15, fontFace: HEAD, fontSize: 54, bold: true,
    color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText("A smaller, faster “also bought” box and four customer groups for GiftLane",
    { x: 0.8, y: 3.25, w: 7.6, h: 1.1, fontFace: BODY, fontSize: 22, color: SOFT, margin: 0, valign: "top", isTextBox: true });
  s.addText([{ text: "Tung Nguyen", options: { bold: true, color: "FFFFFF", breakLine: true } },
             { text: "Data Engineer and ML Engineer  ·  12 October 2026", options: { color: SOFT } }],
    { x: 0.8, y: 5.75, w: 7.6, h: 0.8, fontFace: BODY, fontSize: 15, margin: 0, isTextBox: true });
  s.addNotes("I'm Tung, and I did both roles on this project: the data engineering and the modelling. Sarah asked for "
    + "two things before Q4 planning: a faster 'customers who bought this also bought' box that beats best sellers, "
    + "and one simple picture of our customer groups for marketing. I'll show what we built, what it costs, and how "
    + "we know it works.");
}

// 2. Results at a glance -----------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "Sarah's request, measured", "All four success targets are met");
  const cards = [
    [`${Math.round(r.size.times_smaller)}×`, "smaller stored model",
     `${r.size.factors_mb.toFixed(1)} MB of factors instead of the ${r.size.dense_mb.toFixed(1)} MB customer × product table`,
     "Target: at least 10× smaller"],
    [`${r.job.seconds.toFixed(1)} s`, "whole nightly job",
     `Refit, an “also bought” list for ${num(b.matrix.products)} products, 10 suggestions for ${num(b.matrix.customers)} customers`,
     "Target: under 1 minute"],
    [`+${r.test.gain_points.toFixed(1)}`, "points over baseline",
     `${pct(r.test.hit_rate)} hit rate at 10 against ${pct(r.test.baseline)} for best sellers, on purchases the model never saw`,
     "Target: at least +3 points"],
    [`${segs.length}`, "customer groups",
     `The smallest holds ${pct(Math.min(...segs.map((x) => x.share)), 0)} of customers; each is named from what it buys`,
     "Target: 3 to 6 nameable groups"],
  ];
  const cw = (W - 2 * M - 3 * 0.3) / 4;
  cards.forEach(([big, label, detail, target], i) => {
    const x = M + i * (cw + 0.3), y = 2.0;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: cw, h: 4.2, fill: { color: TINT }, line: { type: "none" } });
    s.addText(big, { x: x + 0.3, y: y + 0.3, w: cw - 0.6, h: 0.95, fontFace: HEAD, fontSize: 44, bold: true, color: INK,
      margin: 0, isTextBox: true });
    s.addText(label, { x: x + 0.3, y: y + 1.25, w: cw - 0.6, h: 0.45, fontFace: BODY, fontSize: 16, bold: true,
      color: INK, margin: 0, isTextBox: true });
    s.addText(detail, { x: x + 0.3, y: y + 1.8, w: cw - 0.6, h: 1.35, fontFace: BODY, fontSize: 13, color: MUTED,
      margin: 0, valign: "top", isTextBox: true });
    s.addText([{ text: target, options: { color: MUTED, breakLine: true } },
               { text: "✓ Met", options: { color: GOOD, bold: true } }],
      { x: x + 0.3, y: y + 3.25, w: cw - 0.6, h: 0.75, fontFace: BODY, fontSize: 12, margin: 0, valign: "bottom", isTextBox: true });
  });
  s.addText("Targets 1 to 3 answer the product-page request; target 4 answers marketing.",
    { x: M, y: 6.5, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 13, color: MUTED, margin: 0, isTextBox: true });
  s.addNotes("Before the detail, the answer. We set four measurable targets on day one, and all four are met. The "
    + "stored model is 31 times smaller than the table the old job builds. The whole nightly job runs in under a "
    + "second. On purchases the model never saw, it beats best sellers by 13.5 points. And we found four customer "
    + "groups marketing can name.");
}

// 3. Data engineering --------------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "Data engineering", `From ${(b.raw_rows / 1e6).toFixed(2)} million order lines to one sparse matrix`);
  const labels = ["Same week in both sheets", "Cancellations (netted)", "Quantity ≤ 0", "Price ≤ 0",
                  "Not a product (postage, fees)", "No customer ID", "Exact duplicates"];
  const values = b.cleaning.map((c) => c["rows removed"]);
  s.addText("Lines removed by each cleaning rule, in order", { x: M, y: 1.85, w: 6.8, h: 0.35, fontFace: BODY,
    fontSize: 13, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addChart(pres.charts.BAR, [{ name: "Lines removed", labels, values }], {
    x: M - 0.1, y: 2.2, w: 6.9, h: 4.4, barDir: "bar", chartColors: [BLUE], barGapWidthPct: 60,
    catAxisOrientation: "maxMin", catAxisLabelColor: INK, catAxisLabelFontFace: BODY, catAxisLabelFontSize: 12,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", dataLabelColor: INK,
    dataLabelFontFace: BODY, dataLabelFontSize: 11, showLegend: false,
  });
  s.addText(`${num(b.clean_purchase_lines)} clean purchase lines remain (${pct(b.clean_purchase_lines / b.raw_rows, 0)} of raw).`,
    { x: M, y: 6.6, w: 6.8, h: 0.35, fontFace: BODY, fontSize: 12, color: MUTED, margin: 0, isTextBox: true });
  points(s, [
    ["The two yearly sheets overlap", `1–9 Dec 2010 is in both, line for line: ${num(cleaning["Line repeated in the next year's sheet (1-9 Dec 2010)"]["rows removed"])} lines kept once.`],
    ["Cancellations undo purchases", "Cancelled units are subtracted from the order they cancel, so a 74,215-unit order cancelled the same day no longer counts."],
    ["A leak-free split", `Test = the last 2 months, only products new to each customer: ${num(b.holdout_funnel["Held-out pairs"])} purchases by ${num(b.holdout_customers)} customers.`],
    ["The matrix", `${num(b.matrix.customers)} customers × ${num(b.matrix.products)} products, ${pct(b.matrix.sparsity, 0)} zeros, ${b.matrix.sparse_csr_mb.toFixed(1)} MB sparse. One command rebuilds it: python build_matrix.py`],
  ], 7.9, 1.9, W - 7.9 - M, 5.1, 14);
  s.addNotes("The raw file has 1.07 million lines. Two things are easy to get wrong here. First, the two yearly "
    + "sheets overlap by a week, so a plain concat double-counts it. Second, deleting cancellation lines still "
    + "leaves the original order counted as a purchase, so I subtract cancelled units instead. Most removed lines "
    + "have no customer ID. The test set is the last two months, and only products the customer never bought "
    + "before, so we measure discovery, not repeat orders.");
}

// 4. PCA or SVD ----------------------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "Method choice (decided before fitting)", "PCA or SVD? On our data they agree");
  const c = r.comparison;
  const cell = (text, opts = {}) => ({ text, options: { fontFace: BODY, fontSize: 13, color: INK, ...opts } });
  const head = (text) => cell(text, { bold: true, color: MUTED, fill: { color: TINT } });
  const rows = [
    [head("Same matrix, k = " + r.model.k), head("PCA"), head("Truncated SVD")],
    [cell("Fit time"), cell(`${c.pca.fit_seconds.toFixed(2)} s`), cell(`${c.svd.fit_seconds.toFixed(2)} s`)],
    [cell("Peak memory during fit"), cell(`${c.pca.peak_mb.toFixed(1)} MB (${Math.round(c.dense_centring_peak_mb)} MB if centred by hand)`),
     cell(`${c.svd.peak_mb.toFixed(1)} MB`)],
    [cell("Stored factors"), cell(`${c.pca.factors_mb.toFixed(2)} MB`), cell(`${c.svd.factors_mb.toFixed(2)} MB`)],
    [cell("Relative reconstruction error"), cell(c.pca.relative_error.toFixed(3)), cell(c.svd.relative_error.toFixed(3))],
    [cell("Hit rate at 10 (test)"), cell(pct(c.pca.hit_rate)), cell(pct(c.svd.hit_rate))],
    [cell("Component 1 means"), cell("Overall buying"), cell("Overall buying")],
  ];
  s.addTable(rows, { x: M, y: 2.0, w: 7.3, colW: [2.6, 2.75, 1.95], rowH: 0.56, border: { type: "solid", pt: 0.75, color: "E1E0D9" },
    valign: "middle", margin: [0, 0.12, 0, 0.12] });
  const bigs = [
    [pct(c.average_share), "of the matrix is the “average customer” PCA removes. 98% of cells are zero, so centring barely changes the model."],
    [pct(c.list_overlap, 0), "of “also bought” lists are identical between the two methods."],
  ];
  bigs.forEach(([big, text], i) => {
    const y = 2.0 + i * 1.55;
    s.addText(big, { x: 8.4, y, w: 1.9, h: 0.8, fontFace: HEAD, fontSize: 36, bold: true, color: INK, margin: 0, isTextBox: true });
    s.addText(text, { x: 10.3, y: y + 0.05, w: W - 10.3 - M, h: 1.2, fontFace: BODY, fontSize: 13, color: MUTED,
      margin: 0, valign: "top", isTextBox: true });
  });
  const lead = (c.pca.hit_rate - c.svd.hit_rate) * 100;
  s.addShape(pres.shapes.RECTANGLE, { x: 8.4, y: 5.25, w: W - 8.4 - M, h: 1.35, fill: { color: TINT }, line: { type: "none" } });
  s.addText([{ text: "Decision: Truncated SVD", options: { bold: true, color: INK, breakLine: true } },
             { text: `PCA is ahead by only ${lead.toFixed(1)} points, under the 1-point bar set before fitting. SVD works on the sparse table as it is.`,
               options: { color: MUTED } }],
    { x: 8.6, y: 5.35, w: W - 8.6 - M - 0.2, h: 1.15, fontFace: BODY, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  s.addNotes("I chose truncated SVD before fitting anything, because it works on the sparse table directly and gives "
    + "product and customer factors in one fit. Then I ran PCA on the same matrix and k. They agree almost exactly: "
    + "the average customer that PCA subtracts is under 5% of the matrix, because 98% of cells are zero. One of my "
    + "predictions was wrong: I expected PCA's first component to be a contrast between kinds of shops, but in both "
    + "methods it is simply how much a customer buys. Centring only hurts if you do it by hand: 493 megabytes.");
}

// 5. Choosing k on validation ----------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "Choosing the settings", "Chosen on a validation period, never on the test set");
  const ks = [...new Set(sweep.map((x) => x.k))].sort((a, b) => a - b);
  const line = (value) => ks.map((k) => sweep.find((x) => x.value === value && x.k === k && x.rule === "rebuilt row").hit);
  const v = r.validation;
  s.addText("Validation hit rate at 10, by k and purchase value", { x: M, y: 1.85, w: 7.8, h: 0.35, fontFace: BODY,
    fontSize: 13, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addChart(pres.charts.LINE, [
    { name: "1/0 bought (chosen)", labels: ks.map(String), values: line("binary") },
    { name: "log(1 + units)", labels: ks.map(String), values: line("log1p") },
    { name: "Raw units", labels: ks.map(String), values: line("quantity") },
    { name: "Best sellers", labels: ks.map(String), values: ks.map(() => v.validation_baseline) },
  ], {
    x: M - 0.1, y: 2.2, w: 8.0, h: 4.6, chartColors: [BLUE, ORANGE, AQUA, GREY], lineSize: 2, lineDataSymbol: "circle",
    lineDataSymbolSize: 7, valAxisMinVal: 0, valAxisMaxVal: 0.5, valAxisLabelFormatCode: "0%", valAxisMajorUnit: 0.1,
    valAxisLabelColor: MUTED, catAxisLabelColor: MUTED, valAxisLabelFontSize: 11, catAxisLabelFontSize: 11,
    catAxisTitle: "k (components kept)", showCatAxisTitle: true, catAxisTitleColor: MUTED, catAxisTitleFontSize: 11,
    valGridLine: { color: "E1E0D9", size: 0.75 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 11, legendColor: INK, legendFontFace: BODY,
  });
  points(s, [
    ["A validation period", `The same 2-month split, inside the training data: 9 Aug to 9 Oct 2011 (${num(b.validation.holdout_customers)} customers).`],
    ["What won", `1/0 “bought it” cells, k = ${v.k}, and rebuilt-row scoring: ${pct(v.validation_hit_rate)} against ${pct(v.validation_baseline)} for best sellers. We take the smallest k within 1 point of the best.`],
    ["The brief's cosine rule lost", "It stayed below best sellers at every k: scaling every product to the same length throws away how much it sells."],
  ], 8.9, 1.9, W - 8.9 - M, 5.0, 14);
  s.addNotes("Three settings had to be chosen: k, what goes in each cell, and how to score products. To keep the test "
    + "honest I repeated the split inside the training data and chose everything there. A plain 'bought it or not' "
    + "flag beat counting units, and 70 components was the smallest k close to the best. The scoring rule in the "
    + "brief, cosine similarity, lost to best sellers at every k, because it normalises away popularity. Using dot "
    + "products, which is the same as rebuilding the customer's row, keeps it.");
}

// 6. Test results ------------------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "Evaluation", "Tested once, on purchases the model never saw");
  const t = r.test;
  s.addText(`Hit rate at 10: share of ${num(t.customers)} test customers who bought one of their 10 suggestions`,
    { x: M, y: 1.85, w: 6.6, h: 0.35, fontFace: BODY, fontSize: 13, bold: true, color: INK, margin: 0, isTextBox: true });
  s.addChart(pres.charts.BAR, [
    { name: "Our model", labels: ["9 Oct to 9 Dec 2011"], values: [t.hit_rate] },
    { name: "Best sellers", labels: ["9 Oct to 9 Dec 2011"], values: [t.baseline] },
    { name: "Brief's cosine rule", labels: ["9 Oct to 9 Dec 2011"], values: [t.cosine_rule_hit_rate] },
  ], {
    x: M - 0.1, y: 2.25, w: 6.6, h: 4.5, barDir: "col", chartColors: [BLUE, GREY, LIGHTGREY], barGapWidthPct: 40,
    valAxisMinVal: 0, valAxisMaxVal: 0.5, valAxisLabelFormatCode: "0%", valAxisMajorUnit: 0.1, valAxisLabelColor: MUTED,
    catAxisLabelColor: MUTED, valGridLine: { color: "E1E0D9", size: 0.75 }, catGridLine: { style: "none" },
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0%", dataLabelColor: INK, dataLabelFontSize: 13,
    showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: INK, legendFontFace: BODY,
  });
  const [low, high] = t.gain_interval_points;
  s.addText(`+${t.gain_points.toFixed(1)} points`, { x: 7.7, y: 1.9, w: 5, h: 0.9, fontFace: HEAD, fontSize: 40, bold: true,
    color: INK, margin: 0, isTextBox: true });
  s.addText(`over best sellers (95% interval +${low.toFixed(1)} to +${high.toFixed(1)}). The suggestions use ${r.coverage["products suggested to at least one customer"].split(" of")[0]} different products.`,
    { x: 7.7, y: 2.8, w: W - 7.7 - M, h: 0.9, fontFace: BODY, fontSize: 14, color: MUTED, margin: 0, valign: "top", isTextBox: true });
  const ex = r.also_bought_example;
  s.addShape(pres.shapes.RECTANGLE, { x: 7.7, y: 3.95, w: W - 7.7 - M, h: 2.75, fill: { color: TINT }, line: { type: "none" } });
  s.addText([
    { text: `Customers who bought the ${ex.product} also bought`, options: { bold: true, color: INK, breakLine: true, paraSpaceAfter: 6 } },
    ...ex.list.slice(0, 6).map((p, i) => ({ text: p, options: { color: MUTED, bullet: { type: "number" }, breakLine: i < 5 } })),
  ], { x: 7.95, y: 4.15, w: W - 7.95 - M - 0.2, h: 2.4, fontFace: BODY, fontSize: 13, margin: 0, valign: "top", isTextBox: true });
  s.addNotes("Only after every choice was fixed did I score the test period once. 40 percent of test customers bought "
    + "at least one of their ten suggestions, against 27 percent for the best sellers they hadn't bought. That's "
    + "13.5 points, with a bootstrap interval from about 11 to 16. The brief's cosine rule would have lost. And the "
    + "suggestions look sensible: people who buy the white hanging heart get other hanging hearts and heart decor.");
}

// 7. Customer map ------------------------------------------------------------------------------
{
  const s = pres.addSlide();
  header(s, "For marketing", "Four customer groups to plan campaigns around");
  const png = fs.readFileSync(path.join(ROOT, "figures", "customer_map.png"));
  const aspect = png.readUInt32BE(16) / png.readUInt32BE(20);
  const h = 5.35, w = h * aspect;
  s.addImage({ path: path.join(ROOT, "figures", "customer_map.png"), x: M - 0.1, y: 1.8, w, h,
    altText: "Customer map: four panels, one per group, on axes of overall buying and taste" });
  const x = M + w + 0.3, cw = W - x - M;
  segs.forEach((seg, i) => {
    const y = 1.85 + i * 1.32;
    s.addText([
      { text: `${seg.name}  `, options: { bold: true, color: INK } },
      { text: `${pct(seg.share, 0)}`, options: { color: MUTED, breakLine: true } },
      { text: WHAT[seg.name] + (seg.overseas > 0.15 ? `; ${pct(seg.overseas, 0)} overseas` : ""), options: { color: MUTED, breakLine: true } },
      { text: `Campaign: ${CAMPAIGNS[seg.name]}`, options: { color: INK, italic: true } },
    ], { x, y, w: cw, h: 1.2, fontFace: BODY, fontSize: 13, margin: 0, valign: "top", isTextBox: true });
  });
  s.addNotes("For marketing, the map uses the model's first two components, reshaped so the axes read as how much a "
    + "shop buys and what it buys. Four groups come out: big regular wholesalers, home-decor shops, children's gift "
    + "shops, which have the most overseas buyers, and one-off small buyers. Each holds at least 10 percent of "
    + "customers, and no two share a distinctive product, so each can get its own campaign. No customer IDs appear "
    + "anywhere.");
}

// 8. Risks and next steps ------------------------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  dots(s, 11.0, 0.5, 4, 3, 0.26, 0.48);
  s.addText("What could go wrong, and what comes next", { x: 0.8, y: 0.7, w: 10, h: 0.9, fontFace: HEAD, fontSize: 32,
    bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  const column = (title, items, x) => {
    s.addText(title.toUpperCase(), { x, y: 1.95, w: 5.6, h: 0.35, fontFace: BODY, fontSize: 12, bold: true, color: SOFT,
      charSpacing: 2, margin: 0, isTextBox: true });
    const runs = [];
    items.forEach(([lead, text], i) => {
      runs.push({ text: lead + " ", options: { bold: true, color: "FFFFFF", paraSpaceAfter: 16 } });
      runs.push({ text, options: { color: SOFT, breakLine: i < items.length - 1, paraSpaceAfter: 16 } });
    });
    s.addText(runs, { x, y: 2.4, w: 5.6, h: 4.0, fontFace: BODY, fontSize: 16, margin: 0, valign: "top", isTextBox: true });
  };
  column("Risks", [
    ["New customers and products.", `The model knows nothing about them; ${pct(coldShare, 0)} of test-period purchases came from customers with no history. Show them best sellers.`],
    ["Seasonality.", "Tested on the pre-Christmas peak; quieter months may differ."],
    ["Popularity.", "The model leans on what sells well."],
    ["Data gaps.", `${pct(noId, 0)} of order lines have no customer ID and are not used.`],
  ], 0.8);
  column("Next steps", [
    ["Test it live.", "A 4-week test on product pages against best sellers, measuring clicks and added revenue."],
    ["Run it nightly.", "Schedule python nightly_job.py and re-check the hit rate every month."],
    ["Cover new products.", "Fall back to items from the same range until they have buyers."],
  ], 7.0);
  s.addText("Code, reports and memo: github.com/tungnguyenasu/DE-ML-project-Customers-Like-You",
    { x: 0.8, y: 6.65, w: 11.5, h: 0.35, fontFace: BODY, fontSize: 12, color: SOFT, margin: 0, isTextBox: true });
  s.addNotes("The main risks: new customers and new products get no personal suggestions, so they should see best "
    + "sellers. We tested on the Christmas peak, so the monthly check matters. Next, I'd run a four-week live test on "
    + "product pages against best sellers, and schedule the nightly job. Everything is in the repository. Thank you.");
}

pres.writeFile({ fileName: path.join(ROOT, "slides.pptx") }).then((f) => console.log(`wrote ${f}`));
