import urllib.request
import sys
from abc import ABC, abstractmethod


class LightNode(ABC):
    @abstractmethod
    def outer_html(self, indent: int = 0) -> str: pass


class LightTextNode(LightNode):
    def __init__(self, text: str):
        self.text = text

    def outer_html(self, indent: int = 0) -> str:
        return "  " * indent + self.text


class LightElementNode(LightNode):
    def __init__(self, tag: str, classes: list[str] = None):
        self.tag = tag
        self.classes = classes or []
        self.children: list[LightNode] = []

    def add(self, node: LightNode) -> "LightElementNode":
        self.children.append(node)
        return self

    def outer_html(self, indent: int = 0) -> str:
        pad = "  " * indent
        attrs = f' class="{" ".join(self.classes)}"' if self.classes else ""
        inner = "\n".join(child.outer_html(indent + 1) for child in self.children)
        return f"{pad}<{self.tag}{attrs}>\n{inner}\n{pad}</{self.tag}>"


class LightElementNodeFlyweight(LightNode):
    def __init__(self, tag: str, classes: list[str] = None):
        self.tag = tag
        self.classes = tuple(classes or [])

    def outer_html(self, indent: int = 0, children: list = None) -> str:
        pad = "  " * indent
        attrs = f' class="{" ".join(self.classes)}"' if self.classes else ""
        inner = "\n".join(child.outer_html(indent + 1) for child in (children or []))
        return f"{pad}<{self.tag}{attrs}>\n{inner}\n{pad}</{self.tag}>"

    def outer_html(self, indent: int = 0) -> str:
        return self.outer_html(indent, [])


class FlyweightFactory:
    _pool: dict = {}

    @classmethod
    def get(cls, tag: str, classes: list[str] = None) -> LightElementNodeFlyweight:
        key = (tag, tuple(classes or []))
        if key not in cls._pool:
            cls._pool[key] = LightElementNodeFlyweight(tag, classes)
        return cls._pool[key]

    @classmethod
    def pool_size(cls) -> int:
        return len(cls._pool)


class FlyweightElementNode(LightNode):
    def __init__(self, tag: str, classes: list[str] = None):
        self._flyweight = FlyweightFactory.get(tag, classes)
        self.children: list[LightNode] = []

    def add(self, node: LightNode) -> "FlyweightElementNode":
        self.children.append(node)
        return self

    def outer_html(self, indent: int = 0) -> str:
        pad = "  " * indent
        attrs = f' class="{" ".join(self._flyweight.classes)}"' if self._flyweight.classes else ""
        inner = "\n".join(child.outer_html(indent + 1) for child in self.children)
        return f"{pad}<{self._flyweight.tag}{attrs}>\n{inner}\n{pad}</{self._flyweight.tag}>"


def fetch_book(url: str) -> list[str]:
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8").splitlines()


def build_tree(lines: list[str], use_flyweight: bool = False):
    Element = FlyweightElementNode if use_flyweight else LightElementNode
    root = Element("div")

    for i, line in enumerate(lines):
        if i == 0:
            el = Element("h1")
        elif len(line) < 20:
            el = Element("h2")
        elif line.startswith(" "):
            el = Element("p", ["indent"])
        else:
            el = Element("p")

        el.add(LightTextNode(line))
        root.add(el)

    return root


def get_size(obj) -> int:
    visited = set()

    def inner(o):
        if id(o) in visited:
            return 0
        visited.add(id(o))
        size = sys.getsizeof(o)
        if hasattr(o, "__dict__"):
            size += inner(o.__dict__)
        if isinstance(o, dict):
            size += sum(inner(k) + inner(v) for k, v in o.items())
        if isinstance(o, (list, tuple, set)):
            size += sum(inner(i) for i in o)
        return size

    return inner(obj)


def main():
    URL = "https://www.gutenberg.org/cache/epub/1513/pg1513.txt"
    print("Завантаження книги")
    lines = fetch_book(URL)
    print(f"Рядків: {len(lines)}\n")

    print("Дерево БЕЗ легковаговика")
    tree_normal = build_tree(lines, use_flyweight=False)
    size_normal = get_size(tree_normal)
    print(f"Розмір у памʼяті: {size_normal / 1024 / 1024:.2f} MB")

    print("\nДерево З легковаговиком")
    tree_flyweight = build_tree(lines, use_flyweight=True)
    size_flyweight = get_size(tree_flyweight)
    print(f"Розмір у памʼяті: {size_flyweight / 1024 / 1024:.2f} MB")
    print(f"Унікальних flyweight обʼєктів у пулі: {FlyweightFactory.pool_size()}")

    saved = size_normal - size_flyweight
    print(f"\nЕкономія: {saved / 1024 / 1024:.2f} MB "
          f"({saved / size_normal * 100:.1f}%)")

    print("\nПерші 5 елементів")
    for child in tree_flyweight.children[:5]:
        print(child.outer_html())


if __name__ == "__main__":
    main()