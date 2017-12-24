####
## Lane Change Mode

import procgame.game
from procgame.game import AdvancedMode

class LaneChangeMode(procgame.game.AdvancedMode):
  """
  manages the lanes/lane-lights at the top of the playfield
  - when a lane is rolled over, the light goes on for that lane
    - re-rolling over the lane does not turn it off
  - when the player flips right or left, the lane lights shift
  - when all three have been hit, an award is given
  """
  def __init__(self, game):
    super(LaneChangeMode, self).__init__(game=game, priority=10, mode_type=AdvancedMode.Ball)
    # stuff that gets done EXACTLY once.
    # happens when the "parent" Game creates this mode

    self.laneSwitches = ['laneL', 'laneC', 'laneR']
    self.laneLamps = ['laneL', 'laneC', 'laneR']

    # used to hold the state of the lane lights
    self.laneStates = [False, False, False]
    pass

  def mode_started(self):
    print("Lane mode started")
    self.laneStates = [False, False, False]

    for switch in self.laneSwitches:
      self.add_switch_handler(name=switch, event_type='active', \
        delay=None, handler=self.switch_rollover)

    self.update_lamps()

  def mode_stopped(self):
    print("Lane mode ended")
    self.cancel_delayed('stopFlashing')
    # do cleanup of the mode here.

  def update_lamps(self):
    """ update the lights to reflect the state of the lanes """
    # make left lane light reflect left lane state
    print(self.laneStates)
    for state, sw, lamp in zip(self.laneStates, self.laneSwitches, self.laneLamps):
      if(state==True):
        self.game.lamps[lamp].enable()
      else:
        self.game.lamps[lamp].disable()

  def checkBonus(self):
    if all(self.laneStates):
      self.laneStates = [False, False, False]
      self.update_lamps()

      self.game.score(100000)
      self.game.displayText("lanes completed")

  def sw_flipperLwR_active(self, sw):
    # shift right
    t = self.laneStates[-1:] + self.laneStates[:-1]
    self.laneStates = t
    self.update_lamps()           # make the lights reflect the states
    return procgame.game.SwitchContinue

  def sw_flipperLwL_active(self, sw):
    t = self.laneStates[1:] + self.laneStates[:1]
    self.update_lamps()
    return procgame.game.SwitchContinue

  def switch_rollover(self, sw):
    i = self.laneSwitches.index(sw.name)
    self.laneStates[i] = True
    self.game.lamps[self.laneLamps[i]].schedule(schedule=0xff00ff00)
    self.checkBonus()
    self.delay(name="stopFlashing", delay=2, handler=self.update_lamps)
    return procgame.game.SwitchContinue

