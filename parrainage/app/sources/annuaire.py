import pandas as pd


def charge_annuaire_mairies(chemin):
    return (
        nettoie_mairies(pd.read_csv(chemin, sep=",", dtype=str))
        .drop(
            columns=[
                "NomCommune",
                "dateMiseAJour",
            ]
        )
        .fillna("")
    )


def nettoie_mairies(df):
    """
    Élimine les doublons pour une même commune
    """
    df.sort_values("codeInsee", inplace=True)
    return df[
        df["NomOrganisme"].str.contains("Mairie")
        & ~df["NomOrganisme"].str.contains("Mairie déléguée")
        & ~df["NomOrganisme"].str.contains("Mairie  déléguée")
        & ~df.duplicated(subset=["codeInsee"])
    ]
