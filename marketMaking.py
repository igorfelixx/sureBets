import spacy
from collections import defaultdict
from Betano.scrapingGame import scrapingLinks
from sportingBet.scrapingGAME import campCarioca
from Betano.campURLS import extract_links
from sportingBet.campURLS import campURLS
from unidecode import unidecode 
from mapp import MARKET_MAPPING

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

    def match_selections(self, selections_a, selections_b):
        """Encontra correspondências entre seleções usando similaridade"""
        matches = []
        for sel_a in selections_a:
            for sel_b in selections_b:
                similarity = self.is_similar(sel_a['Seleção'], sel_b['Seleção'])
                if similarity > self.similarity_threshold:
                    matches.append((sel_a, sel_b, similarity))
        return sorted(matches, key=lambda x: x[2], reverse=True)

    def find_surebets(self, data_platform1, data_platform2):
        """Identifica oportunidades de arbitragem entre duas plataformas"""
        surebets = []
        for game1 in data_platform1:
            for game2 in data_platform2:
                # if self.is_similar(self.normalize_text(game1['Jogo']), self.normalize_text(game2['Jogo'])) < 0.5:
                #     print("game11: ", self.normalize_market(game1['Jogo']))
                #     print('game2: ', self.normalize_market(game2['Jogo'])) ### os Jogos estão vindo errado quando estão ao vivo por causa da Betano, que é uma api diferente para jogos ao vivo
                #     continue
                
                for market1 in game1['Mercados']:
                    market2 = self.find_similar_market(market1, game2['Mercados'])
                    if not market2:
                        continue
                    
                    print('---------------------------------------')
                    print('Jogo SportingBet:', game1['Jogo'], ' ', 'Jogo Betano: ', game2['Jogo'])
                    print('SportingBet:', market1['Mercado'], ' ',)
                    print('Betano:', market2['Mercado'], ' ',)
                    print('---------------------------------------')
                    matches = self.match_selections(market1['Seleções'], market2['Seleções'])
                    for sel1, sel2, similarity in matches:
                        total_prob = (1/sel1['Preço']) + (1/sel2['Preço'])
                        if total_prob < 1:
                            surebet = {
                                'Evento': f"{game1['HomeTeam']} vs {game1['AwayTeam']}",
                                'Mercado': market1['Mercado'] + " - " + market2['Mercado'],
                                'Seleção_Plataforma1': sel1['Seleção'],
                                'Odds1': sel1['Preço'],
                                'Seleção_Plataforma2': sel2['Seleção'],
                                'Odds2': sel2['Preço'],
                                'Lucro_%': round((1/total_prob - 1)*100, 2),
                                'Similaridade': round(similarity, 2)
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
        print(f"Lucro garantido de {oportunidade['Lucro_%']}% no mercado {oportunidade['Mercado']}")