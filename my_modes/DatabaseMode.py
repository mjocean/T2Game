import procgame.game
from procgame.game import AdvancedMode
import logging

class DatabaseMode(procgame.game.AdvancedMode):
    """
    Example of T2 "Database" functionality
    --random award on lockLeft if database is lit
    knockdown of droptarget awards database

    TODO: Sound effects, other visual feedback??

    """
    def __init__(self, game):
        super(DatabaseMode, self).__init__(game=game, priority=30, mode_type=AdvancedMode.Game)

        # useful to set-up a custom logger so it's easier to track debugging messages for this mode
        self.logger = logging.getLogger('DatabaseMode')

        self.db_enabled = False

        self.awards = [250000, 500000, 750000, 1000000, 3000000, 5000000]

        pass

    def sw_dropTarget_active(self, sw):
        self.db_enabled = True
        self.game.lamps.database1.enable()

    def evt_ball_starting(self):
        self.db_enabled = False
        self.game.coils.dropTarget.pulse()
        self.game.lamps.database1.disable()

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.game.coils.dropTarget.pulse()
        self.game.lamps.database1.disable()

    def sw_lockLeft_active_for_500ms(self, sw):
        # advertise and start random award
        self.game.lamps.database1.disable()
        if(self.db_enabled):
            self.game.displayText(["databse random award","50,000"])
            self.game.score(50000)
        else:
            self.game.displayText("Jackpot grows")
            self.game.score(10000)

    def sw_lockLeft_active_for_1s(self, sw):
        if(not self.db_enabled):
            self.game.coils.lockLeft.pulse()

    def sw_lockLeft_active_for_3s(self, sw):
        self.db_enabled = False
        self.game.coils.lockLeft.pulse()

