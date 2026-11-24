from app.api.schemas import Flag, KnowledgePassage
from app.pipeline.explain import ground_flags
from app.pipeline.scoring import score_flags


def _flag(rule_id: str, severity: str, weight: int) -> Flag:
    return Flag(
        rule_id=rule_id,
        severity=severity,
        weight=weight,
        title_en="title",
        title_bn="শিরোনাম",
        explanation_en="because",
        explanation_bn="কারণ",
        evidence_snippet="snippet",
        kb_ids=["licensed-agent-required"],
    )


def test_high_weights_are_danger():
    flags = [_flag("R07_license", "high", 30), _flag("R03_fee_cap", "high", 28), _flag("R05_salary", "high", 26)]
    verdict, score = score_flags(flags)
    assert verdict == "danger"
    assert score == 84


def test_single_high_flag_is_caution():
    verdict, score = score_flags([_flag("R07_license", "high", 30)])
    assert verdict == "caution"
    assert score == 30


def test_no_flags_is_fewer_concerns():
    verdict, score = score_flags([])
    assert verdict == "fewer_concerns"
    assert score == 0


def test_never_uses_safe():
    verdict, _ = score_flags([])
    assert verdict != "safe"


def test_explanations_include_knowledge_base_passage():
    flags = ground_flags([_flag("R07_license", "high", 30)])
    assert flags[0].passages
    assert isinstance(flags[0].passages[0], KnowledgePassage)
    assert flags[0].passages[0].text
    assert "Official note:" in flags[0].explanation_en
