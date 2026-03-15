from abc import ABC, abstractmethod


class ILogger(ABC):
    @abstractmethod
    def log(self, message: str): pass

    @abstractmethod
    def error(self, message: str): pass

    @abstractmethod
    def warn(self, message: str): pass


class Logger(ILogger):
    def log(self, message: str):
        print(f"\033[92m[LOG]: {message}\033[0m")

    def error(self, message: str):
        print(f"\033[91m[ERROR]: {message}\033[0m")

    def warn(self, message: str):
        print(f"\033[93m[WARN]: {message}\033[0m")


class FileWriter:
    def __init__(self, filename: str):
        self.filename = filename

    def write(self, text: str):
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(text)

    def write_line(self, text: str):
        with open(self.filename, "a", encoding="utf-8") as file:
            file.write(text + "\n")


class FileLoggerAdapter(ILogger):
    def __init__(self, file_writer: FileWriter):
        self.file_writer = file_writer

    def log(self, message: str):
        self.file_writer.write_line(f"[LOG]: {message}")

    def error(self, message: str):
        self.file_writer.write_line(f"[ERROR]: {message}")

    def warn(self, message: str):
        self.file_writer.write_line(f"[WARN]: {message}")


def main():
    logger = Logger()

    logger.log("Запуск")
    logger.warn("Попередження")
    logger.error("Помилка")

    filename = "log.txt"
    writer = FileWriter(filename)
    file_logger = FileLoggerAdapter(writer)

    file_logger.log("Лог додався в файл")
    file_logger.warn("Попередження додалося в файл")
    file_logger.error("Помилка додалася в файл")


if __name__ == "__main__":
    main()