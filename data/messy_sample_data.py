"""
Generator przykładowych, zabałaganionych danych ze starego systemu magazynowego / księgowego (Legacy System).
Zawiera typowe błędy z polskich MŚP:
- Niespójne formaty dat (np. 2026/10/12, 15/10/2026, 18.10.2026)
- Błędne kwoty (spacje, przecinki, 'zł', 'PLN')
- Numery NIP z kreskami, prefiksem PL oraz fałszywą sumą kontrolną (np. 123-456-78-90)
- Brakujące kody GTU JPK_V7 oraz wydatki NKUP ukryte w kartotekach zakupowych
"""

MESSY_WAREHOUSE_CSV = """KOD_TOWARU_STARY;NAZWA_ARTYKULU;CENA_ZAKUPU;STAN_MAGAZYN;STAWKA_PODATKU;NIP_DOSTAWCY;DATA_PRZYJECIA
TOW-001;  profil stalowy 40x40x2  ; 30,50 zl ; 500 szt ; 23 % ; 526-10-40-828 ; 2026-10-12
TOW-002;Olej Napedowy DIESEL Eko; 6,20 PLN ; 12000 l ; 23%;PL7740001454; 15/10/2026
TOW-003;serwer DELL PowerEdge r750;18500.00;1 szt;23;525-00-07-738;18.10.2026
TOW-004;Usluga Gastronomiczna - lunch zarzadu; 650,00 ; 1 szt ; 8% ; 123-456-78-90 ; 2026.10.15
TOW-005;  Kabel sieciowy UTP Kat 6 ; 2,40 zł ; 1500 m ; 23 % ; 954 275 46 16 ; 2026-10-19
TOW-006;Benzyna bezołowiowa 95; 5,80 PLN ; 4000 l ; 23% ; 774-000-14-54 ; 2026/10/20
"""
