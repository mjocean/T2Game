import procgame.game
from procgame.game import AdvancedMode
import logging
import random

class MultiballSkillShot(procgame.game.AdvancedMode):
  def __init__(self, game):
    super(MultiballSkillShot, self).__init__(game=game, priority=50, mode_type=AdvancedMode.Manual)
    self.layer = self.game.animations["HK"]
    self.logger = logging.getLogger('MultiballSkillShot')
    pass

  def mode_started(self):
    self.number = random.randint(1,5)
    self.cancel_delayed(name="MultiballSkillShot")
    self.game.displayText(["Hit target %d" % self.number, "to start multiball"])
    self.game.lamps["target%d" % self.number].schedule(0xf0f0f0)
    self.delay(name="MultiballSkillShot", delay=10.0, handler=self.remove_self)
    self.game.sound.fadeout_music()
    self.game.sound.play_music('mb-pending-skillshot')

  def remove_self(self):
    self.game.modes.remove(self)
    self.game.sound.fadeout_music()
    self.game.sound.play_music('base-music-bgm')

  def mode_stopped(self):
    self.game.lamps.target1.disable()
    self.game.lamps.target2.disable()
    self.game.lamps.target3.disable()
    self.game.lamps.target4.disable()
    self.game.lamps.target5.disable()

  def sw_gripTrigger_active(self, sw):
    self.game.sound.play('plunge')

  def checktarget(self, target_num):
    if(self.number == target_num):
      self.game.displayText("Multiball!!")
      self.game.score(1000000)
      self.game.sound.play('multiball-hit')
      self.game.modes.remove(self)
      # TODO: Add multiball mode!!
    else:
      self.game.sound.play('miss')
      self.remove_self()
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

