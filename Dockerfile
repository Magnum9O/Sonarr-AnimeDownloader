FROM --platform=$BUILDPLATFORM python:3.13-alpine

LABEL maintainer="MainKronos"

RUN apk update && \
	apk upgrade && \
	apk add --no-cache curl ffmpeg rtmpdump tzdata build-base musl-locales musl-locales-lang && \
	rm -rf /var/cache/apk/*

RUN addgroup --gid 1000 dockeruser && \
	adduser --uid 1000 -D -G dockeruser dockeruser

RUN pip3 install --no-cache-dir --upgrade pip

RUN pip3 install config --upgrade --no-cache-dir

COPY src/requirements.txt /tmp/

# Fix ARMv7: installa prima dipendenze critiche, poi uvicorn senza standard
RUN pip3 install --no-cache-dir --only-binary=all \
        httptools uvloop watchfiles uvicorn || \
    pip3 install --no-cache-dir uvicorn && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /downloads && \
	mkdir /src

WORKDIR /src

COPY src/ /src/

RUN chmod 777 /downloads -R && \
	chmod 777 /src -R

RUN gcc /src/start.c -o /start.bin && \
	rm /src/start.c && \
	chown root:root /start.bin && \
	chmod 6751 /start.bin

ENV LANG=it_IT.UTF-8 \
    LC_ALL=it_IT.UTF-8 \
    FLASK_DEBUG=production \
    PIP_ROOT_USER_ACTION=ignore \
    USER_NAME=dockeruser

ARG set_version="dev"
ENV VERSION=$set_version

EXPOSE 5000

VOLUME [ "/downloads", "/src/script", "/src/database" ]

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:5000 || exit 1

CMD ["/start.bin"]
