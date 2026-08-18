from pathlib import Path

RAW_DIR = Path("data/raw")

SAEB = {
    2007: RAW_DIR / "saeb" / "MEDIA_UF_2007.xlsx",
    2009: RAW_DIR / "saeb" / "MEDIA_UF_2009.xlsx",
    2011: RAW_DIR / "saeb" / "TS_RESULTADO_UF_2011.csv",
    2013: RAW_DIR / "saeb" / "TS_UF_2013.xlsx",
    2015: RAW_DIR / "saeb" / "TS_UF_2015.xlsx",
    2017: RAW_DIR / "saeb" / "TS_UF_2017.xlsx",
    2019: RAW_DIR / "saeb" / "TS_UF_2019.xlsx",
    2021: RAW_DIR / "saeb" / "TS_UF_2021.xlsx",
}