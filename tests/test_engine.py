from core.strategies import ExtensionStrategy


def test_extension_sorting():
    """L6 Test: Ensure Strategy Pattern maps extensions correctly."""
    mappings = {"Images": [".jpg", ".png"], "Docs": [".pdf"]}
    strategy = ExtensionStrategy(mappings)

    assert strategy.get_folder("vacation.jpg") == "Images"
    assert strategy.get_folder("resume.pdf") == "Docs"
    assert strategy.get_folder("random.exe") == "Others"
