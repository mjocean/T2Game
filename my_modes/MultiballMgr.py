import procgame.game
from procgame.game import AdvancedMode
import logging

class MultiballMgr(procgame.game.AdvancedMode):
    """
    Example of monitoring events for T2 to prepare for
    Multiball

    TODO: Sound effects, other visual feedback??

    """
    def __init__(self, game):
        super(MultiballMgr, self).__init__(game=game, priority=30, mode_type=AdvancedMode.Game)

        # useful to set-up a custom logger so it's easier to track debugging messages for this mode
        self.logger = logging.getLogger('MultiballMgr')
        self.in_multiball = False
        pass

    def sw_dropTarget_active_for_100ms(self, sw):
        self.game.sound.stop_music()
        self.game.sound.play_music('load_the_gun')

    def sw_ballPopper_active_for_450ms(self,sw):
        if(self.in_multiball):
            # check number of balls locked vs. in play
            # if all balls locked:
            if(self.game.gun_mode.is_clear_to_feed()):
                self.game.coils.ballPopper.pulse()
            else:
                # ... we have a problem
                pass
        else:
            # trying to obtain multiball
            # add a staging mode
            self.game.modes.add(self.game.multiball_skillshot)
            if(self.game.gun_mode.is_clear_to_feed()):
                # staging nonsense
                self.game.coils.ballPopper.pulse()
            #else:
                # something else
        return procgame.game.SwitchContinue

