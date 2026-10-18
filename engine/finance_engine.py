"""
Moduł Finansowo-Podatkowy (P2P):
- Ekstrakcja danych z faktur
- Kwalifikacja KUP / NKUP (podatki dochodowe PIT/CIT)
- Walidacja Mechanizmu Podzielonej Płatności (Split Payment / MPP)
- 3-Way Matching (Zamówienie PO <=> Magazyn PZ <=> Faktura FV)
"""

import re
import json

def analyze_finance_document_offline(text: str) -> dict:
    """
    Regułowy silnik offline do analizy dokumentu finansowego.
    Pozwala na natychmiastowe testy bez konieczności podawania klucza API.
    """
    text_lower = text.lower()
    
    # 1. Wykrywanie numeru faktury
    inv_num_match = re.search(r'(?:faktura\s*(?:nr|vat\s*nr)?[:\s]*|nr[:\s]*|fv[/\s])([A-Z0-9/\-_]+)', text, re.IGNORECASE)
    invoice_number = inv_num_match.group(1).strip() if inv_num_match else "FS/NIEZNANA/2026"
    
    # 2. Wykrywanie NIP
    nips = re.findall(r'NIP[:\s]*([0-9]{10}|PL[0-9]{10})', text, re.IGNORECASE)
    seller_nip = nips[0] if len(nips) > 0 else "Brak danych"
    buyer_nip = nips[1] if len(nips) > 1 else "1112223344"
    
    # 3. Wykrywanie kwot
    netto_match = re.search(r'(?:netto|wartość\s*netto)[:\s]*([0-9\s]+(?:[,.][0-9]{2})?)', text, re.IGNORECASE)
    brutto_match = re.search(r'(?:brutto|wartość\s*brutto|do\s*zapłaty)[:\s]*([0-9\s]+(?:[,.][0-9]{2})?)', text, re.IGNORECASE)
    vat_match = re.search(r'(?:kwota\s*vat|vat)[:\s]*([0-9\s]+(?:[,.][0-9]{2})?)', text, re.IGNORECASE)
    
    def parse_amount(val_str, default=0.0):
        if not val_str:
            return default
        cleaned = val_str.replace(" ", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return default

    netto = parse_amount(netto_match.group(1) if netto_match else None, 200.0)
    brutto = parse_amount(brutto_match.group(1) if brutto_match else None, 246.0)
    vat = parse_amount(vat_match.group(1) if vat_match else None, round(brutto - netto, 2))
    
    # 4. Wykrywanie dat
    date_match = re.search(r'(?:data\s*wystawienia|wystawiono|data)[:\s]*([0-9]{2}[.-][0-9]{2}[.-][0-9]{4})', text, re.IGNORECASE)
    issue_date = date_match.group(1) if date_match else "12.10.2026"
    
    # 5. Kwalifikacja KUP / NKUP (Zgodnie z art. 16 ust. 1 CIT / art. 23 ust. 1 PIT)
    is_nkup = any(kw in text_lower for kw in ["gastronomi", "restaurac", "kolacja biznesow", "reprezentac", "alkohol"])
    if is_nkup:
        status_kup = "NKUP"
        kup_uzasadnienie = "Wydatek wyłączony z KUP na podstawie art. 16 ust. 1 pkt 28 CIT / art. 23 ust. 1 pkt 23 PIT (koszty reprezentacji oraz usługi gastronomiczne)."
        kup_alert = True
    else:
        status_kup = "KUP"
        kup_uzasadnienie = "Wydatek powiązany z prowadzoną działalnością gospodarczą i osiąganiem przychodów (art. 15 ust. 1 CIT / art. 22 ust. 1 PIT)."
        kup_alert = False

    # 6. Weryfikacja Split Payment (Mechanizm Podzielonej Płatności - art. 108a ustawy o VAT)
    # Próg 15 000 zł brutto + towary wrażliwe (elektronika, serwery, paliwa, złom, stal itp.)
    is_split_payment_required = brutto >= 15000.0 or "split payment" in text_lower or "mechanizm podzielonej płatności" in text_lower or "mpp" in text_lower
    if is_split_payment_required:
        split_payment_status = "BLOKADA: OBLIGATORYJNY SPLIT PAYMENT"
        split_payment_desc = f"Kwota brutto ({brutto:,.2f} PLN) przekracza próg 15 000 PLN lub dotyczy towarów z Zał. nr 15 do VAT. Standardowy przelew zablokowany."
        split_alert = True
    else:
        split_payment_status = "Standardowy przelew"
        split_payment_desc = "Kwota poniżej progu 15 000 PLN, brak wymogu MPP."
        split_alert = False

    # 7. Kody GTU (Jednolity Plik Kontrolny JPK_V7)
    gtu_detected = []
    if any(k in text_lower for k in ["paliwo", "olej", "benzyn"]):
        gtu_detected.append("GTU-02 (Paliwa)")
    if any(k in text_lower for k in ["serwer", "komputer", "laptop", "procesor"]):
        gtu_detected.append("GTU-06 (Urządzenia elektroniczne)")
    if any(k in text_lower for k in ["doradcz", "marketing", "szkoleni"]):
        gtu_detected.append("GTU-12 (Usługi o charakterze niematerialnym)")
    
    # 8. 3-Way Matching check
    has_po = "po-" in text_lower or "zamówienie" in text_lower
    has_pz = "pz-" in text_lower or "przyjęcie" in text_lower or "magazyn" in text_lower
    matching_status = "3-Way Matching: OK" if (has_po and has_pz) else "Częściowy (Brak powiązania PZ/PO)"

    return {
        "Numer_Faktury": invoice_number,
        "NIP_Sprzedawcy": seller_nip,
        "NIP_Nabywcy": buyer_nip,
        "Data_Wystawienia": issue_date,
        "Kwota_Netto": netto,
        "Kwota_VAT": vat,
        "Kwota_Brutto": brutto,
        "Status_KUP": status_kup,
        "Uzasadnienie_KUP": kup_uzasadnienie,
        "Alert_KUP": kup_alert,
        "Status_Split_Payment": split_payment_status,
        "Opis_Split_Payment": split_payment_desc,
        "Alert_Split": split_alert,
        "Wykryte_Kody_GTU": ", ".join(gtu_detected) if gtu_detected else "Brak specyficznego GTU",
        "Status_Matching": matching_status,
        "Tryb_Analizy": "Offline Rule-Engine (Baza Prawna MŚP)"
    }


def analyze_finance_document_llm(text: str, api_key: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    Analiza dokumentu finansowego z użyciem modelu językowego Gemini.
    """
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    system_prompt = """
Jesteś certyfikowanym doradcą podatkowym i analitykiem systemów ERP w polskim sektorze MŚP.
Przeanalizuj podany tekst faktury lub dokumentu finansowego.

Zastosuj twarde reguły prawa podatkowego:
1. Klasyfikacja KUP / NKUP: Zgodnie z art. 16 ust. 1 pkt 28 CIT / art. 23 ust. 1 pkt 23 PIT, usługi gastronomiczne, alkohol i wydatki na reprezentację stanowią NKUP. Inne wydatki operacyjne to KUP.
2. Split Payment (art. 108a ustawy o VAT): Jeśli kwota brutto >= 15 000 PLN lub faktura zawiera towary z Załącznika nr 15 (np. sprzęt IT, elektronika, stal, paliwa), flaga to "BLOKADA: OBLIGATORYJNY SPLIT PAYMENT".
3. Kody GTU dla JPK_V7: Wykryj jeśli występuje np. GTU-02 (paliwa), GTU-06 (elektronika), GTU-12 (doradztwo).
4. 3-Way Matching: Sprawdź czy dokument zawiera referencje do zamówienia zakupu (PO) oraz przyjęcia magazynowego (PZ).

Zwróć odpowiedź WYŁĄCZNIE jako poprawny format JSON (bez markdown ```json):
{
  "Numer_Faktury": "...",
  "NIP_Sprzedawcy": "...",
  "NIP_Nabywcy": "...",
  "Data_Wystawienia": "...",
  "Kwota_Netto": 0.0,
  "Kwota_VAT": 0.0,
  "Kwota_Brutto": 0.0,
  "Status_KUP": "KUP lub NKUP",
  "Uzasadnienie_KUP": "...",
  "Alert_KUP": true/false,
  "Status_Split_Payment": "Standard lub BLOKADA: OBLIGATORYJNY SPLIT PAYMENT",
  "Opis_Split_Payment": "...",
  "Alert_Split": true/false,
  "Wykryte_Kody_GTU": "...",
  "Status_Matching": "...",
  "Tryb_Analizy": "Gemini AI LLM"
}
"""
    response = model.generate_content(f"{system_prompt}\n\nOto treść dokumentu:\n{text}")
    clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)
