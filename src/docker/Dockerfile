FROM ethereum/client-go:v1.13.0

COPY config /config
COPY data /data
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8545

ENTRYPOINT ["/entrypoint.sh"]
