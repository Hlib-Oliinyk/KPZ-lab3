from abc import ABC, abstractmethod
from collections import deque


class LightNode(ABC):
    @abstractmethod
    def outer_html(self, indent: int = 0) -> str:
        pass


class LightTextNode(LightNode):
    def __init__(self, text: str):
        self.text = text

    def outer_html(self, indent: int = 0) -> str:
        return "  " * indent + self.text


class RenderState(ABC):
    @abstractmethod
    def render(self, element: "LightElementNode", indent: int) -> str:
        pass


class NormalState(RenderState):
    def render(self, element: "LightElementNode", indent: int) -> str:
        pad = "  " * indent
        attrs = element._attrs()

        if element.closing == LightElementNode.SELF_CLOSING:
            return f"{pad}<{element.tag}{attrs} />"

        inner = element.inner_html(indent + 1)
        return f"{pad}<{element.tag}{attrs}>\n{inner}\n{pad}</{element.tag}>"


class HiddenState(RenderState):
    def render(self, element: "LightElementNode", indent: int) -> str:
        pad = "  " * indent
        attrs = element._attrs()

        if element.closing == LightElementNode.SELF_CLOSING:
            return f'{pad}<{element.tag}{attrs} style="display:none" />'

        inner = element.inner_html(indent + 1)
        return f'{pad}<{element.tag}{attrs} style="display:none">\n{inner}\n{pad}</{element.tag}>'


class DisabledState(RenderState):
    def render(self, element: "LightElementNode", indent: int) -> str:
        pad = "  " * indent
        attrs = element._attrs()

        if element.closing == LightElementNode.SELF_CLOSING:
            return f"{pad}<{element.tag}{attrs} disabled />"

        inner = element.inner_html(indent + 1)
        return f"{pad}<{element.tag}{attrs} disabled>\n{inner}\n{pad}</{element.tag}>"


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
        self._state: RenderState = NormalState()
        self._styles: dict[str, str] = {}
        self.on_created()

    def on_created(self) -> None:
        pass

    def on_inserted(self, parent: "LightElementNode") -> None:
        pass

    def on_removed(self, parent: "LightElementNode") -> None:
        pass

    def on_styles_applied(self, styles: dict[str, str]) -> None:
        pass

    def on_class_list_applied(self, classes: list[str]) -> None:
        pass

    def on_text_rendered(self, text: str) -> None:
        pass

    def on_child_added(self, child: LightNode) -> None:
        pass

    def on_rendered(self, html: str) -> None:
        pass

    def set_state(self, state: RenderState) -> None:
        self._state = state

    def set_styles(self, styles: dict[str, str]) -> "LightElementNode":
        self._styles = styles
        self.on_styles_applied(styles)
        return self

    def add(self, node: LightNode) -> "LightElementNode":
        self.children.append(node)
        self.on_child_added(node)
        if isinstance(node, LightElementNode):
            node.on_inserted(self)
        return self

    def remove(self, node: LightNode) -> "LightElementNode":
        self.children.remove(node)
        if isinstance(node, LightElementNode):
            node.on_removed(self)
        return self

    def child_count(self) -> int:
        return len(self.children)

    def _attrs(self) -> str:
        style_str = f' style="{";".join(f"{k}:{v}" for k, v in self._styles.items())}"'  if self._styles else ""
        if self.classes:
            self.on_class_list_applied(self.classes)
        cls = f' class="{" ".join(self.classes)}"' if self.classes else ""
        return cls + style_str

    def inner_html(self, indent: int = 0) -> str:
        parts = []
        for child in self.children:
            if isinstance(child, LightTextNode):
                self.on_text_rendered(child.text)
            parts.append(child.outer_html(indent))
        return "\n".join(parts)

    def outer_html(self, indent: int = 0) -> str:
        html = self._state.render(self, indent)
        self.on_rendered(html)
        return html

    def dfs_iterator(self) -> "DFSIterator":
        return DFSIterator(self)

    def bfs_iterator(self) -> "BFSIterator":
        return BFSIterator(self)


class NodeIterator(ABC):
    @abstractmethod
    def has_next(self) -> bool:
        pass

    @abstractmethod
    def next(self) -> LightNode:
        pass


class DFSIterator(NodeIterator):
    def __init__(self, root: LightElementNode):
        self._stack: list[LightNode] = [root]

    def has_next(self) -> bool:
        return len(self._stack) > 0

    def next(self) -> LightNode:
        node = self._stack.pop()
        if isinstance(node, LightElementNode):
            for child in reversed(node.children):
                self._stack.append(child)
        return node


class BFSIterator(NodeIterator):
    def __init__(self, root: LightElementNode):
        self._queue: deque[LightNode] = deque([root])

    def has_next(self) -> bool:
        return len(self._queue) > 0

    def next(self) -> LightNode:
        node = self._queue.popleft()
        if isinstance(node, LightElementNode):
            for child in node.children:
                self._queue.append(child)
        return node


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass


class AddChildCommand(Command):
    def __init__(self, parent: LightElementNode, child: LightNode):
        self._parent = parent
        self._child = child

    def execute(self) -> None:
        self._parent.children.append(self._child)

    def undo(self) -> None:
        self._parent.children.remove(self._child)


class AddClassCommand(Command):
    def __init__(self, element: LightElementNode, cls: str):
        self._element = element
        self._cls = cls

    def execute(self) -> None:
        self._element.classes.append(self._cls)

    def undo(self) -> None:
        self._element.classes.remove(self._cls)


class CommandHistory:
    def __init__(self):
        self._history: list[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._history.append(command)

    def undo(self) -> None:
        if self._history:
            self._history.pop().undo()


class LoggedElement(LightElementNode):
    def on_created(self) -> None:
        print(f"on_created: <{self.tag}>")

    def on_inserted(self, parent: LightElementNode) -> None:
        print(f"on_inserted: <{self.tag}> -> <{parent.tag}>")

    def on_removed(self, parent: LightElementNode) -> None:
        print(f"on_removed: <{self.tag}> з <{parent.tag}>")

    def on_styles_applied(self, styles: dict[str, str]) -> None:
        print(f"on_styles_applied до <{self.tag}>: {styles}")

    def on_class_list_applied(self, classes: list[str]) -> None:
        print(f"on_class_list_applied до <{self.tag}>: {classes}")

    def on_text_rendered(self, text: str) -> None:
        print(f"on_text_rendered у <{self.tag}>: {repr(text)}")

    def on_child_added(self, child: LightNode) -> None:
        label = child.tag if isinstance(child, LightElementNode) else repr(child.text)
        print(f"on_child_added до <{self.tag}>: {label}")

    def on_rendered(self, html: str) -> None:
        lines = len(html.splitlines())
        print(f"on_rendered: <{self.tag}> ({lines} рядків)")


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
    print()

    div = LightElementNode("div")
    section = LightElementNode("section")
    p1 = LightElementNode("p").add(LightTextNode("Перший параграф"))
    p2 = LightElementNode("p").add(LightTextNode("Другий параграф"))
    span = LightElementNode("span").add(LightTextNode("Всередині секції"))
    section.add(span)
    div.add(p1)
    div.add(p2)
    div.add(section)

    print("DFS обхід:")
    dfs = div.dfs_iterator()
    while dfs.has_next():
        node = dfs.next()
        if isinstance(node, LightElementNode):
            print(f"  <{node.tag}>")
        else:
            print(f"  текст: {node.text}")

    print("\nBFS обхід:")
    bfs = div.bfs_iterator()
    while bfs.has_next():
        node = bfs.next()
        if isinstance(node, LightElementNode):
            print(f"  <{node.tag}>")
        else:
            print(f"  текст: {node.text}")

    print()

    history = CommandHistory()
    article = LightElementNode("article")
    new_child = LightElementNode("p").add(LightTextNode("Новий параграф"))

    print("Команди: стан до виконання:")
    print(article.outer_html())
    print(f"класи: {article.classes}")

    history.execute(AddChildCommand(article, new_child))
    history.execute(AddClassCommand(article, "featured"))

    print("\nПісля execute (додано дочірній елемент і клас):")
    print(article.outer_html())
    print(f"класи: {article.classes}")

    history.undo()
    print("\nПісля undo (скасовано AddClass):")
    print(article.outer_html())
    print(f"класи: {article.classes}")

    history.undo()
    print("\nПісля undo (скасовано AddChild):")
    print(article.outer_html())
    print(f"класи: {article.classes}")

    print()

    button = LightElementNode("button", classes=["btn"]).add(LightTextNode("Натисни"))

    print("Стейт NormalState:")
    print(button.outer_html())

    button.set_state(HiddenState())
    print("\nСтейт HiddenState:")
    print(button.outer_html())

    button.set_state(DisabledState())
    print("\nСтейт DisabledState:")
    print(button.outer_html())

    button.set_state(NormalState())
    print("\nСтейт повернуто до NormalState:")
    print(button.outer_html())


    print()
    print("Шаблонний метод: хуки життєвого циклу:")
    logged_div = LoggedElement("div")
    logged_p = LoggedElement("p").add(LightTextNode("Текст параграфу"))
    logged_div.add(logged_p)
    logged_div.set_styles({"color": "red", "font-size": "16px"})
    print(logged_div.outer_html())
    print()
    logged_div.remove(logged_p)


if __name__ == "__main__":
    main()