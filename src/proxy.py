import http
import os

import requests
from flask import Flask, Response, request

from hidden import TOKENS

app = Flask(__name__)

EXTERNAL_PORT = int(os.environ.get("EXTERNAL_PORT", "12345"))

# reverse proxy
@app.route("/rpc/<path:path>", methods=["GET", "POST"])
def proxy(path):
    token = path
    if token not in TOKENS:
        return "", http.HTTPStatus.NOT_FOUND
    index = TOKENS.index(token)
    port = 20000 + index
    url = f"http://127.0.0.1:{port}"

    headers = {key: value for (key, value) in request.headers if key != "Host"}

    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            stream=True,
        )
    except requests.exceptions.ConnectionError:
        return "Container not launched", http.HTTPStatus.BAD_REQUEST
    except:
        return "Container error", http.HTTPStatus.SERVICE_UNAVAILABLE

    # here exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1
    # ref. https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in response.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    response = Response(
        response=response.content,
        status=response.status_code,
        headers=headers,
    )

    return response, http.HTTPStatus.OK


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=EXTERNAL_PORT, debug=False)
