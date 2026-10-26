"""Test optional preview password without real credentials or network calls."""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def main():
    with tempfile.TemporaryDirectory(prefix="redpad-private-preview-") as temp:
        workspace = Path(temp)
        for name in ("streamlit_app.py", "redpad_video_studio.py"):
            shutil.copy2(ROOT / name, workspace / name)
        for name in ("redpad_pipeline", "assets"):
            shutil.copytree(ROOT / name, workspace / name)

        env = {"REDPAD_REQUIRE_PREVIEW_LOGIN": "true",
               "REDPAD_DASHBOARD_PASSWORD": "FAKE-TEST-PASSWORD-NOT-A-SECRET",
               "REDPAD_ENABLE_PAID_GENERATION": "false"}
        with patch.dict(os.environ, env):
            at = AppTest.from_file(str(workspace / "streamlit_app.py"), default_timeout=45).run()
            assert not at.exception, [x.message for x in at.exception]
            assert not at.tabs, "Private preview exposed dashboard before authentication"
            form_input = next((x for x in at.text_input
                               if x.label == "Preview password"), None)
            assert form_input is not None, "Private preview has no password field"

            form_input.set_value("wrong-password")
            next(b for b in at.button if b.label == "Open dashboard").click().run()
            assert not at.tabs, "Incorrect password unlocked preview"
            assert any("Incorrect" in x.message for x in at.error), "Missing login error"

            next(x for x in at.text_input if x.label == "Preview password"
                 ).set_value(env["REDPAD_DASHBOARD_PASSWORD"])
            next(b for b in at.button if b.label == "Open dashboard").click().run()
            assert not at.exception, [x.message for x in at.exception]
            assert any("Video Studio" in x.label for x in at.tabs), (
                "Correct password did not unlock Video Studio")
            print("PASS: private Render preview requires password; valid password unlocks dashboard")

        with patch.dict(os.environ, {"REDPAD_REQUIRE_PREVIEW_LOGIN": "true",
                                    "REDPAD_DASHBOARD_PASSWORD": ""}):
            other = AppTest.from_file(str(workspace / "streamlit_app.py"),
                                      default_timeout=45).run()
            assert not other.tabs, "Preview unexpectedly opened without a password"
            assert any("locked" in x.message for x in other.error)
            print("PASS: missing server password fails closed")


if __name__ == "__main__":
    main()
