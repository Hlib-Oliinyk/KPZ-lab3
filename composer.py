from abc import ABC, abstractmethod


class LightNode(ABC):
    @abstractmethod
    def outer_html(self, indent: int = 0) -> str:
        pass


class LightTextNode(LightNode):
    def __init__(self, text: str):
        self.text = text

    def outer_html(self, indent: int = 0) -> str:
        return "  " * indent + self.text


class LightElementNode(LightNode):
    BLOCK  = "block"
    INLINE = "inline"
    SELF_CLOSING = "self-closing"
    WITH_CLOSING = "with-closing"

    def __init__(self, tag: str, display: str = BLOCK, closing: str = WITH_CLOSING, classes: list[str] = None):
        self.tag = tag
        self.display = display
        self.closing = closing
        self.classes = classes or []
        self.children: list[LightNode] = []

    def add(self, node: LightNode) -> "LightElementNode":
        self.children.append(node)
        return self

    def child_count(self) -> int:
        return len(self.children)

    def _attrs(self) -> str:
        cls = f' class="{" ".join(self.classes)}"' if self.classes else ""
        return cls

    def inner_html(self, indent: int = 0) -> str:
        return "\n".join(child.outer_html(indent) for child in self.children)

    def outer_html(self, indent: int = 0) -> str:
        pad = "  " * indent
        attrs = self._attrs()

        if self.closing == self.SELF_CLOSING:
            return f"{pad}<{self.tag}{attrs} />"

        inner = self.inner_html(indent + 1)
        return f"{pad}<{self.tag}{attrs}>\n{inner}\n{pad}</{self.tag}>"


def main():
    ul = LightElementNode("ul", classes=["menu"])
    ul.add(LightElementNode("li").add(LightTextNode("Головна")))
    ul.add(LightElementNode("li").add(LightTextNode("Про нас")))
    ul.add(LightElementNode("li").add(LightTextNode("Контакти")))

    print("Список")
    print(ul.outer_html())
    print(f"Дочірніх елементів: {ul.child_count()}\n")

    thead = LightElementNode("thead").add(
        LightElementNode("tr")
            .add(LightElementNode("th").add(LightTextNode("Імʼя")))
            .add(LightElementNode("th").add(LightTextNode("Вік")))
            .add(LightElementNode("th").add(LightTextNode("Місто")))
    )

    tbody = LightElementNode("tbody")
    for name, age, city in [("Олег", "25", "Київ"), ("Марія", "30", "Львів")]:
        tbody.add(
            LightElementNode("tr")
                .add(LightElementNode("td").add(LightTextNode(name)))
                .add(LightElementNode("td").add(LightTextNode(age)))
                .add(LightElementNode("td").add(LightTextNode(city)))
        )

    table = LightElementNode("table", classes=["table"]).add(thead).add(tbody)

    print("Таблиця")
    print(table.outer_html())
    print(f"Дочірніх елементів: {table.child_count()}\n")

    img = LightElementNode("img", display=LightElementNode.INLINE,
                           closing=LightElementNode.SELF_CLOSING, classes=["avatar"])
    print("Self-closing тег")
    print(img.outer_html())


if __name__ == "__main__":
    main()