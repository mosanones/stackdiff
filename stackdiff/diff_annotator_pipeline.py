"""Pipeline that chains diff annotation, scoring, and recommendation into a single result."""
from dataclasses import dataclass, field
from typing import Optional

from stackdiff.diff_engine import DiffResult
from stackdiff.annotator import AnnotatedDiff, annotate_diff
from stackdiff.scorer import DiffScore, score_annotated
from stackdiff.diff_recommender import RecommendationReport, generate_recommendations
from stackdiff.summarizer import DiffSummary, build_summary


@dataclass
class AnnotatorPipelineResult:
    diff: DiffResult
    annotated: AnnotatedDiff
    score: DiffScore
    summary: DiffSummary
    recommendations: RecommendationReport

    def as_dict(self) -> dict:
        return {
            "score": self.score.as_dict(),
            "summary": {
                "total_changes": self.summary.total_changes,
                "critical_keys": self.summary.critical_keys,
                "high_keys": self.summary.high_keys,
            },
            "recommendations": self.recommendations.as_dict(),
            "annotations": [
                {
                    "key": a.key,
                    "severity": a.severity,
                    "category": a.category,
                    "removed": a.removed,
                    "added": a.added,
                }
                for a in self.annotated.annotations
            ],
        }


def run_annotator_pipeline(
    diff: DiffResult,
    extra_sensitive_patterns: Optional[list] = None,
) -> AnnotatorPipelineResult:
    """Run annotation, scoring, summarization, and recommendation on a DiffResult."""
    annotated = annotate_diff(diff)
    score = score_annotated(annotated)
    summary = build_summary(score, annotated)
    recommendations = generate_recommendations(annotated)
    return AnnotatorPipelineResult(
        diff=diff,
        annotated=annotated,
        score=score,
        summary=summary,
        recommendations=recommendations,
    )
