#!/usr/bin/env python

#=======================================================
# Project: LocalAnalysis
#			  SUSY Same Sign Dilepton Analysis
#
# File: dataInterface.py
#
# Author: Daniel Sprenger
#		 daniel.sprenger@cern.ch
#=======================================================


from messageLogger import messageLogger as log

import ROOT
from ROOT import TFile, TH1F

import os, ConfigParser
from math import sqrt
import datetime


class InfoHolder(object):
	class DataTypes(object):
		Unknown = -1
		Data = 1
		DataFake = 2
		MC = 10
		MCSignal = 11
		MCBackground = 12
		MCFake = 13
		EMuBackground = 20

	theHistograms = {
		#'electron pt': "Electrons/electron pt",
		#'electron eta': "Electrons/electron eta",
		#'electron isolation': "Electrons/electron iso",

		#'electron charge methods': "Electrons/electron charge methods agreeing",
		#'electron charge method disagree': "Electrons/electron charge method deviating",

		#'muon pt': "Muons/muon pt",
		#'muon eta': "Muons/muon eta",
		#'muon isolation': "Muons/muon iso",

		#'jet pt': "Jets/jet pt",
		#'jet eta': "Jets/jet eta",
		#'jet pt 1st jet': "Jets/pt first jet",
		#'jet pt 2nd jet': "Jets/pt second jet",

		'chargeProduct': "",
		'ht': "MET/HT",
		'met': "MET/MET",
		'MHT': "MET/MHT",

		'MET vs HT': "MET/MET - HT",
		'MET vs MHT': "MET/MET - MHT",

		#'light lepton multiplicity': "Multiplicity/LightLeptonMultiplicity",
		#'lepton multiplicity (with taus)': "Multiplicity/LeptonMultiplicity",
		#'muon multiplicity': "Multiplicity/MuonMultiplicity",
		#'electron multiplicity': "Multiplicity/ElectronMultiplicity",
		'nJets': "Multiplicity/JetMultiplicity",
		'nBJets': "",

		'nVertices': "nVErtices",

		#'SS electron invariant mass': "Invariant Mass/Invariant mass of SS electron pairs",
		#'OS electron invariant mass': "Invariant Mass/Invariant mass of OS electron pairs",
		#'SS muon invariant mass': "Invariant Mass/Invariant mass of SS muon pairs",
		#'OS muon invariant mass': "Invariant Mass/Invariant mass of OS muon pairs",

		#'OS emu invariant mass': "Invariant Mass/Invariant mass of OFOS lepton pairs",

		#'Trigger': "Trigger paths",

		# for trees
		'p4.M()': "p4.M()",
		'lumiSec': "lumiSec",
}

	theStandardColors = {
		'LM0': "Red",
		#'LM1': "Red",
		'LM1': "DarkGreen",
		'LM2': "Red",
		#'LM3': "Red",
		'LM3': "DarkGreen",
		'LM4': "Red",
		'LM5': "Red",
		#'LM6': "Red",
		'LM6': "DarkGreen",
		'LM7': "Red",
		'LM8': "Red",
		'LM9': "Red",
		'LM13': "DarkRed",
		'T3lh': "DarkGreen",
		'QCD': "Magenta",
		'QCD100': "Magenta",
		'QCD250': "Magenta",
		'QCD500': "Magenta",
		'QCD1000': "Magenta",
		#'WJets': "Orange",
		'WJets': "W11WJets",
		#'ZJets': "MyBlue",
		'ZJets': "W11ZLightJets",
		'AStar': "DarkOrange",
		#'Diboson': "DarkOrange",
		'Diboson': "W11Diboson",
		'DibosonMadgraph': "W11Diboson",
		#'TTJets': "MyGreen",
		'TTJets': "W11ttbar",
		'SingleTop': "W11singlet",
		'JetMETTau': "Black",
		'EG': "Black",
		'ElectronHad': "Black",
		'DoubleEle': "Black",
		'Mu': "Black",
		'MuHad': "Black",
		'DoubleMu': "Black",
		'Data': "Black",
		'DataMET': "Black",
		'DataSS': "Black",
		'DataFake': "Black",
		'DataFakeUpper': "Black",
		'DataFakeLower': "Black",
		'MCFake': "Brown",
	}

	theDataSamples = {
			'sw53X': {
				'Data': ["MergedData"],				
				'BlockA': ["MergedData_BlockA"],
				'DataMET': ["MergedData_METPD"],
				'DataSingleLepton': ["MergedData_SingleLepton"],
				'Data2011': ["MergedData_2011"],

				#~ 'DataSS': [],
				#~ 'DataFake': [],
				#~ 'DataFakeUpper': [],
				#~ 'DataFakeLower': [],
				#~ 'HT' : ["HT_1203a_Run2012A", "HT_1203a_Run2012B"],

				#~ 'DoubleElectron': ["DoubleElectron_1203a_Run2012A", "DoubleElectron_1203a_Run2012B"],
				#~ 'DoubleMu': ["DoubleMu_1203a_Run2012A", "DoubleMu_1203a_Run2012B"],
				#~ 'MuEG': ["MuEG_1203a_Run2012A", "MuEG_1203a_Run2012B"],

	
				'TTJets': ["TTJets_madgraph_Summer12"],
				'TTJetsPowheg': ["TT_Powheg_Summer12_v1"],
				'TTJetsSC': ["TTJets_MGDecays_madgraph_Summer12"],
				'SingleTop': ["TBar_sChannel_Powheg_Summer12","TBar_tChannel_Powheg_Summer12","TBar_tWChannel_Powheg_Summer12","TBar_sChannel_Powheg_Summer12","TBar_tChannel_Powheg_Summer12","TBar_tWChannel_Powheg_Summer12"],
				'ZJets' : ["ZJets_madgraph_Summer12", "AStar_madgraph_Summer12"],
				'ZJetsOnly' : ["ZJets_madgraph_Summer12"],
				'AStar': ["AStar_madgraph_Summer12"],
				"Rare" : ["TTGJets_madgraph_Summer12","TTWJets_madgraph_Summer12","TTWWJets_madgraph_Summer12","TTZJets_madgraph_Summer12","WWGJets_madgraph_Summer12","WWWJets_madgraph_Summer12","WWZNoGstarJets_madgraph_Summer12","WZZNoGstar_madgraph_Summer12"],
				'DibosonMadgraph' : ["WWJetsTo2L2Nu_madgraph_Summer12", "WZJetsTo3LNu_madgraph_Summer12", "ZZJetsTo2L2Nu_madgraph_Summer12", "ZZJetsTo2L2Q_madgraph_Summer12", "ZZJetsTo4L_madgraph_Summer12"],
				# "WZJetsTo2L2Q_madgraph_Summer12", 
				'DibosonMadgraphWW' : ["WWJetsTo2L2Nu_madgraph_Summer12"],
				'DibosonMadgraphWZ' : ["WZJetsTo3LNu_madgraph_Summer12", "WZJetsTo2L2Q_madgraph_Summer12"],
				'DibosonMadgraphZZ' : ["ZZJetsTo2L2Nu_madgraph_Summer12", "ZZJetsTo2L2Q_madgraph_Summer12", "ZZJetsTo4L_madgraph_Summer12"],
				'edge_400_150_80': ["SUSY_Simplified_Model_Madgraph_FastSim_T6bblledge_400_150_80_8TeV"],
				'slepton_550_275_100': ["SUSY_Simplified_Model_Madgraph_FastSim_T6bbslepton_550_275_100_8TeV"],
				'slepton_450_275_100': ["SUSY_Simplified_Model_Madgraph_FastSim_T6bbslepton_450_275_100_8TeV"],
				'slepton_550_175_100': ["SUSY_Simplified_Model_Madgraph_FastSim_T6bbslepton_550_175_100_8TeV"],
				},
}

	theSampleDescriptions = {
		'ZJets': "Z+jets",
		'TTJets': "t#bar{t}+jets",
		'SingleTop': "t / #bar{t}+jets",
		'DibosonMadgraph': "WW, WZ, ZZ",
		'DataFake': "Fake leptons",
		'Rare': "Rare SM",
	}

	theMasterFile = {
		'sw53X':"/home/jan/Doktorarbeit/Dilepton/projects/SubmitScripts/Input/Master53X.ini",
	}

	theXSectionUncertainty = {
		'ZJets': 0.0433,
		'TTJets': 0.1511,
		'SingleTop': 0.0604, # maximum relative uncertainty of all t processes
		'DibosonMadgraph': 0.0385, # uncertainty of WZ process
		'Rare': 0.5, # Conservative  uncertainty on ttV, VVV, etc...
							  }


class DataInterface(object):
	def __init__(self,dataSetPath,dataVersion):
		
		self.dataVersion = dataVersion
		self.dataSetPath = dataSetPath
		self.cfg = ConfigParser.ConfigParser()
			
		log.logDebug("Loading MasterFile: %s" % InfoHolder.theMasterFile[dataVersion])
		self.cfg.read(InfoHolder.theMasterFile[dataVersion])

	# static methods
	#==========
	def getTasksFromRootfile(filePath):
		file = TFile(filePath, 'READ')
		keys = file.GetListOfKeys()
		keyNames = [key.GetName() for key in keys]
		#log.logDebug("%s" % keyNames)
		file.Close()

		return keyNames

	getTasksFromRootfile = staticmethod(getTasksFromRootfile)


	def convertDileptonTree(tree, nMax= -1, weight=1.0, selection="", weightString=""):
		# TODO: make selection more efficient
		log.logDebug("Converting DileptonTree")
		ROOT.gROOT.ProcessLine(\
							   "struct MyDileptonTreeFormat{\
								 Double_t inv;\
								 Int_t chargeProduct;\
								 Int_t nJets;\
								 Double_t ht;\
								 Double_t met;\
								 Double_t pt1;\
								 Double_t pt2;\
								 Double_t weight;\
								};")
		from ROOT import MyDileptonTreeFormat
		data = MyDileptonTreeFormat()
		newTree = ROOT.TTree("treeInvM", "Dilepton Tree")
		newTree.SetDirectory(0)
		newTree.Branch("inv", ROOT.AddressOf(data, "inv"), "inv/D")
		newTree.Branch("chargeProduct", ROOT.AddressOf(data, "chargeProduct"), "chargeProduct/I")
		newTree.Branch("nJets", ROOT.AddressOf(data, "nJets"), "nJets/I")
		newTree.Branch("ht", ROOT.AddressOf(data, "ht"), "ht/D")
		newTree.Branch("met", ROOT.AddressOf(data, "met"), "met/D")
		newTree.Branch("pt1", ROOT.AddressOf(data, "pt1"), "pt1/D")
		newTree.Branch("pt2", ROOT.AddressOf(data, "pt2"), "pt2/D")
		newTree.Branch("weight", ROOT.AddressOf(data, "weight"), "weight/D")

		# only part of tree?
		iMax = tree.GetEntries()
		if (nMax != -1):
			iMax = min(nMax, iMax)

		# Fill tree
		for i in xrange(iMax):
			if (tree.GetEntry(i) > 0):
				data.inv = tree.p4.M()
				data.chargeProduct = tree.chargeProduct
				data.nJets = tree.nJets
				data.ht = tree.ht
				data.met = tree.met
				data.pt1 = tree.pt1
				data.pt2 = tree.pt2
				if (weightString != ""):
					eventWeight = eval(weightString)
					data.weight = tree.weight * eventWeight
				else:
					data.weight = tree.weight * weight
				#log.logDebug("cp: %d" % tree.chargeProduct)
				#log.logDebug("invM = %f" % tree.p4.M())
				newTree.Fill()

		#return newTree
		return newTree.CopyTree(selection)

	convertDileptonTree = staticmethod(convertDileptonTree)

	def convertTree(tree, nMax= -1):
		ROOT.gROOT.ProcessLine(\
							   "struct MyDataFormat{\
								 Double_t invM;\
								 Int_t chargeProduct;\
								};")
		from ROOT import MyDataFormat
		data = MyDataFormat()
		newTree = ROOT.TTree("treeInvM", "Invariant Mass Tree")
		newTree.Branch("invM", ROOT.AddressOf(data, "invM"), "invM/D")
		newTree.Branch("chargeProduct", ROOT.AddressOf(data, "chargeProduct"), "chargeProduct/I")

		# only part of tree?
		iMax = tree.GetEntries()
		if (nMax != -1):
			iMax = min(nMax, iMax)

		# Fill tree
		for i in xrange(iMax):
			if (tree.GetEntry(i) > 0):
				data.invM = tree.p4.M()
				data.chargeProduct = tree.chargeProduct
				#log.logDebug("cp: %d" % tree.chargeProduct)
				#log.logDebug("invM = %f" % tree.p4.M())
				newTree.Fill()

		newTree.SetDirectory(0)
		return newTree

	convertTree = staticmethod(convertTree)

	# other methods
	#==========
	def getKFactor(self, dataset, dataSamples=None):
		if (dataSamples == None):
			dataSamples = self.theConfigDict['DataSamples']

		if (not InfoHolder.theDataSamples.has_key(dataSamples)):
			log.logError("Datasample not registered: %s" % dataSamples)
			return None
		if (not InfoHolder.theDataSamples[dataSamples].has_key(dataset)):
			log.logError("Dataset not found in datasample '%s': %s" % (dataSamples, dataset))
			return None

		jobList = (InfoHolder.theDataSamples[dataSamples])[dataset]
		xSection = self.getXSection(dataset)
		kFactor = 0.0
		for job in jobList:
			kFactor += float(self.cfg.get(job, 'kfactor')) * float(self.cfg.get(job, 'crosssection')) / xSection

		return kFactor

	def getXSection(self, dataset, dataSamples=None):
		if (dataSamples == None):
			dataSamples = self.theConfigDict['DataSamples']

		if (not InfoHolder.theDataSamples.has_key(dataSamples)):
			log.logError("Datasample not registered: %s" % dataSamples)
			return None
		if (not InfoHolder.theDataSamples[dataSamples].has_key(dataset)):
			log.logError("Dataset not found in datasample '%s': %s" % (dataSamples, dataset))
			return None

		jobList = (InfoHolder.theDataSamples[dataSamples])[dataset]
		xSection = 0.0
		for job in jobList:
			xSection += float(self.cfg.get(job, 'crosssection'))

		return xSection

	def getResultHistogram(self, flag, task, dataset, histoName, dataSamples=None, scale=True, trees=[], drawString="", cut="", weight=None, triggerEffCorrection=False):
		if (dataSamples == None):
			dataSamples = self.theConfigDict['DataSamples']

		#if (selection == None):
		#	selection = self.theConfigDict['StandardSelection']

		if (not InfoHolder.theDataSamples.has_key(dataSamples)):
			log.logError("Datasample not registered: %s" % dataSamples)
			return None
		if (not InfoHolder.theDataSamples[dataSamples].has_key(dataset)):
			log.logError("Dataset not found in datasample '%s': %s" % (dataSamples, dataset))
			return None

		jobList = (InfoHolder.theDataSamples[dataSamples])[dataset]
		log.logDebug("Getting '%s' from joblist %s" % (histoName, str(jobList)))

		taskDir = task.split(".", 1)[0]
		taskInFile = task.split(".", 1)[1]
		result = self.__combineDatasets(jobList, flag, taskDir, histoName, taskInFile, scale, dataSamples=dataSamples, trees=trees, drawString=drawString, cut=cut, weight=weight, triggerEffCorrection=triggerEffCorrection)
		if ((not result.scaled) and (result.dataType == InfoHolder.DataTypes.MC or result.dataType == InfoHolder.DataTypes.MCBackground or result.dataType == InfoHolder.DataTypes.MCSignal)):
			log.logWarning("Not scaling MC histogram %s (%s)" % (histoName, dataset))

		result.dataName = dataset
		return result


	def __combineDatasets(self, jobs, flag, task, histoName, taskInFile, scale, dataSamples=None, trees=[], drawString="", cut="", weight=None, triggerEffCorrection=False):
		result = None

		if (jobs == []):
			log.logError("JobList empty")
			return Result(None)

		for job in jobs:
			tempResult = None

			log.logDebug("Trying to get event count for dynamic scaling")
			eventCount = self.getEventCount(job, flag, task, dataSamples=dataSamples)
			if (trees != []):
				if (eventCount > 0.0):
					log.logDebug("Dynamic scaling active (%f)" % eventCount)
					tempResult = self.__getHistogramFromDatasetUsingTrees(job, flag, task, trees, taskInFile, drawString=drawString, cut=cut, scaleMC=scale, dataSamples=dataSamples,
																		  dynamicCount=eventCount, weight=weight, triggerEffCorrection=triggerEffCorrection)
				else:
					log.logInfo("Dynamic scaling not possible (%f)" % eventCount)
					tempResult = self.__getHistogramFromDatasetUsingTrees(job, flag, task, trees, taskInFile, drawString=drawString, cut=cut, scaleMC=scale, dataSamples=dataSamples,
																		  weight=weight, triggerEffCorrection=triggerEffCorrection)
			else:
				if (eventCount > 0.0):
					log.logDebug("Dynamic scaling active (%f)" % eventCount)
					tempResult = self.__getHistogramFromDataset(job, flag, task, histoName, taskInFile, scale, dataSamples=dataSamples, dynamicCount=eventCount)
				else:
					log.logInfo("Dynamic scaling not possible (%f)" % eventCount)
					tempResult = self.__getHistogramFromDataset(job, flag, task, histoName, taskInFile, scale, dataSamples=dataSamples)

			if (tempResult != None):
				log.logDebug("Got histogram: %s" % str(tempResult.histogram))

			if (result == None):
				# first existing histogram
				result = tempResult
			else:
				# not first one, add this
				result = result.addResult(tempResult)
				log.logDebug("Result histogram: %s" % str(result.histogram))

		if (result == None or result.histogram == None):
			log.logError("Could not load histogram from any of jobs %s" % str(jobs))

		#hQCD = weightDataset(path, flag, runName, jobs[0][0], histoName, luminosity, analysis, noScale, n=jobs[0][1])
		return result


	def __getHistogramFromDataset(self, job, flag, task, histoName, taskInFile, scaleMC, dataSamples=None, dynamicCount= -1.0):
		filePath = "%s/%s/%s/%s.%s.%s.root" % (self.theConfigDict['HistosPath'], flag, task, flag, task, job)
		histoPath = "%s/%s/%s;1" % (taskInFile, self.theConfigDict['InternalHistosPath'], histoName)
		#log.logDebug("file: %s" % filePath)
		#log.logDebug("histo: %s" % histoPath)

		histogram = None
		if (os.path.exists(filePath)):
			histogram = self.getHistogramFromFile(filePath, histoPath)
		else:
			log.logWarning("File not found %s" % filePath)
			return Result(None)

		result = Result(histogram)
		#result.dataName = job
		result.taskName = taskInFile
		result.flagName = flag

		cfg = self.cfg
		if (dataSamples != None):
			log.logDebug("Overriding masterfile with %s" % InfoHolder.theMasterFile[dataSamples])
			cfg = ConfigParser.ConfigParser()
			cfg.read(InfoHolder.theMasterFile[dataSamples])


		if cfg.has_section(job):
			result.kFactor = cfg.getfloat(job, 'kfactor')
			result.nEvents = cfg.getfloat(job, 'numevents')
			if (result.nEvents != cfg.getint(job, 'localevents') and dynamicCount < -0.0):
				log.logWarning("nEvents incompatible with nLocalEvents and dynamic count disabled!")

			groups = cfg.get(job, 'groups')
			if ("Data" in groups):
				log.logDebug("Data sample found")
				result.luminosity = abs(cfg.getfloat(job, 'crosssection'))
				result.dataType = InfoHolder.DataTypes.Data

			elif ("Fake" in groups):
				log.logDebug("DataFake sample found")
				result.luminosity = abs(cfg.getfloat(job, 'crosssection'))
				result.dataType = InfoHolder.DataTypes.DataFake

			elif ("MC" in groups):
				log.logDebug("MC sample found")
				result.setXSection(cfg.getfloat(job, 'crosssection'))
				if (dynamicCount > 0.0):
					log.logDebug("Applying dynamic scaling to MC sample: %f (%f)" % (dynamicCount, result.nEvents))
					result.nEvents = dynamicCount

				result.dataType = InfoHolder.DataTypes.MCBackground
				if ("SUSY" in groups):
					log.logDebug("Sample is SUSY signal sample")
					result.dataType = InfoHolder.DataTypes.MCSignal

				luminosity = self.theConfigDict['Luminosity']
				if (scaleMC):
					result.unscaledIntegral = result.integral()

					scalingFactor = 1
					if self.theConfigDict['NLO']:
						scalingFactor = result.xSection / result.nEvents * luminosity * result.kFactor
					else:
						scalingFactor = result.xSection / result.nEvents * luminosity

					log.logDebug("Scaling factor: %f" % scalingFactor)
					result.scale(scalingFactor)
					result.luminosity = luminosity
			else:
				log.logError("Unknown sample found")
				result.dataType = InfoHolder.DataTypes.Unknown
		else:
			log.logError("No section in master list found for job %s" % job)
			return result

		log.logDebug("Number of entries in %s: %f \\pm %f (%d)" % (job, result.integral(), result.integralError(), result.unscaledIntegral))
		return result


	def __getHistogramFromDatasetUsingTrees(self, job, flag, task, trees, taskInFile, drawString="", cut="", scaleMC=True, dataSamples=None, dynamicCount= -1.0, weight=None, triggerEffCorrection=False):
		histogram = None
		intError = -1.0

		for tree in trees:
			filePath = "%s/%s/%s/%s.%s.%s.root" % (self.theConfigDict['HistosPath'], flag, task, flag, task, job)
			#treePath = "%s/%s;1" % (taskInFile, tree)
			treePath = "%s/%s" % (taskInFile, tree)
			#log.logDebug("file: %s" % filePath)
			#log.logDebug("histo: %s" % treePath)

			self.logMemoryContent()
			log.logDebug("Loading tree")

			if (os.path.exists(filePath)):
				theTree = self.getTreeFromFile(filePath, treePath)


				name = "%s%d" % (drawString, datetime.datetime.now().microsecond)
				name = name.replace(".", "")
				name = name.replace("(", "")
				name = name.replace(")", "")

				factor = 1.0
				if (triggerEffCorrection):
					# use SS approval results
					# 2012
					# Update: Use Daniel's results
					year = 2012
					if (tree.endswith("EEDileptonTree")): factor = 0.934 # 0.95
					if (tree.endswith("EMuDileptonTree")): factor = 0.896 # 0.92
					if (tree.endswith("MuMuDileptonTree")): factor = 0.912 # 0.88
					# 2011
					#year = 2011
					#if (tree.endswith("EEDileptonTree")): factor = 0.985 #0.976 # 0.993
					#if (tree.endswith("EMuDileptonTree")): factor = 0.942 #0.925 # 0.921
					#if (tree.endswith("MuMuDileptonTree")): factor = 0.921 #0.944 # 0.892
					log.logHighlighted("Applying %d-trigger efficiency correction of %.3f to %s in %s" % (year, factor, tree, job))

				#self.logMemoryContent()
				tempHistogram = self.getHistoFromTree(theTree, drawString, name, cut, weight=weight, triggerEffCorrectionFactor=factor)

				if (weight != None):
					weight2 = "(%s)*(%s)" % (weight, weight)
					tempErrorHistogram = self.getHistoFromTree(theTree, drawString, name, cut, weight=weight2, triggerEffCorrectionFactor=factor)
					min = 0
					max = 10000
					binMin = tempErrorHistogram.FindBin(min)
					binMax = tempErrorHistogram.FindBin(Result.xMax)
					intError = sqrt(tempErrorHistogram.Integral(binMin, binMax))

				if (histogram == None):
					histogram = tempHistogram
				else:
					histogram.Add(tempHistogram)

			else:
				log.logWarning("File not found %s" % filePath)
				return Result(None)

		result = Result(histogram)
		log.logDebug("Result: %s" % result)
		#result.dataName = job
		result.taskName = taskInFile
		result.flagName = flag

		cfg = self.cfg
		if (dataSamples != None):
			log.logDebug("Overriding masterfile with %s" % InfoHolder.theMasterFile[dataSamples])
			cfg = ConfigParser.ConfigParser()
			cfg.read(InfoHolder.theMasterFile[dataSamples])


		if cfg.has_section(job):
			result.kFactor = cfg.getfloat(job, 'kfactor')
			result.nEvents = cfg.getfloat(job, 'numevents')
			if (result.nEvents != cfg.getint(job, 'localevents') and dynamicCount < -0.0):
				log.logWarning("nEvents incompatible with nLocalEvents and dynamic count disabled!")

			groups = cfg.get(job, 'groups')
			if ("Data" in groups):
				log.logDebug("Data sample found")
				result.luminosity = abs(cfg.getfloat(job, 'crosssection'))
				result.dataType = InfoHolder.DataTypes.Data
				if (triggerEffCorrection):
					log.logError("Applied trigger efficiency correction on Data. This should never happen!")

			elif ("Fake" in groups and not "MC" in groups):
				log.logDebug("DataFake sample found")
				result.luminosity = abs(cfg.getfloat(job, 'crosssection'))
				result.dataType = InfoHolder.DataTypes.DataFake
				result.currentIntegralError = intError
				log.logDebug("Error on DataFake: %f" % intError)

			elif ("MC" in groups):
				log.logDebug("MC sample found")
				if (not triggerEffCorrection):
					log.logWarning("Using MC without applying trigger efficiency correction!")

				result.setXSection(cfg.getfloat(job, 'crosssection'))
				if (dynamicCount > 0.0):
					log.logDebug("Applying dynamic scaling to MC sample: %f (%f)" % (dynamicCount, result.nEvents))
					result.nEvents = dynamicCount

				result.dataType = InfoHolder.DataTypes.MCBackground
				if ("Fake" in groups):
					log.logDebug("MCFake sample found")
					result.dataType = InfoHolder.DataTypes.MCFake
					result.currentIntegralError = intError
					log.logDebug("Error on MCFake: %f" % intError)
				if ("SUSY" in groups):
					log.logDebug("Sample is SUSY signal sample")
					result.dataType = InfoHolder.DataTypes.MCSignal

				luminosity = self.theConfigDict['Luminosity']
				if (scaleMC):
					result.unscaledIntegral = result.integral()

					scalingFactor = 1
					if self.theConfigDict['NLO']:
						scalingFactor = result.xSection / result.nEvents * luminosity * result.kFactor
					else:
						scalingFactor = result.xSection / result.nEvents * luminosity

					log.logDebug("Scaling factor: %f" % scalingFactor)
					result.scale(scalingFactor)
					result.luminosity = luminosity
			else:
				log.logError("Unknown sample found")
				result.dataType = InfoHolder.DataTypes.Unknown

		else:
			log.logError("No section in master list found for job %s" % job)
			return result

		log.logDebug("Number of entries in %s: %f \\pm %f (%d)" % (job, result.integral(), result.integralError(), result.unscaledIntegral))
		return result


	def isHistogramInFile(self, fileName, path):
		log.logDebug("Checking path '%s'\n  in file %s" % (path, fileName))

		file = TFile(fileName, 'READ')
		path = file.Get(path)

		return (path != None)


	def getHistogramFromFile(self, fileName, histoPath):
		log.logDebug("Getting histogram '%s'\n  from file %s" % (histoPath, fileName))

		file = TFile(fileName, 'READ')
		histogram = file.Get(histoPath)

		if (histogram == None):
			log.logError("Could not get histogram '%s'\n  from file %s" % (histoPath, fileName))
			file.Close()
			return None
		else:
			histogram.SetDirectory(0)
			histogram.Sumw2()
			file.Close()
			return histogram


	def getCrossSection(self, job):
		cfg = self.cfg

		value = None
		if cfg.has_section(job):
			value = cfg.getfloat(job, 'crosssection')
			value *= cfg.getfloat(job, 'kfactor')
		else:
			log.logError("Cannot get xSection: job %s not found in MasterList." % job)

		return value


	def getEventCount(self, job, flag, task, dataSamples=None):
		filePath = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)

		histoPath = "%sCounters/analysis paths;1" % (task.split("FinalTrees")[0])
		value = -1.0

		#if (dataSamples == None):
		#	dataSamples = self.theConfigDict['DataSamples']

		#cfg = ConfigParser.ConfigParser()
		#cfg.read(InfoHolder.theMasterFile[dataSamples])

		#isMC = False
		#if cfg.has_section(job):
		#	if ('MC' in cfg.get(job, 'groups')):
		#		isMC = True


		# normal weighting
		histogram = None
		if (os.path.exists(filePath)):
			histogram = self.getHistogramFromFile(filePath, histoPath)

			if (histogram != None):
				count = histogram.GetBinContent(1)
				if (count <= 0.0):
					log.logWarning("Count histogram contained invalid event count: %f" % count)
				else:
					log.logDebug("Event Count: %f" % count)
					value = count

		# Fall11 3D weighting
		# 1. from same file
		histoPath = "%sWeightSummer/Weights;1" % (task)
		weightValue = -1.0

		histogram = None
		if (os.path.exists(filePath)):
			if (self.isHistogramInFile(filePath, histoPath)):
				histogram = self.getHistogramFromFile(filePath, histoPath)

				if (histogram != None):
					count = histogram.GetBinContent(1)
					if (count <= 0.0):
						log.logWarning("3D Weight histogram contained invalid event count: %f" % count)
					else:
						weightValue = count
						log.logDebug("3D Weight: %f" % count)
						tempFactor = weightValue / value
						log.logInfo("3D weight found. Results in weight factor of %.3f for %s" % (tempFactor, job))
						if (abs(1.0 - tempFactor) > 0.1):
							log.logWarning("Unusual 3D weight factor: %f" % (tempFactor))


		# 2. from external file
		taskExternal = "%sNoCuts" % task
		filePathExternal = "%s/%s/%s/%s.%s.%s.root" % (self.dataSetPath, flag, taskExternal, flag, taskExternal, job)
		histoPathExternal = "%sWeightSummer/Weights;1" % (taskExternal)
		weightValueExternal = -1.0

		histogram = None
		if (os.path.exists(filePathExternal) and weightValue >= 0.0):
			if (self.isHistogramInFile(filePathExternal, histoPathExternal)):
				histogram = self.getHistogramFromFile(filePathExternal, histoPathExternal)

				if (histogram != None):
					count = histogram.GetBinContent(1)
					if (count <= 0.0):
						log.logWarning("External 3D Weight histogram contained invalid event count: %f" % count)
					else:
						weightValueExternal = count
						log.logHighlighted("External 3D weight found. Results in weight factor of %.3f for %s. Overwriting previous factor." % (weightValueExternal / value, job))

		if (weightValue >= 0.0 and weightValueExternal > 0.0):
			if (abs(weightValue / weightValueExternal - 1.0) > 0.001):
				log.logError("3D weight and external 3D weight disagree: %f vs %f (ext)!" % (weightValue, weightValueExternal))


		# 3. override from masterlist
		#factor = 1.0

		#if cfg.has_section(job):
		#	if (cfg.has_option(job, 'total3dweightfactor')):
		#		factor = cfg.getfloat(job, 'total3dweightfactor')
		#		log.logError("3D weight override factor found for %s: %f. This is a deprecated feature!" % (job, factor))

		#value *= factor

		if (weightValue >= 0.0):
			value = weightValue

		if (weightValueExternal >= 0.0):
			value = weightValueExternal

		if (weightValue < 0.0 and weightValueExternal < 0.0):
			log.logHighlighted("No 3D weight found for %s" % (job))

		return value

	def getTreeFromDataset(self, flag, task, dataset, treePath, dataVersion=None, cut="", reduce=1.0,central=True):
		if (dataVersion == None):
			dataVersion = self.theConfigDict['DataSamples']
		if central: 
			cut = cut + " && abs(eta1) < 1.4 && abs(eta2) < 1.4"
		else:
			cut = cut + " && 1.6 <= TMath::Max(abs(eta1),abs(eta2)) && !(abs(eta1) > 1.4 && abs(eta1) < 1.6) && !(abs(eta2) > 1.4 && abs(eta2) < 1.6)"
		if (not InfoHolder.theDataSamples.has_key(dataVersion)):
			log.logError("Datasample not registered: %s" % dataVersion)
			return None
		if (not InfoHolder.theDataSamples[dataVersion].has_key(dataset)):
			log.logError("Dataset not found in datasample '%s': %s" % (dataVersion, dataset))
			return None

		jobList = (InfoHolder.theDataSamples[dataVersion])[dataset]
		log.logDebug("Getting '%s' from joblist %s (dataVersion: %s)" % (treePath, str(jobList), dataVersion))
		
		if (len(jobList) > 1):
			log.logError("Adding trees for multiple jobs without scaling!")

		tree = ROOT.TChain("%s%s" % (task, treePath))
		for job in jobList:
			fileName = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)

			if (os.path.exists(fileName)):
				tree.Add(fileName)
			else:
				log.logWarning("File not found: %s" % fileName)

		if (reduce < 1.0):
			log.logDebug("Reducing tree down to %f of its size" % reduce)
			nEntries = tree.GetEntries()
			#log.logDebug("%d" % nEntries)
			tree = tree.CopyTree("", "", int(reduce * nEntries))
			#log.logDebug("%d" % tree.GetEntries())

		if (cut != ""):
			log.logDebug("Cutting tree down to: %s" % cut)
			tree = tree.CopyTree(cut)
			#log.logError("Tree size: %d entries" % (tree.GetEntries()))

		if (tree != None):
			tree.SetDirectory(0)
		else:
			log.logError("Tree invalid: %s -%s - %s - %s" % (flag, task, dataset, treePath))
		return tree


	def getTreeFromJob(self, flag, task, job, treePath, dataVersion=None, cut=""):
		tree = ROOT.TChain("%s%s" % (task, treePath))
		#~ fileName = "%s/%s/%s/%s.%s.%s.root" % (self.theConfigDict['HistosPath'], flag, task, flag, task, job)
		fileName = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)
		if (os.path.exists(fileName)):
			tree.Add(fileName)
		else:
			log.logWarning("File not found: %s" % fileName)

		if (cut != ""):
			log.logDebug("Cutting tree down to: %s" % cut)
			tree = tree.CopyTree(cut)
			#log.logError("Tree size: %d entries" % (tree.GetEntries()))

		if (tree != None):
			tree.SetDirectory(0)
		else:
			log.logError("Tree invalid: %s -%s - %s - %s" % (flag, task, dataset, treePath))
		return tree


	#def getHistoFromTree(self, tree, variable, name, cut, nBins=2000, xMin= -1000.0, xMax=1000.0, weight=None, triggerEffCorrectionFactor=1.0):
	def getHistoFromTree(self, tree, variable, name, cut, nBins=2000, xMin=0.0, xMax=2000.0, weight=None, triggerEffCorrectionFactor=1.0):
		hTree = ROOT.TH1F("h%s" % name, "Brot%s" % variable, nBins, xMin, xMax)
		hTree.Sumw2()

		log.logDebug("Drawing '%s' with cut sequence '%s'" % (variable, cut))
		#cutTree = tree.CopyTree(cut)

		if (triggerEffCorrectionFactor != 1.0):
			log.logDebug("Applying trigger efficiency correction of %f" % triggerEffCorrectionFactor)
			weight = "%s * %f" % (weight, triggerEffCorrectionFactor)

		if (tree != None):
			if (weight != None):
				log.logDebug("Applying weights to tree: %s" % weight)
				#cutTree.Draw("%s >> h%s" % (variable, name), weight)
				tree.Draw("%s >> h%s" % (variable, name), "%s * (%s)" % (weight, cut))
			else:
				#cutTree.Draw("%s >> h%s" % (variable, name), "")
				tree.Draw("%s >> h%s" % (variable, name), cut)
			hTree = ROOT.gDirectory.Get("h%s" % name)
		else:
			#log.logWarning("Tree is not valid (maybe cut down to zero): %s" % name)
			log.logWarning("Tree is not valid: %s" % name)

		if hTree != None:
			hTree.SetDirectory(0)
			#hTree.Sumw2()
		else:
			log.logError("Could not create histogram %s from tree" % name)

		return hTree


	def getTreeFromFile(self, fileName, treePath):
		log.logDebug("Getting tree '%s'\n  from file %s" % (treePath, fileName))

		#file = TFile(fileName, 'READ')
		#tree = file.Get(treePath)
		tree = ROOT.TChain(treePath)
		tree.Add(fileName)

		if (tree == None):
			log.logError("Could not get tree '%s'\n  from file %s" % (treePath, fileName))
			#file.Close()
			return None
		else:
			tree.SetDirectory(0)
			#file.Close()
			return tree

	def logMemoryContent(self):
		directory = ROOT.gDirectory
		list = directory.GetList()
		keyNames = [key.GetName() for key in list]
		log.logDebug("Memory content:%s" % keyNames)



class Result:
	# for integral calculation
	xMax = 10000
	# formatting string for result to string conversion
	formatString = "%.3f \pm %.3f"

	def __init__(self, histogram):
		if (histogram == None):
			log.logWarning("Creating a result from an empty histogram.")


		# default configuration
		self.dataName = "None"
		self.dataVersion = "None"
		self.taskName = "None"
		self.flagName = "None"
		self.dataType = InfoHolder.DataTypes.Unknown
		self.is2DHistogram = False
		self.scaled = False

		self.histogram = histogram
		#self.histogram.Sumw2()
		self.unscaledIntegral = -1
		self.scalingFactor = -1
		self.luminosity = -1
		self.xSection = -1
		self.kFactor = -1
		self.nEvents = -1
		self.__scaledAndAdded = False
		self.currentIntegralError = -1

		self.title = None

		#log.logDebug("%s" % type(histogram))
		self.is2DHistogram = False
		if (type(histogram) == ROOT.TH2F):
			log.logDebug("2D histogram found: %s" % type(histogram))
			self.is2DHistogram = True

	def clone(self):
		if (self.is2DHistogram):
			log.logError("Cloning of 2d histograms not supported!")
			return None

		cloneHistogram = ROOT.TH1F(self.histogram)
		clone = Result(cloneHistogram)
		clone.dataName = self.dataName
		clone.dataVersion = self.dataVersion
		clone.taskName = self.taskName
		clone.flagName = self.flagName
		clone.dataType = self.dataType
		clone.scaled = self.scaled

		clone.unscaledIntegral = self.unscaledIntegral
		clone.scalingFactor = self.scalingFactor
		clone.luminosity = self.luminosity
		clone.xSection = self.xSection
		clone.kFactor = self.kFactor
		clone.nEvents = self.nEvents
		clone.__scaledAndAdded = self.__scaledAndAdded
		clone.currentIntegralError = self.currentIntegralError

		clone.title = self.title

		# not supported
		self.is2DHistogram = False
		return clone

	def setXSection(self, xSection):
		if (xSection <= 0.0):
			log.logError("Cannot set result cross section to zero or less (%f)" % xSection)
		else:
			self.xSection = xSection

	def integral(self):
		#log.logDebug("bin1: %f" % self.histogram.GetBinContent(1))

		#a = self.histogram.GetBinContent(1)
		#if (a == ):
		#	log.logError("NAN!")

		try:
			min = 0
			binMin = self.histogram.FindBin(min)
			binMax = self.histogram.FindBin(Result.xMax)
			return self.histogram.Integral(binMin, binMax)
		except:
			log.logError("Cannot get histogram integral")
			return - 1

	def integralError(self):
		if (self.currentIntegralError >= 0.0):
			return self.currentIntegralError
		if (self.is2DHistogram):
			log.logError("Integral error not implemented for 2D histograms.")
			return - 1

		if (self.scaled):
			# have differently scaled histograms been added? (cannot calculate error the usual way)
			if (self.__scaledAndAdded):
				log.logError("Result scaled and added, but integral error value not set.")
				return - 1
			# usual way
			if (self.unscaledIntegral < 0 or self.scalingFactor < 0):
				log.logWarning("Could not determine integral error: unscaled integral or scaling factor not set!")
				return - 1

			#log.logDebug("Scaled Error: sqrt(%f) * %f = %f" % (self.unscaledIntegral, self.scalingFactor, sqrt(self.unscaledIntegral) * self.scalingFactor))
			return sqrt(self.unscaledIntegral) * self.scalingFactor
		else:
			return sqrt(self.integral())

	def scale(self, factor):
		if (self.histogram == None):
			log.logError("Trying to scale empty result")
			return
		if (self.is2DHistogram):
			log.logError("Scaling not implemented for 2D histograms.")
			return

		self.histogram.Scale(factor)
		#log.logDebug("Result: Scaling factor = %f" % (self.scalingFactor))
		if (self.scalingFactor < 0):
			self.scalingFactor = factor
		else:
			self.scalingFactor *= factor

		if (self.currentIntegralError > 0.0):
			self.currentIntegralError *= factor

		#log.logDebug("Result: Scaling factor afterwards = %f" % (self.scalingFactor))
		self.scaled = True

	def addResult(self, result):
		if (self.histogram == None):
			log.logWarning("Adding to empty result!")
			if (result.histogram == None): log.logWarning("... also adding empty result!")
			return result
		if (result.histogram == None):
			log.logWarning("Adding empty result!")
			return self

		if (not self.scaled == result.scaled):
			log.logError("Cannot add scaled and unscaled results")
			return None

		if (self.dataType != result.dataType):
			log.logError("Cannot add results of different data types (%d, %d)" % (self.dataType, results.dataType))
			return None

		# lumi info
		if (self.luminosity > 0 and result.luminosity > 0):
			if (self.dataType == InfoHolder.DataTypes.Data):
				self.luminosity += result.luminosity # for data
			else:
				pass # for MC and Unknown
		else:
			log.logWarning("Adding results without complete luminosity information (%f, %f)" % (self.luminosity, result.luminosity))
			self.luminosity = -1

		# xSection info
		if (self.xSection > 0 and result.xSection > 0):
			self.xSection += result.xSection
		else:
			if (self.dataType != InfoHolder.DataTypes.Data):
				log.logWarning("Adding results without complete xSection information (%f, %f)" % (self.xSection, result.xSection))
			self.xSection = -1

		# xSection info
		if (self.kFactor > 0 and result.kFactor > 0):
			if (self.kFactor != result.kFactor):
				log.logHighlighted("Adding results with different kFactors (%f, %f). Will not be able to track this any more." % (self.kFactor, result.kFactor))
				self.kFactor = -1
		else:
			log.logInfo("Adding results without complete kFactor information (%f, %f)" % (self.kFactor, result.kFactor))
			self.kFactor = -1

		if (not self.scaled):
			self.histogram.Add(result.histogram)
			return self
		if (self.scalingFactor == result.scalingFactor):
			self.unscaledIntegral += result.unscaledIntegral
			self.histogram.Add(result.histogram)
			return self

		log.logDebug("Combining results: %s, %s" % (str(self), str(result)))
		# first calculate new error
		self.currentIntegralError = sqrt(self.integralError() * self.integralError() + result.integralError() * result.integralError())
		# then change histogram
		self.histogram.Add(result.histogram)
		self.unscaledIntegral += result.unscaledIntegral
		self.scalingFactor = -1
		# finally mark result as scaled and added
		self.__scaledAndAdded = True
		log.logDebug("... to: %s" % (str(self)))
		return self

	def divideByResult(self, result):
		#if (self.dataType != InfoHolder.DataTypes.Data or result.dataType != InfoHolder.DataTypes.Data):
		#	log.logError("Result division only implemented for data results!")
		#	return None
		if (self.luminosity != result.luminosity):
			log.logWarning("Dividing results with unlike luminosity!")

		#self.histogram.Divide(result.histogram)
		self.histogram.Divide(self.histogram, result.histogram, 1, 1, "B")

		return self


	def __str__(self):
		return Result.formatString % (self.integral(), self.integralError())


# entry point
if (__name__ == "__main__"):
	log.outputLevel = 5
	theDataInterface = dataInterface()
	histogram = theDataInterface.getHistogram("test", "cutsV2None", "LM0", InfoHolder.theHistograms['electron pt'])


