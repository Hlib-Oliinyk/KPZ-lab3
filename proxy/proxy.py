import re
from abc import ABC, abstractmethod


class ITextReader(ABC):
    @abstractmethod
    def read(self, filename: str) -> list[list[str]]: pass


class SmartTextReader(ITextReader):
    def read(self, filename: str) -> list[list[str]]:
        with open(filename, "r", encoding="utf-8") as f:
            return [list(line.rstrip("\n")) for line in f.readlines()]


class SmartTextChecker(ITextReader):
    def __init__(self, reader: ITextReader):
        self._reader = reader

    def read(self, filename: str) -> list[list[str]]:
        print(f"[LOG] Відкриття файлу: {filename}")
        result = self._reader.read(filename)
        print(f"[LOG] Файл успішно прочитано і закрито")
        print(f"[LOG] Рядків: {len(result)}")
        print(f"[LOG] Символів: {sum(len(row) for row in result)}")
        return result


class SmartTextReaderLocker(ITextReader):
    def __init__(self, reader: ITextReader, pattern: str):
        self._reader = reader
        self._pattern = pattern

    def read(self, filename: str) -> list[list[str]]:
        if re.search(self._pattern, filename):
            print(f"Access denied!")
            return []
        return self._reader.read(filename)


def main():
    with open("notes.txt", "w", encoding="utf-8") as f:
        f.write("Hello World\nPython is cool")

    with open("secret.txt", "w", encoding="utf-8") as f:
        f.write("top secret data")

    reader = SmartTextReader()

    print("Звичайне читання")
    result = reader.read("notes.txt")
    print(result)

    print("\nЧитання з логуванням")
    checker = SmartTextChecker(SmartTextReader())
    result = checker.read("notes.txt")

    print("\nЧитання з обмеженням доступу")
    locker = SmartTextReaderLocker(SmartTextReader(), r"secret")
    locker.read("notes.txt")
    locker.read("secret.txt")

    print("\nЛогування + обмеження доступу")
    combined = SmartTextChecker(SmartTextReaderLocker(SmartTextReader(), r"secret"))
    combined.read("notes.txt")
    print()
    combined.read("secret.txt")


if __name__ == "__main__":
    main()