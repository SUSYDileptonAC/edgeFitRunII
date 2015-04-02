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
m0s = [40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
nSigs = {"SignalInclusive":125}
xTitles={
"m0":"m_{ll}^{edge} [GeV]",
"nS":"N_{Signal}"
}

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
	result=([label,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, parametersRSFOF,parametersNB,parametersNBErr, project, selection, label])	
			
	return result


def plotMassHistograms(hists):
		
		
		means = []
		widths = []
		normMeans = []
		normWidths = []		
		
		fitResults = {"means":means,"widths":widths,"normMeans":normMeans,"normWidths":normWidths}
		for index, hist in enumerate(hists):
			
			
			
			gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",0,250,"fitted m_{ll}^{edge}","m0","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False)
			
			fitResults["means"].append(gaussFits[0].GetParameter(1))
			fitResults["widths"].append(gaussFits[0].GetParameter(2))
			fitResults["normMeans"].append(gaussFits[0].GetParameter(1)/m0s[index])
			fitResults["normWidths"].append(gaussFits[0].GetParameter(2)/m0s[index])
				
			
		return fitResults	
		
def plotSigHistograms(hists):
		
		
		means = []
		widths = []
		normMeans = []
		normWidths = []		
		
		fitResults = {"means":means,"widths":widths,"normMeans":normMeans,"normWidths":normWidths}
		for index, hist in enumerate(hists):
			
			
			
			gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",-100,500,"fitted N_{S}^{Central}","nS","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False)
			
			fitResults["means"].append(gaussFits[0].GetParameter(1))
			fitResults["widths"].append(gaussFits[0].GetParameter(2))
			fitResults["normMeans"].append(gaussFits[0].GetParameter(1)/m0s[index])
			fitResults["normWidths"].append(gaussFits[0].GetParameter(2)/m0s[index])
				
			
		return fitResults	



def plotToyPlot(hists,color,labels,xMin,xMax,xLabel,varName,plotName,Fit=False,histStyle=True):
	
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
			gaussFits.append(ROOT.TF1("gaussFit%d"%index,"gaus"))	
			gaussFits[index].SetLineColor(color[index])
			hist.Fit("gaussFit%d"%index)
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
	
	latex.DrawLatex(0.95, 0.96, "19.5 fb^{-1} (8 TeV)")
	cmsExtra = "#splitline{Private Work}{Simulation}"

	latexCMS.DrawLatex(0.19,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))	
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)

	legend = ROOT.TLegend(0.16,0.5,0.4,0.75)
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
			hist.SetLineWidth(2)
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


def plotGraph(graph,xMin,xMax,yMin,yMax,xLabel,yLabel,varName,plotName):
	
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
		
	graph.Draw("samepe")
	
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
	
	
	
	
	plotPad.RedrawAxis()

	ROOT.gStyle.SetOptStat(0)
	#ROOT.gStyle.SetOptFit(0)
	hCanvas.Print("toyResults/%svs%s_%s.pdf"%(varName2,varName1,plotName))
	hCanvas.Print("toyResults/%svs%s_%s.root"%(varName2,varName1,plotName))	


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
	
	xPos = []
	xPosErr = []
	for i in range(0,len(m0s)):
		xPos.append(m0s[i])
		xPosErr.append(0)
	
	arrayXPos = n.array(xPos,"d")
	arrayXPosErr = n.array(xPosErr,"d")
	
	graph = TGraphErrors(len(m0s),arrayXPos,arrayMeans,arrayXPosErr,arrayWidths) 
	normGraph = TGraphErrors(len(m0s),arrayXPos,arrayNormMeans,arrayXPosErr,arrayNormWidths) 	
	widthGraph = TGraph(len(m0s),arrayXPos,arrayWidths) 	


	plotGraph(graph,m0s[0]-10,m0s[-1]+10,m0s[0]-10,m0s[-1]+10,"generated m_{ll}^{edge} [GeV]","mean fitted m_{ll}^{edge} [GeV]","meanM0vsGenM0","signalInjectedN125")
	plotGraph(normGraph,m0s[0]-10,m0s[-1]+10,0.7,1.3,"generated m_{ll}^{edge} [GeV]","mean fitted / generated  m_{ll}^{edge}","fitvsGenM0Ratio","signalInjectedN125")
	plotGraph(widthGraph,m0s[0]-10,m0s[-1]+10,0,15,"generated m_{ll}^{edge} [GeV]","width of m_{ll}^{edge} distribution","WidthsvsGenM0Ratio","signalInjectedN125")

	fitResults = plotSigHistograms(nSHists)


	arrayMeans = n.array(fitResults["means"],"d")
	arrayWidths = n.array(fitResults["widths"],"d")
	arrayNormMeans = n.array(fitResults["normMeans"],"d")
	arrayNormWidths = n.array(fitResults["normWidths"],"d")	
	
	xPos = []
	xPosErr = []
	for i in range(0,len(m0s)):
		xPos.append(m0s[i])
		xPosErr.append(0)
	
	arrayXPos = n.array(xPos,"d")
	arrayXPosErr = n.array(xPosErr,"d")
	
	graph = TGraphErrors(len(m0s),arrayXPos,arrayMeans,arrayXPosErr,arrayWidths) 
	normGraph = TGraphErrors(len(m0s),arrayXPos,arrayNormMeans,arrayXPosErr,arrayNormWidths) 	


	plotGraph(graph,m0s[0]-10,m0s[-1]+10,0,300,"generated m_{ll}^{edge} [GeV]","mean fitted N_{S}^{Central} ","meanNSvsGenM0","signalInjectedN125")
	#~ plotGraph(normGraph,m0s[0]-10,m0s[-1]+10,0.7,1.3,"generated m_{ll}^{edge} [GeV]","mean fitted / generated  m_{ll}^{edge}","fitvsGenM0Ratio","signalInjectedN125")



def main():
	from sys import argv

	from ROOT import TH1F, TH2F
	
	
	plotScanResults()
	
	
	listOfScans = ["Scale1Mo70SignalN0_MC_TriangleSFOSCentral","Scale1Mo70SignalN0_FixedEdge_70.0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Down_TriangleSFOSCentral","Scale1Mo70SignalN0_MC_Up_TriangleSFOSCentral","Scale1Mo70SignalN0_MC_Up_Triangle_allowNegSignalSFOSCentral","Scale1Mo70SignalN0_MC_Down_Triangle_allowNegSignalSFOSCentral"]
	names = {"Scale1Mo70SignalN0_MC_TriangleSFOSCentral":"backgroundOnly_m070","Scale1Mo70SignalN0_FixedEdge_70.0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070Fixed","Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral":"signalInjected_m070nS125","Scale1Mo70SignalN0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig","Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m0150_negSig","Scale1Mo70SignalN0_MC_Down_TriangleSFOSCentral":"backgroundOnly_m070_SystDown","Scale1Mo70SignalN0_MC_Up_TriangleSFOSCentral":"backgroundOnly_m070_SystUp","Scale1Mo70SignalN0_MC_Up_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig_SystUp","Scale1Mo70SignalN0_MC_Down_Triangle_allowNegSignalSFOSCentral":"backgroundOnly_m070_negSig_SystDown"}
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















		

	
	
main()
