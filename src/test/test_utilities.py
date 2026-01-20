from server.utilities import trim_name


def test_trim_name():
    assert trim_name("model.version.1") == "1"
    assert trim_name("data.file.csv") == "csv"
    assert trim_name("no_extension") == "no_extension"
    assert trim_name(".hiddenfile") == "hiddenfile"
