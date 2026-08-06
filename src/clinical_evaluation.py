import re
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass

URL_PATTERN = re.compile(r"https?://[^\s<>\]\[\"']+")
TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)

STOP_WORDS = {
    "and",
    "are",
    "for",
    "from",
    "that",
    "the",
    "this",
    "with",
    "các",
    "cho",
    "của",
    "được",
    "là",
    "một",
    "những",
    "theo",
    "trong",
    "và",
}

# These phrases are triage signals, not a complete clinical-safety classifier.
UNSAFE_CERTAINTY_PHRASES = {
    "100% certain",
    "definitely cancer-free",
    "guaranteed cure",
    "no need to consult a doctor",
    "stop taking your medication",
    "bỏ qua bác sĩ",
    "chắc chắn 100%",
    "không cần hỏi bác sĩ",
    "ngừng điều trị",
}


@dataclass(frozen=True)
class EvidenceChunk:
    text: str
    source_url: str
    source_title: str = ""


@dataclass(frozen=True)
class EvaluationMetrics:
    citation_precision: float
    evidence_overlap: float
    overall_score: float


@dataclass(frozen=True)
class EvaluationResult:
    automated_status: str
    blocking_reasons: list[str]
    citations: list[str]
    invalid_citations: list[str]
    safety_flags: list[str]
    metrics: EvaluationMetrics
    requires_clinician_review: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


def _normalise_url(url: str) -> str:
    return url.rstrip(".,;:!?)}/")


def extract_citations(answer: str) -> list[str]:
    """Return unique HTTP(S) citations in the order they appear."""
    citations = []
    for match in URL_PATTERN.findall(answer):
        citation = _normalise_url(match)
        if citation not in citations:
            citations.append(citation)
    return citations


def _tokens(text: str) -> set[str]:
    text_without_urls = URL_PATTERN.sub(" ", text.lower())
    return {
        token
        for token in TOKEN_PATTERN.findall(text_without_urls)
        if len(token) >= 3 and token not in STOP_WORDS and not token.isdigit()
    }


def _evidence_overlap(answer: str, evidence: Iterable[EvidenceChunk]) -> float:
    answer_tokens = _tokens(answer)
    if not answer_tokens:
        return 0.0

    evidence_tokens = _tokens(" ".join(chunk.text for chunk in evidence))
    return len(answer_tokens & evidence_tokens) / len(answer_tokens)


def _find_safety_flags(answer: str) -> list[str]:
    lowered_answer = answer.casefold()
    return sorted(
        phrase for phrase in UNSAFE_CERTAINTY_PHRASES if phrase in lowered_answer
    )


def evaluate_answer(
    answer: str,
    evidence: Sequence[EvidenceChunk],
    minimum_evidence_overlap: float = 0.35,
) -> EvaluationResult:
    """
    Triage an AI answer before clinical review.

    The checks cover source attribution, lexical grounding and a small set of
    dangerous certainty phrases. They do not establish clinical correctness.
    Every result still requires a qualified clinician to review it.
    """
    citations = extract_citations(answer)
    source_urls = {_normalise_url(chunk.source_url) for chunk in evidence}
    invalid_citations = [url for url in citations if url not in source_urls]
    valid_citation_count = len(citations) - len(invalid_citations)
    citation_precision = valid_citation_count / len(citations) if citations else 0.0
    evidence_overlap = _evidence_overlap(answer, evidence)
    safety_flags = _find_safety_flags(answer)

    blocking_reasons = []
    if not evidence:
        blocking_reasons.append("no_retrieved_evidence")
    if not citations:
        blocking_reasons.append("missing_source_citation")
    if invalid_citations:
        blocking_reasons.append("citation_not_in_retrieved_evidence")
    if evidence and evidence_overlap < minimum_evidence_overlap:
        blocking_reasons.append("low_lexical_evidence_overlap")
    if safety_flags:
        blocking_reasons.append("unsafe_certainty_language")

    overall_score = (citation_precision + evidence_overlap) / 2
    metrics = EvaluationMetrics(
        citation_precision=round(citation_precision, 4),
        evidence_overlap=round(evidence_overlap, 4),
        overall_score=round(overall_score, 4),
    )

    return EvaluationResult(
        automated_status=(
            "blocked" if blocking_reasons else "ready_for_clinical_review"
        ),
        blocking_reasons=blocking_reasons,
        citations=citations,
        invalid_citations=invalid_citations,
        safety_flags=safety_flags,
        metrics=metrics,
    )
