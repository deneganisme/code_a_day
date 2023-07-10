import requests


def get_wikidata_entity(wikidata_id: str):
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&format=json"
    req = requests.get(url)
    if not req.ok:
        msg = f"Unable to scrape url={url}. Error={req.text}"
        raise ConnectionError(msg)

    return req


class WikidataEntity:

    def __init__(self,
                 wikidata_id: str,
                 fetch_on_init: bool = False):

        self.__wikidata_id = wikidata_id.upper()
        self.__page = None
        if fetch_on_init:
            # Call page method to fetch data
            self.page

        self.__rels = None

    def __str__(self):
        return self.__wikidata_id

    @property
    def page(self):
        if self.__page is None:
            req = get_wikidata_entity(self.__wikidata_id)
            bod = req.json()
            ents = bod['entities']

            if self.__wikidata_id not in ents:
                raise ValueError(f"Unable to find Wikidata info for {self.__wikidata_id}")

            self.__page = ents[self.__wikidata_id]

        return self.__page

    @property
    def name(self) -> str:
        return self.page["labels"]["en"]["value"]

    @property
    def description(self) -> str:
        return self.page['descriptions']['en']['value']

    @property
    def relationships(self) -> dict:
        if self.__rels is None:
            self.__rels = self.parse_relationships(self.page)

        return self.__rels

    @staticmethod
    def parse_relationships(wikidata_entity: dict) -> list:
        relations = []

        aliases = wikidata_entity['aliases']
        rel = 'alias'
        for alias in aliases.values():
            relations.append((rel, alias))

        rels = wikidata_entity.get('claims')
        if not rels:
            return []

        for rel_wiki_id, values in rels.items():
            rel = WikidataEntity(rel_wiki_id)

            for entry in values:
                val = entry['mainsnak']['datavalue']['value']

                if isinstance(val, dict):
                    wiki_id = val.get('id')
                    if not wiki_id:
                        wiki_id = val.get('text', val.get('time', None))
                        if wiki_id is None:
                            print(f"Unable to find value: {val}")
                else:
                    wiki_id = val

                if wiki_id.startswith('Q'):
                    wiki_obj = WikidataEntity(wiki_id)
                    relations.append((rel, wiki_obj))
                else:
                    relations.append((rel, wiki_id))

        return relations


e = WikidataEntity('Q3111140')
print(e.name, e.description)
for rel, val in e.relationships:
    if not isinstance(rel, str):
        rel = rel.name

    if not isinstance(val, (str, list)):
        val = val.name

    print(rel, val)