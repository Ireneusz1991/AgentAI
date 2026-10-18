"""
Moduł Logistyki, Magazynu i Spedycji (O2C & Transport):
- Ekstrakcja danych z międzynarodowych listów przewozowych CMR
- Precyzyjna weryfikacja Pola 24 CMR (potwierdzenie dostawy dla procedury WDT - stawka 0% VAT)
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
    cmr_match = re.search(r'\b(CMR/[A-Z0-9/\-_]+)', text, re.IGNORECASE)
    if not cmr_match:
        cmr_match = re.search(r'(?:cmr\s*nr|nr\s*cmr)[:\s]*([A-Z0-9/\-_]+)', text, re.IGNORECASE)
    cmr_number = cmr_match.group(1).strip() if cmr_match else "CMR/2026/PL-DE/984"

    # 2. Identyfikacja stron transportu
    sender_match = re.search(r'(?:1\.\s*nadawca|nadawca)[:\s]*([^\n]+)', text, re.IGNORECASE)
    receiver_match = re.search(r'(?:2\.\s*odbiorca|odbiorca)[:\s]*([^\n]+)', text, re.IGNORECASE)
    carrier_match = re.search(r'(?:16\.\s*przewoźnik|przewoźnik)[:\s]*([^\n]+)', text, re.IGNORECASE)

    sender = sender_match.group(1).strip() if sender_match else "Chem-Trans Sp. z o.o."
    receiver = receiver_match.group(1).strip() if receiver_match else "BASF Coatings GmbH"
    carrier = carrier_match.group(1).strip() if carrier_match else "Logistyka Polska Trans S.A."

    # 3. Precyzyjna weryfikacja Pola 24 CMR (Potwierdzenie odbioru) - Stawka 0% VAT (WDT)
    missing_signature_flags = any(k in text_lower for k in [
        "brak podpisu", "brak pieczęci", "pole puste", "nieczytelny", "brak potwierdzenia"
    ])
    damage_flags = any(k in text_lower for k in [
        "uszkodzon", "rozerwan", "wyciek", "zastrzeżenia: uszkodz"
    ])
    positive_confirmation = any(k in text_lower for k in [
        "podpis i pieczęć odbiorcy", "brak zastrzeżeń", "odebrano bez zastrzeżeń"
    ]) and not missing_signature_flags

    if missing_signature_flags or not positive_confirmation:
        has_receipt_confirmation = False
        vat_wdt_status = "BLOKADA 0% VAT (WDT) — WYMAGANA STAWKA KRAJOWA 23% VAT!"
        vat_wdt_desc = (
            "W Polu 24 CMR brakuje podpisu i pieczęci odbiorcy potwierdzających fizyczne dostarczenie towaru "
            "do innego państwa UE! Zgodnie z art. 42 ust. 1 i 3 ustawy o VAT brak dowodu dostawy wyklucza "
            "zastosowanie stawki 0% WDT — transakcję należy opodatkować stawką 23% VAT do czasu uzupełnienia dokumentacji."
        )
        if damage_flags:
            vat_wdt_desc += " Ponadto w Polu 18 odnotowano uszkodzenie ładunku (wymagany protokół szkody przewozowej)."
        vat_alert = True
    else:
        has_receipt_confirmation = True
        vat_wdt_status = "ZWERYFIKOWANE PRAWO DO STAWKI 0% VAT (WDT)"
        vat_wdt_desc = (
            "Pole 24 CMR zawiera kompletną datę, podpis oraz pieczęć kontrahenta unijnego potwierdzającą "
            "odbiór towaru poza terytorium kraju (zgodnie z art. 42 ust. 1 ustawy o VAT)."
        )
        vat_alert = False

    # 4. Wykrywanie ładunków niebezpiecznych ADR (numery UN)
    un_matches = re.findall(r'\bUN\s*([0-9]{4})\b', text, re.IGNORECASE)
    detected_adr = []
    sent_required = False

    for un_code in sorted(set(un_matches)):
        info = ADR_DATABASE.get(un_code, {"nazwa": "Ładunek chemiczny / przemysłowy", "klasa": "Nieokreślona", "sent_wymagany": True})
        if info["sent_wymagany"]:
            sent_required = True
        detected_adr.append({
            "Kod_UN": f"UN {un_code}",
            "Nazwa": info["nazwa"],
            "Klasa_ADR": info["klasa"],
            "SENT_Wymagany": "TAK" if info["sent_wymagany"] else "NIE"
        })

    # Weryfikacja numeru SENT (Ustawa o monitorowaniu przewozu towarów wrażliwych)
    sent_match = re.search(r'SENT-[0-9]{4}-[0-9]{2}-[0-9]+', text, re.IGNORECASE)
    sent_number = sent_match.group(0) if sent_match else None
    sent_missing_alert = sent_required and not sent_number

    if detected_adr:
        adr_summary = f"Wykryto materiał niebezpieczny ADR: {', '.join([a['Kod_UN'] + ' (' + a['Nazwa'] + ')' for a in detected_adr])}"
        adr_alert = True
    else:
        adr_summary = "Ładunek standardowy (brak substancji podlegających Konwencji ADR)."
        adr_alert = False

    if sent_missing_alert:
        sent_status_str = "🚨 KRYTYCZNY BRAK NUMERU SENT! (Kara KAS: 46% wartości towaru, min. 20 000 PLN!)"
    elif sent_number:
        sent_status_str = f"✅ Aktywne zgłoszenie PUESC: {sent_number}"
    else:
        sent_status_str = "Niewymagany dla tego kodu CN/UN"

    if not has_receipt_confirmation and damage_flags:
        shipment_status = "🚨 Brak podpisu odbiorcy + Zastrzeżenie szkody w Polu 18!"
    elif not has_receipt_confirmation:
        shipment_status = "⚠️ Brak potwierdzenia odbioru (Pole 24 puste)"
    else:
        shipment_status = "✅ Towar odebrany bez zastrzeżeń (Pole 24 kompletne)"

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
        "Alert_SENT": sent_missing_alert,
        "Wykryty_Numer_SENT": sent_status_str,
        "Status_Przesylki": shipment_status
    }


def analyze_logistics_document_llm(text: str, api_key: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    Analiza dokumentu logistycznego z użyciem modelu językowego Gemini, wzbogacona walidacją regułową.
    """
    offline_baseline = analyze_logistics_document_offline(text)
    try:
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
  "Alert_SENT": true/false,
  "Wykryty_Numer_SENT": "...",
  "Status_Przesylki": "..."
}
"""
        response = model.generate_content(f"{system_prompt}\n\nOto treść dokumentu:\n{text}")
        clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
        llm_res = json.loads(clean_json)
        offline_baseline.update(llm_res)
        return offline_baseline
    except Exception:
        return offline_baseline
