import base64
import json
import os
from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/serde', methods=['POST'])
def serde():
    try:
        data = request.get_json()

        if not data or 'payload' not in data or 'opts' not in data:
            return Response('Missing required fields', status=400)

        payload_b64 = data['payload']
        opts_str = data['opts']

        print(f'[REQUEST] payload: {payload_b64}')
        print(f'[REQUEST] opts: {opts_str}')

        try:
            payload_bytes = base64.b64decode(payload_b64)
        except Exception as e:
            print(f'[ERROR] Failed to decode payload: {e}')
            return Response('Invalid Base64 payload', status=400)

        try:
            opts = json.loads(opts_str)
            device_code = opts.get('device_code')
            if device_code is None:
                return Response('Missing device_code in opts', status=400)
            if not isinstance(device_code, int) or device_code < 0 or device_code > 255:
                return Response('device_code must be an integer between 0 and 255', status=400)
        except Exception as e:
            print(f'[ERROR] Failed to parse opts: {e}')
            return Response('Invalid opts JSON', status=400)

        payload_list = list(payload_bytes)
        payload_list[1] = device_code
        modified_bytes = bytes(payload_list)
        modified_b64 = base64.b64encode(modified_bytes).decode('utf-8')

        print(f'[RESPONSE] result: {modified_b64}')

        return Response(modified_b64, status=200, content_type='text/plain')

    except Exception as e:
        print(f'[ERROR] Internal error: {e}')
        return Response('Internal server error', status=500)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9500))
    print(f'[INFO] Starting server on 0.0.0.0:{port}')
    app.run(host='0.0.0.0', port=port)
