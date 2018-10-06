"""
The primary frame containing the content for the entire game
"""
import tkinter as tk
import random as random
from quince.utility import is_valid_pickup
from quince.components import Ronda
from quince.ui.opponents.opponent_frame \
    import OpponentFrameHorizontal, OpponentFrameVertical
from quince.ui.table.table import Table
from quince.ui.player.player_frame import PlayerFrame


class GameFrame(tk.Frame):
    """Tk frame containing the main gameplay display including
    cards, decks, and avatars."""
    def __init__(self, parent, player, npc1, npc2, npc3, display_scores):
        """Instantiate a new GameFrame

        Args:
            parent (Tk widget)
            player - Player object representing the (human) user
            npc1 (NPC) - Shadow player (opponent)
            npc2 (NPC) - Shadow player (opponent)
            npc3 (NPC) - Shadow player (opponent)
            display_scores (function) - Callback to execute when
            a ronda is finished
        """
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.display_scores = display_scores

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        self.npc1 = npc1
        self.npc2 = npc2
        self.npc3 = npc3
        self.player = player
        self.selected_table_cards = []

        self.scores = {
            player: 0,
            npc1: 0,
            npc2: 0,
            npc3: 0,
        }

        self.dealer = self.npc2
        self.ronda = None
        self.start_new_ronda()

        # OPPONENT 1
        opp1_hand_size = len(self.ronda.player_cards[self.npc1]["hand"])
        opp1_active = self.ronda.current_player is self.npc1
        self.opp1 = OpponentFrameVertical(self,
                                          self.npc1.image(),
                                          self.npc1.name(),
                                          opp1_active,
                                          opp1_hand_size)
        self.opp1.grid(row=1, column=0)

        # OPPONENT 2
        opp2_active = self.ronda.current_player is self.npc2
        opp2_hand_size = len(self.ronda.player_cards[self.npc2]["hand"])
        self.opp2 = OpponentFrameHorizontal(self,
                                            self.npc2.image(),
                                            self.npc2.name(),
                                            opp2_active,
                                            opp2_hand_size)
        self.opp2.grid(row=0, column=1)

        # OPPONENT 3
        opp3_active = self.ronda.current_player is self.npc3
        opp3_hand_size = len(self.ronda.player_cards[self.npc3]["hand"])
        self.opp3 = OpponentFrameVertical(self,
                                          self.npc3.image(),
                                          self.npc3.name(),
                                          opp3_active,
                                          opp3_hand_size)
        self.opp3.grid(row=1, column=2)

        # PLAYER
        myhand = self.ronda.player_cards[self.player]["hand"]
        player_is_active = self.ronda.current_player is self.player
        self.hud = PlayerFrame(self,
                               self.player,
                               myhand,
                               player_is_active,
                               self.play_hand)
        self.hud.grid(row=2, column=0, columnspan=3)

        # TABLE
        table_cards = self.ronda.current_mesa
        self.tbl = Table(self, table_cards, self.register_table_card_selection)
        self.tbl.grid(row=1, column=1)

    def start_new_ronda(self):
        """Initialize a new round of gameplay."""
        # This is disgusting
        if self.dealer is self.player:
            self.dealer = self.npc1
        elif self.dealer is self.npc1:
            self.dealer = self.npc2
        elif self.dealer is self.npc2:
            self.dealer = self.npc3
        elif self.dealer is self.npc3:
            self.dealer = self.player

        self.ronda = Ronda.start([self.player,
                                  self.npc1,
                                  self.npc2,
                                  self.npc3],
                                 self.dealer)

    def draw(self):
        """Update all widgets on the frame"""
        self.selected_table_cards = []

        table_cards = self.ronda.current_mesa
        current_player = self.ronda.current_player

        # OPPONENT 1
        opp1_hand_size = len(self.ronda.player_cards[self.npc1]["hand"])
        opp1_active = self.ronda.current_player is self.npc1
        self.opp1.refresh(opp1_hand_size, opp1_active)

        # OPPONENT 2
        opp2_active = current_player is self.npc2
        opp2_hand_size = len(self.ronda.player_cards[self.npc2]["hand"])
        self.opp2.refresh(opp2_hand_size, opp2_active)

        # OPPONENT 3
        opp3_active = current_player is self.npc3
        opp3_hand_size = len(self.ronda.player_cards[self.npc3]["hand"])
        self.opp3.refresh(opp3_hand_size, opp3_active)

        # PLAYER
        myhand = self.ronda.player_cards[self.player]["hand"]
        player_is_active = current_player is self.player
        self.hud.refresh(myhand, player_is_active)

        # TABLE
        self.tbl.destroy()
        self.tbl = Table(self, table_cards, self.register_table_card_selection)
        self.tbl.grid(row=1, column=1)

    def register_table_card_selection(self, cards):
        """Callback function executed by the Table
        when the user selects cards.

        The list of cards is stored in the GameFrame's
        state so that it can be queried when the user
        makes a move.

        Args:
            cards (List of Card)
        """
        self.selected_table_cards = cards

    def play_hand(self, hand_card):
        """Callback function executed when
        player clicks the "Play Hand" button.
        """
        player = self.ronda.current_player
        valid = is_valid_pickup(hand_card, self.selected_table_cards)
        if player is self.player and valid:
            self.ronda = self.ronda.play_turn(hand_card,
                                              self.selected_table_cards)
            self.draw()
            self.play_next_move()
        else:
            print("not your turn")

    def play_next_move(self):
        """This function gets called continually as CPU players make
        their moves. When it's the user's turn to play, the loop is
        broken until they play their hand, which will start up the
        cycle again.
        """
        if self.ronda.is_finished:
            self.update_scores()
            self.display_scores(self.ronda, self.scores)
            return

        if self.ronda.current_player is self.player:
            pass
        else:
            sleep_time = random.randrange(1, 3)
            self.after(sleep_time*700, self._play_cpu_move)

    def _play_cpu_move(self):
        table_cards = self.ronda.current_mesa
        current_player = self.ronda.current_player
        hand = self.ronda.player_cards[current_player]["hand"]
        (own_card, mesa_cards) = current_player.get_move(hand, table_cards)

        self.ronda = self.ronda.play_turn(own_card, mesa_cards)

        # Yuck!
        if current_player is self.npc1:
            self.opp1.flash_card(own_card)
        elif current_player is self.npc2:
            self.opp2.flash_card(own_card)
        elif current_player is self.npc3:
            self.opp3.flash_card(own_card)

        self.after(1600, self._finish_turn)

    def _finish_turn(self):
        self.draw()
        self.play_next_move()

    def update_scores(self):
        """Updates the total scores for the game.

        Args:
            scores - Dictionary whose keys are players and
            whose values are the number of points to be added to
            their total scores.
        """
        scores = self.ronda.calculate_scores()
        siete = scores.get("7_de_velo", "Score Error")
        self.scores[siete] += 1

        (most_cards, _) = scores.get("most_cards", ([], None))
        for player in most_cards:
            self.scores[player] += 1

        (most_oros, _) = scores.get("most_oros", ([], None))
        for player in most_oros:
            self.scores[player] += 1

        setenta = scores.get("setenta", [])
        for winner in setenta:
            self.scores[winner.player] += 1

        escobas = scores.get("escobas", [])
        for escoba in escobas:
            (player, count) = escoba
            self.scores[player] += count
