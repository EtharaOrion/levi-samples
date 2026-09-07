
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Get:1 http://deb.debian.org/debian trixie InRelease [140 kB]
Get:2 http://deb.debian.org/debian trixie-updates InRelease [47.3 kB]
Get:3 http://deb.debian.org/debian-security trixie-security InRelease [43.4 kB]
Get:4 http://deb.debian.org/debian trixie/main arm64 Packages [9607 kB]
Get:5 http://deb.debian.org/debian trixie-updates/main arm64 Packages [4424 B]
Get:6 http://deb.debian.org/debian-security trixie-security/main arm64 Packages [252 kB]
Fetched 10.1 MB in 1s (10.7 MB/s)
Reading package lists...
Building dependency tree...
Reading state information...
All packages are up to date.

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Reading package lists...
Building dependency tree...
Reading state information...
patch is already the newest version (2.8-2).
patch set to manually installed.
Summary:
  Upgrading: 0, Installing: 0, Removing: 0, Not Upgrading: 0
[apply] exact: /home/test.patch
[apply] exact: /home/fix.patch
[apply] already applied (skip): /home/test.patch
[apply] already applied (skip): /home/fix.patch
============================= test session starts ==============================
collecting ... collected 14 items

tests/test_config.py::test_config_db_url FAILED                          [  7%]
tests/test_config.py::test_default_db_url PASSED                         [ 14%]
tests/test_config.py::test_empty_db_url PASSED                           [ 21%]
tests/test_config.py::test_none_db_url PASSED                            [ 28%]
tests/test_config.py::test_db_url_precedence PASSED                      [ 35%]
tests/test_config.py::test_db_url_from_db_config PASSED                  [ 42%]
tests/test_config.py::test_get_value[TIMEOUT-1-int] PASSED               [ 50%]
tests/test_config.py::test_get_value[CORS_ALLOWED_ORIGINS-[1, 2, 3]-list] PASSED [ 57%]
tests/test_config.py::test_get_value[DB_NAME-dbname-str] PASSED          [ 64%]
tests/test_config.py::test_event_namespace[kwargs0-/event] PASSED        [ 71%]
tests/test_config.py::test_event_namespace[kwargs1-/api/event] FAILED    [ 78%]
tests/test_config.py::test_event_namespace[kwargs2-/event] PASSED        [ 85%]
tests/test_config.py::test_event_namespace[kwargs3-/event] PASSED        [ 92%]
tests/test_config.py::test_event_namespace[kwargs4-/event] PASSED        [100%]

=========================== short test summary info ============================
PASSED tests/test_config.py::test_default_db_url
PASSED tests/test_config.py::test_empty_db_url
PASSED tests/test_config.py::test_none_db_url
PASSED tests/test_config.py::test_db_url_precedence
PASSED tests/test_config.py::test_db_url_from_db_config
PASSED tests/test_config.py::test_get_value[TIMEOUT-1-int]
PASSED tests/test_config.py::test_get_value[CORS_ALLOWED_ORIGINS-[1, 2, 3]-list]
PASSED tests/test_config.py::test_get_value[DB_NAME-dbname-str]
PASSED tests/test_config.py::test_event_namespace[kwargs0-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs2-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs3-/event]
PASSED tests/test_config.py::test_event_namespace[kwargs4-/event]
FAILED tests/test_config.py::test_config_db_url - KeyError: 'DB_URL'
FAILED tests/test_config.py::test_event_namespace[kwargs1-/api/event] - Asser...
========================= 2 failed, 12 passed in 0.02s =========================
