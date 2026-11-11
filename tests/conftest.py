import os
import tempfile

# Use a throw-away database and report folder for tests. Must run before the app is imported.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_PATH"] = os.path.join(_tmp, "test.db")
os.environ["REPORTS_DIR"] = os.path.join(_tmp, "reports")
