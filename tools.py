#!/usr/bin/env python

#=======================================================
# Project: LocalAnalysis
#              SUSY Same Sign Dilepton Analysis
#
# File: tools.py
#
# Author: Daniel Sprenger
#         daniel.sprenger@cern.ch
#=======================================================
import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT

#import newCombineSummer as helper
#import mainConfig
from messageLogger import messageLogger as log

from ROOT import TCanvas, THStack, TLegend, TPad, TPaveLabel #TFile, TPaveText
from ROOT import gROOT, gStyle

from math import sqrt
import math
import pickle, os, shelve

# paths
theHistoPath = '/home/epsilon/SUSY/Histos'
#theSusyLuminosity = 200. #pb-1


## wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
def waitForInput():
	raw_input('press <return> to quit: ')


def savePadToFile(pad, filename="plot.png", width=1024, height=768):
	c = ROOT.TCanvas("c", "Plot", 10, 10, width, height)
	c.cd()
	newPad = pad.Clone()
	newPad.Draw()
	c.Update()
	newPad.Print(filename)
	c.Close()


def provideNCanvas(n=2, title="Same Sign Dilepton SUSY analysis"):
	if (n < 1):
		log.logError("'%d' is not a valid number of pads!")
		return None
	if (n == 1):
		[c1, pad1, pad2] = provideDoubleCanvas()
		return [c1, [pad1]]
	if (n == 2):
		[c1, pad1, pad2] = provideDoubleCanvas()
		return [c1, [pad1, pad2]]
	if (n == 3):
		[c1, pad1, pad2, pad3, pad4] = provideQuadCanvas()
		return [c1, [pad1, pad2, pad3]]
	if (n == 4):
		[c1, pad1, pad2, pad3, pad4] = provideQuadCanvas()
		return [c1, [pad1, pad2, pad3, pad4]]

	# window settings
	theCanvasSizeX = 1520
	theCanvasSizeY = 920
	theScreenSizeX = 1680
	theScreenSizeY = 1050

	# canvas
	posX = int(theScreenSizeX * 0.04)
	posY = int(theScreenSizeY * 0.03)
	#posX = (theScreenSizeX - theCanvasSizeX) / 2
	#posY = (theScreenSizeY - theCanvasSizeY) / 2
	c1 = TCanvas('c1', title, posX, posY, theCanvasSizeX, theCanvasSizeY)

	i = int(math.ceil(-0.5 + 0.5 * math.sqrt(4.0 * n + 1.0)))
	nRows = i
	nColumns = i + 1

	log.logDebug("no. of columns: %d" % nColumns)
	log.logDebug("no. of rows: %d" % nRows)

	c1.Divide(nColumns, nRows, 0.0001, 0.0001)

	pads = []
	iPad = 1
	for iRow in range(0, nRows):
		for iColumn in range(0, nColumns):
			if (iPad <= n):
				c1.cd(iPad)
				pad = TPad('pad%d' % iPad, 'Pad for %dth histogram' % iPad, 0.03, 0.03, 0.97, 0.97, 0)
				pad.Draw()
				pads.extend([pad])
				iPad += 1

	log.logDebug("Pads: %s" % pads)
	return [c1, pads]

def provideDoubleCanvas(title="Same Sign Dilepton SUSY analysis"):
	# window settings
	theCanvasSizeX = 1200
	theCanvasSizeY = 720
	theScreenSizeX = 1280
	theScreenSizeY = 760

	# canvas
	posX = (theScreenSizeX - theCanvasSizeX) / 2
	posY = (theScreenSizeY - theCanvasSizeY) / 2
	c1 = TCanvas('c1', title, posX, posY, theCanvasSizeX, theCanvasSizeY)
	c1.Divide(2, 1)

	c1.cd(1)
	pad1 = TPad('pad1', 'Pad for left histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad1.Draw()
	c1.cd(2)
	pad2 = TPad('pad2', 'Pad for rigth histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad2.Draw()

	return [c1, pad1, pad2]


def provideQuadCanvas(title="Same Sign Dilepton SUSY analysis"):
	# window settings
	theCanvasSizeX = 1400
	theCanvasSizeY = 920
	theScreenSizeX = 1680
	theScreenSizeY = 1050
	theOffsetX = -80
	theOffsetY = -60

	# canvas
	posX = (theScreenSizeX - theCanvasSizeX) / 2 + theOffsetX
	posY = (theScreenSizeY - theCanvasSizeY) / 2 + theOffsetY
	c1 = TCanvas('c1', title, posX, posY, theCanvasSizeX, theCanvasSizeY)
	c1.Divide(2, 2)

	c1.cd(1)
	pad1 = TPad('pad1', 'Pad for top left histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad1.Draw()
	c1.cd(2)
	pad2 = TPad('pad2', 'Pad for top right histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad2.Draw()
	c1.cd(3)
	pad3 = TPad('pad1', 'Pad for bottom left histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad3.Draw()
	c1.cd(4)
	pad4 = TPad('pad2', 'Pad for bottom right histogram', 0.03, 0.03, 0.97, 0.97, 0)
	pad4.Draw()

	return [c1, pad1, pad2, pad3, pad4]


# rebin and color a histogram
def formatHistogram(histo, rebinValue=1, fill=None, line=None, fillStyle=None):
	histo.SetDirectory(0)
	histo.Rebin(rebinValue)

	if (fill != None):
		histo.SetFillColor(fill)
		histo.SetMarkerColor(fill)

	if (line != None):
		histo.SetLineColor(line)
	elif (fill != None):
		histo.SetLineColor(fill)

	if (fillStyle == None):
		histo.SetFillStyle(1001)
	else:
		histo.SetFillStyle(fillStyle)


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
			elif "arXiv" in annotation[2]:
				latex.SetTextFont(42) 
				latex.SetTextSize(0.035)
			latex.DrawLatex(*annotation)
			latex.SetTextFont(42)
			latex.SetTextSize(textSize)

def makeAnnotationsGroup(annotationList):
	for (annotation, cfgDict) in annotationList:
		if (not cfgDict.has_key('textSize')):
			cfgDict.update({'textSize': 0.04})
		if (not cfgDict.has_key('color')):
			cfgDict.update({'color': None})
		if (not cfgDict.has_key('align')):
			cfgDict.update({'align': None})

		makeAnnotations(annotation, textSize=cfgDict['textSize'], color=cfgDict['color'], align=cfgDict['align'])


def makeCMSAnnotation(xPos, yPos, luminosity, mcOnly=False, preliminary=True, year=2011, ownWork=False, supplementary= False):
		from ROOT import kBlack, kBlue
		energy = -1
		if (year == 2011):
			energy = 7
		elif (year == 2012):
			energy = 8
		elif (year == 2015 or year == 2016):
			energy = 13

		color = kBlack

		if (mcOnly):
			cmsString = "CMS"
			if not (ownWork):
				cmsExtra = "Simulation"
				annotationsCMS = [
						   (xPos, yPos, cmsString),
						   (xPos, yPos-0.04, cmsExtra),
						   (0.685, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000,energy)),
						   ]
			else:
				cmsExtra = "#splitline{Private Work}{Simulation}"
				annotationsCMS = [
						   (xPos, yPos, cmsString),
						   (xPos, yPos-0.07, cmsExtra),
						   (0.685, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000,energy)),
						   ]

			makeAnnotations(annotationsCMS, color=color)
		else:
			cmsString = "CMS"
			if (preliminary):
				cmsExtra = "Preliminary"
			else:
				cmsExtra = ""
			if (ownWork):
				cmsExtra = "Private Work"

			if (supplementary):
				cmsExtra = "Supplementary"
				arxiveLabel = "arxiv:xxxx.xxxxx"
                                
				annotationsCMS = [
						   (xPos-0.02, 0.965, cmsString),
						   (xPos+0.08, 0.965, cmsExtra),
						   (xPos, yPos-0.02, arxiveLabel),
						   (0.685, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000 ,energy)),
							] 
                        
			else:
				annotationsCMS = [
						   (xPos, yPos, cmsString),
						   (xPos, yPos-0.04, cmsExtra),
						   (0.685, 0.965, "%.1f fb^{-1} (%d TeV)" % (float(luminosity) / 1000 ,energy)),
						   ]            
				

			makeAnnotations(annotationsCMS, color=color)
		   
		   
		   


def myLegend(x1, y1, x2, y2, borderSize=1):
	from ROOT import kWhite
	legend = ROOT.TLegend(x1, y1, x2, y2)
	legend.SetLineWidth(2)
	legend.SetBorderSize(borderSize)
	legend.SetFillColor(kWhite)
	return legend


# JES uncertainty tools
def stringJESConversion(string, up=True):
	JESUncertainty = 0.075
	value = "%s" % string
	if (up):
		log.logInfo("Scaling up: %s" % JESUncertainty)
		value = value.replace("ht", "%f * ht" % (1.0 + JESUncertainty))
		value = value.replace("met", "%f * met" % (1.0 + JESUncertainty))
		value = value.replace("jet1pt", "%f * jet1pt" % (1.0 + JESUncertainty))
		value = value.replace("jet2pt", "%f * jet2pt" % (1.0 + JESUncertainty))
		value = value.replace("jet3pt", "%f * jet3pt" % (1.0 + JESUncertainty))
		value = value.replace("jet4pt", "%f * jet4pt" % (1.0 + JESUncertainty))
	else:
		log.logInfo("Scaling down: %s" % JESUncertainty)
		value = value.replace("ht", "%f * ht" % (1.0 - JESUncertainty))
		value = value.replace("met", "%f * met" % (1.0 - JESUncertainty))
		value = value.replace("jet1pt", "%f * jet1pt" % (1.0 - JESUncertainty))
		value = value.replace("jet2pt", "%f * jet2pt" % (1.0 - JESUncertainty))
		value = value.replace("jet3pt", "%f * jet3pt" % (1.0 - JESUncertainty))
		value = value.replace("jet4pt", "%f * jet4pt" % (1.0 - JESUncertainty))
	log.logDebug("Converting '%s' into '%s'." % (string, value))
	return value

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
	

# next version of data storage
def storeData(project, key, value):
	basePath = "shelves/"
	fileName = "data%s.shelve" % (project)
	filePath = "%s%s" % (basePath, fileName)

	db = shelve.open(filePath)
	db[key] = value
	db.close()

def loadData(project, key):
	basePath = "shelves/"
	fileName = "data%s.shelve" % (project)
	filePath = "%s%s" % (basePath, fileName)

	value = None
	#if (os.path.exists(filePath)):
	if (True):
		db = shelve.open(filePath)
		value = db[key]
		db.close()

	return value

def dataExists(project, key):
	basePath = "shelves/"
	fileName = "data%s.shelve" % (project)
	filePath = "%s%s" % (basePath, fileName)

	value = False
	#if (os.path.exists(filePath)):
	if (True):
		db = shelve.open(filePath)
		value = db.has_key(key)
		db.close()

	return value



def createLatexTable(fileName, content, format={}):
	templateTable = """
\\documentclass[12pt,twoside,a4paper]{article}

\\newcommand{\\MET}{\\ensuremath{\\displaystyle{\\not} E_T~}}
\\newcommand{\\HT}{\\ensuremath{H_T~}}

\\begin{document}
	\\begin{table}
%%        \\tiny
		\\small
		\\begin{tabular}{%(cellformat)s}
			\\hline
			%(header)s
			%(content)s
		\\end{tabular}
		%(caption)s
	\\end{table}
\\end{document}
	"""


	tabMap = {
		'cellformat': "c",
		'header': "",
		'content': "test",
		'caption': ""
		}

	tabContent = None
	nColumns = 1
	noLineBreak = False
	for row in content:
		log.logDebug("row: %s" % row)
		rowContent = None
		hline = False
		for column in row:
			cellContent = str(column)
			if (cellContent == "X-HLINE"):
				hline = True

			# format floats as specified
			if (format.has_key('floatFormat') and isinstance(column, float)):
				cellContent = format['floatFormat'] % column

			if (rowContent == None):
				rowContent = cellContent
			else:
				rowContent += " & " + cellContent

		if (tabContent == None):
			tabContent = rowContent
		else:
			if (not noLineBreak):
				tabContent += "\\\\"

			if (hline):
				tabContent += "\\hline\n            "
				noLineBreak = True
			else:
				tabContent += "\n            " + rowContent
				noLineBreak = False

		if (len(row) > nColumns):
			nColumns = len(row)

	log.logDebug("tabContent: %s" % tabContent)
	#tabContent = tabContent.replace("_", "\\_")
	tabMap.update({'content': tabContent})

	if (format.has_key('cellformat')):
		tabMap.update({'cellformat': format['cellformat']})
	else:
		cellformat = ""
		for i in range(0, nColumns):
			cellformat += "c"
		tabMap.update({'cellformat': cellformat})

	if (format.has_key('header')):
		header = None
		for string in format['header']:
			if (header == None):
				header = "\\textbf{" + string + "}"
			else:
				header = header + " & " + "\\textbf{" + string + "}"
		tabMap.update({'header': header + "\\\\\\hline"})

	if (format.has_key('caption')):
		tabMap.update({'caption': "\\caption{" + format['caption'] + "}"})

	if (format.has_key("fontsize")):
		templateTable = templateTable.replace("\\small", "\\%s" % format['fontsize'])

	file = open(fileName, 'w')
	file.write(templateTable % tabMap)
	file.close()


def createPaveLabel(x1, y1, x2, y2, text,
					fillColor=1, textColor=0,
					textSize=None):

	label = TPaveLabel(0.80, 0.80, 0.97, 0.88,
						   'Peak Fit')
	label.SetFillColor(fillColor)
	label.SetTextColor(textColor)
	label.SetTextFont(52)
	if (textSize != None):
		label.SetTextSize(textSize)

	label.Draw()
	return label



# Color definition
#==================
defineMyColors = {
		'Black' : (0, 0, 0),
		'White' : (255, 255, 255),
		'Red' : (255, 0, 0),
		'DarkRed' : (128, 0, 0),
		'Green' : (0, 255, 0),
		'Blue' : (0, 0, 255),
		'Yellow' : (255, 255, 0),
		'Orange' : (255, 128, 0),
		'DarkOrange' : (255, 64, 0),
		'Magenta' : (255, 0, 255),
		'KDEBlue' : (64, 137, 210),
		'Grey' : (128, 128, 128),
		'DarkGreen' : (0, 128, 0),
		'DarkSlateBlue' : (72, 61, 139),
		'Brown' : (70, 35, 10),

		'MyBlue' : (36, 72, 206),
		'MyDarkBlue' : (18, 36, 103),
		'MyGreen' : (70, 164, 60),
		'AnnBlueTitle' : (29, 47, 126),
		'AnnBlue' : (55, 100, 255),
#        'W11AnnBlue' : (0, 68, 204),
#        'W11AnnBlue' : (63, 122, 240),
	}


myColors = {
	'W11ttbar':  855,
	'W11singlet':  854,
	'W11ZLightJets':  401,
	'W11ZbJets':  400,
	'W11WJets':  842,
	'W11Diboson':  920,
	'W11AnnBlue': 856,
	"Black": ROOT.kBlack,
	"Grey": ROOT.kGray,
	"AnnBlue": ROOT.kBlue,
			}

def createMyColors():
	iIndex = 2000
	containerMyColors = []
	for color in defineMyColors.keys():
		tempColor = ROOT.TColor(iIndex,
			float(defineMyColors[color][0]) / 255, float(defineMyColors[color][1]) / 255, float(defineMyColors[color][2]) / 255)
		containerMyColors.append(tempColor)

		myColors.update({ color: iIndex })
		iIndex += 1

	return containerMyColors

def getTrees(theConfig, datasets):
	import dataInterface
	theDataInterface = dataInterface.DataInterface(theConfig.dataSetPath,theConfig.dataVersion)
	treePathOFOS = "/EMuDileptonTree"
	treePathEE = "/EEDileptonTree"
	treePathMM = "/MuMuDileptonTree"

	treesMCOFOS = ROOT.TList()
	treesMCEE = ROOT.TList()
	treesMCMM = ROOT.TList()
	
	cut = theConfig.selection.cut
	
	for dataset in datasets:
		scale = 0.0

		# dynamic scaling
		jobs = dataInterface.InfoHolder.theDataSamples[theConfig.dataVersion][dataset]
		if (len(jobs) > 1):
			log.logDebug("Scaling and adding more than one job: %s" % (jobs))
		for job in jobs:
			treeMCOFOSraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathOFOS, dataVersion=theConfig.dataVersion, cut=cut)
			treeMCEEraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathEE, dataVersion=theConfig.dataVersion, cut=cut)
			treeMCMMraw = theDataInterface.getTreeFromJob(theConfig.flag, theConfig.task, job, treePathMM, dataVersion=theConfig.dataVersion, cut=cut)

			dynNTotal = theDataInterface.getEventCount(job, theConfig.flag, theConfig.task)
			dynXsection = theDataInterface.getCrossSection(job)
			dynNegWeightFraction = theDataInterface.getNegWeightFraction(job)
			#~ dynScale = dynXsection * theConfig.runRange.lumi / dynNTotal
			print theConfig.runRange.lumi
			dynScale = dynXsection * theConfig.runRange.lumi / (dynNTotal * (1 - 2 * dynNegWeightFraction) )
			if (dynScale != scale):
				log.logInfo("dyn scale for %s (%s): n = %d, x = %f => %f" % (job, dataset, dynNTotal, dynXsection, dynScale))
				scale = dynScale
			else:
				log.logError("No dynamic scale applied. This should never happen!")

			# convert trees
			if not treeMCOFOSraw == None:
				treesMCOFOS.Add(dataInterface.DataInterface.convertDileptonTree(treeMCOFOSraw, weight=scale))
			if not treeMCEEraw == None:
				treesMCEE.Add(dataInterface.DataInterface.convertDileptonTree(treeMCEEraw, weight=scale))
			if not treeMCMMraw == None:
				treesMCMM.Add(dataInterface.DataInterface.convertDileptonTree(treeMCMMraw, weight=scale))
			

	treeMCOFOStotal = ROOT.TTree.MergeTrees(treesMCOFOS)
	treeMCEEtotal = ROOT.TTree.MergeTrees(treesMCEE)
	treeMCMMtotal = ROOT.TTree.MergeTrees(treesMCMM)

	return (treeMCOFOStotal, treeMCEEtotal, treeMCMMtotal)
