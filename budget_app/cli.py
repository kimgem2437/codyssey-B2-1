import argparse

from .repositories import (
    BudgetRepository,
    CategoryRepository,
    TransactionRepository,
)
from .services import BudgetService


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="budget_app",
        description="나만의 용돈 기입장 프로그램"
    )

    parser.add_argument(
        "--data-dir",
        default="data",
        help="데이터 저장 폴더 (기본값: data)"
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    subparsers.add_parser(
        "add",
        help="새로운 거래를 추가합니다."
    )

    list_parser = subparsers.add_parser(
        "list",
        help="거래 목록을 조회합니다."
    )

    list_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="출력할 거래 개수"
    )

    search_parser = subparsers.add_parser(
        "search",
        help="거래를 검색합니다."
    )

    search_parser.add_argument(
        "--from",
        dest="from_date",
        help="시작 날짜 YYYY-MM-DD"
    )

    search_parser.add_argument(
        "--to",
        dest="to_date",
        help="종료 날짜 YYYY-MM-DD"
    )

    search_parser.add_argument(
        "--category",
        help="카테고리"
    )

    search_parser.add_argument(
        "--type",
        dest="transaction_type",
        help="income 또는 expense"
    )

    search_parser.add_argument(
        "--q",
        dest="query",
        help="메모 검색어"
    )

    search_parser.add_argument(
        "--tag",
        help="태그"
    )

    summary_parser = subparsers.add_parser(
        "summary",
        help="월별 거래 요약을 출력합니다."
    )

    summary_parser.add_argument(
        "--month",
        required=True,
        help="조회할 월 YYYY-MM"
    )

    summary_parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="지출 카테고리 상위 개수"
    )

    update_parser = subparsers.add_parser(
        "update",
        help="거래를 수정합니다."
    )

    update_parser.add_argument(
        "--id",
        required=True,
        help="수정할 거래 ID"
    )

    delete_parser = subparsers.add_parser(
        "delete",
        help="거래를 삭제합니다."
    )

    delete_parser.add_argument(
        "--id",
        required=True,
        help="삭제할 거래 ID"
    )

    import_parser = subparsers.add_parser(
        "import",
        help="CSV 파일에서 거래를 가져옵니다."
    )

    import_parser.add_argument(
        "--file",
        required=True,
        help="가져올 CSV 파일 경로"
    )

    export_parser = subparsers.add_parser(
        "export",
        help="거래를 CSV 파일로 내보냅니다."
    )

    export_parser.add_argument(
        "--file",
        required=True,
        help="저장할 CSV 파일 경로"
    )

    export_parser.add_argument(
        "--month",
        help="내보낼 월 YYYY-MM"
    )

    export_parser.add_argument(
        "--from",
        dest="from_date",
        help="시작 날짜 YYYY-MM-DD"
    )

    export_parser.add_argument(
        "--to",
        dest="to_date",
        help="종료 날짜 YYYY-MM-DD"
    )

    budget_parser = subparsers.add_parser(
        "budget",
        help="월 예산을 관리합니다."
    )

    budget_subparsers = budget_parser.add_subparsers(
        dest="budget_command"
    )

    budget_set_parser = budget_subparsers.add_parser(
        "set",
        help="월 예산을 설정합니다."
    )

    budget_set_parser.add_argument(
        "--month",
        required=True,
        help="예산을 설정할 월 YYYY-MM"
    )

    budget_set_parser.add_argument(
        "--amount",
        type=int,
        required=True,
        help="예산 금액"
    )

    category_parser = subparsers.add_parser(
        "category",
        help="카테고리를 관리합니다."
    )

    category_subparsers = category_parser.add_subparsers(
        dest="category_command"
    )

    category_subparsers.add_parser(
        "list",
        help="카테고리 목록을 조회합니다."
    )

    category_add_parser = category_subparsers.add_parser(
        "add",
        help="카테고리를 추가합니다."
    )

    category_add_parser.add_argument(
        "--name",
        required=True,
        help="추가할 카테고리 이름"
    )

    category_remove_parser = category_subparsers.add_parser(
        "remove",
        help="카테고리를 삭제합니다."
    )

    category_remove_parser.add_argument(
        "--name",
        required=True,
        help="삭제할 카테고리 이름"
    )

    return parser


def handle_add(service: BudgetService) -> None:
    print("새로운 거래를 추가합니다.")

    date = input(
        "날짜(YYYY-MM-DD): "
    ).strip()

    transaction_type = input(
        "타입(income/expense): "
    ).strip()

    category = input(
        "카테고리: "
    ).strip()

    amount_input = input(
        "금액(양수): "
    ).strip()

    memo = input(
        "메모(선택): "
    ).strip()

    tags_input = input(
        "태그(쉼표로 구분, 없으면 엔터): "
    ).strip()

    amount = int(amount_input)

    tags = []

    if tags_input:
        tags = [
            tag.strip()
            for tag in tags_input.split(",")
            if tag.strip()
        ]

    transaction = service.create_transaction(
        transaction_type=transaction_type,
        date=date,
        amount=amount,
        category=category,
        memo=memo,
        tags=tags
    )

    print(
        f"[저장 완료] id={transaction.id}"
    )


def print_transaction(transaction) -> None:
    print(
        f"{transaction.id} | "
        f"{transaction.date} | "
        f"{transaction.type} | "
        f"{transaction.category} | "
        f"{transaction.amount}원 | "
        f"{transaction.memo}"
    )


def handle_list(
    service: BudgetService,
    limit: int
) -> None:
    transactions = service.list_transactions(
        limit
    )

    if not transactions:
        print("저장된 거래가 없습니다.")
        return

    for transaction in transactions:
        print_transaction(transaction)


def handle_search(
    service: BudgetService,
    args: argparse.Namespace
) -> None:
    transactions = service.search_transactions(
        from_date=args.from_date,
        to_date=args.to_date,
        category=args.category,
        transaction_type=args.transaction_type,
        query=args.query,
        tag=args.tag
    )

    if not transactions:
        print("검색 결과가 없습니다.")
        return

    for transaction in transactions:
        print_transaction(transaction)


def handle_update(
    service: BudgetService,
    transaction_id: str
) -> None:
    current = service.get_transaction(
        transaction_id
    )

    print("[현재 거래]")
    print_transaction(current)

    print()
    print("변경하지 않을 값은 Enter를 누르세요.")

    date_input = input(
        f"날짜 [{current.date}]: "
    ).strip()

    type_input = input(
        f"타입 [{current.type}]: "
    ).strip()

    category_input = input(
        f"카테고리 [{current.category}]: "
    ).strip()

    amount_input = input(
        f"금액 [{current.amount}]: "
    ).strip()

    memo_input = input(
        f"메모 [{current.memo}]: "
    ).strip()

    current_tags = ", ".join(
        current.tags
    )

    tags_input = input(
        f"태그 [{current_tags}]: "
    ).strip()

    date = (
        date_input
        if date_input
        else current.date
    )

    transaction_type = (
        type_input
        if type_input
        else current.type
    )

    category = (
        category_input
        if category_input
        else current.category
    )

    amount = (
        int(amount_input)
        if amount_input
        else current.amount
    )

    memo = (
        memo_input
        if memo_input
        else current.memo
    )

    if tags_input:
        tags = [
            tag.strip()
            for tag in tags_input.split(",")
            if tag.strip()
        ]
    else:
        tags = current.tags

    updated = service.update_transaction(
        transaction_id=transaction_id,
        transaction_type=transaction_type,
        date=date,
        amount=amount,
        category=category,
        memo=memo,
        tags=tags
    )

    print(
        f"[수정 완료] id={updated.id}"
    )


def handle_delete(
    service: BudgetService,
    transaction_id: str
) -> None:
    service.delete_transaction(
        transaction_id
    )

    print(
        f"[삭제 완료] id={transaction_id}"
    )


def handle_import(
    service: BudgetService,
    file_path: str
) -> None:
    result = service.import_csv(
        file_path
    )

    print(
        "[가져오기 완료] "
        f"성공={result['success']}건, "
        f"실패={result['failed']}건"
    )


def handle_export(
    service: BudgetService,
    args: argparse.Namespace
) -> None:
    count = service.export_csv(
        csv_path=args.file,
        month=args.month,
        from_date=args.from_date,
        to_date=args.to_date
    )

    print(
        f"[내보내기 완료] {count}건 "
        f"→ {args.file}"
    )


def handle_summary(
    service: BudgetService,
    month: str,
    top: int
) -> None:
    summary = service.get_monthly_summary(
        month,
        top
    )

    if summary["count"] == 0:
        print(
            f"{month}에는 거래 내역이 없습니다."
        )

    else:
        print(f"[{month} 월별 요약]")

        print(
            f"총 수입: {summary['income']}원"
        )

        print(
            f"총 지출: {summary['expense']}원"
        )

        print(
            f"잔액: {summary['balance']}원"
        )

        print()
        print("[지출 카테고리 TOP]")

        if not summary["top_categories"]:
            print("지출 내역이 없습니다.")

        else:
            for index, (
                category,
                amount
            ) in enumerate(
                summary["top_categories"],
                start=1
            ):
                print(
                    f"{index}. "
                    f"{category}: "
                    f"{amount}원"
                )

    if summary["budget"] is not None:
        print()

        print(
            f"월 예산: {summary['budget']}원"
        )

        print(
            "예산 사용률: "
            f"{summary['budget_usage']:.1f}%"
        )

        if summary["over_budget"]:
            print(
                "[경고] 월 예산을 초과했습니다."
            )


def handle_budget_set(
    service: BudgetService,
    month: str,
    amount: int
) -> None:
    service.set_budget(
        month,
        amount
    )

    print(
        f"{month} 예산이 "
        f"{amount}원으로 설정되었습니다."
    )


def handle_category_list(
    service: BudgetService
) -> None:
    categories = service.list_categories()

    if not categories:
        print("등록된 카테고리가 없습니다.")
        return

    print("[카테고리 목록]")

    for category in categories:
        print(f"- {category}")


def handle_category_add(
    service: BudgetService,
    name: str
) -> None:
    service.add_category(name)

    print(
        f"카테고리가 추가되었습니다: {name}"
    )


def handle_category_remove(
    service: BudgetService,
    name: str
) -> None:
    service.remove_category(name)

    print(
        f"카테고리가 삭제되었습니다: {name}"
    )


def main() -> None:
    parser = create_parser()

    args = parser.parse_args()

    transaction_repository = TransactionRepository(
        args.data_dir
    )

    category_repository = CategoryRepository(
        args.data_dir
    )

    budget_repository = BudgetRepository(
        args.data_dir
    )

    service = BudgetService(
        transaction_repository,
        category_repository,
        budget_repository
    )

    if args.command == "add":
        handle_add(service)

    elif args.command == "list":
        handle_list(
            service,
            args.limit
        )

    elif args.command == "search":
        handle_search(
            service,
            args
        )

    elif args.command == "update":
        handle_update(
            service,
            args.id
        )

    elif args.command == "delete":
        handle_delete(
            service,
            args.id
        )

    elif args.command == "import":
        handle_import(
            service,
            args.file
        )

    elif args.command == "export":
        handle_export(
            service,
            args
        )

    elif args.command == "summary":
        handle_summary(
            service,
            args.month,
            args.top
        )

    elif (
        args.command == "budget"
        and args.budget_command == "set"
    ):
        handle_budget_set(
            service,
            args.month,
            args.amount
        )

    elif (
        args.command == "category"
        and args.category_command == "list"
    ):
        handle_category_list(service)

    elif (
        args.command == "category"
        and args.category_command == "add"
    ):
        handle_category_add(
            service,
            args.name
        )

    elif (
        args.command == "category"
        and args.category_command == "remove"
    ):
        handle_category_remove(
            service,
            args.name
        )

    else:
        parser.print_help()