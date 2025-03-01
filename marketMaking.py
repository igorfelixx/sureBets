import spacy
from collections import defaultdict
from Betano.scrapingGame import scrapingLinks
from sportingBet.scrapingGAME import campCarioca
from Betano.campURLS import extract_links
from sportingBet.campURLS import campURLS
from unidecode import unidecode 
from mapp import MARKET_MAPPING, mapSelection_function, crossingSelections
from fuzzywuzzy import fuzz

urls = extract_links()
# Carregar modelo de NLP em português
nlp = spacy.load("pt_core_news_lg")

# Mapeamento de mercados equivalentes
market_mapping = MARKET_MAPPING

class SureBetFinder:
    def __init__(self, similarity_threshold=0.8):
        self.similarity_threshold = similarity_threshold
        self.market_cache = defaultdict(dict)

    def normalize_text(self, text):
        """Normalização robusta com fallback para texto original"""
        doc = nlp(text.lower())
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return " ".join(tokens) if tokens else text.lower().strip()
    
    def normalize_market(self, market):
        market = unidecode(market)
        return market.lower().strip().replace(" ", "").replace("-", "").replace(":", "").replace(",", "").replace(".","")

    def is_similar(self, text1, text2):
        """Similaridade com verificação de vetores vazios"""
        doc1 = nlp(self.normalize_text(text1))
        doc2 = nlp(self.normalize_text(text2))
        return doc1.similarity(doc2) if doc1.has_vector and doc2.has_vector else 0.0

    def find_equivalent_market(self, market_name):
        """Encontra o mercado equivalente no mapeamento"""
        normalized_name = self.normalize_market(market_name)
        for key, aliases in market_mapping.items():

            if normalized_name in aliases :
                return key
        return None

    def find_similar_market(self, target_market, markets):
        """Encontra mercados equivalentes usando o mapeamento"""
        target_key = self.find_equivalent_market(target_market['Mercado'])
        if not target_key:
            return None

        for market in markets:
            market_key = self.find_equivalent_market(market['Mercado'])
            if market_key == target_key:
                return market
        return None

    def match_selections(self, selections_a, selections_b, homeTeam, awayTeam):
        """Encontra correspondências entre seleções usando similaridade"""
        
        selections = []
        selection_mapping = mapSelection_function(homeTeam, awayTeam)  # Mapeamento de seleções
        opposite_mapping = crossingSelections(homeTeam, awayTeam)  # Mapeamento de opostos
        
        for sel_a in selections_a:
            for sel_b in selections_b:
                # Verifica se a seleção de sel_a está no mapeamento
                for key_a, aliases_a in selection_mapping.items():
                    if self.normalize_market(sel_a['Seleção']) in aliases_a:
                        
                        # Verifica se a seleção de sel_b está no mapeamento
                        for key_b, aliases_b in selection_mapping.items():
                            if self.normalize_market(sel_b['Seleção']) in aliases_b:
                                
                                # Verifica se key_b é o oposto de key_a usando o opposite_mapping
                                if key_b == opposite_mapping.get(key_a):
                                    # surebet = (100/sel_a['Preço']) + (100/sel_b['Preço'])
                                    # if surebet < 100:
                                    #     print("########################################")
                                    #     print('Isso é uma sureBet')
                                    #     print("Encontrou oposto!")
                                    #     print("Seleção A: ", self.normalize_market(sel_a['Seleção']))
                                    #     print("Odd: ", sel_a['Preço'])
                                    #     print("Seleção B: ", self.normalize_market(sel_b['Seleção']))
                                    #     print("Odd: ", sel_b['Preço'])
                                    #     print("Key A: ", key_a)
                                    #     print("Key B: ", key_b)
                                    #     print("########################################") 
                                    selections.append((sel_a, sel_b))
                                    return selections  # Retorna as chaves correspondentes
        return None, None  # Retorna None se não encontrar correspondência


    def find_surebets(self, data_platform1, data_platform2):
        """Identifica oportunidades de arbitragem entre duas plataformas"""
        surebets = []
        for game1 in data_platform1:
            for game2 in data_platform2:
                
                ratio = fuzz.token_set_ratio(game1['Jogo'], game2['Jogo'])
                
                if ratio < 80:
                    ### os Jogos estão vindo errado quando estão ao vivo por causa da Betano, que é uma api diferente para jogos ao vivo
                    continue
                
                for market1 in game1['Mercados']:
                    market2 = self.find_similar_market(market1, game2['Mercados'])
                    if not market2:
                        continue
                    
                    matches = self.match_selections(market1['Seleções'], market2['Seleções'], self.normalize_market(game1['HomeTeam']), self.normalize_market(game1['AwayTeam']))
                    if matches == (None, None):
                        continue
                    # else:
                    #     continue
                        
                    for sel1, sel2 in matches:
                        total_prob = (1/sel1['Preço']) + (1/sel2['Preço'])
                        if total_prob < 1:
                            surebet = {
                                'Evento': f"{game1['HomeTeam']} vs {game2['AwayTeam']}",
                                'Mercado': market1['Mercado'] + " - " + market2['Mercado'],
                                'Seleção_Plataforma1': sel1['Seleção'],
                                'Odds1': sel1['Preço'],
                                'Seleção_Plataforma2': sel2['Seleção'],
                                'Odds2': sel2['Preço'],
                                'Lucro_%': round((1/total_prob - 1)*100, 2),
                            }
                            surebets.append(surebet)
        return sorted(surebets, key=lambda x: x['Lucro_%'], reverse=True)

# Exemplo de uso:
if __name__ == "__main__":
    sportingbet_urls = campURLS()
    sportingbet_data = campCarioca(sportingbet_urls)    
    betano_data = scrapingLinks(urls)

    finder = SureBetFinder(similarity_threshold=0.9)
    oportunidades = finder.find_surebets(sportingbet_data, betano_data)
    
    for oportunidade in oportunidades:
        print('====================================================================================')
        print(f"Jogo: ", oportunidade['Evento'])
        print(f"Lucro garantido de {oportunidade['Lucro_%']}% no mercado {oportunidade['Mercado']}")
        print(f"Seleção 1: {oportunidade['Seleção_Plataforma1']}")
        print(f"Odds 1: {oportunidade['Odds1']}")
        print(f"Seleção 2: {oportunidade['Seleção_Plataforma2']}")
        print(f"Odds 2: {oportunidade['Odds2']}")
        print('====================================================================================')