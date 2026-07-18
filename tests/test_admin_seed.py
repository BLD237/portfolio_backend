import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.security import verify_password
from app.core.config import BACKEND_DIR, Settings
from app.db.session import Base
from app.models.admin import AdminUser
from app.seed import seed_admin_user


class AdminSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        self.engine = create_engine(f"sqlite:///{database_path}")
        Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)()

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()
        self.temp_dir.cleanup()

    def test_creates_admin_and_synchronizes_configured_credentials(self) -> None:
        initial = SimpleNamespace(
            admin_email=" Admin@Belmond.dev ",
            admin_password="InitialPassword123!",
        )
        with patch("app.seed.get_settings", return_value=initial):
            admin = seed_admin_user(self.session)

        self.assertEqual(admin.email, "admin@belmond.dev")
        self.assertTrue(verify_password(initial.admin_password, admin.hashed_password))
        self.assertEqual(self.session.query(AdminUser).count(), 1)

        updated = SimpleNamespace(
            admin_email="admin@belmond.dev",
            admin_password="UpdatedPassword456!",
        )
        with patch("app.seed.get_settings", return_value=updated):
            admin = seed_admin_user(self.session)

        self.assertEqual(self.session.query(AdminUser).count(), 1)
        self.assertTrue(verify_password(updated.admin_password, admin.hashed_password))
        self.assertTrue(admin.is_active)

    def test_relative_database_url_is_anchored_to_backend_directory(self) -> None:
        settings = Settings(_env_file=None, database_url="sqlite:///./data/test.db")

        self.assertEqual(
            settings.database_url,
            f"sqlite:///{(BACKEND_DIR / 'data/test.db').resolve()}",
        )


if __name__ == "__main__":
    unittest.main()
