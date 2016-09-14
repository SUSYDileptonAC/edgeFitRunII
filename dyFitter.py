#!/usr/bin/env python

### routine to make the DY fit
### has to be run first since the main fit relies on the shape

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gStyle
from setTDRStyle import setTDRStyle

ROOT.gROOT.SetBatch(True)

from messageLogger import messageLogger as log
import dataInterface
import tools
import math
import argparse	

from corrections import rSFOF, rEEOF, rMMOF

parametersToSave  = {}
rootContainer = []


### get a histogram from the tree
def createHistoFromTree(tree, variable, weight, nBins, firstBin, lastBin, nEvents = -1):
	"""
	tree: tree to create histo from)
	variable: variable to plot (must be a branch of the tree)
	weight: weights to apply (e.g. "var1*(var2 > 15)" will use weights from var1 and cut on var2 > 15
	nBins, firstBin, lastBin: number of bins, first bin and last bin (same as in TH1F constructor)
	nEvents: number of events to process (-1 = all)
	"""
	from ROOT import TH1F
	from random import randint
	from sys import maxint
	if nEvents < 0:
		nEvents = maxint
	#make a random name you could give something meaningfull here,
	#but that would make this less readable
	name = "%x"%(randint(0, maxint))
	result = TH1F(name, "", nBins, firstBin, lastBin)
	result.Sumw2()
	tree.Draw("%s>>%s"%(variable, name), weight, "goff", nEvents)
	return result



	
	
	
def formatAndDrawFrame(ws,theConfig,frame, title, pdf, yMax=0.0):
	# This routine formats the frame and adds the residual plot.
	# Residuals are determined with respect to the given pdf.
	# For simultaneous models, the slice and projection option can be set.

	frame.SetMinimum(5)
	if (yMax > 0.0):
		frame.SetMaximum(yMax)
	frame.GetXaxis().SetRangeUser(theConfig.plotMinInv, theConfig.plotMaxInv)
	frame.GetYaxis().SetRangeUser(5, yMax)
	
	pad = ROOT.TPad("main%s" % (title), "main%s" % (title), 0.01, 0.25, 0.99, 0.99)
	pad.SetNumber(1)
	#~ pad.SetLogy(1)

	pad.Draw()
	resPad = ROOT.TPad("residual%s" % (title), "residual%s" % (title), 0.01, 0.01, 0.99, 0.25)
	resPad.SetNumber(2)
	resPad.Draw()
	
	pad.cd()
	if title == "EE":
		pad.DrawFrame(theConfig.plotMinInv,1,theConfig.plotMaxInv,yMax,";m_{ee} [GeV];Events / 2 GeV")
	else:
		pad.DrawFrame(theConfig.plotMinInv,1,theConfig.plotMaxInv,yMax,";m_{#mu#mu} [GeV];Events / 2 GeV")
	
	pdf.plotOn(frame,ROOT.RooFit.Components("offShell%s"%title),ROOT.RooFit.LineColor(ROOT.kGreen))
	pdf.plotOn(frame,ROOT.RooFit.Components("zShape%s"%title),ROOT.RooFit.LineColor(ROOT.kRed))
	pdf.plotOn(frame,ROOT.RooFit.Components("model%s"%title),ROOT.RooFit.LineColor(ROOT.kBlue))	
	pdf.plotOn(frame)
	frame.GetYaxis().SetTitle("Events / 1 GeV")		
	frame.Draw("same")
	
	
	resPad.cd()
	residualMaxY = 20.
	residualTitle = "data - fit"
	if theConfig.residualMode == "pull":
		residualMaxY = 3.
		residualTitle = "#frac{(data - fit)}{#sigma_{data}}"
	hAxis = resPad.DrawFrame(theConfig.plotMinInv, -residualMaxY, theConfig.plotMaxInv, residualMaxY, ";;%s"%residualTitle)
	resPad.SetGridx()
	resPad.SetGridy()

	zeroLine = ROOT.TLine(theConfig.plotMinInv, 0.0, theConfig.plotMaxInv, 0.0)
	zeroLine.SetLineColor(ROOT.kBlue)
	zeroLine.SetLineWidth(2)
	zeroLine.Draw()
	residuals = None
	if theConfig.residualMode == "pull":
		residuals = frame.pullHist()
	else:
		theConfig.residuals = frame.residHist()
	residuals.Draw("P0")
	hAxis.GetYaxis().SetNdivisions(4, 2, 5)
	hAxis.SetTitleOffset(0.36, "Y")
	hAxis.SetTitleSize(0.18, "Y")
	hAxis.GetXaxis().SetLabelSize(0.1) 
	hAxis.GetYaxis().SetLabelSize(0.12)
	resPad.Update()
	pad.cd()
	

	rootContainer.append([zeroLine])
	return [pad,resPad]	
	



def main():
	
	
	parser = argparse.ArgumentParser(description='edge fitter reloaded.')
	
	parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
						  help="Verbose mode.")
	parser.add_argument("-m", "--mc", action="store_true", dest="mc", default=False,
						  help="use MC, default is to use data.")
	parser.add_argument("-u", "--use", action="store_true", dest="useExisting", default=False,
						  help="use existing datasets from pickle, default is false.")
	parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="DrellYanControl",
						  help="selection which to apply.")
	parser.add_argument("-r", "--runRange", dest="runRange", action="store", default="Run2015_25ns",
						  help="name of run range.")
	parser.add_argument("-x", "--private", action="store_true", dest="private", default=False,
						  help="plot is private work.")		
					
	args = parser.parse_args()	


	useExistingDataset = args.useExisting
	
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region=args.selection,runName=args.runRange,useMC=args.mc)
	
	### CMS labels
	cmsExtra = ""
	if args.private:
		cmsExtra = "Private Work"
		if args.mc:
			cmsExtra = "#splitline{Private Work}{Simulation}"
	elif args.mc:
		cmsExtra = "Simulation"	
	else:
		cmsExtra = "Preliminary"
		
	regions = ["Central","Forward"]



	
	# init ROOT
	gROOT.Reset()
	gROOT.SetStyle("Plain")
	setTDRStyle()
	ROOT.gROOT.SetStyle("tdrStyle")	
	
	
	treePathOFOS = "/EMuDileptonTree"
	treePathEE = "/EEDileptonTree"
	treePathMM = "/MuMuDileptonTree"

	
	# get data
	theDataInterface = dataInterface.DataInterface(theConfig.dataSetPath,theConfig.dataVersion)
	treeOFOS = None
	treeEE = None
	treeMM = None
		
	trees = {}
	histos = {}
	dataHistos = {}
	w = {}
	
	### loop over central+forward
	for region in regions:
	
		### get the datasets if not existing ones are used
		if not useExistingDataset:
			
			### set the workspace
			w[region] = ROOT.RooWorkspace("w_%s"%region, ROOT.kTRUE)
			
			### set variables to be used, inv=mll, weight for PU weight
			weight = ROOT.RooRealVar("weight","weight",1.,0.,10.)
			inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
			
			## this is kind of stupid, but since ROOT 6 getattr(w[region],'import')(inv) does not work any more
			## and RooFit needs another dummy entry to perform correctly e.g. getattr(w[region],'import')(inv, ROOT.RooCmdArg())
			
			getattr(w[region],'import')(inv, ROOT.RooCmdArg())
			w[region].factory("weight[1.,0.,10.]")	
			vars = ROOT.RooArgSet(inv, w[region].var('weight'))
		
			###get trees and convert them		
			if (theConfig.useMC):
				
				log.logHighlighted("Using MC instead of data.")
				datasets = theConfig.mcdatasets
				### for MC the conversion is done in the getTrees routine
				(trees["OFOS_%s"%region],trees["EE_%s"%region],trees["MM_%s"%region]) = tools.getTrees(theConfig, datasets,etaRegion=region)
				
			else:
				trees["OFOSraw_%s"%region] = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion=region)
				trees["EEraw_%s"%region] = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion=region)
				trees["MMraw_%s"%region] = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion=region)
	
				# convert trees
				trees["OFOS_%s"%region] = dataInterface.DataInterface.convertDileptonTree(trees["OFOSraw_%s"%region])
				trees["EE_%s"%region] = dataInterface.DataInterface.convertDileptonTree(trees["EEraw_%s"%region])
				trees["MM_%s"%region] = dataInterface.DataInterface.convertDileptonTree(trees["MMraw_%s"%region])
				
	
			
			histos["OFOS_%s"%region] = createHistoFromTree(trees["OFOS_%s"%region],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
			histos["EE_%s"%region] = createHistoFromTree(trees["EE_%s"%region],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
			histos["MM_%s"%region] = createHistoFromTree(trees["MM_%s"%region],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
			
			
			if theConfig.useMC:
				eeFac = getattr(rEEOF,region.lower()).valMC
				mmFac = getattr(rMMOF,region.lower()).valMC
			else:
				eeFac = getattr(rEEOF,region.lower()).val
				mmFac = getattr(rMMOF,region.lower()).val
			
			histos["EE_%s"%region].Add(histos["OFOS_%s"%region],-1*eeFac)
			histos["MM_%s"%region].Add(histos["OFOS_%s"%region],-1*mmFac)

		
			dataHistos["EE_%s"%region] = ROOT.RooDataHist("dataHistEE%s"%region, "dataHistEE%s"%region, ROOT.RooArgList(w[region].var('inv')), histos["EE_%s"%region])
			dataHistos["MM_%s"%region] = ROOT.RooDataHist("dataHistMM%s"%region, "dataHistMM%s"%region, ROOT.RooArgList(w[region].var('inv')), histos["MM_%s"%region])
	
			getattr(w[region], 'import')(dataHistos["EE_%s"%region], ROOT.RooCmdArg())
			getattr(w[region], 'import')(dataHistos["MM_%s"%region], ROOT.RooCmdArg())
		
			w[region].Print()
			if theConfig.useMC:
				w[region].writeToFile("workspaces/dyControl_%s_MC.root"%region)
			else:
				w[region].writeToFile("workspaces/dyControl_%s_Data.root"%region)

		else:
			if theConfig.useMC:
				f = ROOT.TFile("workspaces/dyControl_%s_MC.root"%region)
			else:
				f = ROOT.TFile("workspaces/dyControl_%s_Data.root"%region)
			w =  f.Get("w")		
			vars = ROOT.RooArgSet(w[region].var("inv"), w[region].var('weight'))


	
		histoytitle = 'Events / %.2f GeV' % ((theConfig.maxInv - theConfig.minInv) / float(w[region].var('inv').getBins()))
		
		ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
		ROOT.gSystem.Load("libFFTW.so")
		
		w[region].var('inv').setBins(140)
		
		### Load the parameters required for the fit into the workspace
		
		# We know the z mass
		# z mass and width
		# mass resolution in electron and muon channels
		w[region].factory("zmean[91.1876]")
		w[region].factory("zwidthMM[2.4952]")
		w[region].factory("zwidthEE[2.4952]")
		
		### Put them into the Breit-Wigner
		w[region].factory("BreitWigner::zShapeMM(inv,zmean,zwidthMM)")
		w[region].factory("BreitWigner::zShapeEE(inv,zmean,zwidthEE)")
		
		### Parameter ranges for the double-sided crystal-ball
		
		### for dimuon
		w[region].factory("cbmeanMM[3.,-10,10]")	
		w[region].factory("sMM[1.6.,0.,20.]")	
		w[region].factory("nMML[3.,0.,20]")
		w[region].factory("alphaMML[1.15,0,10]")
		w[region].factory("nMMR[1.,0,20]")
		w[region].factory("alphaMMR[2.5,0,10]")
		
		w[region].factory("DoubleCB::cbShapeMM(inv,cbmeanMM,sMM,alphaMML,nMML,alphaMMR,nMMR)")
		
	
		### dielectron
		w[region].factory("cbmeanEE[3.,-10,10]")
		w[region].factory("sEE[1.6,0,20.]")
		w[region].factory("nEEL[2.9,0.,20]")
		w[region].factory("alphaEEL[1.16,0,10]")
		w[region].factory("nEER[1.0,0,100]")
		w[region].factory("alphaEER[2.5,0,10]")
		
		w[region].factory("DoubleCB::cbShapeEE(inv,cbmeanEE,sEE,alphaEEL,nEEL,alphaEER,nEER)")
		
		### convolution of Breit-Wigner and Crystal Ball
		convMM = ROOT.RooFFTConvPdf("peakModelMM","zShapeMM (x) cbShapeMM",w[region].var("inv"),w[region].pdf("zShapeMM"),w[region].pdf("cbShapeMM"))
		getattr(w[region], 'import')(convMM, ROOT.RooCmdArg())
		convEE = ROOT.RooFFTConvPdf("peakModelEE","zShapeEE (x) cbShapeEE",w[region].var("inv"),w[region].pdf("zShapeEE"),w[region].pdf("cbShapeEE"))
		getattr(w[region], 'import')(convEE, ROOT.RooCmdArg())	
	
		#~ Abkg=ROOT.RooRealVar("Abkg","Abkg",1,0.01,10)
		#~ getattr(w[region], 'import')(Abkg, ROOT.RooCmdArg())
		
		### Exponential for the continuum	
		w[region].factory("cContinuumMM[%f,%f,%f]" % (-0.02,-0.1,0))
		w[region].factory("nZMM[100000.,500.,%s]" % (2000000))
		w[region].factory("Exponential::offShellMM(inv,cContinuumMM)")
		
		w[region].factory("cContinuumEE[%f,%f,%f]" % (-0.02,-0.1,0))
		w[region].factory("nZEE[100000.,500.,%s]" % (2000000))	
		w[region].factory("Exponential::offShellEE(inv,cContinuumEE)")
	
		
		w[region].pdf("peakModelMM").setBufferFraction(5.0)
		w[region].pdf("peakModelEE").setBufferFraction(5.0)
		
		### Fraction of onZ and continuum events
		w[region].factory("zFractionMM[0.9,0,1]")
		w[region].factory("zFractionEE[0.9,0,1]")
		expFractionMM = ROOT.RooFormulaVar('expFractionMM', '1-@0', ROOT.RooArgList(w[region].var('zFractionMM')))	
		expFractionEE = ROOT.RooFormulaVar('expFractionEE', '1-@0', ROOT.RooArgList(w[region].var('zFractionEE')))
		getattr(w[region], 'import')(expFractionMM, ROOT.RooCmdArg())
		getattr(w[region], 'import')(expFractionEE, ROOT.RooCmdArg())
		
		### Take the sum of peak and exponential and an overall normalization
		### Only the normalization is varied in the full edge fit afterwards
		w[region].factory("SUM::modelMM1(zFractionMM*peakModelMM,expFractionMM*offShellMM)")
		w[region].factory("SUM::modelMM(nZMM*modelMM1)")	
		w[region].factory("SUM::modelEE1(zFractionEE*peakModelEE,expFractionEE*offShellEE)")
		w[region].factory("SUM::modelEE(nZEE*modelEE1)")
		
		### ranges to compare different regions
		w[region].var("inv").setRange("zPeak",81,101)
		w[region].var("inv").setRange("fullRange",20,300)
		w[region].var("inv").setRange("lowMass",20,70)
		argSet = ROOT.RooArgSet(w[region].var("inv"))	
		
		### maximum and size for the frame
		yMaximum = 1000000
		sizeCanvas = 800
		
		### legend
		legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.93)
		legend.SetFillStyle(0)
		legend.SetBorderSize(0)
		entryHist = ROOT.TH1F()
		entryHist.SetFillColor(ROOT.kWhite)
		legend.AddEntry(entryHist,"Drell-Yan enriched region","h")	
		dataHist = ROOT.TH1F()
		entryHist.SetFillColor(ROOT.kWhite)
		legend.AddEntry(dataHist,"data","p")	
		fitHist = ROOT.TH1F()
		fitHist.SetLineColor(ROOT.kBlue)
		legend.AddEntry(fitHist, "Full Z model","l")	
		expoHist = ROOT.TH1F()
		expoHist.SetLineColor(ROOT.kGreen)
		legend.AddEntry(expoHist,"Exponential component","l")	
		bwHist = ROOT.TH1F()
		bwHist.SetLineColor(ROOT.kRed)
		legend.AddEntry(bwHist,"DSCB #otimes BW component","l")
		
		### labels
		latex = ROOT.TLatex()
		latex.SetTextFont(42)
		latex.SetNDC(True)
		latex.SetTextAlign(31)
		latex.SetTextSize(0.04)
		latexCMS = ROOT.TLatex()
		latexCMS.SetTextFont(61)
		latexCMS.SetTextSize(0.06)
		latexCMS.SetNDC(True)
		latexCMSExtra = ROOT.TLatex()
		latexCMSExtra.SetTextFont(52)
		latexCMSExtra.SetTextSize(0.045)
		latexCMSExtra.SetNDC(True)
		
		if "Simulation" in cmsExtra:
			yLabelPos = 0.81	
		else:
			yLabelPos = 0.84
	
		fitEE = w[region].pdf('modelEE').fitTo(w[region].data("dataHistEE%s"%region),
										ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kFALSE), ROOT.RooFit.Extended(ROOT.kTRUE))
										

		fitMM = w[region].pdf('modelMM').fitTo(w[region].data("dataHistMM%s"%region),
										ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kTRUE), ROOT.RooFit.Extended(ROOT.kTRUE))
										

		peakIntEE = w[region].pdf("modelEE").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak")) 
		peakEE = peakIntEE.getVal()
		
		lowMassIntEE = w[region].pdf("modelEE").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass")) 
		lowMassEE = lowMassIntEE.getVal()
		
		peakIntMM = w[region].pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak"))
		peakMM = peakIntMM.getVal()
		
		lowMassIntMM = w[region].pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		lowMassMM = lowMassIntMM.getVal()
	
		log.logHighlighted( "Peak: %.3f LowMass: %.3f (ee)"%(peakEE,lowMassEE))
		log.logHighlighted( "Peak: %.3f LowMass: %.3f (mm)"%(peakMM,lowMassMM))
		log.logHighlighted( "R(out,in): %.3f (ee) %.3f (mm)"%(lowMassEE/peakEE,lowMassMM/peakMM))
		
		### dielectron

		frameEE = w[region].var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
		frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
		frameEE.GetYaxis().SetTitle("Events / 2.5 GeV")
		ROOT.RooAbsData.plotOn(w[region].data("dataHistEE%s"%region), frameEE)
		w[region].pdf('modelEE').plotOn(frameEE)		

		### make plots
		
		cEE = ROOT.TCanvas("ee distribtution", "ee distribution", sizeCanvas, int(1.25 * sizeCanvas))
		cEE.cd()
			
		pads = formatAndDrawFrame(w[region],theConfig,frameEE, title="EE", pdf=w[region].pdf("modelEE"), yMax=yMaximum)
	
		legend.Draw("same")

		latex.DrawLatex(0.95, 0.96, "%s fb^{-1} (13 TeV)"%theConfig.runRange.printval)			

		latexCMS.DrawLatex(0.19,0.88,"CMS")
	
		latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))		
		
		pads[0].SetLogy(1)
		eeName = "fig/expoFitEE_%s_%s"%(region,args.runRange)
		if theConfig.useMC:
			eeName = "fig/expoFitEE_%s_%s_MC"%(region,args.runRange)	
		cEE.Print(eeName+".pdf")
		for pad in pads:
			pad.Close()


		### dimuon
	
		frameMM = w[region].var('inv').frame(ROOT.RooFit.Title('Invariant mass of #mu#mu lepton pairs'))
		frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
		frameMM.GetYaxis().SetTitle("Events / 2.5 GeV")
		ROOT.RooAbsData.plotOn(w[region].data("dataHistMM%s"%region), frameMM)
		w[region].pdf('modelMM').plotOn(frameMM)
	

		cMM = ROOT.TCanvas("#mu#mu distribtution", "#mu#mu distribution", sizeCanvas, int(1.25 * sizeCanvas))
		cMM.cd()
				
		pads = formatAndDrawFrame(w[region],theConfig,frameMM, title="MM", pdf=w[region].pdf("modelMM"), yMax=yMaximum)

		legend.Draw("same")

		latex.DrawLatex(0.95, 0.96, "%s fb^{-1} (13 TeV)"%theConfig.runRange.printval)				

		latexCMS.DrawLatex(0.19,0.88,"CMS")	
	
		latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))		
	
		pads[0].SetLogy(1)
		mmName = "fig/expoFitMM_%s_%s"%(region,args.runRange)
		if theConfig.useMC:
			mmName = "fig/expoFitMM_%s_%s_MC"%(region,args.runRange)
		
		cMM.Print(mmName+".pdf")
		for pad in pads:
			pad.Close()
		
		### store parameters to use them in the edge fit later on
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "expo", w[region].var('cContinuumEE').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "cbMean", w[region].var('cbmeanEE').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "nL", w[region].var('nEEL').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "nR", w[region].var('nEER').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "alphaL", w[region].var('alphaEEL').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "alphaR", w[region].var('alphaEER').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "nZ", w[region].var('nZEE').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "zFraction", w[region].var('zFractionEE').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_EE" % region, "s", w[region].var('sEE').getVal(),basePath="dyShelves/")	
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "expo", w[region].var('cContinuumMM').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "cbMean", w[region].var('cbmeanMM').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "nL", w[region].var('nMML').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "nR", w[region].var('nMMR').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "alphaL", w[region].var('alphaMML').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "alphaR", w[region].var('alphaMMR').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "nZ", w[region].var('nZMM').getVal(),basePath="dyShelves/")
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "zFraction", w[region].var('zFractionMM').getVal(),basePath="dyShelves/")		
		tools.storeParameter("expofit", "dyExponent_%s_MM" % region, "s", w[region].var('sMM').getVal(),basePath="dyShelves/")	
	
	
		if theConfig.useMC:
			w[region].writeToFile("workspaces/dyWorkspace_%s_MC.root" % region)
		else:
			w[region].writeToFile("workspaces/dyWorkspace_%s.root" % region)
			
		
	
	return w["Central"],w["Forward"]


main()
