import procgame.game
from procgame.game import AdvancedMode

class SkillshotMode(procgame.game.AdvancedMode):
  """
  Skill shot Mode
  """
  def __init__(self, game):
    super(SkillshotMode, self).__init__(game=game,
      priority=10, mode_type=AdvancedMode.Ball) # 10 is the highest so far
    # stuff that gets done EXACTLY once.
    # happens when the "parent" Game creates this mode
    self.layer = self.game.animations["HK"]
    pass

  """
  called when the mode is activated (added to the queue)
  """
  def mode_started(self):
    self.number = 1
    self.direction = 1
    self.cancel_delayed("next_target")
    self.game.sound.play('HK_ship')
    self.delay(name="next_target", delay=1.0, handler=self.next_target)
    self.done = False
  """
  a function that changes number by direction,
  keeping the number between 1 and 5; also displays
  the number on the screen
  """
  def next_target(self):
    self.game.sound.play('skill_shot_tick')
    self.game.lamps["target%d" % self.number].disable()
    self.number = self.number + self.direction
    if(self.number == 5):
      self.direction = -1
    elif(self.number == 1):
      self.direction = 1
    self.game.displayText("Hit target %d" % self.number)
    # self.game.lamps.target3.schedule(0xf0f0f0)
    self.game.lamps["target%d" % self.number].schedule(0xf0f0f0)
    self.delay(name="next_target", delay=1.0, handler=self.next_target)

  def mode_stopped(self):
    self.done = True
    self.game.lamps.target1.disable()
    self.game.lamps.target2.disable()
    self.game.lamps.target3.disable()
    self.game.lamps.target4.disable()
    self.game.lamps.target5.disable()
    self.game.sound.fadeout_music()
    self.game.sound.play_music('base-music-bgm')

  def evt_ball_starting(self):
    self.game.sound.stop_music()
    self.game.sound.play_music('skillshot')
    self.game.displayText("Hit the flashing target!")


  def sw_gripTrigger_active(self, sw):
    if(self.game.switches.shooter.is_active()):
      self.game.sound.play('plunge')
      self.game.coils.plunger.pulse()

  def checktarget(self, target_num):
    if(self.done):
      return procgame.game.SwitchContinue
    self.cancel_delayed("next_target")
    self.game.lamps.target1.disable()
    self.game.lamps.target2.disable()
    self.game.lamps.target3.disable()
    self.game.lamps.target4.disable()
    self.game.lamps.target5.disable()
    if(self.number == target_num):
      self.game.displayText("Skillshot!")
      self.game.score(1000000)
      self.game.sound.play('fire')
      self.delay(delay=0.5,handler=self.game.sound.play, param='explosion')
      self.delay(delay=2.5,handler=self.game.modes.remove,param=self)
    else:
      self.game.sound.play('fire')
      self.game.displayText("missed.")
      self.delay(delay=1.0,handler=self.game.modes.remove,param=self)
    self.done = True
    return procgame.game.SwitchStop

  # Example of how to handle a switch hit
  def sw_target3_active(self, sw):
    return self.checktarget(3)

  def sw_target1_active(self, sw):
    return self.checktarget(1)

  def sw_target2_active(self, sw):
    return self.checktarget(2)

  def sw_target4_active(self, sw):
    return self.checktarget(4)

  def sw_target5_active(self, sw):
    return self.checktarget(5)

