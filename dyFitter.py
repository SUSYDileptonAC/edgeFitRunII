#!/usr/bin/env python

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
from ROOT import gROOT, gStyle
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import dataInterface
import tools
import math

parametersToSave  = {}
rootContainer = []

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
#~ 
#~ 
#~ 
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
	from sys import argv
	
	region = "DrellYanControl"
	run = argv[2]
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region=region,runName=run)
	
	useExistingDataset = int(argv[3])		
	
	
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


	
		
	

	if not useExistingDataset:
		w = ROOT.RooWorkspace("w", ROOT.kTRUE)
		inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		getattr(w,'import')(inv)
		w.factory("weight[1.,0.,10.]")
		vars = ROOT.RooArgSet(inv, w.var('weight'))		
		if (theConfig.useMC):
			
			log.logHighlighted("Using MC instead of data.")
			datasets = theConfig.mcdatasets # ["TTJets", "ZJets", "DibosonMadgraph", "SingleTop"]
			if argv[1] == "Central":
				(treeOFOS, treeEE, treeMM) = tools.getTrees(theConfig, datasets,central=True)
			elif argv[1] == "Forward":
				(treeOFOS, treeEE, treeMM) = tools.getTrees(theConfig, datasets,central=False)
			else:
				log.logError("Region must be Central or Forward")
				sys.exit()
			
		else:
			if argv[1] == "Central":
				treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)
				treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)
				treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)

				# convert trees
				treeOFOS = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
				treeEE = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
				treeMM = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
			elif argv[1] == "Forward":	
				treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)
				treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)
				treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)

				# convert trees
				treeOFOS = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
				treeEE = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
				treeMM = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
		
			else:
				log.logError("Region must be Central or Forward")
				sys.exit()



		tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(treeEE), ROOT.RooFit.WeightVar("weight"))
		tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(treeMM), ROOT.RooFit.WeightVar("weight"))
		tmpOFOS = ROOT.RooDataSet("tmpOFOS", "tmpOFOS", vars, ROOT.RooFit.Import(treeOFOS), ROOT.RooFit.WeightVar("weight"))	
		tmpSFOS = tmpMM.Clone()
		tmpSFOS.append(tmpEE.Clone())


		tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(treeEE), ROOT.RooFit.WeightVar("weight"))
		tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(treeMM), ROOT.RooFit.WeightVar("weight"))
		tmpOFOS = ROOT.RooDataSet("tmpOFOS", "tmpOFOS", vars, ROOT.RooFit.Import(treeOFOS), ROOT.RooFit.WeightVar("weight"))
		tmpSFOS = ROOT.RooDataSet("tmpSFOS", "tmpSFOS", vars, ROOT.RooFit.Import(treeMM), ROOT.RooFit.WeightVar("weight"))
		tmpSFOS.append(tmpEE)





		dataEE = ROOT.RooDataSet("%sEE" % ("Data"), "Dataset with invariant mass of ee lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
		dataMM = ROOT.RooDataSet("%sMM" % ("Data"), "Dataset with invariant mass of mm lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))

		dataSFOS = ROOT.RooDataSet("%sSFOS" % ("Data"), "Dataset with invariant mass of SFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
		dataOFOS = ROOT.RooDataSet("%sOFOS" % ("Data"), "Dataset with invariant mass of OFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))
								   

			
		
		getattr(w, 'import')(dataSFOS)
		getattr(w, 'import')(dataOFOS)
		getattr(w, 'import')(dataEE)
		getattr(w, 'import')(dataMM)
		
		
		
		
		histOFOS = createHistoFromTree(treeOFOS,"inv","",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		histEE = createHistoFromTree(treeEE,"inv","",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		histMM = createHistoFromTree(treeMM,"inv","",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		

		eeFrac = dataEE.sumEntries()/(dataEE.sumEntries() + dataMM.sumEntries())
		
		histEE.Add(histOFOS,-1*eeFrac)
		histMM.Add(histOFOS,-1*(1-eeFrac))
		
		dataHistEE = ROOT.RooDataHist("dataHistEE", "dataHistEE", ROOT.RooArgList(w.var('inv')), ROOT.RooFit.Import(histEE))
		dataHistMM = ROOT.RooDataHist("dataHistMM", "dataHistMM", ROOT.RooArgList(w.var('inv')), ROOT.RooFit.Import(histMM))

		getattr(w, 'import')(dataHistEE)
		getattr(w, 'import')(dataHistMM)
		if theConfig.useMC:
			w.writeToFile("workspaces/dyControl_%s_MC.root"%argv[1])
		else:
			w.writeToFile("workspaces/dyControl_%s_Data.root"%argv[1])

	else:
		if theConfig.useMC:
			f = ROOT.TFile("workspaces/dyControl_%s_MC.root"%argv[1])
		else:
			f = ROOT.TFile("workspaces/dyControl_%s_Data.root"%argv[1])
		w =  f.Get("w")		
		vars = ROOT.RooArgSet(w.var("inv"), w.var('weight'))


	histoytitle = 'Events / %.1f GeV' % ((theConfig.maxInv - theConfig.minInv) / float(w.var('inv').getBins()))
	
	ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
	ROOT.gSystem.Load("libFFTW.so") 	
	

	
	w.var('inv').setBins(140)
	

	
	
	# We know the z mass
	# z mass and width
	# mass resolution in electron and muon channels
	w.factory("zmean[91.1876]")
	w.factory("cbmeanMM[3.,-10,10]")
	w.factory("cbmeanEE[3.00727145780911975e+00,-10,10]")
	w.factory("zwidthMM[2.4952]")
	w.factory("zwidthEE[2.4952]")
	
	w.factory("sMM[1.6.,0.,20.]")
	w.factory("BreitWigner::zShapeMM(inv,zmean,zwidthMM)")

	w.factory("sEE[1.61321382563436089e+00,0,20.]")
	w.factory("BreitWigner::zShapeEE(inv,zmean,zwidthEE)")

	w.factory("nMML[3.,0.,20]")
	w.factory("alphaMML[1.15,0,10]")
	w.factory("nMMR[1.,0,20]")
	w.factory("alphaMMR[2.5,0,10]")
	
	w.factory("DoubleCB::cbShapeMM(inv,cbmeanMM,sMM,alphaMML,nMML,alphaMMR,nMMR)")
	

	w.factory("nEEL[2.90366994026457270e+00,0.,20]")
	w.factory("alphaEEL[1.15985663333662714e+00,0,10]")
	w.factory("nEER[1.0,0,100]")
	w.factory("alphaEER[2.50878194343888694e+00,0,10]")
	
	w.factory("DoubleCB::cbShapeEE(inv,cbmeanEE,sEE,alphaEEL,nEEL,alphaEER,nEER)")

	Abkg=ROOT.RooRealVar("Abkg","Abkg",1,0.01,10)
	getattr(w, 'import')(Abkg)
	
	#~ w.var("inv").setBins(250,"cache")
	w.factory("cContinuumEE[%f,%f,%f]" % (-0.02,-0.1,0))
	
	w.factory("nZEE[100000.,500.,%s]" % (1000000))


	w.factory("Exponential::offShellEE(inv,cContinuumEE)")

	convEE = ROOT.RooFFTConvPdf("peakModelEE","zShapeEE (x) cbShapeEE",w.var("inv"),w.pdf("zShapeEE"),w.pdf("cbShapeEE"))
	getattr(w, 'import')(convEE)
	w.pdf("peakModelEE").setBufferFraction(5.0)
	w.factory("zFractionEE[0.9,0,1]")
	expFractionEE = ROOT.RooFormulaVar('expFractionEE', '1-@0', ROOT.RooArgList(w.var('zFractionEE')))
	getattr(w, 'import')(expFractionEE)	
	w.factory("SUM::modelEE1(zFractionEE*peakModelEE,expFractionEE*offShellEE)")
	w.factory("SUM::modelEE(nZEE*modelEE1)")


	w.factory("cContinuumMM[%f,%f,%f]" % (-0.02,-0.1,0))
	w.factory("Exponential::offShellMM(inv,cContinuumMM)")
	
	w.factory("nZMM[100000.,500.,%s]" % (1000000))


	
	convMM = ROOT.RooFFTConvPdf("peakModelMM","zShapeMM (x) cbShapeMM",w.var("inv"),w.pdf("zShapeMM"),w.pdf("cbShapeMM"))
	getattr(w, 'import')(convMM)
	w.pdf("peakModelMM").setBufferFraction(5.0)
	w.factory("zFractionMM[0.9,0,1]")
	expFractionMM = ROOT.RooFormulaVar('expFractionMM', '1-@0', ROOT.RooArgList(w.var('zFractionMM')))
	getattr(w, 'import')(expFractionMM)		
	w.factory("SUM::modelMM1(zFractionMM*peakModelMM,expFractionMM*offShellMM)")
	w.factory("SUM::modelMM(nZMM*modelMM1)")

	
	
	fitEE = w.pdf('modelEE').fitTo(w.data('dataHistEE'),
										#ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(2.0))
										ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kFALSE), ROOT.RooFit.Extended(ROOT.kTRUE))
										
										

		
	fitMM = w.pdf('modelMM').fitTo(w.data('dataHistMM'),
										#ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(2.0))
										ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kTRUE), ROOT.RooFit.Extended(ROOT.kTRUE))
										
										

	w.var("inv").setRange("zPeak",81,101)
	w.var("inv").setRange("fullRange",20,300)
	w.var("inv").setRange("lowMass",20,70)
	argSet = ROOT.RooArgSet(w.var("inv"))

	peakIntEE = w.pdf("peakModelEE").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("zPeak")) 
	peakIntEE2 = w.pdf("offShellEE").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("zPeak"))
	peakEE = peakIntEE.getVal() + peakIntEE2.getVal()
	
	lowMassIntEE = w.pdf("peakModelEE").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("lowMass")) 
	lowMassIntEE2 = w.pdf("offShellEE").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("lowMass"))
	lowMassEE = lowMassIntEE.getVal() + lowMassIntEE2().getVal()
	
	peakIntMM = w.pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("zPeak"))
	peakMM = peakIntMM.getVal()
	
	lowMassIntMM = w.pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(w.var("inv"))), ROOT.RooFit.Range("lowMass"))
	lowMassMM = lowMassIntMM.getVal()
	
	log.logHighlighted( "Peak: %.2f LowMass: %.2f (ee)"%(peakEE,lowMassEE))
	log.logHighlighted( "Peak: %.2f LowMass: %.2f (mm)"%(peakMM,lowMassMM))
	log.logHighlighted( "R(In,Out): %.2f (ee) %.2f (mm)"%(lowMassEE/peakEE,lowMassMM/peakMM))
	


	
	
	yMaximum = 100000

	frameEE = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
	frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
	frameEE.GetYaxis().SetTitle("Events / 2.5 GeV")
	ROOT.RooAbsData.plotOn(w.data('dataHistEE'), frameEE)
	w.pdf('modelEE').plotOn(frameEE)		
	sizeCanvas = 800
	

	cEE = ROOT.TCanvas("ee distribtution", "ee distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cEE.cd()
	pads = formatAndDrawFrame(w,theConfig,frameEE, title="EE", pdf=w.pdf("modelEE"), yMax=0.2*yMaximum)

	
	legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.95)
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



	legend.Draw("same")
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.15, 0.96, "CMS Private Work  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%19.4)	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.5, 0.5, "%s"%theConfig.selection.latex)	
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "expo", w.var('cContinuumEE').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "cbMean", w.var('cbmeanEE').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "nL", w.var('nEEL').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "nR", w.var('nEER').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "alphaL", w.var('alphaEEL').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "alphaR", w.var('alphaEER').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "nZ", w.var('nZEE').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "zFraction", w.var('zFractionEE').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_EE" % argv[1], "s", w.var('sEE').getVal(),basePath="dyShelves/")
	eeName = "fig/expoFitEE_%s"%argv[1]
	cEE.Print(eeName+".pdf")
	cEE.Print(eeName+".root")	
	for pad in pads:
		pad.Close()	
	pads = formatAndDrawFrame(w,theConfig,frameEE, title="EE", pdf=w.pdf("modelEE"), yMax=yMaximum)
	legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.95)
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



	legend.Draw("same")
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.15, 0.96, "CMS Private Work  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%19.4)	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.5, 0.5, "%s"%theConfig.selection.latex)		
	pads[0].SetLogy(1)
	eeName = "fig/expoFitEE_Log_%s"%argv[1]
	cEE.Print(eeName+".pdf")
	cEE.Print(eeName+".root")	
	for pad in pads:
		pad.Close()


	frameMM = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of #mu#mu lepton pairs'))
	frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
	frameMM.GetYaxis().SetTitle("Events / 2.5 GeV")
	ROOT.RooAbsData.plotOn(w.data("dataHistMM"), frameMM)
	w.pdf('modelMM').plotOn(frameMM)		
	sizeCanvas = 800
	
	residualMode = "pull"
	cMM = ROOT.TCanvas("#mu#mu distribtution", "#mu#mu distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cMM.cd()
	pads = formatAndDrawFrame(w,theConfig,frameMM, title="MM", pdf=w.pdf("modelMM"), yMax=0.2*yMaximum)

	
	
	legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.95)
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



	legend.Draw("same")
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.15, 0.96, "CMS Private Work  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%19.4)	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.5, 0.5, "%s"%theConfig.selection.latex)	
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "expo", w.var('cContinuumMM').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "cbMean", w.var('cbmeanMM').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "nL", w.var('nMML').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "nR", w.var('nMMR').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "alphaL", w.var('alphaMML').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "alphaR", w.var('alphaMMR').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "nZ", w.var('nZMM').getVal(),basePath="dyShelves/")
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "zFraction", w.var('zFractionMM').getVal(),basePath="dyShelves/")		
	tools.storeParameter("expofit", "dyExponent_%s_MM" % argv[1], "s", w.var('sMM').getVal(),basePath="dyShelves/")		
	mmName = "fig/expoFitMM_%s"%argv[1]
	cMM.Print(mmName+".pdf")
	cMM.Print(mmName+".root")
	
	for pad in pads:
		pad.Close()	
		
	pads = formatAndDrawFrame(w,theConfig,frameMM, title="MM", pdf=w.pdf("modelMM"), yMax=yMaximum)
	legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.95)
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



	legend.Draw("same")
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.15, 0.96, "CMS Private Work  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%19.4)	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.5, 0.5, "%s"%theConfig.selection.latex)	
	pads[0].SetLogy(1)
	mmName = "fig/expoFitMM_Log_%s"%argv[1]
	cMM.Print(mmName+".pdf")
	cMM.Print(mmName+".root")	
	for pad in pads:
		pad.Close()



	w.writeToFile("dyWorkspace_%s.root" % argv[1])
	return w


main()
