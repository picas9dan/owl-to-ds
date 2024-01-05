import random
from typing import Iterable

from .base import Paraphraser


class OSParaphraser(Paraphraser):
    ENTITY_PLACEHOLDERS = [
        "methanol",
        "ethanol",
        "propanol",
        "butanol",
        "pentanol",
        "hexanol",
        "heptanol",
        "octanol",
        "nonanol",
    ]

    def _paraphrase(self, text: str, entity_placeholders: Iterable[str]):
        entity_actuals = []

        while True:
            idx_entity_start = text.find("<entity>")
            if idx_entity_start < 0:
                break

            idx_entity_end = text.find("</entity>", idx_entity_start)
            if idx_entity_end < 0:
                raise ValueError("Missing closing entity tag: " + text)
            idx_entity_end += len("</entity>")

            entity = text[idx_entity_start:idx_entity_end]
            text = "{left}[{mid}]{right}".format(
                left=text[:idx_entity_start],
                mid=entity_placeholders[len(entity_actuals)],
                right=text[idx_entity_end:],
            )
            entity_actuals.append(entity)

        paraphrases = super().paraphrase(text)
        if not entity_actuals:
            return paraphrases

        processed_paraphrases = []
        for paraphrase in paraphrases:
            valid = True
            for placeholder, actual in zip(entity_placeholders, entity_actuals):
                processed_paraphrase = paraphrase.replace(placeholder, actual)
                if processed_paraphrase == paraphrase:
                    valid = False
                    break
            if valid:
                processed_paraphrases.append(processed_paraphrase)
        return processed_paraphrases

    def paraphrase(self, text: str):
        _text = text.replace("<entity>", "[")
        _text = _text.replace("</entity>", "]")
        paraphrases = super().paraphrase(_text)

        if len(paraphrases) < 3:
            entity_placeholders = [x for x in self.ENTITY_PLACEHOLDERS if x not in text]

            try_num = 0
            while len(paraphrases) < 3 and try_num < self.TRY_LIMIT:
                random.shuffle(entity_placeholders)
                paraphrases.extend(self._paraphrase(text, entity_placeholders))
                try_num += 1

            if len(paraphrases) < 3:
                print(
                    "Unable to generate 3 faithful paraphrases.\nOriginal text: {og}\nParaphrases: {p}".format(
                        og=text, p=paraphrases
                    )
                )

            return paraphrases
