import procgame.game
from procgame.game import AdvancedMode
import logging

class EscapeRoute(procgame.game.AdvancedMode):
    """
    Example of T2 "Escape Route" functionality
    (described in the rules PDF on page J)

    TODO: Sound effects, other visual feedback??

    """
    def __init__(self, game):
        super(EscapeRoute, self).__init__(game=game, priority=30, mode_type=AdvancedMode.Game)

        # useful to set-up a custom logger so it's easier to track debugging messages for this mode
        self.logger = logging.getLogger('EscapeRoute')

        # the names of the progress lamps as a list for easier code
        # via indexing, later
        self.esc_lamps = ["securityPass", "holdBonus47", "lightHurryUp",
                "multiball", "extraBall44", "million10"]

        self.qualified = 0 # the number that are flashing
        self.collected = 0 # the number the player already has
        self.laps = 0

        self.mid_switches = [False, False, False]
        self.awards = [] # the list of awards

        pass

    def evt_player_added(self, player):
        player.setState('esc_route_qualified',0)
        player.setState('esc_route_collected',0)
        player.setState('esc_route_laps',0)

    def evt_ball_starting(self):
        self.cancel_delayed(name="disabler")
        self.mid_switches = [False, False, False]
        self.qualified = self.game.getPlayerState("esc_route_qualified")
        self.collected = self.game.getPlayerState("esc_route_collected")
        self.laps = self.game.getPlayerState("esc_route_laps")
        self.sync_lamps_to_progress()

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.cancel_delayed(name="disabler")
        self.game.setPlayerState("esc_route_qualified", self.qualified)
        self.game.setPlayerState("esc_route_collected", self.collected)
        self.game.setPlayerState("esc_route_laps", self.laps)

    def sw_standupMidL_active(self, sw):
        self.mid_switches[0] = True
        self.game.lamps.standupMidL.enable()
        self.checkAllSwitches()
        return procgame.game.SwitchStop

    def sw_standupMidC_active(self, sw):
        self.mid_switches[1] = True
        self.game.lamps.standupMidC.enable()
        self.checkAllSwitches()
        return procgame.game.SwitchStop

    def sw_standupMidR_active(self, sw):
        self.mid_switches[2] = True
        self.game.lamps.standupMidR.enable()
        self.checkAllSwitches()
        return procgame.game.SwitchStop

    def checkAllSwitches(self):
        """ called by each of the standupMid? handlers to
            determine if the bank has been completed """
        if(self.mid_switches[0] and self.mid_switches[1] and
            self.mid_switches[2]): # all three are True
                self.game.displayText("Shoot the escape route!")
                self.game.score(1000)
                self.game.sound.play('target_bank')
                self.game.lamps.standupMidL.disable()
                self.game.lamps.standupMidC.disable()
                self.game.lamps.standupMidR.disable()
                self.qualified += 1
                self.mid_switches = [False, False, False]
                self.sync_lamps_to_progress()
        else:
                self.game.score(10)
                self.game.sound.play('target')
        self.debug()

    def debug(self):
        self.logger.info("qualified = %d; collected = %d" % (self.qualified, self.collected))

    def sw_lockTop_active_for_500ms(self, sw):
        if(self.qualified > self.collected):
            # do award
            self.game.displayText("Collected " + str(self.collected))
            self.collected += 1
        else:
            self.game.displayText("Jackpot grows!")
            self.game.score(10)
        self.debug()
        self.sync_lamps_to_progress()

    def sw_lockTop_active_for_1s(self, sw):
        self.game.coils.lockTop.pulse()

    def disable_progress_lamps(self):
        for l in self.esc_lamps:
            self.game.lamps[l].disable()

    def set_lamp(self, lamp_name, state):
        l = self.game.lamps[lamp_name]
        if(state==0):
            l.disable()
        elif(state==1):
            l.enable()
        elif(state==2):
            l.schedule(0xff00ff00)
        elif(state==3):
            l.schedule(0xf0f0f0f0)

    def sync_lamps_to_progress(self):
        for i in range(0, len(self.esc_lamps)):
            l_state = 0
            if(self.collected>i):
                l_state = 1
            elif(self.qualified>i):
                l_state = 2
            self.logger.info("setting " + self.esc_lamps[i] + " to " + str(l_state))
            self.set_lamp(self.esc_lamps[i], l_state)

        self.set_lamp("standupMidL",self.mid_switches[0])
        self.set_lamp("standupMidC",self.mid_switches[1])
        self.set_lamp("standupMidR",self.mid_switches[2])

