FROM python:3.11-alpine

ARG USER_UID
ARG USER_GID

RUN apk update && apk add ffmpeg
RUN addgroup -g ${USER_GID:-101} -S sayu \
 && adduser -S -D -H -u ${USER_UID:-101} -h /app -s /sbin/nologin -G sayu -g sayu sayu \
 && mkdir -p /app \
 && chown sayu:sayu -R /app
 RUN pip install poetry

USER sayu
WORKDIR /app
COPY pyproject.toml .
RUN poetry install
COPY . .

USER root
RUN chown sayu:sayu -R /app
USER sayu
CMD ["poetry", "run", "python", "-m", "source"]
