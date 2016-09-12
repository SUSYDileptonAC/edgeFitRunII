import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations


class edgeConfig:
		
		
		flag = "CMSDASNtuples"
		task = "cutsV31DileptonFinalTrees"
		dataset = "Data"
		figPath = "fig/"
		shelvePath = "shelves/"
				
		residualMode = "pull"
		plotErrorBands = False	
		
		edgePosition = 70
		fixEdge = False
		
		title = "None"
		histoytitle = "None"
		
		useMC = True
		useToys = False
		mcdatasets = ["TT_Powheg","ZJets"]
		signalDataSets = []
		addDataset = None
		isSignal = False
		runMinos = True
		plotAsymErrs = True		
		isPreliminary = True
		allowNegSignal = True
		randomStartPoint = True
		ownWork = False
		year = 2015
		showText = True
		plotYMax = 120
		
		dataVersion = "sw74X"
		
		maxInv = 300
		minInv = 20
		plotMaxInv = 300
		plotMinInv = 20
		nBinsMinv = 96
		
		### toy-related configuration
		toyConfig = {"nToys":1000,"nSig":125,"m0":70,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular","plotToys":False}

		
		def __init__(self,region="SignalInclusive",backgroundShape="CB",signalShape="T",runName = "Run2015_25ns",dataSet="Combined",useMC=False,toys=0,addSignal=""):
			sys.path.append(pathes.basePath)
			
			self.dataSetPath = locations.dataSetPath
			
			self.useMC = useMC
			
			from defs import runRanges
			if not runName in dir(runRanges):
				print "invalid run name, exiting"
				sys.exit()
			else:	
				self.runRange =  getattr(runRanges,runName)
			
			from defs import Regions
			if not region in dir(Regions):
				print "invalid region, exiting"
				sys.exit()
			else:	
				self.selection = getattr(Regions,region)
		
			from centralConfig import zPredictions
			from corrections import  rSFOF, rEEOF, rMMOF	
			self.rSFOF = rSFOF
			self.rEEOF = rEEOF
			self.rMMOF = rMMOF
			self.zPredictions = zPredictions
			
			self.backgroundShape = backgroundShape
			self.signalShape = signalShape
			
			
			self.title = self.selection.name+"_"+dataSet+"_"+self.runRange.label+"_"+self.backgroundShape+self.signalShape
			self.histoytitle = 'Events / %.1f GeV' % ((self.maxInv - self.minInv) / self.nBinsMinv)	
			
			self.toyConfig["nToys"] = int(toys)
			
			if toys > 0:
				self.useMC = True
				self.useToys = True
				
			if addSignal is not "":
				self.signalDataSets.append(addSignal)
				self.isSignal = True
				self.addDataset = addSignal
