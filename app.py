import streamlit as st
from FSM import WarkopFSM

st.set_page_config(page_title="Logic Warkop", page_icon="☕", layout="wide")

st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;  
        border: 1px solid #e0e0e0;
    }
    .stChatMessage {
            padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

if 'bot' not in st.session_state:
    st.session_state.bot = WarkopFSM()
    st.session_state.bot.step()
    st.session_state.history = [{"role": "assistant", "content": st.session_state.bot.get_response()}]

st.title("☕ Logic Warkop - Chatbot Pemesanan Minuman")
st.markdown("Selamat datang di Logic Warkop! Silahkan pesan minuman favorit Anda dengan mengetik di bawah ini. Contoh: `pesan 2 kopi dan 1 teh`")

# --- LAYOUT UTAMA DENGAN TAB ---
tab1, tab2 = st.tabs(["💬 Chat Pemesanan", "📜 Daftar Menu"])

# === TAB 1: CHAT PEMESANAN ===
with tab1:
    col_chat, col_info = st.columns([2, 1])

    with col_info:
        st.subheader("📝 Informasi Pesanan")
        if st.session_state.bot.cart:
            total = 0
            for i, item in enumerate(st.session_state.bot.cart):
                subtotal = item["price"] * item["qty"]
                total += subtotal
                st.markdown(f"{item['emoji']} **{item['item'].capitalize()}** x {item['qty']} = Rp {subtotal:,}")
                st.caption(f"{item['qty']} x Rp {item['price']:,} = Rp {subtotal:,}")
            st.divider()
            st.metric("Total Pesanan", f"Rp {total:,}")

            if st.button("Batalkan Semua Pesanan"):
                st.session_state.bot.cart = []
                st.rerun()
        else:
            st.info("Keranjang Anda kosong. Silahkan pesan minuman dengan mengetik di kolom chat.")

        st.markdown("---")
        st.caption(f"Status Bot: `{st.session_state.bot.state.name}`")
        if st.button("Reset Sistem"):
            st.session_state.clear()
            st.rerun()

# Kolom Chat
    with col_chat:
        # Container untuk chat history
        chat_container = st.container(height=500)
        
        with chat_container:
            for msg in st.session_state.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        # Input User
        if prompt := st.chat_input("Contoh: Pesan 2 kopi dan 1 teh..."):
            # Tampilkan pesan user
            st.session_state.history.append({"role": "user", "content": prompt})
            
            # Proses di FSM
            st.session_state.bot.step(prompt)
            bot_reply = st.session_state.bot.get_response()
            
            # Simpan balasan bot
            st.session_state.history.append({"role": "assistant", "content": bot_reply})
            
            st.rerun()

# ==================== TAB 2: DAFTAR MENU ====================
with tab2:
    st.header("Daftar Menu Kami")
    st.markdown("Minuman terbaik diracik dengan *logika* dan *cinta*.")
    
    # Ambil data menu dari bot
    menu_items = st.session_state.bot.engine.menu_data  # sesuaikan path jika berbeda
    
    cols = st.columns(2)
    
    for index, (key, data) in enumerate(menu_items.items()):
        with cols[index % 2]:
            st.container()
            st.markdown(f"### {data['emoji']} {key.capitalize()}")
            st.markdown(f"*{data['desc']}*")
            st.metric(label="Harga", value=f"Rp {data['price']:,}")
            st.markdown("---")