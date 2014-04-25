import os
from __main__ import vtk, qt, ctk, slicer
import EditorLib
from EditorLib.EditOptions import HelpButton
from EditorLib.EditOptions import EditOptions
from EditorLib import EditUtil
from EditorLib import LabelEffect

from EditorLib import Effect
from EditorLib import LabelEffectLogic

from copy import copy, deepcopy
import numpy as np
#
# The Editor Extension itself.
#
# This needs to define the hooks to be come an editor effect.
#

#
# FastGrowCutEffectOptions - see LabelEffect, EditOptions and Effect for superclasses
#

class FastGrowCutEffectOptions(EditorLib.LabelEffectOptions):
  """ FastGrowCutEffect-specfic gui
  """

  def __init__(self, parent=0):
    super(FastGrowCutEffectOptions,self).__init__(parent)
    #~ print("Made a FastGrowCutEffectOptions")
    
    #save a layout manager, get all 3 slice widgets
    editUtil = EditorLib.EditUtil.EditUtil()
    parameterNode = editUtil.getParameterNode()
    lm = slicer.app.layoutManager()
    self.redSliceWidget = lm.sliceWidget('Red')
    self.yellowSliceWidget = lm.sliceWidget('Yellow')
    self.greenSliceWidget = lm.sliceWidget('Green')
    self.parameterNode=parameterNode
    self.attributes = ('MouseTool')
    self.displayName = 'FastGrowCutEffect Effect'

  def __del__(self):
    super(FastGrowCutEffectOptions,self).__del__()

  def create(self):
    super(FastGrowCutEffectOptions,self).create()
    self.helpLabel = qt.QLabel("Run the Fast GrowCut segmentation on the current label/seed image.\n Background and foreground seeds will be used as starting points to fill in the rest of the volume.", self.frame)
    self.frame.layout().addWidget(self.helpLabel)
    
    #create a "Start Bot" button
    self.botButton = qt.QPushButton(self.frame)

    self.frame.layout().addWidget(self.botButton)
    self.botButton.connect('clicked()', self.onStartBot)

    self.locRadFrame = qt.QFrame(self.frame)
    self.locRadFrame.setLayout(qt.QHBoxLayout())
    self.frame.layout().addWidget(self.locRadFrame)
    self.widgets.append(self.locRadFrame)

    #HelpButton(self.frame, "TO USE: \n Start the interactive segmenter and initialize the segmentation with any other editor tool. \n KEYS: \n Press the following keys to interact: \n C: copy label slice \n V: paste label slice \n Q: evolve contour in 2D \n E: evolve contour in 3D \n A: toggle between draw/erase modes" )
    HelpButton(self.frame, "TO USE: \n Start the Fast GrowCut segmenter and initialize the segmentation with any other editor tool. \n KEYS: \n Press the following keys to interact: \n G: start Fast GrowCut \n S: toggle between seed image and segmentation result \n R: reset fast GrowCut \n" )
    self.frame.layout().addStretch(1) # Add vertical spacer
    
    if hasattr(slicer.modules, 'FGCEditorBot'):
	  slicer.util.showStatusMessage(slicer.modules.FGCEditorBot.logic.currentMessage)
	  self.botButton.text = "Stop FastGrowCut Segmenter"
	  if self.locRadFrame:
		self.locRadFrame.hide()
    else:
	  self.botButton.text = "Start FastGrowCut Segmenter"
	  if self.locRadFrame:
		self.locRadFrame.show()

  def destroy(self):
	self.currentMessage = ""
	slicer.util.showStatusMessage(self.currentMessage)
	
	super(FastGrowCutEffectOptions,self).destroy()
    

  # note: this method needs to be implemented exactly as-is
  # in each leaf subclass so that "self" in the observer
  # is of the correct type
  def updateParameterNode(self, caller, event):
    node = EditUtil.EditUtil().getParameterNode()
    if node != self.parameterNode:
      if self.parameterNode:
        node.RemoveObserver(self.parameterNodeTag)
      self.parameterNode = node
      self.parameterNodeTag = node.AddObserver(vtk.vtkCommand.ModifiedEvent, self.updateGUIFromMRML)

  def setMRMLDefaults(self):
    super(FastGrowCutEffectOptions,self).setMRMLDefaults()

  def onStartBot(self):

    """Stop CarreraSlice bot to avoid conflicts"""
    if hasattr(slicer.modules, 'editorBot'):
      slicer.modules.editorBot.stop()
      del(slicer.modules.editorBot)
      
    """create the bot for background editing"""      
    if hasattr(slicer.modules, 'FGCEditorBot'):
      slicer.modules.FGCEditorBot.stop()
      del(slicer.modules.FGCEditorBot)
      if self.botButton:
        self.botButton.text = "Start Fast GrowCut Segmenter"   
        slicer.util.showStatusMessage("FastGrowCut: stopped")     
      if self.locRadFrame:
        self.locRadFrame.show()
    else:
      FastGrowCutBot(self)
      slicer.modules.FGCEditorBot.logic.emergencyStopFunc = self.botEstop; #save the function that stops bot, destroys FastGrowCut segmenter, if things go wrong
      if self.botButton:
        self.botButton.text = "Stop Fast GrowCut Segmenter"  
        self.currentMessage =  "FastGrowCut started: go to PaintEffect to edit seed image or press G to do fast GrowCut"
        slicer.util.showStatusMessage(self.currentMessage)        
        
      if self.locRadFrame:
        self.locRadFrame.hide()

  def updateGUIFromMRML(self,caller,event):
    self.disconnectWidgets()
    super(FastGrowCutEffectOptions,self).updateGUIFromMRML(caller,event)
    self.connectWidgets()

  #def onApply(self):
  #  print('This is just an example - nothing here yet')

  def updateMRMLFromGUI(self):
    if self.updatingGUI:
      return
    disableState = self.parameterNode.GetDisableModifiedEvent()
    self.parameterNode.SetDisableModifiedEvent(1)
    super(FastGrowCutEffectOptions,self).updateMRMLFromGUI()
    self.parameterNode.SetDisableModifiedEvent(disableState)
    if not disableState:
      self.parameterNode.InvokePendingModifiedEvent()


  def botEstop(self):
    if hasattr(slicer.modules, 'FGCEditorBot'):
      slicer.modules.FGCEditorBot.stop()
      del(slicer.modules.FGCEditorBot)
      if self.botButton:
        self.botButton.text = "Start Fast GrowCut Segmenter"
      if self.locRadFrame:
        self.locRadFrame.show()

class FastGrowCutBot(object): #stays active even when running the other editor effects
  """
Task to run in the background for this effect.
Receives a reference to the currently active options
so it can access tools if needed.
"""
  def __init__(self,options):
    self.editUtil = EditUtil.EditUtil()
    self.sliceWidget = options.tools[0].sliceWidget
    #self.sliceWidget = slicer.app.layoutManager().sliceWidget('Red')
    if hasattr(slicer.modules, 'FGCEditorBot'):
      slicer.modules.FGCEditorBot.active = False
      del(slicer.modules.FGCEditorBot)
    slicer.modules.FGCEditorBot = self

    self.redSliceWidget=options.redSliceWidget
    self.greenSliceWidget=options.greenSliceWidget
    self.yellowSliceWidget=options.yellowSliceWidget
    self.start()

  def start(self):
    sliceLogic = self.sliceWidget.sliceLogic()
    self.logic = FastGrowCutEffectLogic( self.redSliceWidget.sliceLogic() )

  def stop(self):

    self.logic.destroy()
#
# FastGrowCutEffectTool
#

class FastGrowCutEffectTool(LabelEffect.LabelEffectTool):
  """
  One instance of this will be created per-view when the effect
  is selected.  It is responsible for implementing feedback and
  label map changes in response to user input.
  This class observes the editor parameter node to configure itself
  and queries the current view for background and label volume
  nodes to operate on.
  """

  def __init__(self, sliceWidget):
    super(FastGrowCutEffectTool,self).__init__(sliceWidget)
    # create a logic instance to do the non-gui work
    #self.logic = FastGrowCutEffectLogic(self.sliceWidget.sliceLogic())

  def cleanup(self):
    super(FastGrowCutEffectTool,self).cleanup()

  def processEvent(self, caller=None, event=None):
    """
    handle events from the render window interactor
    """

    # let the superclass deal with the event if it wants to
    if super(FastGrowCutEffectTool,self).processEvent(caller,event):
      return

    # events from the slice node
    if caller and caller.IsA('vtkMRMLSliceNode'):
      # here you can respond to pan/zoom or other changes
      # to the view
      pass

#
# FastGrowCutEffectLogic
#
class FastGrowCutEffectLogic(LabelEffect.LabelEffectLogic):
  """
  This class contains helper methods for a given effect
  type.  It can be instanced as needed by an FastGrowCutEffectTool
  or FastGrowCutEffectOptions instance in order to compute intermediate
  results (say, for user feedback) or to implement the final
  segmentation editing operation.  This class is split
  from the FastGrowCutEffectTool so that the operations can be used
  by other code without the need for a view context.
  """

  def __init__(self,sliceLogic):
    print("Preparing Growcut interaction")
    self.attributes = ('MouseTool')
    self.displayName = 'FastGrowCut Effect'

    #disconnect all shortcuts that may exist, to allow Fast GrowCut's to work, reconnect once bot is turned off
    slicer.modules.EditorWidget.removeShortcutKeys()
    self.sliceLogic = sliceLogic
    self.editUtil = EditUtil.EditUtil()

    #initialize Fast GrowCut
    self.init_fGrowCut()
    
    #~ self.currSlice = None
    #~ self.ijkPlane = 'IJ'
    #~ self.sw = slicer.app.layoutManager().sliceWidget('Red')
    #~ self.interactor = self.sw.sliceView().interactor() #initialize to red slice interactor
    
    #~ self.mouse_obs_growcut, self.swLUT_growcut = bind_view_observers(self.entranceCursorDetect)

    #self.fullInitialized=False #tracks if completed the initializtion (so can do stop correctly) of Fast GrowCut
    self.fastCrowCutCreated=False
  
  def init_fGrowCut(self):
	
	self.emergencyStopFunc = None    
	self.dialogBox=qt.QMessageBox() #will display messages to draw users attention if he does anything wrong
	self.dialogBox.setWindowTitle("Fast GrowCut Error")
	self.dialogBox.setWindowModality(qt.Qt.NonModal) #will allow user to continue interacting with Slicer
    
    # TODO: check this claim- might be causing leaks
    # set the image, label nodes (this will not change although the user can
    # alter what is bgrnd/frgrnd in editor)
    # Confused about how info propagates UIarray to UIVol, not the other way, NEEDS AUTO TESTS
	self.labelNode = self.editUtil.getLabelVolume() #labelLogic.GetVolumeNode()
	self.backgroundNode = self.editUtil.getBackgroundVolume() #backgroundLogic.GetVolumeNode()
    
    #perform safety check on right images/labels being selected, #set up images
    #if red slice doesnt have a label or image, go no further
	if type(self.backgroundNode)==type(None) or type(self.labelNode)==type(None):
		self.dialogBox.setText("Either Image (must be Background Image) or Label not set in slice views.")
		self.dialogBox.show()
       
		if self.emergencyStopFunc:
			self.emergencyStopFunc()
		return
       
	volumesLogic = slicer.modules.volumes.logic()
    
	self.labelName = self.labelNode.GetName() # record name of label so user, cant trick us
	self.imgName = self.backgroundNode.GetName()
    
	if self.sliceViewMatchEditor(self.sliceLogic)==False: # do nothing, exit function if user has played with images
		if self.emergencyStopFunc:
			self.emergencyStopFunc()
		return
         
    # fast growcut shortcuts
	resetFGC = qt.QKeySequence(qt.Qt.Key_R) # reset initialization flag
	runFGC = qt.QKeySequence(qt.Qt.Key_G) # run fast growcut
	editSeed = qt.QKeySequence(qt.Qt.Key_S) # edit seed labels

	print " keys for reset init, run GC, edit seed are R,G, S"
    
	self.qtkeyconnections = []
	self.qtkeydefsGrowcut = [[resetFGC, self.resetFastGrowCutFlag],
                             [runFGC,self.runFastGrowCut],
                             [editSeed, self.editGrowCutSeed]]

	for keydef in self.qtkeydefsGrowcut:
		s = qt.QShortcut(keydef[0], slicer.util.mainWindow()) # connect this qt event to mainWindow focus
        #s.setContext(1)
		s.connect('activated()', keydef[1])
        #s.connect('activatedAmbiguously()', keydef[1])
		self.qtkeyconnections.append(s)
    
	self.fGCLabelMod_tag = self.sliceLogic.AddObserver("ModifiedEvent", self.FastGrowCutChangeLabelInput) # put test listener on the whole window  
   
    # fast grow cut parameters
	self.bSegmenterInitialized = "no"
	self.bEditGrowCutSeed = True
	self.currentMessage = ""
    
	seedArray = slicer.util.array(self.labelName)
	self.growCutSeedArray = seedArray.copy()
	self.growCutSegArray = seedArray.copy()
	self.growCutSeedArray[:] = 0
	self.growCutSegArray[:] = 0
    
	import vtkSlicerFastGrowCutModuleLogicPython

	fastGCMod =vtkSlicerFastGrowCutModuleLogicPython.vtkFastGrowCutSeg()
	fastGCMod.SetSourceVol(self.backgroundNode.GetImageData())
	fastGCMod.SetSeedVol(self.labelNode.GetImageData())
	fastGCMod.Initialization()
	self.fastGCMod = fastGCMod
    
	self.fastCrowCutCreated=True #tracks if completed the initializtion (so can do stop correctly) of KSlice

    
  def sliceViewMatchEditor(self, sliceLogic):
    #if self.dialogBox==type(None): #something deleted teh dialogBox, this function then breaks, bail
    # if self.emergencyStopFunc:
    # self.emergencyStopFunc()
    # return False
    
    imgNode = sliceLogic.GetBackgroundLayer().GetVolumeNode()
    labelNode = sliceLogic.GetLabelLayer().GetVolumeNode()

    if type(imgNode)==type(None) or type(labelNode)==type(None) :
        self.dialogBox.setText("Either image (must be Background Image) or label not set in slice views.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

    dimImg=self.backgroundNode.GetImageData().GetDimensions()
    dimLab=self.labelNode.GetImageData().GetDimensions()
    #~ dimImg=imgNode.GetImageData().GetDimensions()
    #~ dimLab=labelNode.GetImageData().GetDimensions()

    if not (dimImg[0]==dimLab[0] and dimImg[1]==dimLab[1] and dimImg[2]==dimLab[2]): #if sizes dont match up(doing this b/c cant reach HelperBox parameters
        self.dialogBox.setText("Mismatched label to image.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

    if (self.imgName== imgNode.GetName()) and (self.labelName == labelNode.GetName()):
        return True
    else:
        self.dialogBox.setText("Set image to values used for starting the FastGrowCut bot or stop bot.")
        self.dialogBox.show()
        if self.emergencyStopFunc:
            self.emergencyStopFunc()
        return False

  def FastGrowCutChangeLabelInput(self, caller, event):
    
    if self.sliceViewMatchEditor(self.sliceLogic)==False:
       return #do nothing, exit function

  # run fast GrowCut segmenter for the current master volume and label volume
  
  def runFastGrowCut(self):
	if self.bEditGrowCutSeed == True:

		self.currentMessage = "FastGrowCut: running fast GrowCut..."
		slicer.util.showStatusMessage(self.currentMessage)
		seedArray = slicer.util.array(self.labelNode.GetName())
		self.growCutSeedArray[:]  = seedArray[:]
		
		bGCInitialized = False
		if self.bSegmenterInitialized != "no":
			bGCInitialized = True
		self.fastGCMod.SetSourceVol(self.backgroundNode.GetImageData())
		self.fastGCMod.SetSeedVol(self.labelNode.GetImageData())
		self.fastGCMod.SetInitializationFlag(bGCInitialized)
		self.fastGCMod.RunFGC()
		self.growCutSegArray[:] = seedArray[:]
		
		self.labelNode.GetImageData().Modified()
		self.labelNode.Modified()
			
		self.bSegmenterInitialized = "yes"
		self.bEditGrowCutSeed = False
		
		self.currentMessage = "Fast GrowCut done: press 'S' to refine seed image, or 'R' to reset fast GrowCut parameters"
		slicer.util.showStatusMessage(self.currentMessage)
	else:
		self.currentMessage = "Fast GrowCut: go to seed labels first by pressing 'S'"
		slicer.util.showStatusMessage(self.currentMessage)
  
  # reset fast growcut segmenter
  def resetFastGrowCutFlag(self):
        self.bSegmenterInitialized = "no"
        self.bEditGrowCutSeed = True
        self.growCutSeedArray[:] = 0
        self.growCutSegArray[:] = 0
        
        seedArray = slicer.util.array(self.labelNode.GetName())
        seedArray[:] = 0
        
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
        print('reset Fast GrowCut parameters')
        self.currentMessage = "Fast GrowCut: parameters have been reset. Go to PaintEffect to draw foreground and background seeds and press 'G' to run fast GrowCut"
        slicer.util.showStatusMessage(self.currentMessage)
        
        
  def editGrowCutSeed(self):
	
    seedArray = slicer.util.array(self.labelNode.GetName())
    if self.bEditGrowCutSeed == False:
        self.growCutSegArray[:] = seedArray[:]
        seedArray[:] = self.growCutSeedArray[:]
        self.bEditGrowCutSeed = True
        self.labelNode.GetImageData().Modified()
        self.labelNode.Modified()
		
        print('show seed image')
        self.currentMessage = "Fast GrowCut: seed image is shown. Go to PaintEffect to refine foreground and background seeds if necessary, and press 'G' to run fast GrowCut"
        slicer.util.showStatusMessage(self.currentMessage)
    else:
        if self.growCutSegArray.any() != 0 :
		
			seedArray[:] = self.growCutSegArray[:]
			self.bEditGrowCutSeed = False
			self.labelNode.GetImageData().Modified()
			self.labelNode.Modified()
			
			print('show segmentation')
			self.currentMessage = "Fast GrowCut: segmentation result is shown. If not satisfied, press 'S' to edit seeds and run fast GrowCut again"
			slicer.util.showStatusMessage(self.currentMessage)
        else:
			print('no segmentation result')	
			self.currentMessage = "Fast GrowCut: no segmentation result available"
			slicer.util.showStatusMessage(self.currentMessage)
			
  def destroy(self):

    #destroy GrowCut key shortcuts
    for i in range(len(self.qtkeydefsGrowcut)):  #this will be an empty list if the KSlice part has been reached (all growcut functionality disabled)
        keyfun = self.qtkeydefsGrowcut[i]
        keydef = self.qtkeyconnections[i]
        test1=keydef.disconnect('activated()', keyfun[1])
        test2=keydef.disconnect('activatedAmbiguously()', keyfun[1])
        #self.qtkeyconnections.remove(keydef) #remove from list
        keydef.setParent(None)
        #why is this necessary for full disconnect (if removed, get the error that more and more keypresses are required if module is repetedly erased and created
        keydef.delete() #this causes errors   
    
    # destroy GrowCut objects
    self.growCutSeedArray = None
    self.growCutSegArray = None
    self.fastGCMod = None
    self.currentMessage = ""
    self.imgName = None
    self.labelName = None
    self.labelNode = None
    self.backgroundNode = None
    
    # remove GrowCut observer
    self.sliceLogic.RemoveObserver(self.fGCLabelMod_tag)
    print("Fast GrowCut deletion completed")
    	    
    #if self.fastCrowCutCreated==False: #if initialized, remove, otherwise do nothing
    #    return
    #put back the editor shortcuts we removed
    slicer.modules.EditorWidget.installShortcutKeys()

    print("Deletion completed")
#
# The FastGrowCutEffect class definition
#

class FastGrowCutEffectExtension(LabelEffect.LabelEffect):
  """Organizes the Options, Tool, and Logic classes into a single instance
  that can be managed by the EditBox
  """

  def __init__(self):
    # name is used to define the name of the icon image resource (e.g. FastGrowCutEffect.png)
    self.name = "FastGrowCutEffect"
    # tool tip is displayed on mouse hover
    self.toolTip = "Paint: circular paint brush for label map editing"

    self.options = FastGrowCutEffectOptions
    self.tool = FastGrowCutEffectTool
    self.logic = FastGrowCutEffectLogic

""" Test:

sw = slicer.app.layoutManager().sliceWidget('Red')
import EditorLib
pet = EditorLib.FastGrowCutEffectTool(sw)

"""

#
# FastGrowCutEffect
#

class FastGrowCutEffect:
  """
  This class is the 'hook' for slicer to detect and recognize the extension
  as a loadable scripted module
  """
  def __init__(self, parent):
    parent.dependencies = ["Editor"]
    parent.title = "Editor FastGrowCut Effect"
    parent.categories = ["Developer Tools.Editor Extensions"]
    parent.contributors = ["Liangjia Zhu, Ivan Kolesov, Allen Tannenbaum (Stony Brook University), Yi Gao(University of Alabama Birmingham), and Ron Kikinis (BWH)"] # insert your name in the list
    parent.helpText = """Interactive segmentation editor extension."""
    parent.acknowledgementText = """ This editor extension was developed by Liangjia Zhu, Ivan Kolesov, Allen Tannenbaum (Stony Brook University), Yi Gao(University of Alabama Birmingham), and Ron Kikinis (BWH) """


    # TODO:
    # don't show this module - it only appears in the Editor module
    #parent.hidden = True

    # Add this extension to the editor's list for discovery when the module
    # is created.  Since this module may be discovered before the Editor itself,
    # create the list if it doesn't already exist.
    try:
      slicer.modules.editorExtensions
    except AttributeError:
      slicer.modules.editorExtensions = {}
    slicer.modules.editorExtensions['FastGrowCutEffect'] = FastGrowCutEffectExtension

#
# FastGrowCutEffectWidget
#

class FastGrowCutEffectWidget:
  def __init__(self, parent = None):
    self.parent = parent

  def setup(self):
    # don't display anything for this widget - it will be hidden anyway
    pass

  def enter(self):
    pass

  def exit(self):
    pass


