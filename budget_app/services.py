import csv
import heapq
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .models import Transaction
from .repositories import (
    BudgetRepository,
    CategoryRepository,
    TransactionRepository,
)


class BudgetService:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        category_repository: CategoryRepository,
        budget_repository: BudgetRepository
    ) -> None:
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository
        self.budget_repository = budget_repository

    def create_transaction(
        self,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
        memo: str = "",
        tags: list[str] | None = None
    ) -> Transaction:

        if not self.validate_date(date):
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. "
                "YYYY-MM-DD 형식으로 입력해주세요."
            )

        if not self.validate_type(transaction_type):
            raise ValueError(
                "타입은 income 또는 expense만 가능합니다."
            )

        if not self.validate_amount(amount):
            raise ValueError(
                "금액은 0보다 큰 정수여야 합니다."
            )

        if not self.category_repository.exists(category):
            raise ValueError(
                f"존재하지 않는 카테고리입니다: {category}"
            )

        transaction_id = self._generate_transaction_id()

        transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags or []
        )

        self.transaction_repository.add(transaction)

        return transaction

    def get_transaction(
        self,
        transaction_id: str
    ) -> Transaction:

        transaction = self.transaction_repository.get_by_id(
            transaction_id
        )

        if transaction is None:
            raise ValueError(
                f"해당 거래를 찾을 수 없습니다: {transaction_id}"
            )

        return transaction

    def update_transaction(
        self,
        transaction_id: str,
        transaction_type: str,
        date: str,
        amount: int,
        category: str,
        memo: str,
        tags: list[str]
    ) -> Transaction:

        self.get_transaction(transaction_id)

        if not self.validate_date(date):
            raise ValueError(
                "날짜 형식이 올바르지 않습니다. "
                "YYYY-MM-DD 형식으로 입력해주세요."
            )

        if not self.validate_type(transaction_type):
            raise ValueError(
                "타입은 income 또는 expense만 가능합니다."
            )

        if not self.validate_amount(amount):
            raise ValueError(
                "금액은 0보다 큰 정수여야 합니다."
            )

        if not self.category_repository.exists(category):
            raise ValueError(
                f"존재하지 않는 카테고리입니다: {category}"
            )

        updated_transaction = Transaction(
            id=transaction_id,
            type=transaction_type,
            date=date,
            amount=amount,
            category=category,
            memo=memo,
            tags=tags
        )

        self.transaction_repository.update(
            updated_transaction
        )

        return updated_transaction

    def delete_transaction(
        self,
        transaction_id: str
    ) -> None:

        self.get_transaction(transaction_id)

        deleted = self.transaction_repository.delete(
            transaction_id
        )

        if not deleted:
            raise ValueError(
                f"거래 삭제에 실패했습니다: {transaction_id}"
            )

    def list_transactions(
        self,
        limit: int = 10
    ) -> list[Transaction]:

        if limit <= 0:
            raise ValueError(
                "limit은 1 이상이어야 합니다."
            )

        return heapq.nlargest(
            limit,
            self.transaction_repository.get_all(),
            key=lambda transaction: (
                transaction.date,
                transaction.id
            )
        )

    def search_transactions(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
        category: str | None = None,
        transaction_type: str | None = None,
        query: str | None = None,
        tag: str | None = None
    ) -> list[Transaction]:

        if from_date and not self.validate_date(from_date):
            raise ValueError(
                "시작 날짜 형식은 YYYY-MM-DD여야 합니다."
            )

        if to_date and not self.validate_date(to_date):
            raise ValueError(
                "종료 날짜 형식은 YYYY-MM-DD여야 합니다."
            )

        if (
            from_date
            and to_date
            and from_date > to_date
        ):
            raise ValueError(
                "시작 날짜는 종료 날짜보다 늦을 수 없습니다."
            )

        if (
            transaction_type
            and not self.validate_type(transaction_type)
        ):
            raise ValueError(
                "타입은 income 또는 expense만 가능합니다."
            )

        results = []

        for transaction in self.transaction_repository.get_all():

            if from_date and transaction.date < from_date:
                continue

            if to_date and transaction.date > to_date:
                continue

            if category and transaction.category != category:
                continue

            if (
                transaction_type
                and transaction.type != transaction_type
            ):
                continue

            if (
                query
                and query.lower() not in transaction.memo.lower()
            ):
                continue

            if tag and tag not in transaction.tags:
                continue

            results.append(transaction)

        return sorted(
            results,
            key=lambda transaction: (
                transaction.date,
                transaction.id
            ),
            reverse=True
        )

    def import_csv(
        self,
        csv_path: str
    ) -> dict:

        path = Path(csv_path)

        if not path.exists():
            raise ValueError(
                f"CSV 파일을 찾을 수 없습니다: {csv_path}"
            )

        success_count = 0
        failed_count = 0

        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            required_fields = {
                "date",
                "type",
                "category",
                "amount"
            }

            if reader.fieldnames is None:
                raise ValueError(
                    "CSV 헤더가 없습니다."
                )

            missing_fields = (
                required_fields
                - set(reader.fieldnames)
            )

            if missing_fields:
                raise ValueError(
                    "필수 CSV 컬럼이 없습니다: "
                    + ", ".join(
                        sorted(missing_fields)
                    )
                )

            for row in reader:
                try:
                    date = (
                        row.get("date") or ""
                    ).strip()

                    transaction_type = (
                        row.get("type") or ""
                    ).strip()

                    category = (
                        row.get("category") or ""
                    ).strip()

                    amount = int(
                        (row.get("amount") or "").strip()
                    )

                    memo = (
                        row.get("memo") or ""
                    ).strip()

                    tags_input = (
                        row.get("tags") or ""
                    ).strip()

                    tags = []

                    if tags_input:
                        tags = [
                            tag.strip()
                            for tag in tags_input.split(",")
                            if tag.strip()
                        ]

                    self.create_transaction(
                        transaction_type=transaction_type,
                        date=date,
                        amount=amount,
                        category=category,
                        memo=memo,
                        tags=tags
                    )

                    success_count += 1

                except (ValueError, TypeError):
                    failed_count += 1

        return {
            "success": success_count,
            "failed": failed_count
        }

    def export_csv(
        self,
        csv_path: str,
        month: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None
    ) -> int:

        if month:
            if from_date or to_date:
                raise ValueError(
                    "--month와 --from/--to는 "
                    "동시에 사용할 수 없습니다."
                )

            if not self.validate_month(month):
                raise ValueError(
                    "월 형식은 YYYY-MM이어야 합니다."
                )

        else:
            if not from_date or not to_date:
                raise ValueError(
                    "export는 --month 또는 "
                    "--from과 --to가 필요합니다."
                )

            if not self.validate_date(from_date):
                raise ValueError(
                    "시작 날짜 형식은 YYYY-MM-DD여야 합니다."
                )

            if not self.validate_date(to_date):
                raise ValueError(
                    "종료 날짜 형식은 YYYY-MM-DD여야 합니다."
                )

            if from_date > to_date:
                raise ValueError(
                    "시작 날짜는 종료 날짜보다 "
                    "늦을 수 없습니다."
                )

        path = Path(csv_path)

        if path.parent != Path("."):
            path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

        count = 0

        with path.open(
            "w",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            fieldnames = [
                "date",
                "type",
                "category",
                "amount",
                "memo",
                "tags"
            ]

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for transaction in self.transaction_repository.get_all():

                if month:
                    if not transaction.date.startswith(month):
                        continue

                else:
                    if transaction.date < from_date:
                        continue

                    if transaction.date > to_date:
                        continue

                writer.writerow({
                    "date": transaction.date,
                    "type": transaction.type,
                    "category": transaction.category,
                    "amount": transaction.amount,
                    "memo": transaction.memo,
                    "tags": ",".join(
                        transaction.tags
                    )
                })

                count += 1

        return count

    def add_category(
        self,
        category: str
    ) -> None:

        category = category.strip()

        if not category:
            raise ValueError(
                "카테고리 이름을 입력해주세요."
            )

        if self.category_repository.exists(category):
            raise ValueError(
                f"이미 존재하는 카테고리입니다: {category}"
            )

        self.category_repository.add(category)

    def list_categories(self) -> list[str]:
        return list(
            self.category_repository.get_all()
        )

    def remove_category(
        self,
        category: str
    ) -> None:

        if not self.category_repository.exists(category):
            raise ValueError(
                f"존재하지 않는 카테고리입니다: {category}"
            )

        for transaction in self.transaction_repository.get_all():
            if transaction.category == category:
                raise ValueError(
                    "현재 거래에서 사용 중인 "
                    f"카테고리라 삭제할 수 없습니다: {category}"
                )

        self.category_repository.remove(category)

    def set_budget(
        self,
        month: str,
        amount: int
    ) -> None:

        if not self.validate_month(month):
            raise ValueError(
                "월 형식은 YYYY-MM이어야 합니다."
            )

        if amount <= 0:
            raise ValueError(
                "예산은 0보다 큰 정수여야 합니다."
            )

        self.budget_repository.set(
            month,
            amount
        )

    def get_monthly_summary(
        self,
        month: str,
        top: int = 3
    ) -> dict:

        if not self.validate_month(month):
            raise ValueError(
                "월 형식은 YYYY-MM이어야 합니다."
            )

        if top <= 0:
            raise ValueError(
                "top은 1 이상이어야 합니다."
            )

        total_income = 0
        total_expense = 0
        transaction_count = 0

        category_expenses = defaultdict(int)

        for transaction in self.transaction_repository.get_all():

            if not transaction.date.startswith(month):
                continue

            transaction_count += 1

            if transaction.type == "income":
                total_income += transaction.amount

            elif transaction.type == "expense":
                total_expense += transaction.amount

                category_expenses[
                    transaction.category
                ] += transaction.amount

        balance = total_income - total_expense

        top_categories = sorted(
            category_expenses.items(),
            key=lambda item: item[1],
            reverse=True
        )[:top]

        budget = self.budget_repository.get(month)

        budget_usage = None
        over_budget = False

        if budget is not None:
            budget_usage = (
                total_expense / budget
            ) * 100

            over_budget = (
                total_expense > budget
            )

        return {
            "month": month,
            "count": transaction_count,
            "income": total_income,
            "expense": total_expense,
            "balance": balance,
            "top_categories": top_categories,
            "budget": budget,
            "budget_usage": budget_usage,
            "over_budget": over_budget
        }

    def _generate_transaction_id(self) -> str:
        max_number = 0

        for transaction in self.transaction_repository.get_all():
            number = int(
                transaction.id.replace(
                    "TX-",
                    ""
                )
            )

            if number > max_number:
                max_number = number

        next_number = max_number + 1

        return f"TX-{next_number:06d}"

    def validate_date(self, date: str) -> bool:
        try:
            parsed = datetime.strptime(date, "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d") == date
        except ValueError:
            return False

    def validate_month(
        self,
        month: str
    ) -> bool:
        try:
            parsed_month = datetime.strptime(
                month,
                "%Y-%m"
            )

            return (
                parsed_month.strftime("%Y-%m")
                == month
            )

        except ValueError:
            return False

    def validate_type(
        self,
        transaction_type: str
    ) -> bool:
        return transaction_type in [
            "income",
            "expense"
        ]

    def validate_amount(
        self,
        amount: int
    ) -> bool:
        return amount > 0