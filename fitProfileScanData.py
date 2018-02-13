#!/usr/bin/env python

import sys
sys.path.append('cfg/')
import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)
print sys.path
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import gROOT, gStyle, TFile, TH2F, TH2D, TGraph, TCanvas
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import dataInterface
import tools
import math
import argparse	

from corrections import rSFOF, rEEOF, rMMOF

def getGraph():
	graph = ROOT.TGraph()
	graph.SetName("Profile")
	graph.SetTitle("-log(L)")
	
	graph.SetPoint(0,32.35,0)
	graph.SetPoint(1,32.35,2.034096841)
	graph.SetPoint(2,35,2.034096841)
	graph.SetPoint(3,37.65,2.564778848)
	graph.SetPoint(4,40.3,2.908019569)
	graph.SetPoint(5,42.95,2.980626814)
	graph.SetPoint(6,45.6,2.946043133)
	graph.SetPoint(7,48.25,2.996534646)
	graph.SetPoint(8,50.9,2.994903554)
	graph.SetPoint(9,53.55,2.984772549)
	graph.SetPoint(10,56.2,2.929729989)
	graph.SetPoint(11,58.85,2.410021498)
	graph.SetPoint(12,61.5,2.049122348)
	graph.SetPoint(13,64.15,2.805981878)
	graph.SetPoint(14,66.8,2.992623463)
	graph.SetPoint(15,69.45,2.976715309)
	graph.SetPoint(16,72.1,2.826847947)
	graph.SetPoint(17,74.75,2.595750937)
	graph.SetPoint(18,77.4,1.921311649)
	graph.SetPoint(19,80.05,2.294381011)
	graph.SetPoint(20,82.7,2.610477044)
	graph.SetPoint(21,85.35,2.812256781)
	graph.SetPoint(22,88,2.812471464)
	graph.SetPoint(23,90.65,2.781854545)
	graph.SetPoint(24,93.3,2.829228397)
	graph.SetPoint(25,95.95,2.75611614)
	graph.SetPoint(26,98.6,2.302172505)
	graph.SetPoint(27,101.25,1.989015114)
	graph.SetPoint(28,103.9,2.578025595)
	graph.SetPoint(29,106.55,2.718135192)
	graph.SetPoint(30,109.2,2.926340014)
	graph.SetPoint(31,111.85,2.958998524)
	graph.SetPoint(32,114.5,2.904307868)
	graph.SetPoint(33,117.15,2.85177628)
	graph.SetPoint(34,119.8,2.880471763)
	graph.SetPoint(35,122.45,2.973342658)
	graph.SetPoint(36,125.1,2.999117769)
	graph.SetPoint(37,127.75,2.974869117)
	graph.SetPoint(38,130.4,2.830805028)
	graph.SetPoint(39,133.05,2.498311088)
	graph.SetPoint(40,135.7,1.955499588)
	graph.SetPoint(41,138.35,1.937257996)
	graph.SetPoint(42,141,1.525137393)
	graph.SetPoint(43,143.65,0.7290163848)
	graph.SetPoint(44,146.3,0.9380434516)
	graph.SetPoint(45,148.95,1.274669266)
	graph.SetPoint(46,151.6,1.347486892)
	graph.SetPoint(47,154.25,1.123868679)
	graph.SetPoint(48,156.9,0.30551217)
	graph.SetPoint(49,159.55,0.03800652232)
	graph.SetPoint(50,162.2,0.05431280703)
	graph.SetPoint(51,164.85,0.2079617089)
	graph.SetPoint(52,167.5,0.4532593113)
	graph.SetPoint(53,170.15,1.274673547)
	graph.SetPoint(54,172.8,2.125851085)
	graph.SetPoint(55,175.45,2.595813164)
	graph.SetPoint(56,178.1,2.672690888)
	graph.SetPoint(57,180.75,2.726008438)
	graph.SetPoint(58,183.4,2.604406882)
	graph.SetPoint(59,186.05,2.363021763)
	graph.SetPoint(60,188.7,2.473543194)
	graph.SetPoint(61,191.35,2.73324767)
	graph.SetPoint(62,194,2.887070922)
	graph.SetPoint(63,196.65,2.95127282)
	graph.SetPoint(64,199.3,2.994547123)
	graph.SetPoint(65,201.95,2.992964913)
	graph.SetPoint(66,204.6,2.994005697)
	graph.SetPoint(67,207.25,2.999054825)
	graph.SetPoint(68,209.9,2.961656841)
	graph.SetPoint(69,212.55,2.909986741)
	graph.SetPoint(70,215.2,2.779639175)
	graph.SetPoint(71,217.85,2.525417907)
	graph.SetPoint(72,220.5,2.182814177)
	graph.SetPoint(73,223.15,2.055533)
	graph.SetPoint(74,225.8,2.154848787)
	graph.SetPoint(75,228.45,2.22570126)
	graph.SetPoint(76,231.1,2.153081312)
	graph.SetPoint(77,233.75,2.099545301)
	graph.SetPoint(78,236.4,1.955769962)
	graph.SetPoint(79,239.05,1.663806209)
	graph.SetPoint(80,241.7,1.724541878)
	graph.SetPoint(81,244.35,2.045483262)
	graph.SetPoint(82,247,2.210773078)
	graph.SetPoint(83,249.65,2.056398186)
	graph.SetPoint(84,252.3,2.276335205)
	graph.SetPoint(85,254.95,2.692351663)
	graph.SetPoint(86,257.6,2.747264854)
	graph.SetPoint(87,260.25,2.70493313)
	graph.SetPoint(88,262.9,2.659463552)
	graph.SetPoint(89,265.55,2.823940687)
	graph.SetPoint(90,268.2,2.935005055)
	graph.SetPoint(91,270.85,2.898464279)
	graph.SetPoint(92,273.5,2.909134535)
	graph.SetPoint(93,276.15,2.887321572)
	graph.SetPoint(94,278.8,2.727246009)
	graph.SetPoint(95,281.45,2.481754102)
	graph.SetPoint(96,284.1,2.159100795)
	graph.SetPoint(97,286.75,1.835274008)
	graph.SetPoint(98,289.4,2.038682647)
	graph.SetPoint(99,292.05,2.413874008)
	graph.SetPoint(100,294.7,2.280054081)
	graph.SetPoint(101,297.35,2.042230353)
	graph.SetPoint(102,300,2.172428551)
	graph.SetPoint(103,300,2.172428551)
	graph.SetPoint(104,302.65,2.172428551)
	graph.SetPoint(105,302.65,0)
	
	return graph



def plot():
	
	canv = TCanvas("canv", "canv",800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
	style=setTDRStyle()	
	#~ style.SetPadRightMargin(0.18)	
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()
	
	latex = ROOT.TLatex()
	latex.SetTextSize(0.035)
	latex.SetNDC(True)
	latexLumi = ROOT.TLatex()
	latexLumi.SetTextFont(42)
	latexLumi.SetTextAlign(31)
	latexLumi.SetTextSize(0.04)
	latexLumi.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.055)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.03)
	latexCMSExtra.SetNDC(True)
	
	likelihoodGraph = getGraph()
	
	
	minL = likelihoodGraph.GetMinimum()
	
	
	nEntries = likelihoodGraph.GetN()
	
	xValues = likelihoodGraph.GetX()
	yValues = likelihoodGraph.GetY()
	
	plotGraph = ROOT.TGraph()
	
	minL = 1000
	
	for i in range(1,nEntries-1):
		if yValues[i] < minL:
			minL = yValues[i]
	for i in range(1,nEntries-1):		
		#~ print str(xValues[i])+": "+str(yValues[i]-minL)
		plotGraph.SetPoint(i-1,xValues[i],yValues[i]-minL)
	
	plotGraph.SetLineWidth(2)
	plotGraph.SetLineColor(2)
	
	
	plotPad.DrawFrame(35,0,300,5,"; m_{ll}^{edge} [GeV]; log(L) - log(L_{min})")
	
	latexLumi.DrawLatex(0.95, 0.96, "35.9 fb^{-1} (13 TeV)")
	latexCMS.DrawLatex(0.19,0.88,"CMS")
	#~ latexCMSExtra.DrawLatex(0.19,0.83,"#splitline{Private Work}{Simulation}")
	latexCMSExtra.DrawLatex(0.19,0.84,"Private Work")
	
	plotGraph.Draw("same c")
	
	canv.Update()
	canv.Print("ProfileScanData.pdf")
	
	
	

if (__name__ == "__main__"):
    plot()
