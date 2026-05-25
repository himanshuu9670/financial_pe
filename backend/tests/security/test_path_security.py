from app.utils.path_security import safe_filename


def test_empty_uses_default():
    assert safe_filename("") == "file.pdf"


def test_strips_directory_components():
    assert safe_filename("/var/tmp/evil.pdf") == "evil.pdf"
