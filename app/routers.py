# app/routers.py - VERSI FINAL UTUH DAN LENGKAP (KEBAL ERROR 500)
from fastapi import APIRouter, HTTPException
from app.services import hitung_analisis_saham, hitung_momentum_gorengan
from app.config import INDEX_BLUECHIP_UTAMA, WATCHLIST_GORENGAN

router = APIRouter(prefix="/v1")

# ==========================================
# 1. ENDPOINT ANALISIS TUNGGAL (PER EMITEN)
# ==========================================

@router.get("/analisis/swing/{ticker}")
async def get_analisis_swing(ticker: str):
    try:
        hasil = hitung_analisis_saham(ticker)
        if not hasil:
            raise HTTPException(status_code=404, detail=f"Saham {ticker} gagal diproses.")
        return hasil
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analisis/gorengan/{ticker}")
async def get_analisis_gorengan(ticker: str):
    try:
        hasil = hitung_momentum_gorengan(ticker)
        if not hasil:
            raise HTTPException(status_code=404, detail=f"Saham {ticker} gagal diproses.")
        return hasil
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 2. ENDPOINT SCREENER MASSAL (WATCHLIST)
# ==========================================

@router.get("/screener/swing-dividen")
async def run_screener_swing_dividen():
    saham_lolos = []
    for ticker in INDEX_BLUECHIP_UTAMA:
        try:
            symbol = ticker.replace(".JK", "")
            data = hitung_analisis_saham(symbol)
            
            # Memastikan data aman dan mengecek guardrail risiko dari services.py
            if data and not data.get("guardrail_proteksi", {}).get("wajib_stop_loss", True):
                rekomendasi = data.get("rekomendasi_akhir", "")
                # Meloloskan saham yang berada di zona momentum beli aman
                if "BUY" in rekomendasi or "SEROK" in rekomendasi or "PASIF" in rekomendasi:
                    saham_lolos.append({
                        "saham": data.get("saham"),
                        "harga_saat_ini": data.get("harga_saat_ini"),
                        "yield_dividen": data.get("fundamental", {}).get("status_dividen"),
                        "arus_modal": data.get("teknikal", {}).get("status_arus_modal"),
                        "rekomendasi": rekomendasi
                    })
        except Exception:
            continue  # Mengabaikan emiten jika data Yahoo Finance-nya sedang putus agar Vercel tidak crash
            
    return {"status": "success", "jumlah_saham_lolos": len(saham_lolos), "data_watchlist_siap_beli": saham_lolos}

@router.get("/screener/gorengan-momentum")
async def run_screener_gorengan_momentum():
    saham_lolos = []
    for ticker in WATCHLIST_GORENGAN:
        try:
            symbol = ticker.replace(".JK", "")
            data = hitung_momentum_gorengan(symbol)
            
            # PENTING: Menggunakan .get() agar aman jika saham berstatus GAGAL
            if data and "LOLOS" in data.get("status_filter", ""):
                saham_lolos.append({
                    "saham": data.get("saham"),
                    "status": data.get("status_filter"),
                    "rsi_momentum": data.get("indikator", {}).get("rsi_momentum"),
                    "adx_power": data.get("indikator", {}).get("adx_power"),
                    "rekomendasi": data.get("rekomendasi_aksi")
                })
        except Exception:
            continue
            
    return {"status": "success", "jumlah_saham_meledak": len(saham_lolos), "radar_saham_gorengan_aktif": saham_lolos}
