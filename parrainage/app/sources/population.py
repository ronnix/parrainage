import pandas as pd


def charge_population_communes(chemin):
    df = pd.read_csv(chemin, sep=";", dtype=str).fillna("")
    df["CODE"] = df["CODDEP"] + df["CODCOM"]
    return df[["CODE", "PMUN"]]
