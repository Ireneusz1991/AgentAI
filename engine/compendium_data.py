"""
Kompendium Wiedzy Wdrożeniowca AI w MŚP.
Zawiera dane o 9 kluczowych podręcznikach, aktach prawnych, matrycach procesowych oraz szablonie oferty 'Klin i Młot'.
"""

BOOKS_COMPENDIUM = [
    {
        "id": 1,
        "title": "Zarządzanie finansami przedsiębiorstwa",
        "author": "Andrzej Rutkowski",
        "publisher": "Wydawnictwo Naukowe PWN",
        "category": "Finanse Przedsiębiorstw",
        "key_topics": "Kapitał obrotowy, płynność finansowa (Cash Flow), wycena ryzyka, wskaźniki rentowności (ROE, ROA), budżetowanie.",
        "ai_application": "Budowa algorytmów priorytetyzacji faktur kosztowych i sprzedażowych pod kątem cash-flow, scoring kontrahentów, wyliczanie terminów płatności w celu uzyskania skonta."
    },
    {
        "id": 2,
        "title": "Prawo podatkowe przedsiębiorców",
        "author": "Bogumił Brzeziński",
        "publisher": "TNOiK Dom Organizatora",
        "category": "Prawo Podatkowe",
        "key_topics": "Konstrukcja zobowiązań podatkowych, kwalifikacja KUP i NKUP (art. 15 i 16 CIT, art. 22 i 23 PIT), Ordynacja Podatkowa, moment powstania obowiązku podatkowego.",
        "ai_application": "Reguły klasyfikacji podatkowej dla modeli LLM/OCR, automatyczne wykrywanie kosztów niestanowiących kosztów uzyskania przychodu (np. reprezentacja), weryfikacja dat."
    },
    {
        "id": 3,
        "title": "Projektowanie procesów biznesowych. Od strategii do operacji",
        "author": "Piotr Śliwiński",
        "publisher": "Wydawnictwo Naukowe PWN",
        "category": "Zarządzanie Procesami",
        "key_topics": "Notacja BPMN, mapowanie strumieni P2P (Procure-to-Pay) i O2C (Order-to-Cash), identyfikacja wąskich gardeł, punkty kontrolne.",
        "ai_application": "Projektowanie architektury automatyzacji: wyzwalanie zdarzeń w ERP na podstawie dokumentów cyfrowych, automatyzacja bram decyzyjnych."
    },
    {
        "id": 4,
        "title": "Akt w sprawie sztucznej inteligencji (AI Act). Komentarz",
        "author": "Red. naukowa (np. prof. D. Flisak / wyd. C.H. Beck)",
        "publisher": "Wydawnictwo C.H. Beck",
        "category": "Regulacje AI & Nadzór",
        "key_topics": "Podejście oparte na ryzyku (Risk-based approach), systemy wysokiego ryzyka (High-Risk AI), nadzór ludzki (Human-in-the-loop), transparentność i rozliczalność.",
        "ai_application": "Audyt zgodności algorytmów rekrutacyjnych i scoringowych, projektowanie rejestru decyzji AI, ochrona przed biasem i halucynacjami w dokumentacji prawnej."
    },
    {
        "id": 5,
        "title": "Kodeks pracy. Komentarz / Dokumentacja pracownicza",
        "author": "Red. K. Walczak / Monika Wacikowska",
        "publisher": "Wydawnictwo C.H. Beck / Wolters Kluwer",
        "category": "Kadry & e-Teczka",
        "key_topics": "Struktura akt osobowych (Części A, B, C, D, E), okresy retencji dokumentacji (10/50 lat), nawiązanie i rozwiązanie stosunku pracy, ewidencja czasu pracy.",
        "ai_application": "Automatyczna kategoryzacja skanów kadrowych do części e-Teczki, walidacja kompletności akt, monitoring terminów ważności szkoleń BHP i badań lekarskich."
    },
    {
        "id": 6,
        "title": "Organizacja i monitorowanie procesów magazynowych",
        "author": "Stanisław Krzyżaniak, Andrzej Niemczyk, Jerzy Majewski",
        "publisher": "Instytut Logistyki i Magazynowania (ILiM)",
        "category": "Gospodarka Magazynowa",
        "key_topics": "Dowody obrotu materiałowego (PZ, WZ, MM, RW), zarządzanie zapasami, integracja z WMS/ERP, inwentaryzacja.",
        "ai_application": "Automatyczny 3-way matching (Zamówienie PO <=> Kwit PZ <=> Faktura FV), odczyt kwitów magazynowych i wykrywanie rozbieżności ilościowych."
    },
    {
        "id": 7,
        "title": "Ogólne rozporządzenie o ochronie danych. RODO. Komentarz",
        "author": "Paweł Litwiński, Paweł Barta, Maciej Kawecki",
        "publisher": "Wydawnictwo C.H. Beck",
        "category": "Ochrona Danych (RODO)",
        "key_topics": "Zasada minimalizacji danych (art. 5 ust. 1 lit. c), Privacy by Design & Default, prawo do bycia zapomnianym, retencja danych, kary UODO.",
        "ai_application": "Moduł automatycznego maskowania (anonimizacji) nadmiarowych danych (np. seria i nr dowodu osobistego na umowie o pracę, dane wrażliwe z zaświadczeń lekarskich)."
    },
    {
        "id": 8,
        "title": "Transport i spedycja",
        "author": "Maciej Stajniak, Marcin Hajdul, Marcin Foltyński, Agnieszka Krupa",
        "publisher": "Instytut Logistyki i Magazynowania (ILiM)",
        "category": "Spedycja & Dokumenty Przewozowe",
        "key_topics": "Międzynarodowy list przewozowy CMR, konwencja CMR, zlecenia spedycyjne, warunki Incoterms, potwierdzenie dostawy w WDT (0% VAT).",
        "ai_application": "Ekstrakcja kluczowych pól z CMR (pole 24 - potwierdzenie odbioru), parowanie listów przewozowych z fakturami sprzedaży, obsługa procedury unijnej WDT."
    },
    {
        "id": 9,
        "title": "Umowa europejska dotycząca międzynarodowego przewozu towarów niebezpiecznych (ADR)",
        "author": "Wytyczne ADR / Poradniki DGSA",
        "publisher": "Oficjalne wydawnictwa rządowe / Doradca ADR",
        "category": "Ładunki Niebezpieczne (ADR)",
        "key_topics": "Numery UN, grupy pakowania, klasy zagrożeń, instrukcje pisemne dla kierowcy, wyłączenia ilościowe (1.1.3.6 ADR), system SENT.",
        "ai_application": "Weryfikacja deklaracji ADR na dokumentach przewozowych, automatyczne ostrzeganie o przewozie towarów niebezpiecznych i wymaganych certyfikatach."
    }
]

LEGAL_ACTS = [
    {
        "act": "Ustawa o podatku od towarów i usług (VAT)",
        "key_rules": "Art. 108a (Obligatoryjny Split Payment > 15 000 zł i Załącznik 15), KSeF (Krajowy System e-Faktur), Biała Lista Podatników, stawka 0% WDT z dokumentem CMR."
    },
    {
        "act": "Ustawy o PIT i CIT (Podatki Dochodowe)",
        "key_rules": "Art. 15 / 16 CIT oraz Art. 22 / 23 PIT – definicja Kosztów Uzyskania Przychodu (KUP) oraz katalog wyłączeń (NKUP - usługi gastronomiczne, reprezentacja, kary umowne)."
    },
    {
        "act": "Kodeks Pracy i Rozporządzenie ws. dokumentacji pracowniczej",
        "key_rules": "Części akt osobowych: A (rekrutacja), B (zatrudnienie), C (ustanie), D (odpowiedzialność porządkowa), E (kontrola trzeźwości / praca zdalna). Retencja: 10 lat (od 2019 r.)."
    },
    {
        "act": "Rozporządzenie Parlamentu Europejskiego (RODO)",
        "key_rules": "Art. 5 ust. 1 lit. c (minimalizacja danych – zakaz pobierania kserokopii dowodów osobistych), art. 25 (Privacy by Design), art. 32 (bezpieczeństwo przetwarzania)."
    },
    {
        "act": "Unijny Akt o Sztucznej Inteligencji (AI Act)",
        "key_rules": "Kwalifikacja systemów AI: minimalne ryzyko (OCR faktur), wysokie ryzyko (ocena pracowników w HR, scoring kredytowy B2B). Obowiązkowy Human-in-the-Loop."
    }
]

OFFER_KLIN_MLOT = {
    "title": "Strategia Ofertowa dla MŚP: Model 'Klin i Młot'",
    "stages": [
        {
            "name": "ETAP 1: KLIN (Audyt Procesowo-Merytoryczny)",
            "role": "Doradca i analityk procesów",
            "description": "Niski próg wejścia. Właściciel firmy nie kupuje 'skomplikowanego IT', lecz płatny audyt obiegu dokumentów i mapowanie wąskich gardeł.",
            "packages": [
                {"name": "Szybka Diagnoza P2P", "price": "1 500 - 2 500 PLN", "scope": "Jeden proces (faktury kosztowe), raport 3 wąskich gardeł."},
                {"name": "Kompleksowy Audyt Obiegu", "price": "4 000 - 8 000 PLN", "scope": "P2P + O2C, mapa BPMN, identyfikacja ryzyk podatkowych."},
                {"name": "Audyt Compliance + AI Blueprint", "price": "10 000+ PLN", "scope": "Finanse + Kadry (e-Teczka/RODO) + plan architektury AI."}
            ],
            "haczyk": "Koszt audytu może zostać odliczony od właściwego wdrożenia w etapie drugim!"
        },
        {
            "name": "ETAP 2: MŁOT (Wdrożenie w Piaskownicy / PoC)",
            "role": "Architekt Rozwiązań AI",
            "description": "Prezentacja na historycznych dokumentach klienta. Działa na 'cyfrowym bliźniaku' z człowiekiem w pętli (Human-in-the-Loop). Zerowe ryzyko zepsucia bazy ERP.",
            "pillars": [
                "1. Bezpieczna Piaskownica (izolowane środowisko)",
                "2. Human-in-the-loop (AI asystuje, człowiek zatwierdza)",
                "3. Mierzalny zwrot ROI (oszczędność czasu 30-70% w administracji)"
            ]
        }
    ]
}
