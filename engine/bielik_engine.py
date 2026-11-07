# -*- coding: utf-8 -*-
"""
OptiDoc AI Enterprise — Moduł Suwerenny Bielik (bielik_engine.py)
Komunikacja z lokalnym lub chmurowym serwerem Ollama (Bielik 11B / 7B)
Domyślny węzeł: Google Cloud Warszawa (europe-central2-a)
"""

import json
import re
import time
import requests
from typing import Dict, Any, Optional, Generator

DEFAULT_OLLAMA_URL = "http://34.116.170.183:11434"
DEFAULT_BIELIK_MODEL = "bielik:latest"

BIELIK_SYSTEM_PROMPT = """Jesteś polskim ekspertem ds. audytu finansowo-księgowego i prawnego w systemie OptiDoc AI.
Twoim zadaniem jest dokładna analiza przekazanego tekstu dokumentu (faktury, umowy, pisma urzędowego).

Dla FAKTURY zwróć ZAWSZE czysty format JSON (bez bloków markdown, bez zbędnych słów wstępu):
{
  "typ_dokumentu": "faktura",
  "sprzedawca_nazwa": "pełna nazwa sprzedawcy",
  "sprzedawca_nip": "10-cyfrowy NIP bez kresek",
  "nabywca_nazwa": "pełna nazwa nabywcy",
  "numer_faktury": "numer dokumentu",
  "kwota_netto": 0.00,
  "kwota_vat": 0.00,
  "kwota_brutto": 0.00,
  "rachunek_bankowy": "26-cyfrowy numer konta bez spacji",
  "uwagi_ryzyka": "informacja o mechanizmie podzielonej płatności, walucie lub braku danych"
}
"""

def test_bielik_connection(endpoint_url: str = DEFAULT_OLLAMA_URL) -> Dict[str, Any]:
    """Sprawdza dostępność serwera Ollama, listę pobranych modeli i mierzy opóźnienie (ping)."""
    url = f"{endpoint_url.rstrip('/')}/api/tags"
    t0 = time.time()
    try:
        resp = requests.get(url, timeout=7)
        latency_ms = int((time.time() - t0) * 1000)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name") for m in data.get("models", [])]
            return {
                "sukces": True,
                "komunikat": f"Połączono z węzłem Warszawa! Latencja: {latency_ms} ms. Dostępne modele: {', '.join(models) if models else 'Brak'}",
                "modele": models,
                "latencja_ms": latency_ms
            }
    except Exception as e:
        return {"sukces": False, "komunikat": f"Błąd połączenia z serwerem: {str(e)}", "modele": [], "latencja_ms": -1}
    return {"sukces": False, "komunikat": "Serwer zwrócił nieoczekiwany kod błędu", "modele": [], "latencja_ms": -1}

def stream_bielik(prompt: str, endpoint_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_BIELIK_MODEL, num_predict: int = 350) -> Generator[str, None, None]:
    """Strumieniuje odpowiedź modelu Bielik token po tokenie w czasie rzeczywistym."""
    url = f"{endpoint_url.rstrip('/')}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": num_predict,
            "num_thread": 4
        }
    }
    try:
        with requests.post(url, json=payload, stream=True, timeout=120) as resp:
            if resp.status_code != 200:
                yield f"Błąd serwera HTTP {resp.status_code}: {resp.text}"
                return
            for line in resp.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done", False):
                            break
                    except Exception:
                        continue
    except Exception as e:
        yield f"\n[Błąd strumieniowania: {str(e)}]"

def query_bielik(prompt: str, endpoint_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_BIELIK_MODEL, timeout: int = 120, num_predict: int = 350) -> str:
    """Wysyła dowolne zapytanie do modelu Bielik i zwraca wygenerowany tekst."""
    chunks = []
    for token in stream_bielik(prompt, endpoint_url=endpoint_url, model_name=model_name, num_predict=num_predict):
        chunks.append(token)
    return "".join(chunks)

def analyze_with_bielik(document_text: str, endpoint_url: str = DEFAULT_OLLAMA_URL, model_name: str = DEFAULT_BIELIK_MODEL, timeout: int = 120) -> Dict[str, Any]:
    """Wysyła tekst dokumentu do modelu Bielik i parsuje odpowiedź JSON."""
    url = f"{endpoint_url.rstrip('/')}/api/generate"
    
    prompt = f"{BIELIK_SYSTEM_PROMPT}\n\nTEKST DOKUMENTU DO ANALIZY:\n{document_text}\n\nODPOWIEDŹ JSON:"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": 350,
            "num_thread": 4
        }
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            result_raw = resp.json().get("response", "").strip()
            try:
                return json.loads(result_raw)
            except Exception:
                match = re.search(r"(\{.*\})", result_raw, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
                return {"surowa_odpowiedz": result_raw, "error": "Brak poprawnego formatu JSON w odpowiedzi"}
        else:
            return {"error": f"Błąd serwera HTTP {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"error": f"Błąd wykonania zapytania: {str(e)}"}
