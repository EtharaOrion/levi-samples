
WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Get:1 http://deb.debian.org/debian bookworm InRelease [151 kB]
Get:2 http://deb.debian.org/debian bookworm-updates InRelease [55.4 kB]
Get:3 http://deb.debian.org/debian-security bookworm-security InRelease [34.8 kB]
Get:4 http://deb.debian.org/debian bookworm/main arm64 Packages [8689 kB]
Get:5 http://deb.debian.org/debian bookworm-updates/main arm64 Packages [6936 B]
Get:6 http://deb.debian.org/debian-security bookworm-security/main arm64 Packages [334 kB]
Fetched 9272 kB in 1s (10.7 MB/s)
Reading package lists...
Building dependency tree...
Reading state information...
8 packages can be upgraded. Run 'apt list --upgradable' to see them.

WARNING: apt does not have a stable CLI interface. Use with caution in scripts.

Reading package lists...
Building dependency tree...
Reading state information...
patch is already the newest version (2.7.6-7).
0 upgraded, 0 newly installed, 0 to remove and 8 not upgraded.
+ export CI=true
+ CI=true
+ cd /home/changedetection.io
+ bash /home/filter_patch.sh /home/test.patch
+ bash /home/filter_patch.sh /home/fix.patch
+ git -C /home/changedetection.io apply --whitespace=nowarn /home/test.applied.patch /home/fix.applied.patch
+ bash /home/install.sh
Ignoring jq: markers 'python_version >= "3.8" and sys_platform == "darwin"' don't match your environment
Requirement already satisfied: feedgen~=0.9 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 2)) (0.9.0)
Requirement already satisfied: flask-compress in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 3)) (1.24)
Requirement already satisfied: flask-login>=0.6.3 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 5)) (0.6.3)
Requirement already satisfied: flask-paginate in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 6)) (2024.4.12)
Requirement already satisfied: flask_expects_json~=1.7 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 7)) (1.7.0)
Requirement already satisfied: flask_restful in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 8)) (0.3.10)
Requirement already satisfied: flask_cors in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 9)) (6.0.5)
Requirement already satisfied: janus in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 10)) (2.0.0)
Requirement already satisfied: flask_wtf~=1.2 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 11)) (1.3.0)
Requirement already satisfied: flask~=2.3 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 12)) (2.3.3)
Requirement already satisfied: flask-socketio~=5.5.1 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 13)) (5.5.1)
Requirement already satisfied: python-socketio~=5.13.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 14)) (5.13.0)
Requirement already satisfied: python-engineio~=4.12.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 15)) (4.12.3)
Requirement already satisfied: inscriptis~=2.2 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 16)) (2.7.4)
Requirement already satisfied: pytz in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 17)) (2026.3.post1)
Requirement already satisfied: timeago~=1.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 18)) (1.0.16)
Requirement already satisfied: validators~=0.21 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 19)) (0.35.0)
Requirement already satisfied: brotli~=1.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 24)) (1.2.0)
Requirement already satisfied: requests-file in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 26)) (3.0.1)
Requirement already satisfied: chardet>2.3.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 30)) (7.6.0)
Requirement already satisfied: wtforms~=3.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 32)) (3.2.2)
Requirement already satisfied: jsonpath-ng~=1.5.3 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 33)) (1.5.3)
Collecting apprise==1.9.4 (from -r requirements.txt (line 42))
  Downloading apprise-1.9.4-py3-none-any.whl.metadata (55 kB)
Requirement already satisfied: cryptography==44.0.1 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 48)) (44.0.1)
Requirement already satisfied: paho-mqtt!=2.0.* in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 52)) (2.1.0)
Requirement already satisfied: beautifulsoup4>=4.0.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 55)) (4.15.0)
Requirement already satisfied: lxml!=5.2.0,!=5.2.1,<6,>=4.8.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 61)) (5.4.0)
Requirement already satisfied: elementpath==4.1.5 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 65)) (4.1.5)
Requirement already satisfied: selenium~=4.31.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 67)) (4.31.0)
Requirement already satisfied: werkzeug==3.0.6 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 71)) (3.0.6)
Requirement already satisfied: jinja2~=3.1 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 74)) (3.1.6)
Requirement already satisfied: jinja2-time in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 75)) (0.2.0)
Requirement already satisfied: openpyxl in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 76)) (3.1.5)
Requirement already satisfied: jq~=1.3 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 80)) (1.12.0)
Requirement already satisfied: pyppeteer-ng==2.0.0rc10 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 84)) (2.0.0rc10)
Requirement already satisfied: pyppeteerstealth>=0.0.4 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 86)) (0.0.5)
Requirement already satisfied: pytest~=7.2 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 89)) (7.4.4)
Requirement already satisfied: pytest-flask~=1.2 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 90)) (1.3.0)
Requirement already satisfied: jsonschema~=4.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 93)) (4.24.1)
Requirement already satisfied: openapi-core>=0.19.0 in /usr/local/lib/python3.11/site-packages (from openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.19.5)
Requirement already satisfied: loguru in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 99)) (0.7.3)
Requirement already satisfied: extruct in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 102)) (0.18.0)
Requirement already satisfied: babel in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 105)) (2.18.0)
Requirement already satisfied: levenshtein in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 107)) (0.27.4)
Requirement already satisfied: greenlet>=3.0.3 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 110)) (3.5.5)
Requirement already satisfied: gevent in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 115)) (26.8.0)
Requirement already satisfied: referencing==0.35.1 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 118)) (0.35.1)
Requirement already satisfied: panzi-json-logic in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 121)) (1.0.1)
Requirement already satisfied: price-parser in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 123)) (0.5.1)
Requirement already satisfied: python-magic in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 128)) (0.4.27)
Requirement already satisfied: tzdata in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 131)) (2026.3)
Requirement already satisfied: pluggy~=1.5 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 135)) (1.6.0)
Requirement already satisfied: psutil==7.0.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 138)) (7.0.0)
Requirement already satisfied: ruff>=0.11.2 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 140)) (0.16.6)
Requirement already satisfied: pre_commit>=4.2.0 in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 141)) (4.6.2)
Requirement already satisfied: blinker in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 144)) (1.9.0)
Requirement already satisfied: requests[socks] in /usr/local/lib/python3.11/site-packages (from -r requirements.txt (line 25)) (2.34.2)
Requirement already satisfied: requests-oauthlib in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->-r requirements.txt (line 42)) (2.0.0)
Requirement already satisfied: click>=5.0 in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->-r requirements.txt (line 42)) (8.5.0)
Requirement already satisfied: markdown in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->-r requirements.txt (line 42)) (3.10.3)
Requirement already satisfied: PyYAML in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->-r requirements.txt (line 42)) (6.0.3)
Requirement already satisfied: certifi in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->-r requirements.txt (line 42)) (2026.7.22)
Requirement already satisfied: cffi>=1.12 in /usr/local/lib/python3.11/site-packages (from cryptography==44.0.1->-r requirements.txt (line 48)) (2.1.1)
Requirement already satisfied: MarkupSafe>=2.1.1 in /usr/local/lib/python3.11/site-packages (from werkzeug==3.0.6->-r requirements.txt (line 71)) (3.0.3)
Requirement already satisfied: aenum<3.0.0,>=2.2.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (2.2.6)
Requirement already satisfied: appdirs<2.0.0,>=1.4.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (1.4.4)
Requirement already satisfied: ordered_set<5.0.0,>=4.0.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (4.1.0)
Requirement already satisfied: pillow>=9.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (12.3.0)
Requirement already satisfied: pyee>=12.0.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (13.0.1)
Requirement already satisfied: tqdm<5.0.0,>=4.42.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (4.70.0)
Requirement already satisfied: typing_extensions>=4.0.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (4.16.0)
Requirement already satisfied: typing_inspect<0.6.0,>=0.5.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (0.5.0)
Requirement already satisfied: urllib3<2.0.0,>=1.25.8 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (1.26.20)
Requirement already satisfied: websockets<11.0,>=10.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (10.4)
Requirement already satisfied: attrs>=22.2.0 in /usr/local/lib/python3.11/site-packages (from referencing==0.35.1->-r requirements.txt (line 118)) (26.1.0)
Requirement already satisfied: rpds-py>=0.7.0 in /usr/local/lib/python3.11/site-packages (from referencing==0.35.1->-r requirements.txt (line 118)) (2026.6.3)
Requirement already satisfied: python-dateutil in /usr/local/lib/python3.11/site-packages (from feedgen~=0.9->-r requirements.txt (line 2)) (2.9.0.post0)
Requirement already satisfied: itsdangerous in /usr/local/lib/python3.11/site-packages (from flask_wtf~=1.2->-r requirements.txt (line 11)) (2.2.0)
Requirement already satisfied: bidict>=0.21.0 in /usr/local/lib/python3.11/site-packages (from python-socketio~=5.13.0->-r requirements.txt (line 14)) (0.24.1)
Requirement already satisfied: simple-websocket>=0.10.0 in /usr/local/lib/python3.11/site-packages (from python-engineio~=4.12.0->-r requirements.txt (line 15)) (1.1.0)
Requirement already satisfied: ply in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 33)) (3.11)
Requirement already satisfied: decorator in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 33)) (5.3.1)
Requirement already satisfied: six in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->-r requirements.txt (line 33)) (1.17.0)
Requirement already satisfied: trio~=0.17 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->-r requirements.txt (line 67)) (0.34.0)
Requirement already satisfied: trio-websocket~=0.9 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->-r requirements.txt (line 67)) (0.12.2)
Requirement already satisfied: websocket-client~=1.8 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->-r requirements.txt (line 67)) (1.9.2)
Requirement already satisfied: iniconfig in /usr/local/lib/python3.11/site-packages (from pytest~=7.2->-r requirements.txt (line 89)) (2.3.0)
Requirement already satisfied: packaging in /usr/local/lib/python3.11/site-packages (from pytest~=7.2->-r requirements.txt (line 89)) (26.3)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in /usr/local/lib/python3.11/site-packages (from jsonschema~=4.0->-r requirements.txt (line 93)) (2025.9.1)
Requirement already satisfied: charset_normalizer<4,>=2 in /usr/local/lib/python3.11/site-packages (from requests[socks]->-r requirements.txt (line 25)) (3.5.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.11/site-packages (from requests[socks]->-r requirements.txt (line 25)) (3.19)
Requirement already satisfied: sortedcontainers in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->-r requirements.txt (line 67)) (2.4.0)
Requirement already satisfied: outcome in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->-r requirements.txt (line 67)) (1.3.0.post0)
Requirement already satisfied: sniffio>=1.3.0 in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->-r requirements.txt (line 67)) (1.3.1)
Requirement already satisfied: wsproto>=0.14 in /usr/local/lib/python3.11/site-packages (from trio-websocket~=0.9->selenium~=4.31.0->-r requirements.txt (line 67)) (1.3.2)
Requirement already satisfied: mypy-extensions>=0.3.0 in /usr/local/lib/python3.11/site-packages (from typing_inspect<0.6.0,>=0.5.0->pyppeteer-ng==2.0.0rc10->-r requirements.txt (line 84)) (1.1.0)
Requirement already satisfied: PySocks!=1.5.7,<2.0,>=1.5.6 in /usr/local/lib/python3.11/site-packages (from urllib3[socks]<3,>=1.26->selenium~=4.31.0->-r requirements.txt (line 67)) (1.7.1)
Requirement already satisfied: backports.zstd in /usr/local/lib/python3.11/site-packages (from flask-compress->-r requirements.txt (line 3)) (1.7.0)
Requirement already satisfied: aniso8601>=0.82 in /usr/local/lib/python3.11/site-packages (from flask_restful->-r requirements.txt (line 8)) (10.0.1)
Requirement already satisfied: soupsieve>=1.6.1 in /usr/local/lib/python3.11/site-packages (from beautifulsoup4>=4.0.0->-r requirements.txt (line 55)) (2.9.2)
Requirement already satisfied: arrow in /usr/local/lib/python3.11/site-packages (from jinja2-time->-r requirements.txt (line 75)) (1.4.0)
Requirement already satisfied: et-xmlfile in /usr/local/lib/python3.11/site-packages (from openpyxl->-r requirements.txt (line 76)) (2.0.0)
Requirement already satisfied: isodate in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.7.2)
Requirement already satisfied: jsonschema-path<0.4.0,>=0.3.1 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.3.4)
Requirement already satisfied: more-itertools in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (11.1.0)
Requirement already satisfied: openapi-schema-validator<0.7.0,>=0.6.0 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.6.3)
Requirement already satisfied: openapi-spec-validator<0.8.0,>=0.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.7.2)
Requirement already satisfied: parse in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (1.22.1)
Requirement already satisfied: pathable<0.5.0,>=0.4.1 in /usr/local/lib/python3.11/site-packages (from jsonschema-path<0.4.0,>=0.3.1->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.4.4)
Requirement already satisfied: rfc3339-validator in /usr/local/lib/python3.11/site-packages (from openapi-schema-validator<0.7.0,>=0.6.0->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (0.1.4)
Requirement already satisfied: lazy-object-proxy<2.0.0,>=1.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-spec-validator<0.8.0,>=0.7.1->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->-r requirements.txt (line 96)) (1.12.0)
Requirement already satisfied: lxml-html-clean in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (0.4.4)
Requirement already satisfied: rdflib>=6.0.0 in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (7.6.0)
Requirement already satisfied: pyrdfa3 in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (3.6.5)
Requirement already satisfied: mf2py in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (2.0.1)
Requirement already satisfied: w3lib in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (2.4.1)
Requirement already satisfied: html-text>=0.5.1 in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (0.7.1)
Requirement already satisfied: jstyleson in /usr/local/lib/python3.11/site-packages (from extruct->-r requirements.txt (line 102)) (0.0.2)
Requirement already satisfied: rapidfuzz<4.0.0,>=3.9.0 in /usr/local/lib/python3.11/site-packages (from levenshtein->-r requirements.txt (line 107)) (3.14.6)
Requirement already satisfied: zope.event in /usr/local/lib/python3.11/site-packages (from gevent->-r requirements.txt (line 115)) (6.2)
Requirement already satisfied: zope.interface in /usr/local/lib/python3.11/site-packages (from gevent->-r requirements.txt (line 115)) (8.6)
Requirement already satisfied: cfgv>=2.0.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->-r requirements.txt (line 141)) (3.5.0)
Requirement already satisfied: identify>=1.0.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->-r requirements.txt (line 141)) (2.6.19)
Requirement already satisfied: nodeenv>=0.11.1 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->-r requirements.txt (line 141)) (1.10.0)
Requirement already satisfied: virtualenv>=20.10.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->-r requirements.txt (line 141)) (21.7.8)
Requirement already satisfied: pycparser in /usr/local/lib/python3.11/site-packages (from cffi>=1.12->cryptography==44.0.1->-r requirements.txt (line 48)) (3.0)
Requirement already satisfied: pyparsing<4,>=2.1.0 in /usr/local/lib/python3.11/site-packages (from rdflib>=6.0.0->extruct->-r requirements.txt (line 102)) (3.3.2)
Requirement already satisfied: distlib<1,>=0.3.7 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->-r requirements.txt (line 141)) (0.4.3)
Requirement already satisfied: filelock<4,>=3.24.2 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->-r requirements.txt (line 141)) (3.32.5)
Requirement already satisfied: platformdirs<5,>=3.9.1 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->-r requirements.txt (line 141)) (4.11.7)
Requirement already satisfied: python-discovery>=1.6 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->-r requirements.txt (line 141)) (1.6.0)
Requirement already satisfied: h11<1,>=0.16.0 in /usr/local/lib/python3.11/site-packages (from wsproto>=0.14->trio-websocket~=0.9->selenium~=4.31.0->-r requirements.txt (line 67)) (0.16.0)
Requirement already satisfied: html5lib<2.0,>=1.1 in /usr/local/lib/python3.11/site-packages (from mf2py->extruct->-r requirements.txt (line 102)) (1.1)
Requirement already satisfied: webencodings in /usr/local/lib/python3.11/site-packages (from html5lib<2.0,>=1.1->mf2py->extruct->-r requirements.txt (line 102)) (0.6.1)
Requirement already satisfied: oauthlib>=3.0.0 in /usr/local/lib/python3.11/site-packages (from requests-oauthlib->apprise==1.9.4->-r requirements.txt (line 42)) (3.3.1)
Downloading apprise-1.9.4-py3-none-any.whl (1.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.4/1.4 MB 161.2 MB/s  0:00:00
Installing collected packages: apprise
  Attempting uninstall: apprise
    Found existing installation: apprise 1.9.3
    Uninstalling apprise-1.9.3:
      Successfully uninstalled apprise-1.9.3
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
changedetection-io 0.50.14 requires apprise==1.9.3, but you have apprise 1.9.4 which is incompatible.
Successfully installed apprise-1.9.4
Obtaining file:///home/changedetection.io
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Requirement already satisfied: feedgen~=0.9 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.9.0)
Requirement already satisfied: flask-compress in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.24)
Requirement already satisfied: flask-login>=0.6.3 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.6.3)
Requirement already satisfied: flask-paginate in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2024.4.12)
Requirement already satisfied: flask_expects_json~=1.7 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.7.0)
Requirement already satisfied: flask_restful in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.3.10)
Requirement already satisfied: flask_cors in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (6.0.5)
Requirement already satisfied: janus in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.0.0)
Requirement already satisfied: flask_wtf~=1.2 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.3.0)
Requirement already satisfied: flask~=2.3 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.3.3)
Requirement already satisfied: flask-socketio~=5.5.1 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (5.5.1)
Requirement already satisfied: python-socketio~=5.13.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (5.13.0)
Requirement already satisfied: python-engineio~=4.12.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.12.3)
Requirement already satisfied: inscriptis~=2.2 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.7.4)
Requirement already satisfied: pytz in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2026.3.post1)
Requirement already satisfied: timeago~=1.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.0.16)
Requirement already satisfied: validators~=0.21 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.35.0)
Requirement already satisfied: brotli~=1.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.2.0)
Requirement already satisfied: requests[socks] in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.34.2)
Requirement already satisfied: requests-file in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.0.1)
Requirement already satisfied: chardet>2.3.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (7.6.0)
Requirement already satisfied: wtforms~=3.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.2.2)
Requirement already satisfied: jsonpath-ng~=1.5.3 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.5.3)
Requirement already satisfied: apprise==1.9.4 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.9.4)
Requirement already satisfied: cryptography==44.0.1 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (44.0.1)
Requirement already satisfied: paho-mqtt!=2.0.* in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.1.0)
Requirement already satisfied: beautifulsoup4>=4.0.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.15.0)
Requirement already satisfied: lxml!=5.2.0,!=5.2.1,<6,>=4.8.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (5.4.0)
Requirement already satisfied: elementpath==4.1.5 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.1.5)
Requirement already satisfied: selenium~=4.31.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.31.0)
Requirement already satisfied: werkzeug==3.0.6 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.0.6)
Requirement already satisfied: jinja2~=3.1 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.1.6)
Requirement already satisfied: jinja2-time in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.2.0)
Requirement already satisfied: openpyxl in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.1.5)
Requirement already satisfied: jq~=1.3 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.12.0)
Requirement already satisfied: pyppeteer-ng==2.0.0rc10 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.0.0rc10)
Requirement already satisfied: pyppeteerstealth>=0.0.4 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.0.5)
Requirement already satisfied: pytest~=7.2 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (7.4.4)
Requirement already satisfied: pytest-flask~=1.2 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.3.0)
Requirement already satisfied: jsonschema~=4.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.24.1)
Requirement already satisfied: openapi-core>=0.19.0 in /usr/local/lib/python3.11/site-packages (from openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.19.5)
Requirement already satisfied: loguru in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.7.3)
Requirement already satisfied: extruct in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.18.0)
Requirement already satisfied: babel in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2.18.0)
Requirement already satisfied: levenshtein in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.27.4)
Requirement already satisfied: greenlet>=3.0.3 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (3.5.5)
Requirement already satisfied: gevent in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (26.8.0)
Requirement already satisfied: referencing==0.35.1 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.35.1)
Requirement already satisfied: panzi-json-logic in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.0.1)
Requirement already satisfied: price-parser in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.5.1)
Requirement already satisfied: python-magic in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.4.27)
Requirement already satisfied: tzdata in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (2026.3)
Requirement already satisfied: pluggy~=1.5 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.6.0)
Requirement already satisfied: psutil==7.0.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (7.0.0)
Requirement already satisfied: ruff>=0.11.2 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (0.16.6)
Requirement already satisfied: pre_commit>=4.2.0 in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (4.6.2)
Requirement already satisfied: blinker in /usr/local/lib/python3.11/site-packages (from changedetection.io==0.50.14) (1.9.0)
Requirement already satisfied: requests-oauthlib in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->changedetection.io==0.50.14) (2.0.0)
Requirement already satisfied: click>=5.0 in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->changedetection.io==0.50.14) (8.5.0)
Requirement already satisfied: markdown in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->changedetection.io==0.50.14) (3.10.3)
Requirement already satisfied: PyYAML in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->changedetection.io==0.50.14) (6.0.3)
Requirement already satisfied: certifi in /usr/local/lib/python3.11/site-packages (from apprise==1.9.4->changedetection.io==0.50.14) (2026.7.22)
Requirement already satisfied: cffi>=1.12 in /usr/local/lib/python3.11/site-packages (from cryptography==44.0.1->changedetection.io==0.50.14) (2.1.1)
Requirement already satisfied: aenum<3.0.0,>=2.2.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (2.2.6)
Requirement already satisfied: appdirs<2.0.0,>=1.4.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (1.4.4)
Requirement already satisfied: ordered_set<5.0.0,>=4.0.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (4.1.0)
Requirement already satisfied: pillow>=9.3 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (12.3.0)
Requirement already satisfied: pyee>=12.0.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (13.0.1)
Requirement already satisfied: tqdm<5.0.0,>=4.42.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (4.70.0)
Requirement already satisfied: typing_extensions>=4.0.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (4.16.0)
Requirement already satisfied: typing_inspect<0.6.0,>=0.5.0 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (0.5.0)
Requirement already satisfied: urllib3<2.0.0,>=1.25.8 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (1.26.20)
Requirement already satisfied: websockets<11.0,>=10.1 in /usr/local/lib/python3.11/site-packages (from pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (10.4)
Requirement already satisfied: attrs>=22.2.0 in /usr/local/lib/python3.11/site-packages (from referencing==0.35.1->changedetection.io==0.50.14) (26.1.0)
Requirement already satisfied: rpds-py>=0.7.0 in /usr/local/lib/python3.11/site-packages (from referencing==0.35.1->changedetection.io==0.50.14) (2026.6.3)
Requirement already satisfied: MarkupSafe>=2.1.1 in /usr/local/lib/python3.11/site-packages (from werkzeug==3.0.6->changedetection.io==0.50.14) (3.0.3)
Requirement already satisfied: python-dateutil in /usr/local/lib/python3.11/site-packages (from feedgen~=0.9->changedetection.io==0.50.14) (2.9.0.post0)
Requirement already satisfied: itsdangerous>=2.1.2 in /usr/local/lib/python3.11/site-packages (from flask~=2.3->changedetection.io==0.50.14) (2.2.0)
Requirement already satisfied: ply in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->changedetection.io==0.50.14) (3.11)
Requirement already satisfied: decorator in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->changedetection.io==0.50.14) (5.3.1)
Requirement already satisfied: six in /usr/local/lib/python3.11/site-packages (from jsonpath-ng~=1.5.3->changedetection.io==0.50.14) (1.17.0)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in /usr/local/lib/python3.11/site-packages (from jsonschema~=4.0->changedetection.io==0.50.14) (2025.9.1)
Requirement already satisfied: iniconfig in /usr/local/lib/python3.11/site-packages (from pytest~=7.2->changedetection.io==0.50.14) (2.3.0)
Requirement already satisfied: packaging in /usr/local/lib/python3.11/site-packages (from pytest~=7.2->changedetection.io==0.50.14) (26.3)
Requirement already satisfied: simple-websocket>=0.10.0 in /usr/local/lib/python3.11/site-packages (from python-engineio~=4.12.0->changedetection.io==0.50.14) (1.1.0)
Requirement already satisfied: bidict>=0.21.0 in /usr/local/lib/python3.11/site-packages (from python-socketio~=5.13.0->changedetection.io==0.50.14) (0.24.1)
Requirement already satisfied: charset_normalizer<4,>=2 in /usr/local/lib/python3.11/site-packages (from requests[socks]->changedetection.io==0.50.14) (3.5.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.11/site-packages (from requests[socks]->changedetection.io==0.50.14) (3.19)
Requirement already satisfied: trio~=0.17 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->changedetection.io==0.50.14) (0.34.0)
Requirement already satisfied: trio-websocket~=0.9 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->changedetection.io==0.50.14) (0.12.2)
Requirement already satisfied: websocket-client~=1.8 in /usr/local/lib/python3.11/site-packages (from selenium~=4.31.0->changedetection.io==0.50.14) (1.9.2)
Requirement already satisfied: sortedcontainers in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->changedetection.io==0.50.14) (2.4.0)
Requirement already satisfied: outcome in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->changedetection.io==0.50.14) (1.3.0.post0)
Requirement already satisfied: sniffio>=1.3.0 in /usr/local/lib/python3.11/site-packages (from trio~=0.17->selenium~=4.31.0->changedetection.io==0.50.14) (1.3.1)
Requirement already satisfied: wsproto>=0.14 in /usr/local/lib/python3.11/site-packages (from trio-websocket~=0.9->selenium~=4.31.0->changedetection.io==0.50.14) (1.3.2)
Requirement already satisfied: mypy-extensions>=0.3.0 in /usr/local/lib/python3.11/site-packages (from typing_inspect<0.6.0,>=0.5.0->pyppeteer-ng==2.0.0rc10->changedetection.io==0.50.14) (1.1.0)
Requirement already satisfied: PySocks!=1.5.7,<2.0,>=1.5.6 in /usr/local/lib/python3.11/site-packages (from urllib3[socks]<3,>=1.26->selenium~=4.31.0->changedetection.io==0.50.14) (1.7.1)
Requirement already satisfied: soupsieve>=1.6.1 in /usr/local/lib/python3.11/site-packages (from beautifulsoup4>=4.0.0->changedetection.io==0.50.14) (2.9.2)
Requirement already satisfied: pycparser in /usr/local/lib/python3.11/site-packages (from cffi>=1.12->cryptography==44.0.1->changedetection.io==0.50.14) (3.0)
Requirement already satisfied: isodate in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.7.2)
Requirement already satisfied: jsonschema-path<0.4.0,>=0.3.1 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.3.4)
Requirement already satisfied: more-itertools in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (11.1.0)
Requirement already satisfied: openapi-schema-validator<0.7.0,>=0.6.0 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.6.3)
Requirement already satisfied: openapi-spec-validator<0.8.0,>=0.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.7.2)
Requirement already satisfied: parse in /usr/local/lib/python3.11/site-packages (from openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (1.22.1)
Requirement already satisfied: pathable<0.5.0,>=0.4.1 in /usr/local/lib/python3.11/site-packages (from jsonschema-path<0.4.0,>=0.3.1->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.4.4)
Requirement already satisfied: rfc3339-validator in /usr/local/lib/python3.11/site-packages (from openapi-schema-validator<0.7.0,>=0.6.0->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (0.1.4)
Requirement already satisfied: lazy-object-proxy<2.0.0,>=1.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-spec-validator<0.8.0,>=0.7.1->openapi-core>=0.19.0->openapi-core[flask]>=0.19.0->changedetection.io==0.50.14) (1.12.0)
Requirement already satisfied: cfgv>=2.0.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->changedetection.io==0.50.14) (3.5.0)
Requirement already satisfied: identify>=1.0.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->changedetection.io==0.50.14) (2.6.19)
Requirement already satisfied: nodeenv>=0.11.1 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->changedetection.io==0.50.14) (1.10.0)
Requirement already satisfied: virtualenv>=20.10.0 in /usr/local/lib/python3.11/site-packages (from pre_commit>=4.2.0->changedetection.io==0.50.14) (21.7.8)
Requirement already satisfied: distlib<1,>=0.3.7 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->changedetection.io==0.50.14) (0.4.3)
Requirement already satisfied: filelock<4,>=3.24.2 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->changedetection.io==0.50.14) (3.32.5)
Requirement already satisfied: platformdirs<5,>=3.9.1 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->changedetection.io==0.50.14) (4.11.7)
Requirement already satisfied: python-discovery>=1.6 in /usr/local/lib/python3.11/site-packages (from virtualenv>=20.10.0->pre_commit>=4.2.0->changedetection.io==0.50.14) (1.6.0)
Requirement already satisfied: h11<1,>=0.16.0 in /usr/local/lib/python3.11/site-packages (from wsproto>=0.14->trio-websocket~=0.9->selenium~=4.31.0->changedetection.io==0.50.14) (0.16.0)
Requirement already satisfied: lxml-html-clean in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (0.4.4)
Requirement already satisfied: rdflib>=6.0.0 in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (7.6.0)
Requirement already satisfied: pyrdfa3 in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (3.6.5)
Requirement already satisfied: mf2py in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (2.0.1)
Requirement already satisfied: w3lib in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (2.4.1)
Requirement already satisfied: html-text>=0.5.1 in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (0.7.1)
Requirement already satisfied: jstyleson in /usr/local/lib/python3.11/site-packages (from extruct->changedetection.io==0.50.14) (0.0.2)
Requirement already satisfied: pyparsing<4,>=2.1.0 in /usr/local/lib/python3.11/site-packages (from rdflib>=6.0.0->extruct->changedetection.io==0.50.14) (3.3.2)
Requirement already satisfied: backports.zstd in /usr/local/lib/python3.11/site-packages (from flask-compress->changedetection.io==0.50.14) (1.7.0)
Requirement already satisfied: aniso8601>=0.82 in /usr/local/lib/python3.11/site-packages (from flask_restful->changedetection.io==0.50.14) (10.0.1)
Requirement already satisfied: zope.event in /usr/local/lib/python3.11/site-packages (from gevent->changedetection.io==0.50.14) (6.2)
Requirement already satisfied: zope.interface in /usr/local/lib/python3.11/site-packages (from gevent->changedetection.io==0.50.14) (8.6)
Requirement already satisfied: arrow in /usr/local/lib/python3.11/site-packages (from jinja2-time->changedetection.io==0.50.14) (1.4.0)
Requirement already satisfied: rapidfuzz<4.0.0,>=3.9.0 in /usr/local/lib/python3.11/site-packages (from levenshtein->changedetection.io==0.50.14) (3.14.6)
Requirement already satisfied: html5lib<2.0,>=1.1 in /usr/local/lib/python3.11/site-packages (from mf2py->extruct->changedetection.io==0.50.14) (1.1)
Requirement already satisfied: webencodings in /usr/local/lib/python3.11/site-packages (from html5lib<2.0,>=1.1->mf2py->extruct->changedetection.io==0.50.14) (0.6.1)
Requirement already satisfied: et-xmlfile in /usr/local/lib/python3.11/site-packages (from openpyxl->changedetection.io==0.50.14) (2.0.0)
Requirement already satisfied: oauthlib>=3.0.0 in /usr/local/lib/python3.11/site-packages (from requests-oauthlib->apprise==1.9.4->changedetection.io==0.50.14) (3.3.1)
Building wheels for collected packages: changedetection.io
  Building editable for changedetection.io (pyproject.toml): started
  Building editable for changedetection.io (pyproject.toml): finished with status 'done'
  Created wheel for changedetection.io: filename=changedetection_io-0.50.14-0.editable-py3-none-any.whl size=11609 sha256=b9d29b12f807c4a0549af03d6347a418fdbf678324c0ea9c0ff4b73de4cdbc7e
  Stored in directory: /tmp/pip-ephem-wheel-cache-rqxf31zp/wheels/b0/b8/7d/94f16beb2ba1aa27ae8ed824305dd705ced62c75374aa1654e
Successfully built changedetection.io
Installing collected packages: changedetection.io
  Attempting uninstall: changedetection.io
    Found existing installation: changedetection.io 0.50.14
    Uninstalling changedetection.io-0.50.14:
      Successfully uninstalled changedetection.io-0.50.14
Successfully installed changedetection.io-0.50.14
Requirement already satisfied: pytest in /usr/local/lib/python3.11/site-packages (7.4.4)
Requirement already satisfied: pytest-flask in /usr/local/lib/python3.11/site-packages (1.3.0)
Requirement already satisfied: iniconfig in /usr/local/lib/python3.11/site-packages (from pytest) (2.3.0)
Requirement already satisfied: packaging in /usr/local/lib/python3.11/site-packages (from pytest) (26.3)
Requirement already satisfied: pluggy<2.0,>=0.12 in /usr/local/lib/python3.11/site-packages (from pytest) (1.6.0)
Requirement already satisfied: Flask in /usr/local/lib/python3.11/site-packages (from pytest-flask) (2.3.3)
Requirement already satisfied: Werkzeug in /usr/local/lib/python3.11/site-packages (from pytest-flask) (3.0.6)
Requirement already satisfied: Jinja2>=3.1.2 in /usr/local/lib/python3.11/site-packages (from Flask->pytest-flask) (3.1.6)
Requirement already satisfied: itsdangerous>=2.1.2 in /usr/local/lib/python3.11/site-packages (from Flask->pytest-flask) (2.2.0)
Requirement already satisfied: click>=8.1.3 in /usr/local/lib/python3.11/site-packages (from Flask->pytest-flask) (8.5.0)
Requirement already satisfied: blinker>=1.6.2 in /usr/local/lib/python3.11/site-packages (from Flask->pytest-flask) (1.9.0)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.11/site-packages (from Jinja2>=3.1.2->Flask->pytest-flask) (3.0.3)
Requirement already satisfied: typing_extensions in /usr/local/lib/python3.11/site-packages (4.16.0)
Requirement already satisfied: openapi-core<0.20,>=0.19 in /usr/local/lib/python3.11/site-packages (0.19.5)
Requirement already satisfied: isodate in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (0.7.2)
Requirement already satisfied: jsonschema<5.0.0,>=4.18.0 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (4.24.1)
Requirement already satisfied: jsonschema-path<0.4.0,>=0.3.1 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (0.3.4)
Requirement already satisfied: more-itertools in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (11.1.0)
Requirement already satisfied: openapi-schema-validator<0.7.0,>=0.6.0 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (0.6.3)
Requirement already satisfied: openapi-spec-validator<0.8.0,>=0.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (0.7.2)
Requirement already satisfied: parse in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (1.22.1)
Requirement already satisfied: typing-extensions<5.0.0,>=4.8.0 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (4.16.0)
Requirement already satisfied: werkzeug<3.1.2 in /usr/local/lib/python3.11/site-packages (from openapi-core<0.20,>=0.19) (3.0.6)
Requirement already satisfied: attrs>=22.2.0 in /usr/local/lib/python3.11/site-packages (from jsonschema<5.0.0,>=4.18.0->openapi-core<0.20,>=0.19) (26.1.0)
Requirement already satisfied: jsonschema-specifications>=2023.03.6 in /usr/local/lib/python3.11/site-packages (from jsonschema<5.0.0,>=4.18.0->openapi-core<0.20,>=0.19) (2025.9.1)
Requirement already satisfied: referencing>=0.28.4 in /usr/local/lib/python3.11/site-packages (from jsonschema<5.0.0,>=4.18.0->openapi-core<0.20,>=0.19) (0.35.1)
Requirement already satisfied: rpds-py>=0.7.1 in /usr/local/lib/python3.11/site-packages (from jsonschema<5.0.0,>=4.18.0->openapi-core<0.20,>=0.19) (2026.6.3)
Requirement already satisfied: PyYAML>=5.1 in /usr/local/lib/python3.11/site-packages (from jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (6.0.3)
Requirement already satisfied: pathable<0.5.0,>=0.4.1 in /usr/local/lib/python3.11/site-packages (from jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (0.4.4)
Requirement already satisfied: requests<3.0.0,>=2.31.0 in /usr/local/lib/python3.11/site-packages (from jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (2.34.2)
Requirement already satisfied: rfc3339-validator in /usr/local/lib/python3.11/site-packages (from openapi-schema-validator<0.7.0,>=0.6.0->openapi-core<0.20,>=0.19) (0.1.4)
Requirement already satisfied: lazy-object-proxy<2.0.0,>=1.7.1 in /usr/local/lib/python3.11/site-packages (from openapi-spec-validator<0.8.0,>=0.7.1->openapi-core<0.20,>=0.19) (1.12.0)
Requirement already satisfied: charset_normalizer<4,>=2 in /usr/local/lib/python3.11/site-packages (from requests<3.0.0,>=2.31.0->jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (3.5.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.11/site-packages (from requests<3.0.0,>=2.31.0->jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (3.19)
Requirement already satisfied: urllib3<3,>=1.26 in /usr/local/lib/python3.11/site-packages (from requests<3.0.0,>=2.31.0->jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (1.26.20)
Requirement already satisfied: certifi>=2023.5.7 in /usr/local/lib/python3.11/site-packages (from requests<3.0.0,>=2.31.0->jsonschema-path<0.4.0,>=0.3.1->openapi-core<0.20,>=0.19) (2026.7.22)
Requirement already satisfied: MarkupSafe>=2.1.1 in /usr/local/lib/python3.11/site-packages (from werkzeug<3.1.2->openapi-core<0.20,>=0.19) (3.0.3)
Requirement already satisfied: six in /usr/local/lib/python3.11/site-packages (from rfc3339-validator->openapi-schema-validator<0.7.0,>=0.6.0->openapi-core<0.20,>=0.19) (1.17.0)
+ cd /home/changedetection.io/changedetectionio
+ TARGET='tests/test_add_replace_remove_filter.py tests/test_backend.py tests/test_basic_socketio.py tests/test_block_while_text_present.py tests/test_conditions.py tests/test_css_selector.py tests/test_element_removal.py tests/test_errorhandling.py tests/test_extract_regex.py tests/test_ignore.py tests/test_ignore_text.py tests/test_ignorehyperlinks.py tests/test_ignorestatuscode.py tests/test_ignorewhitespace.py tests/test_jinja2.py tests/test_jsonpath_jq_selector.py tests/test_nonrenderable_pages.py tests/test_preview_endpoints.py tests/test_restock_itemprop.py tests/test_source.py tests/test_trigger.py tests/test_trigger_regex.py tests/test_trigger_regex_with_filter.py tests/test_ui.py tests/test_unique_lines.py tests/test_xpath_selector.py'
+ ran=0
+ for f in $TARGET
+ '[' -e tests/test_add_replace_remove_filter.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_add_replace_remove_filter.py ====='
===== PYTEST FILE: tests/test_add_replace_remove_filter.py =====
+ timeout -k 30 240 python -m pytest tests/test_add_replace_remove_filter.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_add_replace_remove_filter.py ..                               [100%]

=============================== warnings summary ===============================
html_tools.py:437
  /home/changedetection.io/changedetectionio/html_tools.py:437: DeprecationWarning: invalid escape sequence '\['
    pattern = '<!\[CDATA\[(\s*(?:.(?<!\]\]>)\s*)*)\]\]>'

html_tools.py:501
  /home/changedetection.io/changedetectionio/html_tools.py:501: DeprecationWarning: invalid escape sequence '\s'
    content = re.sub('<!--\s+-->', '', content)

flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_add_replace_remove_filter.py::test_check_removed_line_contains_trigger
  /home/changedetection.io/changedetectionio/blueprint/backups/__init__.py:124: DeprecationWarning: invalid escape sequence '\d'
    backup_filename_regex = BACKUP_FILENAME_FORMAT.format("\d+")

tests/test_add_replace_remove_filter.py::test_check_add_line_contains_trigger
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_add_replace_remove_filter.py::test_check_removed_line_contains_trigger
PASSED tests/test_add_replace_remove_filter.py::test_check_add_line_contains_trigger
======================== 2 passed, 5 warnings in 15.23s ========================
2026-09-05 13:36:49.940 | CRITICAL | changedetectionio.store:save_datastore:445 - Shutting down datastore thread
+ for f in $TARGET
+ '[' -e tests/test_backend.py ']'
+ ran=1
===== PYTEST FILE: tests/test_backend.py =====
+ echo '===== PYTEST FILE: tests/test_backend.py ====='
+ timeout -k 30 240 python -m pytest tests/test_backend.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_backend.py ...                                                [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_backend.py::test_check_basic_change_detection_functionality
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_backend.py::test_inscriptus
PASSED tests/test_backend.py::test_check_basic_change_detection_functionality
PASSED tests/test_backend.py::test_non_text_mime_or_downloads
======================== 3 passed, 2 warnings in 10.69s ========================
+ for f in $TARGET
+ '[' -e tests/test_basic_socketio.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_basic_socketio.py ====='
+ timeout -k 30 240 python -m pytest tests/test_basic_socketio.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_basic_socketio.py =====
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_basic_socketio.py F                                           [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_basic_socketio.py::test_everything
  /usr/local/lib/python3.11/site-packages/flask/app.py:1883: UserWarning: Current server name 'localhost' doesn't match configured server name 'localhost.localdomain:5005'
    return self.url_map.bind_to_environ(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED tests/test_basic_socketio.py::test_everything - AssertionError: Got general stats update event
assert False
======================== 1 failed, 2 warnings in 13.19s ========================
+ true
+ for f in $TARGET
+ '[' -e tests/test_block_while_text_present.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_block_while_text_present.py ====='
===== PYTEST FILE: tests/test_block_while_text_present.py =====
+ timeout -k 30 240 python -m pytest tests/test_block_while_text_present.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_block_while_text_present.py .                                 [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_block_while_text_present.py::test_check_block_changedetection_text_NOT_present
tests/test_block_while_text_present.py::test_check_block_changedetection_text_NOT_present
tests/test_block_while_text_present.py::test_check_block_changedetection_text_NOT_present
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_block_while_text_present.py::test_check_block_changedetection_text_NOT_present
======================== 1 passed, 4 warnings in 5.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_conditions.py ']'
+ ran=1
===== PYTEST FILE: tests/test_conditions.py =====
+ echo '===== PYTEST FILE: tests/test_conditions.py ====='
+ timeout -k 30 240 python -m pytest tests/test_conditions.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 4 items

tests/test_conditions.py ....                                            [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_conditions.py:107
  /home/changedetection.io/changedetectionio/tests/test_conditions.py:107: DeprecationWarning: invalid escape sequence '\d'
    "conditions-5-value": "\d",

tests/test_conditions.py::test_wordcount_conditions_plugin
tests/test_conditions.py::test_wordcount_conditions_plugin
tests/test_conditions.py::test_wordcount_conditions_plugin
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_conditions.py::test_conditions_with_text_and_number
PASSED tests/test_conditions.py::test_condition_validate_rule_row
PASSED tests/test_conditions.py::test_wordcount_conditions_plugin
PASSED tests/test_conditions.py::test_lev_conditions_plugin
======================== 4 passed, 5 warnings in 14.19s ========================
+ for f in $TARGET
+ '[' -e tests/test_css_selector.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_css_selector.py ====='
===== PYTEST FILE: tests/test_css_selector.py =====
+ timeout -k 30 240 python -m pytest tests/test_css_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 4 items

tests/test_css_selector.py ....                                          [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_css_selector.py::test_check_markup_include_filters_restriction
tests/test_css_selector.py::test_check_markup_include_filters_restriction
tests/test_css_selector.py::test_check_markup_include_filters_restriction
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_css_selector.py::test_include_filters_output
PASSED tests/test_css_selector.py::test_check_markup_include_filters_restriction
PASSED tests/test_css_selector.py::test_check_multiple_filters
PASSED tests/test_css_selector.py::test_filter_is_empty_help_suggestion
======================== 4 passed, 4 warnings in 17.19s ========================
+ for f in $TARGET
+ '[' -e tests/test_element_removal.py ']'
+ ran=1
===== PYTEST FILE: tests/test_element_removal.py =====
+ echo '===== PYTEST FILE: tests/test_element_removal.py ====='
+ timeout -k 30 240 python -m pytest tests/test_element_removal.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_element_removal.py ...                                        [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_element_removal.py::test_element_removal_full
tests/test_element_removal.py::test_element_removal_full
tests/test_element_removal.py::test_element_removal_full
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_element_removal.py::test_element_removal_output
PASSED tests/test_element_removal.py::test_element_removal_full
PASSED tests/test_element_removal.py::test_element_removal_nth_offset_no_shift
======================== 3 passed, 4 warnings in 9.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_errorhandling.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_errorhandling.py ====='
===== PYTEST FILE: tests/test_errorhandling.py =====
+ timeout -k 30 240 python -m pytest tests/test_errorhandling.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_errorhandling.py ...                                          [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_errorhandling.py::test_http_error_handler
PASSED tests/test_errorhandling.py::test_DNS_errors
PASSED tests/test_errorhandling.py::test_low_level_errors_clear_correctly
======================== 3 passed, 1 warning in 14.19s =========================
+ for f in $TARGET
+ '[' -e tests/test_extract_regex.py ']'
+ ran=1
===== PYTEST FILE: tests/test_extract_regex.py =====
+ echo '===== PYTEST FILE: tests/test_extract_regex.py ====='
+ timeout -k 30 240 python -m pytest tests/test_extract_regex.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_extract_regex.py ...                                          [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_extract_regex.py:149
  /home/changedetection.io/changedetectionio/tests/test_extract_regex.py:149: DeprecationWarning: invalid escape sequence '\d'
    'extract_text': '/\d+ online/\r\n/\d+ guests/\r\n/somecase insensitive \d+/i\r\n/somecase insensitive (345\d)/i\r\n/issue1828.+?2022/i',

tests/test_extract_regex.py:225
  /home/changedetection.io/changedetectionio/tests/test_extract_regex.py:225: DeprecationWarning: invalid escape sequence '\d'
    data={"extract_text": '/something bad\d{3/XYZ',

tests/test_extract_regex.py::test_regex_error_handling
tests/test_extract_regex.py::test_regex_error_handling
tests/test_extract_regex.py::test_regex_error_handling
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_extract_regex.py::test_check_filter_multiline
PASSED tests/test_extract_regex.py::test_check_filter_and_regex_extract
PASSED tests/test_extract_regex.py::test_regex_error_handling
======================== 3 passed, 6 warnings in 6.69s =========================
+ for f in $TARGET
+ '[' -e tests/test_ignore.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignore.py ====='
===== PYTEST FILE: tests/test_ignore.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignore.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_ignore.py ..                                                  [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ignore.py:49
  /home/changedetection.io/changedetectionio/tests/test_ignore.py:49: DeprecationWarning: invalid escape sequence '\ '
    assert b'/oh\ yeah\ \d+/' in res.data

tests/test_ignore.py::test_ignore
tests/test_ignore.py::test_ignore
tests/test_ignore.py::test_ignore
tests/test_ignore.py::test_strip_ignore_lines
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignore.py::test_ignore
PASSED tests/test_ignore.py::test_strip_ignore_lines
======================== 2 passed, 6 warnings in 2.68s =========================
+ for f in $TARGET
+ '[' -e tests/test_ignore_text.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignore_text.py ====='
+ timeout -k 30 240 python -m pytest tests/test_ignore_text.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_ignore_text.py =====
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 4 items

tests/test_ignore_text.py ....                                           [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ignore_text.py:263
  /home/changedetection.io/changedetectionio/tests/test_ignore_text.py:263: DeprecationWarning: invalid escape sequence '\?'
    _run_test_global_ignore(client, as_source=True, extra_ignore='/\?v=\d/')

tests/test_ignore_text.py::test_check_ignore_text_functionality
tests/test_ignore_text.py::test_check_ignore_text_functionality
tests/test_ignore_text.py::test_check_ignore_text_functionality
tests/test_ignore_text.py::test_check_global_ignore_text_functionality
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignore_text.py::test_strip_text_func
PASSED tests/test_ignore_text.py::test_check_ignore_text_functionality
PASSED tests/test_ignore_text.py::test_check_global_ignore_text_functionality
PASSED tests/test_ignore_text.py::test_check_global_ignore_text_functionality_as_source
======================== 4 passed, 6 warnings in 12.19s ========================
+ for f in $TARGET
+ '[' -e tests/test_ignorehyperlinks.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorehyperlinks.py ====='
===== PYTEST FILE: tests/test_ignorehyperlinks.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignorehyperlinks.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_ignorehyperlinks.py .                                         [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ignorehyperlinks.py::test_render_anchor_tag_content_true
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorehyperlinks.py::test_render_anchor_tag_content_true
======================== 1 passed, 2 warnings in 5.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_ignorestatuscode.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorestatuscode.py ====='
===== PYTEST FILE: tests/test_ignorestatuscode.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignorestatuscode.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_ignorestatuscode.py ..                                        [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ignorestatuscode.py::test_normal_page_check_works_with_ignore_status_code
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorestatuscode.py::test_normal_page_check_works_with_ignore_status_code
PASSED tests/test_ignorestatuscode.py::test_403_page_check_works_with_ignore_status_code
======================== 2 passed, 2 warnings in 9.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_ignorewhitespace.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ignorewhitespace.py ====='
===== PYTEST FILE: tests/test_ignorewhitespace.py =====
+ timeout -k 30 240 python -m pytest tests/test_ignorewhitespace.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_ignorewhitespace.py .                                         [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ignorewhitespace.py::test_check_ignore_whitespace
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ignorewhitespace.py::test_check_ignore_whitespace
======================== 1 passed, 2 warnings in 11.18s ========================
+ for f in $TARGET
+ '[' -e tests/test_jinja2.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_jinja2.py ====='
===== PYTEST FILE: tests/test_jinja2.py =====
+ timeout -k 30 240 python -m pytest tests/test_jinja2.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_jinja2.py ..                                                  [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_jinja2.py: 10 warnings
  /home/changedetection.io/changedetectionio/model/Watch.py:92: DeprecationWarning: 'flask.Markup' is deprecated and will be removed in Flask 2.4. Import 'markupsafe.Markup' instead.
    from flask import (

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_jinja2.py::test_jinja2_in_url_query
PASSED tests/test_jinja2.py::test_jinja2_security_url_query
======================== 2 passed, 11 warnings in 2.68s ========================
+ for f in $TARGET
+ '[' -e tests/test_jsonpath_jq_selector.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_jsonpath_jq_selector.py ====='
+ timeout -k 30 240 python -m pytest tests/test_jsonpath_jq_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_jsonpath_jq_selector.py =====
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 15 items

tests/test_jsonpath_jq_selector.py ...............                       [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_jsonpath_jq_selector.py:5
tests/test_jsonpath_jq_selector.py:5
  /home/changedetection.io/changedetectionio/tests/test_jsonpath_jq_selector.py:5: DeprecationWarning: 'flask.escape' is deprecated and will be removed in Flask 2.4. Import 'markupsafe.escape' instead.
    from flask import url_for, escape

tests/test_jsonpath_jq_selector.py::test_check_jsonpath_filter
tests/test_jsonpath_jq_selector.py::test_check_jsonpath_filter
tests/test_jsonpath_jq_selector.py::test_check_jsonpath_filter
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_jsonpath_jq_selector.py::test_unittest_inline_html_extract
PASSED tests/test_jsonpath_jq_selector.py::test_unittest_inline_extract_body
PASSED tests/test_jsonpath_jq_selector.py::test_check_json_without_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jsonpath_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jq_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jqraw_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jsonpath_filter_bool_val
PASSED tests/test_jsonpath_jq_selector.py::test_check_jq_filter_bool_val
PASSED tests/test_jsonpath_jq_selector.py::test_check_jqraw_filter_bool_val
PASSED tests/test_jsonpath_jq_selector.py::test_ignore_json_order
PASSED tests/test_jsonpath_jq_selector.py::test_correct_header_detect
PASSED tests/test_jsonpath_jq_selector.py::test_check_jsonpath_ext_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jq_ext_filter
PASSED tests/test_jsonpath_jq_selector.py::test_check_jqraw_ext_filter
PASSED tests/test_jsonpath_jq_selector.py::test_jsonpath_BOM_utf8
======================= 15 passed, 6 warnings in 53.70s ========================
+ for f in $TARGET
+ '[' -e tests/test_nonrenderable_pages.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_nonrenderable_pages.py ====='
===== PYTEST FILE: tests/test_nonrenderable_pages.py =====
+ timeout -k 30 240 python -m pytest tests/test_nonrenderable_pages.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_nonrenderable_pages.py .                                      [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_nonrenderable_pages.py::test_check_basic_change_detection_functionality
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_nonrenderable_pages.py::test_check_basic_change_detection_functionality
======================== 1 passed, 2 warnings in 6.68s =========================
2026-09-05 13:40:13.482 | CRITICAL | changedetectionio.store:save_datastore:445 - Shutting down datastore thread
+ for f in $TARGET
+ '[' -e tests/test_preview_endpoints.py ']'
+ ran=1
===== PYTEST FILE: tests/test_preview_endpoints.py =====
+ echo '===== PYTEST FILE: tests/test_preview_endpoints.py ====='
+ timeout -k 30 240 python -m pytest tests/test_preview_endpoints.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item / 1 deselected / 0 selected

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 1 deselected, 1 warning in 0.01s =======================
+ true
+ for f in $TARGET
+ '[' -e tests/test_restock_itemprop.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_restock_itemprop.py ====='
+ timeout -k 30 240 python -m pytest tests/test_restock_itemprop.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_restock_itemprop.py =====
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 8 items

tests/test_restock_itemprop.py ........                                  [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_restock_itemprop.py::test_change_with_notification_values
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_restock_itemprop.py::test_restock_itemprop_basic
PASSED tests/test_restock_itemprop.py::test_itemprop_price_change
PASSED tests/test_restock_itemprop.py::test_restock_itemprop_minmax
PASSED tests/test_restock_itemprop.py::test_restock_itemprop_with_tag
PASSED tests/test_restock_itemprop.py::test_itemprop_percent_threshold
PASSED tests/test_restock_itemprop.py::test_change_with_notification_values
PASSED tests/test_restock_itemprop.py::test_data_sanity
PASSED tests/test_restock_itemprop.py::test_special_prop_examples
=================== 8 passed, 2 warnings in 64.21s (0:01:04) ===================
+ for f in $TARGET
+ '[' -e tests/test_source.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_source.py ====='
===== PYTEST FILE: tests/test_source.py =====
+ timeout -k 30 240 python -m pytest tests/test_source.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 2 items

tests/test_source.py ..                                                  [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_source.py::test_check_basic_change_detection_functionality_source
PASSED tests/test_source.py::test_check_ignore_elements
========================= 2 passed, 1 warning in 9.68s =========================
+ for f in $TARGET
+ '[' -e tests/test_trigger.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_trigger.py ====='
===== PYTEST FILE: tests/test_trigger.py =====
+ timeout -k 30 240 python -m pytest tests/test_trigger.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger.py .                                                  [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_trigger.py::test_trigger_functionality
tests/test_trigger.py::test_trigger_functionality
tests/test_trigger.py::test_trigger_functionality
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_trigger.py::test_trigger_functionality
======================== 1 passed, 4 warnings in 3.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_trigger_regex.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_trigger_regex.py ====='
===== PYTEST FILE: tests/test_trigger_regex.py =====
+ timeout -k 30 240 python -m pytest tests/test_trigger_regex.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger_regex.py .                                            [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_trigger_regex.py:50
  /home/changedetection.io/changedetectionio/tests/test_trigger_regex.py:50: DeprecationWarning: invalid escape sequence '\d'
    data={"trigger_text": '/something \d{3}/',

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_trigger_regex.py::test_trigger_regex_functionality
======================== 1 passed, 2 warnings in 4.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_trigger_regex_with_filter.py ']'
+ ran=1
===== PYTEST FILE: tests/test_trigger_regex_with_filter.py =====
+ echo '===== PYTEST FILE: tests/test_trigger_regex_with_filter.py ====='
+ timeout -k 30 240 python -m pytest tests/test_trigger_regex_with_filter.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 1 item

tests/test_trigger_regex_with_filter.py .                                [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_trigger_regex_with_filter.py::test_trigger_regex_functionality_with_filter
======================== 1 passed, 1 warning in 15.18s =========================
+ for f in $TARGET
+ '[' -e tests/test_ui.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_ui.py ====='
===== PYTEST FILE: tests/test_ui.py =====
+ timeout -k 30 240 python -m pytest tests/test_ui.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 5 items

tests/test_ui.py ....F                                                   [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_ui.py::test_recheck_time_field_validation_global_settings
tests/test_ui.py::test_recheck_time_field_validation_single_watch
tests/test_ui.py::test_recheck_time_field_validation_single_watch
tests/test_ui.py::test_recheck_time_field_validation_single_watch
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_ui.py::test_recheck_time_field_validation_global_settings
PASSED tests/test_ui.py::test_recheck_time_field_validation_single_watch
PASSED tests/test_ui.py::test_checkbox_open_diff_in_new_tab
PASSED tests/test_ui.py::test_page_title_listing_behaviour
FAILED tests/test_ui.py::test_ui_viewed_unread_flag - assert b'<span id="unread-tab-counter">2</span>' in b'<!DOCTYPE html>\n<html lang="en" data-darkmode="false">\n\n  <head>\n    <meta charset="utf-8" >\n    <meta name="vi...n></div>\n    <div id="realtime-conn-error" style="display:none">Real-time updates offline</div>\n  </body>\n\n</html>'
 +  where b'<!DOCTYPE html>\n<html lang="en" data-darkmode="false">\n\n  <head>\n    <meta charset="utf-8" >\n    <meta name="vi...n></div>\n    <div id="realtime-conn-error" style="display:none">Real-time updates offline</div>\n  </body>\n\n</html>' = <WrapperTestResponse 30983 bytes [200 OK]>.data
=================== 1 failed, 4 passed, 5 warnings in 7.70s ====================
+ true
+ for f in $TARGET
+ '[' -e tests/test_unique_lines.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_unique_lines.py ====='
+ timeout -k 30 240 python -m pytest tests/test_unique_lines.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
===== PYTEST FILE: tests/test_unique_lines.py =====
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 3 items

tests/test_unique_lines.py ...                                           [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_unique_lines.py::test_unique_lines_functionality
PASSED tests/test_unique_lines.py::test_sort_lines_functionality
PASSED tests/test_unique_lines.py::test_extra_filters
========================= 3 passed, 1 warning in 8.69s =========================
+ for f in $TARGET
+ '[' -e tests/test_xpath_selector.py ']'
+ ran=1
+ echo '===== PYTEST FILE: tests/test_xpath_selector.py ====='
===== PYTEST FILE: tests/test_xpath_selector.py =====
+ timeout -k 30 240 python -m pytest tests/test_xpath_selector.py -k 'not webdriver and not pdf' -p no:cacheprovider -rA --tb=no -o log_cli=false --continue-on-collection-errors
============================= test session starts ==============================
platform linux -- Python 3.11.16, pytest-7.4.4, pluggy-1.6.0
rootdir: /home/changedetection.io/changedetectionio
configfile: pytest.ini
plugins: flask-1.3.0
collected 13 items

tests/test_xpath_selector.py .............                               [100%]

=============================== warnings summary ===============================
flask_app.py:89
  /home/changedetection.io/changedetectionio/flask_app.py:89: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    default_locale = locale.getdefaultlocale()

tests/test_xpath_selector.py::test_xpath_validation
tests/test_xpath_selector.py::test_xpath_validation
tests/test_xpath_selector.py::test_xpath_validation
  /usr/local/lib/python3.11/site-packages/jinja2/lexer.py:654: DeprecationWarning: invalid escape sequence '\d'
    .decode("unicode-escape")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
PASSED tests/test_xpath_selector.py::test_check_xpath_filter_utf8
PASSED tests/test_xpath_selector.py::test_check_xpath_text_function_utf8
PASSED tests/test_xpath_selector.py::test_check_markup_xpath_filter_restriction
PASSED tests/test_xpath_selector.py::test_xpath_validation
PASSED tests/test_xpath_selector.py::test_xpath23_prefix_validation
PASSED tests/test_xpath_selector.py::test_xpath1_lxml
PASSED tests/test_xpath_selector.py::test_xpath1_validation
PASSED tests/test_xpath_selector.py::test_check_with_prefix_include_filters
PASSED tests/test_xpath_selector.py::test_various_rules
PASSED tests/test_xpath_selector.py::test_xpath_20
PASSED tests/test_xpath_selector.py::test_xpath_20_function_count
PASSED tests/test_xpath_selector.py::test_xpath_20_function_count2
PASSED tests/test_xpath_selector.py::test_xpath_20_function_string_join_matches
======================= 13 passed, 4 warnings in 38.20s ========================
+ '[' 1 = 0 ']'
