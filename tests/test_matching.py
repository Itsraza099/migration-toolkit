from migration_toolkit.matching import Band, best_match

TARGET = {"t1": "Acme Widgets Ltd", "t2": "Northwind Traders"}


def test_near_identical_name_auto_links() -> None:
    m = best_match("ACME widgets ltd", TARGET)
    assert (m.candidate_id, m.band) == ("t1", Band.AUTO)


def test_similar_name_goes_to_review() -> None:
    m = best_match("Acme Widgets Limited", TARGET)
    assert m.band is Band.REVIEW and m.candidate_id == "t1"


def test_unrelated_name_is_new() -> None:
    m = best_match("Brightside Bakery", TARGET)
    assert m.band is Band.NEW and m.candidate_id is None


def test_no_candidates() -> None:
    assert best_match("x", {}).band is Band.NEW
