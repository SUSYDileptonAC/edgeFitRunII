import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations

### main config file for the fit
### some options are updated by command line arguments

class edgeConfig:
		
		### basic flags and paths
		flag = "CMSDASNtuples"
		task = "cutsV31DileptonFinalTrees"
		dataset = "Data"
		figPath = "fig/"
		shelvePath = "shelves/"
		
		### mode for the ratio plot		
		residualMode = "pull"
		plotErrorBands = False	
		
		### starting edge position and option to fix it or use a random one
		### a fixed edge should not be combined with a random starting point
		edgePosition = 70
		fixEdge = False
		randomStartPoint = True
		
		title = "None"
		histoytitle = "None"
		
		### Options to use MC or toys (overwritten by command line)
		useMC = True
		useToys = False
		### MC datasets to be used
		mcdatasets = ["TT_Powheg","ZJets"]
		### array for the signal samples that can be added via -a <sample name>
		signalDataSets = []
		### additional dataset, will be changed to the signal dataset
		addDataset = None
		isSignal = False
		
		### Minos produces asymmetric uncertainties but takes more time
		### If runMinos is false, plotAsymErrs has to be false as well
		runMinos = True
		plotAsymErrs = True	
		
		### Labels
		ownWork = False	
		isPreliminary = True
		
		### allow negative signal or restrict it to positive values
		allowNegSignal = True
		
		### stuff for labels
		year = 2015
		showText = True
		
		### y-range
		plotYMax = 120
		
		dataVersion = "sw74X"
		
		### binning
		maxInv = 300
		minInv = 20
		plotMaxInv = 300
		plotMinInv = 20
		nBinsMinv = 70
		
		### toy-related configuration
		### nToys = number of toys, can be set with option -t
		### nSig and m0: Number of signal events injected and edge position of the injected signal
		### scale: option to scale the toys up or down, eg. to make tests for more/less lumi
		### systShift: Option to shift R_SFOF Up/Down by 1 sigma for systematic studies
		### sShape: signal shape, Triangular, Convex or Concave
		### plotToys: Option to make plots for all the toy datasets
		toyConfig = {"nToys":1000,"nSig":125,"m0":70,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular","plotToys":False}

		### initialize the config with the command line arguments
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
