"""
fasta_toolkit.py — работа с FASTA-файлами.

Класс Seq          — одна последовательность с заголовком.
Класс FastaReader  — потоковое чтение FASTA-файлов.

"""

import os
from typing import Iterator # нужен для аннотации read_records


# IUPAC-наборы символов, по которым определяем алфавит последовательности.
# set("ABC") превращает строку в множество {'A', 'B', 'C'} 
NUCLEOTIDES = set("ACGTUNRYKMSWBDHV-")          # ДНК/РНК + неоднозначные + gap
PROTEINS = set("ACDEFGHIKLMNPQRSTVWYBXZJUO*-")  # 20 аминокислот + редкие + стоп + gap


class Seq:
    """Одна последовательность вместе с её заголовком FASTA.
    Attributes:
        header: Заголовок FASTA без ведущего ``>``.
        sequence: Нормализованная последовательность (верхний регистр,
            без пробелов и переводов строк).
    """

    def __init__(self, header: str, sequence: str) -> None:
        """Создаёт объект последовательности.
        Args:
            header: Заголовок FASTA без ведущего ``>``.
            sequence: Строка с последовательностью.

        Raises:
            ValueError: Если заголовок или последовательность пусты
                после нормализации.
        """
        #   strip() убирает пробелы по краям,
        #   убираем пробелы и переводы строк внутри последовательности,
        #   приводим к верхнему регистру.
        header = header.strip()
        sequence = sequence.replace(" ", "").replace("\n", "").upper()

        # пустые значения недопустимы.
        if not header:
            raise ValueError("Заголовок не может быть пустым")
        if not sequence:
            raise ValueError("Последовательность не может быть пустой")

        self.header = header
        self.sequence = sequence

        # Разбираем заголовок на id и описание.
        # split(" ", 1) режет по ПЕРВОМУ пробелу, максимум на 2 части,
        # чтобы описание осталось одним куском.
        parts = header.split(" ", 1)
        self.id = parts[0]
        self.description = parts[1]


    def __len__(self) -> int:
        """Позволяет писать len(seq)."""
        return len(self.sequence)
 

    def alphabet(self) -> str:
        """Определяет алфавит: 'nucleotide'или 'protein'.

        Собираем множество уникальных символов и проверяем,
        является ли оно подмножеством одного из наборов.
        Нуклеотиды проверяем первыми: буквы A, C, G, T входят
        и в нуклеотидный, и в белковый набор.
        """
        chars = set(self.sequence)
        if chars <= NUCLEOTIDES:
            return "nucleotide"
        if chars <= PROTEINS:
            return "protein"
        return "unknown"
        

    def _wrap(self, width: int =60) -> str:
        """Разбивает последовательность на строки по width символов.

        В FASTA длинные последовательности принято выводить строками
        по 60 (или 70, 80) символов. Внутренний метод — отсюда "_".
        Args:
            width: Ширина одной строки в символах.

        Returns:
            Последовательность, разбитая на строки через ``\\n``.
        """
        parts = []
        for i in range(0, len(self.sequence), width):
            parts.append(self.sequence[i:i + width])
        return "\n".join(parts)

    def __str__(self) -> str:
        """Красивый вывод в формате FASTA."""
        return f">{self.header}\n{self._wrap()}"

    def __repr__(self):
        """Короткое представление для отладки."""
        return f"Seq(id={self.id!r}, length={len(self)})"



class FastaReader:
    """Читает FASTA-файл и выдаёт Seq по одной записи.
    Attributes:
        path: Путь к FASTA-файлу.
    """

    def __init__(self, path: str) -> None:
        """Создаёт читатель для указанного файла.

        Args:
            path: Путь к FASTA-файлу.

        Raises:
            FileNotFoundError: Если файла по указанному пути нет.
            IsADirectoryError: Если путь указывает на каталог.
        """
        # os.path.exists() возвращает True и для файлов, и для каталогов.
        self.path = path 
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Файл не найден: {self.path}")

        # Проверяем, что это именно файл, а не каталог.
        if os.path.isdir(self.path):
            raise IsADirectoryError(f"Это каталог, а не файл: {self.path}")

    def is_valid(self) -> bool:
        """Проверяет, что файл похож на FASTA.

        Returns:
        ``True``, если файл похож на FASTA, иначе ``False``.
        """
        with open(self.path, "r", encoding="utf-8") as f:
        # Ищем первый заголовок, пропуская пустые строки.
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if not line.startswith(">") or len(line) < 2:
                    return False

                # Заголовок найден — дальше проверяем, есть ли буквы.
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(">"):
                        return False   # заголовок без последовательности
                    return True        # нашли первую букву — файл валиден

                # Если внутренний цикл ничего не нашёл (файл кончился сразу
                # после заголовка) — файл невалиден.
                return False

  
     
    def read_records(self) -> Iterator[Seq]:
        """Генератор: выдаёт Seq по одной записи.

        Файл не загружается в память целиком — в любой момент времени
        в памяти находится только текущая запись. Работает с FASTA
        любого размера.
        Yields:
            Экземпляры class `Seq` в порядке следования в файле.

        Raises:
            ValueError: Если файл не является FASTA.
        """
    
        if not self.is_valid():
            raise ValueError(f"Файл не является FASTA: {self.path}")

        header = None    # заголовок текущей записи
        # chunks — список кусков последовательности.
        chunks = []

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.startswith(">"):
                    # Новый заголовок — предыдущая запись закончилась.
                    # yield отдаёт предыдущую запись наружу.
                    if header is not None:
                        yield Seq(header, "".join(chunks))

                    header = line[1:]    # отрезаем ведущий '>'
                    chunks = []          # начинаем собирать новую последовательность
                else:
                    chunks.append(line)

        # После конца файла последняя запись ещё не выдана —
        # мы выдаём запись только при встрече СЛЕДУЮЩЕГО заголовка.
        if header is not None:
            yield Seq(header, "".join(chunks))

    


