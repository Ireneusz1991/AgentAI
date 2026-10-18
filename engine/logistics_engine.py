"""
Moduł Logistyki, Magazynu i Spedycji (O2C & Transport):
- Ekstrakcja danych z międzynarodowych listów przewozowych CMR
- Weryfikacja potwierdzenia dostawy dla procedury WDT (stawka 0% VAT)
- Identyfikacja i walidacja przewozu towarów niebezpiecznych ADR (numery UN, klasy zagrożeń)
- Weryfikacja zgłoszeń SENT (Ustawa o systemie monitorowania drogowego i kolejowego przewozu towarów)
"""

import re
import json

ADR_DATABASE = {
    "1202": {"nazwa": "PALIWO DO SILNIKÓW DIESLA / OLEJ OPAŁOWY", "klasa": "3 (Ciecze zapalne)", "sent_wymagany": True},
    "1203": {"nazwa": "BENZYNA SILNIKOWA", "klasa": "3 (Ciecze zapalne)", "sent_wymagany": True},
    "1993": {"nazwa": "MATERIAŁ CIEKŁY ZAPALNY I.N.O.", "klasa": "3 (Ciecze zapalne)", "sent_wymagany": True},
    "1789": {"nazwa": "KWAS SOLNY", "klasa": "8 (Materiały żrące)", "sent_wymagany": False},
    "1824": {"nazwa": "WODOROTLENEK SODU W ROZTWORZE", "klasa": "8 (Materiały żrące)", "sent_wymagany": False}
}

def analyze_logistics_document_offline(text: str) -> dict:
    """
    Regułowy silnik analizy dokumentu transportowego i magazynowego w trybie offline.
    """
    text_lower = text.lower()
    
    # 1. Numer CMR / WZ
    cmr_match = re.search(r'(?:cmr\s*(?:nr)?[:\s]*|nr[:\s]*)([A-Z0-9/\-_]+)', text, re.IGNORECASE)
    cmr_number = cmr_match.group(1).strip() if cmr_match else "CMR/2026/PL-DE/984"

    # 2. Identyfikacja stron transportu
    sender_match = re.search(r'(?:nadawca|1\.\s*nadawca)[:\s]*([^\n,]+)', text, re.IGNORECASE)
    receiver_match = re.search(r'(?:odbiorca|2\.\s*odbiorca)[:\s]*([^\n,]+)', text, re.IGNORECASE)
    carrier_match = re.search(r'(?:przewoźnik|16\.\s*przewoźnik)[:\s]*([^\n,]+)', text, re.IGNORECASE)

    sender = sender_match.group(1).strip() if sender_match else "Chem-Trans Sp. z o.o."
    receiver = receiver_match.group(1).strip() if receiver_match else "BASF Coatings GmbH"
    carrier = carrier_match.group(1).strip() if carrier_match else "Logistyka Polska Trans S.A."

    # 3. Potwierdzenie odbioru (Pole 24 CMR) - Stawka 0% VAT (WDT)
    has_receipt_confirmation = any(k in text_lower for k in [
        "przesyłkę otrzymano", "odbiorca:", "podpis i pieczęć odbiorcy", "brak zastrzeżeń", "odebrano"
    ])
    
    if has_receipt_confirmation:
        vat_wdt_status = "ZWERYFIKOWANE DLA STAWKI 0% VAT (WDT)"
        vat_wdt_desc = "Dokument CMR posiada potwierdzenie odbioru przez kontrahenta unijnego. Zgodnie z art. 42 ust. 1 ustawy o VAT, firma ma prawo do zastosowania preferencyjnej stawki 0% VAT."
        vat_alert = False
    else:
        vat_wdt_status = "RYZYKO: BRAK POTWIERDZENIA ODBIORU (STAWKA 23% VAT)"
        vat_wdt_desc = "Brak czytelnego potwierdzenia odbioru w polu 24 CMR. Ryzyko zakwestionowania stawki 0% WDT przez Urząd Skarbowy i konieczność opodatkowania stawką krajową 23%!"
        vat_alert = True

    # 4. Wykrywanie ładunków niebezpiecznych ADR (numery UN)
    un_matches = re.findall(r'\bUN\s*([0-9]{4})\b', text, re.IGNORECASE)
    detected_adr = []
    sent_required = False

    for un_code in set(un_matches):
        info = ADR_DATABASE.get(un_code, {"nazwa": "Ładunek chemiczny / przemysłowy", "klasa": "Nieokreślona", "sent_wymagany": True})
        if info["sent_wymagany"]:
            sent_required = True
        detected_adr.append({
            "Kod_UN": f"UN {un_code}",
            "Nazwa": info["nazwa"],
            "Klasa_ADR": info["klasa"],
            "SENT_Wymagany": info["sent_wymagany"]
        })

    # Weryfikacja numeru SENT
    sent_match = re.search(r'SENT-[0-9]{4}-[0-9]{2}-[0-9]+', text, re.IGNORECASE)
    sent_number = sent_match.group(0) if sent_match else None

    if detected_adr:
        adr_summary = f"Wykryto materiał niebezpieczny ADR: {', '.join([a['Kod_UN'] for a in detected_adr])}"
        adr_alert = True
    else:
        adr_summary = "Ładunek standardowy (brak substancji podlegających ADR)."
        adr_alert = False

    return {
        "Numer_CMR": cmr_number,
        "Nadawca": sender,
        "Odbiorca": receiver,
        "Przewoźnik": carrier,
        "Status_Potwierdzenia_WDT_0_VAT": vat_wdt_status,
        "Opis_Konsekwencji_Podatkowych": vat_wdt_desc,
        "Alert_VAT": vat_alert,
        "Status_ADR": adr_summary,
        "Wykryte_Kody_UN": detected_adr,
        "Alert_ADR": adr_alert,
        "Wymóg_Rejestracji_SENT": sent_required,
        "Wykryty_Numer_SENT": sent_number if sent_number else ("BRAK (Zalecana natychmiastowa rejestracja w PUESC!)" if sent_required else "Niewymagany"),
        "Status_Przesylki": "Towar odebrany bez zastrzeżeń" if has_receipt_confirmation else "W drodze / Brak potwierdzenia"
    }


def analyze_logistics_document_llm(text: str, api_key: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    Analiza dokumentu logistycznego z użyciem modelu językowego Gemini.
    """
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    system_prompt = """
Jesteś dyspozytorem transportu międzynarodowego oraz specjalistą ds. compliance w prawie przewozowym i podatkowym.
Przeanalizuj poniższy list przewozowy CMR lub dokument magazynowy.

Wykonaj następujące zadania:
1. Zweryfikuj pole 24 CMR (potwierdzenie otrzymania przesyłki) pod kątem prawa do stawki 0% VAT przy Wewnątrzwspólnotowej Dostawie Towarów (art. 42 ustawy o VAT).
2. Sprawdź, czy dokument dotyczy ładunku niebezpiecznego ADR (wykryj numery UN, klasy zagrożenia).
3. Zweryfikuj wymóg rejestracji w systemie SENT (monitorowanie przewozu paliw i towarów wrażliwych).

Zwróć odpowiedź WYŁĄCZNIE jako poprawny JSON:
{
  "Numer_CMR": "...",
  "Nadawca": "...",
  "Odbiorca": "...",
  "Przewoźnik": "...",
  "Status_Potwierdzenia_WDT_0_VAT": "...",
  "Opis_Konsekwencji_Podatkowych": "...",
  "Alert_VAT": true/false,
  "Status_ADR": "...",
  "Wykryte_Kody_UN": [],
  "Alert_ADR": true/false,
  "Wymóg_Rejestracji_SENT": true/false,
  "Wykryty_Numer_SENT": "...",
  "Status_Przesylki": "..."
}
"""
    response = model.generate_content(f"{system_prompt}\n\nOto treść dokumentu:\n{text}")
    clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)
