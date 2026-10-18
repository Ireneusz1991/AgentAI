"""
Przykładowe dokumenty testowe dla systemu OptiDoc AI Enterprise.
Dokumenty zawierają realne cechy i pułapki prawno-podatkowe, kadrowe i logistyczne,
zidentyfikowane na forach księgowych (Gofin, Infor, ForumPrawne) oraz kontrolach PIP i US.
Zawierają również poprawne (oraz celowo błędne w scenariuszach awaryjnych) sumy kontrolne NIP i PESEL.
"""

SAMPLE_DOCUMENTS = {
    "FINANSE_STANDARD": {
        "title": "Faktura Kosztowa Standard (KUP - Paliwo / Poprawny NIP)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Standardowy koszt eksploatacyjny firmy z poprawną sumą kontrolną NIP i rachunkiem z Białej Listy.",
        "text": """Sprzedawca: ORLEN S.A., NIP: 7740001454
Adres: ul. Chemików 7, 09-411 Płock
Faktura nr: FS/123/10/2026
Data wystawienia: 12.10.2026
Data sprzedaży: 12.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
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
        "text": """Sprzedawca: Restauracja Złota Kaczka Jan Kowalski, NIP: 5213004450
Adres: Rynek Starego Miasta 4, 00-272 Warszawa
Faktura nr: 15/10/2026/GASTRO
Data wystawienia: 15.10.2026
Data wykonania usługi: 15.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Pozycja 1: Usługa gastronomiczna - kolacja biznesowa z kluczowym kontrahentem i alkohol
Wartość Netto: 450,00 PLN
Stawka VAT: 8%
Kwota VAT: 36,00 PLN
Wartość Brutto: 486,00 PLN
Forma płatności: Gotówka (Opłacono)
Adnotacja: Wydatki na reprezentację i usługi restauracyjne."""
    },

    "FINANSE_AUTO_MIESZANE": {
        "title": "Samochód Osobowy: Odliczenie Mieszane (50% VAT / 75% KUP)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Klasyczny błąd z forów: księgowi mylą odliczenia dla aut osobowych używanych mieszanie (art. 86a VAT i art. 16 ust. 1 pkt 51 CIT).",
        "text": """Sprzedawca: Serwis Auto-Pol Sp. z o.o., NIP: 5260250995
Faktura nr: FV/SERWIS/2026/894
Data wystawienia: 16.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Dotyczy: Naprawa i serwis samochodu osobowego Skoda Octavia nr rej. WI 98765
Pozycja 1: Wymiana klocków hamulcowych i oleju silnikowego
Wartość Netto: 2 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 460,00 PLN
Wartość Brutto: 2 460,00 PLN
Konto bankowe: 44 1020 1013 0000 9988 7766 5544
Przeznaczenie: Samochód osobowy wykorzystywany do celów mieszanych (służbowo-prywatnych)."""
    },

    "FINANSE_PROFORMA_ERROR": {
        "title": "Błąd: Próba Zaksięgowania Proformy (To nie jest faktura!)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Częsty błąd przedsiębiorców: płacą proformę i próbują ją wrzucić w koszty. System musi zablokować księgowanie.",
        "text": """DOKUMENT PROFORMA nr PF/2026/10/77
UWAGA: DOKUMENT NIE STANOWI DOWODU KSIĘGOWEGO ANI FAKTURY VAT
Sprzedawca: Agencja Reklamowa Kreatywni Sp. z o.o., NIP: 5213004450
Data wystawienia: 17.10.2026
Termin płatności: 3 dni
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Tytuł wpłaty: Zaliczka na poczet kampanii marketingowej w Google Ads
Wartość Netto: 3 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 690,00 PLN
Wartość Brutto: 3 690,00 PLN
Forma: Przelew bankowy na konto firmowe."""
    },
    
    "FINANSE_SPLIT_PAYMENT": {
        "title": "Faktura Pułapka Płynnościowa (Sprzęt IT > 15 000 PLN - Split Payment)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Faktura przekraczająca próg 15 000 zł brutto z towarem z Załącznika nr 15 do Ustawy o VAT, wymagająca obligatoryjnego MPP.",
        "text": """Sprzedawca: Hurtownia IT X-Kom Sp. z o.o., NIP: 9492107026
Adres: Al. Pokoju 12, 42-200 Częstochowa
Faktura nr: FV/2026/10/001
Data wystawienia: 18.10.2026
Data sprzedaży: 17.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Pozycja 1: Serwer bazodanowy Dell PowerEdge R750 (kod GTU-06), Ilość: 1 szt.
Wartość Netto: 14 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 3 220,00 PLN
Wartość Brutto: 17 220,00 PLN
Termin płatności: 14 dni (przelew bankowy)
Numer rachunku: 55 1090 2402 0000 0001 9876 5432
Adnotacja: Mechanizm Podzielonej Płatności (MPP)"""
    },

    "FINANSE_BLAD_RACHUNKOWY_NIP": {
        "title": "Faktura z Błędem Matematycznym i Fałszywym NIP (Oszustwo / Pomyłka)",
        "category": "Finanse & Podatki (P2P)",
        "description": "Faktura zawierająca błędną sumę kontrolną NIP sprzedawcy oraz błąd arytmetyczny (Netto + VAT != Brutto).",
        "text": """Sprzedawca: P.H.U. Widmo-Bud Janusz Tracz, NIP: 1234567890
Faktura nr: FV/999/10/2026
Data wystawienia: 19.10.2026
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Pozycja 1: Usługi remontowo-budowlane i doradcze
Wartość Netto: 10 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 2 300,00 PLN
Wartość Brutto: 13 500,00 PLN
Numer rachunku: 12 3456 7890 (Niepełny numer NRB!)"""
    },

    "P2P_3WAY_MATCHING": {
        "title": "Rozbieżność 3-Way Matching: Braki Ilościowe w Dostawie",
        "category": "Proces P2P (Integracja)",
        "description": "Na zamówieniu PO i fakturze jest 500 sztuk, ale magazyn przyjął tylko 450 sztuk. AI blokuje płatność za brakujące 50 szt!",
        "text": """DOKUMENT 1: ZAMÓWIENIE ZAKUPU (Purchase Order - PO-2026-881)
Dostawca: Stal-Hurt Sp. z o.o., NIP: 7740001454
Pozycja: Profil stalowy 40x40x2, Ilość zamówiona: 500 sztuk, Cena jedn. netto: 30,00 PLN

DOKUMENT 2: DOWÓD PRZYJĘCIA MAGAZYNOWEGO (PZ-2026/10/412)
Magazyn: Magazyn Główny - Twoja Firma Sp. z o.o.
UWAGA: ZGŁOSZONO ROZBIEŻNOŚĆ ILOŚCIOWĄ PRZY ROZŁADUNKU!
Fizycznie dostarczono i przyjęto: 450 sztuk (Brak 50 sztuk profili). Sporządzono protokół szkody/braku.

DOKUMENT 3: FAKTURA VAT DOSTAWCY
Faktura nr: FV/STAL/10/2026
Sprzedawca: Stal-Hurt Sp. z o.o., NIP: 7740001454
Nabywca: Twoja Firma Sp. z o.o., NIP: 5260250995
Pozycja: Profil stalowy 40x40x2, Ilość na fakturze: 500 sztuk (ZAFAKTUROWANO ZA DUŻO!)
Wartość Netto: 15 000,00 PLN
Stawka VAT: 23%
Kwota VAT: 3 450,00 PLN
Wartość Brutto: 18 450,00 PLN"""
    },

    "HR_UMOWA_RODO": {
        "title": "Umowa o Pracę (Część B e-Teczki + Anonimizacja Dowodu i Niekaralności)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Umowa o pracę zawierająca nadmiarowe dane osobowe (seria i nr dowodu osobistego oraz wzmiankę o zaświadczeniu o niekaralności).",
        "text": """DOKUMENT HR - SKAN 001
TYTUŁ: Umowa o pracę na czas nieokreślony
DATA ZAWARCIA: 20.10.2026
MIEJSCE ZAWARCIA: Warszawa

STRONY UMOWY:
Pracodawca: Twoja Firma Sp. z o.o., NIP 5260250995, z siedzibą w Warszawie przy ul. Prostej 10
Pracownik: Jan Kowalski, PESEL: 85021512343, Seria i nr dowodu osobistego: ABC 123456 (wydany przez Prezydenta Miasta Warszawy), zamieszkały: ul. Kwiatowa 5/12, 02-500 Warszawa.

WARUNKI ZATRUDNIENIA:
Stanowisko: Główny Magazynier i Koordynator Logistyki
Wymiar czasu pracy: 1/1 pełnego wymiaru (cały etat)
Wynagrodzenie zasadnicze: 6 500,00 PLN brutto miesięcznie
Data rozpoczęcia pracy: 01.11.2026
Załączniki dołączone do teczki: Kserokopia dowodu osobistego oraz Zaświadczenie o niekaralności z KRK."""
    },

    "HR_KARA_PORZADKOWA": {
        "title": "Kara Porządkowa Nagany (Część D e-Teczki + Retencja 1 rok)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Zawiadomienie o ukaraniu z art. 108 Kodeksu Pracy. Musi trafić do Części D i ulec zatarciu/usunięciu po 1 roku (art. 113 KP).",
        "text": """ZAWIADOMIENIE O ZASTOSOWANIU KARY PORZĄDKOWEJ
Miejscowość: Warszawa, Data: 14.10.2026
Pracodawca: Twoja Firma Sp. z o.o.
Do Pracownika: Tomasz Wiśniewski, PESEL: 85021512343
Stanowisko: Kierowca kat. C

Działając na podstawie art. 108 i 110 Kodeksu Pracy, zawiadamiam o nałożeniu na Pana KARY NAGANY
za nieusprawiedliwione opuszczenie stanowiska pracy w dniu 10.10.2026 r. oraz niestawienie się na planowany załadunek.
Pouczenie: Zgodnie z art. 112 Kodeksu Pracy ma Pan prawo wnieść sprzeciw w terminie 7 dni od otrzymania niniejszego pisma.
Podpis pracodawcy: Dyrektor ds. Operacyjnych"""
    },

    "HR_BADANIA_PRZETERMINOWANE": {
        "title": "Orzeczenie Medycyny Pracy – Ryzyko Mandatu PIP (Przeterminowane!)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Badania, których termin ważności minął. Dopuszczenie pracownika do pracy rodzi ryzyko grzywny PIP do 30 000 zł.",
        "text": """ORZECZENIE LEKARSKIE NR 112/2023
Wydane na podstawie art. 229 Kodeksu Pracy
Badany: Tomasz Wiśniewski, PESEL: 85021512343
Stanowisko: Kierowca samochodu ciężarowego powyżej 3.5t
Pracodawca: Twoja Firma Sp. z o.o.

Treść: Zdolny do wykonywania pracy na w/w stanowisku.
Rozpoznanie medyczne: Nadciśnienie tętnicze umiarkowane.
Termin kolejnego badania okresowego: 10.05.2025 r. [UWAGA: BADANIA WYGASŁY!]
Podpis lekarza uprawnionego: lek. med. Andrzej Nowak"""
    },

    "HR_DOBA_PRACOWNICZA_PIP": {
        "title": "Ewidencja Czasu Pracy – Naruszenie Doby Pracowniczej i Odpoczynku 11h (Mandat PIP)",
        "category": "Kadry & e-Teczka (HR)",
        "description": "Najczęstszy mandat PIP z forów kadrowych: naruszenie 11h odpoczynku dobowego oraz niezapłacona nadgodzina dobowa.",
        "text": """KARTA EWIDENCJI CZASU PRACY - PAŹDZIERNIK 2026
Pracownik: Marek Zieliński, PESEL: 85021512343
Stanowisko: Operator Wózka Widłowego (System zmianowy)

Harmonogram zmian:
- Poniedziałek (12.10.2026): Praca w godz. 14:00 - 22:00 (8h)
- Wtorek (13.10.2026): Praca w godz. 06:00 - 14:00 (8h) -> [UWAGA: TYLKO 8 GODZIN ODPOCZYNKU MIĘDZY ZMIANAMI! NARUSZENIE ART. 132 KP (min. 11h) ORAZ NARUSZENIE DOBY PRACOWNICZEJ (6h nadgodzin dobowych!)]
- Środa (14.10.2026): Praca w godz. 06:00 - 14:00 (8h)"""
    },

    "LOGISTYKA_CMR_ADR": {
        "title": "Prawidłowy Międzynarodowy List CMR (Ładunek ADR + Stawka 0% VAT WDT)",
        "category": "Logistyka & Spedycja",
        "description": "List przewozowy CMR z pieczęcią odbiorcy w polu 24 oraz aktywnym zgłoszeniem SENT dla towaru ADR.",
        "text": """MIĘDZYNARODOWY SAMOCHODOWY LIST PRZEWOZY (CMR) nr CMR/2026/PL-DE/984

1. Nadawca: Chem-Trans Sp. z o.o., ul. Przemysłowa 8, 40-001 Katowice, Polska, NIP: PL7740001454
2. Odbiorca: BASF Coatings GmbH, Glasuritstraße 1, 48165 Münster, Niemcy, VAT ID: DE123456789
3. Miejsce przeznaczenia: Magazyn Centralny BASF Münster
4. Miejsce i data załadowania: Katowice, 19.10.2026
5. Załączone dokumenty: Certyfikat jakości, Deklaracja ADR, Zgłoszenie SENT-2026-10-884
6. Cechy i numery: 24 palety, UN 1202 PALIWO DO SILNIKÓW DIESLA, 3, III, (D/E), Ilość: 12 000 litrów
Masa brutto: 10 500 kg
16. Przewoźnik: Logistyka Polska Trans S.A., NIP: 5260250995
24. Przesyłkę otrzymano: [PODPIS I PIECZĘĆ ODBIORCY: BASF Münster, 21.10.2026 - Towar odebrano bez zastrzeżeń]"""
    },

    "LOGISTYKA_CMR_BRAK_PIECZECI": {
        "title": "Błąd CMR: Brak Pieczęci w Polu 24 i Brak SENT (Utrata 0% VAT WDT!)",
        "category": "Logistyka & Spedycja",
        "description": "Kierowca oddał CMR bez podpisu odbiorcy w polu 24 i bez numeru SENT. Urząd Skarbowy naliczy 23% VAT zamiast 0%!",
        "text": """MIĘDZYNARODOWY SAMOCHODOWY LIST PRZEWOZOWY (CMR) nr CMR/2026/PL-FR/102

1. Nadawca: Chem-Trans Sp. z o.o., Katowice, Polska
2. Odbiorca: TotalEnergies Paris, Francja, VAT ID: FR987654321
3. Miejsce przeznaczenia: Paryż, Francja
4. Miejsce i data załadowania: Katowice, 15.10.2026
5. Załączone dokumenty: WZ/102/2026 (Brak numeru referencyjnego SENT!)
6. Cechy i numery: Cysterna, UN 1203 BENZYNA SILNIKOWA, 3, II, (D/E), Ilość: 24 000 litrów
16. Przewoźnik: Szybki-Trans Sp. z o.o.
24. Przesyłkę otrzymano: [POLE PUSTE - BRAK PODPISU I PIECZĘCI ODBIORCY]"""
    }
}
