import re

class Engine:
    def __init__(self):
        # Database Menu dengan Info Tambahan untuk UI
        self.menu_data = {
            "kopi": {"price": 15000, "emoji": "☕", "desc": "Kopi hitam tanpa gula"},
            "teh": {"price": 10000, "emoji": "🍵", "desc": "Teh manis dengan gula"},
            "jus": {"price": 20000, "emoji": "🥤", "desc": "Jus buah segar"},
            "susu": {"price": 12000, "emoji": "🥛", "desc": "Susu segar tanpa gula"},
        }

        # Regex Pattern
        self.re_number = r"\b(\d+)\b"
        # Membuat pola regex dinamis dari keys menu
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"
        self.re_split = r"[,.]|\bdan\b|\b&\b"

        # Regex untuk pembatalan/pengurangan
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|hapus|kurangi|minus|tolak|cancel)\b"

    def _parse_single_segment(self, text):
        """Helper untuk memproses satu potongan kalimat (misal: '2 kopi')"""
        # 1. Cari Item
        item_match = re.search(self.re_menu, text)
        if not item_match:
            return None  # Tidak ada item yang ditemukan
        
        item_key = item_match.group(1)

        # 2. Cari Jumlah (Default 1)
        qty_match = re.search(self.re_number, text)
        qty = int(qty_match.group(1)) if qty_match else 1

        return {"item": item_key, "qty": qty, "price": self.menu_data[item_key]["price"], "emoji": self.menu_data[item_key]["emoji"], "desc": self.menu_data[item_key]["desc"]}
        
    def parse_order(self, full_text):
        """
        Memecah kalimat majemuk: 'pesan teh 2, kopi 1' Menjadi list order.
        """
        segments = re.split(self.re_split, full_text)

        found_orders = []
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            order = self._parse_single_segment(segment)
            if order:
                found_orders.append(order)
        return found_orders
    
    def detected_intent(self, text):
        """
        Deteksi Intent Pembatalan/Pengurangan
        """
        text = text.lower()
        if re.search(r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan|batal semua|ulangi)\b", text):
            return "RESET"
        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"
        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"
        if re.search(r"menu|daftar menu|lihat menu|tampilkan menu|apa saja|jual apa|list", text):
            return "ASK_MENU"
        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"
        if re.search(r"\b(ya|oke|betul|siap|baik)\b", text):
            return "YES"
        if re.search(r"\b(tidak|gak|nggak|no|bukan|enggak|batal|salah)\b", text):
            return "NO"
        return "UNKNOWN"
    
    def print_menu(self):
        print(self.menu_data)
        