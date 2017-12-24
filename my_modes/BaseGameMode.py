import procgame.game
from procgame.game import AdvancedMode
import logging

class BaseGameMode(procgame.game.AdvancedMode):
    """
    An example of a mode that runs whenever the GAME is in progress.
    Notice the super() function call in __init__ below specifies
     the mode_type is set to AdvancedMode.Game.  This means:
    - it is automatically added when a game starts
        (mode_started will be called once per game)
    - it is automatically removed when a game ends
        (mode_stopped will be called once per game)

    NOTE: a second player does not cause a second game
        (confusing, no doubt).  When a new player is
        added, an evt_player_added will fire.  When
        a new ball starts, that's a good time to ensure
        our data comes from that player and sync up
        lamps via a call to update_lamps.  Read on...
    """

    def __init__(self, game):
        """
        The __init__ function is called automatically whenever an instance
        of this object is created --e.g., whenever the code:
                something = new BaseGameMode()
        is executed, this __init__ function is called
        """

        # a call to 'super' call's the parent object's __init__ method
        # in this case, it calls the procgame.game.Mode's init()
        super(BaseGameMode, self).__init__(game=game, priority=5, mode_type=AdvancedMode.Game)

        # useful to set-up a custom logger so it's easier to track debugging messages for this mode
        self.logger = logging.getLogger('BaseGameMode')

        # You might be used to storing data right in the mode, like as follows:
        # self.leftTargets = [False, False, False, False, False]
        # self.kickbackEnabled = False

        # you CAN do this, and it's OK to do so, but if these are properties
        #  of the PLAYER not the mode, so if there's more than one player,
        #  when the player number changes, these are no longer valid, but we
        #  may want to restore them when this player's turn resumes.

        #  We need to store some data per player.  Fortunately, that's
        #  what the player object lets us do! --that said, the player
        #  does not yet exist when the mode is created, so it's too early to
        #  add these fields... in this method
        pass

    def evt_player_added(self, player):
        """ an event that gets fired whenever a player is added to the game (presses start);
            the player argument is the newly created player who has just been added.
            In a multiplayer game, this event will hand the mode the newly created player
            as an argument, during another player's turn (the new player is not yet active).
        """
        player.setState('multiplier', 0)
        player.setState('kickbackEnabled', False)

        """
        Notice that progress is stored in the player object, so LATER when the player is active,
        we can get values with:
            self.game.getPlayerState(key)
        which is a wrapper around:
            self.game.get_current_player().getState(key)
        """

    def evt_ball_starting(self):
        """ an event that gets fired when a ball is starting --note that
            the ball is not yet in play (hasn't been plunged) but this event
            lets us know that the ball is about to be fed to the shooter lane
            to be plunged
        """
        # turn on the GI lamps
        self.game.lamps.topInsertGI.enable()
        self.game.lamps.playfieldLeftGI.enable()
        self.game.lamps.playfieldRightGI.enable()
        self.game.lamps.bottomInsertGI.enable()

        # fadeout any music that might already be playing, and play some new music
        self.game.sound.fadeout_music()
        self.game.sound.play_music('base-music-bgm')

    def sw_shooter_inactive_for_250ms(self, sw):
        # When the ball has been free of the shooter lane for 250ms, we reset the ball
        # saver, so that the ball saver timer is based on the ball leaving the shooter
        # lane
        self.game.enable_ball_saver()


    def evt_ball_saved(self):
        """ this event is fired to notify us that a ball has been saved
        """
        self.logger.info("BaseGameMode: BALL SAVED")
        self.game.sound.play('ball_saved') # plays a sound with key 'ball_saved' defined in `asset_list.yaml`
        self.game.displayText('Ball Saved!') # shows a message on the player's screen

        # you probably won't even see this
        self.game.coils.flasherShootAgain.pulse()
        # we do NOT tell the trough to launch balls; in SkeletonGame it's handled automatically/

    def mode_started(self):
        """
        the mode_started method is called whenever this mode is added
        to the mode queue (activated); this might happen multiple times per
        game, depending on how the Game itself adds/removes it.  B/C this is
        an AdvancedMode with mode_type=AdvancedMode.Game, we know when it will
        be added when a game is started and removed when the game ends.
        """
        pass

    def mode_stopped(self):
        """
        the mode_stopped method is called whenever this mode is removed
        from the mode queue; see `mode_started(self)`
        """
        pass

    def update_lamps(self):
        """
        update_lamps is a very important method -- you use it to set the lamps
        to reflect the current state of the internal mode progress variables.
        This method is called after a lampshow is played so that the player's
        view of the state on the lamps is correctly reflected after the
        lampshow is done.  It can be called other times, too.

        Notice that progress is stored in the player object, so check with:
            self.game.getPlayerState(key)
        which is a wrapper around:
            self.game.get_current_player().getState(key)
        """
        if(self.game.getPlayerState('kickbackEnabled')==True):
            self.game.lamps.kickback.enable()
        else:
            self.game.lamps.kickback.disable()

        if(self.game.getPlayerState('multiplier') == 2):
            self.game.lamps.mult2x.enable()
        else:
            self.game.lamps.mult2x.disable()


    """ The following are the event handlers for events broadcast by SkeletonGame.
        handling these events lets your mode give custom feedback to the player
        (lamps, dmd, sound, etc)
    """

    def evt_ball_ending(self, (shoot_again, last_ball)):
        """ this is the handler for the evt_ball_ending event.  The framework fires
            this event so your code can show the player information about the end of the
            ball; notice this event is ball endING not endED; so you technically the
            framework hasn't committed to the idea that the ball is over yet, but it is
            unavoidable at this point.  You can delay the event propegation to "buy time"
            if you have things you need to happen before the event is complete.  Once the
            event is complete, the bonus mode will start, then the next ball will start.
            If I want to show something before all of that, I need to stall the ball end.
            For example, if I wanted to show the player a message for 5 seconds before
            the ball actually ended (and bonus mode began), I would return 5.
            Returning 0 (or None) would indicate no delay.
        """
        self.logger.info("base game mode trough changed notification ('ball_ending - again=%s, last=%s')" % (shoot_again,last_ball))

        # stop any music as appropriate
        # self.game.sound.fadeout_music()
        self.game.sound.play('ball_drain')
        self.game.sound.play_music('sonic')
        self.game.displayText('End of ball')
        return 2.0

    def evt_game_ending(self):

        # show the message GAME ENDED, on top of an animation asset with key 'gameover' (in `asset_list.yaml`) for 2.0 seconds
        self.game.displayText("GAME ENDED", 'gameover', duration=2.0)

        # return 2 so the framework knows that after 2 seconds, the game can continue ending.
        return 2


    """
    this is an example of a timed switch handler
         sw_      : indicates a switch handler
         outhole  : the name of the switch
         active   : the state (could be inactive, open, closed)
         for_200ms: how long that the switch must be detected
                                in this state before this handler is called

    in this case, if the controller sees this switch closed
    for 200ms, then this function is called; waiting 200ms
    will wait for long enough for the ball to settle in the
    slot before responding
    """
    def sw_outhole_active_for_200ms(self,sw):
            self.game.coils.outhole.pulse()

    def kickback_disabler(self, phase=0):
        if(phase > 0):
            self.game.lamps.kickback.schedule(schedule=0x0f0f0f0)
            self.delay(name='disable_kickback',
                                 delay=2.0,
                                 handler=self.kickback_disabler,
                                 param=0)
        else:
            self.game.setPlayerState('kickbackEnabled',False)
            self.game.lamps.kickback.disable()
            self.kickback_used = False

    def sw_outlaneL_active(self, sw):
        if(self.game.getPlayerState('kickbackEnabled')):
            self.game.coils.kickback.pulse()
            self.game.sound.play('kickback')
            self.game.score(100)
            self.game.displayText("Kickback!!!")
            if(not self.kickback_used):
                self.kickback_used = True
                self.game.lamps.kickback.schedule(schedule=0xff00ff00)
                self.delay(name='disable_kickback',
                                     delay=3.0,
                                     handler=self.kickback_disabler,
                                     param=1)
        else:
            self.game.displayText("Too bad")

        return procgame.game.SwitchContinue

    def sw_slingL_active(self, sw):
        self.game.score(100)
        self.game.sound.play('shot_generic')
        return procgame.game.SwitchContinue

    def sw_slingR_active(self, sw):
        self.game.score(100)
        self.game.sound.play('shot_generic')
        return procgame.game.SwitchContinue

    def sw_gripTrigger_active(self, sw):
        if self.game.switches.shooter.is_active():
            self.game.coils.plunger.pulse()
            self.game.sound.play('plunge')
        return procgame.game.SwitchStop

    def sw_jetL_active(self, sw):
        self.game.score(100)
        self.game.sound.play('shot_generic')

    def sw_jetR_active(self, sw):
        self.game.score(100)
        self.game.sound.play('shot_generic')

    def sw_jetB_active(self, sw):
        self.game.score(100)
        self.game.sound.play('shot_generic')

    def sw_standupRightT_active(self, sw):
        self.game.score(100)
        if(self.game.getPlayerState('r_T')):
            # already got it
            self.game.sound.play('target_again')
        else:
            self.game.setPlayerState('r_T', True)
            self.kickback_targets_update()

    def sw_standupRightM_active(self, sw):
        self.game.score(100)
        if(self.game.getPlayerState('r_M')):
            # already got it
            self.game.sound.play('target_again')
        else:
            self.game.setPlayerState('r_M', True)
            self.kickback_targets_update()

    def sw_standupRightB_active(self, sw):
        self.game.score(100)
        if(self.game.getPlayerState('r_B')):
            # already got it
            self.game.sound.play('target_again')
        else:
            self.game.setPlayerState('r_B', True)
            self.kickback_targets_update()

    def kickback_targets_update(self):
        if(self.game.getPlayerState('r_B') and
            self.game.getPlayerState('r_M') and
            self.game.getPlayerState('r_T')):
            self.game.setPlayerState('kickbackEnabled', True)
            self.game.lamps.kickback.enable()
            self.game.score(1000)
            self.game.displayText('kickback enabled')
            self.game.sound.play('kickback_enabled')
            return True
        else:
            self.game.sound.play('target')
            return False