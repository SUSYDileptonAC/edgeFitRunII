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

ROOT.gROOT.ProcessLine(\
					   "struct MyDileptonTreeFormat{\
						 Double_t inv;\
						 Int_t chargeProduct;\
						 Int_t nJets;\
						 Double_t ht;\
						 Double_t met;\
						 Double_t MT2;\
						 Double_t pt1;\
						 Double_t pt2;\
						 Double_t weight;\
						};")
from ROOT import MyDileptonTreeFormat


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
		'chargeProduct': "",
		'ht': "MET/HT",
		'met': "MET/MET",
		'MHT': "MET/MHT",

		'MET vs HT': "MET/MET - HT",
		'MET vs MHT': "MET/MET - MHT",

		'nJets': "Multiplicity/JetMultiplicity",
		'nBJets': "",

		'nVertices': "nVErtices",

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
			
			'sw80X': {
				'Data': ["MergedData"],
	
				'TTJets_Madgraph': ["TTJets_Dilepton_Madgraph_MLM_Summer16_25ns"],
				'TT_aMCatNLO': ["TT_Dilepton_aMCatNLO_FXFX_Summer16_25ns"],
				'TTJets_aMCatNLO': ["TTJets_aMCatNLO_FXFX_Spring16_25ns"],
				'TT_Dilepton_Powheg': ["TT_Dilepton_Powheg_Summer16_25ns"],
				'TT_Powheg': ["TT_Powheg_Summer16_25ns"],
				
				'SingleTop': ["ST_sChannel_4f_aMCatNLO_Summer16_25ns","ST_antitop_tWChannel_5f_Powheg_NoFullyHadronicDecays_Summer16_25ns","ST_top_tWChannel_5f_Powheg_NoFullyHadronicDecays_Summer16_25ns"],
				'FourTop': ["4T_aMCatNLO_FXFX_Summer16_25ns"],
				#~ 'ZJets' : ["ZJets_aMCatNLO_Spring16_25ns","AStar_aMCatNLO_Spring16_25ns"],
				'ZJets' : ["ZJets_Madgraph_Summer16_25ns","AStar_Madgraph_Summer16_25ns"],
				'ZJetsLO' : ["ZJets_Madgraph_Summer16_25ns","AStar_Madgraph_Summer16_25ns"],
				#~ 'ZJetsOnly' : ["ZJets_aMCatNLO_Spring16_25ns"],
				'ZJetsOnly' : ["ZJets_Madgraph_Summer16_25ns"],
				'AStar': ["AStar_Madgraph_Summer16_25ns"],
				"Rare" : ["TTZToLLNuNu_aMCatNLO_FXFX_Summer16_25ns","TTZToQQ_aMCatNLO_FXFX_Summer16_25ns","TTWToLNu_aMCatNLO_FXFX_Summer16_25ns","TTWToQQ_aMCatNLO_FXFX_Summer16_25ns","TTG_aMCatNLO_FXFX_Summer16_25ns","4T_aMCatNLO_FXFX_Summer16_25ns","TZQ_LL_aMCatNLO_Summer16_25ns","WZZ_aMCatNLO_FXFX_Summer16_25ns","WWZ_aMCatNLO_FXFX_Summer16_25ns","ZZZ_aMCatNLO_FXFX_Summer16_25ns","TTHToNonbb_Powheg_Summer16_25ns","TTHTobb_Powheg_Summer16_25ns","VH_ToNonbb_aMCatNLO_Summer16_25ns"],
				'Diboson' : ["WWTo2L2Nu_Powheg_Summer16_25ns","WWTo1L1Nu2Q_aMCatNLO_Summer16_25ns","WZTo1L1Nu2Q_aMCatNLO_Summer16_25ns","WZTo1L3Nu_aMCatNLO_Summer16_25ns","WZTo3LNu_aMCatNLO_Summer16_25ns","ZZTo4Q_aMCatNLO_Summer16_25ns","ZZTo4L_Powheg_Summer16_25ns","ZZTo2Q2Nu_aMCatNLO_Summer16_25ns","ZZTo2L2Q_aMCatNLO_Summer16_25ns","ZZTo2L2Nu_Powheg_Summer16_25ns"],
				# "WZJetsTo2L2Q_madgraph_Summer12", 
				'DibosonWW' : ["WWTo2L2Nu_Powheg_Summer16_25ns","WWTo1L1Nu2Q_aMCatNLO_Summer16_25ns"],
				'DibosonWZ' : ["WZTo1L1Nu2Q_aMCatNLO_Summer16_25ns","WZTo1L3Nu_aMCatNLO_Summer16_25ns","WZTo3LNu_aMCatNLO_Summer16_25ns"],
				'DibosonZZ' : ["ZZTo4Q_aMCatNLO_Summer16_25ns","ZZTo4L_Powheg_Summer16_25ns","ZZTo2Q2Nu_aMCatNLO_Summer16_25ns","ZZTo2L2Q_aMCatNLO_Summer16_25ns","ZZTo2L2Nu_Powheg_Summer16_25ns"],
				'slepton_750_175': ["T6bbllslepton_msbottom_750_mneutralino_175"],
				'slepton_800_150': ["T6bbllslepton_msbottom_800_mneutralino_150"],
				'slepton_800_200': ["T6bbllslepton_msbottom_800_mneutralino_200"],
				'slepton_800_250': ["T6bbllslepton_msbottom_800_mneutralino_250"],
				'slepton_800_300': ["T6bbllslepton_msbottom_800_mneutralino_300"],
				'slepton_800_400': ["T6bbllslepton_msbottom_800_mneutralino_400"],
				'slepton_800_500': ["T6bbllslepton_msbottom_800_mneutralino_500"],
				'slepton_850_150': ["T6bbllslepton_msbottom_850_mneutralino_150"],
				'slepton_850_250': ["T6bbllslepton_msbottom_850_mneutralino_250"],
				'slepton_850_300': ["T6bbllslepton_msbottom_850_mneutralino_300"],
				'slepton_850_500': ["T6bbllslepton_msbottom_850_mneutralino_500"],
				'slepton_900_150': ["T6bbllslepton_msbottom_900_mneutralino_150"],
				'slepton_900_200': ["T6bbllslepton_msbottom_900_mneutralino_200"],
				'slepton_900_250': ["T6bbllslepton_msbottom_900_mneutralino_250"],
				'slepton_900_350': ["T6bbllslepton_msbottom_900_mneutralino_350"],
				'slepton_900_500': ["T6bbllslepton_msbottom_900_mneutralino_500"],
				'slepton_1000_150': ["T6bbllslepton_msbottom_1000_mneutralino_150"],
				'slepton_1000_300': ["T6bbllslepton_msbottom_1000_mneutralino_300"],
				'slepton_1000_500': ["T6bbllslepton_msbottom_1000_mneutralino_500"],
				'slepton_1000_700': ["T6bbllslepton_msbottom_1000_mneutralino_700"],
				'slepton_1100_700': ["T6bbllslepton_msbottom_1100_mneutralino_700"],
				'slepton_1200_700': ["T6bbllslepton_msbottom_1200_mneutralino_700"],
				'slepton_1300_700': ["T6bbllslepton_msbottom_1300_mneutralino_700"],
		
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

	### needs to be adapted or switched to relative path
	theMasterFile = {
		'sw80X':"/home/home4/institut_1b/schomakers/FrameWork/SubmitScripts/Input/Master80X_MC_Summer16.ini",
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
		
		print dataSetPath
		print InfoHolder.theMasterFile
			
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

		data = MyDileptonTreeFormat()
		newTree = ROOT.TTree("treeInvM", "Dilepton Tree")
		newTree.SetDirectory(0)
		newTree.Branch("inv", ROOT.AddressOf(data, "inv"), "inv/D")
		newTree.Branch("chargeProduct", ROOT.AddressOf(data, "chargeProduct"), "chargeProduct/I")
		newTree.Branch("nJets", ROOT.AddressOf(data, "nJets"), "nJets/I")
		newTree.Branch("ht", ROOT.AddressOf(data, "ht"), "ht/D")
		newTree.Branch("met", ROOT.AddressOf(data, "met"), "met/D")
		newTree.Branch("MT2", ROOT.AddressOf(data, "MT2"), "MT2/D")
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
				### depending on the sample we have to switch between p4.M() and mll
				#~ data.inv = tree.p4.M()
				data.inv = tree.mll
				data.chargeProduct = tree.chargeProduct
				data.nJets = tree.nJets
				data.ht = tree.ht
				data.met = tree.met
				data.MT2 = tree.MT2
				data.pt1 = tree.pt1
				data.pt2 = tree.pt2
				if (weightString != ""):
					eventWeight = eval(weightString)
					data.weight = eventWeight
				else:
					data.weight = weight
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
				#~ data.invM = tree.p4.M()
				data.invM = tree.mll
				data.chargeProduct = tree.chargeProduct
				newTree.Fill()

		newTree.SetDirectory(0)
		return newTree

	convertTree = staticmethod(convertTree)


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

	def getNegWeightFraction(self, job):
		cfg = self.cfg

		value = None
		if cfg.has_section(job):
			value = cfg.getfloat(job, 'negWeightFraction')
		else:
			log.logError("Cannot get negWeightFraction: job %s not found in MasterList." % job)

		return value


	def getEventCount(self, job, flag, task, dataSamples=None):
		filePath = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)
		

		histoPath = "%sCounters/analysis paths;1" % (task.split("FinalTrees")[0])
		value = -1.0
		



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

	def getTreeFromDataset(self, flag, task, dataset, treePath, dataVersion=None, cut="", reduce=1.0):
		if (dataVersion == None):
			dataVersion = self.theConfigDict['DataSamples']
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
		#~ if "Data" in job or "HT_Run2016B" in job:
			#~ task = "cutsV32DileptonFinalTrees"
		#~ else:
			#~ task = "cutsV31DileptonFinalTrees"
		tree = ROOT.TChain("%s%s" % (task, treePath))
		#~ fileName = "%s/%s/%s/%s.%s.%s.root" % (self.theConfigDict['HistosPath'], flag, task, flag, task, job)
		fileName = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)
		print fileName
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
		#~ else:
			#~ log.logError("Tree invalid: %s -%s - %s - %s"%(flag, task, dataset, treePath))
		return tree



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


