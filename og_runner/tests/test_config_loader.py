def test_load_config_returns_run_id(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("""
run:
  scenario_name: test
  country_module: ""
  time_path: false
  start_year: 2025
og_spec:
  alpha_T: [0.09]
output:
  base_dir: outputs
""")
    from runner.config_loader import load_config
    config = load_config(str(cfg_path))
    assert config.run_id is not None
    assert config.scenario_name == "test"