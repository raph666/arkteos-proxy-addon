ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3

COPY arkteos_proxy.py /arkteos_proxy.py
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
