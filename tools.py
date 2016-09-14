#!/usr/bin/env python

### helper functions to make labels, legends, store parameters
### and get MC trees

import ROOT

#import mainConfig
from messageLogger import messageLogger as log

from ROOT import TCanvas, THStack, TLegend, TPad, TPaveLabel #TFile, TPaveText
from ROOT import gROOT, gStyle

from math import sqrt
import math
import pickle, os, shelve

### Add labels
def makeAnnotations(annotations, textSize=0.04, color=None, align=None):
		from ROOT import TLatex
		latex = TLatex()
		latex.SetNDC()

		annoColor = 12
		if (color != None):
			annoColor = color
		latex.SetTextSize(textSize)
		latex.SetTextFont(42)
		latex.SetTextColor(annoColor)
		if (align != None):
			latex.SetTextAlign(align) # 31 = right alignment

		for annotation in annotations:
			if "CMS" in annotation[2]:
				latex.SetTextFont(61)
				latex.SetTextSize(0.05)
			elif "Preliminary" in annotation[2] or "Private" in annotation[2] or "Simulation" in annotation[2]:
				latex.SetTextFont(52) 
				latex.SetTextSize(0.0375)
			latex.DrawLatex(*annotation)
			latex.SetTextFont(42)
			latex.SetTextSize(textSize)

### make the CMS annotations (CMS, preliminary/simulation, energy and luminosity)
def makeCMSAnnotation(xPos, yPos, luminosity, mcOnly=False, preliminary=True, year=2011, ownWork=False):
		from ROOT import kBlack, kBlue
		energy = -1
		if (year == 2011):
			energy = 7
		elif (year == 2012):
			energy = 8
		elif (year == 2015):
			energy = 13

		color = kBlack

		if (mcOnly):
			cmsString = "CMS"
			if (ownWork):
				cmsExtra = "Simulation"
				annotationsCMS = [
						   (xPos, yPos, cmsString),
						   (xPos, yPos-0.04, cmsExtra),
						   (0.7, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000,energy)),
						   ]
			else:
				cmsExtra = "#splitline{Private Work}{Simulation}"
				annotationsCMS = [
						   (xPos, yPos, cmsString),
						   (xPos, yPos-0.07, cmsExtra),
						   (0.7, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000,energy)),
						   ]

			makeAnnotations(annotationsCMS, color=color)
		else:
			cmsString = "CMS"
			if (preliminary):
				cmsExtra = "Preliminary"
			if (ownWork):
				cmsExtra = "Private Work"

			annotationsCMS = [
					   (xPos, yPos, cmsString),
					   (xPos, yPos-0.04, cmsExtra),
					   (0.7, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000 ,energy)),
					   ]            
				

			makeAnnotations(annotationsCMS, color=color)
		   
		   
### legend tool
def myLegend(x1, y1, x2, y2, borderSize=1):
	from ROOT import kWhite
	legend = ROOT.TLegend(x1, y1, x2, y2)
	legend.SetLineWidth(2)
	legend.SetBorderSize(borderSize)
	legend.SetFillColor(kWhite)
	return legend

# store and load values into / from pickle files
def storeParameter(project, task, name, value, basePath = "shelves/"):
	fileName = "%s-%s-%s.pkl" % (project, task, name)
	if not os.path.exists(basePath):
		os.makedirs(basePath)
	pFile = open("%s%s" % (basePath, fileName), 'wb')
	pickle.dump(value, pFile)
	pFile.close()
	
def loadParameter(project, task, name, basePath = "shelves/"):
	fileName = "%s-%s-%s.pkl" % (project, task, name)
	filePath = "%s%s" % (basePath, fileName)
	value = None
	if (os.path.exists(filePath)):
		pFile = open(filePath, 'rb')
		value = pickle.load(pFile)
		pFile.close()

	return value

def updateParameter(project, task, name, value, index = None, basePath = "shelves/"):
	if not index == None:
		dictPath = "%s/dicts/"%basePath
		result = loadParameter(project, task, name, basePath = dictPath)
		if not "update" in dir(result):
			result = {index:value}
		else:
			result.update({index:value})
				
		storeParameter(project, task, name, result, basePath = dictPath)
		
	else:
		result = value
		
	storeParameter(project, task, name, value)
	
### get the trees for MC
def getTrees(theConfig, datasets, etaRegion="Central"):
	import dataInterface
	theDataInterface = dataInterface.DataInterface(theConfig.dataSetPath,theConfig.dataVersion)
	treePathOFOS = "/EMuDileptonTree"
	treePathEE = "/EEDileptonTree"
	treePathMM = "/MuMuDileptonTree"

	treesMCOFOS = ROOT.TList()
	treesMCEE = ROOT.TList()
	treesMCMM = ROOT.TList()

	### make eta cuts
	if etaRegion=="Inclusive":
		cut = theConfig.selection.cut
	elif etaRegion=="Central":
		cut = theConfig.selection.cut + " && abs(eta1) < 1.4 && abs(eta2) < 1.4"
	elif etaRegion=="Forward":
		cut = theConfig.selection.cut + " && 1.6 <= TMath::Max(abs(eta1),abs(eta2)) && !(abs(eta1) > 1.4 && abs(eta1) < 1.6) && !(abs(eta2) > 1.4 && abs(eta2) < 1.6)"

	for dataset in datasets:
		scale = 0.0

		### jobs for each MC sample
		jobs = dataInterface.InfoHolder.theDataSamples[theConfig.dataVersion][dataset]
		if (len(jobs) > 1):
			log.logDebug("Scaling and adding more than one job: %s" % (jobs))
		for job in jobs:
			### get the trees
			treeMCOFOSraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathOFOS, dataVersion=theConfig.dataVersion, cut=cut)
			treeMCEEraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathEE, dataVersion=theConfig.dataVersion, cut=cut)
			treeMCMMraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathMM, dataVersion=theConfig.dataVersion, cut=cut)

			### scale to cross section
			dynNTotal = theDataInterface.getEventCount(job, theConfig.flag, theConfig.task)
			dynXsection = theDataInterface.getCrossSection(job)
			dynScale = dynXsection * theConfig.runRange.lumi / dynNTotal
			if (dynScale != scale):
				log.logInfo("dyn scale for %s (%s): n = %d, x = %f => %f" % (job, dataset, dynNTotal, dynXsection, dynScale))
				scale = dynScale
			else:
				log.logError("No dynamic scale applied. This should never happen!")

			# convert trees
			treesMCOFOS.Add(dataInterface.DataInterface.convertDileptonTree(treeMCOFOSraw, weight=scale))
			treesMCEE.Add(dataInterface.DataInterface.convertDileptonTree(treeMCEEraw, weight=scale))
			treesMCMM.Add(dataInterface.DataInterface.convertDileptonTree(treeMCMMraw, weight=scale))

	treeMCOFOStotal = ROOT.TTree.MergeTrees(treesMCOFOS)
	treeMCEEtotal = ROOT.TTree.MergeTrees(treesMCEE)
	treeMCMMtotal = ROOT.TTree.MergeTrees(treesMCMM)

	return (treeMCOFOStotal, treeMCEEtotal, treeMCMMtotal)
