#!/usr/bin/env python

### file that holds information and helper routines

from messageLogger import messageLogger as log

import ROOT
from ROOT import TFile, TH1F

import os, ConfigParser
from math import sqrt
import datetime

### simpler/smaller tree format to increase the speed
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

### Info holder for sample information
class InfoHolder(object):
	theDataSamples = {			
			'sw74X': {
				'Data': ["MergedData"],
	
				'TTJets_Madgraph': ["TTJets_Dilepton_Madgraph_MLM_Spring15_25ns_v1"],
				'TTJets_aMCatNLO': ["TTJets_aMCatNLO_FXFX_Spring15_25ns"],
				'TT_Powheg': ["TT_Dilepton_Powheg_Spring15_25ns"],
				
				'SingleTop': ["ST_sChannel_4f_aMCatNLO_Spring15_25ns","ST_antitop_tChannel_4f_Powheg_Spring15_25ns","ST_top_tChannel_4f_Powheg_Spring15_25ns","ST_antitop_tWChannel_5f_Powheg_Spring15_25ns","ST_top_tWChannel_5f_Powheg_Spring15_25ns"],
				'ZJets' : ["ZJets_aMCatNLO_Spring15_25ns","AStar_aMCatNLO_Spring15_25ns"],
				'ZJetsLO' : ["ZJets_Madgraph_Spring15_25ns","AStar_aMCatNLO_Spring15_25ns"],
				'ZJetsOnly' : ["ZJets_aMCatNLO_Spring15_25ns"],
				'AStar': ["AStar_aMCatNLO_Spring15_25ns"],
				"Rare" : ["TTZToLLNuNu_aMCatNLO_FXFX_Spring15_25ns","TTZToQQ_aMCatNLO_FXFX_Spring15_25ns","TTWToLNu_aMCatNLO_FXFX_Spring15_25ns","TTG_aMCatNLO_FXFX_Spring15_25ns","WZZ_aMCatNLO_FXFX_Spring15_25ns","WWZ_aMCatNLO_FXFX_Spring15_25ns","ZZZ_aMCatNLO_FXFX_Spring15_25ns"],
				'Diboson' : ["WWTo2L2Nu_Powheg_Spring15_25ns","WWToLNuQQ_Powheg_Spring15_25ns","WZTo1L1Nu2Q_aMCatNLO_Spring15_25ns","WZTo1L3Nu_aMCatNLO_Spring15_25ns","WZTo3LNu_Powheg_Spring15_25ns","WZTo2L2Q_aMCatNLO_Spring15_25ns","ZZTo4Q_aMCatNLO_Spring15_25ns","ZZTo4L_Powheg_Spring15_25ns","ZZTo2Q2Nu_aMCatNLO_Spring15_25ns","ZZTo2L2Q_aMCatNLO_Spring15_25ns"],
				'slepton_500_250': ["T6bbllslepton_msbottom_500_mneutralino_250"],
				'slepton_550_175': ["T6bbllslepton_msbottom_550_mneutralino_175"],
				'slepton_550_200': ["T6bbllslepton_msbottom_550_mneutralino_200"],
				'slepton_550_225': ["T6bbllslepton_msbottom_550_mneutralino_225"],
				'slepton_550_250': ["T6bbllslepton_msbottom_550_mneutralino_250"],
				},				
				
}

	theSampleDescriptions = {
		'ZJets': "Z+jets",
		'TTJets': "t#bar{t}+jets",
		'SingleTop': "t / #bar{t}+jets",
		'Diboson': "WW, WZ, ZZ",
		'DataFake': "Fake leptons",
		'Rare': "Rare SM",
	}

	theMasterFile = {
		'sw74X':"../frameWorkBase/MasterList.ini",
	}

### main interface to access data
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
	
	### convert the trees to the new format to improve the speed
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
				newTree.Fill()

		#return newTree
		return newTree.CopyTree(selection)

	convertDileptonTree = staticmethod(convertDileptonTree)


	### Check if a histogram exists
	def isHistogramInFile(self, fileName, path):
		log.logDebug("Checking path '%s'\n  in file %s" % (path, fileName))

		file = TFile(fileName, 'READ')
		path = file.Get(path)

		return (path != None)


	### get the histogram from the file
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


	### fetch the MC cross section
	def getCrossSection(self, job):
		cfg = self.cfg

		value = None
		if cfg.has_section(job):
			value = cfg.getfloat(job, 'crosssection')
		else:
			log.logError("Cannot get xSection: job %s not found in MasterList." % job)

		return value


	### get the event counts for MC normalization
	def getEventCount(self, job, flag, task, dataSamples=None):
		filePath = "%s/%s.%s.%s.root" % (self.dataSetPath, flag, "processed", job)
		

		histoPath = "%sCounters/analysis paths;1" % (task.split("FinalTrees")[0])
		value = -1.0
		
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

		return value

	### fetch the tree from the dataset
	def getTreeFromDataset(self, flag, task, dataset, treePath, dataVersion=None, cut="", reduce=1.0,etaRegion="Inclusive"):
		if (dataVersion == None):
			dataVersion = self.theConfigDict['DataSamples']
		### cut on eta region
		if etaRegion=="Central": 
			cut = cut + " && abs(eta1) < 1.4 && abs(eta2) < 1.4"
		elif etaRegion=="Forward":
			cut = cut + " && 1.6 <= TMath::Max(abs(eta1),abs(eta2))"
		### Check if the sample is known for this version(in the Info holder)
		if (not InfoHolder.theDataSamples.has_key(dataVersion)):
			log.logError("Datasample not registered: %s" % dataVersion)
			return None
		if (not InfoHolder.theDataSamples[dataVersion].has_key(dataset)):
			log.logError("Dataset not found in datasample '%s': %s" % (dataVersion, dataset))
			return None

		### Some background categories (like diboson) contain several samples so a job list is created
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

		### Possibility to refuce the trees to a fraction if they get too large
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


	### Get the tree for a certain job (MC sample)
	def getTreeFromJob(self, flag, task, job, treePath, dataVersion=None, cut=""):
		tree = ROOT.TChain("%s%s" % (task, treePath))
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



# entry point
if (__name__ == "__main__"):
	log.outputLevel = 5
	theDataInterface = dataInterface()
	histogram = theDataInterface.getHistogram("test", "cutsV2None", "LM0", InfoHolder.theHistograms['electron pt'])


