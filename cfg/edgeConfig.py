import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations


class edgeConfig:
		
		
		flag = "sw538v0477"
		task = "cutsV23DileptonFinalTrees"
		dataset = "Data"
		figPath = "fig/"
		shelvePath = "shelves/"
				
		residualMode = "pull"
		plotErrorBands = False	
		year = 2012	
		
		edgePosition = 70
		fixEdge = True
		
		#~ edgePosition = 82.392
		#~ fixEdge = True
		
		title = "None"
		histoytitle = "None"
		
		useMC = True
		mcdatasets = ["TTJets", "ZJets"]
		addDataset = None
		isSignal = False
		runMinos = False
		isPreliminary = True
		allowNegSignal = True
		ownWork = False
		year = 2012
		showText = True
		plotYMax = 220
		### toy-related configuration
		toyConfig = {"nToys":1000,"nSig":0,"m0":70,"scale":1,"systShift":"None"}

		dataVersion = "sw53X"
		dataSetPath = "/home/jan/Trees/sw538v0478/"
		
		maxInv = 300
		minInv = 20
		plotMaxInv = 300
		plotMinInv = 20
		nBinsMinv = 56
		
		def __init__(self,region="SignalInclusive",backgroundShape="ETH",signalShape="T",runName = "Full2012",dataSet="Combined",useMC=False,toys=0):
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
