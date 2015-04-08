#!/usr/bin/env python


import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.gROOT.SetBatch(True)

from tools import loadParameter


basePath = "shelves/dicts/"
project = "edgefit"
selection = "SignalInclusive_Combined_Full2012_OTriangle"
m0s = [40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280]
nSigs = {"SignalInclusive":125}
xTitles={
"m0":"m_{ll}^{edge} [GeV]",
"nS":"N_{Signal}"
}



def getEffciency(nominatorHisto, denominatorHisto):
	eff = ROOT.TGraphAsymmErrors(nominatorHisto,denominatorHisto,"w")
	effValue = ROOT.Double(0.)
	blubb = ROOT.Double(0.)
	intttt = eff.GetPoint(0,blubb,effValue)

	result = [nominatorHisto.Integral()/denominatorHisto.Integral(),eff.GetErrorYhigh(0),eff.GetErrorYlow(0)]
	return result

def createColorSpectrum():
	from ROOT import TColor
	from numpy import array
	granularity = 255
	palette = []
	#~ _stops = {"red":(0.00, 0.00, 0.87, 1.00, 0.51,1.),"green":(,0.5),"blue":(0,0,255,0.0)}
	stops = [0.00, 0.34, 0.61, 0.84, 1.00]
	red = [0.00, 0.09, 0.18, 0.09, 0.00]
	green = [0.01, 0.02, 0.39, 0.68, 0.97]
	blue = [0.17, 0.39, 0.62, 0.79, 0.97]
      #~ Double_t stops[nRGBs] = { 0.00, 0.34, 0.61, 0.84, 1.00 };
      #~ Double_t red[nRGBs]   = { 0.00, 0.09, 0.18, 0.09, 0.00 };
      #~ Double_t green[nRGBs] = { 0.01, 0.02, 0.39, 0.68, 0.97 };
      #~ Double_t blue[nRGBs]  = { 0.17, 0.39, 0.62, 0.79, 0.97 };	
	#~ stops = [0.00, 0.34, 0.61, 0.84, 1.00]
	#~ red = [0.00, 0.00, 0.87, 1.00, 0.51]
	#~ green = [0.00, 0.81, 1.00, 0.20, 0.00]
	#~ blue = [0.51, 1.00, 0.12, 0.00, 0.00]
	minStop =0.
	maxStop = 1.
	#~ for name in sorted(_stops.keys(), key=lambda x: _stops[x][3]):
		#~ r, g, b, l = _stops[name]
		#~ red.append(r * 1. / 255.)
		#~ green.append(g * 1. / 255.)
		#~ blue.append(b * 1. / 255.)
		#~ stops.append((l - minStop) * 1. / maxStop)
		#~ legendColors[name] = TColor.GetColor(red[-1], green[-1], blue[-1])
	print stops, red, green, blue
	ROOT.gStyle.SetNumberContours(granularity)
	baseColor = TColor.CreateGradientColorTable(len(stops), array( stops,"d"),
													array(red,"d"), array(green,"d"), array(blue,"d"),
													granularity)
	invertedPalette = []												
	for i in range(0,granularity):
		palette.append(baseColor+i)
	for i in range(1,granularity):
		invertedPalette.append(palette[-i])
	invertedPalette.append(palette[0])	
	print invertedPalette
	ROOT.gStyle.SetPalette(granularity,array(invertedPalette,"i"))												



def loadToysForScan(name,region="SignalInclusive"):
	
	result = {}
	for  i in range(0,len(m0s)):
		#~ if (m0s[i]/2.5)%2 != 0:
			#~ title = "ETHT_MC_Scale1Mo%.1fSignalN%dSFOS"%(m0s[i],nSigs[region])
		#~ else:
		title = "Scale1Mo%dSignalN%d_MC_Triangle_allowNegSignalSFOSCentral"%(m0s[i],nSigs[region])
		parameters = loadParameter(project, "%s_%s"%(selection,title), name, basePath = basePath)
		#~ parametersError = loadParameter(project, "%s-%s"%(region,title), name+"error", basePath = basePath)
		#~ parametersMass = loadParameter(project, "%s-%s"%(region,title), "m0", basePath = basePath)
		#~ parametersChi2 = loadParameter(project, "%s-%s"%(region,title), "chi2", basePath = basePath)
		result[i]=([name,m0s[i], parameters, project, region, title, name])	
	
	
	return result
	
#~ def loadToysForSignalScan(region = "SignalInclusive"):
	#~ 
	#~ result = {}
	#~ 
	#~ name = "nS"
	#~ for  i in range(0,len(m0s)):
			
		#~ title = "Scale1Mo%dSignalN%d_MC_Triangle_allowNegSignalSFOSCentral"%(m0s[i],nSigs[region])
		#~ parameters = loadParameter(project, "%s_%s"%(selection,title), name, basePath = basePath)
		#~ result[i]=([name,m0s[i], parameters, project, region, title, name])	
	#~ 
	#~ 
	#~ return result
def loadToys(label):
	
			

	parameters = {}
	parametersError = {}
	parametersMass = {}
	parametersChi2 = {}
	parametersLogLH0 = {}
	parametersLogLH1 = {}
	parametersRSFOF = {}
	parametersNB = {}
	parametersNBErr = {}
	parametersRandM0 = {}
	
	print "%s_%s"%(selection,label)
	
	parameters.update(loadParameter(project, "%s_%s"%(selection,label), "nS", basePath = basePath))
	parametersError.update(loadParameter(project, "%s_%s"%(selection,label), "nSerror", basePath = basePath))
	parametersNB.update(loadParameter(project, "%s_%s"%(selection,label), "nB", basePath = basePath))
	parametersNBErr.update(loadParameter(project, "%s_%s"%(selection,label), "nBerror", basePath = basePath))
	parametersMass.update(loadParameter(project, "%s_%s"%(selection,label), "m0", basePath = basePath))
	parametersChi2.update(loadParameter(project, "%s_%s"%(selection,label), "chi2", basePath = basePath))
	parametersLogLH0.update(loadParameter(project, "%s_%s"%(selection,label), "minNllH0", basePath = basePath))
	parametersLogLH1.update(loadParameter(project, "%s_%s"%(selection,label), "minNllH1", basePath = basePath))
	parametersRSFOF.update(loadParameter(project, "%s_%s"%(selection,label), "rSFOF", basePath = basePath))
	if "randM0" in label:
		parametersRandM0.update(loadParameter(project, "%s_%s"%(selection,label), "initialM0", basePath = basePath))
		result=([label,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, parametersRSFOF,parametersNB,parametersNBErr,parametersRandM0, project, selection, label])	
	else:
		result=([label,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, parametersRSFOF,parametersNB,parametersNBErr, project, selection, label])	
			
	return result


def plotMassHistograms(hists):
		
		
		means = []
		widths = []
		normMeans = []
		normWidths = []		
		meansFit = []
		widthsFit = []
		normMeansFit = []
		normWidthsFit = []		
		
		fitResults = {"means":means,"widths":widths,"normMeans":normMeans,"normWidths":normWidths,"meansFit":meansFit,"widthsFit":widthsFit,"normMeansFit":normMeansFit,"normWidthsFit":normWidthsFit}
		for index, hist in enumerate(hists):
			
			
			
			gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",0,250,"fitted m_{ll}^{edge}","m0","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False,intVal=40+index*10)
			fitResults["means"].append(hist.GetMean())
			fitResults["widths"].append(hist.GetRMS())
			fitResults["normMeans"].append(hist.GetMean()/m0s[index])
			fitResults["normWidths"].append(hist.GetRMS()/m0s[index])	
			fitResults["meansFit"].append(gaussFits[0].GetParameter(1))
			fitResults["widthsFit"].append(gaussFits[0].GetParameter(2))
			fitResults["normMeansFit"].append(gaussFits[0].GetParameter(1)/m0s[index])
			fitResults["normWidthsFit"].append(gaussFits[0].GetParameter(2)/m0s[index])
				
			
			print fitResults["widthsFit"]
			
		return fitResults	
		
def plotSigHistograms(hists):
		
		
		means = []
		widths = []
		normMeans = []
		normWidths = []		
		meansFit = []
		widthsFit = []
		normMeansFit = []
		normWidthsFit = []		
		
		fitResults = {"means":means,"widths":widths,"normMeans":normMeans,"normWidths":normWidths,"meansFit":meansFit,"widthsFit":widthsFit,"normMeansFit":normMeansFit,"normWidthsFit":normWidthsFit}
		for index, hist in enumerate(hists):
			
			
			
			gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",-100,500,"fitted N_{S}^{Central}","nS","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False)
			
			fitResults["means"].append(hist.GetMean())
			fitResults["widths"].append(hist.GetRMS())
			fitResults["normMeans"].append(hist.GetMean()/m0s[index])
			fitResults["normWidths"].append(hist.GetRMS()/m0s[index])	
			fitResults["meansFit"].append(gaussFits[0].GetParameter(1))
			fitResults["widthsFit"].append(gaussFits[0].GetParameter(2))
			fitResults["normMeansFit"].append(gaussFits[0].GetParameter(1)/m0s[index])
			fitResults["normWidthsFit"].append(gaussFits[0].GetParameter(2)/m0s[index])
				
			
		return fitResults	



def plotToyPlot(hists,color,labels,xMin,xMax,xLabel,varName,plotName,Fit=False,histStyle=True,flipLables=False,intVal=None):
	
	from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TF1, TGraphErrors, TTree
	from numpy import array
	import numpy as n
	
	from setTDRStyle import setTDRStyle
			
		
	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	style.SetTitleYOffset(1.2)

	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()		


	gaussFits = []
	yMax = 0
	if Fit:
		for index, hist in enumerate(hists):
			if intVal==None:
				gaussFits.append(ROOT.TF1("gaussFit%d"%index,"gaus"))
				hist.Fit("gaussFit%d"%index)	
			else:	
				gaussFits.append(ROOT.TF1("gaussFit%d"%index,"gaus",intVal-3,intVal+3))	
				hist.Fit("gaussFit%d"%index,"R")
			gaussFits[index].SetLineColor(color[index])
			
			print hist.GetBinContent(hist.GetMaximumBin())
			if hist.GetBinContent(hist.GetMaximumBin()) > yMax:
				yMax = hist.GetBinContent(hist.GetMaximumBin())
	else:
		for index, hist in enumerate(hists):
			if hist.GetBinContent(hist.GetMaximumBin()) > yMax:
				yMax = hist.GetBinContent(hist.GetMaximumBin())				
	hCanvas.DrawFrame(xMin,0,xMax,yMax+10,"; %s ; %s" %(xLabel,"N_{Fitresults}"))	
	
	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.06)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True)	
	
	
	xLabelPos=0.19
	xLegendMax = 0.4
	if flipLables:
		xLabelPos=0.65
		xLegendMax = 0.9
	
	latex.DrawLatex(0.95, 0.96, "19.5 fb^{-1} (8 TeV)")
	cmsExtra = "#splitline{Private Work}{Simulation}"

	latexCMS.DrawLatex(xLabelPos,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(xLabelPos,yLabelPos,"%s"%(cmsExtra))	
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)

	legend = ROOT.TLegend(xLabelPos,0.5,xLegendMax,0.75)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)	
	

	
	for index, hist in enumerate(hists):
		gaussFit = ROOT.TF1("gaussFit","gaus")	
		if Fit:
			#~ hist.Fit("gaussFit")
			latex.SetTextColor(color[index])
			if varName == "rSFOF":
				latex.DrawLatex(0.7, 0.85-index*0.08, "#splitline{mean: %.3f}{width: %.3f}"%(gaussFits[index].GetParameter(1),gaussFits[index].GetParameter(2)))			
			else:
				latex.DrawLatex(0.7, 0.85-index*0.08, "#splitline{mean: %.2f}{width: %.2f}"%(gaussFits[index].GetParameter(1),gaussFits[index].GetParameter(2)))			
		
		if histStyle:		
			hist.SetMarkerStyle(20)
			hist.SetMarkerSize(0)
			#~ hist.SetLineWidth(2)
			hist.SetMarkerColor(color[index])
			hist.SetLineColor(color[index])
			
			legend.AddEntry(hist,labels[index],"le")
			
			hist.Draw("samehiste")
		else:	
			hist.SetMarkerStyle(20)
			hist.SetMarkerColor(color[index])
			hist.SetLineColor(color[index])
			
			legend.AddEntry(hist,labels[index],"pe")
			
			hist.Draw("samepe")
			
	ROOT.gStyle.SetOptStat(0)
	#ROOT.gStyle.SetOptFit(0)
	if len(hists) > 1:
		legend.Draw("same")

	hCanvas.Print("toyResults/%s_%s.pdf"%(varName,plotName))
	hCanvas.Print("toyResults/%s_%s.root"%(varName,plotName))	
	
	if Fit:
		return gaussFits


def plotGraph(graphs,colors,labels,xMin,xMax,yMin,yMax,xLabel,yLabel,varName,plotName):
	
	from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TF1, TGraphErrors, TTree
	from numpy import array
	import numpy as n
	
	from setTDRStyle import setTDRStyle
			
		
	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	#~ style.SetTitleYOffset(1.2)
	#~ style.SetPadRightMargin(0.15)

	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()		

	hCanvas.DrawFrame(xMin,yMin,xMax,yMax,"; %s ; %s" %(xLabel,yLabel))	

	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.06)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True)	
	
	latex.DrawLatex(0.95, 0.96, "19.5 fb^{-1} (8 TeV)")
	cmsExtra = "#splitline{Private Work}{Simulation}"

	latexCMS.DrawLatex(0.19,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))	
	
	legend = ROOT.TLegend(0.19,0.5,0.4,0.75)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)	
		
	
	for index, graph in enumerate(graphs):
		print index
		graph.SetMarkerColor(colors[index])
		graph.SetMarkerStyle(20+4*index)
		graph.SetLineColor(colors[index])
		if len(labels) > 0:
			if "#pm" in labels[index]:
				legend.AddEntry(graph,labels[index],"pe")
			else:
				legend.AddEntry(graph,labels[index],"p")

		graph.Draw("samepe")
	
	legend.Draw("same")
	hCanvas.Print("toyResults/%s_%s.pdf"%(varName,plotName))
	hCanvas.Print("toyResults/%s_%s.root"%(varName,plotName))		


def plotToyPlot2D(hist,xMin,xMax,yMin,yMax,xLabel,yLabel,varName1,varName2,plotName,showCorr=True,showDiagonal=False,mean=None,log=False):
	
	from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TF1, TGraphErrors, TTree, TLine
	from numpy import array
	import numpy as n
	
	from setTDRStyle import setTDRStyle
			
		
	hCanvas = TCanvas("hCanvas", "Distribution", 1000,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	style.SetTitleYOffset(1.15)
	style.SetPadRightMargin(0.2)
	style.SetPadLeftMargin(0.15)

	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()		


	
			
	if log:
		plotPad.SetLogz()
	plotPad.DrawFrame(xMin,yMin,xMax,yMax,"; %s ; %s ; test" %(xLabel,yLabel))	
	

	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)

	legend = ROOT.TLegend(0.16,0.5,0.4,0.75)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)	
	

	

	createColorSpectrum()	
			
	hist.Draw("samecolz")
	hist.GetZaxis().SetLabelSize(0.05)
	hist.GetZaxis().SetTitleSize(0.05)
	hist.GetZaxis().SetTitleOffset(1.25)
	hist.GetYaxis().SetLabelSize(0.04)
	hist.GetYaxis().SetTitleSize(0.04)
	hist.GetXaxis().SetLabelSize(0.04)
	hist.GetXaxis().SetTitleSize(0.04)
	
	
	if showCorr:
		latex.DrawLatex(0.5, 0.85, "Correlation: %.2f"%(hist.GetCorrelationFactor()))			
	if showDiagonal:
		diagonal = ROOT.TLine(xMin,xMin,yMax,yMax)
		diagonal.SetLineColor(ROOT.kRed+1)
		diagonal.SetLineWidth(2)
		diagonal.SetLineStyle(ROOT.kDashed)
		diagonal.Draw("same")
	if not mean == None:
		mean = ROOT.TLine(mean,yMin,mean,yMax)
		mean.SetLineColor(ROOT.kRed+1)
		mean.SetLineWidth(2)
		mean.SetLineStyle(ROOT.kDashed)
		mean.Draw("same")		
	
	
	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.06)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True)	
	
	latex.DrawLatex(0.85, 0.96, "19.5 fb^{-1} (8 TeV)")
	cmsExtra = "#splitline{Private Work}{Simulation}"

	latexCMS.DrawLatex(0.19,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))		
	
	plotPad.RedrawAxis()

	ROOT.gStyle.SetOptStat(0)
	#ROOT.gStyle.SetOptFit(0)
	hCanvas.Print("toyResults/%svs%s_%s.pdf"%(varName2,varName1,plotName))
	hCanvas.Print("toyResults/%svs%s_%s.root"%(varName2,varName1,plotName))	








def plotPValues(shelves,shelvesFixed,Fit=False,illustrate=False,observedValue=0.,observedValueFixed=0.):
	from ROOT import TH1F, TCanvas, TLegend
	from setTDRStyle import setTDRStyle



	bckgOnlyHist = TH1F("bckgOnlyHist","bckgOnlyHist",50,-1,22)
	bckgOnlyHistFixed = TH1F("bckgOnlyHist","bckgOnlyHist",50,-1,22)
		
	nominatorHist = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	nominatorHistFull = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	denominatorHist = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
	denominatorHistFull = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
		
	nominatorHistFixed = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	nominatorHistFullFixed = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	denominatorHistFixed = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
	denominatorHistFullFixed = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
	
	for index, value in shelves[2].iteritems():
		bckgOnlyHist.Fill(-2*(shelves[7][index]-shelves[6][index]))	
		if shelves[4][index] > 0:
			denominatorHistFull.Fill(0.5)
			if -2*(shelves[7][index]-shelves[6][index]) >= observedValue:
				nominatorHistFull.Fill(0.5)
			if shelves[4][index] < 90 and shelves[4][index] > 0:	
				denominatorHist.Fill(0.5)
				if -2*(shelves[7][index]-shelves[6][index]) >= observedValue:
					nominatorHist.Fill(0.5)
						
	for index, value in shelvesFixed[2].iteritems():
		bckgOnlyHistFixed.Fill(-2*(shelvesFixed[7][index]-shelvesFixed[6][index]))	
		if shelvesFixed[4][index] > 0:
			denominatorHistFullFixed.Fill(0.5)
			if -2*(shelvesFixed[7][index]-shelvesFixed[6][index]) >= observedValueFixed:
				nominatorHistFullFixed.Fill(0.5)
			if shelvesFixed[4][index] < 90 and shelvesFixed[4][index] > 0:	
				denominatorHistFixed.Fill(0.5)
				if -2*(shelvesFixed[7][index]-shelvesFixed[6][index]) >= observedValueFixed:
					nominatorHistFixed.Fill(0.5)
			
	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()


	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()	
	
	chi2Shape = ROOT.TF1("chi2Shape","[1]*TMath::GammaDist(x,[0],0,2)",0,18)
	chi2Shape.SetParameters(1,434)
	chi3Shape = ROOT.TF1("chi2Shape","[1]*TMath::GammaDist(x,[0],0,2)",0,18)
	chi3Shape.SetParameters(1.5,434)
	
	if Fit:
		bckgOnlyHist.Fit("chi2Shape")
	hCanvas.DrawFrame(0,0,22,bckgOnlyHistFixed.GetBinContent(bckgOnlyHistFixed.GetMaximumBin())+40,"; %s ; %s" %("-2#Delta(log(L))","N_{Results}"))	
	if illustrate:
		chi2Shape.SetLineColor(ROOT.kBlue)
		chi3Shape.SetLineColor(ROOT.kBlack)
		chi2Shape.Draw("same")			
		chi3Shape.Draw("same")			
	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.06)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.045)
	latexCMSExtra.SetNDC(True)	
	
	
	xLabelPos=0.19
	
	latex.DrawLatex(0.95, 0.96, "19.5 fb^{-1} (8 TeV)")
	cmsExtra = "#splitline{Private Work}{Simulation}"

	latexCMS.DrawLatex(xLabelPos,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(xLabelPos,yLabelPos,"%s"%(cmsExtra))	

	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	if Fit:
		latex.DrawLatex(0.5, 0.6, "#splitline{fit of #chi^{2} dist., NDF = %.2f}{#chi^{2}/N_{dof} %.2f}"%(chi2Shape.GetParameter(0)*2,chi2Shape.GetChisquare()/chi2Shape.GetNDF()))			
	
	observedLine = ROOT.TLine(observedValue,0,observedValue,bckgOnlyHistFixed.GetBinContent(bckgOnlyHistFixed.GetMaximumBin())+40)
	observedLine.SetLineColor(ROOT.kRed)
	observedLine.SetLineStyle(2)
	if observedValue > 0.:
		observedLine.Draw("same")
	bckgOnlyHist.Draw("samepe")
	bckgOnlyHistFixed.SetMarkerColor(ROOT.kBlue)
	bckgOnlyHistFixed.SetLineColor(ROOT.kBlue)
	bckgOnlyHistFixed.Draw("samepe")
	#~ chi2Shape.Draw("same")
	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptFit(0)
	
	legend = ROOT.TLegend(0.475,0.65,0.925,0.9)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	legend.SetTextFont(42)
	if observedValue > 0.:	
		legend.AddEntry(observedLine,"observed","l")
	if illustrate:
		legend.AddEntry(chi2Shape,"#chi^{2} dist. with 2 d.o.f.","l")
		legend.AddEntry(chi3Shape,"#chi^{2} dist. with 3 d.o.f.","l")
		
	hist = ROOT.TH1F()
	hist.SetLineColor(ROOT.kWhite)
	
	
	pValue = getEffciency(nominatorHist,denominatorHist)
	pValueFull = getEffciency(nominatorHistFull,denominatorHistFull)
	pValueFixed = getEffciency(nominatorHistFixed,denominatorHistFixed)
	pValueFullFixed = getEffciency(nominatorHistFullFixed,denominatorHistFullFixed)
	
	#~ legend.AddEntry(hist,"p-Value low mass: %.3f + %.3f - %.3f (%.2f #sigma)"%(pValue[0],pValue[1],pValue[2], ROOT.TMath.NormQuantile(1.0-pValue[0]/2)))
	legend.AddEntry(bckgOnlyHist,"floating edge","pe")
	if observedValue > 0.:
		legend.AddEntry(hist,"p-Value: %.3f^{+ %.3f}_{- %.3f} (%.2f #sigma)"%(pValueFull[0],pValueFull[1],pValueFull[2],ROOT.TMath.NormQuantile(1.0-pValueFull[0]/2)),"f")	
	legend.AddEntry(bckgOnlyHistFixed,"fixed edge","pe")
	if observedValueFixed > 0.:
		legend.AddEntry(hist,"p-Value: %.3f^{+ %.3f}_{- %.3f} (%.2f #sigma)"%(pValueFullFixed[0],pValueFullFixed[1],pValueFullFixed[2],ROOT.TMath.NormQuantile(1.0-pValueFullFixed[0]/2)),"f")		

	
	legend.Draw("same")
	hCanvas.Print("toyResults/significanceStudy_BackgroundOnly.pdf")
	hCanvas.Print("toyResults/significanceStudy_BackgroundOnly.root")			






def plotScanResults():


	from ROOT import TH1F, TH2F, TTree, TCanvas, TGraphErrors, TGraph
	
	import numpy as n		

		
	m0pkl = loadToysForScan("m0","SignalInclusive")	
	nSpkl = loadToysForScan("nS","SignalInclusive")
	rSFOFpkl = loadToysForScan("rSFOF","SignalInclusive")
	massHists = []
	nSHists = []
	rSFOFHists = []

	

	
	for i in range(0,len(m0s)):
		massHists.append(TH1F("hist_%d"%i,"hist_%d"%i,256,0,256))	
		nSHists.append(TH1F("hist_%d"%i,"hist_%d"%i,50,-100,400))	

	scanHist = TH2F("scanHist","scanHist; fitted m_{ll}^{edge} [GeV]; generated m_{ll}^{edge} [GeV]; N_{results}",int((m0s[-1]+55-25)/2.5),25,m0s[-1]+55,len(m0s),m0s[0]-5,m0s[-1]+5)
	for index, value in m0pkl.iteritems():
		
		m0 = m0s[index]
		
		for index2, value2 in value[2].iteritems():	
				scanHist.Fill(value2,m0)
				massHists[index].Fill(value2)
			
		
	
	
	plotToyPlot2D(scanHist,25,m0s[-1]+55,25,m0s[-1]+5,"fitted m_{ll}^{edge} [GeV]","generated m_{ll}^{edge} [GeV]","fittedM0","generatedM0","signalInjectedN125",showCorr=False,showDiagonal=True,log=False)
	
	
	scanHistSignal = TH2F("scanHist","scanHist; fitted N_{S}^{Central} [GeV]; generated m_{ll}^{edge} [GeV]; N_{results}",50,-100,400,len(m0s),m0s[0]-5,m0s[-1]+5)
	for index, value in nSpkl.iteritems():
		
		m0 = m0s[index]
		
		for index2, value2 in value[2].iteritems():	
				scanHistSignal.Fill(value2,m0)
				nSHists[index].Fill(value2)
			
	
	plotToyPlot2D(scanHistSignal,-100,400,25,m0s[-1]+70,"fitted N_{S}^{Central}","generated m_{ll}^{edge} [GeV]","fittedNS","generatedM0","signalInjectedN125",showCorr=False,mean=125,log=False)
	
	scanHistRSFOF = TH2F("scanHist","scanHist; fitted R_{SF/OF}^{Central}; generated m_{ll}^{edge} [GeV]; N_{results}",80,0.8,1.2,len(m0s),m0s[0]-5,m0s[-1]+5)
	for index, value in rSFOFpkl.iteritems():
		
		m0 = m0s[index]
		
		for index2, value2 in value[2].iteritems():	
				scanHistRSFOF.Fill(value2,m0)
				#~ nSHists[index].Fill(value2)
			
	plotToyPlot2D(scanHistRSFOF,0.8,1.2,25,m0s[-1]+5,"fitted R_{SF/OF}^{Central}","generated m_{ll}^{edge} [GeV]","fittedRSFOF","generatedM0","signalInjectedN125",showCorr=False,mean=1.013,log=False)
	
	
	
	fitResults = plotMassHistograms(massHists)
	

	arrayMeans = n.array(fitResults["means"],"d")
	arrayWidths = n.array(fitResults["widths"],"d")
	arrayNormMeans = n.array(fitResults["normMeans"],"d")
	arrayNormWidths = n.array(fitResults["normWidths"],"d")	
	arrayMeansFit = n.array(fitResults["meansFit"],"d")
	arrayWidthsFit = n.array(fitResults["widthsFit"],"d")
	arrayNormMeansFit = n.array(fitResults["normMeansFit"],"d")
	arrayNormWidthsFit = n.array(fitResults["normWidthsFit"],"d")	
	
	xPos = []
	xPosErr = []
	for i in range(0,len(m0s)):
		xPos.append(m0s[i])
		xPosErr.append(0)
	
	arrayXPos = n.array(xPos,"d")
	arrayXPosErr = n.array(xPosErr,"d")
	
	graph = TGraphErrors(len(m0s),arrayXPos,arrayMeans,arrayXPosErr,arrayWidths) 
	graphFit = TGraphErrors(len(m0s),arrayXPos,arrayMeansFit,arrayXPosErr,arrayWidthsFit) 
	normGraph = TGraphErrors(len(m0s),arrayXPos,arrayNormMeans,arrayXPosErr,arrayNormWidths) 	
	widthGraph = TGraph(len(m0s),arrayXPos,arrayWidths) 	
	widthGraphFit = TGraph(len(m0s),arrayXPos,arrayWidthsFit) 	


	plotGraph([graph,graphFit],[ROOT.kBlack,ROOT.kBlue],["mean #pm RMS","gaussian mean #pm #sigma"],m0s[0]-10,m0s[-1]+10,m0s[0]-10,m0s[-1]+10,"generated m_{ll}^{edge} [GeV]","mean fitted m_{ll}^{edge} [GeV]","meanM0vsGenM0","signalInjectedN125")
	plotGraph([normGraph],[ROOT.kBlack],["RMS"],m0s[0]-10,m0s[-1]+10,0.7,1.3,"generated m_{ll}^{edge} [GeV]","mean fitted / generated  m_{ll}^{edge}","fitvsGenM0Ratio","signalInjectedN125")
	plotGraph([widthGraph,widthGraphFit],[ROOT.kBlack,ROOT.kBlue],["RMS","gaussian #sigma"],m0s[0]-10,m0s[-1]+10,0,15,"generated m_{ll}^{edge} [GeV]","width of m_{ll}^{edge} dist. [GeV]","WidthsvsGenM0Ratio","signalInjectedN125")

	fitResults = plotSigHistograms(nSHists)


	arrayMeans = n.array(fitResults["means"],"d")
	arrayWidths = n.array(fitResults["widths"],"d")
	arrayNormMeans = n.array(fitResults["normMeans"],"d")
	arrayNormWidths = n.array(fitResults["normWidths"],"d")	
	arrayMeansFit = n.array(fitResults["meansFit"],"d")
	arrayWidthsFit = n.array(fitResults["widthsFit"],"d")
	arrayNormMeansFit = n.array(fitResults["normMeansFit"],"d")
	arrayNormWidthsFit = n.array(fitResults["normWidthsFit"],"d")	
	
	xPos = []
	xPosErr = []
	for i in range(0,len(m0s)):
		xPos.append(m0s[i])
		xPosErr.append(0)
	
	arrayXPos = n.array(xPos,"d")
	arrayXPosErr = n.array(xPosErr,"d")
	
	graph = TGraphErrors(len(m0s),arrayXPos,arrayMeans,arrayXPosErr,arrayWidths) 
	graphFit = TGraphErrors(len(m0s),arrayXPos,arrayMeansFit,arrayXPosErr,arrayWidthsFit) 
	normGraph = TGraphErrors(len(m0s),arrayXPos,arrayNormMeans,arrayXPosErr,arrayNormWidths) 	


	plotGraph([graphFit],[ROOT.kBlack],[],m0s[0]-10,m0s[-1]+10,0,300,"generated m_{ll}^{edge} [GeV]","mean fitted N_{S}^{Central} ","meanNSvsGenM0","signalInjectedN125")
	#~ plotGraph(normGraph,m0s[0]-10,m0s[-1]+10,0.7,1.3,"generated m_{ll}^{edge} [GeV]","mean fitted / generated  m_{ll}^{edge}","fitvsGenM0Ratio","signalInjectedN125")



def main():
	from sys import argv

	from ROOT import TH1F, TH2F
	
	
	plotScanResults()
	
	
	listOfScans = ["Scale1Mo70SignalN0_MC_TriangleSFOSCentral","Scale1Mo70SignalN0_MC_Triangle_randM0SFOSCentral","Scale1Mo70SignalN0_FixedEdge_70.0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Down_TriangleSFOSCentral","Scale1Mo70SignalN0_MC_Up_TriangleSFOSCentral","Scale1Mo70SignalN0_MC_Up_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Down_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN125_MC_Triangle_randM0SFOSCentral","Scale1Mo70SignalN125_MC_Triangle_allowNegSignal_randM0SFOSCentral","Scale1Mo70SignalN125_MC_Triangle_Concave_allowNegSignalSFOSCentral","Scale1Mo70SignalN125_MC_Triangle_Convex_allowNegSignalSFOSCentral"]
	names = {"Scale1Mo70SignalN0_MC_TriangleSFOSCentral":"backgroundOnly_m070","Scale1Mo70SignalN0_MC_Triangle_randM0SFOSCentral":"backgroundOnly_m070_randM0","Scale1Mo70SignalN0_FixedEdge_70.0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070Fixed","Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral":"signalInjected_m070nS125","Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig","Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m0150_negSig","Scale1Mo70SignalN0_MC_Down_TriangleSFOSCentral":"backgroundOnly_m070_SystDown","Scale1Mo70SignalN0_MC_Up_TriangleSFOSCentral":"backgroundOnly_m070_SystUp","Scale1Mo70SignalN0_MC_Up_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig_SystUp","Scale1Mo70SignalN0_MC_Down_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig_SystDown","Scale1Mo70SignalN125_MC_Triangle_randM0SFOSCentral":"signalInjected_m070nS125_randM0","Scale1Mo70SignalN125_MC_Triangle_allowNegSignal_randM0SFOSCentral":"signalInjected_m070nS125_randM0_allowNegSig","Scale1Mo70SignalN125_MC_Triangle_Concave_allowNegSignalSFOSCentral":"signalInjected_m070nS125_Concave","Scale1Mo70SignalN125_MC_Triangle_Convex_allowNegSignalSFOSCentral":"signalInjected_m070nS125_Convex"}
	for name in listOfScans:
		label = names[name]			
		pkls = loadToys(name)
		hist = TH1F("","",100,-10,10)
		for index, value in pkls[2].iteritems():
			if not index == "35009d4d" and not index =="28c868c8":
				hist.Fill(value/pkls[3][index])	
		
		
		plotToyPlot([hist],[ROOT.kBlack],[label],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS",label,Fit=True)
		
		
		hist = TH1F("","",80,-200,200)
		for index, value in pkls[2].iteritems():
			hist.Fill(value)	
		plotToyPlot([hist],[ROOT.kBlack],[label],-200,200,"fitted N_{S}","nSPure",label,Fit=False)

			
		
		hist = TH1F("","",100,-10,10)
		for index, value in pkls[6].iteritems():
			if "FixedEdge" in name:
				pvalue = ROOT.TMath.Prob(max(0,-2*(pkls[7][index]-value)), 2)
			else:
				pvalue = ROOT.TMath.Prob(max(0,-2*(pkls[7][index]-value)), 4)
			sigma = ROOT.TMath.NormQuantile(1.0-pvalue/2.0);			
			hist.Fill(sigma)	

		plotToyPlot([hist],[ROOT.kBlack],[label],-10,10,"#sigma from Likelihoods","signif",label,Fit=False)
		
			
		hist = TH1F("","",140,20,300)
		for index, value in pkls[4].iteritems():
				hist.Fill(value)
				
		plotToyPlot([hist],[ROOT.kBlack],[label],30,300,"fitted m_{ll}^{max}","m0",label,Fit=False)
					

				
		hist = TH1F("","",80,0.8,1.2)
		for index, value in pkls[8].iteritems():
				hist.Fill(value)
		plotToyPlot([hist],[ROOT.kBlack],[label],0.8,1.2,"fitted R_{SF/OF}","rSFOF",label,Fit=True)		
				
		hist = TH1F("","",100,2400,3000)
		for index, value in pkls[9].iteritems():
				hist.Fill(value)
		plotToyPlot([hist],[ROOT.kBlack],[label],2400,3000,"fitted N_{B}","nB",label,Fit=True)		
	

		hist = TH2F("bckgOnlyHist","bckgOnlyHist",80,0.8,1.2,20,-10,10)
		for index, value in pkls[2].iteritems():
			if not index == "35009d4d":
				hist.Fill(pkls[8][index],value/pkls[3][index])	
	#~ 
		plotToyPlot2D(hist,0.8,1.2,-10,10,"fitted R_{SF/OF}","fitted N_{S}/#sigma_{N_{S}}","rSFOF","nS",label)


		
	pkls = loadToys("Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral")
	pklsUp = loadToys("Scale1Mo70SignalN0_MC_Up_Triangle_allowNegSignalSFOSCentral")
	pklsDown = loadToys("Scale1Mo70SignalN0_MC_Down_Triangle_allowNegSignalSFOSCentral")
	hist = TH1F("","",50,-10,10)
	histUp = TH1F("","",50,-10,10)
	histDown = TH1F("","",50,-10,10)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value/pkls[3][index])	
	for index, value in pklsUp[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histUp.Fill(value/pklsUp[3][index])	
	for index, value in pklsDown[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histDown.Fill(value/pklsDown[3][index])	
	
	
	plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["mean","+1#sigma","-1#sigma"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS","systShift",Fit=False)
	
	hist = TH1F("","",40,-200,200)
	histUp = TH1F("","",40,-200,200)
	histDown = TH1F("","",40,-200,200)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value)	
	for index, value in pklsUp[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histUp.Fill(value)	
	for index, value in pklsDown[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histDown.Fill(value)	
	
	
	plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["mean","+1#sigma","-1#sigma"],-200,200,"fitted N_{S}","nSPure","systShift",Fit=False)



	hist = TH1F("","",140,20,300)
	histUp = TH1F("","",140,20,300)
	histDown = TH1F("","",140,20,300)
	for index, value in pkls[4].iteritems():
			hist.Fill(value)
	for index, value in pklsUp[4].iteritems():
			histUp.Fill(value)
	for index, value in pklsDown[4].iteritems():
			histDown.Fill(value)
			
	plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["mean","+1#sigma","-1#sigma"],30,300,"fitted m_{ll}^{max}","m0","systShift",Fit=True)
				

			
	hist = TH1F("","",80,0.8,1.2)
	histUp = TH1F("","",80,0.8,1.2)
	histDown = TH1F("","",80,0.8,1.2)
	for index, value in pkls[8].iteritems():
			hist.Fill(value)
	for index, value in pklsUp[8].iteritems():
			histUp.Fill(value)
	for index, value in pklsDown[8].iteritems():
			histDown.Fill(value)
	plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["mean","+1#sigma","-1#sigma"],0.8,1.2,"fitted R_{SF/OF}","rSFOF","systShift",Fit=True)





		
	pkls = loadToys("Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral")
	pklsFixed = loadToys("Scale1Mo70SignalN0_FixedEdge_70.0_MC_Triangle_allowNegSignalSFOSCentral")
	hist = TH1F("","",100,-10,10)
	histFixed = TH1F("","",100,-10,10)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value/pkls[3][index])	
	for index, value in pklsFixed[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histFixed.Fill(value/pklsFixed[3][index])	

	
	
	plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS","floatVsFixed",Fit=True)



	hist = TH1F("","",80,-200,200)
	histFixed = TH1F("","",80,-200,200)

	for index, value in pkls[2].iteritems():
			hist.Fill(value)
	for index, value in pklsFixed[2].iteritems():
			histFixed.Fill(value)
			
			
	plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],-200,200,"fitted N_{S}","nSPure","floatVsFixed",Fit=True)
	
	

	
	
	
	
	hist = TH1F("","",140,20,300)
	histFixed = TH1F("","",140,20,300)

	for index, value in pkls[4].iteritems():
			hist.Fill(value)
	for index, value in pklsFixed[4].iteritems():
			histFixed.Fill(value)
			
			
	plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],30,300,"fitted m_{ll}^{max}","m0","floatVsFixed",Fit=True)
				

			
	hist = TH1F("","",80,0.8,1.2)
	histFixed = TH1F("","",80,0.8,1.2)
	for index, value in pkls[8].iteritems():
			hist.Fill(value)
	for index, value in pklsFixed[8].iteritems():
			histFixed.Fill(value)

	plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],0.8,1.2,"fitted R_{SF/OF}","rSFOF","floatVsFixed",Fit=True)


	plotPValues(pkls,pklsFixed,illustrate=True,Fit=False,observedValue=8.565427984283815,observedValueFixed=8.584575826738728)


	pkls = loadToys("Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral")
	hist = TH1F("","",50,0,10)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value/pkls[3][index])	
				
	plotToyPlot([hist],[ROOT.kBlack],["signal injected"],0,10,"fitted N_{S} / #sigma_{N_{S}}","nS","signalInjected",Fit=True)



	hist = TH1F("","",80,0,400)

	for index, value in pkls[2].iteritems():
			hist.Fill(value)
			
			
	plotToyPlot([hist],[ROOT.kBlack],["signal injected"],0,400,"fitted N_{S}","nSPure","signalInjected",Fit=True)
	
		
	hist = TH1F("","",40,50,90)

	for index, value in pkls[4].iteritems():
			hist.Fill(value)
			
			
	plotToyPlot([hist],[ROOT.kBlack],["signal injected"],50,90,"fitted m_{ll}^{max}","m0","signalInjected",Fit=True)
				

			
	hist = TH1F("","",80,0.8,1.2)
	for index, value in pkls[8].iteritems():
			hist.Fill(value)

	plotToyPlot([hist],[ROOT.kBlack],["signal injected"],0.8,1.2,"fitted R_{SF/OF}","rSFOF","signalInjected",Fit=True)





	pklsNegSig = loadToys("Scale1Mo70SignalN125_MC_Triangle_allowNegSignal_randM0SFOSCentral")
	pkls = loadToys("Scale1Mo70SignalN125_MC_Triangle_randM0SFOSCentral")
	pklsNegSig150 = loadToys("Scale1Mo150SignalN125_MC_Triangle_allowNegSignal_randM0SFOSCentral")
	pkls150 = loadToys("Scale1Mo150SignalN125_MC_Triangle_randM0SFOSCentral")
	pklsBgOnly = loadToys("Scale1Mo70SignalN0_MC_Triangle_randM0SFOSCentral")
	pklsBgOnlyNegSig = loadToys("Scale1Mo70SignalN0_MC_Triangle_allowNegSignal_randM0SFOSCentral")
	
	hist = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)
	histNegSig = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)

	
	for index, value in pkls[4].iteritems():
		if not index == "35009d4d":
			hist.Fill(pkls[11][index],value)	
#~ 
	plotToyPlot2D(hist,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","signalInjectedM70N125")
	for index, value in pklsNegSig[4].iteritems():
		if not index == "35009d4d":
			histNegSig.Fill(pklsNegSig[11][index],value)	
#~ 
	plotToyPlot2D(histNegSig,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","signalInjectedM70N125_NegSig")
	
	hist = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)
	histNegSig = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)

	
	for index, value in pkls150[4].iteritems():
		if not index == "35009d4d":
			hist.Fill(pkls150[11][index],value)	
#~ 
	plotToyPlot2D(hist,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","signalInjectedM150N125")
	for index, value in pklsNegSig150[4].iteritems():
		if not index == "35009d4d":
			histNegSig.Fill(pklsNegSig150[11][index],value)	
#~ 
	plotToyPlot2D(histNegSig,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","signalInjectedM150N125_NegSig")
	
	hist = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)

	
	for index, value in pklsBgOnly[4].iteritems():
		if not index == "35009d4d":
			hist.Fill(pklsBgOnly[11][index],value)	
#~ 
	plotToyPlot2D(hist,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","backgroundOnly_randM0")
	
	hist = TH2F("initialVsFittedHist","initialVsFittedHist",150,0,300,150,0,300)

	
	for index, value in pklsBgOnlyNegSig[4].iteritems():
		if not index == "35009d4d":
			hist.Fill(pklsBgOnlyNegSig[11][index],value)	
#~ 
	plotToyPlot2D(hist,30,300,30,300,"initial value of m_{ll}^{edge}","final value of m_{ll}^{edge}","initialM0","fittedM0","backgroundOnly_randM0_NegSig")







	pkls = loadToys("Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral")
	pklsConcave = loadToys("Scale1Mo70SignalN125_MC_Triangle_Concave_allowNegSignalSFOSCentral")
	pklsConvex = loadToys("Scale1Mo70SignalN125_MC_Triangle_Convex_allowNegSignalSFOSCentral")
	hist = TH1F("","",50,-10,10)
	histConcave = TH1F("","",50,-10,10)
	histConvex = TH1F("","",50,-10,10)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value/pkls[3][index])	
	for index, value in pklsConcave[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histConcave.Fill(value/pklsConcave[3][index])	
	for index, value in pklsConvex[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histConvex.Fill(value/pklsConvex[3][index])	
	
	
	plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],-2,10,"fitted N_{S} / #sigma_{N_{S}}","nS","shapeBias",Fit=True)


	hist = TH1F("","",40,-50,350)
	histConcave = TH1F("","",40,-50,350)
	histConvex = TH1F("","",40,-50,350)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value)	
	for index, value in pklsConcave[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histConcave.Fill(value)	
	for index, value in pklsConvex[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histConvex.Fill(value)	
	
	
	plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],-50,350,"fitted N_{S}","nSPure","shapeBias",Fit=True)



	hist = TH1F("","",140,20,300)
	histConcave = TH1F("","",140,20,300)
	histConvex = TH1F("","",140,20,300)
	for index, value in pkls[4].iteritems():
			hist.Fill(value)
	for index, value in pklsConcave[4].iteritems():
			histConcave.Fill(value)
	for index, value in pklsConvex[4].iteritems():
			histConvex.Fill(value)
			
	plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],30,100,"fitted m_{ll}^{max}","m0","shapeBias",Fit=True)
				

			
	hist = TH1F("","",80,0.8,1.2)
	histConcave = TH1F("","",80,0.8,1.2)
	histConvex = TH1F("","",80,0.8,1.2)
	for index, value in pkls[8].iteritems():
			hist.Fill(value)
	for index, value in pklsConcave[8].iteritems():
			histConcave.Fill(value)
	for index, value in pklsConvex[8].iteritems():
			histConvex.Fill(value)
	plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],0.8,1.2,"fitted R_{SF/OF}","rSFOF","shapeBias",Fit=True)
		


	pkls = loadToys("Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral")
	pklsRand = loadToys("Scale1Mo70SignalN0_MC_Triangle_allowNegSignal_randM0SFOSCentral")


	hist = TH1F("","",50,-10,10)
	histRand = TH1F("","",50,-10,10)
	for index, value in pkls[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value/pkls[3][index])	
	for index, value in pklsRand[2].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histRand.Fill(value/pklsRand[3][index])	

	
	plotToyPlot([hist,histRand],[ROOT.kBlack,ROOT.kRed],["nominal","rand. initial m_{ll}^{edge}"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS","randCompare",Fit=False)

	hist = TH1F("","",70,20,300)
	histRand = TH1F("","",70,20,300)
	for index, value in pkls[4].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			hist.Fill(value)	
	for index, value in pklsRand[4].iteritems():
		if not index == "35009d4d" and not index =="28c868c8":
			histRand.Fill(value)	

	
	plotToyPlot([hist,histRand],[ROOT.kBlack,ROOT.kRed],["nominal","rand. initial m_{ll}^{edge}"],30,300,"fitted m_{ll}^{max}","m0","randCompare",Fit=False,flipLables=True)
	
	

	
main()
