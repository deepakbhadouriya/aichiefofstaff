from libs.db.settings import get_settings


def main() -> None:
    settings = get_settings()
    print(f"worker started for environment={settings.environment}")
    print("no queue consumer wired yet; this is the orchestration worker placeholder")


if __name__ == "__main__":
    main()

