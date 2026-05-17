"""Report generation for theolog-bench results."""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_report(results: dict) -> str:
    """Generate a formatted text report from benchmark results."""
    model_name = results.get("model_name", "unknown")
    timestamp = results.get("timestamp", "unknown")
    questions = results.get("questions", [])

    lines = []
    lines.append("=" * 60)
    lines.append(f"theolog-bench Results: {model_name}")
    lines.append(f"Date: {timestamp}")
    lines.append("=" * 60)

    # Collect per-category scores
    cat_scores: dict[str, list[int]] = {}
    cat_counts: dict[str, int] = {}
    for q in questions:
        cat = q["category"]
        score = q.get("score", 0)
        cat_scores.setdefault(cat, []).append(score)
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    cat_weights = results.get("category_weights", {})
    overall = 0.0
    total_weight = 0.0

    lines.append("")
    lines.append("Category Breakdown:")

    for cat_name, scores in sorted(cat_scores.items()):
        avg = sum(scores) / len(scores) if scores else 0
        weight = cat_weights.get(cat_name, 0)
        overall += avg * weight
        total_weight += weight
        display_name = cat_name.replace("_", " ").title()
        lines.append(
            f"  {display_name:30s} {avg:5.1f} / 100"
            f"  ({len(scores)}/{cat_counts[cat_name]} answered)"
        )

    if total_weight > 0:
        overall = overall / total_weight

    # Insert overall score after the header block
    lines.insert(4, "")
    lines.insert(5, f"Overall Score: {overall:.1f} / 100")

    # Flagged failures (score < 40)
    failures = [q for q in questions if q.get("score", 0) < 40]
    if failures:
        lines.append("")
        lines.append(f"Flagged Failures (score < 40): {len(failures)} questions")
        for q in failures[:20]:
            detail = q.get("score_details", {}).get("justification", "")
            if not detail:
                detail = q.get("score_details", {}).get("detected_position", "")
            lines.append(
                f"  [{q['id']}] {q.get('question', '')[:60]}..."
                f" (score: {q.get('score', 0)})"
            )

    lines.append("")
    results_path = results.get("results_path", "")
    if results_path:
        lines.append(f"Full results: {results_path}")
    lines.append("=" * 60)

    return "\n".join(lines)


def generate_comparison_report(results_list: list[dict], title: str = None) -> str:
    """Generate a markdown comparison report between multiple benchmark runs.

    Uses a markdown table with models as rows and categories as columns,
    sorted by overall score descending. Works well for 2-20+ models.

    Args:
        results_list: List of benchmark result dicts.
        title: Custom report title (default: "theolog-bench Comparison Report").
    """
    if len(results_list) < 2:
        return "Need at least 2 result sets to compare."

    # Category display names (short for column headers)
    cat_short = {
        "catechism_recall": "Catech",
        "confessional_knowledge": "Confes",
        "doctrinal_position": "Doctrn",
        "biblical_reference": "BibRef",
        "error_detection": "ErrDet",
        "comparative_theology": "Compar",
    }

    # Compute per-model category averages and overall score
    model_data = []
    all_cats: set[str] = set()
    for results in results_list:
        name = results.get("model_name", "unknown")
        cat_scores: dict[str, list[int]] = {}
        for q in results.get("questions", []):
            cat = q["category"]
            cat_scores.setdefault(cat, []).append(q.get("score", 0))
        all_cats.update(cat_scores.keys())

        cat_avgs = {}
        for cat, scores in cat_scores.items():
            cat_avgs[cat] = sum(scores) / len(scores) if scores else 0.0

        cat_weights = results.get("category_weights", {})
        overall = 0.0
        total_weight = 0.0
        for cat, avg in cat_avgs.items():
            w = cat_weights.get(cat, 0)
            overall += avg * w
            total_weight += w
        if total_weight > 0:
            overall /= total_weight

        model_data.append({
            "name": name,
            "cat_avgs": cat_avgs,
            "overall": overall,
        })

    # Sort by overall score descending
    model_data.sort(key=lambda m: m["overall"], reverse=True)
    cats_ordered = sorted(all_cats)

    report_title = title or "theolog-bench Comparison Report"

    lines = []
    lines.append(f"# {report_title}")
    lines.append("")

    # Build markdown table header
    hdr_cols = ["#", "Model"]
    for cat in cats_ordered:
        hdr_cols.append(cat_short.get(cat, cat[:6].title()))
    hdr_cols.append("OVERALL")

    lines.append("| " + " | ".join(hdr_cols) + " |")

    # Alignment row: right-align numbers, left-align model
    align = [":--:"] + [":--"] + ["--:"] * (len(cats_ordered) + 1)
    lines.append("| " + " | ".join(align) + " |")

    # Data rows
    for rank, m in enumerate(model_data, 1):
        cols = [str(rank), m["name"]]
        for cat in cats_ordered:
            avg = m["cat_avgs"].get(cat, 0.0)
            cols.append(f"{avg:.1f}%")
        cols.append(f"**{m['overall']:.1f}%**")
        lines.append("| " + " | ".join(cols) + " |")

    # Delta if exactly 2 models
    if len(results_list) == 2:
        delta = model_data[0]["overall"] - model_data[1]["overall"]
        lines.append("")
        lines.append(
            f"Delta ({model_data[0]['name']} vs {model_data[1]['name']}): "
            f"+{delta:.1f} points"
        )

    return "\n".join(lines)


# Category display names for detailed reports
_CAT_DISPLAY = {
    "catechism_recall": "Catechism Recall",
    "confessional_knowledge": "Confessional Knowledge",
    "doctrinal_position": "Doctrinal Position",
    "biblical_reference": "Biblical Reference",
    "error_detection": "Error Detection",
    "comparative_theology": "Comparative Theology",
}


def _compute_report_data(results_list: list[dict], config: dict,
                         group_name: str = None) -> dict:
    """Compute structured data from benchmark results for report generation.

    Returns a dict with per-model stats, rankings, and metadata suitable
    for building an LLM prompt.
    """
    presets = config.get("presets", {})

    models = []
    all_cats: set[str] = set()

    for results in results_list:
        model_name = results.get("model_name", "unknown")
        questions = results.get("questions", [])

        # Look up meta from config presets by matching model name
        meta = {}
        for preset_cfg in presets.values():
            if preset_cfg.get("model") == model_name or \
               preset_cfg.get("model_path", "").endswith(model_name):
                meta = preset_cfg.get("meta", {})
                break

        # Compute per-category scores
        cat_scores: dict[str, list[int]] = {}
        for q in questions:
            cat = q["category"]
            cat_scores.setdefault(cat, []).append(q.get("score", 0))
        all_cats.update(cat_scores.keys())

        cat_avgs = {}
        for cat, scores in cat_scores.items():
            cat_avgs[cat] = round(sum(scores) / len(scores), 1) if scores else 0.0

        # Weighted overall score
        cat_weights = results.get("category_weights", {})
        overall = 0.0
        total_weight = 0.0
        for cat, avg in cat_avgs.items():
            w = cat_weights.get(cat, 0)
            overall += avg * w
            total_weight += w
        if total_weight > 0:
            overall /= total_weight

        # Failure counts
        severe_failures = sum(1 for q in questions if q.get("score", 0) < 20)
        zeros = sum(1 for q in questions if q.get("score", 0) == 0)

        models.append({
            "name": model_name,
            "meta": meta,
            "cat_avgs": cat_avgs,
            "overall": round(overall, 1),
            "total_questions": len(questions),
            "severe_failures": severe_failures,
            "zeros": zeros,
        })

    # Sort by overall score descending
    models.sort(key=lambda m: m["overall"], reverse=True)

    # Determine category winners
    cats_ordered = sorted(all_cats)
    cat_winners = {}
    for cat in cats_ordered:
        best_score = -1
        best_model = ""
        for m in models:
            score = m["cat_avgs"].get(cat, 0.0)
            if score > best_score:
                best_score = score
                best_model = m["name"]
        cat_winners[cat] = best_model

    return {
        "group_name": group_name or "Model Comparison",
        "models": models,
        "categories": cats_ordered,
        "category_weights": results_list[0].get("category_weights", {}),
        "cat_winners": cat_winners,
        "run_date": datetime.now().strftime("%B %d, %Y"),
    }


def _build_report_prompt(report_data: dict, example_report: str,
                         group_description: str = None) -> str:
    """Build the LLM prompt for generating a detailed narrative report.

    Includes the computed data, style example, and instructions.
    """
    models = report_data["models"]
    categories = report_data["categories"]
    cat_weights = report_data["category_weights"]
    cat_winners = report_data["cat_winners"]
    group_name = report_data["group_name"]

    # Build the data summary for the LLM
    data_lines = []
    data_lines.append(f"Report title: {group_name}")
    if group_description:
        data_lines.append(f"Group description: {group_description}")
    data_lines.append(f"Number of models: {len(models)}")
    data_lines.append(f"Run date: {report_data['run_date']}")
    data_lines.append("")

    # Overall rankings
    data_lines.append("=== OVERALL RANKINGS ===")
    for rank, m in enumerate(models, 1):
        meta = m["meta"]
        arch = meta.get("architecture", "unknown")
        vendor = meta.get("vendor", "unknown")
        local = "Yes" if meta.get("local_capable") else "No"
        data_lines.append(
            f"  #{rank}: {m['name']} — {arch} (vendor: {vendor}) — "
            f"Overall: {m['overall']}% — "
            f"Severe failures (<20): {m['severe_failures']}/{m['total_questions']} — "
            f"Zeros: {m['zeros']} — "
            f"Local capable: {local}"
        )
    data_lines.append("")

    # Category breakdown
    data_lines.append("=== CATEGORY BREAKDOWN ===")
    for cat in categories:
        weight = cat_weights.get(cat, 0)
        display = _CAT_DISPLAY.get(cat, cat.replace("_", " ").title())
        winner = cat_winners.get(cat, "")
        data_lines.append(f"  {display} (weight: {weight:.0%}):")
        for m in models:
            score = m["cat_avgs"].get(cat, 0.0)
            marker = " ** BEST **" if m["name"] == winner else ""
            data_lines.append(f"    {m['name']}: {score}%{marker}")
    data_lines.append("")

    # Per-model detail
    data_lines.append("=== PER-MODEL DETAILS ===")
    for m in models:
        meta = m["meta"]
        data_lines.append(f"  Model: {m['name']}")
        data_lines.append(f"    Vendor: {meta.get('vendor', 'unknown')}")
        data_lines.append(f"    Architecture: {meta.get('architecture', 'unknown')}")
        data_lines.append(f"    Parameters: {meta.get('params', 'unknown')}")
        data_lines.append(f"    Local capable: {meta.get('local_capable', False)}")
        data_lines.append(f"    Overall: {m['overall']}%")
        data_lines.append(f"    Severe failures: {m['severe_failures']}/{m['total_questions']}")
        data_lines.append(f"    Zeros: {m['zeros']}")

        # Category scores
        best_cats = sorted(m["cat_avgs"].items(), key=lambda x: x[1], reverse=True)
        strengths = [(c, s) for c, s in best_cats[:3] if s > 0]
        weaknesses = [(c, s) for c, s in best_cats[-2:] if s < best_cats[0][1]]
        if strengths:
            data_lines.append(f"    Top categories: {', '.join(f'{_CAT_DISPLAY.get(c, c)} ({s}%)' for c, s in strengths)}")
        if weaknesses:
            data_lines.append(f"    Weakest categories: {', '.join(f'{_CAT_DISPLAY.get(c, c)} ({s}%)' for c, s in weaknesses)}")
        data_lines.append("")

    data_summary = "\n".join(data_lines)

    prompt = (
        "You are a technical writer producing a benchmark comparison report for "
        "theolog-bench, a Reformed theology evaluation benchmark.\n\n"
        "Below is a STYLE EXAMPLE of what the output should look like. Match its "
        "structure, tone, and formatting closely:\n\n"
        "--- STYLE EXAMPLE START ---\n"
        f"{example_report}\n"
        "--- STYLE EXAMPLE END ---\n\n"
        "Now generate a NEW report for the following data. Do NOT copy the example's "
        "specific findings — use only the data provided below.\n\n"
        "--- BENCHMARK DATA START ---\n"
        f"{data_summary}\n"
        "--- BENCHMARK DATA END ---\n\n"
        "Requirements:\n"
        "1. Start with a brief intro paragraph describing what was tested.\n"
        "2. Include an 'Overall Rankings' markdown table with columns: #, Model, "
        "Architecture, and Overall score. Bold the top performer.\n"
        "3. Include a 'Category Breakdown' markdown table with a column per model. "
        "Bold the best score in each row.\n"
        "4. Include a 'Detailed Analysis' section with a subsection per model "
        "(ranked by score). For each model, discuss strengths, weaknesses, "
        "failure patterns, and architecture notes.\n"
        "5. If relevant, include a 'Context' section comparing to other tiers.\n"
        "6. End with a 'Recommendation' section with a clear verdict.\n"
        "7. End with an italicized footer noting the scorer version, judge model, "
        "and run date.\n"
        "8. Output ONLY the markdown report, no preamble or commentary.\n"
        "9. Use the category weights when discussing which categories matter most.\n"
        "10. Cite specific numbers from the data — do not invent scores.\n"
        "11. Before the footer, include a brief 'Scoring Notes' section with these "
        "two caveats: (a) Doctrinal Position and Error Detection (35% combined) use "
        "regex pattern matching that favors direct affirm/deny answers over balanced "
        "multi-perspective responses — models that hedge or present comparative views "
        "may score lower than their understanding warrants; (b) Catechism Recall (25%) "
        "rewards near-verbatim recall of catechism phrasing, giving a natural advantage "
        "to models trained on Reformed source texts.\n"
    )

    return prompt


def generate_detailed_report(results_list: list[dict], config: dict,
                             group_name: str = None,
                             group_description: str = None) -> str:
    """Generate a detailed narrative markdown report using the judge LLM.

    Computes all score data in Python, then sends it to the judge LLM with
    a prompt template and style example to generate the report.

    Falls back to generate_comparison_report() if the LLM call fails.
    """
    if len(results_list) < 2:
        return "Need at least 2 result sets to generate a detailed report."

    # Compute report data
    report_data = _compute_report_data(results_list, config, group_name)

    # Load the style example
    example_path = Path(__file__).parent.parent / "results" / "reports" / "96gb-card-comparison.md"
    try:
        example_report = example_path.read_text()
    except FileNotFoundError:
        example_report = "(No style example available — use standard benchmark report formatting.)"

    # If no group_description provided, try to look it up from config
    if group_description is None and group_name:
        group_descriptions = config.get("group_descriptions", {})
        # Try exact match, then lowercase match
        group_description = group_descriptions.get(group_name)
        if group_description is None:
            group_description = group_descriptions.get(group_name.lower())

    # Build prompt
    prompt = _build_report_prompt(report_data, example_report, group_description)

    # Create APIBackend from judge config
    try:
        from lib.backends import APIBackend

        judge_cfg = config.get("judge", {})
        backend = APIBackend(
            api_url=judge_cfg.get("api_url", "https://openrouter.ai/api/v1"),
            model=judge_cfg.get("model", "google/gemini-2.5-flash"),
            api_key=judge_cfg.get("api_key"),
            max_tokens=4096,
        )

        logger.info("Generating detailed report using %s...", backend.name())
        report = backend.generate(prompt)

        if not report or len(report.strip()) < 100:
            logger.warning("LLM returned empty/short response, falling back to leaderboard")
            return generate_comparison_report(results_list)

        return report

    except Exception as e:
        logger.warning("Detailed report generation failed: %s", e)
        logger.warning("Falling back to leaderboard comparison report")
        return generate_comparison_report(results_list)
