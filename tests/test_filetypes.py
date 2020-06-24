from netcfgbu.filetypes import CommentedCsvReader


def test_filetypes_csv_hascomments(request):
    filepath = f"{request.fspath.dirname}/files/test-csv-withcomments.csv"
    csv_data = [rec["host"] for rec in (CommentedCsvReader(open(filepath)))]
    assert "switch1" in csv_data
    assert "switch2" in csv_data
    assert "switch3" not in csv_data
    assert "switch4" not in csv_data
