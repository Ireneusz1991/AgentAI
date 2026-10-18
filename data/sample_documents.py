"""
Przykładowe dokumenty testowe (Sandbox) dla wdrożeń AI w polskich MŚP.
Dokumenty zawierają realne cechy i pułapki prawno-podatkowe, kadrowe i logistyczne.
"""

SAMPLE_DOCUMENTS = {
    "FINANSE_STANDARD": {
        "title": "Faktura Kosztowa Standard (KUP - Paliwo / Koszty bieżące)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Standardowy koszt eksploatacyjny firmy poniżej progu Split Payment.",
        "text": """Sprzedawca: ORLEN S.A., NIP: 7740001454
Adres: ul. Chemików 7, 09-411 Płock
Faktura nr: FS/123/10/2026
Data wystawienia: 12.10.2026
Data sprzedaży: 12.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 1112223344
Pozycja 1: Paliwo silnikowe Pb95, Ilość: 40 litrów, Cena jedn. netto: 5.00 PLN
Wartość Netto: 200,00 PLN
Stawka VAT: 23%
Kwota VAT: 46,00 PLN
Wartość Brutto: 246,00 PLN
Forma płatności: Karta płatnicza (Opłacono)
Konto bankowe: 10 1020 1013 0000 1234 5678 9012"""
    },
    
    "FINANSE_NKUP": {
        "title": "Faktura Pułapka Podatkowa (Gastronomia / Reprezentacja - NKUP)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Usługa gastronomiczna podlegająca wyłączeniu z kosztów uzyskania przychodu (art. 16 ust. 1 pkt 28 CIT / art. 23 ust. 1 pkt 23 PIT).",
        "text": """Sprzedawca: Restauracja Złota Kaczka Jan Kowalski, NIP: 8889990000
Adres: Rynek Starego Miasta 4, 00-272 Warszawa
Faktura nr: 15/10/2026/GASTRO
Data wystawienia: 15.10.2026
Data wykonania usługi: 15.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 1112223344
Pozycja 1: Usługa gastronomiczna - kolacja biznesowa z kluczowym kontrahentem
Wartość Netto: 450,00 PLN
Stawka VAT: 8%
Kwota VAT: 36,00 PLN
Wartość Brutto: 486,00 PLN
Forma płatności: Gotówka (Opłacono)
Adnotacja: Wydatki na reprezentację i usługi restauracyjne."""
    },
    
    "FINANSE_SPLIT_PAYMENT": {
        "title": "Faktura Pułapka Płynnościowa (Sprzęt IT > 15 000 PLN - Split Payment)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Faktura przekraczająca próg 15 000 zł brutto z towarem z Załącznika nr 15 do Ustawy o VAT, wymagająca obligatoryjnego MPP.",
        "text": """Sprzedawca: Hurtownia IT X-Kom Sp. z o.o., NIP: 7778889999
Adres: Al. Pokoju 12, 42-200 Częstochowa
Faktura nr: FV/2026/10/001
Data wystawienia: 18.10.2026
Data sprzedaży: 17.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 1112223344
Pozycja 1: Serwer bazodanowy Dell PowerEdge R750 (kod GTU-06), Ilość: 1 szt.
Wartość Netto: 14 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 3 220,00 PLN
Wartość Brutto: 17 220,00 PLN
Termin płatności: 14 dni (przelew bankowy)
Numer rachunku: 55 1090 2402 0000 0001 9876 5432
Adnotacja: Mechanizm Podzielonej Płatności (MPP)"""
    },

    "HR_UMOWA_RODO": {
        "title": "Umowa o Pracę (Część B e-Teczki + Anonimizacja RODO)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Umowa o pracę zawierająca nadmiarowe dane osobowe (seria i nr dowodu osobistego), które zgodnie z RODO powinny zostać zamaskowane.",
        "text": """DOKUMENT HR - SKAN 001
TYTUŁ: Umowa o pracę na czas nieokreślony
DATA ZAWARCIA: 20.10.2026
MIEJSCE ZAWARCIA: Warszawa

STRONY UMOWY:
Pracodawca: Twoja Firma Sp. z o.o., NIP 1112223344, z siedzibą w Warszawie przy ul. Prostej 10
Pracownik: Jan Kowalski, PESEL: 85021512345, Seria i nr dowodu osobistego: ABC 123456 (wydany przez Prezydenta Miasta Warszawy), zamieszkały: ul. Kwiatowa 5/12, 02-500 Warszawa.

WARUNKI ZATRUDNIENIA:
Stanowisko: Główny Magazynier i Koordynator Logistyki
Miejsce wykonywania pracy: Magazyn Centralny, ul. Magazynowa 1, Pruszków
Wymiar czasu pracy: 1/1 pełnego wymiaru (cały etat)
Wynagrodzenie zasadnicze: 6 500,00 PLN brutto miesięcznie
Dodatek funkcyjny: 500,00 PLN brutto
Data rozpoczęcia pracy: 01.11.2026
Podpisy stron: Jan Kowalski (Pracownik), Marek Nowak - Prezes Zarządu (Pracodawca)"""
    },

    "HR_BADANIA_LEKARSKIE": {
        "title": "Orzeczenie Lekarskie Wstępne (Część A e-Teczki)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Dokument medycyny pracy kwalifikowany do Części A lub B akt osobowych z rygorystycznym zakazem przechowywania diagnoz.",
        "text": """ORZECZENIE LEKARSKIE NR 458/2026
Wydane na podstawie art. 229 Kodeksu Pracy
Data badania: 25.10.2026

Badany: Jan Kowalski, PESEL: 85021512345
Kandydat do pracy na stanowisku: Kierowca kat. C / Magazynier
Pracodawca: Twoja Firma Sp. z o.o.

Treść orzeczenia:
Wobec braku przeciwwskazań zdrowotnych orzeka się zdolność do wykonywania pracy na określonym wyżej stanowisku.
Termin kolejnego badania okresowego: 25.10.2029.
Podpis i pieczęć uprawnionego lekarza medycyny pracy: lek. med. Anna Wiśniewska, NPWZ: 7891234."""
    },

    "LOGISTYKA_CMR_ADR": {
        "title": "Międzynarodowy List Przewozowy CMR (Ładunek ADR / WDT 0% VAT)",
        "category": "Logistyka & Spedycja",
        "description": "List przewozowy CMR dla transportu międzynarodowego z ładunkiem niebezpiecznym podlegającym rygorom Konwencji ADR.",
        "text": """MIĘDZYNARODOWY SAMOCHODOWY LIST PRZEWOZOWY (CMR) nr CMR/2026/PL-DE/984

1. Nadawca: Chem-Trans Sp. z o.o., ul. Przemysłowa 8, 40-001 Katowice, Polska, NIP: PL9540001122
2. Odbiorca: BASF Coatings GmbH, Glasuritstraße 1, 48165 Münster, Niemcy, VAT ID: DE123456789
3. Miejsce przeznaczenia: Magazyn Centralny BASF Münster
4. Miejsce i data załadowania: Katowice, 19.10.2026
5. Załączone dokumenty: Certyfikat jakości, Deklaracja ADR, Zgłoszenie SENT-2026-10-884
6. Cechy i numery: 24 palety, UN 1202 PALIWO DO SILNIKÓW DIESLA, 3, III, (D/E), Ilość: 12 000 litrów
Masa brutto: 10 500 kg
13. Instrukcje nadawcy: Przewóz w temperaturze kontrolowanej, kierowca z uprawnieniem ADR kl. 3
16. Przewoźnik: Logistyka Polska Trans S.A., NIP: 6760003344
24. Przesyłkę otrzymano: [PODPIS I PIECZĘĆ ODBIORCY: Münster, 21.10.2026 - Brak zastrzeżeń]"""
    },

    "P2P_3WAY_MATCHING": {
        "title": "Pakiet 3-Way Matching (Zamówienie PO + Kwit PZ + Faktura FV)",
        "category": "Proces P2P (Integracja)",
        "description": "Zestawienie trzech powiązanych dokumentów sprawdzających automatyczną zgodność wolumenów i kwot przed akceptacją płatności.",
        "text": """DOKUMENT 1: ZAMÓWIENIE ZAKUPU (Purchase Order - PO-2026-881)
Dostawca: Stal-Hurt Sp. z o.o.
Pozycja: Profil stalowy 40x40x2, Ilość: 500 sztuk, Cena jedn. netto: 30,00 PLN
Łączna wartość zamówienia netto: 15 000,00 PLN + VAT 23% (3 450,00 PLN) = 18 450,00 PLN Brutto.

DOKUMENT 2: DOWÓD PRZYJĘCIA MAGAZYNOWEGO (PZ-2026/10/412)
Magazyn: Magazyn Główny - Twoja Firma Sp. z o.o.
Dostarczono z dokumentu WZ dostawcy nr WZ/992
Pozycja: Profil stalowy 40x40x2, Ilość fizycznie przyjęta: 500 sztuk.
Stan: Towar zgodny ilościowo i jakościowo, przyjęto bez uwag dnia 19.10.2026.

DOKUMENT 3: FAKTURA VAT DOSTAWCY (FV-STAL/10/2026)
Wystawca: Stal-Hurt Sp. z o.o., NIP: 5250009988
Pozycja: Profil stalowy 40x40x2, Ilość na fakturze: 500 sztuk, Cena jedn.: 30,00 PLN
Netto: 15 000,00 PLN, VAT 23%: 3 450,00 PLN, Brutto: 18 450,00 PLN.
Mechanizm Split Payment: WYMAGANY (kwota > 15 000 PLN)."""
    }
}
