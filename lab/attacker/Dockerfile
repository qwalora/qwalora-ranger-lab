# Qwalora Ranger - attacker workstation.
# Minimal offensive toolbox on the internal (no-egress) network. You exec in
# here to run the exploit by hand; CI runs the same script headless.
FROM python:3.12-slim@sha256:REPLACE_WITH_PINNED_DIGEST

RUN apt-get update \
 && apt-get install -y --no-install-recommends curl jq nmap ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/toolbox
COPY toolbox/ /opt/toolbox/
ENV TARGET=http://target:8080
# attacker stays interactive; compose sets `command: sleep infinity`
CMD ["sleep", "infinity"]
