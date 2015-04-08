#!/usr/bin/env python


import ROOT
from tools import loadParameter


basePath = "shelves/dicts/"
project = "edgefit"
m0s = [30.,32.5,35,37.5,40,42.5,45,47.5,50,52.5,55,57.5,60.,62.5,65.,67.5,70,72.5,75,77.5,80,82.5,85,87.5,90,92.5,95,97.5,100,102.5,105,107.5,110,112.5,115,117.5,120,122.5,125,127.5,130,132.5,135,137.5,140,142.5,145,147.5,150]
nSigs = {"SignalHighMET":66,"SignalNonRectCentral":100}
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



def loadToysForMassScan(region = "SignalHighMET"):
	
	result = {}
	
	name = "m0"
	for  i in range(0,len(m0s)):
		if (m0s[i]/2.5)%2 != 0:
			title = "MarcoAndreaT_MC_Scale1Mo%.1fSignalN%dSFOS"%(m0s[i],nSigs[region])
		else:
			title = "MarcoAndreaT_MC_Scale1Mo%dSignalN%dSFOS"%(m0s[i],nSigs[region])
			
		print title 
		parameters = loadParameter(project, "%s-%s"%(region,title), name, basePath = basePath)
		#~ parametersError = loadParameter(project, "%s-%s"%(region,title), name+"error", basePath = basePath)
		#~ parametersMass = loadParameter(project, "%s-%s"%(region,title), "m0", basePath = basePath)
		#~ parametersChi2 = loadParameter(project, "%s-%s"%(region,title), "chi2", basePath = basePath)
		result[i]=([name,m0s[i], parameters, project, region, title, name])	
		print result[i]
	
	
	return result
	
def loadToysForSignalScan(region = "SignalHighMET"):
	
	result = {}
	
	name = "nS"
	for  i in range(0,len(m0s)):
		if (m0s[i]/2.5)%2 != 0:
			title = "MarcoAndreaT_MC_Scale1Mo%.1fSignalN%dSFOS"%(m0s[i],nSigs[region])
		else:
			title = "MarcoAndreaT_MC_Scale1Mo%dSignalN%dSFOS"%(m0s[i],nSigs[region])
			
		print title 
		parameters = loadParameter(project, "%s-%s"%(region,title), name, basePath = basePath)
		#~ parametersError = loadParameter(project, "%s-%s"%(region,title), name+"error", basePath = basePath)
		#~ parametersMass = loadParameter(project, "%s-%s"%(region,title), "m0", basePath = basePath)
		#~ parametersChi2 = loadParameter(project, "%s-%s"%(region,title), "chi2", basePath = basePath)
		result[i]=([name,m0s[i], parameters, project, region, title, name])	
		print result[i]
	
	
	return result
def loadToysForBackgroundOnly(region = "SignalHighMET"):
	
		
	name = "nS"	
	#~ titles = ["OldT_MC_Scale1Mo40SignalN0_toyBlock1SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock1SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock2SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock3SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock4SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock5SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock6SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock7SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock8SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock9SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock10SFOSCentral"]
	titles = ["OldT_MC_Scale1Mo40SignalN0_toyBlock2SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock3SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock4SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock5SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock6SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock7SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock8SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock9SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock10SFOSCentral"]
	#~ titles = ["OldT_MC_Scale1Mo40SignalN0_toyBlock2SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock3SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock4SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock5SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock6SFOSCentral","OldT_MC_Scale1Mo40SignalN0_toyBlock7SFOSCentral"]
		
	parameters = {}
	parametersError = {}
	parametersMass = {}
	parametersChi2 = {}
	parametersLogLH0 = {}
	parametersLogLH1 = {}
	
	for title in titles:
			parameters.update(loadParameter(project, "%s-%s"%(region,title), name, basePath = basePath))
			parametersError.update(loadParameter(project, "%s-%s"%(region,title), name+"error", basePath = basePath))
			parametersMass.update(loadParameter(project, "%s-%s"%(region,title), "m0", basePath = basePath))
			parametersChi2.update(loadParameter(project, "%s-%s"%(region,title), "chi2", basePath = basePath))
			parametersLogLH0.update(loadParameter(project, "%s-%s"%(region,title), "minNllH0", basePath = basePath))
			parametersLogLH1.update(loadParameter(project, "%s-%s"%(region,title), "minNllH1", basePath = basePath))
	result=([name,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, project, region, title, name])	
	
	print result
		
	return result
	

def plotMassHistograms(canvas,hists,trees):
		
		
		means = []
		widths = []
		normMeans = []
		normWidths = []		
		
		fitResults = {"means":means,"widths":widths,"normMeans":normMeans,"normWidths":normWidths}
		for index, hist in enumerate(hists):
			
			
			canvas.Clear()
			plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
			plotPad.UseCurrentStyle()
			plotPad.Draw()	
			plotPad.cd()	
			canvas.DrawFrame(0,0,250,hist.GetBinContent(hist.GetMaximumBin())+40,"; %s ; %s" %("fitted m_{ll}^{egde}","N_{results}"))	

			#~ gaussFit = TF1("gaussFit","gaus",value[1]-35,value[1]+35)	
			gaussFit = ROOT.TF1("gaussFit","gaus")	
			hist.Fit("gaussFit")
			#~ gaussFit.SetParLimits(0, 1, 1)
			#~ gaussFit.SetParameter(1,value[1])
			#~ tree.UnbinnedFit("gaussFit","var","","EM")

			fitResults["means"].append(gaussFit.GetParameter(1))
			fitResults["widths"].append(gaussFit.GetParameter(2))
			fitResults["normMeans"].append(gaussFit.GetParameter(1)/m0s[index])
			fitResults["normWidths"].append(gaussFit.GetParameter(2)/m0s[index])
				
		

			legend = ROOT.TLegend(0.6, 0.6, 0.95, 0.90)
			legend.SetFillStyle(0)
			legend.SetBorderSize(0)
			legend.AddEntry(hist,"High E_{T}^{miss} Inclusive","l")
			ROOT.gStyle.SetOptStat(0)
			#legend.Draw("same")
			latex = ROOT.TLatex()
			latex.SetTextSize(0.04)
			latex.SetNDC(True)
			latex.DrawLatex(0.15, 0.96, "CMS Simulation  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%9.2)	
			latex = ROOT.TLatex()
			latex.SetTextSize(0.04)
			latex.SetNDC(True)
			latex.DrawLatex(0.5, 0.6, "mean: %.2f width: %.2f"%(gaussFit.GetParameter(1),gaussFit.GetParameter(2)))			
			

			hist.Draw("samepe")
			ROOT.gStyle.SetOptStat(0)
			#ROOT.gStyle.SetOptFit(0)
			canvas.Print("m0_Toys_%.1f.pdf"%(m0s[index]))
			canvas.Print("m0_Toys_%.1f.root"%(m0s[index]))	
			
		return fitResults	

def main():
	from sys import argv
	from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TF1, TGraphErrors, TTree
	from numpy import array
	import numpy as n
	
	from setTDRStyle import setTDRStyle
	region = "SignalNonRectCombinedConstrained"
			
		
	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()	
			

	#~ result=([name,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, project, region, title, name])	
		

				
	bckgOnlyPkl = loadToysForBackgroundOnly(region)
	bckgOnlyHist = TH1F("bckgOnlyHist","bckgOnlyHist",50,-1,22)
	nTest = 0
	nTestLarger = 0
	
	nominatorHist = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	nominatorHistFull = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
	denominatorHist = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
	denominatorHistFull = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
	
	for index, value in bckgOnlyPkl[2].iteritems():
		if not index == "38ed30c9":
			if bckgOnlyPkl[4][index] > 0:
				denominatorHistFull.Fill(0.5)
				if -2*(bckgOnlyPkl[7][index]-bckgOnlyPkl[6][index]) >= 2*4.3808:
					nominatorHistFull.Fill(0.5)
				if bckgOnlyPkl[4][index] < 90 and bckgOnlyPkl[4][index] > 0:	
					bckgOnlyHist.Fill(-2*(bckgOnlyPkl[7][index]-bckgOnlyPkl[6][index]))	
					nTest = nTest+1
					denominatorHist.Fill(0.5)
					if -2*(bckgOnlyPkl[7][index]-bckgOnlyPkl[6][index]) >= 2*4.3808:
						nTestLarger = nTestLarger + 1
						nominatorHist.Fill(0.5)
	print nTest, nTestLarger
			
	hCanvas.Clear()
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)	
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()	
	hCanvas.DrawFrame(-1,0,18,bckgOnlyHist.GetBinContent(bckgOnlyHist.GetMaximumBin())+20,"; %s ; %s" %("-2*(log(L_{1})-log(L_{0}))","N_{Results}"))	
	chi2Shape = ROOT.TF1("chi2Shape","[2]*TMath::GammaDist(x,[0],[1],2)",0,18)
	chi2Shape.SetParameters(1.5,0,200)
	#~ chi2Shape.Draw("same")	
	#~ bckgOnlyHist.Fit("chi2Shape")
	hCanvas.DrawFrame(-1,0,22,bckgOnlyHist.GetBinContent(bckgOnlyHist.GetMaximumBin())+20,"; %s ; %s" %("-2*(log(L_{1})-log(L_{0}))","N_{Results}"))	
		
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latex.DrawLatex(0.15, 0.96, "CMS Simulation  #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = %s fb^{-1}"%19.4)	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	#~ latex.DrawLatex(0.6, 0.6, "#splitline{fit of #chi^{2} dist., NDF = %.2f}{#chi^{2}/N_{dof} %.2f}"%(chi2Shape.GetParameter(0)*2,chi2Shape.GetChisquare()/chi2Shape.GetNDF()))			
	
	observedLine = ROOT.TLine(2*4.3808,0,2*4.3808,bckgOnlyHist.GetBinContent(bckgOnlyHist.GetMaximumBin())+20)
	observedLine.SetLineColor(ROOT.kRed)
	observedLine.SetLineStyle(2)
	observedLine.Draw("same")
	bckgOnlyHist.Draw("samepe")
	#~ chi2Shape.Draw("same")
	ROOT.gStyle.SetOptStat(0)
	ROOT.gStyle.SetOptFit(0)
	
	legend = ROOT.TLegend(0.5,0.75,0.95,0.95)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	legend.SetTextFont(42)
	legend.AddEntry(observedLine,"observed","l")
	hist = ROOT.TH1F()
	hist.SetLineColor(ROOT.kWhite)
	
	#~ efficiencyObject = ROOT.TEfficiency(nominatorHist,denominatorHist)
	#~ uncertaintyUp = efficiencyObject.Wilson(nTestLarger,nTest,0.69,ROOT.kTRUE)
	#~ uncertaintyDown = efficiencyObject.Wilson(nTestLarger,nTest,0.69,ROOT.kFALSE)
	#~ print uncertaintyUp
	
	pValue = getEffciency(nominatorHist,denominatorHist)
	pValueFull = getEffciency(nominatorHistFull,denominatorHistFull)
	
	#~ legend.AddEntry(hist,"p-Value low mass: %.3f + %.3f - %.3f (%.2f #sigma)"%(pValue[0],pValue[1],pValue[2], ROOT.TMath.NormQuantile(1.0-pValue[0]/2)))
	legend.AddEntry(hist,"p-Value: %.3f + %.3f - %.3f (%.2f #sigma)"%(pValueFull[0],pValueFull[1],pValueFull[2],ROOT.TMath.NormQuantile(1.0-pValue[0]/2)))
	legend.Draw("same")
	hCanvas.Print("significanceStudy_BackgroundOnly.pdf")
	hCanvas.Print("significanceStudy_BackgroundOnly.root")		
	
	print nTest, nTestLarger
		
main()
