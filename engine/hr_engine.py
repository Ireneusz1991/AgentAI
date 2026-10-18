"""
Moduł Kadrowo-Płacowy i RODO (HR & Compliance):
- Kwalifikacja dokumentu do części e-Teczki (Części A, B, C, D, E)
- Anonimizacja RODO (Privacy by Design - maskowanie serii i numeru dowodu, danych wrażliwych)
- Compliance z AI Act (Zarządzanie ryzykiem w systemach HR, audytowalność, Human-in-the-Loop)
"""

import re
import json
from datetime import datetime

# Wzorce Regex do wykrywania nadmiarowych danych osobowych
REGEX_ID_CARD = r'\b[A-Z]{3}\s?[0-9]{6}\b'  # Seria i nr dowodu osobistego (np. ABC 123456)
REGEX_PESEL = r'\b[0-9]{11}\b'             # PESEL

def classify_eteczka_part(text_lower: str) -> tuple[str, str, int]:
    """
    Zgodnie z Rozporządzeniem Ministra Rodziny, Pracy i Polityki Społecznej
    w sprawie dokumentacji pracowniczej (części A, B, C, D, E).
    Zwraca: (Oznaczenie części, Nazwa i zakres prawny, okres retencji w latach).
    """
    if any(k in text_lower for k in ["kandydat", "rekrutac", "kwestionariusz osoby ubiegającej", "badanie wstępn", "orzeczenie lekarskie nr"]):
        return (
            "Część A", 
            "Dokumenty zgromadzone w związku z ubieganiem się o zatrudnienie (etap rekrutacji)", 
            10
        )
    elif any(k in text_lower for k in ["umowa o pracę", "nawiązanie", "porozumienie zmieniające", "aneks", "szkolenie bhp", "oświadczenie pit-2", "zakres obowiązków"]):
        return (
            "Część B", 
            "Dokumenty dotyczące nawiązania stosunku pracy oraz przebiegu zatrudnienia pracownika", 
            10
        )
    elif any(k in text_lower for k in ["wypowiedzenie", "świadectwo pracy", "rozwiązanie umowy", "odwołanie ze stanowiska"]):
        return (
            "Część C", 
            "Dokumenty związane z ponoszeniem odpowiedzialności porządkowej lub ustaniem zatrudnienia", 
            10
        )
    elif any(k in text_lower for k in ["upomnienie", "nagana", "kara porządkowa", "zawiadomienie o ukaraniu"]):
        return (
            "Część D", 
            "Odpis zawiadomienia o ukaraniu oraz inne dokumenty związane z odpowiedzialnością porządkową (art. 108 KP)", 
            1  # Usunięcie po roku nienagannej pracy
        )
    elif any(k in text_lower for k in ["trzeźwoś", "badanie alkomatem", "środki odurzające", "praca zdalna okazjonalna"]):
        return (
            "Część E", 
            "Dokumenty związane z kontrolą trzeźwości pracowników oraz pracą zdalną (obowiązuje od 2023 r.)", 
            1
        )
    else:
        return (
            "Część B (Domyślna)", 
            "Dokumentacja bieżącego stosunku pracy", 
            10
        )


def anonymize_rodo_text(raw_text: str) -> tuple[str, list[str]]:
    """
    Wdrożenie zasady minimalizacji danych (art. 5 ust. 1 lit. c RODO).
    Pracodawca nie może gromadzić kserokopii dowodów osobistych ani przetwarzać
    serii i numeru dowodu, jeśli tożsamość potwierdzono numerem PESEL (art. 22[1] Kodeksu Pracy).
    """
    detected_violations = []
    anonymized_text = raw_text

    # 1. Wykrywanie serii i numeru dowodu osobistego
    id_cards = re.findall(REGEX_ID_CARD, anonymized_text)
    if id_cards:
        for match in set(id_cards):
            detected_violations.append(f"Seria i nr dowodu osobistego: '{match}' (Dane nadmiarowe)")
            anonymized_text = re.sub(re.escape(match), "[ZANONIMIZOWANO: Seria i Nr Dowodu Osobistego]", anonymized_text)

    # 2. Wykrywanie danych wrażliwych medycznych (art. 9 RODO)
    medical_sensitive_terms = ["diagnoza", "rozpoznanie", "choroba", "hospitalizacja", "leczenie psychiatryczne"]
    for term in medical_sensitive_terms:
        if term in anonymized_text.lower():
            detected_violations.append(f"Wykryto potencjalną diagnozę medyczną: '{term}' (Art. 9 RODO)")
            anonymized_text = re.sub(rf'(?i){term}[^.,\n]*', "[ZANONIMIZOWANO: Szczegóły Medyczne - Art. 9 RODO]", anonymized_text)

    return anonymized_text, detected_violations


def analyze_hr_document_offline(text: str) -> dict:
    """
    Regułowy silnik analizy dokumentu pracowniczego w trybie offline.
    """
    text_lower = text.lower()
    
    # 1. Identyfikacja typu dokumentu
    if "umowa o pracę" in text_lower:
        doc_type = "Umowa o Pracę"
    elif "orzeczenie lekarskie" in text_lower or "badanie" in text_lower:
        doc_type = "Orzeczenie Lekarskie Medycyny Pracy"
    elif "świadectwo pracy" in text_lower:
        doc_type = "Świadectwo Pracy"
    elif "wypowiedzenie" in text_lower:
        doc_type = "Oświadczenie o Wypowiedzeniu Umowy"
    else:
        doc_type = "Dokument Kadrowy Inny"

    # 2. Klasyfikacja e-Teczki
    czesc_eteczki, opis_czesci, okres_retencji = classify_eteczka_part(text_lower)

    # 3. Anonimizacja RODO
    anonymized_text, rodo_violations = anonymize_rodo_text(text)

    # 4. Wyciąganie pracownika i stanowiska
    pesel_match = re.search(r'PESEL[:\s]*([0-9]{11})', text)
    pesel = pesel_match.group(1) if pesel_match else "Nie wykryto"

    stanowisko_match = re.search(r'Stanowisko[:\s]*([^\n,]+)', text, re.IGNORECASE)
    stanowisko = stanowisko_match.group(1).strip() if stanowisko_match else "Nieokreślone"

    # 5. Zgodność z AI Act (Ocena ryzyka wg Załącznika III do AI Act)
    # Narzędzia AI w rekrutacji i zarządzaniu pracownikami kwalifikowane są jako High-Risk AI.
    is_high_risk = czesc_eteczki in ["Część A", "Część B", "Część D"]
    ai_act_status = {
        "Kategoria_Ryzyka": "Wysokie Ryzyko (High-Risk AI System)" if is_high_risk else "Minimalne Ryzyko",
        "Wymóg_Nadzoru_Ludzkiego": True,
        "Podstawa_AI_Act": "Załącznik III pkt 4 AI Act (Zatrudnienie, zarządzanie pracownikami i dostęp do samozatrudnienia)",
        "Rekomendacja": "Wymagany ostateczny podpis i zatwierdzenie przez kadrowca (Human-in-the-loop)."
    }

    return {
        "Typ_Dokumentu": doc_type,
        "Czesc_eTeczki": czesc_eteczki,
        "Opis_Kwalifikacji": opis_czesci,
        "Wymagany_Okres_Retencji": f"{okres_retencji} lat (od końca roku kalendarzowego ustania zatrudnienia)",
        "PESEL_Pracownika": pesel,
        "Stanowisko": stanowisko,
        "Naruszenia_RODO": rodo_violations,
        "Liczba_Incydentow_RODO": len(rodo_violations),
        "Zanonimizowany_Tekst": anonymized_text,
        "AI_Act_Compliance": ai_act_status,
        "Wskaznik_Pewnosci_AI": 0.98,
        "Timestamp_Audytu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def analyze_hr_document_llm(text: str, api_key: str, model_name: str = "gemini-1.5-flash") -> dict:
    """
    Analiza dokumentu HR z użyciem modelu językowego Gemini.
    """
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    system_prompt = """
Jesteś inspektorem ochrony danych (IOD / RODO) oraz specjalistą ds. kadr i płac w polskim MŚP.
Przeanalizuj poniższy dokument kadrowy.

Wykonaj następujące zadania:
1. Sklasyfikuj dokument do właściwej części e-Teczki (Część A, B, C, D lub E) zgodnie z Rozporządzeniem ws. dokumentacji pracowniczej.
2. Wskaż ustawowy okres retencji dokumentu (np. 10 lat).
3. Przeprowadź anonimizację (Privacy by Design): wykryj i zamaskuj serię i numer dowodu osobistego (pracodawca ma prawo żądać tylko PESEL) oraz wszelkie dane o stanie zdrowia (art. 9 RODO).
4. Oceń zgodność z AI Act (systemy AI wspierające procesy kadrowe kwalifikowane są jako High-Risk AI - wskaż wymóg nadzoru człowieka Human-in-the-loop).

Zwróć odpowiedź WYŁĄCZNIE jako poprawny JSON (bez znaczników markdown):
{
  "Typ_Dokumentu": "...",
  "Czesc_eTeczki": "Część A/B/C/D/E",
  "Opis_Kwalifikacji": "...",
  "Wymagany_Okres_Retencji": "... lat",
  "PESEL_Pracownika": "...",
  "Stanowisko": "...",
  "Naruszenia_RODO": ["..."],
  "Liczba_Incydentow_RODO": 0,
  "Zanonimizowany_Tekst": "...",
  "AI_Act_Compliance": {
      "Kategoria_Ryzyka": "...",
      "Wymóg_Nadzoru_Ludzkiego": true,
      "Podstawa_AI_Act": "...",
      "Rekomendacja": "..."
  },
  "Wskaznik_Pewnosci_AI": 0.95,
  "Timestamp_Audytu": "..."
}
"""
    response = model.generate_content(f"{system_prompt}\n\nOto treść dokumentu HR:\n{text}")
    clean_json = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)
