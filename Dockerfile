FROM python:3-alpine
LABEL org.opencontainers.image.title="x2gbfs"
LABEL org.opencontainers.image.description="Library & command line to generate GBFS feeds from various sharing providers."
LABEL org.opencontainers.image.authors="Holger Bruch <hb@mfdz.de>, MobiData-BW IPL contributors <mobidata-bw@nvbw.de>"
LABEL org.opencontainers.image.documentation="https://github.com/mobidata-bw/x2gbfs"
LABEL org.opencontainers.image.source="https://github.com/mobidata-bw/x2gbfs"
LABEL org.opencontainers.image.licenses="(EUPL-1.2)"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY x2gbfs/ ./x2gbfs/
COPY config/ ./config/

ENTRYPOINT [ "python", "-m", "x2gbfs.x2gbfs" ]
