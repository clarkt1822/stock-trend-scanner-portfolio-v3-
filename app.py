from __future__ import annotations


def main() -> int:
    print(
        "The desktop PySide6 UI has been isolated.\n"
        "Run `python -m uvicorn api.main:app --reload` for the backend, `cd web && npm run dev` for the frontend,\n"
        "or `python legacy/desktop_app.py` for the legacy desktop app."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
