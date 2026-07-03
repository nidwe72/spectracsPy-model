import os


def get_app_data_dir() -> str:
    """Absolute directory for app-private data (SQLite DBs, cached images).

    Android (python-for-android): use ``ANDROID_PRIVATE`` — the app's internal files directory
    (``Context.getFilesDir``), which p4a sets in the environment before Python starts. It resolves
    at import time with no QApplication dependency, and the desktop-only ``appdata`` package is not
    shipped in the APK. Each APK has its own sandbox, so the two apps get isolated data dirs
    automatically.

    Desktop: keep the existing ``appdata`` location unchanged so existing local databases keep
    working — no migration needed. See docs/SPEC_android_port.md decision D7.
    """
    android_private = os.environ.get("ANDROID_PRIVATE")
    if android_private:
        os.makedirs(android_private, exist_ok=True)
        return android_private

    from appdata import AppDataPaths
    app_paths = AppDataPaths()
    app_paths.setup()
    return app_paths.app_data_path
