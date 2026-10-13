# Qwalora Ranger - board2 target image.
# Pinned by digest via `qrange pin`. The tag here is a readable fallback; CI and
# the committed lock file carry the digest that actually runs.
FROM python:3.12-slim@sha256:REPLACE_WITH_PINNED_DIGEST

# non-root from the start; the compose also enforces user 10001
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin ranger
WORKDIR /srv
COPY app.py /srv/app.py

USER 10001:10001
EXPOSE 8080
ENV PORT=8080 QW_ACCESS_LOG=/tmp/access.log
# no shell form -> no implicit /bin/sh, smaller attack surface
ENTRYPOINT ["python3", "/srv/app.py"]
