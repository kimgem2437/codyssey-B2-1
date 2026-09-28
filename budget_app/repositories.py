import json
from dataclasses import asdict
from pathlib import Path
from typing import Generator

from .models import Transaction


class TransactionRepository:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "transactions.jsonl"

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file_path.touch(
            exist_ok=True
        )

    def add(self, transaction: Transaction) -> None:
        with self.file_path.open(
            "a",
            encoding="utf-8"
        ) as file:
            json_line = json.dumps(
                asdict(transaction),
                ensure_ascii=False
            )

            file.write(json_line + "\n")

    def get_all(self) -> Generator[Transaction, None, None]:
        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                yield Transaction(**data)

    def get_by_id(
        self,
        transaction_id: str
    ) -> Transaction | None:
        for transaction in self.get_all():
            if transaction.id == transaction_id:
                return transaction

        return None

    def update(
        self,
        updated_transaction: Transaction
    ) -> bool:
        temp_path = self.data_dir / "transactions.tmp"

        found = False

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as source:
            with temp_path.open(
                "w",
                encoding="utf-8"
            ) as target:

                for line in source:
                    line = line.strip()

                    if not line:
                        continue

                    data = json.loads(line)

                    if data["id"] == updated_transaction.id:
                        data = asdict(
                            updated_transaction
                        )

                        found = True

                    target.write(
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ) + "\n"
                    )

        temp_path.replace(
            self.file_path
        )

        return found

    def delete(
        self,
        transaction_id: str
    ) -> bool:
        temp_path = self.data_dir / "transactions.tmp"

        found = False

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as source:
            with temp_path.open(
                "w",
                encoding="utf-8"
            ) as target:

                for line in source:
                    line = line.strip()

                    if not line:
                        continue

                    data = json.loads(line)

                    if data["id"] == transaction_id:
                        found = True
                        continue

                    target.write(
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ) + "\n"
                    )

        temp_path.replace(
            self.file_path
        )

        return found


class CategoryRepository:
    DEFAULT_CATEGORIES = [
        "food",
        "transport",
        "rent",
        "salary",
        "shopping",
        "etc"
    ]

    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "categories.jsonl"

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file_path.touch(
            exist_ok=True
        )

        if self.file_path.stat().st_size == 0:
            self._create_default_categories()

    def _create_default_categories(self) -> None:
        for category in self.DEFAULT_CATEGORIES:
            self.add(category)

    def add(self, category: str) -> None:
        with self.file_path.open(
            "a",
            encoding="utf-8"
        ) as file:
            data = {
                "name": category
            }

            json_line = json.dumps(
                data,
                ensure_ascii=False
            )

            file.write(json_line + "\n")

    def get_all(self) -> Generator[str, None, None]:
        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                yield data["name"]

    def exists(self, category: str) -> bool:
        for saved_category in self.get_all():
            if saved_category == category:
                return True

        return False

    def remove(self, category: str) -> None:
        temp_path = self.data_dir / "categories.tmp"

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as source:
            with temp_path.open(
                "w",
                encoding="utf-8"
            ) as target:

                for line in source:
                    line = line.strip()

                    if not line:
                        continue

                    data = json.loads(line)

                    if data["name"] == category:
                        continue

                    target.write(
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ) + "\n"
                    )

        temp_path.replace(
            self.file_path
        )


class BudgetRepository:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "budgets.jsonl"

        self.data_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.file_path.touch(
            exist_ok=True
        )

    def get(self, month: str) -> int | None:
        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                if data["month"] == month:
                    return data["amount"]

        return None

    def set(
        self,
        month: str,
        amount: int
    ) -> None:
        temp_path = self.data_dir / "budgets.tmp"

        found = False

        with self.file_path.open(
            "r",
            encoding="utf-8"
        ) as source:
            with temp_path.open(
                "w",
                encoding="utf-8"
            ) as target:

                for line in source:
                    line = line.strip()

                    if not line:
                        continue

                    data = json.loads(line)

                    if data["month"] == month:
                        data["amount"] = amount
                        found = True

                    target.write(
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ) + "\n"
                    )

                if not found:
                    data = {
                        "month": month,
                        "amount": amount
                    }

                    target.write(
                        json.dumps(
                            data,
                            ensure_ascii=False
                        ) + "\n"
                    )

        temp_path.replace(
            self.file_path
        )