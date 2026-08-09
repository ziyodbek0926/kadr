from app.utils.sanitize import sanitize_rich_text


def test_strips_script_tag() -> None:
    result = sanitize_rich_text("<p>Yaxshi xodim</p><script>alert('xss')</script>")
    assert "<script>" not in result
    assert "alert" not in result
    assert "Yaxshi xodim" in result


def test_strips_event_handler_attribute() -> None:
    result = sanitize_rich_text('<p onclick="alert(1)">Matn</p>')
    assert "onclick" not in result
    assert "Matn" in result


def test_keeps_allowed_formatting_tags() -> None:
    result = sanitize_rich_text("<p><b>Muhim</b> va <i>e'tiborli</i></p>")
    assert "<b>Muhim</b>" in result
    assert "<i>e'tiborli</i>" in result


def test_none_passthrough() -> None:
    assert sanitize_rich_text(None) is None
