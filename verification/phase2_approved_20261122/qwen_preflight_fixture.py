"""Synthetic contract fixture only. No worker wiring or model loading."""
import unittest

REQUIRED = ("matmul_2d", "matmul_batched", "matmul_grouped")


def preflight(backend, capabilities, kernels, before, validate):
    if backend != "cuda" or not capabilities:
        raise RuntimeError("no assigned CUDA device")
    if any(type(pair) is not tuple or len(pair) != 2
           or any(type(n) is not int or n < 0 for n in pair)
           or pair < (8, 9) for pair in capabilities):
        raise RuntimeError("unsupported CUDA capability")
    if any(not callable(kernels.get(name)) for name in REQUIRED):
        raise RuntimeError("missing FP8 kernel entry point")
    if before is not False:
        raise RuntimeError("initial FP8 precision state invalid")
    if validate() is not False:
        raise RuntimeError("BF16 fallback or unknown precision state")


class TestPreflight(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(backend="cuda", capabilities=[(8, 9)],
                           kernels=dict.fromkeys(REQUIRED, lambda: None),
                           before=False, validate=lambda: False)

    def rejects(self, reason, **changes):
        with self.assertRaisesRegex(RuntimeError, reason):
            preflight(**(self.inputs | changes))

    def test_valid_mock(self):
        self.assertIsNone(preflight(**self.inputs))

    def test_no_device(self):
        self.rejects("no assigned", capabilities=[])

    def test_non_cuda(self):
        self.rejects("no assigned", backend="cpu")

    def test_secondary_unsupported(self):
        self.rejects("unsupported", capabilities=[(9, 0), (8, 6)])

    def test_malformed_capability(self):
        self.rejects("unsupported", capabilities=[(8, "9")])

    def test_grouped_missing(self):
        self.rejects("missing", kernels={"matmul_2d": lambda: None,
                                        "matmul_batched": lambda: None})

    def test_grouped_non_callable(self):
        self.rejects("missing", kernels=self.inputs["kernels"] | {"matmul_grouped": True})

    def test_already_dequantized(self):
        self.rejects("initial", before=True)

    def test_fallback(self):
        self.rejects("BF16 fallback", validate=lambda: True)

    def test_state_unavailable(self):
        self.rejects("unknown precision", validate=lambda: None)

    def test_validator_error_propagates(self):
        def failure():
            raise RuntimeError("validator unavailable")
        self.rejects("validator unavailable", validate=failure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
