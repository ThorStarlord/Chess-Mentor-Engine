from pathlib import Path


def test_authoritative_docs_do_not_claim_v1_release_is_still_pending() -> None:
    paths = (
        Path("CONTEXT.md"),
        Path("docs/architecture/architecture.md"),
    )
    forbidden = (
        "remaining repository blocker for Version 1.0",
        "next required V1 package",
        "remaining repository V1 task is release/distribution qualification",
    )

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text, f"stale V1 authority in {path}: {phrase}"


def test_post_v1_spec_uses_descriptive_product_use_claim_ceiling() -> None:
    text = Path(
        "docs/product/post-v1-local-product-use-observation.md"
    ).read_text(encoding="utf-8")

    assert "descriptive_local_product_use_only" in text
    assert "learning_effect = not_established" in text
    assert "tutor_efficacy = not_established" in text
    assert "mastery = not_established" in text
    assert "does not execute the M46 proposal" in text
