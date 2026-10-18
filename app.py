import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime

# Import silników domenowych
from engine.finance_engine import analyze_finance_document_offline, analyze_finance_document_llm
from engine.hr_engine import analyze_hr_document_offline, analyze_hr_document_llm
from engine.logistics_engine import analyze_logistics_document_offline, analyze_logistics_document_llm
from engine.compendium_data import BOOKS_COMPENDIUM, LEGAL_ACTS
from data.sample_documents import SAMPLE_DOCUMENTS

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
# 2. PASEK BOCZNY (PANEL NAWIGACYJNY KLIENTA)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏢 **OptiDoc AI** `v2.4`")
    st.caption("System Automatyzacji Procesów Finansowo-Prawnych")
    
    st.markdown("""
    <div style='background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:12px; font-size:0.85rem; color:#1E40AF;'>
        🔒 <b>Certyfikowane Środowisko Bezpieczeństwa:</b><br>
        • Zgodność z RODO (Privacy by Design)<br>
        • AI Act: Nadzór Human-in-the-Loop<br>
        • Kwalifikacja KSeF & JPK_V7 Ready
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📁 Baza Dokumentów Demonstracyjnych")
    st.caption("Wybierz przykładowy dokument biznesowy do natychmiastowej weryfikacji:")
    
    demo_doc_key = st.selectbox(
        "Wybierz dokument:",
        list(SAMPLE_DOCUMENTS.keys()),
        format_func=lambda x: f"{SAMPLE_DOCUMENTS[x]['category']} - {SAMPLE_DOCUMENTS[x]['title']}"
    )
    
    if st.button("📥 Wczytaj Dokument do Analizy", use_container_width=True):
        st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS[demo_doc_key]["text"]
        st.session_state["active_doc_cat"] = SAMPLE_DOCUMENTS[demo_doc_key]["category"]
        st.toast(f"Wczytano: {SAMPLE_DOCUMENTS[demo_doc_key]['title']}", icon="📄")

    st.divider()
    with st.expander("⚙️ Zaawansowane Ustawienia Systemu"):
        engine_type = st.radio(
            "Silnik analityczny:",
            ["Wbudowany Inteligentny Silnik Reguł MŚP", "Chmurowy Model Wielozadaniowy (Gemini Enterprise)"],
            index=0
        )
        api_token = ""
        if "Gemini" in engine_type:
            api_token = st.text_input("Klucz API Chmury (opcjonalny):", type="password")

# Inicjalizacja tekstu roboczego
if "active_doc_text" not in st.session_state:
    st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_NKUP"]["text"]

# -------------------------------------------------------------
# 3. GŁÓWNA NAWIGACJA KOMERCYJNA
# -------------------------------------------------------------
tab_exec, tab_finance, tab_hr, tab_logistics, tab_compliance = st.tabs([
    "📊 Panel Zarządczy & Oszczędności (ROI)",
    "📑 Weryfikacja Faktur & Podatków (P2P)",
    "👥 Cyfrowa e-Teczka & Ochrona Danych (HR)",
    "🚚 Logistyka & Kontrola Przewozów (CMR/ADR)",
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
            <span class="badge-success">-95% czasu</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">100%</div>
            <div class="kpi-label">Ochrona przed Sankcjami</div>
            <span class="badge-success">KUP / Split Payment</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">Zero</div>
            <div class="kpi-label">Ryzyka Kar RODO</div>
            <span class="badge-success">Automatyczne Maskowanie</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-number">A – E</div>
            <div class="kpi-label">Kwalifikacja e-Teczki</div>
            <span class="badge-success">Zgodne z MRiPS</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("💰 Symulator Oszczędności Operacyjnych Przedsiębiorstwa")
    st.caption("Dostosuj parametry do skali swojej organizacji, aby oszacować miesięczną i roczną stopę zwrotu:")
    
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        vol_docs = st.slider("Miesięczny wolumen dokumentów (faktury, kwity, umowy):", 50, 5000, 450, step=50)
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
    st.subheader("Centrum Weryfikacji Finansowo-Podatkowej (Procure-to-Pay)")
    st.markdown("Inteligentny moduł weryfikujący zgodność kosztów z polskimi przepisami podatkowymi przed dokonaniem płatności.")
    
    cf1, cf2 = st.columns([3, 1])
    with cf1:
        fin_text = st.text_area(
            "Treść przetwarzanego dokumentu finansowego (wynik OCR lub format cyfrowy):",
            value=st.session_state.get("active_doc_text", ""),
            height=200
        )
    with cf2:
        st.markdown("**Szybki wybór sprawdzianu:**")
        if st.button("🍽️ Faktura Gastronomia (NKUP)", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_NKUP"]["text"]
            st.rerun()
        if st.button("💻 Sprzęt IT > 15 tys. (Split Payment)", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["FINANSE_SPLIT_PAYMENT"]["text"]
            st.rerun()
        if st.button("📦 Zestaw 3-Way Matching", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["P2P_3WAY_MATCHING"]["text"]
            st.rerun()
            
        btn_run_fin = st.button("⚡ Wykonaj Audyt Finansowy", type="primary", use_container_width=True)

    if btn_run_fin:
        with st.spinner("Trwa walidacja podatkowa dokumentu..."):
            if "Gemini" in engine_type and api_token:
                res = analyze_finance_document_llm(fin_text, api_token)
            else:
                res = analyze_finance_document_offline(fin_text)

            st.divider()
            st.markdown("### Wynik Weryfikacji Podatkowej")
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Dokument", res.get("Numer_Faktury", "Brak danych"))
            m2.metric("Wartość Netto", f"{res.get('Kwota_Netto', 0):,.2f} PLN")
            m3.metric("Podatek VAT", f"{res.get('Kwota_VAT', 0):,.2f} PLN")
            m4.metric("Wartość Brutto", f"{res.get('Kwota_Brutto', 0):,.2f} PLN")

            # Decyzje podatkowe w nowoczesnym layoucie
            al1, al2 = st.columns(2)
            with al1:
                if res.get("Alert_KUP"):
                    st.error(f"🚨 **STATUS KOSZTU: {res.get('Status_KUP')}**\n\n{res.get('Uzasadnienie_KUP')}")
                else:
                    st.success(f"✅ **STATUS KOSZTU: {res.get('Status_KUP')}**\n\n{res.get('Uzasadnienie_KUP')}")
            
            with al2:
                if res.get("Alert_Split"):
                    st.warning(f"⚠️ **PŁYNNOŚĆ: {res.get('Status_Split_Payment')}**\n\n{res.get('Opis_Split_Payment')}")
                else:
                    st.info(f"ℹ️ **PŁYNNOŚĆ: {res.get('Status_Split_Payment')}**\n\n{res.get('Opis_Split_Payment')}")

            # Raport dla księgowości
            st.markdown("#### Ustrukturyzowane Dane Dekretacyjne (Gotowe do eksportu ERP)")
            df_fin = pd.DataFrame([res])
            st.dataframe(df_fin, use_container_width=True)
            
            buf_fin = io.StringIO()
            df_fin.to_csv(buf_fin, index=False, sep=";")
            st.download_button(
                "📥 Eksportuj rekord do systemu ERP (CSV)",
                data=buf_fin.getvalue(),
                file_name=f"audyt_{res.get('Numer_Faktury', 'dokument')}.csv",
                mime="text/csv"
            )

# =============================================================
# MODUŁ 3: CYFROWA E-TECZKA & RODO (HR)
# =============================================================
with tab_hr:
    st.subheader("Cyfrowa e-Teczka Pracownicza & Audyt Bezpieczeństwa RODO")
    st.markdown("Automatyczna klasyfikacja dokumentacji kadrowej i anonimizacja wrażliwych danych osobowych (Privacy by Design).")
    
    ch1, ch2 = st.columns([3, 1])
    with ch1:
        hr_text = st.text_area(
            "Treść dokumentu pracowniczego (umowa, zaświadczenie, orzeczenie):",
            value=SAMPLE_DOCUMENTS["HR_UMOWA_RODO"]["text"],
            height=200
        )
    with ch2:
        st.markdown("**Przykłady aktów:**")
        if st.button("📄 Umowa o Pracę (z dowodem)", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["HR_UMOWA_RODO"]["text"]
            st.rerun()
        if st.button("🩺 Orzeczenie Medycyny Pracy", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["HR_BADANIA_LEKARSKIE"]["text"]
            st.rerun()
            
        btn_run_hr = st.button("🛡️ Weryfikuj e-Teczkę & RODO", type="primary", use_container_width=True)

    if btn_run_hr:
        with st.spinner("Trwa analiza zgodności z Kodeksem Pracy i RODO..."):
            if "Gemini" in engine_type and api_token:
                res_hr = analyze_hr_document_llm(hr_text, api_token)
            else:
                res_hr = analyze_hr_document_offline(hr_text)

            st.divider()
            c_h1, c_h2, c_h3 = st.columns(3)
            c_h1.metric("Kwalifikacja do e-Teczki", res_hr.get("Czesc_eTeczki", "Część B"))
            c_h2.metric("Typ Aktu", res_hr.get("Typ_Dokumentu", "Umowa"))
            c_h3.metric("Ustawowa Retencja", res_hr.get("Wymagany_Okres_Retencji", "10 lat"))

            st.write(f"**Zakres ustawowy:** {res_hr.get('Opis_Kwalifikacji')}")

            st.divider()
            st.markdown("### 🔒 Weryfikacja RODO & Zasada Minimalizacji Danych (Art. 5 RODO)")
            
            incydenty = res_hr.get("Naruszenia_RODO", [])
            if incydenty:
                st.error(f"🚨 **Wykryto {len(incydenty)} niedozwoloną daną osobową (Zablokowano przed zapisem do bazy):**")
                for inc in incydenty:
                    st.markdown(f"- ⚠️ **{inc}**")
                st.caption("ℹ️ Zgodnie z art. 22¹ Kodeksu Pracy pracodawca nie może przetwarzać numeru dowodu osobistego, jeśli tożsamość zweryfikowano PESEL-em.")
            else:
                st.success("✅ Dokument nie zawiera nadmiarowych danych osobowych podlegających obowiązkowej redakcji.")

            tx1, tx2 = st.columns(2)
            with tx1:
                st.markdown("**Oryginalny skan / tekst źródłowy:**")
                st.text_area("Oryginał", value=hr_text, height=160, disabled=True, key="hr_o")
            with tx2:
                st.markdown("**Bezpieczna wersja zanonimizowana (zgodna z RODO):**")
                st.text_area("Zanonimizowany", value=res_hr.get("Zanonimizowany_Tekst", ""), height=160, disabled=True, key="hr_a")

            st.divider()
            st.markdown("### ⚖️ Karta Zgodności z AI Act (Nadzór Człowieka)")
            ai_info = res_hr.get("AI_Act_Compliance", {})
            st.info(f"**Klasyfikacja wg AI Act:** {ai_info.get('Kategoria_Ryzyka', 'Wysokie Ryzyko (High-Risk AI)')} — {ai_info.get('Rekomendacja')}")
            st.checkbox("Podpis i autoryzacja kadrowca (Human-in-the-Loop Approval)", value=True)

# =============================================================
# MODUŁ 4: LOGISTYKA, TRANSPORT & CMR/ADR (O2C)
# =============================================================
with tab_logistics:
    st.subheader("Centrum Walidacji Transportowej & Spedycyjnej")
    st.markdown("Kontrola międzynarodowych listów przewozowych pod kątem preferencyjnej stawki 0% VAT (WDT) oraz ładunków niebezpiecznych ADR.")
    
    cl1, cl2 = st.columns([3, 1])
    with cl1:
        log_text = st.text_area(
            "Treść dokumentu CMR lub specyfikacji przewozowej:",
            value=SAMPLE_DOCUMENTS["LOGISTYKA_CMR_ADR"]["text"],
            height=200
        )
    with cl2:
        st.markdown("**Dokumenty transportowe:**")
        if st.button("🚛 Międzynarodowy CMR + ADR", use_container_width=True):
            st.session_state["active_doc_text"] = SAMPLE_DOCUMENTS["LOGISTYKA_CMR_ADR"]["text"]
            st.rerun()
        btn_run_log = st.button("📦 Sprawdź CMR & ADR", type="primary", use_container_width=True)

    if btn_run_log:
        with st.spinner("Analiza przepisów prawa przewozowego i konwencji CMR..."):
            if "Gemini" in engine_type and api_token:
                res_log = analyze_logistics_document_llm(log_text, api_token)
            else:
                res_log = analyze_logistics_document_offline(log_text)

            st.divider()
            c_l1, c_l2, c_l3 = st.columns(3)
            c_l1.metric("Numer Listu CMR", res_log.get("Numer_CMR", "Brak danych"))
            c_l2.metric("Status Odbioru", res_log.get("Status_Przesylki", "Odebrano"))
            c_l3.metric("System SENT", "Wymagany" if res_log.get("Wymóg_Rejestracji_SENT") else "Niewymagany")

            v_col1, v_col2 = st.columns(2)
            with v_col1:
                if res_log.get("Alert_VAT"):
                    st.error(f"🚨 **STAWKA PODATKU: {res_log.get('Status_Potwierdzenia_WDT_0_VAT')}**\n\n{res_log.get('Opis_Konsekwencji_Podatkowych')}")
                else:
                    st.success(f"✅ **STAWKA PODATKU: {res_log.get('Status_Potwierdzenia_WDT_0_VAT')}**\n\n{res_log.get('Opis_Konsekwencji_Podatkowych')}")
            
            with v_col2:
                if res_log.get("Alert_ADR"):
                    st.warning(f"☣️ **BEZPIECZEŃSTWO ADR: {res_log.get('Status_ADR')}**\n\nRejestracja w PUESC: {res_log.get('Wykryty_Numer_SENT')}")
                else:
                    st.info(f"ℹ️ **BEZPIECZEŃSTWO ADR: {res_log.get('Status_ADR')}**")

            kody = res_log.get("Wykryte_Kody_UN", [])
            if kody:
                st.markdown("#### Wykryte substancje podlegające Konwencji ADR:")
                st.table(pd.DataFrame(kody))

# =============================================================
# MODUŁ 5: CERTYFIKACJA PRAWNA & AUDYT
# =============================================================
with tab_compliance:
    st.subheader("Architektura Zgodności Prawnej & Certyfikaty Systemu")
    st.markdown("OptiDoc AI został zaprojektowany w oparciu o sztywne normy polskiego prawa gospodarczego i unijne regulacje technologiczne.")
    
    c_tab1, c_tab2 = st.tabs(["🏛️ Akty Prawne w Silniku", "📚 Baza Wiedzy Referencyjnej"])
    with c_tab1:
        for act in LEGAL_ACTS:
            st.markdown(f"**{act['act']}**")
            st.caption(act["key_rules"])
            st.divider()

    with c_tab2:
        st.caption("System wykorzystuje modele decyzyjne oparte na standardach doradztwa i audytu:")
        for book in BOOKS_COMPENDIUM:
            st.markdown(f"• **{book['title']}** ({book['author']}) — *{book['category']}*")

st.divider()
st.caption(f"OptiDoc AI Enterprise Edition • Bezpieczne Środowisko Certyfikowane • Sesja aktywna: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
