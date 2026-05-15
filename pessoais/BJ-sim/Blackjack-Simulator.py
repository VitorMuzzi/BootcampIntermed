import random
import statistics


# 1. baralho e regras funcionando

class Shoe:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.running_count = 0
        self.shuffle()

    def shuffle(self):
        single_deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4   # 2 a 10 valem eles mesmos. J,Q,K = 10. A = 11.
        self.cards = single_deck * self.num_decks                         
        random.shuffle(self.cards)
        self.running_count = 0

    def draw_card(self):
        if len(self.cards) < 30: 
            self.shuffle()
        card = self.cards.pop()
        
        if card <= 6: self.running_count += 1
        elif card >= 10: self.running_count -= 1
        return card

def calculate_hand(hand):
    total = sum(hand)
    aces = hand.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def play_random(hand, shoe, current_money, current_bet):
    # grupo 1 não sabe fazer Double, Split ou Surrender. (bestas)
    while calculate_hand(hand) < 21:
        if random.choice([True, False]) or calculate_hand(hand) < 14:
            hand.append(shoe.draw_card())
        else:
            break
    return [(hand, current_bet)]

def play_basic_strategy(hand, dealer_upcard, shoe, current_money, current_bet, is_split=False):
    # surrender - Apenas na primeira mão (2 cartas)
    if not is_split and len(hand) == 2:
        total = calculate_hand(hand)
        # Rende-se com 16 contra 9, 10 ou Ás, e com 15 contra 10
        if (total == 16 and dealer_upcard >= 9) or (total == 15 and dealer_upcard == 10):
            return [("SURRENDER", current_bet)]

    # split
    can_split = len(hand) == 2 and hand[0] == hand[1] and current_money >= (current_bet * 2)
    if can_split and (hand[0] in [8, 11] or (hand[0] in [2, 3, 7, 9] and dealer_upcard <= 7)):
        hand1 = [hand[0], shoe.draw_card()]
        hand2 = [hand[1], shoe.draw_card()]
        hands_to_play = []
        hands_to_play.extend(process_single_hand(hand1, dealer_upcard, shoe, current_money, current_bet, is_split=True))
        hands_to_play.extend(process_single_hand(hand2, dealer_upcard, shoe, current_money, current_bet, is_split=True))
        return hands_to_play

    return process_single_hand(hand, dealer_upcard, shoe, current_money, current_bet)


def process_single_hand(hand, dealer_upcard, shoe, current_money, current_bet, is_split=False):
    total = calculate_hand(hand)
    
    # dobrar
    can_double = len(hand) == 2 and current_money >= (current_bet * 2)
    if can_double and (total == 11 or (total == 10 and dealer_upcard <= 9)):
        hand.append(shoe.draw_card())
        return [(hand, current_bet * 2)]

    # pedir ou parar
    while calculate_hand(hand) < 21:
        total = calculate_hand(hand)
        if total <= 11:
            hand.append(shoe.draw_card())
        elif total >= 17:
            break
        elif dealer_upcard >= 7:
            hand.append(shoe.draw_card())
        else:
            break 
            
    return [(hand, current_bet)]


# 3. funcionamento do jogo

def play_blackjack_round(player_type, current_money, base_bet, shoe):
    bet = base_bet
    true_count = shoe.running_count / max(1, len(shoe.cards) / 52)
    
    # Robô dimensiona a aposta inicial baseado no Hi-Lo
    if player_type == "Robo":
        if true_count >= 2: bet = base_bet * 3
        elif true_count <= -1: bet = base_bet * 0.5
            
    if bet > current_money: bet = current_money

    # Distribuição
    player_hand = [shoe.draw_card(), shoe.draw_card()]
    dealer_hand = [shoe.draw_card(), shoe.draw_card()]
    dealer_upcard = dealer_hand[0]

    new_money = current_money

    # insurance (qm usa isso)
    if dealer_upcard == 11: # Dealer tem um Ás visível
        takes_insurance = False
        if player_type == "Aleatorio": 
            takes_insurance = random.choice([True, False])
        elif player_type == "Matematico": 
            takes_insurance = False # A matemática pura recusa sempre o seguro (sabidos)
        elif player_type == "Robo": 
            if true_count >= 3: 
                takes_insurance = True # O robo sabe que o baralho tem muitas face cards (J,Q,K,A)

        if takes_insurance and new_money >= (bet * 1.5):
            insurance_bet = bet * 0.5
            new_money -= insurance_bet # Tira o dinheiro do seguro
            if calculate_hand(dealer_hand) == 21:
                new_money += insurance_bet * 3 # Seguro pago a 2:1

    # Verificação do Blackjack Natural (3:2)
    p_bj = calculate_hand(player_hand) == 21
    d_bj = calculate_hand(dealer_hand) == 21
    
    if p_bj and not d_bj: return new_money + (bet * 1.5)
    if p_bj and d_bj: return new_money
    if d_bj: return new_money - bet # acaba aqui se o dealer tem BJ

    # player joga
    if player_type == "Aleatorio":
        final_hands = play_random(player_hand, shoe, new_money, bet)
    else:
        final_hands = play_basic_strategy(player_hand, dealer_upcard, shoe, new_money, bet)

    # dealer joga
    dealer_plays = False
    for hand_data in final_hands:
        if hand_data[0] != "SURRENDER" and calculate_hand(hand_data[0]) <= 21: 
            dealer_plays = True
            
    if dealer_plays:
        while calculate_hand(dealer_hand) < 17:
            dealer_hand.append(shoe.draw_card())
            
    dealer_total = calculate_hand(dealer_hand)

    for hand, hand_bet in final_hands:
        if hand == "SURRENDER":
            new_money -= (hand_bet * 0.5) # Perde só metade da aposta
        else:
            p_total = calculate_hand(hand)
            if p_total > 21:
                new_money -= hand_bet
            elif dealer_total > 21 or p_total > dealer_total:
                new_money += hand_bet
            elif dealer_total > p_total:
                new_money -= hand_bet

    return new_money

#simulação dos gps

def simulate_group(group_name, player_type, num_players=1000, rounds=100, starting_money=1000):
    balances = []
    shoe = Shoe(num_decks=6)

    for _ in range(num_players):
        money = starting_money
        for _ in range(rounds):
            if money <= 0: break
            money = play_blackjack_round(player_type, money, base_bet=20, shoe=shoe)
        balances.append(money)

    avg = sum(balances) / len(balances)
    med = statistics.median(balances)
    ratio_zeros = (balances.count(0) / num_players) * 100
    
    print(f"\n--- GRUPO: {group_name} ---")
    print(f"Média Final: {avg:.2f}")
    print(f"Mediana: {med:.2f}")
    print(f"Taxa de Quebra: {ratio_zeros:.2f}%")
    print(f"Maior Fortuna: {max(balances):.2f}")

def main():
    print("Iniciando Simulação de Blackjack (REGRAS COMPLETAS: Double, Split, Rendição e Seguro)...")
    simulate_group("Os Turistas (Aleatório)", "Aleatorio")
    simulate_group("Os Matemáticos (Estratégia Básica)", "Matematico")
    simulate_group("Os Profissionais (Básica + Robô Contador)", "Robo")

if __name__ == "__main__":
    main()