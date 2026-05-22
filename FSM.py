from enum import Enum, auto

from numpy import info
from engine import Engine

class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()

class WarkopFSM:
    def __init__(self):
        self.state = State.IDLE
        self.engine = Engine()
        self.cart = []
        self.response = ""
    
    def get_response(self):
        return self.response
    
    def calculate_total(self):
        return sum(item["price"] * item["qty"] for item in self.cart)
    
    def get_menu_text(self):
        """Fungsi bantuan untuk merangkai teks daftar menu"""
        teks_menu = "**📜 Daftar Menu Logic Warkop:**\n\n"
        for key, data in self.engine.menu_data.items():
            teks_menu += f"- {data['emoji']} **{key.capitalize()}**  (Rp {data['price']:,}): {data['desc']}\n"
        teks_menu += "\nSilahkan ketik pesanan Anda (Contoh pesan: pesan 2 kopi dan 1 teh)"
        return teks_menu
    
    def reduce_cart(self, item_to_reduce, qty_to_remove):
        """Fungsi untuk mengurangi item atau menghapusnya jika qty <= 0"""
        found = False
        message = ""

        #cari item di cart
        for item in self.cart:
            if item["item"] == item_to_reduce:
                item["qty"] -= qty_to_remove
                found = True
                if item["qty"] <= 0:
                    self.cart.remove(item)
                    message = f"❌ **{item_to_reduce}** telah dihapus dari keranjang."
                else:
                    message = f"⚠️ Jumlah **{item_to_reduce}** dikurangi {qty_to_remove}. Sisa: {item['qty']}."
                break

        if not found:
            message = f"⚠️ Gagal: **{item_to_reduce}** tidak ditemukan di keranjang Anda."

        return message
    
    def step(self, user_input=""):
        user_input = user_input.lower().strip()
        intent = self.engine.detected_intent(user_input)

        # GLOBAL RESET SYSTEM
        if self.state == "RESET_SYSTEM":
            self.__init__()  # Reset FSM
            self.response = "Sistem direset total. Selamat datang di Logic Warkop! Mau pesan apa?"
            return
        
        # STATE LOGIC: ORDERING
        if self.state == State.IDLE:
            self.response = "Halo! Selamat datang di Warkop! Mau pesan apa? Ketik 'menu' untuk melihat daftar menu."

        elif self.state == State.ORDERING:
            # FITUR: Tanya menu
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()

            # FITUR: Batalkan semua
            elif intent == "CANCEL_ALL":
                self.cart = []
                self.response = "🗑️ Keranjang Anda telah dikosongkan. Mau pesan yang lain?"

            # FITUR: Kurangi/Batalkan item tertentu
            elif intent == "REDUCE_ITEM":
                items_to_remove = self.engine.parse_orders(user_input)
                if items_to_remove:
                    results = []
                    for itm in items_to_remove:
                        res = self.reduce_cart(itm["item"], itm["qty"])
                        results.append(res)
                    self.response = "\n".join(results)
                else:
                    self.response = "⚠️ Gagal mendeteksi item yang ingin dikurangi. Pastikan formatnya benar (contoh: 'batalkan 1 kopi')."

            # FITUR: Checkout Keranjang
            elif intent == "CHECKOUT":
                if not self.cart:
                    self.response = "⚠️ Keranjang Anda kosong. Silahkan pesan terlebih dahulu."
                else:
                    self.state = State.CONFIRMATION
                    self.response = f"🧾 Total tagihan: **Rp {self.calculate_total():,}**. Ketik 'ya' untuk konfirmasi pembayaran atau 'batalkan semua' untuk mengosongkan keranjang."
                    
            else:
                # Logika Penambahan Pesanan
                new_orders = self.engine.parse_orders(user_input)
                if new_orders:
                    for order in new_orders:
                        # Cek jika item sudah ada, tambah qty saja.
                        existing = next((i for i in self.cart if i['item'] == order['item']["item"]), None)
                        if existing:
                            existing['qty'] += order['qty']
                        else:
                            # Ambil info harga dan emoji dari menu_data
                            menu_info = self.engine.menu_data.get(order['item'])
                            order.update({"price": menu_info["price"], "emoji": menu_info["emoji"], "desc": menu_info["desc"]})
                            self.cart.append(order)
                    self.response = "✅ Pesanan Anda telah ditambahkan ke keranjang. Mau pesan yang lain? Ketik 'bayar' untuk selesai"
                else:
                    self.response = "⚠️ Gagal mendeteksi pesanan. Pastikan formatnya benar (contoh: '**pesan 2 kopi dan 1 teh** atau **hapus 1 kopi**')."

         #STATE LOGIC: CONFIRMATION
        elif self.state == State.CONFIRMATION:
            intent = self.engine.detected_intent(user_input)
            if intent == "YES":
                self.state = State.PAYMENT
                self.step()  # Langsung proses pembayaran
            elif intent == "NO":
                self.state = State.ORDERING
                self.response = "Pembayaran dibatalkan. Mau pesan yang lain?"
            else:
                self.response = "⚠️ Mohon konfirmasi dengan mengetik 'Ya' atau 'Tidak'."

        # STATE LOGIC: PAYMENT
        elif self.state == State.PAYMENT:
            total = self.calculate_total()
            self.response = f"💰 Pembayaran berhasil! Total yang dibayarkan: Rp {total:,}. Terima kasih telah memesan di Warkop! Pesananmu sedang diproses."
            self.state = State.IDLE
            self.cart = []  # Reset keranjang setelah pembayaran