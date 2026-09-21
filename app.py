import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import base64

st.set_page_config(
    page_title="Polibra Kimya - Üretim & Stok Yönetimi", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# GÖNDERİLEN ORİJİNAL POLİBRA LOGOSUNUN TAM TEMİZ SVG KODU (YORUM SATIRSIZ)
CLEAN_POLIBRA_SVG = """<svg width="260" height="60" viewBox="0 0 260 60" fill="none" xmlns="http://www.w3.org/2000/svg">
<text x="10" y="42" font-family="'Helvetica Neue', Arial, sans-serif" font-weight="300" font-size="34" fill="#000000" letter-spacing="1.5">ПОЛИБРА</text>
<path d="M195 27 L212 17 L220 32 Z" fill="url(#blue_grad)"/>
<path d="M220 7 L238 21 L219 28 Z" fill="url(#orange_grad)"/>
<path d="M218 34 L240 37 L226 50 Z" fill="url(#green_grad)"/>
<defs>
<linearGradient id="blue_grad" x1="195" y1="27" x2="220" y2="32" gradientUnits="userSpaceOnUse">
<stop stop-color="#00a8ff"/>
<stop offset="1" stop-color="#0072ce"/>
</linearGradient>
<linearGradient id="orange_grad" x1="220" y1="7" x2="238" y2="28" gradientUnits="userSpaceOnUse">
<stop stop-color="#ff9f1c"/>
<stop offset="1" stop-color="#ff4500"/>
</linearGradient>
<linearGradient id="green_grad" x1="218" y1="34" x2="240" y2="50" gradientUnits="userSpaceOnUse">
<stop stop-color="#2ed573"/>
<stop offset="1" stop-color="#10ac84"/>
</linearGradient>
</defs>
</svg>"""

# SVG'Yİ KUSURSUZ RENDER İÇİN BASE64 DATA URI'YE DÖNÜŞTÜRME
svg_b64 = base64.b64encode(CLEAN_POLIBRA_SVG.encode('utf-8')).decode('utf-8')
POLIBRA_LOGO_IMG = f"data:image/svg+xml;base64,{svg_b64}"

# KURUMSAL ARAYÜZ VE BAŞLIK STİLLERİ
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
        color: #212529;
    }
    .polibra-header-card {
        background-color: #ffffff;
        border: 1px solid #e9ecef;
        padding: 14px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .polibra-sub-text {
        color: #6c757d;
        font-size: 13px;
        font-weight: 500;
    }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border-radius: 6px;
    }
    .stDataFrame, div[data-testid="stDataEditor"] {
        background-color: #ffffff !important;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div.stButton > button {
        background-color: #212529 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

VERI_DOSYASI = "sistem_verileri.json"

KULLANICILAR = {
    "Polibra1": "Tevfik123?",
    "Polibra2": "Yusif2026."
}

default_stoklar = {
    "Askom 70T":                 {"tanim": "Kalsit",                  "depo_stok": 17700.0, "yoldaki_stok": 0.0,    "lead_time": 60, "mensei": "Çin",     "usd_kg": 0.1500},
    "HL 125":                    {"tanim": "PA",                      "depo_stok": 15350.0, "yoldaki_stok": 2000.0, "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.2000},
    "HL 225":                    {"tanim": "PA",                      "depo_stok": 550.0,   "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.2500},
    "HL 100":                    {"tanim": "PA",                      "depo_stok": 1300.0,  "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.1800},
    "CAS 200":                   {"tanim": "Calcium Stearate",        "depo_stok": 3480.0,  "yoldaki_stok": 0.0,    "lead_time": 60, "mensei": "Çin",     "usd_kg": 1.8000},
    "ZNS 200":                   {"tanim": "Zinc Stearate",           "depo_stok": 11675.0, "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 2.1000},
    "PL 390":                    {"tanim": "Hydrotalcite",            "depo_stok": 1980.0,  "yoldaki_stok": 0.0,    "lead_time": 45, "mensei": "Avrupa",  "usd_kg": 3.5000},
    "AC 390":                    {"tanim": "Hydrotalcite",            "depo_stok": 700.0,   "yoldaki_stok": 0.0,    "lead_time": 45, "mensei": "Avrupa",  "usd_kg": 3.4000},
    "Nikomag A7":                {"tanim": "Magnesium hydroxide",     "depo_stok": 340.0,   "yoldaki_stok": 0.0,    "lead_time": 60, "mensei": "Çin",     "usd_kg": 2.8000},
    "PO CAC":                    {"tanim": "Calcium acetylacetonate", "depo_stok": 4750.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 4.2000},
    "Calcium acetylacetonate":   {"tanim": "Calcium acetylacetonate", "depo_stok": 575.0,   "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 4.1000},
    "PO SB":                     {"tanim": "Steorail bezoil Metan",   "depo_stok": 3300.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 5.0000},
    "PO 125 A":                  {"tanim": "Theic",                   "depo_stok": 3600.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 3.1000},
    "Theic":                     {"tanim": "Theic",                   "depo_stok": 875.0,   "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 3.0000},
    "BPA CCP":                   {"tanim": "BPA",                     "depo_stok": 675.0,   "yoldaki_stok": 0.0,    "lead_time": 60, "mensei": "Çin",     "usd_kg": 2.2000},
    "BPA TOZ":                   {"tanim": "BPA",                     "depo_stok": 25.0,    "yoldaki_stok": 0.0,    "lead_time": 60, "mensei": "Çin",     "usd_kg": 2.1500},
    "EW 169":                    {"tanim": "Ester wax",               "depo_stok": 4775.0,  "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 2.9000},
    "RL 59":                     {"tanim": "Ester wax",               "depo_stok": 450.0,   "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 2.8500},
    "RL 69":                     {"tanim": "Ester wax",               "depo_stok": 1200.0,  "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 2.9500},
    "PEW 20":                    {"tanim": "PE WAX - HİGH GRADE",     "depo_stok": 6000.0,  "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.6000},
    "RL 200":                    {"tanim": "PE WAX - HİGH GRADE",     "depo_stok": 1675.0,  "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.6500},
    "PEW 220":                   {"tanim": "PE WAX",                  "depo_stok": 19400.0, "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.4000},
    "Syntowax":                  {"tanim": "PE WAX",                  "depo_stok": 760.0,   "yoldaki_stok": 0.0,    "lead_time": 15, "mensei": "Lokal",   "usd_kg": 1.5000},
    "FT 110 A":                  {"tanim": "FT WAX",                  "depo_stok": 7200.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 1.9000},
    "RL 110 A":                  {"tanim": "FT WAX",                  "depo_stok": 2100.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 1.8500},
    "Kope97":                    {"tanim": "Stabilizör Katkı",       "depo_stok": 11000.0, "yoldaki_stok": 0.0,    "lead_time": 30, "mensei": "Avrupa",  "usd_kg": 2.5000},
    "MLA Lead St.":              {"tanim": "Lead Stearate",           "depo_stok": 6200.0,  "yoldaki_stok": 0.0,    "lead_time": 30, "mensei": "Avrupa",  "usd_kg": 2.5000},
    "Aerosil R 972":             {"tanim": "Silicon oxide",           "depo_stok": 440.0,   "yoldaki_stok": 0.0,    "lead_time": 30, "mensei": "Avrupa",  "usd_kg": 8.5000},
    "MAVİ":                      {"tanim": "Pigment",                 "depo_stok": 80.0,    "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 12.0000},
    "MOR":                       {"tanim": "Pigment",                 "depo_stok": 33.0,    "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 15.0000},
    "BSK PVC":                   {"tanim": "PVC",                     "depo_stok": 1100.0,  "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 1.1000},
    "Andcarb CT2K":              {"tanim": "Kalsit",                  "depo_stok": 175.0,   "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 0.1800},
    "Niğtaş":                    {"tanim": "Kalsit",                  "depo_stok": 75.0,    "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 0.1200},
    "SPK":                       {"tanim": "SPK",                     "depo_stok": 175.0,   "yoldaki_stok": 0.0,    "lead_time": 7,  "mensei": "Lokal",   "usd_kg": 1.0000}
}

default_receteler = {
    "ORS-5 PB": {
        "batch_kg": 1000.0,
        "icerik": {
            "Askom 70T": {"phr": 3.50, "batch_kg": 61.0},
            "HL 125": {"phr": 1.234, "batch_kg": 21.5},
            "CAS 200": {"phr": 0.338, "batch_kg": 5.9},
            "ZNS 200": {"phr": 1.664, "batch_kg": 29.0},
            "PL 390": {"phr": 0.275, "batch_kg": 4.8},
            "Nikomag A7": {"phr": 0.585, "batch_kg": 10.2},
            "PO CAC": {"phr": 0.585, "batch_kg": 10.2},
            "PO SB": {"phr": 0.275, "batch_kg": 4.8},
            "PO 125 A": {"phr": 0.275, "batch_kg": 4.8},
            "BPA CCP": {"phr": 0.092, "batch_kg": 1.6},
            "EW 169": {"phr": 0.619, "batch_kg": 10.8},
            "PEW 20": {"phr": 0.619, "batch_kg": 10.8},
            "FT 110 A": {"phr": 1.274, "batch_kg": 22.2},
            "Kope97": {"phr": 0.316, "batch_kg": 5.52},
            "MAVİ": {"phr": 0.0033, "batch_kg": 0.058},
            "MOR": {"phr": 0.0, "batch_kg": 0.0}
        }
    }
}

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.stoklar = data.get("stoklar", default_stoklar)
                st.session_state.receteler = data.get("receteler", default_receteler)
                st.session_state.uretim_gecmisi = data.get("uretim_gecmisi", [])
                
                for r_adi, r_val in st.session_state.receteler.items():
                    icerik_dict = {}
                    old_icerik = r_val.get("icerik", r_val.get("phr_oranlari", r_val.get("batch_miktarlari", {})))
                    for k, v in old_icerik.items():
                        if isinstance(v, dict):
                            icerik_dict[k] = v
                        else:
                            icerik_dict[k] = {"phr": float(v)/10.0 if float(v)>10 else float(v), "batch_kg": float(v)}
                    r_val["icerik"] = icerik_dict
                return
        except Exception:
            pass
    st.session_state.stoklar = default_stoklar
    st.session_state.receteler = default_receteler
    st.session_state.uretim_gecmisi = []

def nihai_kaydet_ve_cik():
    data = {
        "stoklar": st.session_state.stoklar,
        "receteler": st.session_state.receteler,
        "uretim_gecmisi": st.session_state.uretim_gecmisi
    }
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    st.session_state.logged_in = False
    st.session_state.user = ""

def snapshot_al():
    st.session_state.undo_stoklar = json.loads(json.dumps(st.session_state.stoklar))
    st.session_state.undo_receteler = json.loads(json.dumps(st.session_state.receteler))
    st.session_state.undo_uretim_gecmisi = json.loads(json.dumps(st.session_state.uretim_gecmisi))
    st.session_state.can_undo = True

def undo_yap():
    if st.session_state.get("can_undo", False):
        st.session_state.stoklar = json.loads(json.dumps(st.session_state.undo_stoklar))
        st.session_state.receteler = json.loads(json.dumps(st.session_state.undo_receteler))
        st.session_state.uretim_gecmisi = json.loads(json.dumps(st.session_state.undo_uretim_gecmisi))
        st.session_state.can_undo = False
        st.toast("↩️ Son işlem hafızadan geri alındı!")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""

# ==========================================
# EKRAN 1: KULLANICI GİRİŞİ (ORİJİNAL LOGOLU - BASE64)
# ==========================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='text-align: center; background: white; padding: 25px; border-radius: 12px; border: 1px solid #e9ecef; box-shadow: 0 4px 12px rgba(0,0,0,0.06);'>
            <div style='margin-bottom: 10px;'><img src="{POLIBRA_LOGO_IMG}" style="max-width: 220px; height: auto;"></div>
            <p style='color: #6c757d; font-size: 14px; margin: 0; font-weight: 500;'>Üretim & Stok Yönetim Paneli</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Kullanıcı Adı")
            password = st.text_input("Şifre", type="password")
            submit = st.form_submit_button("🔓 Oturum Aç", use_container_width=True)

            if submit:
                if username in KULLANICILAR and KULLANICILAR[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.user = username
                    veri_yukle()
                    st.rerun()
                else:
                    st.error("❌ Hatalı Kullanıcı Adı veya Şifre!")
    st.stop()

# ==========================================
# EKRAN 2: ANA PROGRAM (ORİJİNAL LOGOLU - BASE64)
# ==========================================
if "stoklar" not in st.session_state:
    veri_yukle()
if "can_undo" not in st.session_state:
    st.session_state.can_undo = False

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div class='polibra-header-card'>
        <div><img src="{POLIBRA_LOGO_IMG}" style="height: 48px; width: auto;"></div>
        <div style='text-align: right;'>
            <div style='color: #212529; font-size: 18px; font-weight: 700;'>Üretim & Stok Paneli</div>
            <div class='polibra-sub-text'>Aktif Oturum: <b>{st.session_state.user}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("💾 KAYDET & ÇIKIŞ YAP", use_container_width=True):
        nihai_kaydet_ve_cik()
        st.toast("✅ Veriler disk'e yazıldı ve güvenli çıkış yapıldı!")
        st.rerun()

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 İmalat & Tedarik Hesabı", 
    "🛠️ İş Emri & Gerçekleşen Üretim", 
    "💰 Reçete Maliyet Hesabı (USD/KG)", 
    "🧪 Reçete Girişi & Düzenleme", 
    "📦 Depo Stok Yönetimi"
])

# ==========================================
# SEKTÖR 1: İMALAT VE TEDARİK HESABI
# ==========================================
with tab1:
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.subheader("⚙️ İhtiyaç Hesabı Parametreleri")
        secilen_recete = st.selectbox("Reçete Kodu", list(st.session_state.receteler.keys()), key="s1_recete")
        hedef_kg = st.number_input("Planlanan Üretim Miktarı (KG)", min_value=1.0, value=50000.0, step=1000.0)
        uretim_tarihi = st.date_input("Planlanan Üretim Tarihi", datetime.now() + timedelta(days=30), key="s1_tarih")

    with col_right:
        if secilen_recete in st.session_state.receteler:
            recete_info = st.session_state.receteler[secilen_recete]
            icerik_dict = recete_info.get("icerik", {})
            toplam_b_kg = sum(item.get("batch_kg", 0.0) for item in icerik_dict.values())
            bugun = datetime.now().date()

            rapor_data = []
            acik_uyarilar = []

            for hammadde, val in icerik_dict.items():
                b_kg = val.get("batch_kg", 0.0)
                if b_kg == 0:
                    continue

                gerekli_kg = (b_kg / toplam_b_kg) * hedef_kg if toplam_b_kg > 0 else 0
                detay = st.session_state.stoklar.get(hammadde, {"tanim": "-", "depo_stok": 0.0, "yoldaki_stok": 0.0, "lead_time": 7, "mensei": "Lokal"})
                
                tanim = detay.get("tanim", "-")
                depo = detay["depo_stok"]
                yoldaki = detay["yoldaki_stok"]
                toplam_stok = depo + yoldaki
                lead_time = detay["lead_time"]
                mensei = detay["mensei"]

                son_siparis_tarihi = uretim_tarihi - timedelta(days=lead_time)
                kalan_gun = (son_siparis_tarihi - bugun).days

                if toplam_stok >= gerekli_kg:
                    durum = "✅ Stok Yeterli"
                    aksiyon = "Eylem Gerekmiyor"
                else:
                    eksik_kg = gerekli_kg - toplam_stok
                    if kalan_gun < 0:
                        durum = "🚨 GECİKTİ!"
                        aksiyon = f"ACİL Sipariş! ({abs(kalan_gun)} gün gecikmede)"
                        acik_uyarilar.append(f"<b>[{tanim}] {hammadde}</b> ({mensei}): {eksik_kg:.1f} kg eksik! Gecikme: {abs(kalan_gun)} gün.")
                    elif kalan_gun == 0:
                        durum = "⚠️ BUGÜN SİPARİŞ VER"
                        aksiyon = f"Bugün en geç {eksik_kg:.1f} kg sipariş geçilmeli."
                        acik_uyarilar.append(f"<b>[{tanim}] {hammadde}</b> ({mensei}): BUGÜN {eksik_kg:.1f} kg sipariş verilmelidir.")
                    else:
                        durum = "📦 Sipariş Zamanı Yaklaşıyor"
                        aksiyon = f"En geç {son_siparis_tarihi.strftime('%d.%m.%Y')} tarihinde sipariş ver."

                rapor_data.append({
                    "Kimyasal Tanımı": tanim,
                    "Ürün Kodu": hammadde,
                    "Menşei": mensei,
                    "Gerekli Miktar (KG)": round(gerekli_kg, 3),
                    "Depo Stoku (KG)": round(depo, 3),
                    "Yoldaki Stok (KG)": round(yoldaki, 3),
                    "Tedarik (Gün)": lead_time,
                    "Son Sipariş Tarihi": son_siparis_tarihi.strftime("%d.%m.%Y"),
                    "Durum": durum,
                    "Aksiyon": aksiyon
                })

            df_rapor = pd.DataFrame(rapor_data)
            st.subheader(f"📊 {secilen_recete} Reçetesi - {hedef_kg:,.0f} KG İhtiyaç Tablosu")
            st.dataframe(df_rapor, use_container_width=True)

            if acik_uyarilar:
                st.subheader("🚨 Acil Sipariş Uyarısı!")
                for uyar in acik_uyarilar:
                    st.error(uyar, icon="⚠️")

# ==========================================
# SEKTÖR 2: İŞ EMRİ VE GERÇEKLEŞEN ÜRETİM
# ==========================================
with tab2:
    st.subheader("🛠️ İş Emri Girişi ve Otomatik Stok Düşümü")
    st.info("💡 Not: İşlemlerinizin diske kaydedilmesi için çıkış yaparken sağ üstteki 'KAYDET & ÇIKIŞ YAP' butonuna tıklayınız.")

    col_ie1, col_ie2 = st.columns(2)
    with col_ie1:
        is_emri_recete = st.selectbox("Üretilecek Reçete / Kod Seçimi", list(st.session_state.receteler.keys()), key="ie_recete")
        uretim_tarihi_giris = st.date_input("Üretim Tarihi", datetime.now(), key="ie_tarih")
    with col_ie2:
        uretilen_kg = st.number_input("Üretilen Net Miktar (KG)", min_value=1.0, value=3000.0, step=100.0)
        is_emri_no = st.text_input("İş Emri / Parti No", f"IE-{datetime.now().strftime('%Y%m%d-%H%M')}")

    if is_emri_recete in st.session_state.receteler:
        recete_info = st.session_state.receteler[is_emri_recete]
        icerik_dict = recete_info.get("icerik", {})
        toplam_b_kg = sum(item.get("batch_kg", 0.0) for item in icerik_dict.values())

        st.write("##### 📋 Düşülecek Hammadde Miktarları Önizlemesi:")
        dusum_ozet = []
        
        for hammadde, val in icerik_dict.items():
            b_kg = val.get("batch_kg", 0.0)
            if b_kg == 0:
                continue
            harcanacak_kg = (b_kg / toplam_b_kg) * uretilen_kg if toplam_b_kg > 0 else 0
            mevcut_stok = st.session_state.stoklar.get(hammadde, {}).get("depo_stok", 0.0)
            kalan_stok = mevcut_stok - harcanacak_kg
            durum_str = "✅ Yeterli" if kalan_stok >= 0 else "❌ Yetersiz Stok!"

            dusum_ozet.append({
                "Ürün Kodu": hammadde,
                "Harcanacak (KG)": round(harcanacak_kg, 3),
                "Mevcut Depo (KG)": round(mevcut_stok, 3),
                "Kalan Depo (KG)": round(kalan_stok, 3),
                "Stok Durumu": durum_str
            })
        
        st.dataframe(pd.DataFrame(dusum_ozet), use_container_width=True)

        if st.button("🏭 Üretimi İşle ve Stoktan Düş (Geçici)", type="primary"):
            snapshot_al()
            for item in dusum_ozet:
                kod = item["Ürün Kodu"]
                harcanan = item["Harcanacak (KG)"]
                if kod in st.session_state.stoklar:
                    st.session_state.stoklar[kod]["depo_stok"] = max(0.0, st.session_state.stoklar[kod]["depo_stok"] - harcanan)

            st.session_state.uretim_gecmisi.append({
                "İptal Et": False,
                "Tarih": uretim_tarihi_giris.strftime("%d.%m.%Y"),
                "İş Emri No": is_emri_no,
                "Reçete": is_emri_recete,
                "Üretilen Miktar (KG)": uretilen_kg
            })
            st.success(f"🎉 {is_emri_no} nolu üretim listeye eklendi! Kalıcı olması için çıkarken 'KAYDET & ÇIKIŞ YAP' butonuna basın.")
            st.rerun()

    st.divider()
    
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.write("### 📜 Gerçekleşen Üretim Geçmişi")
    with col_hdr2:
        if st.session_state.get("can_undo", False):
            if st.button("↩️ Son İşlemi Geri Al (Undo)", type="secondary"):
                undo_yap()
                st.rerun()

    if st.session_state.uretim_gecmisi:
        df_gecmis = pd.DataFrame(st.session_state.uretim_gecmisi)
        if "İptal Et" not in df_gecmis.columns:
            df_gecmis.insert(0, "İptal Et", False)

        edited_gecmis = st.data_editor(
            df_gecmis,
            use_container_width=True,
            key="gecmis_editor",
            column_config={
                "İptal Et": st.column_config.CheckboxColumn("Seç / İptal Et", default=False)
            },
            disabled=["Tarih", "İş Emri No", "Reçete", "Üretilen Miktar (KG)"]
        )

        if st.button("🗑️ Seçili İş Emrini İptal Et & Stokları İade Et", type="primary"):
            snapshot_al()
            yeni_gecmis = []
            for idx, row in edited_gecmis.iterrows():
                if row["İptal Et"]:
                    rec_kodu = row["Reçete"]
                    u_kg = float(row["Üretilen Miktar (KG)"])
                    if rec_kodu in st.session_state.receteler:
                        ic_dict = st.session_state.receteler[rec_kodu].get("icerik", {})
                        t_b_kg = sum(item.get("batch_kg", 0.0) for item in ic_dict.values())
                        for h_kod, val in ic_dict.items():
                            h_b_kg = val.get("batch_kg", 0.0)
                            if t_b_kg > 0 and h_kod in st.session_state.stoklar:
                                iade_kg = (h_b_kg / t_b_kg) * u_kg
                                st.session_state.stoklar[h_kod]["depo_stok"] += iade_kg
                else:
                    yeni_gecmis.append(row.to_dict())

            st.session_state.uretim_gecmisi = yeni_gecmis
            st.success("✅ Seçilen iş emirleri iptal edildi ve stoklar iade edildi.")
            st.rerun()

# ==========================================
# SEKTÖR 3: REÇETE MALİYET HESABI
# ==========================================
with tab3:
    st.subheader("💰 Net Landed Cost (Net Varış Maliyeti) ile Reçete Hesaplama")
    
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        maliyet_recete_sec = st.selectbox("Maliyeti Hesaplanacak Reçete", list(st.session_state.receteler.keys()), key="m_recete")
        rec_data = st.session_state.receteler[maliyet_recete_sec]
        batch_size_kg = st.number_input("Batch Ağırlığı (KG)", min_value=1.0, value=float(rec_data.get("batch_kg", 1000.0)), step=50.0)

    with col_m2:
        if st.session_state.get("can_undo", False):
            if st.button("↩️ Son Maliyet Değişikliğini Geri Al (Undo)", type="secondary"):
                undo_yap()
                st.rerun()

    rec_icerik = rec_data.get("icerik", {})
    toplam_b_kg = sum(item.get("batch_kg", 0.0) for item in rec_icerik.values())
    toplam_phr_val = sum(item.get("phr", 0.0) for item in rec_icerik.values())

    maliyet_tablosu = []
    toplam_maliyet_usd = 0.0

    for hammadde, val in rec_icerik.items():
        b_kg = val.get("batch_kg", 0.0)
        phr = val.get("phr", 0.0)
        if b_kg == 0 and phr == 0:
            continue
        
        batch_miktari_kg = (b_kg / toplam_b_kg) * batch_size_kg if toplam_b_kg > 0 else 0

        detay = st.session_state.stoklar.get(hammadde, {})
        usd_kg = float(detay.get("usd_kg", 1.0000))
        
        maliyet_batch_usd = batch_miktari_kg * usd_kg
        toplam_maliyet_usd += maliyet_batch_usd

        maliyet_tablosu.append({
            "Kimyasal Tanımı": detay.get("tanim", "-"),
            "Ürün Kodu": hammadde,
            "Kullanım Oranı (PHR)": round(phr, 4),
            "1 Batch İçin Gereken (KG)": round(batch_miktari_kg, 3),
            "Landed Cost (USD/KG)": float(usd_kg),
            "Batch Maliyet (USD)": round(maliyet_batch_usd, 2)
        })

    if maliyet_tablosu:
        toplam_b_kg_sum = sum(x["1 Batch İçin Gereken (KG)"] for x in maliyet_tablosu)
        maliyet_tablosu.append({
            "Kimyasal Tanımı": "TOPLAM",
            "Ürün Kodu": "-",
            "Kullanım Oranı (PHR)": round(toplam_phr_val, 4),
            "1 Batch İçin Gereken (KG)": round(toplam_b_kg_sum, 3),
            "Landed Cost (USD/KG)": None,
            "Batch Maliyet (USD)": round(toplam_maliyet_usd, 2)
        })

    df_maliyet = pd.DataFrame(maliyet_tablosu)
    
    st.write("##### 💵 Reçete Bileşenleri & Landed Cost Birim Fiyat Girişi:")
    edited_maliyet = st.data_editor(
        df_maliyet,
        use_container_width=True,
        key="maliyet_editor",
        column_config={
            "Landed Cost (USD/KG)": st.column_config.NumberColumn(
                "Landed Cost (USD/KG)", 
                format="$%.4f", 
                step=0.0001,
                min_value=0.0
            )
        },
        disabled=["Kimyasal Tanımı", "Ürün Kodu", "Kullanım Oranı (PHR)", "1 Batch İçin Gereken (KG)", "Batch Maliyet (USD)"]
    )

    birim_maliyet_usd_kg = toplam_maliyet_usd / batch_size_kg if batch_size_kg > 0 else 0

    st.write("---")
    st.subheader("📌 Reçete Maliyet Özeti:")
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("1 KG Ürün Hammadde Maliyeti", f"${birim_maliyet_usd_kg:.4f} / KG")
    c_m2.metric(f"1 Batch ({batch_size_kg:,.0f} KG) Maliyeti", f"${toplam_maliyet_usd:,.2f}")
    c_m3.metric("1 Ton (1.000 KG) Maliyeti", f"${birim_maliyet_usd_kg * 1000:,.2f}")

    if st.button("🔄 Birim Fiyat Değişikliklerini Uygula (Geçici)", type="primary"):
        snapshot_al()
        for idx, row in edited_maliyet.iterrows():
            kod = row["Ürün Kodu"]
            if kod in st.session_state.stoklar and row["Landed Cost (USD/KG)"] is not None:
                yeni_fiyat = float(row["Landed Cost (USD/KG)"])
                st.session_state.stoklar[kod]["usd_kg"] = yeni_fiyat
        st.success("✅ Fiyatlar güncellendi. Kalıcı olması için çıkışta 'KAYDET & ÇIKIŞ YAP' butonuna basın.")
        st.rerun()

# ==========================================
# SEKTÖR 4: REÇETE GİRİŞİ (STOKTAN SEÇİMLİ SİSTEM)
# ==========================================
with tab4:
    if "show_new_recipe_form" not in st.session_state:
        st.session_state.show_new_recipe_form = False

    stoktaki_urunler_listesi = list(st.session_state.stoklar.keys())

    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.subheader("🧪 Reçete Yönetimi & Sadece Stoktan Ürün Seçimi")
        st.caption("📌 **Kullanım Kuralları:** Hammaddeleri **sadece depodaki stok listesinden seçebilirsiniz.** 1 Batch (KG) miktarını girin, hedef PHR oranını belirleyip butona basın. Sistem orantılayıp PHR değerlerini otomatik hesaplar.")
    with col_top2:
        if st.session_state.get("can_undo", False):
            if st.button("↩️ Son Reçete İşlemini Geri Al (Undo)", type="secondary"):
                undo_yap()
                st.rerun()

    c_sel1, c_sel2 = st.columns([2.5, 1.5])
    with c_sel1:
        duzenlenecek_recete = st.selectbox("Düzenlenecek / İncelediğiniz Reçete", list(st.session_state.receteler.keys()), key="edit_rec_select_v25")
    with c_sel2:
        st.write("<br>", unsafe_allow_html=True)
        btn_txt = "❌ Kapat" if st.session_state.show_new_recipe_form else "➕ Yeni Reçete Oluştur"
        if st.button(btn_txt, type="secondary", use_container_width=True):
            st.session_state.show_new_recipe_form = not st.session_state.show_new_recipe_form
            st.rerun()

    # YENİ REÇETE OLUŞTURMA PANELİ
    if st.session_state.show_new_recipe_form:
        st.markdown("---")
        st.write("### ➕ Yeni Reçete Tanımlama Formu")
        st.info("💡 Ürün kodları doğrudan depodan seçilmektedir. Manuel yeni kod girilemez.")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            yeni_recete_kodu = st.text_input("Yeni Reçete Kodu / Adı (Örn: ORS-10 PB)", value="ORS-10 PB")
        with c_n2:
            yeni_batch_kg = st.number_input("Standart Batch / Mikser Ağırlığı (KG)", min_value=1.0, value=1000.0, step=50.0)

        st.write("##### 📋 Stoktan Katkı Seçimi & 1 Batch Miktarı Girişi:")
        
        if "new_rec_rows" not in st.session_state:
            st.session_state.new_rec_rows = pd.DataFrame([
                {"Ürün Kodu": stoktaki_urunler_listesi[0] if stoktaki_urunler_listesi else "", "1 Batch İçin Gereken (KG)": 60.0},
                {"Ürün Kodu": stoktaki_urunler_listesi[1] if len(stoktaki_urunler_listesi)>1 else "", "1 Batch İçin Gereken (KG)": 20.0}
            ])

        edited_new_rec = st.data_editor(
            st.session_state.new_rec_rows,
            num_rows="dynamic",
            use_container_width=True,
            key="new_rec_editor_v25",
            column_config={
                "Ürün Kodu": st.column_config.SelectboxColumn(
                    "Ürün Kodu (Stoktan Seç)",
                    options=stoktaki_urunler_listesi,
                    required=True
                )
            }
        )

        target_phr_new = st.number_input("🎯 Bu Reçetenin Toplam Kullanım Oranı (PHR)", min_value=0.01, value=3.5, format="%.4f", step=0.1, key="target_phr_new_v25")

        if st.button("💾 Yeni Reçeteyi Hesapla, Kaydet ve Listeye Ekle", type="primary", use_container_width=True):
            if not yeni_recete_kodu.strip():
                st.error("Lütfen geçerli bir Reçete Kodu giriniz!")
            else:
                snapshot_al()
                yeni_icerik_dict = {}
                toplam_b_kg_new = edited_new_rec["1 Batch İçin Gereken (KG)"].sum()

                for idx, row in edited_new_rec.iterrows():
                    kod_v = str(row["Ürün Kodu"]).strip() if pd.notnull(row["Ürün Kodu"]) else ""
                    b_kg_v = float(row["1 Batch İçin Gereken (KG)"]) if pd.notnull(row["1 Batch İçin Gereken (KG)"]) else 0.0
                    
                    phr_v = (b_kg_v / toplam_b_kg_new) * target_phr_new if toplam_b_kg_new > 0 else 0.0

                    if kod_v:
                        yeni_icerik_dict[kod_v] = {"phr": phr_v, "batch_kg": b_kg_v}

                st.session_state.receteler[yeni_recete_kodu.strip()] = {
                    "batch_kg": yeni_batch_kg,
                    "icerik": yeni_icerik_dict
                }
                st.session_state.show_new_recipe_form = False
                st.success(f"🎉 '{yeni_recete_kodu}' reçetesi {target_phr_new:.4f} PHR oranına göre başarıyla oluşturuldu!")
                st.rerun()

    # MEVCUT REÇETE DÜZENLEME PANELİ
    rec_info = st.session_state.receteler[duzenlenecek_recete]
    rec_icerik = rec_info.get("icerik", {})

    st.markdown("---")
    
    # PHR GİRDİ VE OTOMATİK ORAN-ORANTI HESAPLAMA PANELİ
    c_scale1, c_scale2 = st.columns([2, 3])
    with c_scale1:
        mevcut_phr_sum = sum(val.get("phr", 0.0) for val in rec_icerik.values())
        target_phr = st.number_input("🎯 Hedef Reçete Kullanım Oranı (PHR)", min_value=0.01, value=float(mevcut_phr_sum) if mevcut_phr_sum > 0 else 3.5, format="%.4f", step=0.1, key="target_phr_v25")
    
    with c_scale2:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("⚡ PHR Sütununu Orantılayıp Otomatik Hesapla", type="primary", use_container_width=True):
            snapshot_al()
            toplam_batch_kg_sum = sum(val.get("batch_kg", 0.0) for val in rec_icerik.values())
            if toplam_batch_kg_sum > 0:
                for kod, val in rec_icerik.items():
                    b_kg = val.get("batch_kg", 0.0)
                    val["phr"] = (b_kg / toplam_batch_kg_sum) * target_phr
                st.session_state.receteler[duzenlenecek_recete]["icerik"] = rec_icerik
                st.toast(f"🎉 PHR sütunu {target_phr:.4f} PHR toplamı olacak şekilde orantılanarak güncellendi!")
                st.rerun()

    st.markdown("---")
    st.write(f"##### 📋 '{duzenlenecek_recete}' Reçete Bileşenleri Tablosu:")

    rec_tablo_data = []
    top_phr = 0.0
    top_bkg = 0.0

    for kod, val in rec_icerik.items():
        tanim = st.session_state.stoklar.get(kod, {}).get("tanim", "-")
        phr_v = float(val.get("phr", 0.0))
        b_kg_v = float(val.get("batch_kg", 0.0))
        
        top_phr += phr_v
        top_bkg += b_kg_v

        rec_tablo_data.append({
            "Seç / Sil": False,
            "Kimyasal Tanımı": tanim,
            "Ürün Kodu": kod,
            "1 Batch İçin Gereken (KG)": b_kg_v,
            "Kullanım Oranı (PHR)": round(phr_v, 4)
        })

    if rec_tablo_data:
        rec_tablo_data.append({
            "Seç / Sil": False,
            "Kimyasal Tanımı": "TOPLAM",
            "Ürün Kodu": "-",
            "1 Batch İçin Gereken (KG)": round(top_bkg, 3),
            "Kullanım Oranı (PHR)": round(top_phr, 4)
        })

    df_rec_edit = pd.DataFrame(rec_tablo_data)

    edited_rec_df = st.data_editor(
        df_rec_edit,
        num_rows="dynamic",
        use_container_width=True,
        key="recete_table_editor_v25",
        disabled=["Kimyasal Tanımı"],
        column_config={
            "Ürün Kodu": st.column_config.SelectboxColumn(
                "Ürün Kodu (Stoktan Seç)",
                options=stoktaki_urunler_listesi,
                required=True
            )
        }
    )

    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        if st.button("➕ Yeni Satır (Hammadde) Ekle", type="secondary", use_container_width=True):
            default_code = stoktaki_urunler_listesi[0] if stoktaki_urunler_listesi else ""
            default_tanim = st.session_state.stoklar.get(default_code, {}).get("tanim", "-")
            new_row = pd.DataFrame([{"Seç / Sil": False, "Kimyasal Tanımı": default_tanim, "Ürün Kodu": default_code, "1 Batch İçin Gereken (KG)": 0.0, "Kullanım Oranı (PHR)": 0.0}])
            edited_rec_df = pd.concat([edited_rec_df, new_row], ignore_index=True)
            st.rerun()

    with col_b2:
        if st.button("🗑️ Seçili Satırları Reçeteden Sil", type="secondary", use_container_width=True):
            snapshot_al()
            kalan_rows = edited_rec_df[(edited_rec_df["Seç / Sil"] == False) & (edited_rec_df["Kimyasal Tanımı"] != "TOPLAM")]
            yeni_icerik = {}
            for idx, row in kalan_rows.iterrows():
                kod_val = str(row["Ürün Kodu"]).strip() if pd.notnull(row["Ürün Kodu"]) else ""
                phr_val = float(row["Kullanım Oranı (PHR)"]) if pd.notnull(row["Kullanım Oranı (PHR)"]) else 0.0
                b_kg_val = float(row["1 Batch İçin Gereken (KG)"]) if pd.notnull(row["1 Batch İçin Gereken (KG)"]) else 0.0
                if kod_val and kod_val != "-":
                    yeni_icerik[kod_val] = {"phr": phr_val, "batch_kg": b_kg_val}
            st.session_state.receteler[duzenlenecek_recete]["icerik"] = yeni_icerik
            st.success("✅ Seçili hammaddeler reçeteden çıkarıldı!")
            st.rerun()

    with col_b3:
        if st.button("💾 Reçeteyi Kaydet ve Hafızaya İşle", type="primary", use_container_width=True):
            snapshot_al()
            yeni_icerik = {}
            for idx, row in edited_rec_df.iterrows():
                if not row["Seç / Sil"] and str(row["Kimyasal Tanımı"]) != "TOPLAM":
                    kod_val = str(row["Ürün Kodu"]).strip() if pd.notnull(row["Ürün Kodu"]) else ""
                    phr_val = float(row["Kullanım Oranı (PHR)"]) if pd.notnull(row["Kullanım Oranı (PHR)"]) else 0.0
                    b_kg_val = float(row["1 Batch İçin Gereken (KG)"]) if pd.notnull(row["1 Batch İçin Gereken (KG)"]) else 0.0

                    if kod_val and kod_val != "-":
                        yeni_icerik[kod_val] = {"phr": phr_val, "batch_kg": b_kg_val}

            st.session_state.receteler[duzenlenecek_recete]["icerik"] = yeni_icerik
            st.success(f"🎉 '{duzenlenecek_recete}' reçetesi başarıyla kaydedildi!")
            st.rerun()

# ==========================================
# SEKTÖR 5: DEPO STOK YÖNETİMİ
# ==========================================
with tab5:
    col_st1, col_st2 = st.columns([3, 1])
    with col_st1:
        st.subheader("📦 Depo Stok Yönetimi ve Excel Sayım Dosyası Yükleme")
    with col_st2:
        if st.session_state.get("can_undo", False):
            if st.button("↩️ Son Stok İşlemini Geri Al (Undo)", type="secondary"):
                undo_yap()
                st.rerun()
    
    uploaded_excel = st.file_uploader("📂 Depo Sayım Excel Dosyası Yükle (.xlsx)", type=["xlsx"])
    if uploaded_excel is not None:
        try:
            snapshot_al()
            df_excel = pd.read_excel(uploaded_excel)
            df_excel.columns = df_excel.columns.str.strip()
            df_excel['Miktar Kg'] = df_excel['Miktar Kg'].fillna(0)
            
            grouped = df_excel.groupby(['Tanım', 'Ürün'], as_index=False)['Miktar Kg'].sum()
            
            yeni_stoklar = {}
            for _, row in grouped.iterrows():
                t_adi = str(row['Tanım']).strip()
                u_kodu = str(row['Ürün']).strip()
                m_kg = float(row['Miktar Kg'])
                
                eski_detay = st.session_state.stoklar.get(u_kodu, {"lead_time": 7, "mensei": "Lokal", "yoldaki_stok": 0.0, "usd_kg": 1.0000})
                yeni_stoklar[u_kodu] = {
                    "tanim": t_adi,
                    "depo_stok": m_kg,
                    "yoldaki_stok": eski_detay.get("yoldaki_stok", 0.0),
                    "lead_time": eski_detay.get("lead_time", 7),
                    "mensei": eski_detay.get("mensei", "Lokal"),
                    "usd_kg": eski_detay.get("usd_kg", 1.0000)
                }
            
            st.session_state.stoklar = yeni_stoklar
            st.success(f"✅ Excel hafızaya aktarıldı! {len(yeni_stoklar)} ürün stoku güncellendi. Kalıcı kılmak için 'KAYDET & ÇIKIŞ YAP'a basın.")
            st.rerun()
        except Exception as e:
            st.error(f"Excel hatası: {e}")

    st.write("---")
    
    stok_listesi = []
    for hammadde, val in st.session_state.stoklar.items():
        stok_listesi.append({
            "Seç / Sil": False,
            "Kimyasal Tanımı": val.get("tanim", "-"),
            "Ürün Kodu": hammadde,
            "Depo Stoku (KG)": float(val["depo_stok"]),
            "Yoldaki Stok (KG)": float(val["yoldaki_stok"]),
            "Tedarik (Gün)": int(val["lead_time"]),
            "Menşei": val["mensei"],
            "Landed Cost (USD/KG)": float(val.get("usd_kg", 1.0000))
        })
    
    df_stok_edit = pd.DataFrame(stok_listesi)
    
    edited_df = st.data_editor(
        df_stok_edit,
        num_rows="dynamic",
        use_container_width=True,
        key="stok_table_editor_v25"
    )

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        if st.button("➕ Yeni Satır (Ürün) Ekle", type="secondary", use_container_width=True):
            new_stok_row = pd.DataFrame([{
                "Seç / Sil": False, "Kimyasal Tanımı": "", "Ürün Kodu": "", "Depo Stoku (KG)": 0.0,
                "Yoldaki Stok (KG)": 0.0, "Tedarik (Gün)": 7, "Menşei": "Lokal", "Landed Cost (USD/KG)": 1.0000
            }])
            edited_df = pd.concat([edited_df, new_stok_row], ignore_index=True)
            st.rerun()

    with col_s2:
        if st.button("🗑️ Seçili Ürünleri Depodan Tamamen Sil", type="secondary", use_container_width=True):
            snapshot_al()
            kalan_stoklar = edited_df[edited_df["Seç / Sil"] == False]
            yeni_stok_dict = {}
            for idx, row in kalan_stoklar.iterrows():
                yeni_stok_dict[row["Ürün Kodu"]] = {
                    "tanim": row["Kimyasal Tanımı"],
                    "depo_stok": row["Depo Stoku (KG)"],
                    "yoldaki_stok": row["Yoldaki Stok (KG)"],
                    "lead_time": row["Tedarik (Gün)"],
                    "mensei": row["Menşei"],
                    "usd_kg": float(row["Landed Cost (USD/KG)"])
                }
            st.session_state.stoklar = yeni_stok_dict
            st.success("✅ Seçili ürünler listeden çıkarıldı!")
            st.rerun()

    with col_s3:
        if st.button("🔄 Tablodaki Değişiklikleri Listeye İşle", type="primary", use_container_width=True):
            snapshot_al()
            yeni_stok_dict = {}
            for idx, row in edited_df.iterrows():
                if not row["Seç / Sil"]:
                    u_kodu = str(row["Ürün Kodu"]).strip() if pd.notnull(row["Ürün Kodu"]) else ""
                    if u_kodu:
                        yeni_stok_dict[u_kodu] = {
                            "tanim": str(row["Kimyasal Tanımı"]).strip() if pd.notnull(row["Kimyasal Tanımı"]) else "-",
                            "depo_stok": float(row["Depo Stoku (KG)"]) if pd.notnull(row["Depo Stoku (KG)"]) else 0.0,
                            "yoldaki_stok": float(row["Yoldaki Stok (KG)"]) if pd.notnull(row["Yoldaki Stok (KG)"]) else 0.0,
                            "lead_time": int(row["Tedarik (Gün)"]) if pd.notnull(row["Tedarik (Gün)"]) else 7,
                            "mensei": str(row["Menşei"]) if pd.notnull(row["Menşei"]) else "Lokal",
                            "usd_kg": float(row["Landed Cost (USD/KG)"]) if pd.notnull(row["Landed Cost (USD/KG)"]) else 1.0000
                        }
            st.session_state.stoklar = yeni_stok_dict
            st.success("✅ Depo tablosu güncellendi. Kalıcı kayıt için sağ üstteki 'KAYDET & ÇIKIŞ YAP' butonuna tıklayınız.")
            st.rerun()
