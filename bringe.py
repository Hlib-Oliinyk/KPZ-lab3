from abc import ABC, abstractmethod


class IRenderer(ABC):
    @abstractmethod
    def render(self, shape: str):
        pass


class VectorRenderer(IRenderer):
    def render(self, shape: str):
        print(f"Drawing {shape} as vectors")


class RasterRenderer(IRenderer):
    def render(self, shape: str):
        print(f"Drawing {shape} as pixels")


class Shape(ABC):
    def __init__(self, renderer: IRenderer):
        self.renderer = renderer

    @abstractmethod
    def draw(self):
        pass


class Circle(Shape):
    def draw(self):
        self.renderer.render("Circle")

class Square(Shape):
    def draw(self):
        self.renderer.render("Square")

class Triangle(Shape):
    def draw(self):
        self.renderer.render("Triangle")


def main():
    vector = VectorRenderer()
    raster = RasterRenderer()

    Circle(vector).draw()
    Circle(raster).draw()

    Square(vector).draw()
    Square(raster).draw()

    Triangle(vector).draw()
    Triangle(raster).draw()


if __name__ == "__main__":
    main()