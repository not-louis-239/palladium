def snoise2(
        x: float,
        y: float,
        *,
        octaves: int = 1,
        persistence: float = 0.5,
        repeatx: int | None = None,
        repeaty: int | None = None,
        lacunarity: float = 2.0,
        base: int | None = None,
    ) -> float:
    """Return a float from -1 to 1 using Simplex Noise."""
    ...
