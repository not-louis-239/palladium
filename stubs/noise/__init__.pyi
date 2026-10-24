def snoise2(
        x: float,
        y: float,
        *,
        octaves: int = 1,  # number of layered noise functions
        persistence: float = 0.5,  # ratio of magnitude between octaves
        repeatx: int | None = None,
        repeaty: int | None = None,
        lacunarity: float = 2.0,  # ratio of frequency between octaves
        base: int | None = None,
    ) -> float:
    """Return a float from -1 to 1 using 2D Simplex Noise."""

def snoise3(
        x: float,
        y: float,
        z: float,
        *,
        octaves: int = 1,  # number of layered noise functions
        persistence: float = 0.5,  # ratio of magnitude between octaves
        repeatx: int | None = None,
        repeaty: int | None = None,
        repeatz: int | None = None,
        lacunarity: float = 2.0,  # ratio of frequency between octaves
        base: int | None = None,
    ) -> float:
    """Return a float from -1 to 1 using 3D Simplex Noise."""
