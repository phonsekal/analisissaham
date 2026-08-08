# app/routers.py - Versi AMAN 500 Error
from fastapi import APIRouter, HTTPException
from app.services import hitung_analisis_saham, hitung_momentum_gorengan
from app.config import INDEX_BLUECHIP_UTAMA, WATCHLIST_GORENGAN

router = APIRouter(prefix="/v1")

@router.get("/analisis/swing/{ticker}")
async def analisis_swing_saham(ticker: str):
    """Analisis lengkap satu saham (fundamental + teknikal) untuk strategi swing-dividen."""
    data = hitung_analisis_saham(ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"Data untuk {ticker.upper()} tidak ditemukan atau tidak lengkap.")
    return {"status": "success", "data": data}

@router.get("/analisis/gorengan/{ticker}")
async def analisis_gorengan_saham(ticker: str):
    """Analisis momentum satu saham untuk strategi day-trading ADX."""
    data = hitung_momentum_gorengan(ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"Data untuk {ticker.upper()} tidak ditemukan atau tidak lengkap.")
    return {"status": "success", "data": data}

@router.get("/screener/swing-dividen")
async def run_screener_swing_dividen():
    saham_lolos = []
    for ticker in INDEX_BLUECHIP_UTAMA:
        try:
            symbol = ticker.replace(".JK", "")
            data = hitung_analisis_saham(symbol)
            if not data:
                continue
            # Gunakan data.get() agar aman dari KeyError
            teknikal = data.get("teknikal", {})
            if "AKTIF" in teknikal.get("konfirmasi_oversold_swing", ""):
                saham_lolos.append({
                    "saham": data.get("saham"),
                    "harga_saat_ini": data.get("harga_saat_ini"),
                    "status_tren": teknikal.get("status_tren"),
                    "konfirmasi_oversold_swing": teknikal.get("konfirmasi_oversold_swing"),
                    "status_dividen": data.get("fundamental", {}).get("status_dividen"),
                    "rekomendasi": data.get("rekomendasi_akhir")
                })
        except Exception:
            continue
    return {"status": "success", "data": saham_lolos}

@router.get("/screener/gorengan-momentum")
async def run_screener_gorengan_momentum():
    saham_lolos = []
    for ticker in WATCHLIST_GORENGAN:
        try:
            symbol = ticker.replace(".JK", "")
            data = hitung_momentum_gorengan(symbol)
            # PENTING: Gunakan data.get() untuk menghindari KeyError
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
            
    return {"status": "success", "radar_saham_gorengan_aktif": saham_lolos}
