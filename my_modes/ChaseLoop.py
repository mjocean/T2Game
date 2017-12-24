import procgame.game
from procgame.game import AdvancedMode
import logging

class ChaseLoop(procgame.game.AdvancedMode):
    """
    Example of T2 "Chase Loop" functionality
    (described in the rules PDF on page J)

    TODO: Sound effects, other visual feedback??

    """
    def __init__(self, game):
        super(ChaseLoop, self).__init__(game=game, priority=30, mode_type=AdvancedMode.Game)

        # useful to set-up a custom logger so it's easier to track debugging messages for this mode
        self.logger = logging.getLogger('ChaseLoop')

        # the names of the progress lamps as a list for easier code
        # via indexing, later
        self.chase_lamps = ["twofiftyK", "fivehunK", "sevenfiftyK",
                "oneMil", "threeMil", "fiveMil"]

        self.collected = 0 # the number the player already has
        self.loop_seq = [False, False, False, False]

        self.awards = [250000, 500000, 750000, 1000000, 3000000, 5000000] # the list of awards

        pass

    def evt_player_added(self, player):
        player.setState('chase_current',0)

    def evt_ball_starting(self):
        self.cancel_delayed(name="disabler")
        self.mid_switches = [False, False, False]
        self.collected = 0 # progress resets on new ball
        self.sync_lamps_to_progress()
        self.loop_seq = [False, False, False, False]

    def evt_ball_ending(self, (shoot_again, last_ball)):
        self.cancel_delayed(name="disabler")


    def debug(self):
        # self.logger.info("escL: %d, escH: %d, clH:%d, clL:%d" % (self.game.switches.escapeL.hw_timestamp, self.game.switches.escapeH.hw_timestamp, self.game.switches.chaseLoopHigh.hw_timestamp, self.game.switches.chaseLoopLow.hw_timestamp))
        self.logger.info("collected = %d" % (self.collected))

    def sw_chaseLoopLow_active(self, sw):
        self.seq_handler(0)

    def sw_chaseLoopHigh_active(self, sw):
        self.seq_handler(1)

    def sw_escapeH_active(self, sw):
        self.seq_handler(2)

    def sw_escapeL_active(self, sw):
        if(self.seq_handler(3)):
            # loop complete
            self.chase_loop_award()
            self.loop_seq = [False, False, False, False]

    def seq_handler(self, num):
        self.cancel_delayed(name="clear_%d" % num)

        # if a previous switch is False, no sequence
        if(False in self.loop_seq[0:num]):
            self.logger.info("saw later switch -- sequence destroyed")
            for i in range(0,num):
                self.reset_switch_memory(i)
            self.loop_seq[num] = False
            self.logger.info("hit %d | Sequence: %s" % (num, self.loop_seq))
            return False

        self.loop_seq[num] = True
        # clear later switches
        for i in range(num+1,4):
            self.reset_switch_memory(i)
        self.logger.info("hit %d | Sequence: %s" % (num, self.loop_seq))
        if(num!=3):
            self.delay(name="clear_%d" % num, delay=4.0, handler=self.reset_switch_memory, param=num)
        return True

    def reset_switch_memory(self, switch_num):
        self.cancel_delayed(name="clear_%d" % switch_num)
        if(self.loop_seq[switch_num] == False):
            return # nothing to do
        self.loop_seq[switch_num] = False
        self.logger.info("RESET %d | Sequence: %s" % (switch_num, self.loop_seq))

    def OFF_sw_escapeL_active(self, sw):
        self.debug()
        if(self.game.switches.chaseLoopLow.hw_timestamp == None):
            return procgame.game.SwitchContinue

        if (((self.game.switches.escapeL.hw_timestamp - self.game.switches.chaseLoopLow.hw_timestamp) < 2000) and
            (self.game.switches.escapeL.hw_timestamp > self.game.switches.escapeH.hw_timestamp) and
            (self.game.switches.escapeH.hw_timestamp > self.game.switches.chaseLoopHigh.hw_timestamp) and
            (self.game.switches.chaseLoopHigh.hw_timestamp > self.game.switches.chaseLoopLow.hw_timestamp)):
            self.chase_loop_award()
            return procgame.game.SwitchStop
        else:
            return procgame.game.SwitchContinue

    def chase_loop_award(self):
        self.sync_lamps_to_progress(special=self.collected)
        self.game.displayText("Chase Loop " + str(self.awards[self.collected]))
        self.game.score(self.awards[self.collected])

        if(self.collected < len(self.chase_lamps)-1):
            self.collected += 1
        else:
            # already got them all
            pass

        self.debug()
        self.delay(name="lamp_sync", delay=1.0, handler=self.sync_lamps_to_progress)


    def disable_progress_lamps(self):
        for l in self.chase_lamps:
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

    def sync_lamps_to_progress(self, special=None):
        self.cancel_delayed(name="lamp_sync")
        for i in range(0, len(self.chase_lamps)):
            l_state = 0
            if(special is not None and i==special):
                l_state=3
            elif(self.collected>i):
                l_state = 1
            elif(self.collected==i):
                l_state = 2
            self.logger.info("setting " + self.chase_lamps[i] + " to " + str(l_state))
            self.set_lamp(self.chase_lamps[i], l_state)


