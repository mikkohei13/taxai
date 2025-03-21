import requests
import json
import re

import token

def main(taxon_name_untrusted):
    # Validate that taxon name contains only letters, dashes and spaces
    if not re.match(r'^[a-zA-Z0-9\- ]+$', taxon_name_untrusted):
        return {
            "error": "Taxon name contains invalid characters"
        }
    taxon_name = taxon_name_untrusted.strip()

    return {
        "taxon": taxon_name
    }