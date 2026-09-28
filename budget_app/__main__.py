from .cli import main
from .decorators import handle_errors


@handle_errors
def run() -> None:
    main()


if __name__ == "__main__":
    run()