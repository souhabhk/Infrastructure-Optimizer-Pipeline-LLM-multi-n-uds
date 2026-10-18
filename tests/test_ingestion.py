from app.pipeline.nodes.ingestion import ingestion_node


def test_valid_records_pass(raw_record):
    out = ingestion_node({"raw_records": [raw_record(), raw_record(cpu_usage=90)]})
    assert len(out["records"]) == 2
    assert out["invalid_count"] == 0


def test_bad_records_are_skipped(raw_record):
    raw = [raw_record(), {"garbage": True}, raw_record(cpu_usage=250)]
    out = ingestion_node({"raw_records": raw})
    assert len(out["records"]) == 1
    assert out["invalid_count"] == 2
