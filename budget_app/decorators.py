from collections.abc import Callable
from functools import wraps


def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as error:
            print(f"[오류] {error}")
            print("[힌트] 입력값이나 명령어를 확인해주세요.")

            raise SystemExit(1)

        except KeyboardInterrupt:
            print()
            print("[오류] 사용자가 프로그램을 중단했습니다.")

            raise SystemExit(130)

        except Exception as error:
            print(f"[오류] 예상하지 못한 문제가 발생했습니다: {error}")
            print("[힌트] 명령어와 데이터 파일을 확인해주세요.")

            raise SystemExit(1)

    return wrapper