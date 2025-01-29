import random
import pygame
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UNO with Hatsune Miku")

# Fonts
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)

# Load Hatsune Miku image
miku_image = pygame.image.load(os.path.join("assets", "miku.jpeg"))  # Add a Hatsune Miku image in the assets folder
miku_image = pygame.transform.scale(miku_image, (200, 300))

# Load card back image
card_back = pygame.image.load(os.path.join("assets", "card_back.png"))  # Add a card back image in the assets folder
card_back = pygame.transform.scale(card_back, (CARD_WIDTH, CARD_HEIGHT))

# Load sound effects
pygame.mixer.init()
card_play_sound = pygame.mixer.Sound(os.path.join("assets", "card.mp3"))  # Add a sound effect for card play
card_draw_sound = pygame.mixer.Sound(os.path.join("assets", "card.mp3"))  # Add a sound effect for card draw
win_sound = pygame.mixer.Sound(os.path.join("assets", "win.mp3"))  # Add a sound effect for winning

class Card:
    opposite_colors = {'red': 'blue', 'blue': 'red', 'green': 'yellow', 'yellow': 'green'}
    
    def __init__(self, color, value):
        self.color = color
        self.value = value
        
    def __repr__(self):
        if self.color == 'wild':
            return f"{self.value}"
        return f"{self.color} {self.value}"
    
    def draw(self, x, y, selected=False):
        # Draw card background with rounded corners
        if self.color == 'wild':
            pygame.draw.rect(screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        else:
            pygame.draw.rect(screen, WHITE, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=10)
        
        # Draw card border if selected
        if selected:
            pygame.draw.rect(screen, YELLOW, (x, y, CARD_WIDTH, CARD_HEIGHT), 3, border_radius=10)
        
        # Draw card value
        if self.color == 'wild':
            color_text = small_font.render(self.value, True, WHITE)
        else:
            color_text = small_font.render(self.color, True, BLACK)
            value_text = small_font.render(str(self.value), True, BLACK)
            screen.blit(value_text, (x + 10, y + 10))
        screen.blit(color_text, (x + 10, y + 50))

class Deck:
    def __init__(self):
        self.cards = []
        self.build()
        self.shuffle()
        
    def build(self):
        colors = ['red', 'blue', 'green', 'yellow']
        values = [str(i) for i in range(10)] + ['skip', 'reverse', 'draw_two']
        
        # Add colored cards
        for color in colors:
            for value in values:
                self.cards.append(Card(color, value))
                if value != '0':
                    self.cards.append(Card(color, value))
                    
        # Add wild cards
        for _ in range(4):
            self.cards.append(Card('wild', 'wild'))
            self.cards.append(Card('wild', 'wild_draw_four'))
            
    def shuffle(self):
        random.shuffle(self.cards)
        
    def draw(self, num=1):
        return [self.cards.pop() for _ in range(num)]

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        
    def draw(self, deck, num=1):
        self.hand.extend(deck.draw(num))
        
    def play(self, index):
        return self.hand.pop(index)

class UNOGame:
    def __init__(self):
        self.deck = Deck()
        self.discard = []
        self.players = [Player("You"), Player("Hatsune Miku")]
        self.current_player = 0
        self.direction = 1
        self.current_color = None
        self.selected_card_index = None
        
        # Deal initial cards
        for player in self.players:
            player.draw(self.deck, 7)
            
        # Start with initial card
        while True:
            card = self.deck.draw()[0]
            if card.color != 'wild':
                self.discard.append(card)
                self.current_color = card.color
                break
    
    def get_opposite_color(self, player):
        colors = [c.color for c in player.hand if c.color in Card.opposite_colors]
        if colors:
            return Card.opposite_colors[random.choice(colors)]
        return random.choice(['red', 'blue', 'green', 'yellow'])
    
    def next_turn(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)
        
    def handle_special(self, card):
        if card.value == 'skip':
            self.next_turn()
        elif card.value == 'reverse':
            self.direction *= -1
        elif card.value == 'draw_two':
            next_player = (self.current_player + self.direction) % len(self.players)
            self.players[next_player].draw(self.deck, 2)
        elif card.value == 'wild_draw_four':
            next_player = (self.current_player + self.direction) % len(self.players)
            self.players[next_player].draw(self.deck, 4)
    
    def ai_turn(self):
        player = self.players[1]
        target = self.players[0]
        
        # Check for forced loop condition
        if len(target.hand) == 2:
            # Look for any wild card to force color change
            wilds = [i for i, c in enumerate(player.hand) if c.color == 'wild']
            if wilds:
                chosen = random.choice(wilds)
                card = player.play(chosen)
                self.discard.append(card)
                self.current_color = self.get_opposite_color(target)
                self.handle_special(card)
                return True
                
        # Normal AI play
        playable = []
        for i, c in enumerate(player.hand):
            if c.color == self.current_color or c.color == 'wild' or c.value == self.discard[-1].value:
                playable.append(i)
        
        if playable:
            chosen = random.choice(playable)
            card = player.play(chosen)
            self.discard.append(card)
            
            if card.color == 'wild':
                self.current_color = self.get_opposite_color(target) if len(target.hand) == 2 else random.choice(['red', 'blue', 'green', 'yellow'])
            else:
                self.current_color = card.color
                
            self.handle_special(card)
            return True
        else:
            player.draw(self.deck)
            return False
    
    def player_turn(self):
        player = self.players[0]
        
        # Check for mouse clicks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Check if a card is clicked
                for i, card in enumerate(player.hand):
                    card_x = 50 + i * (CARD_WIDTH + 10)
                    card_y = SCREEN_HEIGHT - CARD_HEIGHT - 20
                    if card_x <= x <= card_x + CARD_WIDTH and card_y <= y <= card_y + CARD_HEIGHT:
                        self.selected_card_index = i
                        break
        
        # Draw player's hand
        for i, card in enumerate(player.hand):
            card_x = 50 + i * (CARD_WIDTH + 10)
            card_y = SCREEN_HEIGHT - CARD_HEIGHT - 20
            card.draw(card_x, card_y, selected=(i == self.selected_card_index))
        
        # Draw discard pile
        if self.discard:
            self.discard[-1].draw(SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)
        
        # Draw current color
        color_text = font.render(f"Current Color: {self.current_color}", True, BLACK)
        screen.blit(color_text, (20, 20))
        
        # Draw current player
        player_text = font.render(f"Current Player: {self.players[self.current_player].name}", True, BLACK)
        screen.blit(player_text, (20, 60))
        
        # Draw Hatsune Miku
        screen.blit(miku_image, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 350))
        
        # Check if a card is selected
        if self.selected_card_index is not None:
            card = player.hand[self.selected_card_index]
            if card.color == self.current_color or card.color == 'wild' or card.value == self.discard[-1].value:
                player.play(self.selected_card_index)
                self.discard.append(card)
                if card.color == 'wild':
                    self.current_color = random.choice(['red', 'blue', 'green', 'yellow'])
                else:
                    self.current_color = card.color
                self.handle_special(card)
                self.selected_card_index = None
                self.next_turn()
    
    def check_winner(self):
        for i, player in enumerate(self.players):
            if not player.hand:
                return i
        return -1
    
    def start(self):
        clock = pygame.time.Clock()
        while True:
            screen.fill(WHITE)
            
            if self.current_player == 0:
                self.player_turn()
            else:
                self.ai_turn()
            
            winner = self.check_winner()
            if winner != -1:
                winner_text = font.render(f"{self.players[winner].name} wins!", True, BLACK)
                screen.blit(winner_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
                pygame.display.flip()
                pygame.time.wait(3000)
                break
            
            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    game = UNOGame()
    game.start()