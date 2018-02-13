import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations


class edgeConfig:
		
		
		flag = "sw8026v1001"
		#~ flag = "sw8026v1003"
		task = "cutsV34DileptonFinalTrees"
		dataset = "Data"
		figPath = "fig/"
		shelvePath = "shelves/"
				
		residualMode = "pull"
		plotErrorBands = False	
		
		edgePosition = 160
		fixEdge = False	
				
		title = "None"
		histoytitle = "None"
		
		useMC = True
		useToys = False
		### Use MadGraph TT sample. Pythia sample is too large -> takes longer 
		### and due to relatively small fluctuations the pull looked worse
		### (have not checked this for a while)
		#~ mcdatasets = ["TTJets_Madgraph","ZJets",'SingleTop','Diboson',"Rare"]
		mcdatasets = ["TTJets_Madgraph","ZJets"]
		signalDataSets = ["slepton_600_175"]
		signalDataSets = []
		addDataset = None
		isSignal = False
		
		### Minos produces asymmetric (and more correct) uncertainties but
		### takes much longer -> Use for main fit but not for toys
		### Can still decide to plot symmetric errors if desired
		runMinos = False
		plotAsymErrs = False
			
		isPreliminary = True
		
		### Can restrict fit to positive signal (which is what we expect)
		### Note that this introduces a bias to positive signal contributions
		allowNegSignal = True
		ownWork = False
		year = 2016
		showText = True
		logPlot = False
		
		### Set maximum of y-axis by hand to have the same in SF and OF
		### Might consider a way to use the SF plot to set it for both
		plotYMax = 400
		
		### toy-related configuration
		toyConfig = {"nToys":1000,"nSig":70,"m0":300,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular"}

		dataVersion = "sw80X"
		dataSetPath = "/disk/user/schomakers/trees/sw8026v1001"
		
		### Usually we fit up to 500 GeV (maxInv) but plot only up to 300 (plotMaxInv)
		### due to insignificant statistics, nBinsMinv is usually (maxInv-minInv)/5
		### Might be good to check once if there is anything above 300
		#~ maxInv = 700
		maxInv = 500
		#~ maxInv = 300
		minInv = 20
		plotMaxInv = 300
		plotMinInv = 20
		#~ nBinsMinv = 136
		nBinsMinv = 96
		#~ nBinsMinv = 56
		
		def __init__(self,region="SignalInclusive",backgroundShape="ETH",signalShape="T",runName = "Full2012",useMC=False,toys=0,addSignal=""):
			sys.path.append(pathes.basePath)
			
			### Use smaller data sets produced for the likelihood for
			### fit in signal region to increase the speed
			### Due to MET cut this is not possible for DY fit ->
			### normal trees
			self.dataSetPath = locations.dataSetPathNLL
			#~ self.dataSetPath = locations.dataSetPath
			
			self.useMC = useMC
			
			from defs import runRanges
			if not runName in dir(runRanges):
				print "invalid run name, exiting"
				sys.exit()
			else:	
				self.runRange =  getattr(runRanges,runName)
				print runName
			
			from defs import Regions
			if not region in dir(Regions):
				print "invalid region, exiting"
				sys.exit()
			else:	
				self.selection = getattr(Regions,region)
				self.selection.cut = self.selection.cut + getattr(runRanges,runName).runCut
		
			from centralConfig import zPredictions
			from corrections import  rSFOF, rEEOF, rMMOF	
			self.rSFOF = rSFOF
			self.rEEOF = rEEOF
			self.rMMOF = rMMOF
			self.zPredictions = zPredictions
			
			self.backgroundShape = backgroundShape
			self.signalShape = signalShape
			
			
			self.title = self.selection.name+"_"+self.runRange.label+"_"+self.backgroundShape+self.signalShape
			self.histoytitle = 'Events / %.1f GeV' % ((self.maxInv - self.minInv) / self.nBinsMinv)	
			
			self.toyConfig["nToys"] = int(toys)
			
			if toys > 0:
				self.useMC = True
				self.useToys = True
				
			if addSignal is not "":
				self.signalDataSets.append(addSignal)
				self.isSignal = True
				self.addDataset = addSignal
