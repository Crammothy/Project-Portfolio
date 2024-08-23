"""
handles all of the moving of data between game objects, checks
for game over states, opens initial window
"""
import pygame
import gameobject
import csv
import random

class solitaire:
    def __init__(self):
        #initialise game engine and create a window
        pygame.init()
        self.game_window = pygame.display.set_mode((576, 400))
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)

        #generate and collect the game objects
        self.deck = []
        self.values = ["A","02","03","04","05","06","07","08","09","10","J","Q","K"]
        self.discard_pile = []
        self.generate_cards()
        self.shuffle(self.deck)
        self.components = {"board" : gameobject.board(),
                           "draw_zone" : gameobject.draw_zone(self.deck),
                           "extra_cards" : gameobject.extra_cards(),
                           "column_1" : gameobject.column(1, self.deck),
                           "column_2" : gameobject.column(2, self.deck),
                           "column_3" : gameobject.column(3, self.deck),
                           "column_4" : gameobject.column(4, self.deck),
                           "column_5" : gameobject.column(5, self.deck),
                           "column_6" : gameobject.column(6, self.deck),
                           "column_7" : gameobject.column(7, self.deck),
                           "foundation" : gameobject.foundation(),
                           "moving_cards" : gameobject.moving_cards(),
                           "new_game_button" : gameobject.new_game_button(),
                           "score" : gameobject.score(self.font),
                           "game_win" : gameobject.game_win_message(self.font)}

        #stored function calls for game events used in event_handler
        self.events = {"draw_card" : self.draw_card,
                       "move_cards" : self.move_cards,
                       "place_cards" : self.place_cards,
                       "return_cards" : self.return_cards,
                       "reset" : self.reset_game}

        #collection of gameobjects with considering_move attribute
        #used in place_cards
        self.movables = ["extra_cards",
                         "column_1",
                         "column_2",
                         "column_3",
                         "column_4",
                         "column_5",
                         "column_6",
                         "column_7",]


    #functions that handle user interface
    def render(self):
        for component in self.components.values():
            component.render(self.game_window)
        pygame.display.update()

    def update_pos(self):
        for component in self.components.values():
            component.update_pos()

    def event_handler(self, event):
        """
        Calls game object event handle function which returns a list. The
        first element in the list is the method to be called from self.events
        and the remaining elements are the arguments for the function.
        """
        for component in self.components.values():
            event_response = component.event_listener(event)
            if event_response != None:
                action = event_response.pop(0)
                if len(event_response) != 0:
                    action_parameter = event_response.pop(0)
                    self.events[action](action_parameter)
                else:
                    self.events[action]()
                return

    def increment_score(self):
       self.components["score"].value += 1

    #functions that handle deck/discard interaction
    def generate_cards(self):
        with open("_cards.csv", newline='') as csvfile:
            filereader = csv.reader(csvfile)
            for row in filereader:
                self.deck.append(gameobject.card(''.join(row)))

    def shuffle(self, cards: list):
        shuffler = []
        to_shuffle = len(cards)
        while len(shuffler) != to_shuffle:
            shuffler.append(cards.pop(random.randint(0, len(cards) - 1)))
        for card in range(len(shuffler)):
            cards.append(shuffler[card])

    def draw_card(self):
        in_deck = len(self.deck)
        in_discard = len(self.discard_pile)
        in_extra = len(self.components["extra_cards"].cards)

        if in_deck == 0:
            if in_discard == 0:
                if in_extra == 0:
                    return
                else:
                    self.combine_piles(self.components["extra_cards"].cards)
                    self.components["extra_cards"].cards.append(self.deck.pop(-1))
            elif in_extra < 3:
                self.combine_piles(self.discard_pile)
                self.components["extra_cards"].cards.append(self.deck.pop(-1))
            else:
                self.combine_piles(self.discard_pile, self.components["extra_cards"].cards)
                self.components["extra_cards"].cards.append(self.deck.pop(-1))
        elif in_extra < 3:
            self.components["extra_cards"].cards.append(self.deck.pop(-1))
        else:
            self.discard_pile.extend(self.components["extra_cards"].cards)
            self.components["extra_cards"].cards.clear()
            self.components["extra_cards"].cards.append(self.deck.pop(-1))
        self.increment_score()

    def combine_piles(self, *piles):
        for pile in piles:
            self.deck.extend(pile)
            pile.clear()
        self.shuffle(self.deck)
            
        
    #functions that handle moving cards
    def move_cards(self, to_move):
        if type(to_move) == list:
            for card in to_move:
                self.components["moving_cards"].cards.append(card)
        else:
            self.components["moving_cards"].cards.append(to_move)
                
            
    def place_cards(self, destination):
        if len(self.components["moving_cards"].cards) == 0:
            return
        else:
            if "column" in destination:
                if self.check_valid_column_move(destination):
                    if len(self.components[destination].cards) != 0:
                        self.increment_score()
                    self.column_move(destination)
                else:
                    self.return_cards()
            else:
                if self.check_valid_foundation_move(destination):
                    self.foundation_move(destination)
                else:
                    self.return_cards()
                    
    def check_valid_foundation_move(self, destination) -> bool:
        candidates = self.components["moving_cards"].cards
        if candidates[-1].suit == destination:
            if len(self.components["foundation"].cards.get(destination)) == 0:
                if candidates[-1].value == "A":
                    return True
            else:
                candidate_index = self.values.index(candidates[-1].value)
                required_index = self.values.index(
                self.components["foundation"].cards.get(destination)[-1].value) + 1
                if candidate_index == required_index:
                    return True
        return False

    def foundation_move(self, destination):
        card_to_place = self.components["moving_cards"].cards.pop(-1)
        self.components["foundation"].cards.get(destination).append(card_to_place)
        for game_object in self.movables:
            if self.components[game_object].considering_move:
                self.components[game_object].cards.extend(
                    self.components["moving_cards"].cards)
                self.components["moving_cards"].cards.clear()
                self.components[game_object].considering_move = False
                return
    
    def check_valid_column_move(self, destination) -> bool:
        candidates = self.components["moving_cards"].cards
        if len(self.components[destination].cards) == 0:
            return True
        elif candidates[0].colour != self.components[destination].cards[-1].colour:
            candidate_index = self.values.index(candidates[0].value)
            required_index = self.values.index(self.components[destination].cards[-1].value) - 1
            if candidate_index == required_index:
                return True
        return False

    def column_move(self, destination):
        self.components.get(destination).cards.extend\
                                        (self.components["moving_cards"].cards)
        self.components["moving_cards"].cards.clear()
        for game_object in self.movables:
            if self.components[game_object].considering_move:
                self.components[game_object].considering_move = False
                return           

    def return_cards(self):
        for game_object in self.movables:
            if self.components[game_object].considering_move:
                self.components[game_object].cards.extend\
                                            (self.components["moving_cards"].cards)
                self.components["moving_cards"].cards.clear()
                self.components[game_object].considering_move = False
                return

    #functions that handle winning the game
    def check_win(self) -> bool:
        if len(self.deck) == 0 and \
           len(self.discard_pile) == 0 and \
           len(self.components["extra_cards"].cards) == 0:
            for game_object in self.movables:
                if self.components[game_object].considering_move == True:
                    return False
            return True
        return False

    def win(self):
        self.components["game_win"].visibility = True

    #functions that handle resetting the game
    def check_reset(self, event) -> bool:
        response = self.components["new_game_button"].event_listener(event)
        if response != None:
            action = response.pop(0)
            self.events[action]()
            return True
        
    def reset_game(self):
        self.combine_piles(self.discard_pile,
                           self.components["extra_cards"].cards,
                           self.components["column_1"].cards,
                           self.components["column_2"].cards,
                           self.components["column_3"].cards,
                           self.components["column_4"].cards,
                           self.components["column_5"].cards,
                           self.components["column_6"].cards,
                           self.components["column_7"].cards,
                           self.components["foundation"].cards["hearts"],
                           self.components["foundation"].cards["diamonds"],
                           self.components["foundation"].cards["spades"],
                           self.components["foundation"].cards["clubs"])        
        self.shuffle(self.deck)
        for cards in self.deck:
            cards.visibility = False
            cards.position = None
        for game_object in self.components:
            if "column" in game_object:
                self.components[game_object].setup()
        self.components["score"].value = 0
        self.components["game_win"].visibility = False

if __name__ == "__main__":
    running = True
    game_over = False
    game = solitaire()
    while running:
            game.update_pos()
            game.render()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif game.check_win() and game_over == False:
                    game.win()
                    game_over = True
                elif game_over == False:
                    game.event_handler(event)
                else:
                    if game.check_reset(event) and game_over:
                        game_over = False
                    
    pygame.quit()

    
        
        
