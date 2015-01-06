import sys
from frameworkStructure import pathes


class edgeConfig:
		
		
		flag = "sw538v0478"
		task = "cutsV23DileptonFinalTrees"
		dataset = "Data"
		figPath = "fig/"
		shelvePath = "shelves/"
				
		residualMode = "pull"
		plotErrorBands = False	
		year = 2012	
		
		edgePosition = 70
		fixeEdge = False
		
		useMC = False
		mcDatasets = ["TTJets", "ZJets"]
		addDataset = None
		isSignal = False
		### toy-related configuration
		toyConfig = {"nToys":0,"nSig":100,"m0":125,"scale":1,"systShift":"None"}

		dataVersion = "sw53X"
		dataSetPath = "/home/jan/Trees/sw538v0478/"
		
		maxInv = 300
		minInv = 20
		nBinsMinv = 56
		
		def __init__(self,region="SignalInclusive",backgroundShape="ETH",signalShape="T",runName = "Full2012"):
			sys.path.append(pathes.basePath)
			
			self.dataSetPath = pathes.dataSetPath
			
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
		
			from corrections import zPredictions, rSFOF	
			self.rSFOF = rSFOF
			self.zPredictions = zPredictions
			
			self.backgroundShape = backgroundShape
			self.signalShape = signalShape
			
			
