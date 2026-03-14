from exchange.writer import write_og_exchange
import json
import os

def test_writer(tmp_path):
    data = {"test": "data"}
    output = tmp_path / "out.json"
    write_og_exchange(data, output)
    
    assert output.exists()
    with open(output) as f:
        assert json.load(f) == data
