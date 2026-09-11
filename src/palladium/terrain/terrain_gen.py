class TerrainSurface:
    def __init__(self, heightmap: list[list[float]]):
        self.heightmap = heightmap

    def get_height(self, x: int, y: int) -> float:
        return self.heightmap[y][x]
