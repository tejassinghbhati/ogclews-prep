def test_metadata_written(tmp_path):
    from runner.output_writer import OutputWriter
    import json
    w = OutputWriter(tmp_path, "run_001", "test_scenario")
    w.write_metadata({"foo": "bar"})
    meta = json.loads((tmp_path / "run_001" / "metadata.json").read_text())
    assert meta["status"] == "running"
    assert meta["run_id"] == "run_001"