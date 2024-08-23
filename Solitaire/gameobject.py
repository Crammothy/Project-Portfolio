"""
every object needs to be able to:
- handle events. events return list containing action plus arguments for reaction
- update the status of it's attributes
- render attributes


"""
import pygame

class game_object:
    def __init__():
        pass
    
    def event_listener(self, event) -> list:
        pass

    def update_pos(self):
        pass

    def render(self, draw_surface):
        pass


class board(game_object):
    def __init__(self):
        self.colour = (59, 108, 59)

    def render(self, draw_surface):
        draw_surface.fill(self.colour)


class draw_zone(game_object):
    def __init__(self, deck):
        self.deck = deck
        self.empty_deck = False
        self.position = pygame.Rect(0,0,64,64)
        self.assets = ["assets\\card_back.png", "assets\\deck_empty.png"]

    def event_listener(self, event) -> list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.position.collidepoint(event.pos):
                return ["draw_card"]

    def render(self, draw_surface):
        if len(self.deck) != 0:
            draw_surface.blit(pygame.image.load(self.assets[0]), self.position)
        else:
            draw_surface.blit(pygame.image.load(self.assets[1]), self.position)


class extra_cards(game_object):
    def __init__(self):
        self.cards = []
        self.considering_move = False

    def event_listener(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(self.cards) != 0 and self.cards[-1].position.collidepoint(event.pos):
                self.considering_move = True
                return["move_cards", self.cards.pop(-1)]

    def update_pos(self):
        for card_index in range(len(self.cards)):
            self.cards[card_index].position = pygame.Rect(0, 74 + card_index * 20, 64, 64 )
            self.cards[card_index].visibility = True

    def render(self, draw_surface):
        for card in self.cards:
            draw_surface.blit(pygame.image.load(card.get_asset()), card.position)


class column(game_object):
    def __init__(self, setup_value, deck):
        self.deck = deck
        self.column_ID = str("column_" + str(setup_value))
        self.left = 64 * setup_value
        self.position = pygame.Rect(self.left, 64, 64, 400)
        self.initial_cards = setup_value
        self.cards = []
        self.considering_move = False
        self.setup()
        
    def event_listener(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if self.position.collidepoint(event.pos):
                return ["place_cards", self.column_ID]
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if len(self.cards) == 0:
                return
            else:
                for card in self.cards:
                    if card.position.collidepoint(event.pos) and \
                       card.visibility == True:
                        index = self.cards.index(card)
                        to_move = []
                        while len(self.cards) != index:
                            to_move.insert(0, self.cards.pop(-1))
                        self.considering_move = True
                        return["move_cards", to_move]

    def update_pos(self):
        if len(self.cards) == 0:
            return
        for x in range(len(self.cards)):
            if x == len(self.cards) - 1:
                self.cards[x].position = pygame.Rect(self.left, 64 + x * 20, 64, 64)
            else:
                self.cards[x].position = pygame.Rect(self.left, 64 + x * 20, 64, 20)
        if not self.considering_move:
            self.cards[-1].visibility = True
                       
    def render(self, draw_surface):
        for card in self.cards:
            draw_surface.blit(pygame.image.load(card.get_asset()), card.position)
            

    def setup(self):
        for x in range(self.initial_cards):
            self.cards.append(self.deck.pop(0))
            if x == self.initial_cards - 1:
                self.cards[-1].visibility = True
            

class foundation(game_object):
    def __init__(self):
        self.cards = {"hearts" : [],
                      "diamonds" : [],
                      "spades" : [],
                      "clubs" : [] }
        self.positions = {"hearts" : pygame.Rect(512, 16, 64, 64),
                          "diamonds" : pygame.Rect(512, 112, 64, 64),
                          "spades" : pygame.Rect(512, 208, 64, 64),
                          "clubs" : pygame.Rect(512, 304, 64, 64)}

    def event_listener(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            for position in self.positions:
                if self.positions.get(position).collidepoint(event.pos):
                    return ["place_cards", position]

    def render(self, draw_surface):
        for suit in self.cards:
            if len(self.cards.get(suit)) == 0:
                asset = "assets\\foundation_" + suit + ".png"
                draw_surface.blit(pygame.image.load(asset), self.positions[suit])
            else:
                asset = self.cards[suit][-1].get_asset()
                draw_surface.blit(pygame.image.load(asset), self.positions[suit])


class card(game_object):
    def __init__(self, name):
        self.name = name
        self.card_front = "assets\\" + name + ".png"
        self.card_back = "assets\\card_back.png"
        self.visibility = False
        self.position = None
        self.set_properties(name)


    def set_properties(self, name):
        if "hearts" in name:
            self.suit = "hearts"
            self.colour = "red"
        elif "diamonds" in name:
            self.suit = "diamonds"
            self.colour = "red"
        elif "spades" in name:
            self.suit = "spades"
            self.colour = "black"
        elif "clubs" in name:
            self.suit = "clubs"
            self.colour = "black"
        self.value = name.split("_")[-1]
        
    def get_asset(self):
        if self.visibility:
            return self.card_front
        else:
            return self.card_back


class moving_cards(game_object):
    def __init__(self):
        self.cards = []
      
    def event_listener(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            if len(self.cards) != 0:
                return ["return_cards"]
        elif event.type == pygame.MOUSEMOTION:
            for card in self.cards:
                card.position.move_ip(event.rel)

    def render(self, draw_surface):
        for card in self.cards:
            draw_surface.blit(pygame.image.load(card.get_asset()), card.position)


class new_game_button(game_object):
    def __init__(self):
        self.asset = "assets\\new_game.png"
        self.position = pygame.Rect(100, 20, 91, 30)

    def event_listener(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.position.collidepoint(event.pos):
                return ["reset"]

    def render(self, draw_surface):
        draw_surface.blit(pygame.image.load(self.asset), self.position)


class score(game_object):
    def __init__(self, font):
        self.value = 0
        self.font = font

    def render(self, draw_surface):
        draw_surface.blit(self.font.render(f"Score: {self.value}", True,
                                           (255, 255, 255)), (200, 20))


class game_win_message(game_object):
    def __init__(self, font):
        self.visibility = False
        self.font = font
        
    def render(self, draw_surface):
        if self.visibility:
            draw_surface.blit(self.font.render(self.message, True,
                                           (255, 255, 255)), (300, 20))
