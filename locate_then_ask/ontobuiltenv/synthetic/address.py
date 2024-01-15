import os

import pandas as pd
from constants.fs import ROOTDIR
from locate_then_ask.ontobuiltenv.model import IctAddress


class IctAddressSynthesizer:
    def __init__(self) -> None:
        self.df = pd.read_csv(os.path.join(ROOTDIR, "data/ontobuiltenv/Addresses.csv"))
        self.df = self.df[self.df["Address"].apply(lambda addr: addr[0].isnumeric())]

    def make(self) -> IctAddress:
        row = self.df.sample(n=1).iloc[0]
        address = row["Address"].split(",", maxsplit=1)[0]
        street_number, street = address.split(maxsplit=1)
        postal_code = row["Postcode"]

        return IctAddress(
            street=street.upper(), street_number=street_number, postal_code=postal_code
        )
