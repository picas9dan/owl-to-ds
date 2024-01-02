import argparse
from typing import Optional

from .base import Paraphraser
from .ontospecies import OSParaphraser


def get_paraphraser(domain: Optional[str], endpoint, api_key, model):
    if domain == "ontospecies":
        return OSParaphraser(endpoint, api_key, model)
    else:
        return Paraphraser(endpoint, api_key, model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    parser.add_argument("--domain", type=str, required=False)
    parser.add_argument("--endpoint", type=str, required=False)
    parser.add_argument("--api_key", type=str, requried=False)
    parser.add_argument("--model", type=str, required=False)
    args = parser.parse_args()

    paraphraser = get_paraphraser(args.domain, args.endpoint, args.api_key, args.model)
    paraphraser.paraphrase_from_file(args.filepath)
