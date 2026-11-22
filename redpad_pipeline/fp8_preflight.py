"""Fail-closed checks for the explicitly scoped, still-disabled FP8 research route.

No imports of model libraries, automatic downloads, model construction or route
promotion. A caller must verify the secure worker/runtime before device probing.
"""
KERNEL_REVISION = '3c8fcc86c0e42b7abe5bcf666d3a3afdce93a0e8'
MODEL_REPO = 'Qwen/Qwen3.5-35B-A3B-FP8'
MODEL_REVISION = '9d1823d2dee688a6b25e77009dc727688c44936e'
REQUIRED_KERNELS = ('matmul_2d', 'matmul_batched', 'matmul_grouped')


def validate_resolution(revision):
    if revision != KERNEL_REVISION:
        raise RuntimeError('FP8 kernel resolution differs from the reviewed immutable v4 commit')


def precision_gate(backend, capabilities, kernel, config, validate_backend):
    """Reject fallback before any caller may construct/load a model.

    Capabilities must cover every device assigned by the verified caller. This
    contract does not measure kernel precision, outputs, memory or GPU fit.
    """
    if backend != 'cuda' or not isinstance(capabilities, (tuple, list)) or not capabilities:
        raise RuntimeError('No assigned CUDA device; CPU/disk fallback is prohibited')
    if any(type(c) is not tuple or len(c) != 2 or
           any(type(n) is not int or n < 0 for n in c) or c < (8, 9)
           for c in capabilities):
        raise RuntimeError('Unsupported capability on at least one assigned CUDA device')
    if any(not callable(getattr(kernel, name, None)) for name in REQUIRED_KERNELS):
        raise RuntimeError('Missing reviewed grouped/batched FP8 kernel entry point')
    if getattr(config, 'dequantize', None) is not False:
        raise RuntimeError('Initial FP8 state is unknown or already dequantized')
    validate_backend()
    if getattr(config, 'dequantize', None) is not False:
        raise RuntimeError('Backend enabled BF16 dequantization or unknown precision state')
    return {'preflight_passed': True, 'kernel_execution_verified': False,
            'model_inference_verified': False, 'production_ready': False}


def assigned_device_gate(torch, kernel, quantizer, assigned_devices, *, isolated_runtime_verified=False):
    """Future secure-worker entry, not permission to launch an accelerator job."""
    if isolated_runtime_verified is not True:
        raise RuntimeError('Secure host and exact runtime binding must pass before CUDA checks')
    if (not isinstance(assigned_devices, (list, tuple)) or not assigned_devices or
            any(type(n) is not int or n < 0 for n in assigned_devices) or
            len(set(assigned_devices)) != len(assigned_devices)):
        raise RuntimeError('Exact unique assigned CUDA device identifiers required')
    if torch.version.cuda is None or not torch.cuda.is_available():
        raise RuntimeError('Approved CUDA runtime/device unavailable')
    capabilities = [torch.cuda.get_device_capability(n) for n in assigned_devices]
    return precision_gate('cuda', capabilities, kernel, quantizer.quantization_config,
                          quantizer.validate_environment)
