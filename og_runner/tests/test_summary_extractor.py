def test_to_scalar_numpy():
    import numpy as np
    from runner.summary_extractor import _to_scalar
    assert _to_scalar(np.array([3.14])) == 3.14
    assert isinstance(_to_scalar(np.array([1.0, 2.0])), list)