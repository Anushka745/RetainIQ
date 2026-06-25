"""
utils/api_client.py
Thin wrapper around `requests` for calling the RetainIQ FastAPI backend.
Reads the JWT token from Streamlit session_state and attaches it as a Bearer header.
"""

import os
from typing import Any, Dict, Optional

import requests
import streamlit as st

BACKEND_URL = os.getenv("RETAINIQ_BACKEND_URL", "http://localhost:8000")
TIMEOUT = 15


def _headers() -> Dict[str, str]:
    token = st.session_state.get("access_token")
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(response: requests.Response) -> Dict[str, Any]:
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code >= 400:
        message = data.get("detail", "Something went wrong. Please try again.")
        if isinstance(message, list):
            message = "; ".join(str(m.get("msg", m)) for m in message)
        return {"error": True, "status_code": response.status_code, "message": message}

    return {"error": False, "data": data}


def api_get(path: str, params: Optional[dict] = None) -> Dict[str, Any]:
    try:
        response = requests.get(f"{BACKEND_URL}{path}", headers=_headers(), params=params, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return {"error": True, "status_code": 0, "message": f"Could not reach backend: {exc}"}
    return _handle_response(response)


def api_post(path: str, json_body: Optional[dict] = None, files: Optional[dict] = None) -> Dict[str, Any]:
    try:
        if files:
            # When sending multipart/form-data, don't send a JSON content-type header.
            headers = _headers()
            response = requests.post(f"{BACKEND_URL}{path}", headers=headers, files=files, timeout=TIMEOUT)
        else:
            response = requests.post(f"{BACKEND_URL}{path}", headers=_headers(), json=json_body, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return {"error": True, "status_code": 0, "message": f"Could not reach backend: {exc}"}
    return _handle_response(response)


def api_put(path: str, json_body: Optional[dict] = None) -> Dict[str, Any]:
    try:
        response = requests.put(f"{BACKEND_URL}{path}", headers=_headers(), json=json_body, timeout=TIMEOUT)
    except requests.RequestException as exc:
        return {"error": True, "status_code": 0, "message": f"Could not reach backend: {exc}"}
    return _handle_response(response)


def api_delete(path: str) -> Dict[str, Any]:
    try:
        response = requests.delete(f"{BACKEND_URL}{path}", headers=_headers(), timeout=TIMEOUT)
    except requests.RequestException as exc:
        return {"error": True, "status_code": 0, "message": f"Could not reach backend: {exc}"}
    return _handle_response(response)
