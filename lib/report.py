"""Report generation for theolog-bench results."""


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


def generate_comparison_report(results_list: list[dict]) -> str:
    """Generate a comparison report between multiple benchmark runs.

    Uses a leaderboard layout with models as rows and categories as columns,
    sorted by overall score descending. Works well for 2-20+ models.
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

    # Determine model name column width (fit full names)
    max_name = max(len(m["name"]) for m in model_data)
    name_width = max(max_name, 5) + 2  # at least "Model" + padding

    lines = []
    lines.append("=" * 80)
    lines.append("theolog-bench Comparison Report")
    lines.append("=" * 80)
    lines.append("")

    # Build header: Rank | Model | cat1 | cat2 | ... | OVERALL
    hdr = f"{'#':>3s}  {'Model':<{name_width}s}"
    for cat in cats_ordered:
        short = cat_short.get(cat, cat[:6].title())
        hdr += f"  {short:>6s}"
    hdr += f"  {'OVERALL':>7s}"
    lines.append(hdr)
    lines.append("-" * len(hdr))

    # Data rows
    for rank, m in enumerate(model_data, 1):
        row = f"{rank:>3d}  {m['name']:<{name_width}s}"
        for cat in cats_ordered:
            avg = m["cat_avgs"].get(cat, 0.0)
            row += f"  {avg:>5.1f}%"
        row += f"  {m['overall']:>6.1f}%"
        lines.append(row)

    lines.append("-" * len(hdr))

    # Delta if exactly 2 models
    if len(results_list) == 2:
        delta = model_data[0]["overall"] - model_data[1]["overall"]
        lines.append("")
        lines.append(
            f"Delta ({model_data[0]['name']} vs {model_data[1]['name']}): "
            f"+{delta:.1f} points"
        )

    lines.append("=" * 80)
    return "\n".join(lines)
