"""
Silnik Oczyszczania i Migracji Danych Magazynowo-Finansowych (Data Cleanser & Legacy Modernizer).
Automatycznie porządkuje 'brudne' pliki ze starych systemów ERP/magazynowych:
- Naprawa formatów kwot, walut i jednostek miar
- Standaryzacja numerów NIP (usuwanie kresek, spacji, prefiksu PL) + matematyczna walidacja sumy kontrolnej NIP
- Konwersja dat do jednolitego standardu ISO (YYYY-MM-DD)
- Automatyczne wyliczanie wartości zapasów oraz wzbogacanie kartotek o kody GTU i statusy podatkowe
"""

import pandas as pd
import re
from datetime import datetime

try:
    from engine.finance_engine import validate_nip_checksum
except ImportError:
    def validate_nip_checksum(nip_raw: str) -> tuple[bool, str]:
        digits = re.sub(r'[^0-9]', '', str(nip_raw))
        if len(digits) != 10:
            return False, f"Błędna długość NIP ({len(digits)} cyfr)"
        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        checksum = sum(int(digits[i]) * weights[i] for i in range(9)) % 11
        if checksum == 10 or checksum != int(digits[9]):
            return False, f"BŁĄD SUMY KONTROLNEJ NIP ({digits})"
        return True, f"Poprawny NIP ({digits})"


def clean_amount(val) -> float:
    """Konwertuje brudne napisy kwotowe typu '6 200,00 PLN' lub '30,50 zl' na czysty float."""
    if pd.isna(val):
        return 0.0
    val_str = str(val).lower()
    val_str = re.sub(r'[^\d,.-]', '', val_str)
    val_str = val_str.replace(',', '.')
    try:
        return round(float(val_str), 2)
    except ValueError:
        return 0.0


def clean_nip(val) -> str:
    """Oczyszcza NIP z kresek, spacji i prefiksu PL."""
    if pd.isna(val):
        return ""
    val_str = str(val).upper()
    digits = re.sub(r'[^0-9]', '', val_str)
    return digits if len(digits) == 10 else val_str.strip()


def clean_date(val) -> str:
    """Standaryzuje daty z różnych formatów (DD/MM/YYYY, YYYY.MM.DD, DD-MM-YYYY) do YYYY-MM-DD."""
    if pd.isna(val):
        return ""
    val_str = str(val).strip()
    
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%Y.%m.%d", 
        "%Y/%m/%d", "%d-%m-%Y", "%Y%m%d"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return val_str


def clean_and_modernize_legacy_data(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Główna funkcja porządkująca zabałaganiony zbiór magazynowy/księgowy.
    """
    df_clean = df_raw.copy()
    issues_fixed = {
        "kwoty_poprawione": 0,
        "nipy_oczyszczone": 0,
        "bledne_nipy_wykryte": 0,
        "daty_zestandaryzowane": 0,
        "gtu_przypisane": 0,
        "alerty_podatkowe": 0,
        "wartosc_magazynu_pln": 0.0
    }

    cols = {col.upper(): col for col in df_clean.columns}
    
    # 1. Czyszczenie kwot / cen
    price_col = None
    for k in cols:
        if any(w in k for w in ["CENA", "WARTOSC", "KWOTA", "NETTO", "BRUTTO"]):
            price_col = cols[k]
            break
    if price_col:
        df_clean["CENA_JEDN_PLN"] = df_clean[price_col].apply(clean_amount)
        issues_fixed["kwoty_poprawione"] = len(df_clean)

    # 2. Czyszczenie stanów magazynowych / ilości
    qty_col = None
    for k in cols:
        if any(w in k for w in ["STAN", "ILOSC", "SZTUK", "QTY"]):
            qty_col = cols[k]
            break
    if qty_col:
        def parse_qty_and_unit(val):
            val_str = str(val).strip()
            num_match = re.search(r'[\d\s]+', val_str)
            unit_match = re.search(r'[a-zA-Ząćęłńóśźż]+', val_str)
            qty = float(num_match.group(0).replace(" ", "")) if num_match else 1.0
            unit = unit_match.group(0).lower() if unit_match else "szt"
            return qty, unit

        res_qty = df_clean[qty_col].apply(parse_qty_and_unit)
        df_clean["ILOSC_LICZBA"] = [r[0] for r in res_qty]
        df_clean["JEDNOSTKA"] = [r[1] for r in res_qty]

    # Wyliczenie łącznej wartości pozycji netto
    if "CENA_JEDN_PLN" in df_clean.columns and "ILOSC_LICZBA" in df_clean.columns:
        df_clean["WARTOSC_NETTO_PLN"] = (df_clean["CENA_JEDN_PLN"] * df_clean["ILOSC_LICZBA"]).round(2)
        issues_fixed["wartosc_magazynu_pln"] = round(float(df_clean["WARTOSC_NETTO_PLN"].sum()), 2)

    # 3. Czyszczenie i walidacja matematyczna NIP
    nip_col = None
    for k in cols:
        if "NIP" in k:
            nip_col = cols[k]
            break
    if nip_col:
        df_clean["NIP_STANDARYZOWANY"] = df_clean[nip_col].apply(clean_nip)
        issues_fixed["nipy_oczyszczone"] = len(df_clean)
        
        nip_statuses = []
        for nip_val in df_clean["NIP_STANDARYZOWANY"]:
            is_valid, _ = validate_nip_checksum(str(nip_val))
            if is_valid:
                nip_statuses.append("✅ Suma kontrolna OK")
            else:
                nip_statuses.append("🚨 FAŁSZYWY NIP (Błąd wagi mod 11)")
                issues_fixed["bledne_nipy_wykryte"] += 1
        df_clean["WALIDACJA_NIP"] = nip_statuses

    # 4. Czyszczenie Dat
    date_col = None
    for k in cols:
        if any(w in k for w in ["DATA", "PRZYJECIA", "DOKUMENTU"]):
            date_col = cols[k]
            break
    if date_col:
        df_clean["DATA_ISO"] = df_clean[date_col].apply(clean_date)
        issues_fixed["daty_zestandaryzowane"] = len(df_clean)

    # 5. Inteligentne wzbogacanie o GTU i reguły podatkowe (AI / Reguły)
    name_col = None
    for k in cols:
        if any(w in k for w in ["NAZWA", "ARTYKUL", "OPIS"]) and "KOD" not in k:
            name_col = cols[k]
            break

    if name_col:
        df_clean[name_col] = df_clean[name_col].astype(str).str.strip()
        gtu_list = []
        tax_status_list = []
        
        for idx, row in df_clean.iterrows():
            item_name = str(row[name_col]).lower().strip()
            total_val = row.get("WARTOSC_NETTO_PLN", row.get("CENA_JEDN_PLN", 0) * row.get("ILOSC_LICZBA", 1))
            nip_status = row.get("WALIDACJA_NIP", "✅")
            
            # GTU
            if any(w in item_name for w in ["olej", "diesel", "benzyn", "paliw"]):
                gtu = "GTU-02 (Paliwa)"
                issues_fixed["gtu_przypisane"] += 1
            elif any(w in item_name for w in ["serwer", "komputer", "kabel", "elektronik", "procesor"]):
                gtu = "GTU-06 (Urządzenia elektroniczne)"
                issues_fixed["gtu_przypisane"] += 1
            elif any(w in item_name for w in ["profil", "stal", "blach", "rura"]):
                gtu = "GTU-08 (Metale i stal)"
                issues_fixed["gtu_przypisane"] += 1
            else:
                gtu = "Brak GTU"
            gtu_list.append(gtu)

            # Podatki (KUP/NKUP & Split Payment & Fałszywy NIP)
            if "FAŁSZYWY" in nip_status:
                status = "🚨 BLOKADA: Fałszywy NIP + NKUP"
                issues_fixed["alerty_podatkowe"] += 1
            elif any(w in item_name for w in ["gastronomi", "lunch", "restaurac", "kolacja"]):
                status = "🚨 NKUP (art. 16 ust. 1 pkt 28 CIT)"
                issues_fixed["alerty_podatkowe"] += 1
            elif total_val * 1.23 >= 15000.0 and gtu != "Brak GTU":
                status = "⚠️ WYMAGANY SPLIT PAYMENT (Zał. 15)"
                issues_fixed["alerty_podatkowe"] += 1
            else:
                status = "✅ KUP Standard"
            tax_status_list.append(status)

        df_clean["KOD_GTU_JPK"] = gtu_list
        df_clean["STATUS_PODATKOWY"] = tax_status_list

    return df_clean, issues_fixed
