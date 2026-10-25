# ⚖️ Ekosystem Wdrożeniowy AI w Polskich MŚP
### Piaskownica (Sandbox) dla Wdrożeniowca Optymalizacji e-Dokumentacji

Kompleksowa platforma analityczno-wdrożeniowa łącząca **prawo podatkowe (PIT/CIT/VAT)**, **kodeks pracy i e-Teczki**, **wymogi RODO i AI Act**, **gospodarkę magazynową (PZ/WZ)** oraz **międzynarodowe prawo przewozowe (CMR/ADR)** z nowoczesnym przetwarzaniem tekstu.

---

## 🚀 Jak uruchomić aplikację?

### Sposób 1: Jeden klik (Windows)
Dwukrotnie kliknij plik:
```
run.bat
```

### Sposób 2: Z poziomu PowerShell / Terminala
```powershell
streamlit run app.py
```
Aplikacja otworzy się automatycznie w przeglądarce pod adresem: `http://localhost:8501`.

---

## 🧩 Moduły i Scenariusze Systemu

### 1. 📊 Pulpit Główny & Interaktywny Kalkulator ROI
* Oblicza realne oszczędności finansowe i czasowe dla przedsiębiorstwa (np. redukcja 80% czasu na papierologię).
* Gotowe argumenty biznesowe do rozmowy z zarządem / wspólnikiem.

### 2. 📑 Moduł 1: Finanse & Prawo Podatkowe (P2P)
* **KUP / NKUP**: Automatyczna klasyfikacja wydatków zgodnie z art. 16 ust. 1 CIT / art. 23 ust. 1 PIT (np. wyłapywanie gastronomii i reprezentacji).
* **Split Payment (MPP)**: Weryfikacja progu 15 000 PLN brutto oraz Załącznika nr 15 do Ustawy o VAT (blokada tradycyjnego przelewu).
* **Kody GTU**: Automatyczne oznaczanie na potrzeby plików JPK_V7.
* **3-Way Matching**: Weryfikacja spójności: *Zamówienie (PO) <=> Magazyn (PZ) <=> Faktura (FV)*.
* **Eksport do CSV / ERP**: Generowanie ustrukturyzowanych danych do systemów księgowych (Enova, Optima, Symfonia, KPiR).

### 3. 👥 Moduł 2: Kadry, e-Teczka Pracownicza & RODO
* **Kwalifikacja do e-Teczki**: Podział na Części **A**, **B**, **C**, **D** oraz **E** (wg Rozporządzenia MRiPS) wraz z wyznaczeniem okresu retencji (10 lat).
* **Zasada Minimalizacji Danych (Privacy by Design)**: Automatyczne wykrywanie i maskowanie nadmiarowych danych (seria i nr dowodu osobistego, wrażliwe dane zdrowotne z art. 9 RODO).
* **Nadzór AI Act**: Klasyfikacja do systemów *High-Risk AI* (Załącznik III pkt 4 AI Act) oraz obowiązkowa bramka *Human-in-the-Loop* (zatwierdzenie przez kadrowca).

### 4. 🚚 Moduł 3: Logistyka, Magazyn & CMR/ADR (O2C)
* **Weryfikacja CMR dla stawki 0% VAT (WDT)**: Kontrola pola 24 (potwierdzenie odbioru przez kontrahenta unijnego zgodnie z art. 42 ustawy o VAT).
* **Kwalifikacja ADR**: Wykrywanie numerów UN i klas zagrożeń chemicznych/paliwowych.
* **Monitoring SENT**: Weryfikacja numeru rejestracji w PUESC.

### 5. 📚 Moduł 4: Baza Wiedzy & Model Ofertowy "Klin i Młot"
* Kompendium 9 fundamentalnych podręczników akademickich (Rutkowski, Brzeziński, Śliwiński, AI Act, Walczak, Krzyżaniak, Litwiński, Stajniak, ADR).
* Przegląd kluczowych artykułów ustaw.
* Gotowy szablon 1-stronicowej oferty komercyjnej dla MŚP.

---

## 🛠️ Dwa Tryby Pracy

1. **Tryb Offline (Wbudowane Reguły MŚP)**:
   * Działa natychmiast, bezpłatnie i bez internetu.
   * Nie wymaga klucza API.
   * Idealny do błyskawicznej demonstracji wspólnikowi i klientom.

2. **Tryb Live AI (Gemini API)**:
   * Uruchamia zaawansowane modele LLM (np. `gemini-1.5-flash`).
   * Wymaga podania własnego klucza API w pasku bocznym.

---

## 📁 Struktura Projektu

```
├── app.py                      # Główny panel graficzny (Streamlit)
├── run.bat                     # Skrót do uruchomienia na Windows
├── requirements.txt            # Zależności biblioteczne Pythona
├── engine/                     # Silniki domenowe i reguły biznesowe
│   ├── finance_engine.py       # Logika podatkowa, KUP/NKUP, Split Payment
│   ├── hr_engine.py            # e-Teczka, RODO, AI Act
│   ├── logistics_engine.py     # CMR, ADR, WDT, SENT
│   └── compendium_data.py      # Baza wiedzy (książki, ustawy, oferta)
└── data/
    └── sample_documents.py     # Zbiór gotowych dokumentów do demonstracji
```
