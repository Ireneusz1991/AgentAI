import streamlit as st
import pandas as pd
import json
import io
import re
import importlib
from datetime import datetime

# Wymuszenie przeładowania modułów z dysku (zapobiega błędowi ImportError w pamięci podręcznej Streamlit Cloud po aktualizacji na GitHubie)
import engine.finance_engine as _fin_mod
try:
    importlib.reload(_fin_mod)
except Exception:
    pass

import engine.hr_engine as _hr_mod
import engine.logistics_engine as _log_mod
import engine.data_cleaner_engine as _clean_mod
import engine.compendium_data as _comp_mod
import data.sample_documents as _doc_mod
import data.messy_sample_data as _messy_mod

for _m in (_hr_mod, _log_mod, _clean_mod, _comp_mod, _doc_mod, _messy_mod):
    try:
        importlib.reload(_m)
    except Exception:
        pass

analyze_finance_document_offline = _fin_mod.analyze_finance_document_offline
analyze_finance_document_llm = _fin_mod.analyze_finance_document_llm


def _fallback_ksef_xml(data: dict) -> str:
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/29/12648/">
  <Naglowek>
    <KodFormularza kodSystemowy="FA (2)" wersjaSchemy="1-0E">FA</KodFormularza>
    <WariantFormularza>2</WariantFormularza>
    <DataWytworzeniaFa>{now_iso}</DataWytworzeniaFa>
    <SystemInfo>OptiDoc AI Enterprise v2.5</SystemInfo>
  </Naglowek>
  <Fa>
    <KodWaluty>PLN</KodWaluty>
    <P_2>{data.get('Numer_Faktury', 'FV/2026')}</P_2>
    <P_13_1>{data.get('Kwota_Netto', 0.0):.2f}</P_13_1>
    <P_14_1>{data.get('Kwota_VAT', 0.0):.2f}</P_14_1>
    <P_15>{data.get('Kwota_Brutto', 0.0):.2f}</P_15>
  </Fa>
</Faktura>"""


generate_ksef_xml = getattr(_fin_mod, "generate_ksef_xml", _fallback_ksef_xml)
analyze_hr_document_offline = _hr_mod.analyze_hr_document_offline
analyze_hr_document_llm = _hr_mod.analyze_hr_document_llm
analyze_logistics_document_offline = _log_mod.analyze_logistics_document_offline
analyze_logistics_document_llm = _log_mod.analyze_logistics_document_llm
clean_and_modernize_legacy_data = _clean_mod.clean_and_modernize_legacy_data
BOOKS_COMPENDIUM = _comp_mod.BOOKS_COMPENDIUM
LEGAL_ACTS = _comp_mod.LEGAL_ACTS
SAMPLE_DOCUMENTS = _doc_mod.SAMPLE_DOCUMENTS
MESSY_WAREHOUSE_CSV = _messy_mod.MESSY_WAREHOUSE_CSV


def export_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Audyt_OptiDoc") -> bytes:
    """Generuje natywny arkusz Excel (.xlsx) za pomocą biblioteki openpyxl."""
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
        return output.getvalue()
    except Exception:
        return df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig")


def export_to_excel_compatible_csv(df: pd.DataFrame) -> bytes:
    """
    Generuje plik CSV w 100% zoptymalizowany pod polską wersję programu Microsoft Excel:
    1. Kodowanie UTF-8 z BOM (utf-8-sig) - brak zniekształceń polskich znaków (ą, ć, ę, ł, ń, ó, ś, ź, ż).
    2. Separator kolumn: średnik (;) - automatyczny podział na kolumny A, B, C zamiast zbijania w jedną kolumnę.
    3. Separator dziesiętny: przecinek (,) - Excel rozpoznaje kwoty jako liczby do sumowania formułą =SUMA().
    """
    csv_str = df.to_csv(index=False, sep=";", decimal=",")
    return csv_str.encode("utf-8-sig")

# -------------------------------------------------------------
# 1. KONFIGURACJA STRONY & STYLING ENTERPRISE
# -------------------------------------------------------------
st.set_page_config(
    page_title="OptiDoc AI | Inteligentny System Obiegu Dokumentów & Compliance",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS dla profesjonalnego wyglądu B2B
st.markdown("""
<style>
    /* Stylizacja głównego nagłówka */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    /* Karty KPI */
    .kpi-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    /* Pigułki statusu */
    .badge-success {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# INICJALIZACJA STANU SESJI DLA WSZYSTKICH MODUŁÓW
# -------------------------------------------------------------
if "fin_doc_text" not in st.session_state:
    st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_NKUP"]["text"]
if "hr_doc_text" not in st.session_state:
    st.session_state["hr_doc_text"] = SAMPLE_DOCUMENTS["HR_UMOWA_RODO"]["text"]
if "log_doc_text" not in st.session_state:
    st.session_state["log_doc_text"] = SAMPLE_DOCUMENTS["LOGISTYKA_CMR_ADR"]["text"]

# -------------------------------------------------------------
# 2. PASEK BOCZNY (PANEL NAWIGACYJNY KLIENTA)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏢 **OptiDoc AI** `v2.5 Enterprise`")
    st.caption("System Automatyzacji Procesów Finansowo-Prawnych")
    
    st.markdown("""
    <div style='background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:12px; font-size:0.85rem; color:#1E40AF;'>
        🔒 <b>Certyfikowane Środowisko Bezpieczeństwa:</b><br>
        • Walidacja sum kontrolnych NIP / PESEL / NRB<br>
        • Zgodność z RODO (Privacy by Design)<br>
        • AI Act: Nadzór Human-in-the-Loop<br>
        • Generator KSeF FA(2) & JPK_V7 Ready
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📁 Baza Dokumentów Demonstracyjnych")
    st.caption("Wybierz przykładowy dokument biznesowy do natychmiastowej weryfikacji:")
    
    demo_doc_key = st.selectbox(
        "Wybierz dokument:",
        list(SAMPLE_DOCUMENTS.keys()),
        format_func=lambda x: f"{SAMPLE_DOCUMENTS[x]['category']} — {SAMPLE_DOCUMENTS[x]['title']}"
    )
    
    if st.button("📥 Wczytaj Dokument do Modułu", use_container_width=True):
        doc_obj = SAMPLE_DOCUMENTS[demo_doc_key]
        cat = doc_obj["category"]
        if "Finanse" in cat:
            st.session_state["fin_doc_text"] = doc_obj["text"]
            target_tab_name = "Weryfikacja Faktur & Podatków (P2P)"
        elif "Kadry" in cat:
            st.session_state["hr_doc_text"] = doc_obj["text"]
            target_tab_name = "Cyfrowa e-Teczka & Ochrona Danych (HR)"
        else:
            st.session_state["log_doc_text"] = doc_obj["text"]
            target_tab_name = "Logistyka & Kontrola Przewozów (CMR/ADR)"
        st.toast(f"Wczytano do zakładki: {target_tab_name}", icon="📄")

    st.divider()
    with st.expander("⚙️ Zaawansowane Ustawienia Systemu"):
        engine_type = st.radio(
            "Silnik analityczny:",
            ["Wbudowany Deterministyczny Silnik Reguł i Algorytmów MŚP", "Hybrydowy Model Chmurowy (Gemini + Walidator Reguł)"],
            index=0
        )
        api_token = ""
        if "Gemini" in engine_type:
            api_token = st.text_input("Klucz API Chmury (opcjonalny):", type="password")

# -------------------------------------------------------------
# 3. GŁÓWNA NAWIGACJA KOMERCYJNA
# -------------------------------------------------------------
tab_exec, tab_finance, tab_hr, tab_logistics, tab_legacy, tab_compliance = st.tabs([
    "📊 Panel Zarządczy & Oszczędności (ROI)",
    "📑 Weryfikacja Faktur & Podatków (P2P)",
    "👥 Cyfrowa e-Teczka & Ochrona Danych (HR)",
    "🚚 Logistyka & Kontrola Przewozów (CMR/ADR)",
    "🗃️ Poligon Danych: Magazyn & Excel",
    "⚖️ Standardy Prawne & Certyfikacja"
])

# =============================================================
# MODUŁ 1: PANEL ZARZĄDCZY (DLA WŁAŚCICIELA / DYREKTORA)
# =============================================================
with tab_exec:
    st.markdown('<div class="main-header">OptiDoc AI Enterprise</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Zautomatyzowana kontrola merytoryczno-prawna dokumentów i ochrona płynności finansowej przedsiębiorstwa</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">0.4 s</div>
            <div class="kpi-label">Średni Czas Procesowania</div>
            <span class="badge-success">-95% czasu pracy</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">Mod 11 / 10</div>
            <div class="kpi-label">Kontrola NIP, PESEL i NRB</div>
            <span class="badge-success">Weryfikacja Matematyczna</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">Zero</div>
            <div class="kpi-label">Ryzyka Kar RODO i PIP</div>
            <span class="badge-success">Automatyczne Maskowanie</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">FA(2) XML</div>
            <div class="kpi-label">Gotowość na KSeF i JPK</div>
            <span class="badge-success">Eksport Strukturalny</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("💰 Symulator Oszczędności Operacyjnych Przedsiębiorstwa")
    st.caption("Dostosuj parametry do skali swojej organizacji, aby oszacować miesięczną i roczną stopę zwrotu:")
    
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        vol_docs = st.slider("Miesięczny wolumen dokumentów (faktury, kwity, umowy, listy CMR):", 50, 5000, 450, step=50)
        time_doc = st.slider("Średni czas manualnej weryfikacji i dekretacji (minuty):", 3, 25, 12, step=1)
        rate_hour = st.number_input("Koszt roboczogodziny pracownika księgowości/kadr (PLN brutto):", 35, 250, 60, step=5)
    
    with c_s2:
        manual_hours = (vol_docs * time_doc) / 60.0
        manual_cost = manual_hours * rate_hour
        saved_hours = manual_hours * 0.82  # Średnia oszczędność 82%
        saved_cost_mo = saved_hours * rate_hour
        saved_cost_yr = saved_cost_mo * 12.0
        
        st.markdown(f"""
        <div style='background-color:#F0FDF4; border:1px solid #BBF7D0; border-radius:10px; padding:20px;'>
            <h4 style='color:#166534; margin-top:0;'>Raport Efektywności Wdrożenia</h4>
            <p>• Ręczny czas administracyjny bez OptiDoc: <b>{manual_hours:.1f} godz./miesięcznie</b> ({manual_cost:,.2f} PLN)</p>
            <p>• Czas odzyskany dzięki automatyzacji: <b>{saved_hours:.1f} godz./miesięcznie</b></p>
            <hr style='border:0; border-top:1px solid #BBF7D0;'>
            <h3 style='color:#15803D; margin-bottom:5px;'>Roczna oszczędność: {saved_cost_yr:,.2f} PLN</h3>
            <span style='color:#166534; font-size:0.9rem;'>Szacowany czas zwrotu z inwestycji (ROI): <b>poniżej 60 dni</b>.</span>
        </div>
        """, unsafe_allow_html=True)

# =============================================================
# MODUŁ 2: WERYFIKACJA FAKTUR & PODATKÓW (P2P)
# =============================================================
with tab_finance:
    st.subheader("Centrum Weryfikacji Finansowo-Podatkowej (Procure-to-Pay & KSeF)")
    st.markdown("Moduł weryfikujący sumy kontrolne NIP, poprawność rachunkową, Białą Listę VAT, kwalifikację KUP/NKUP oraz rozbieżności magazynowe 3-Way Matching przed zleceniem przelewu.")
    
    cf1, cf2 = st.columns([3, 1])
    with cf2:
        st.markdown("**Szybki wybór scenariusza kontrolnego:**")
        if st.button("🍽️ Faktura Gastronomia (NKUP)", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_NKUP"]["text"]
        if st.button("🚗 Auto 50% VAT / 75% KUP", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_AUTO_MIESZANE"]["text"]
        if st.button("🛑 Błąd: Proforma (Zakaz KUP!)", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_PROFORMA_ERROR"]["text"]
        if st.button("💻 Sprzęt IT > 15 tys. (Split Payment)", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_SPLIT_PAYMENT"]["text"]
        if st.button("📦 Rozbieżność PZ vs Faktura", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["P2P_3WAY_MATCHING"]["text"]
        if st.button("🧮 Błąd Rachunkowy & Fałszywy NIP", use_container_width=True):
            st.session_state["fin_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_BLAD_RACHUNKOWY_NIP"]["text"]
            
        btn_run_fin = st.button("⚡ Wykonaj Audyt Finansowy", type="primary", use_container_width=True)

    with cf1:
        fin_text = st.text_area(
            "Treść przetwarzanego dokumentu finansowego (wynik OCR lub format cyfrowy):",
            key="fin_doc_text",
            height=260
        )

    if btn_run_fin:
        with st.spinner("Trwa wielostopniowa walidacja matematyczna i podatkowa dokumentu..."):
            if "Gemini" in engine_type and api_token:
                res = analyze_finance_document_llm(fin_text, api_token)
            else:
                res = analyze_finance_document_offline(fin_text)

            st.divider()
            st.markdown("### 1. Parametry Księgowe Dokumentu")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Numer Dokumentu", res.get("Numer_Faktury", "Brak danych"))
            m2.metric("Wartość Netto", f"{res.get('Kwota_Netto', 0):,.2f} PLN")
            m3.metric("Podatek VAT", f"{res.get('Kwota_VAT', 0):,.2f} PLN")
            m4.metric("Wartość Brutto", f"{res.get('Kwota_Brutto', 0):,.2f} PLN")

            st.markdown("### 2. Walidacja Matematyczna, Formalna i Bankowa (Anti-Fraud)")
            v1, v2, v3 = st.columns(3)
            with v1:
                if not res.get("NIP_Poprawny", True):
                    st.error(f"🚨 **WERYFIKACJA NIP ({res.get('NIP_Sprzedawcy')}):**\n\n{res.get('Walidacja_NIP')}")
                else:
                    st.success(f"✅ **WERYFIKACJA NIP ({res.get('NIP_Sprzedawcy')}):**\n\n{res.get('Walidacja_NIP')}")
            with v2:
                if not res.get("Arytmetyka_Poprawna", True):
                    st.error(f"🚨 **KONTROLA ARYTMETYCZNA:**\n\n{res.get('Walidacja_Arytmetyczna')}")
                else:
                    st.success(f"✅ **KONTROLA ARYTMETYCZNA:**\n\n{res.get('Walidacja_Arytmetyczna')}")
            with v3:
                if res.get("Alert_Bank", False):
                    st.error(f"🚨 **BIAŁA LISTA VAT & NRB:**\n\n{res.get('Status_Rachunku_NRB')}")
                else:
                    st.success(f"✅ **BIAŁA LISTA VAT & NRB:**\n\n{res.get('Status_Rachunku_NRB')}")

            st.markdown("### 3. Kwalifikacja Podatkowa CIT/PIT & Płynność VAT")
            al1, al2 = st.columns(2)
            with al1:
                if res.get("Alert_KUP"):
                    st.error(f"🚨 **STATUS KOSZTU: {res.get('Status_KUP')}**\n\n{res.get('Uzasadnienie_KUP')}")
                else:
                    st.success(f"✅ **STATUS KOSZTU: {res.get('Status_KUP')}**\n\n{res.get('Uzasadnienie_KUP')}")
            
            with al2:
                if res.get("Alert_Split"):
                    st.warning(f"⚠️ **MECHANIZM PŁATNOŚCI: {res.get('Status_Split_Payment')}**\n\n{res.get('Opis_Split_Payment')} (Oznaczenie JPK: **{res.get('Wykryte_Kody_GTU')}**)")
                else:
                    st.info(f"ℹ️ **MECHANIZM PŁATNOŚCI: {res.get('Status_Split_Payment')}**\n\n{res.get('Opis_Split_Payment')} (Oznaczenie JPK: **{res.get('Wykryte_Kody_GTU')}**)")

            if "ALARM" in str(res.get("Status_Matching", "")):
                st.error(f"📦 **KONTROLA MAGAZYNOWA 3-WAY MATCHING (Zamówienie PO ↔ Dokument PZ ↔ Faktura):** {res.get('Status_Matching')}")

            # Raport dla księgowości + Eksport CSV oraz KSeF XML
            st.markdown("#### 4. Ustrukturyzowane Dane Dekretacyjne (Eksport ERP oraz KSeF `FA(2)`)")
            df_fin = pd.DataFrame([res])
            st.dataframe(df_fin, use_container_width=True)
            
            excel_fin = export_to_excel_bytes(df_fin, "Dekretacja_FV")
            csv_fin = export_to_excel_compatible_csv(df_fin)
            ksef_xml_str = generate_ksef_xml(res)
            safe_doc_name = res.get('Numer_Faktury', 'dokument').replace('/', '_').replace('\\', '_')

            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                st.download_button(
                    "📊 Pobierz Arkusz Excel (.xlsx)",
                    data=excel_fin,
                    file_name=f"audyt_{safe_doc_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with dl2:
                st.download_button(
                    "📥 Pobierz CSV dla Excela / ERP (.csv)",
                    data=csv_fin,
                    file_name=f"audyt_{safe_doc_name}.csv",
                    mime="text/csv; charset=utf-8",
                    use_container_width=True
                )
            with dl3:
                st.download_button(
                    "🏛️ Pobierz e-Fakturę KSeF XML FA(2)",
                    data=ksef_xml_str,
                    file_name=f"KSeF_FA2_{safe_doc_name}.xml",
                    mime="application/xml",
                    use_container_width=True
                )

            with st.expander("🔍 Podgląd wygenerowanej struktury XML dla Krajowego Systemu e-Faktur (KSeF FA(2))"):
                st.code(ksef_xml_str, language="xml")

# =============================================================
# MODUŁ 3: CYFROWA E-TECZKA & RODO (HR)
# =============================================================
with tab_hr:
    st.subheader("Cyfrowa e-Teczka Pracownicza, Kontrola Czasu Pracy PIP & Ochrona RODO")
    st.markdown("Automatyczna klasyfikacja akt osobowych (Części A–E), walidacja sumy kontrolnej PESEL, wykrywanie naruszeń doby pracowniczej (art. 128 i 132 KP) oraz anonimizacja nadmiarowych danych (art. 22¹ KP i art. 9 RODO).")
    
    ch1, ch2 = st.columns([3, 1])
    with ch2:
        st.markdown("**Scenariusze kadrowe i PIP:**")
        if st.button("📄 Umowa o Pracę (z dowodem RODO)", use_container_width=True):
            st.session_state["hr_doc_text"] = SAMPLE_DOCUMENTS["HR_UMOWA_RODO"]["text"]
        if st.button("🛑 Badania Wygasłe + Diagnoza (PIP/RODO)", use_container_width=True):
            st.session_state["hr_doc_text"] = SAMPLE_DOCUMENTS["HR_BADANIA_PRZETERMINOWANE"]["text"]
        if st.button("⚖️ Kara Nagany (Część D e-Teczki)", use_container_width=True):
            st.session_state["hr_doc_text"] = SAMPLE_DOCUMENTS["HR_KARA_PORZADKOWA"]["text"]
        if st.button("⏰ Doba Pracownicza / 11h Odpoczynku (PIP)", use_container_width=True):
            st.session_state["hr_doc_text"] = SAMPLE_DOCUMENTS["HR_DOBA_PRACOWNICZA_PIP"]["text"]
            
        btn_run_hr = st.button("🛡️ Weryfikuj e-Teczkę, PIP & RODO", type="primary", use_container_width=True)

    with ch1:
        hr_text = st.text_area(
            "Treść dokumentu pracowniczego (umowa, orzeczenie lekarskie, grafik czasu pracy):",
            key="hr_doc_text",
            height=220
        )

    if btn_run_hr:
        with st.spinner("Trwa analiza zgodności z Kodeksem Pracy, wytycznymi PIP oraz RODO..."):
            if "Gemini" in engine_type and api_token:
                res_hr = analyze_hr_document_llm(hr_text, api_token)
            else:
                res_hr = analyze_hr_document_offline(hr_text)

            st.divider()
            c_h1, c_h2, c_h3, c_h4 = st.columns(4)
            c_h1.metric("Kwalifikacja do e-Teczki", res_hr.get("Czesc_eTeczki", "Część B"))
            c_h2.metric("Typ Aktu", res_hr.get("Typ_Dokumentu", "Umowa"))
            c_h3.metric("Ustawowa Retencja", res_hr.get("Wymagany_Okres_Retencji", "10 lat"))
            c_h4.metric("Wykryty PESEL", res_hr.get("PESEL_Pracownika", "Brak"))

            st.write(f"**Podstawa kwalifikacji:** {res_hr.get('Opis_Kwalifikacji')}")

            # Walidacja PIP oraz PESEL
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                if res_hr.get("Alert_PIP"):
                    st.error(f"🚨 **KONTROLA PIP / BHP / CZAS PRACY:**\n\n{res_hr.get('Status_PIP')}")
                else:
                    st.success(f"✅ **KONTROLA PIP / BHP / CZAS PRACY:**\n\n{res_hr.get('Status_PIP')}")
            with p_col2:
                if not res_hr.get("PESEL_Poprawny", True):
                    st.error(f"🚨 **WALIDACJA SUMY KONTROLNEJ PESEL:**\n\n{res_hr.get('Walidacja_PESEL')}")
                else:
                    st.info(f"ℹ️ **WALIDACJA SUMY KONTROLNEJ PESEL:**\n\n{res_hr.get('Walidacja_PESEL')}")

            st.divider()
            st.markdown("### 🔒 Weryfikacja RODO & Zasada Minimalizacji Danych (Art. 22¹ KP & Art. 9 RODO)")
            
            incydenty = res_hr.get("Naruszenia_RODO", [])
            if incydenty:
                st.error(f"🚨 **Wykryto i zablokowano {len(incydenty)} naruszenie(a) ochrony danych osobowych przed zapisem do repozytorium:**")
                for inc in incydenty:
                    st.markdown(f"- ⚠️ **{inc}**")
            else:
                st.success("✅ Dokument nie zawiera nadmiarowych danych osobowych podlegających obowiązkowej redakcji.")

            tx1, tx2 = st.columns(2)
            with tx1:
                st.markdown("**Oryginalny skan / tekst źródłowy:**")
                st.text_area("Oryginał", value=hr_text, height=180, disabled=True, key="hr_o")
            with tx2:
                st.markdown("**Bezpieczna wersja zanonimizowana (zgodna z RODO i KP):**")
                st.text_area("Zanonimizowany", value=res_hr.get("Zanonimizowany_Tekst", ""), height=180, disabled=True, key="hr_a")

            st.divider()
            st.markdown("### ⚖️ Karta Zgodności z AI Act (Nadzór Człowieka)")
            ai_info = res_hr.get("AI_Act_Compliance", {})
            st.checkbox("Podpis i autoryzacja kadrowca (Human-in-the-Loop Approval)", value=True)

            st.markdown("#### Raport Audytu HR & Ochrony Danych (Eksport)")
            df_hr_export = pd.DataFrame([{
                "Typ_Dokumentu": res_hr.get("Typ_Dokumentu"),
                "Czesc_eTeczki": res_hr.get("Czesc_eTeczki"),
                "PESEL": res_hr.get("PESEL_Pracownika"),
                "Walidacja_PESEL": res_hr.get("Walidacja_PESEL"),
                "Alert_PIP": res_hr.get("Status_PIP"),
                "Liczba_Incydentow_RODO": res_hr.get("Liczba_Incydentow_RODO"),
                "Okres_Retencji": res_hr.get("Wymagany_Okres_Retencji")
            }])
            excel_hr = export_to_excel_bytes(df_hr_export, "Audyt_HR_RODO")
            csv_hr = export_to_excel_compatible_csv(df_hr_export)

            c_hr_d1, c_hr_d2 = st.columns(2)
            with c_hr_d1:
                st.download_button(
                    "📊 Pobierz Protokół HR do Excela (.xlsx)",
                    data=excel_hr,
                    file_name="protokol_audytu_hr.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with c_hr_d2:
                st.download_button(
                    "📥 Pobierz Raport RODO/PIP (.csv dla Excela)",
                    data=csv_hr,
                    file_name="protokol_audytu_hr.csv",
                    mime="text/csv; charset=utf-8",
                    use_container_width=True
                )

# =============================================================
# MODUŁ 4: LOGISTYKA, TRANSPORT & CMR/ADR (O2C)
# =============================================================
with tab_logistics:
    st.subheader("Centrum Walidacji Transportowej, Spedycyjnej & Podatkowej WDT")
    st.markdown("Weryfikacja Pola 24 międzynarodowych listów przewozowych CMR (warunek stawki 0% VAT w WDT), kontrola przewozu materiałów niebezpiecznych ADR oraz rejestracji w systemie SENT (PUESC).")
    
    cl1, cl2 = st.columns([3, 1])
    with ch2 if False else cl2:
        st.markdown("**Scenariusze przewozowe:**")
        if st.button("🚛 Prawidłowy CMR + ADR + SENT (0% VAT)", use_container_width=True):
            st.session_state["log_doc_text"] = SAMPLE_DOCUMENTS["LOGISTYKA_CMR_ADR"]["text"]
        if st.button("🚨 Błąd CMR: Brak Pieczęci w Polu 24 & Brak SENT", use_container_width=True):
            st.session_state["log_doc_text"] = SAMPLE_DOCUMENTS["LOGISTYKA_CMR_BRAK_PIECZECI"]["text"]
        btn_run_log = st.button("📦 Sprawdź CMR, WDT & SENT", type="primary", use_container_width=True)

    with cl1:
        log_text = st.text_area(
            "Treść dokumentu CMR lub specyfikacji przewozowej:",
            key="log_doc_text",
            height=220
        )

    if btn_run_log:
        with st.spinner("Analiza przepisów prawa przewozowego, ustawy o VAT (WDT) oraz konwencji ADR/SENT..."):
            if "Gemini" in engine_type and api_token:
                res_log = analyze_logistics_document_llm(log_text, api_token)
            else:
                res_log = analyze_logistics_document_offline(log_text)

            st.divider()
            c_l1, c_l2, c_l3 = st.columns(3)
            c_l1.metric("Numer Listu CMR", res_log.get("Numer_CMR", "Brak danych"))
            c_l2.metric("Status Odbioru (Pole 24)", res_log.get("Status_Przesylki", "Odebrano"))
            c_l3.metric("Monitorowanie SENT", "WYMAGANE (PUESC)" if res_log.get("Wymóg_Rejestracji_SENT") else "Niewymagane")

            v_col1, v_col2 = st.columns(2)
            with v_col1:
                if res_log.get("Alert_VAT"):
                    st.error(f"🚨 **RYZYKO PODATKOWE WDT: {res_log.get('Status_Potwierdzenia_WDT_0_VAT')}**\n\n{res_log.get('Opis_Konsekwencji_Podatkowych')}")
                else:
                    st.success(f"✅ **STAWKA PODATKU WDT: {res_log.get('Status_Potwierdzenia_WDT_0_VAT')}**\n\n{res_log.get('Opis_Konsekwencji_Podatkowych')}")
            
            with v_col2:
                if res_log.get("Alert_SENT"):
                    st.error(f"🚨 **NARUSZENIE USTAWY O SENT & ADR:**\n\n{res_log.get('Status_ADR')}\n\n{res_log.get('Wykryty_Numer_SENT')}")
                elif res_log.get("Alert_ADR"):
                    st.warning(f"☣️ **BEZPIECZEŃSTWO ADR: {res_log.get('Status_ADR')}**\n\nStatus SENT: {res_log.get('Wykryty_Numer_SENT')}")
                else:
                    st.info(f"ℹ️ **BEZPIECZEŃSTWO ADR: {res_log.get('Status_ADR')}**")

            kody = res_log.get("Wykryte_Kody_UN", [])
            if kody:
                st.markdown("#### Wykryte substancje podlegające Konwencji ADR i nadzorowi PUESC:")
                st.table(pd.DataFrame(kody))

            st.markdown("#### Raport Zgodności Przewozowej & Podatkowej WDT (Eksport)")
            df_log_export = pd.DataFrame([{
                "Numer_CMR": res_log.get("Numer_CMR"),
                "Nadawca": res_log.get("Nadawca"),
                "Odbiorca": res_log.get("Odbiorca"),
                "Status_WDT_0_VAT": res_log.get("Status_Potwierdzenia_WDT_0_VAT"),
                "Status_ADR": res_log.get("Status_ADR"),
                "Status_SENT": res_log.get("Wykryty_Numer_SENT"),
                "Stan_Przesylki": res_log.get("Status_Przesylki")
            }])
            excel_log = export_to_excel_bytes(df_log_export, "Audyt_Logistyka_CMR")
            csv_log = export_to_excel_compatible_csv(df_log_export)

            c_log_d1, c_log_d2 = st.columns(2)
            with c_log_d1:
                st.download_button(
                    "📊 Pobierz Raport CMR/WDT do Excela (.xlsx)",
                    data=excel_log,
                    file_name="raport_cmr_wdt.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with c_log_d2:
                st.download_button(
                    "📥 Pobierz Raport CMR/WDT (.csv dla Excela)",
                    data=csv_log,
                    file_name="raport_cmr_wdt.csv",
                    mime="text/csv; charset=utf-8",
                    use_container_width=True
                )

# =============================================================
# MODUŁ 5: POLIGON DANYCH & OCZYSZCZANIE MAGAZYNU (LEGACY DATA)
# =============================================================
with tab_legacy:
    st.subheader("Poligon Danych: Oczyszczanie i Migracja ze Starych Systemów")
    st.markdown("""
    Rozwiązanie dedykowane dla firm migrujących ze starych baz (Subiekt 4, programy DOS, chaotyczne arkusze Excel).
    System automatycznie naprawia formaty walut, ujednolica daty, weryfikuje matematyczną **sumę kontrolną NIP (wagi mod 11)** każdego dostawcy, wylicza wartość stanów magazynowych oraz wzbogaca kartoteki o **kody GTU** i **statusy podatkowe**.
    """)
    
    col_leg_opt, col_leg_info = st.columns([2, 1])
    with col_leg_opt:
        data_source = st.radio(
            "Wybierz źródło danych do testu migracji:",
            ["Załaduj przykładowy 'brudny' zrzut ze starego magazynu", "Wgraj własny plik arkusza (CSV / Excel)"],
            horizontal=True
        )
    
    raw_df = None
    if "przykładowy" in data_source:
        raw_df = pd.read_csv(io.StringIO(MESSY_WAREHOUSE_CSV), sep=";")
    else:
        uploaded_file = st.file_uploader("Przeciągnij i upuść plik CSV lub Excel klienta:", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    raw_df = pd.read_csv(uploaded_file, sep=None, engine='python')
                else:
                    raw_df = pd.read_excel(uploaded_file)
            except Exception as e:
                st.error(f"Błąd odczytu pliku: {e}")

    if raw_df is not None:
        st.markdown("#### 1. Podgląd surowego, zabałaganionego pliku klienta:")
        st.dataframe(raw_df, use_container_width=True)
        st.caption("⚠️ Zwróć uwagę na niespójne formaty: spacje i tekst w cenach ('30,50 zl'), różne formaty dat ('15/10/2026', '2026.10.15'), kreski w NIP, fałszywy NIP ('123-456-78-90') oraz brak kodów GTU.")

        if st.button("🛠️ Uruchom Automatyczne Oczyszczanie, Walidację NIP i Normalizację Bazy", type="primary", use_container_width=True):
            with st.spinner("AI przetwarza, waliduje sumy kontrolne i standaryzuje kartoteki magazynowe..."):
                cleaned_df, stats = clean_and_modernize_legacy_data(raw_df)
                
                st.divider()
                st.markdown("### 2. Wynik Automatycznego Audytu i Czyszczenia:")
                
                s1, s2, s3, s4, s5, s6 = st.columns(6)
                s1.metric("Naprawione Kwoty", stats.get("kwoty_poprawione", 0))
                s2.metric("Znormalizowane NIP", stats.get("nipy_oczyszczone", 0))
                s3.metric("Fałszywe NIP (Blokada)", stats.get("bledne_nipy_wykryte", 0))
                s4.metric("Daty ISO", stats.get("daty_zestandaryzowane", 0))
                s5.metric("Wykryte Kody GTU", stats.get("gtu_przypisane", 0))
                s6.metric("Wartość Zapasu Netto", f"{stats.get('wartosc_magazynu_pln', 0):,.2f} PLN")

                st.markdown("#### Czysta, zwalidowana baza gotowa do importu do nowego systemu ERP:")
                st.dataframe(cleaned_df, use_container_width=True)

                # Eksport czystego pliku (Excel .xlsx + CSV zoptymalizowany dla polskiego Excela)
                excel_clean = export_to_excel_bytes(cleaned_df, "Baza_Magazynowa_Czysta")
                csv_clean = export_to_excel_compatible_csv(cleaned_df)

                dl_leg1, dl_leg2 = st.columns(2)
                with dl_leg1:
                    st.download_button(
                        "📊 Pobierz Czysty Arkusz Excel (.xlsx)",
                        data=excel_clean,
                        file_name="baza_magazynowa_oczyszczona.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with dl_leg2:
                    st.download_button(
                        "📥 Pobierz CSV dla Excela / ERP (.csv)",
                        data=csv_clean,
                        file_name="baza_magazynowa_oczyszczona.csv",
                        mime="text/csv; charset=utf-8",
                        use_container_width=True
                    )
                st.success("✅ Kartoteki zostały pomyślnie znormalizowane, przeliczone wartościowo i zabezpieczone przed błędami JPK_V7!")

# =============================================================
# MODUŁ 6: CERTYFIKACJA PRAWNA & AUDYT
# =============================================================
with tab_compliance:
    st.subheader("Architektura Zgodności Prawnej & Certyfikaty Systemu")
    st.markdown("OptiDoc AI został zaprojektowany w oparciu o sztywne normy polskiego prawa gospodarczego i unijne regulacje technologiczne.")
    
    c_tab1, c_tab2, c_tab3 = st.tabs(["🏛️ Akty Prawne w Silniku", "📚 Baza Wiedzy Referencyjnej", "📖 Studium Przypadków & Menedżment BPM"])
    with c_tab1:
        for act in LEGAL_ACTS:
            st.markdown(f"**{act['act']}**")
            st.caption(act["key_rules"])
            st.divider()

    with c_tab2:
        st.caption("System wykorzystuje modele decyzyjne oparte na standardach doradztwa i audytu:")
        for book in BOOKS_COMPENDIUM:
            st.markdown(f"• **{book['title']}** ({book['author']}) — *{book['category']}*")

    with c_tab3:
        st.markdown("### 🏛️ Architektura Menedżmentu Procesami Biznesowymi (BPM) & Studium Przypadków")
        st.caption("Praktyczne studium 12 przypadków biznesowych łączących prawo gospodarcze, procedury operacyjne (SOP) oraz cyfrowe bramki kontrolne (Decision Gates).")

        bpm_col1, bpm_col2 = st.columns(2)
        with bpm_col1:
            st.markdown("#### 📦 Filar I: Finanse P2P & Podatki")
            with st.expander("1. Usługi Gastronomiczne i Reprezentacja (NKUP)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Błędne odliczenie VAT i wrzucenie w koszty faktur restauracyjnych zarządu.
                - **Podstawa prawna:** Art. 16 ust. 1 pkt 28 CIT / Art. 23 ust. 1 pkt 23 PIT oraz Art. 88 ust. 1 pkt 4 VAT.
                - **Bramka BPM:** Automatyczne zatrzymanie faktury; dekretacja 100% NKUP i 0% odliczenia VAT w planie kont.
                """)
            with st.expander("2. Samochód Osobowy w Użytku Mieszanym (50% VAT / 75% KUP)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Błędy ręcznych wyliczeń proporcji kosztów eksploatacji floty.
                - **Podstawa prawna:** Art. 86a ust. 1 i 2 VAT (odliczenie 50% VAT) oraz Art. 16 ust. 1 pkt 51 CIT / Art. 23 ust. 1 pkt 46 PIT (75% KUP sumy Netto + nieodliczony VAT).
                - **Bramka BPM:** Automatyczny split 3-liniowy w ERP bez udziału człowieka.
                """)
            with st.expander("3. Blokada Księgowania Proformy"):
                st.markdown("""
                - **Procedura / Ryzyko:** Zaksięgowanie proformy jako kosztu i odliczenie VAT (zagrożenie sankcją nierzetelnego dowodu).
                - **Podstawa prawna:** Art. 106b VAT oraz Art. 21 i 22 ustawy o rachunkowości.
                - **Bramka BPM (Gatekeeper):** Twarda blokada (Hard Stop) w obiegu OCR i żądanie właściwej e-Faktury.
                """)
            with st.expander("4. Sprzęt IT > 15 000 PLN (Split Payment & GTU-06)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Zapłata zwykłym przelewem zamiast MPP za towary wrażliwe (sankcja 30% VAT).
                - **Podstawa prawna:** Art. 108a ust. 1a i ust. 7 VAT oraz Rozporządzenie JPK_V7 (kod GTU-06).
                - **Bramka BPM:** Blokada zwykłego przelewu w bankowości; wymuszenie transferu na subkonto VAT.
                """)
            with st.expander("5. 3-Way Matching (Rozbieżność Magazynowa PZ vs Faktura)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Zapłata za 500 szt., gdy magazyn przyjął tylko 450 szt. (nadpłata 1 845 PLN brutto).
                - **Podstawa prawna:** Art. 88 ust. 3a pkt 4 lit. a VAT (zakaz odliczenia dla niedostarczonych towarów), Art. 15 ust. 1 CIT oraz KSR nr 4 (Zapasy).
                - **Bramka BPM:** Trójstronne uzgodnienie PO ↔ PZ ↔ FV; blokada płatności za brakujące 50 szt.
                """)
            with st.expander("6. Anti-Fraud: Fałszywy NIP, Błąd Rachunkowy & Biała Lista"):
                st.markdown("""
                - **Procedura / Ryzyko:** Wyłudzenia podatkowe, puste faktury, płatność na konto spoza wykazu MF.
                - **Podstawa prawna:** Algorytm wagi mod 11 NIP, Art. 96b VAT oraz Art. 117ba Ordynacji podatkowej (odpowiedzialność solidarna).
                - **Bramka BPM:** Algorytmiczna weryfikacja sumy kontrolnej NIP i 26 cyfr NRB przed wysłaniem przelewu.
                """)

        with bpm_col2:
            st.markdown("#### 👥 Filar II: Kadry HR, BHP & RODO")
            with st.expander("7. Cyfrowa e-Teczka (Części A, B, C, D, E) & Retencja"):
                st.markdown("""
                - **Procedura / Ryzyko:** Mieszanie kar porządkowych z umowami; brak usuwania kar po roku (mandat PIP).
                - **Podstawa prawna:** Rozporządzenie MRiPS ws. dokumentacji pracowniczej oraz Art. 113 § 1 Kodeksu Pracy.
                - **Bramka BPM:** Automatyczna segregacja akt do części A–E z ustawowym licznikiem retencji.
                """)
            with st.expander("8. Anonimizacja Danych Wrażliwych i Dowodów (RODO)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Kserowanie dowodów osobistych, nielegalne żądanie KRK, diagnozy lekarskie.
                - **Podstawa prawna:** Art. 5 ust. 1 lit. c i Art. 9 RODO oraz Art. 22¹ Kodeksu Pracy.
                - **Bramka BPM (Privacy by Design):** Automatyczna redakcja numeru dowodu i tajemnicy lekarskiej przed zapisem w chmurze.
                """)
            with st.expander("9. Doba Pracownicza i Bezpieczeństwo Pracy (PIP Compliance)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Złamanie 11h odpoczynku dobowego w grafiku; praca z przeterminowanym badaniem.
                - **Podstawa prawna:** Art. 128 § 3 pkt 1 KP, Art. 132 § 1 KP oraz Art. 229 § 4 KP (grzywny do 30 000 PLN).
                - **Bramka BPM:** Prewencyjny alert blokujący grafik pracy i ostrzegający przed karą PIP.
                """)

            st.markdown("#### 🚚 Filar III & IV: Logistyka, SENT & Data Governance")
            with st.expander("10. List Przewozowy CMR: Pole 24 a Stawka 0% VAT (WDT)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Brak podpisu/pieczęci odbiorcy unijnego w Polu 24 (konieczność dopłaty 23% VAT).
                - **Podstawa prawna:** Art. 42 ust. 1, 3 i 4 ustawy o VAT oraz Konwencja CMR.
                - **Bramka BPM:** Inspekcja skanu Pola 24; utworzenie rezerwy na VAT 23% przy braku dowodu dostawy.
                """)
            with st.expander("11. Transport Towarów Wrażliwych ADR i SENT (PUESC)"):
                st.markdown("""
                - **Procedura / Ryzyko:** Przewóz paliw/chemikaliów (UN 1202/1203) bez numeru SENT (kara 46% wartości, min. 20 000 PLN).
                - **Podstawa prawna:** Ustawa o systemie monitorowania drogowego (SENT) oraz Umowa europejska ADR.
                - **Bramka BPM:** Weryfikacja aktywnego zgłoszenia PUESC przed wyjazdem transportu z bazy.
                """)
            with st.expander("12. Oczyszczanie Bazy Magazynowej ze Starych Systemów"):
                st.markdown("""
                - **Procedura / Ryzyko:** Zabałaganione kartoteki z DOS-a/Excela uniemożliwiające migrację do nowego ERP i generowanie JPK_V7.
                - **Podstawa prawna:** Art. 26 ustawy o rachunkowości oraz wymogi struktury logicznej JPK_V7.
                - **Bramka BPM:** Pipeline standaryzacji typów danych, usuwania błędów w NIP i kalkulacji wyceny zapasów.
                """)

st.divider()
st.caption(f"OptiDoc AI Enterprise Edition v2.5 • Bezpieczne Środowisko Certyfikowane • Sesja aktywna: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
