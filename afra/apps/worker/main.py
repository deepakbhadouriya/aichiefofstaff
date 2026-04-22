from libs.db.settings import get_settings
from services.payments.orchestration import resume_incomplete_workflows


def main() -> None:
    settings = get_settings()
    print(f"worker started for environment={settings.environment}")
    resumed = resume_incomplete_workflows()
    print(f"resumed_workflows={len(resumed)}")


if __name__ == "__main__":
    main()
