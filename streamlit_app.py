import json
import os
import base64
from datetime import datetime

import requests
import streamlit as st

# ==========================================================
# CONFIGURAÇÃO DO SUPABASE
# ==========================================================
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ==========================================================
# CSS CUSTOMIZADO - TEMA ELEGANTE
# ==========================================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main, .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
    }

    .st-emotion-cache-1y4p8pa {
        max-width: 1200px;
        padding: 0 20px;
    }

    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
"""

# ==========================================================
# CORES E ÍCONES
# ==========================================================
ELEMENT_COLORS = {
    "Pyro": "#DC2626", "Hydro": "#0284C7", "Electro": "#7C3AED",
    "Cryo": "#38BDF8", "Geo": "#D97706", "Anemo": "#0D9488", "Dendro": "#16A34A"
}

STATUS_COLORS = {
    "Disponível": "#10B981", "Reservada": "#F59E0B", "Vendida": "#6B7280",
    "Pausada": "#7C3AED", "Farmando": "#0891B2", "Revisar": "#EF4444"
}

ELEMENT_ICONS = {
    "Pyro": "🔥", "Hydro": "💧", "Electro": "⚡", "Cryo": "❄️",
    "Geo": "🟡", "Anemo": "🌪️", "Dendro": "🌿"
}

MAP_AREAS = [
    ("mondstadt", "Mondstadt"), ("dragonspine", "Espinha do Dragão"),
    ("liyue", "Liyue"), ("chasm_surface", "Despenhadeiro - Sup."),
    ("chasm_underground", "Despenhadeiro - Sub."), ("chenyu_vale", "Vale Chenyu"),
    ("inazuma", "Inazuma"), ("enkanomiya", "Enkanomiya"),
    ("sumeru_rainforest", "Sumeru - Floresta"), ("sumeru_desert", "Sumeru - Deserto"),
    ("hadramaveth", "Hadramaveth"), ("girdle_of_the_sands", "Cinturão das Areias"),
    ("fontaine", "Fontaine"), ("sea_of_bygone_eras", "Mar das Eras Passadas"),
    ("natlan", "Natlan"), ("sacred_mountain", "Montanha Sagrada"),
    ("ancient_temple", "Templo Antigo"),
]

# ==========================================================
# FUNÇÕES DE API
# ==========================================================
@st.cache_data(ttl=30)
def fetch_accounts():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        url = f"{SUPABASE_URL}/rest/v1/public_accounts?is_visible=eq.true&order=updated_at.desc"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []


def parse_json_field(data, field):
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or []
    except Exception:
        return []


def parse_json_dict(data, field):
    try:
        val = data.get(field)
        if isinstance(val, str):
            return json.loads(val)
        return val or {}
    except Exception:
        return {}


# ==========================================================
# RENDERIZAR CARD COMPACTO
# ==========================================================
def render_compact_card(account, idx):
    """Card compacto com imagem thumbnail, expande ao clicar."""
    name = account.get("name", "Conta sem nome")
    server = account.get("server", "-")
    status = account.get("status", "-")
    ar = account.get("ar", 0)
    wl = account.get("world_level", 0)
    price = account.get("price", "-")
    tags = account.get("tags", "")

    primogems = account.get("primogems", 0)
    intertwined = account.get("intertwined_wishes", 0)
    acquaint = account.get("acquaint_wishes", 0)
    starglitter = account.get("starglitter", 0)
    stardust = account.get("stardust", 0)
    resin = account.get("fragile_resin", 0)

    characters = parse_json_field(account, "characters_json")
    weapons = parse_json_field(account, "weapons_json")
    map_progress = parse_json_dict(account, "map_progress_json")

    abyss_floor = account.get("abyss_floor", "-")
    birthday = "Sim" if account.get("birthday_set") else "Não"
    abyss = "Sim" if account.get("abyss_unlocked") else "Não"
    extra = account.get("extra_info", "")
    cover_b64 = account.get("cover_image_base64", "")

    status_color = STATUS_COLORS.get(status, "#334155")

    # ===== CARD COMPACTO =====
    with st.container():
        # Container principal com borda e sombra
        st.markdown(f"""
        <div style="background: rgba(30,41,59,0.95); border: 1px solid rgba(124,58,237,0.2); 
                    border-radius: 12px; overflow: hidden; margin-bottom: 16px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3); transition: all 0.3s;">
        </div>
        """, unsafe_allow_html=True)

        # Layout: [Imagem pequena] [Info principal] [Preço/Status]
        if cover_b64:
            cols = st.columns([1, 3, 1])
        else:
            cols = st.columns([4, 1])

        # IMAGEM THUMBNAIL (pequena, quadrada)
        if cover_b64:
            with cols[0]:
                try:
                    img_data = base64.b64decode(cover_b64)
                    st.image(img_data, width=120, use_container_width=False)
                except Exception:
                    st.markdown("<div style='width:120px;height:120px;background:#1E293B;border-radius:8px;display:flex;align-items:center;justify-content:center;'><span style='color:#64748B;font-size:24px;'>📷</span></div>", unsafe_allow_html=True)

        # INFO PRINCIPAL
        with cols[-2]:
            # Nome da conta
            st.markdown(f"<h4 style='margin:0;color:#F8FAFC;font-weight:700;'>{name}</h4>", unsafe_allow_html=True)

            # Server + AR + WL
            st.markdown(f"<p style='margin:4px 0;color:#94A3B8;font-size:13px;'>🌐 {server} • ⭐ AR {ar} • WL {wl}</p>", unsafe_allow_html=True)

            # Tags em pills pequenas
            if tags:
                tag_list = [t.strip() for t in tags.split(",") if t.strip()][:3]  # max 3 tags
                tags_html = " ".join([f'<span style="background:rgba(124,58,237,0.3);color:#C4B5FD;padding:2px 8px;border-radius:4px;font-size:11px;margin-right:4px;border:1px solid rgba(124,58,237,0.5);">{t}</span>' for t in tag_list])
                st.markdown(tags_html, unsafe_allow_html=True)

            # Personagens em linha (só ícones + nomes curtos)
            if characters:
                char_html = ""
                for char in characters[:5]:
                    el = char.get("element", "")
                    el_icon = ELEMENT_ICONS.get(el, "✦")
                    c_name = char.get("character_name", "?")
                    c_const = char.get("constellation", "")
                    char_html += f'<span style="margin-right:10px;font-size:13px;">{el_icon} <strong>{c_name}</strong> <span style="color:#94A3B8;font-size:11px;">{c_const}</span></span>'
                if len(characters) > 5:
                    char_html += f'<span style="color:#64748B;font-size:12px;">+{len(characters)-5}</span>'
                st.markdown(f"<p style='margin:8px 0 0 0;'>{char_html}</p>", unsafe_allow_html=True)

        # PREÇO + STATUS
        with cols[-1]:
            st.markdown(f"""
            <div style="text-align:right;">
                <div style="background:{status_color};color:white;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;display:inline-block;margin-bottom:8px;">
                    {status.upper()}
                </div>
                <div style="color:#10B981;font-size:22px;font-weight:800;">
                    {price}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ===== EXPANSOR DE DETALHES =====
        with st.expander("🔍 Ver detalhes completos"):
            # Recursos em grid
            st.markdown("**📦 Recursos**")
            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("💎 Primogems", f"{primogems:,}")
            with r2:
                st.metric("🌠 Limitados", intertwined)
            with r3:
                st.metric("⭐ Padrão", acquaint)

            r4, r5, r6 = st.columns(3)
            with r4:
                st.metric("✨ Starglitter", starglitter)
            with r5:
                st.metric("🌙 Stardust", stardust)
            with r6:
                st.metric("⚡ Resina", resin)

            st.divider()

            # Progresso
            st.markdown("**📊 Progresso**")
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                st.metric("🎂 Aniversário", birthday)
            with pc2:
                st.metric("🏰 Abismo", abyss)
            with pc3:
                st.metric("📈 Andar máx.", abyss_floor)

            # Exploração
            st.markdown("**🗺️ Exploração**")
            for key, label in MAP_AREAS:
                val = map_progress.get(key, 0)
                if val > 0:
                    color = "#7C3AED" if val >= 80 else "#0DCAF0" if val >= 50 else "#64748B"
                    st.progress(val / 100, text=f"{label} - {val}%")

            # Armas
            if weapons:
                st.markdown(f"**⚔️ Armas ({len(weapons)})**")
                for w in weapons[:8]:
                    wname = w.get("weapon_name", "?")
                    wchar = w.get("character_name", "-")
                    wref = w.get("refinement", "R1")
                    st.markdown(f"• **{wname}** ({wchar}) • {wref}")
                if len(weapons) > 8:
                    st.caption(f"+{len(weapons)-8} armas")

            # Observações
            if extra:
                st.markdown("**📝 Observações**")
                st.info(extra)


# ==========================================================
# APP PRINCIPAL
# ==========================================================
def main():
    st.set_page_config(
        page_title="Genshin Impact - Contas à Venda",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Header elegante
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px 30px; margin-bottom: 30px;">
        <h1 style="margin:0; color:#F8FAFC; font-size: 38px; font-weight: 800; letter-spacing: -0.5px;">
            ⚔️ Catálogo de Contas
        </h1>
        <p style="margin:8px 0 0 0; color:#94A3B8; font-size: 16px;">
            Genshin Impact • Contas verificadas e entregues com segurança
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Botão de filtros (sidebar colapsada por padrão)
    col_filter, col_count = st.columns([1, 3])
    with col_filter:
        if st.button("🔍 Filtros", use_container_width=True):
            st.session_state.show_filters = not st.session_state.get("show_filters", False)

    # Sidebar de filtros (condicional)
    if st.session_state.get("show_filters", False):
        with st.sidebar:
            st.markdown("<h3 style='color:#F8FAFC;'>Filtros</h3>", unsafe_allow_html=True)

            search = st.text_input("Buscar", "")

            status_filter = st.multiselect(
                "Status",
                ["Disponível", "Reservada", "Vendida", "Pausada", "Farmando", "Revisar"],
                default=["Disponível"]
            )

            server_filter = st.multiselect(
                "Servidor",
                ["America", "Europe", "Asia", "TW/HK/MO", "Outro"],
                default=[]
            )

            min_ar, max_ar = st.slider("AR", 1, 60, (1, 60))

            price_sort = st.selectbox(
                "Ordenar",
                ["Mais recente", "Menor preço", "Maior AR", "Mais personagens"]
            )

            if st.button("🔄 Atualizar", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
    else:
        search = ""
        status_filter = ["Disponível"]
        server_filter = []
        min_ar, max_ar = (1, 60)
        price_sort = "Mais recente"

    # Buscar dados
    accounts = fetch_accounts()

    if not accounts:
        st.warning("⚠️ Nenhuma conta disponível no momento.")
        if not SUPABASE_URL:
            st.error("🔧 SUPABASE_URL não definido.")
        return

    # Filtros
    filtered = []
    for acc in accounts:
        if status_filter and acc.get("status") not in status_filter:
            continue
        if server_filter and acc.get("server") not in server_filter:
            continue
        ar = acc.get("ar", 0)
        if ar < min_ar or ar > max_ar:
            continue
        if search:
            search_lower = search.lower()
            blob = f"{acc.get('name','')} {acc.get('tags','')}"
            chars = parse_json_field(acc, "characters_json")
            for c in chars:
                blob += f" {c.get('character_name','')}"
            if search_lower not in blob.lower():
                continue
        filtered.append(acc)

    # Ordenação
    if price_sort == "Menor preço":
        def extract_price(a):
            p = str(a.get("price", "0"))
            nums = "".join([c for c in p if c.isdigit() or c == "."])
            try:
                return float(nums) if nums else 999999
            except:
                return 999999
        filtered.sort(key=extract_price)
    elif price_sort == "Maior AR":
        filtered.sort(key=lambda x: x.get("ar", 0), reverse=True)
    elif price_sort == "Mais personagens":
        def count_chars(a):
            return len(parse_json_field(a, "characters_json"))
        filtered.sort(key=count_chars, reverse=True)

    # Contador
    with col_count:
        st.markdown(f"<p style='text-align:right;color:#94A3B8;margin:0;padding-top:10px;'>📦 {len(filtered)} contas encontradas</p>", unsafe_allow_html=True)

    st.divider()

    # Grid de cards
    if not filtered:
        st.info("Nenhuma conta encontrada com os filtros.")
    else:
        for idx, account in enumerate(filtered):
            render_compact_card(account, idx)

    # Footer
    st.markdown(f"""
    <div style="text-align:center; color:#64748B; font-size:12px; margin-top:40px; padding:20px; border-top:1px solid #1E293B;">
        Genshin Account Manager Pro • Última atualização: {datetime.now().strftime('%H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
