def nettoie_mairies(df):
    df.sort_values("codeInsee", inplace=True)
    return df[
        df["NomOrganisme"].str.contains("Mairie")
        & ~df["NomOrganisme"].str.contains("Mairie déléguée")
        & ~df["NomOrganisme"].str.contains("Mairie  déléguée")
        & ~df.duplicated(subset=["codeInsee"])
    ]
