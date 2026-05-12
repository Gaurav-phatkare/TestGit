# ─────────────────────────────────────────────────────────────────
# Agent 4 — Plotly Code Generator
# ─────────────────────────────────────────────────────────────────

_PLOTLY_SYSTEM = """
You are an expert Python data visualization engineer using Plotly.
Given a user's question, SQL query result data, and chart metadata, 
write complete executable Python code using plotly.express or plotly.graph_objects
that generates the chart and saves it as an HTML file.

Rules:
1. Return ONLY raw Python code — no markdown, no backticks, no explanation.
2. The data is already available as a Python list of dicts in variable `data`.
3. Convert `data` to a pandas DataFrame at the start: `df = pd.DataFrame(data)`
4. Save the final figure using: `fig.write_html(output_path)`
5. `output_path` variable is already defined — do NOT redefine it.
6. Always set a chart title, axis labels, and a clean theme (use template="plotly_white").
7. Handle edge cases — if a column has many unique values, limit to top 20 by value.
8. For bar charts use px.bar, line use px.line, pie use px.pie, scatter use px.scatter.
9. Always import pandas as pd and plotly.express as px at the top.
10. Do NOT use fig.show() — only fig.write_html(output_path).
"""

_PLOTLY_HUMAN = """
## User Question
{question}

## Chart Metadata
Chart Type   : {chart_type}
Title        : {title}
X Axis       : {x_axis}
Y Axis       : {y_axis}
Series Label : {series_label}

## Column Names
{columns}

## Sample Data (first 10 rows as list of dicts)
{sample_data}

## Instructions
- Variable `data` contains the full dataset as list of dicts.
- Variable `output_path` is already set to the output file path.
- Write complete Python code to generate and save the plotly chart.
"""


@dataclass
class PlotlyResult:
    success:     bool
    code:        str        = ""
    output_html: Optional[str] = None
    error:       Optional[str] = None


class PlotlyCodeAgent:
    def __init__(self):
        self._llm   = ChatGoogleGenerativeAI(
            model=GEMINI_MODEL, google_api_key=GEMINI_API_KEY, temperature=0.1
        )
        self._chain = ChatPromptTemplate.from_messages([
            ("system", _PLOTLY_SYSTEM),
            ("human",  _PLOTLY_HUMAN),
        ]) | self._llm

    def generate(
        self,
        question:    str,
        viz_meta:    VizMeta,
        columns:     list,
        data:        list,        # full data list of dicts
    ) -> PlotlyResult:
        if not data:
            return PlotlyResult(success=False, error="No data to plot.")

        try:
            response = self._chain.invoke({
                "question":    question,
                "chart_type":  viz_meta.chart_type,
                "title":       viz_meta.title,
                "x_axis":      viz_meta.x_axis   or "None",
                "y_axis":      viz_meta.y_axis   or "None",
                "series_label": viz_meta.series_label or "None",
                "columns":     ", ".join(columns),
                "sample_data": str(data[:10]),
            })

            code = response.content.strip()
            # Strip accidental markdown fences if Gemini adds them
            code = re.sub(r"^```python\s*", "", code)
            code = re.sub(r"^```\s*", "", code)
            code = re.sub(r"```$", "", code).strip()

        except Exception as exc:
            return PlotlyResult(success=False, error=f"Code generation failed: {exc}")

        # ── Execute the generated code ────────────────────────────
        timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug        = re.sub(r"\W+", "_", question[:40]).strip("_").lower()
        output_path = str(_ensure_dir(OUTPUT_DIR) / f"chart_{slug}__{timestamp}.html")

        exec_globals = {
            "data":        data,
            "output_path": output_path,
        }

        try:
            exec(code, exec_globals)   # nosec — LLM-generated plotly code only
            return PlotlyResult(
                success     = True,
                code        = code,
                output_html = output_path,
            )
        except Exception as exc:
            return PlotlyResult(
                success = False,
                code    = code,
                error   = f"Code execution failed: {exc}",
            )





class NL2SQLPipeline:
    def __init__(self):
        self.loader     = DataLoader()
        self._selector  = TableSelectorAgent()
        self._validator = SQLValidatorAgent(self.loader)
        self._viz_agent = VizMetaAgent()
        self._gen_chain = _SQLGeneratorChain()
        self._plotly    = PlotlyCodeAgent()    # ← add this


# ── Agent 3 — Viz metadata ──
                viz = self._viz_agent.generate(
                    question    = question,
                    sql         = sql,
                    columns     = cols,
                    sample_data = data,
                )

                # ── Agent 4 — Plotly chart ──
                plotly_result = self._plotly.generate(
                    question = question,
                    viz_meta = viz,
                    columns  = cols,
                    data     = data,        # full data
                )



@dataclass
class QueryResult:
    ...
    plotly_code:      str            = ""
    output_html:      Optional[str]  = None
    plotly_error:     Optional[str]  = None





return QueryResult(
                    ...
                    plotly_code  = plotly_result.code,
                    output_html  = plotly_result.output_html,
                    plotly_error = plotly_result.error,
                )




return _ok({
            "sql":          result.final_sql,
            "rows":         result.rows,
            "columns":      result.columns,
            "data":         result.data,
            "tables_used":  result.tables_used,
            "attempts":     result.attempts,
            "output_csv":   result.output_csv,
            "reasoning":    result.reasoning,
            "column_roles": result.column_roles,
            "visualization": { ... },

            # ── NEW: plotly chart ──
            "chart": {
                "output_html":  result.output_html,    # downloadable HTML file path
                "plotly_code":  result.plotly_code,    # code Gemini wrote
                "error":        result.plotly_error,   # None if successful
            },
        })





@app.route("/chart/<path:filename>", methods=["GET"])
def download_chart(filename):
    """Download the generated Plotly HTML chart."""
    safe = secure_filename(filename)
    if not (OUTPUT_DIR / safe).exists():
        return _err(f"Chart '{safe}' not found.", status=404)
    return send_from_directory(
        directory     = str(OUTPUT_DIR.resolve()),
        path          = safe,
        as_attachment = False,    # ← False = opens in browser directly
        mimetype      = "text/html",
    )




"chart": {
    "output_html": "output/chart_users_available_districtwise__20260512.html",
    "plotly_code": "import pandas as pd\nimport plotly.express as px\n...",
    "error": null
}



