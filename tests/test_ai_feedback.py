from backend.core.schemas import LLMWeakConcept, LLMSessionFeedback


def test_session_feedback_contains_weak_concepts() -> None:
    """Validate the structured feedback response shape."""
    feedback = LLMSessionFeedback(
        weak_concepts=[
            LLMWeakConcept(
                concept="Newton's second law",
                advice="Review force-mass-acceleration relationships.",
            )
        ]
    )

    assert feedback.weak_concepts[0].concept == "Newton's second law"
    assert "Review" in feedback.weak_concepts[0].advice
