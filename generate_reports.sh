#!/bin/bash
# Regenerate all comparison reports from current result data.
# Run this after re-judging or adding new model results.

set -e
cd "$(dirname "$0")"

REPORTS=results/reports
EXCLUDE="reformed qwen3-1.7b"

echo "Generating leaderboard..."
python3 report.py --all --exclude $EXCLUDE \
    --title "theolog-bench Leaderboard" \
    --output "$REPORTS/leaderboard.md"

echo "Generating tier group reports..."
for group in 12gb 24gb 48gb 96gb budget mid frontier; do
    echo "  $group..."
    python3 report.py --all --group "$group" \
        --output "$REPORTS/${group}-comparison.md"
done

echo "Done. All reports written to $REPORTS/"
