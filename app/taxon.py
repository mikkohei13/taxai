import requests
import json
import re
import time
import helpers


def get_description(taxon_data_advanced):
    # Get descriptions if they exist
    descriptions = taxon_data_advanced.get('descriptions', [])
    result = {
        "text": "",
        "authors": ""
    }
    
    # Go through all description groups
    for description in descriptions:
        for group in description.get('groups', []):
            # Look for the general description group
            if group.get('group') == 'MX.SDVG1':
                # Go through variables to find the description text and authors
                for variable in group.get('variables', []):
                    if variable.get('variable') == 'MX.descriptionText':
                        content = variable.get('content', {})
                        # Handle both string and dictionary content
                        if isinstance(content, str):
                            result["text"] = content
                        else:
                            result["text"] = content.get('fi', '')
                    elif variable.get('variable') == 'MX.descriptionAuthors':
                        content = variable.get('content', {})
                        if isinstance(content, str):
                            result["authors"] = content
                        else:
                            result["authors"] = content.get('fi', '')
    
    return result

def get_html_description(taxon_data_advanced):
    html = ""
    description = taxon_data_advanced['descriptions'][0]

    for group in description['groups']:
        for variable in group['variables']:
            if variable['title'] == 'Ingressi':
                pass
            else:
                html += f"<h4>{variable['title']}</h4>\n"
                html += f"{variable['content']}\n"

    html += f"<h4>{description['speciesCardAuthors']['title']}</h4>\n"
    html += f"{description['speciesCardAuthors']['content']}\n"

    return html


def main(taxon_name_untrusted):
    start_time = time.time()

    # Validate that taxon name contains only letters, dashes and spaces
    if not re.match(r'^[a-zA-Z0-9\- ]+$', taxon_name_untrusted):
        return {
            "error": "Taxon name contains invalid characters"
        }
    taxon_name = taxon_name_untrusted.strip()

    # Fetch taxon data from FinBIF
    taxon_data = helpers.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/search?query={taxon_name}&limit=10&matchType=exact&onlySpecies=false&onlyFinnish=false&onlyInvasive=false&observationMode=false&access_token=")

    if not taxon_data or len(taxon_data) == 0:
        return {
            "error": "Taxon not found"
        }

    taxon_id = taxon_data[0]['id']

    # Get more data
    taxon_data_advanced = helpers.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{taxon_id}?langFallback=true&maxLevel=0&includeHidden=false&includeMedia=true&includeDescriptions=true&includeRedListEvaluations=true&sortOrder=taxonomic&lang=fi&access_token=")

    # Get the data we need
    fi_name = taxon_data[0].get('vernacularName', {}).get('fi', '')
    scientific_name = taxon_data[0].get('scientificName', '')
    author = taxon_data[0].get('scientificNameAuthorship', '')
    rank = taxon_data[0].get('taxonRank', '')
    name_type = taxon_data[0].get('nameType', '')


    # typeOfOccurrenceInFinland LIST
    # habitatOccurrenceCounts

    is_invasive = taxon_data_advanced.get('invasiveSpecies', False)
    occurrence_count = taxon_data_advanced.get('observationCountFinland', 0)
    has_descriptions = taxon_data_advanced.get('hasDescriptions', False)
    primary_habitat = taxon_data_advanced.get('primaryHabitat', {}).get('habitat', '')

    html_description = get_html_description(taxon_data_advanced)

    # Translations
    if rank == 'MX.species':
        rank = "laji"
    elif rank == 'MX.genus':
        rank = "suku"
    else:
        rank = rank.replace('MX.', '')

    end_time = time.time()
    response_time = round(end_time - start_time, 3)

    return {
        "taxon": taxon_name,
        "taxon_id": taxon_id,
        "fi_name": fi_name,
        "scientific_name": scientific_name,
        "author": author,
        "rank": rank,
        "name_type": name_type,
        "is_invasive": is_invasive,
        "occurrence_count": occurrence_count,
        "has_descriptions": has_descriptions,
        "primary_habitat": primary_habitat,
        "description": html_description,
        "response_time": response_time
    }