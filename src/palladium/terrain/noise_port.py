# noise_port.py
# typed port of noise's functions because the `noise` library's type stubs
# kinda suck ngl

from noise import snoise2 as _snoise2

def snoise2(
        x: float, y: float, *, scale: float = 1.0,
        octaves: int = 1, persistence: float = 0.5,
        repeatx: int | None = None, repeaty: int | None = None,
        lacunarity: float = 2.0, base: int | None = None,
    ) -> float:
    """Return a float from -1 to 1 based on snoise2 function.
    This is a wrapper function around noise.snoise2 because
    it has no type stubs, which is a bit annoying."""

    if scale == 0:
        raise ValueError("Scale cannot be zero.")

    x *= scale
    y *= scale

    kwargs = {
        "octaves": octaves,
        "persistence": persistence,
        "lacunarity": lacunarity,
    }

    if repeatx is not None:
        kwargs["repeatx"] = repeatx
    if repeaty is not None:
        kwargs["repeaty"] = repeaty
    if base is not None:
        kwargs["base"] = base

    return _snoise2(x, y, **kwargs)
