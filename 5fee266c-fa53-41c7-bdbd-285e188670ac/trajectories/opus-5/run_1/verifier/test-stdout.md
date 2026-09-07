
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Get:1 http://deb.debian.org/debian bullseye InRelease [75.1 kB]
Get:2 http://deb.debian.org/debian-security bullseye-security InRelease [27.2 kB]
Get:3 http://deb.debian.org/debian bullseye-updates InRelease [44.0 kB]
Get:4 http://deb.debian.org/debian bullseye/main arm64 Packages [7955 kB]
Get:5 http://deb.debian.org/debian-security bullseye-security/main arm64 Packages [471 kB]
Get:6 http://deb.debian.org/debian bullseye-updates/main arm64 Packages [16.3 kB]
Fetched 8589 kB in 1s (11.4 MB/s)
Reading package lists...
Building dependency tree...
Reading state information...
121 packages can be upgraded. Run 'apt list --upgradable' to see them.

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Reading package lists...
Building dependency tree...
Reading state information...
patch is already the newest version (2.7.6-7).
0 upgraded, 0 newly installed, 0 to remove and 121 not upgraded.
+ export CI=true
+ CI=true
+ cd /home/changedetection.io
+ bash /home/filter_patch.sh /home/test.patch
+ bash /home/filter_patch.sh /home/fix.patch
+ git -C /home/changedetection.io apply --whitespace=nowarn /home/test.applied.patch /home/fix.applied.patch
+ bash /home/install.sh
Requirement already satisfied: flask~=2.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 1)) (2.1.3)
Requirement already satisfied: flask_wtf in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 2)) (1.2.1)
Requirement already satisfied: eventlet>=0.31.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 3)) (0.39.1)
Requirement already satisfied: validators in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 4)) (0.34.0)
Requirement already satisfied: timeago~=1.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 5)) (1.0.16)
Requirement already satisfied: inscriptis~=2.2 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 6)) (2.5.0)
Requirement already satisfied: feedgen~=0.9 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 7)) (0.9.0)
Requirement already satisfied: flask-login~=0.5 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 8)) (0.6.3)
Requirement already satisfied: pytz in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 9)) (2026.3.post1)
Requirement already satisfied: requests~=2.26 in /usr/local/lib/python3.8/site-packages (from requests[socks]~=2.26->-r requirements.txt (line 12)) (2.32.4)
Requirement already satisfied: urllib3>1.26 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 13)) (1.26.20)
Requirement already satisfied: chardet>2.3.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 14)) (5.2.0)
Requirement already satisfied: wtforms~=3.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 16)) (3.1.2)
Requirement already satisfied: jsonpath-ng~=1.5.3 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 17)) (1.5.3)
Requirement already satisfied: apprise~=0.9.8.3 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 20)) (0.9.8.3)
Requirement already satisfied: paho-mqtt in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 23)) (2.1.0)
Requirement already satisfied: cryptography~=3.4 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 27)) (3.4.8)
Requirement already satisfied: bs4 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 30)) (0.0.2)
Requirement already satisfied: lxml in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 33)) (6.1.2)
Requirement already satisfied: selenium~=4.1.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 36)) (4.1.5)
Requirement already satisfied: werkzeug~=2.0.0 in /usr/local/lib/python3.8/site-packages (from -r requirements.txt (line 41)) (2.0.3)
Requirement already satisfied: Jinja2>=3.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->-r requirements.txt (line 1)) (3.1.6)
Requirement already satisfied: itsdangerous>=2.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->-r requirements.txt (line 1)) (2.0.1)
Requirement already satisfied: click>=8.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->-r requirements.txt (line 1)) (8.1.8)
Requirement already satisfied: importlib-metadata>=3.6.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->-r requirements.txt (line 1)) (8.5.0)
Requirement already satisfied: dnspython>=1.15.0 in /usr/local/lib/python3.8/site-packages (from eventlet>=0.31.0->-r requirements.txt (line 3)) (2.6.1)
Requirement already satisfied: greenlet>=1.0 in /usr/local/lib/python3.8/site-packages (from eventlet>=0.31.0->-r requirements.txt (line 3)) (3.1.1)
Requirement already satisfied: python-dateutil in /usr/local/lib/python3.8/site-packages (from feedgen~=0.9->-r requirements.txt (line 7)) (2.9.0.post0)
Requirement already satisfied: charset_normalizer<4,>=2 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->-r requirements.txt (line 12)) (3.5.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->-r requirements.txt (line 12)) (3.15)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->-r requirements.txt (line 12)) (2026.7.22)
Requirement already satisfied: markupsafe in /usr/local/lib/python3.8/site-packages (from wtforms~=3.0->-r requirements.txt (line 16)) (2.0.1)
Requirement already satisfied: ply in /usr/local/lib/python3.8/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 17)) (3.11)
Requirement already satisfied: decorator in /usr/local/lib/python3.8/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 17)) (5.3.1)
Requirement already satisfied: six in /usr/local/lib/python3.8/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 17)) (1.17.0)
Requirement already satisfied: requests-oauthlib in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->-r requirements.txt (line 20)) (2.0.0)
Requirement already satisfied: markdown in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->-r requirements.txt (line 20)) (3.7)
Requirement already satisfied: PyYAML in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->-r requirements.txt (line 20)) (6.0.3)
Requirement already satisfied: cffi>=1.12 in /usr/local/lib/python3.8/site-packages (from cryptography~=3.4->-r requirements.txt (line 27)) (1.17.1)
Requirement already satisfied: beautifulsoup4 in /usr/local/lib/python3.8/site-packages (from bs4->-r requirements.txt (line 30)) (4.15.0)
Requirement already satisfied: trio~=0.17 in /usr/local/lib/python3.8/site-packages (from selenium~=4.1.0->-r requirements.txt (line 36)) (0.27.0)
Requirement already satisfied: trio-websocket~=0.9 in /usr/local/lib/python3.8/site-packages (from selenium~=4.1.0->-r requirements.txt (line 36)) (0.12.2)
Requirement already satisfied: PySocks!=1.5.7,>=1.5.6 in /usr/local/lib/python3.8/site-packages (from requests[socks]~=2.26->-r requirements.txt (line 12)) (1.7.1)
Requirement already satisfied: pycparser in /usr/local/lib/python3.8/site-packages (from cffi>=1.12->cryptography~=3.4->-r requirements.txt (line 27)) (2.23)
Requirement already satisfied: zipp>=3.20 in /usr/local/lib/python3.8/site-packages (from importlib-metadata>=3.6.0->flask~=2.0->-r requirements.txt (line 1)) (3.20.2)
Requirement already satisfied: attrs>=23.2.0 in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->-r requirements.txt (line 36)) (25.3.0)
Requirement already satisfied: sortedcontainers in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->-r requirements.txt (line 36)) (2.4.0)
Requirement already satisfied: outcome in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->-r requirements.txt (line 36)) (1.3.0.post0)
Requirement already satisfied: sniffio>=1.3.0 in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->-r requirements.txt (line 36)) (1.3.1)
Requirement already satisfied: exceptiongroup in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->-r requirements.txt (line 36)) (1.3.1)
Requirement already satisfied: wsproto>=0.14 in /usr/local/lib/python3.8/site-packages (from trio-websocket~=0.9->selenium~=4.1.0->-r requirements.txt (line 36)) (1.2.0)
Requirement already satisfied: pyOpenSSL>=0.14 in /usr/local/lib/python3.8/site-packages (from urllib3[secure,socks]~=1.26->selenium~=4.1.0->-r requirements.txt (line 36)) (21.0.0)
Requirement already satisfied: urllib3-secure-extra in /usr/local/lib/python3.8/site-packages (from urllib3[secure,socks]~=1.26->selenium~=4.1.0->-r requirements.txt (line 36)) (0.1.0)
Requirement already satisfied: soupsieve>=1.6.1 in /usr/local/lib/python3.8/site-packages (from beautifulsoup4->bs4->-r requirements.txt (line 30)) (2.7)
Requirement already satisfied: typing-extensions>=4.0.0 in /usr/local/lib/python3.8/site-packages (from beautifulsoup4->bs4->-r requirements.txt (line 30)) (4.13.2)
Requirement already satisfied: oauthlib>=3.0.0 in /usr/local/lib/python3.8/site-packages (from requests-oauthlib->apprise~=0.9.8.3->-r requirements.txt (line 20)) (3.3.1)
Requirement already satisfied: h11<1,>=0.9.0 in /usr/local/lib/python3.8/site-packages (from wsproto>=0.14->trio-websocket~=0.9->selenium~=4.1.0->-r requirements.txt (line 36)) (0.16.0)
Requirement already satisfied: pytest~=6.2 in /usr/local/lib/python3.8/site-packages (from -r requirements-dev.txt (line 1)) (6.2.5)
Requirement already satisfied: pytest-flask~=1.2 in /usr/local/lib/python3.8/site-packages (from -r requirements-dev.txt (line 2)) (1.3.0)
Requirement already satisfied: attrs>=19.2.0 in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (25.3.0)
Requirement already satisfied: iniconfig in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (2.1.0)
Requirement already satisfied: packaging in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (26.2)
Requirement already satisfied: pluggy<2.0,>=0.12 in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (1.5.0)
Requirement already satisfied: py>=1.8.2 in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (1.11.0)
Requirement already satisfied: toml in /usr/local/lib/python3.8/site-packages (from pytest~=6.2->-r requirements-dev.txt (line 1)) (0.10.2)
Requirement already satisfied: Flask in /usr/local/lib/python3.8/site-packages (from pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (2.1.3)
Requirement already satisfied: Werkzeug in /usr/local/lib/python3.8/site-packages (from pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (2.0.3)
Requirement already satisfied: Jinja2>=3.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (3.1.6)
Requirement already satisfied: itsdangerous>=2.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (2.0.1)
Requirement already satisfied: click>=8.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (8.1.8)
Requirement already satisfied: importlib-metadata>=3.6.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (8.5.0)
Requirement already satisfied: zipp>=3.20 in /usr/local/lib/python3.8/site-packages (from importlib-metadata>=3.6.0->Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (3.20.2)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.8/site-packages (from Jinja2>=3.0->Flask->pytest-flask~=1.2->-r requirements-dev.txt (line 2)) (2.0.1)
Obtaining file:///home/changedetection.io
  Preparing metadata (setup.py): started
  Preparing metadata (setup.py): finished with status 'done'
Requirement already satisfied: flask~=2.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (2.1.3)
Requirement already satisfied: flask_wtf in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (1.2.1)
Requirement already satisfied: eventlet>=0.31.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.39.1)
Requirement already satisfied: validators in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.34.0)
Requirement already satisfied: timeago~=1.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (1.0.16)
Requirement already satisfied: inscriptis~=2.2 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (2.5.0)
Requirement already satisfied: feedgen~=0.9 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.9.0)
Requirement already satisfied: flask-login~=0.5 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.6.3)
Requirement already satisfied: pytz in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (2026.3.post1)
Requirement already satisfied: requests~=2.26 in /usr/local/lib/python3.8/site-packages (from requests[socks]~=2.26->changedetection.io==0.39.13) (2.32.4)
Requirement already satisfied: urllib3>1.26 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (1.26.20)
Requirement already satisfied: chardet>2.3.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (5.2.0)
Requirement already satisfied: wtforms~=3.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (3.1.2)
Requirement already satisfied: jsonpath-ng~=1.5.3 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (1.5.3)
Requirement already satisfied: apprise~=0.9.8.3 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.9.8.3)
Requirement already satisfied: paho-mqtt in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (2.1.0)
Requirement already satisfied: cryptography~=3.4 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (3.4.8)
Requirement already satisfied: bs4 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (0.0.2)
Requirement already satisfied: lxml in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (6.1.2)
Requirement already satisfied: selenium~=4.1.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (4.1.5)
Requirement already satisfied: werkzeug~=2.0.0 in /usr/local/lib/python3.8/site-packages (from changedetection.io==0.39.13) (2.0.3)
Requirement already satisfied: requests-oauthlib in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->changedetection.io==0.39.13) (2.0.0)
Requirement already satisfied: six in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->changedetection.io==0.39.13) (1.17.0)
Requirement already satisfied: click>=5.0 in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->changedetection.io==0.39.13) (8.1.8)
Requirement already satisfied: markdown in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->changedetection.io==0.39.13) (3.7)
Requirement already satisfied: PyYAML in /usr/local/lib/python3.8/site-packages (from apprise~=0.9.8.3->changedetection.io==0.39.13) (6.0.3)
Requirement already satisfied: cffi>=1.12 in /usr/local/lib/python3.8/site-packages (from cryptography~=3.4->changedetection.io==0.39.13) (1.17.1)
Requirement already satisfied: dnspython>=1.15.0 in /usr/local/lib/python3.8/site-packages (from eventlet>=0.31.0->changedetection.io==0.39.13) (2.6.1)
Requirement already satisfied: greenlet>=1.0 in /usr/local/lib/python3.8/site-packages (from eventlet>=0.31.0->changedetection.io==0.39.13) (3.1.1)
Requirement already satisfied: python-dateutil in /usr/local/lib/python3.8/site-packages (from feedgen~=0.9->changedetection.io==0.39.13) (2.9.0.post0)
Requirement already satisfied: Jinja2>=3.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->changedetection.io==0.39.13) (3.1.6)
Requirement already satisfied: itsdangerous>=2.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->changedetection.io==0.39.13) (2.0.1)
Requirement already satisfied: importlib-metadata>=3.6.0 in /usr/local/lib/python3.8/site-packages (from flask~=2.0->changedetection.io==0.39.13) (8.5.0)
Requirement already satisfied: ply in /usr/local/lib/python3.8/site-packages (from jsonpath-ng~=1.5.3->changedetection.io==0.39.13) (3.11)
Requirement already satisfied: decorator in /usr/local/lib/python3.8/site-packages (from jsonpath-ng~=1.5.3->changedetection.io==0.39.13) (5.3.1)
Requirement already satisfied: charset_normalizer<4,>=2 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->changedetection.io==0.39.13) (3.5.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->changedetection.io==0.39.13) (3.15)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.8/site-packages (from requests~=2.26->requests[socks]~=2.26->changedetection.io==0.39.13) (2026.7.22)
Requirement already satisfied: PySocks!=1.5.7,>=1.5.6 in /usr/local/lib/python3.8/site-packages (from requests[socks]~=2.26->changedetection.io==0.39.13) (1.7.1)
Requirement already satisfied: trio~=0.17 in /usr/local/lib/python3.8/site-packages (from selenium~=4.1.0->changedetection.io==0.39.13) (0.27.0)
Requirement already satisfied: trio-websocket~=0.9 in /usr/local/lib/python3.8/site-packages (from selenium~=4.1.0->changedetection.io==0.39.13) (0.12.2)
Requirement already satisfied: markupsafe in /usr/local/lib/python3.8/site-packages (from wtforms~=3.0->changedetection.io==0.39.13) (2.0.1)
Requirement already satisfied: beautifulsoup4 in /usr/local/lib/python3.8/site-packages (from bs4->changedetection.io==0.39.13) (4.15.0)
Requirement already satisfied: pycparser in /usr/local/lib/python3.8/site-packages (from cffi>=1.12->cryptography~=3.4->changedetection.io==0.39.13) (2.23)
Requirement already satisfied: zipp>=3.20 in /usr/local/lib/python3.8/site-packages (from importlib-metadata>=3.6.0->flask~=2.0->changedetection.io==0.39.13) (3.20.2)
Requirement already satisfied: attrs>=23.2.0 in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->changedetection.io==0.39.13) (25.3.0)
Requirement already satisfied: sortedcontainers in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->changedetection.io==0.39.13) (2.4.0)
Requirement already satisfied: outcome in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->changedetection.io==0.39.13) (1.3.0.post0)
Requirement already satisfied: sniffio>=1.3.0 in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->changedetection.io==0.39.13) (1.3.1)
Requirement already satisfied: exceptiongroup in /usr/local/lib/python3.8/site-packages (from trio~=0.17->selenium~=4.1.0->changedetection.io==0.39.13) (1.3.1)
Requirement already satisfied: wsproto>=0.14 in /usr/local/lib/python3.8/site-packages (from trio-websocket~=0.9->selenium~=4.1.0->changedetection.io==0.39.13) (1.2.0)
Requirement already satisfied: pyOpenSSL>=0.14 in /usr/local/lib/python3.8/site-packages (from urllib3[secure,socks]~=1.26->selenium~=4.1.0->changedetection.io==0.39.13) (21.0.0)
Requirement already satisfied: urllib3-secure-extra in /usr/local/lib/python3.8/site-packages (from urllib3[secure,socks]~=1.26->selenium~=4.1.0->changedetection.io==0.39.13) (0.1.0)
Requirement already satisfied: soupsieve>=1.6.1 in /usr/local/lib/python3.8/site-packages (from beautifulsoup4->bs4->changedetection.io==0.39.13) (2.7)
Requirement already satisfied: typing-extensions>=4.0.0 in /usr/local/lib/python3.8/site-packages (from beautifulsoup4->bs4->changedetection.io==0.39.13) (4.13.2)
Requirement already satisfied: oauthlib>=3.0.0 in /usr/local/lib/python3.8/site-packages (from requests-oauthlib->apprise~=0.9.8.3->changedetection.io==0.39.13) (3.3.1)
Requirement already satisfied: h11<1,>=0.9.0 in /usr/local/lib/python3.8/site-packages (from wsproto>=0.14->trio-websocket~=0.9->selenium~=4.1.0->changedetection.io==0.39.13) (0.16.0)
Installing collected packages: changedetection.io
  Attempting uninstall: changedetection.io
    Found existing installation: changedetection.io 0.39.13
    Uninstalling changedetection.io-0.39.13:
      Successfully uninstalled changedetection.io-0.39.13
  DEPRECATION: Legacy editable install of changedetection.io==0.39.13 from file:///home/changedetection.io (setup.py develop) is deprecated. pip 25.1 will enforce this behaviour change. A possible replacement is to add a pyproject.toml or enable --use-pep517, and use setuptools >= 64. If the resulting installation is not behaving as expected, try using --config-settings editable_mode=compat. Please consult the setuptools documentation for more information. Discussion can be found at https://github.com/pypa/pip/issues/11457
  Running setup.py develop for changedetection.io
Successfully installed changedetection.io
Requirement already satisfied: pytest in /usr/local/lib/python3.8/site-packages (6.2.5)
Requirement already satisfied: pytest-flask in /usr/local/lib/python3.8/site-packages (1.3.0)
Requirement already satisfied: attrs>=19.2.0 in /usr/local/lib/python3.8/site-packages (from pytest) (25.3.0)
Requirement already satisfied: iniconfig in /usr/local/lib/python3.8/site-packages (from pytest) (2.1.0)
Requirement already satisfied: packaging in /usr/local/lib/python3.8/site-packages (from pytest) (26.2)
Requirement already satisfied: pluggy<2.0,>=0.12 in /usr/local/lib/python3.8/site-packages (from pytest) (1.5.0)
Requirement already satisfied: py>=1.8.2 in /usr/local/lib/python3.8/site-packages (from pytest) (1.11.0)
Requirement already satisfied: toml in /usr/local/lib/python3.8/site-packages (from pytest) (0.10.2)
Requirement already satisfied: Flask in /usr/local/lib/python3.8/site-packages (from pytest-flask) (2.1.3)
Requirement already satisfied: Werkzeug in /usr/local/lib/python3.8/site-packages (from pytest-flask) (2.0.3)
Requirement already satisfied: Jinja2>=3.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask) (3.1.6)
Requirement already satisfied: itsdangerous>=2.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask) (2.0.1)
Requirement already satisfied: click>=8.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask) (8.1.8)
Requirement already satisfied: importlib-metadata>=3.6.0 in /usr/local/lib/python3.8/site-packages (from Flask->pytest-flask) (8.5.0)
Requirement already satisfied: zipp>=3.20 in /usr/local/lib/python3.8/site-packages (from importlib-metadata>=3.6.0->Flask->pytest-flask) (3.20.2)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.8/site-packages (from Jinja2>=3.0->Flask->pytest-flask) (2.0.1)
Requirement already satisfied: typing_extensions in /usr/local/lib/python3.8/site-packages (4.13.2)
Requirement already satisfied: markupsafe<2.1 in /usr/local/lib/python3.8/site-packages (2.0.1)
Requirement already satisfied: itsdangerous<2.1 in /usr/local/lib/python3.8/site-packages (2.0.1)
+ cd /home/changedetection.io/changedetectionio
+ TARGET='tests/test_api.py tests/test_auth.py tests/test_backend.py tests/test_clone.py tests/test_css_selector.py tests/test_element_removal.py tests/test_encoding.py tests/test_errorhandling.py tests/test_ignore_text.py tests/test_ignorehyperlinks.py tests/test_ignorestatuscode.py tests/test_ignorewhitespace.py tests/test_import.py tests/test_jsonpath_selector.py tests/test_nonrenderable_pages.py tests/test_notification.py tests/test_notification_errors.py tests/test_share_watch.py tests/test_source.py tests/test_trigger.py tests/test_trigger_regex.py tests/test_trigger_regex_with_filter.py tests/test_xpath_selector.py'
+ ran=0
+ for f in $TARGET
+ '[' -e tests/test_api.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_api.py ====='
+ timeout -k 30 240 python -m pytest tests/test_api.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_api.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_api.py ..                                                     [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_api.py::test_api_simple
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_api.py::test_api_simple
PASSED tests/test_api.py::test_access_denied
======================== 2 passed, 2 warnings in 6.11s =========================
Shutting down datastore thread
+ for f in $TARGET
+ '[' -e tests/test_auth.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_auth.py ====='
===== PYTEST FILE: tests/test_auth.py =====
+ timeout -k 30 240 python -m pytest tests/test_auth.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_auth.py F                                                     [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_auth.py::test_basic_auth - werkzeug.routing.BuildError: Cou...
========================= 1 failed, 1 warning in 1.09s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_backend.py ']'
===== PYTEST FILE: tests/test_backend.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_backend.py ====='
+ timeout -k 30 240 python -m pytest tests/test_backend.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_backend.py .F                                                 [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_backend.py::test_inscriptus
FAILED tests/test_backend.py::test_check_basic_change_detection_functionality
==================== 1 failed, 1 passed, 1 warning in 3.09s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_clone.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_clone.py ====='
+ timeout -k 30 240 python -m pytest tests/test_clone.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_clone.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_clone.py F                                                    [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_clone.py::test_trigger_functionality - werkzeug.routing.Bui...
========================= 1 failed, 1 warning in 1.08s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_css_selector.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_css_selector.py ====='
+ timeout -k 30 240 python -m pytest tests/test_css_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_css_selector.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_css_selector.py ..F                                           [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_css_selector.py::test_check_markup_css_filter_restriction
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_css_selector.py::test_setup
PASSED tests/test_css_selector.py::test_css_filter_output
FAILED tests/test_css_selector.py::test_check_markup_css_filter_restriction
=================== 1 failed, 2 passed, 2 warnings in 1.09s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_element_removal.py ']'
===== PYTEST FILE: tests/test_element_removal.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_element_removal.py ====='
+ timeout -k 30 240 python -m pytest tests/test_element_removal.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_element_removal.py ..F                                        [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_element_removal.py::test_element_removal_full
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_element_removal.py::test_element_removal_full
tests/test_element_removal.py::test_element_removal_full
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_element_removal.py::test_setup
PASSED tests/test_element_removal.py::test_element_removal_output
FAILED tests/test_element_removal.py::test_element_removal_full - werkzeug.ro...
=================== 1 failed, 2 passed, 4 warnings in 1.11s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_encoding.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_encoding.py ====='
+ timeout -k 30 240 python -m pytest tests/test_encoding.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_encoding.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_encoding.py .FF                                               [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_encoding.py::test_check_encoding_detection
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_encoding.py::test_setup
FAILED tests/test_encoding.py::test_check_encoding_detection - werkzeug.routi...
FAILED tests/test_encoding.py::test_check_encoding_detection_missing_content_type_header
=================== 2 failed, 1 passed, 2 warnings in 2.10s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_errorhandling.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_errorhandling.py ====='
+ timeout -k 30 240 python -m pytest tests/test_errorhandling.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_errorhandling.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_errorhandling.py .FF                                          [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_errorhandling.py::test_error_handler
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_errorhandling.py::test_setup
FAILED tests/test_errorhandling.py::test_error_handler - werkzeug.routing.Bui...
FAILED tests/test_errorhandling.py::test_error_text_handler - werkzeug.routin...
=================== 2 failed, 1 passed, 2 warnings in 2.10s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_ignore_text.py ']'
+ ran=1
===== PYTEST FILE: tests/test_ignore_text.py =====
+ echo '===== PYTEST FILE: tests/test_ignore_text.py ====='
+ timeout -k 30 240 python -m pytest tests/test_ignore_text.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 4 items

tests/test_ignore_text.py ..FF                                           [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_ignore_text.py::test_check_ignore_text_functionality
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_ignore_text.py::test_check_global_ignore_text_functionality
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignore_text.py::test_setup
PASSED tests/test_ignore_text.py::test_strip_text_func
FAILED tests/test_ignore_text.py::test_check_ignore_text_functionality - werk...
FAILED tests/test_ignore_text.py::test_check_global_ignore_text_functionality
=================== 2 failed, 2 passed, 3 warnings in 2.12s ====================
Shutting down datastore thread
+ true
===== PYTEST FILE: tests/test_ignorehyperlinks.py =====
+ for f in $TARGET
+ '[' -e tests/test_ignorehyperlinks.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorehyperlinks.py ====='
+ timeout -k 30 240 python -m pytest tests/test_ignorehyperlinks.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_ignorehyperlinks.py .F                                        [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_ignorehyperlinks.py::test_render_anchor_tag_content_true
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_ignorehyperlinks.py::test_render_anchor_tag_content_true
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorehyperlinks.py::test_setup
FAILED tests/test_ignorehyperlinks.py::test_render_anchor_tag_content_true - ...
=================== 1 failed, 1 passed, 3 warnings in 4.11s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_ignorestatuscode.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorestatuscode.py ====='
===== PYTEST FILE: tests/test_ignorestatuscode.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignorestatuscode.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 4 items

tests/test_ignorestatuscode.py .FFF                                      [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_ignorestatuscode.py::test_normal_page_check_works_with_ignore_status_code
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_ignorestatuscode.py::test_normal_page_check_works_with_ignore_status_code
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorestatuscode.py::test_setup
FAILED tests/test_ignorestatuscode.py::test_normal_page_check_works_with_ignore_status_code
FAILED tests/test_ignorestatuscode.py::test_403_page_check_works_with_ignore_status_code
FAILED tests/test_ignorestatuscode.py::test_403_page_check_fails_without_ignore_status_code
=================== 3 failed, 1 passed, 3 warnings in 6.15s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_ignorewhitespace.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorewhitespace.py ====='
===== PYTEST FILE: tests/test_ignorewhitespace.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignorewhitespace.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_ignorewhitespace.py .F                                        [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_ignorewhitespace.py::test_check_ignore_whitespace
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_ignorewhitespace.py::test_check_ignore_whitespace
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorewhitespace.py::test_setup
FAILED tests/test_ignorewhitespace.py::test_check_ignore_whitespace - werkzeu...
=================== 1 failed, 1 passed, 3 warnings in 4.10s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_import.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_import.py ====='
+ timeout -k 30 240 python -m pytest tests/test_import.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_import.py =====
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_import.py .FF                                                 [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_import.py::test_import
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_import.py::test_import_distillio
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'example.com'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_import.py::test_setup
FAILED tests/test_import.py::test_import - werkzeug.routing.BuildError: Could...
FAILED tests/test_import.py::test_import_distillio - werkzeug.routing.BuildEr...
=================== 2 failed, 1 passed, 3 warnings in 2.09s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_jsonpath_selector.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_jsonpath_selector.py ====='
===== PYTEST FILE: tests/test_jsonpath_selector.py =====
+ timeout -k 30 240 python -m pytest tests/test_jsonpath_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 6 items

tests/test_jsonpath_selector.py ..FFFF                                   [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_jsonpath_selector.py::test_unittest_inline_html_extract
tests/test_jsonpath_selector.py::test_unittest_inline_html_extract
  /home/changedetection.io/changedetectionio/html_tools.py:101: DeprecationWarning: Call to deprecated method findAll. (Replaced by find_all) -- Deprecated since version 4.0.0.
    bs_result = soup.findAll('script')

tests/test_jsonpath_selector.py::test_check_json_without_filter
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_jsonpath_selector.py::test_setup
PASSED tests/test_jsonpath_selector.py::test_unittest_inline_html_extract
FAILED tests/test_jsonpath_selector.py::test_check_json_without_filter - werk...
FAILED tests/test_jsonpath_selector.py::test_check_json_filter - werkzeug.rou...
FAILED tests/test_jsonpath_selector.py::test_check_json_filter_bool_val - wer...
FAILED tests/test_jsonpath_selector.py::test_check_json_ext_filter - werkzeug...
=================== 4 failed, 2 passed, 4 warnings in 10.18s ===================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_nonrenderable_pages.py ']'
===== PYTEST FILE: tests/test_nonrenderable_pages.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_nonrenderable_pages.py ====='
+ timeout -k 30 240 python -m pytest tests/test_nonrenderable_pages.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_nonrenderable_pages.py F                                      [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_nonrenderable_pages.py::test_check_basic_change_detection_functionality
========================= 1 failed, 1 warning in 3.11s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_notification.py ']'
+ ran=1
===== PYTEST FILE: tests/test_notification.py =====
+ echo '===== PYTEST FILE: tests/test_notification.py ====='
+ timeout -k 30 240 python -m pytest tests/test_notification.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_notification.py .FF                                           [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_notification.py::test_check_notification
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_notification.py::test_check_notification
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_notification.py::test_setup
FAILED tests/test_notification.py::test_check_notification - werkzeug.routing...
FAILED tests/test_notification.py::test_notification_validation - werkzeug.ro...
=================== 2 failed, 1 passed, 3 warnings in 6.09s ====================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_notification_errors.py ']'
===== PYTEST FILE: tests/test_notification_errors.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_notification_errors.py ====='
+ timeout -k 30 240 python -m pytest tests/test_notification_errors.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_notification_errors.py F                                      [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_notification_errors.py::test_check_notification_error_handling
========================= 1 failed, 1 warning in 3.04s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_share_watch.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_share_watch.py ====='
===== PYTEST FILE: tests/test_share_watch.py =====
+ timeout -k 30 240 python -m pytest tests/test_share_watch.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_share_watch.py F                                              [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_share_watch.py::test_share_watch
tests/test_share_watch.py::test_share_watch
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_share_watch.py::test_share_watch - werkzeug.routing.BuildEr...
======================== 1 failed, 3 warnings in 0.10s =========================
/usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
  warnings.warn(
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_source.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_source.py ====='
===== PYTEST FILE: tests/test_source.py =====
+ timeout -k 30 240 python -m pytest tests/test_source.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_source.py .F.                                                 [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_source.py::test_check_basic_change_detection_functionality_source
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_source.py::test_setup
PASSED tests/test_source.py::test_check_ignore_elements
FAILED tests/test_source.py::test_check_basic_change_detection_functionality_source
=================== 1 failed, 2 passed, 2 warnings in 11.11s ===================
Shutting down datastore thread
+ true
+ for f in $TARGET
===== PYTEST FILE: tests/test_trigger.py =====
+ '[' -e tests/test_trigger.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_trigger.py ====='
+ timeout -k 30 240 python -m pytest tests/test_trigger.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger.py F                                                  [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_trigger.py::test_trigger_functionality - werkzeug.routing.B...
========================= 1 failed, 1 warning in 1.08s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_trigger_regex.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_trigger_regex.py ====='
===== PYTEST FILE: tests/test_trigger_regex.py =====
+ timeout -k 30 240 python -m pytest tests/test_trigger_regex.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger_regex.py F                                            [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_trigger_regex.py:58
  /home/changedetection.io/changedetectionio/tests/test_trigger_regex.py:58: DeprecationWarning: invalid escape sequence \d
    data={"trigger_text": '/something \d{3}/',

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_trigger_regex.py::test_trigger_regex_functionality - werkze...
======================== 1 failed, 2 warnings in 1.09s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_trigger_regex_with_filter.py ']'
===== PYTEST FILE: tests/test_trigger_regex_with_filter.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_trigger_regex_with_filter.py ====='
+ timeout -k 30 240 python -m pytest tests/test_trigger_regex_with_filter.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger_regex_with_filter.py F                                [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_trigger_regex_with_filter.py:58
  /home/changedetection.io/changedetectionio/tests/test_trigger_regex_with_filter.py:58: DeprecationWarning: invalid escape sequence \d
    data={"trigger_text": "/cool.stuff\d/",

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
FAILED tests/test_trigger_regex_with_filter.py::test_trigger_regex_functionality
======================== 1 failed, 2 warnings in 1.08s =========================
Shutting down datastore thread
+ true
+ for f in $TARGET
+ '[' -e tests/test_xpath_selector.py ']'
===== PYTEST FILE: tests/test_xpath_selector.py =====
+ ran=1
+ echo '===== PYTEST FILE: tests/test_xpath_selector.py ====='
+ timeout -k 30 240 python -m pytest tests/test_xpath_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.8.20, pytest-6.2.5, py-1.11.0, pluggy-1.5.0
rootdir: /home/changedetection.io/changedetectionio, configfile: pytest.ini
plugins: flask-1.3.0
collected 5 items

tests/test_xpath_selector.py .FFFF                                       [100%]

=============================== warnings summary ===============================
../../../usr/local/lib/python3.8/site-packages/requests/__init__.py:43
  /usr/local/lib/python3.8/site-packages/requests/__init__.py:43: DeprecationWarning: 'urllib3[secure]' extra is deprecated and will be removed in a future release of urllib3 2.x. Read more in this issue: https://github.com/urllib3/urllib3/issues/2680
    import urllib3

tests/test_xpath_selector.py::test_check_xpath_filter_utf8
  /usr/local/lib/python3.8/site-packages/urllib3/connectionpool.py:1064: InsecureRequestWarning: Unverified HTTPS request is being made to host 'changedetection.io'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
    warnings.warn(

tests/test_xpath_selector.py::test_xpath_validation
tests/test_xpath_selector.py::test_xpath_validation
  /usr/local/lib/python3.8/site-packages/jinja2/lexer.py:652: DeprecationWarning: invalid escape sequence '\d'
    self._normalize_newlines(value_str[1:-1])

-- Docs: https://docs.pytest.org/en/stable/warnings.html
=========================== short test summary info ============================
PASSED tests/test_xpath_selector.py::test_setup
FAILED tests/test_xpath_selector.py::test_check_xpath_filter_utf8 - assert b'...
FAILED tests/test_xpath_selector.py::test_check_markup_xpath_filter_restriction
FAILED tests/test_xpath_selector.py::test_xpath_validation - werkzeug.routing...
FAILED tests/test_xpath_selector.py::test_check_with_prefix_css_filter - werk...
=================== 4 failed, 1 passed, 4 warnings in 5.14s ====================
Shutting down datastore thread
+ true
+ '[' 1 = 0 ']'
