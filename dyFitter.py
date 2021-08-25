#!/usr/bin/env python

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT, gStyle,TMath
from setTDRStyle import setTDRStyle

ROOT.gROOT.SetBatch(True)

from messageLogger import messageLogger as log
import dataInterface
import tools
import math
import argparse 

from defs import getRunRange
from helpers import *


parametersToSave  = {}
rootContainer = []

def createFitHistoFromTree(tree, variable, weight, nBins, firstBin, lastBin, nEvents = -1):
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



        
        
        
def formatAndDrawFrame(ws,theConfig,frame, title, pdf, yMin=0.0, yMax=0.0):
        # This routine formats the frame and adds the residual plot.
        # Residuals are determined with respect to the given pdf.
        # For simultaneous models, the slice and projection option can be set.

        frame.SetMinimum(5)
        if (yMax > 0.0):
                frame.SetMaximum(yMax)
        frame.GetXaxis().SetRangeUser(theConfig.plotMinInv, theConfig.plotMaxInvDY)
        frame.GetYaxis().SetRangeUser(5, yMax)
        
        pad = ROOT.TPad("main%s" % (title), "main%s" % (title), 0.01, 0.25, 0.99, 0.99)
        pad.SetNumber(1)
        pad.Draw()
        
        resPad = ROOT.TPad("residual%s" % (title), "residual%s" % (title), 0.01, 0.01, 0.99, 0.25)
        resPad.SetNumber(2)
        resPad.Draw()
        
        pad.cd()
        if title == "EE":
                pad.DrawFrame(theConfig.plotMinInv,yMin,theConfig.plotMaxInvDY,yMax,";m_{ee} [GeV];%s"%(histoytitle))
        else:
                pad.DrawFrame(theConfig.plotMinInv,yMin,theConfig.plotMaxInvDY,yMax,";m_{#mu#mu} [GeV];%s"%(histoytitle))
        
        pdf.plotOn(frame,ROOT.RooFit.Components("offShell%s"%title),ROOT.RooFit.LineColor(ROOT.kGreen))
        pdf.plotOn(frame,ROOT.RooFit.Components("zShape%s"%title),ROOT.RooFit.LineColor(ROOT.kRed))
        pdf.plotOn(frame,ROOT.RooFit.Components("model%s"%title),ROOT.RooFit.LineColor(ROOT.kBlue))     
        pdf.plotOn(frame)
        frame.GetYaxis().SetTitle("Events / 2 GeV")             
        frame.Draw("same")
        frame.Print()
        
        
        resPad.cd()
        residualMaxY = 20.
        residualTitle = "data - fit"
        if theConfig.residualMode == "pull":
                residualMaxY = 3.
                #~ residualTitle = "#frac{(data - fit)}{#sigma_{data}}"
                residualTitle = "#frac{data - fit}{#sqrt{fit}}"
        hAxis = resPad.DrawFrame(theConfig.plotMinInv, -residualMaxY, theConfig.plotMaxInvDY, residualMaxY, ";;%s"%residualTitle)
        resPad.SetGridx()
        resPad.SetGridy()


        zeroLine = ROOT.TLine(theConfig.plotMinInv, 0.0, theConfig.plotMaxInvDY, 0.0)
        zeroLine.SetLineColor(ROOT.kBlue)
        zeroLine.SetLineWidth(2)
        zeroLine.Draw()
        residuals = None
        if theConfig.residualMode == "pull":
                ### For pulls divided by data uncertainty (default in RooFit pulls)
                #~ residuals = frame.pullHist()
                
                ### For pulls with division by prediction uncertainty
                curve = frame.findObject("model%s_Norm[inv]"%title,ROOT.RooCurve.Class())
                if curve == None:
                        print "Curve not found"         
                
                datahist = frame.findObject("h_dataHist%s"%title,ROOT.RooHist.Class())
                
                ### Somehow the histogram is not plotted if I use a TGraphAsymmError or new RooHist
                ### But it works if I fetch the default pull histogram and update the values
                ### No clue why this is the case
                #~ residuals = ROOT.TGraphAsymmErrors()
                #~ residuals = ROOT.RooHist()
                residuals = frame.pullHist()
                
                xstart,xstop,y = ROOT.Double(0.),ROOT.Double(0.),ROOT.Double(0.)
                curve.GetPoint(0,xstart,y)
                curve.GetPoint(curve.GetN()-1,xstop,y)
                for i in range(0,datahist.GetN()):
                        x,point = ROOT.Double(0.),ROOT.Double(0.)
                        datahist.GetPoint(i,x,point)
                        if x<xstart or x>xstop:
                                continue
                        
                        binWidth = float(theConfig.maxInv - theConfig.minInv)/ float(nBinsDY)
                        #curveVal = curve.average(x - 2, x + 2)
                        curveVal = curve.interpolate(x)
                        
                        yy = ROOT.Double(0.)
                        yy = point - curveVal
                        norm = math.sqrt(curveVal)                  
                        errLow = datahist.GetErrorYlow(i)
                        errHigh = datahist.GetErrorYhigh(i)
                        
                        if norm == 0.:
                                print "Residual histogram: Point %i has zero error, setting residual to 0"%i
                                yy = 0
                                errLow = 0
                                errHigh = 0
                        else:
                                yy = yy/norm
                                errLow = errLow/norm
                                errHigh = errHigh/norm
                        
                        residuals.SetPoint(i,x,yy)
                        residuals.SetPointError(i,0,0,errLow,errHigh)
                        #~ residuals.addBinWithError(x,yy,errLow,errHigh)       
        else:
                theConfig.residuals = frame.residHist()
        residuals.Draw("P0")
        hAxis.GetYaxis().SetNdivisions(4, 2, 5)
        hAxis.GetYaxis().CenterTitle()
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
        ### MT2 changes the mll shape, but the effect on the Z shape is small
        ### Used a control region definition with MT2 cut in my thesis, but
        ### the plots do not look well when using MC due to lacking statistics
        ### or a missing sample. You have to check which CR to use. The impact
        ### on the fit results is negligible. Adapt y-range accordingly

        parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="DrellYanControl",
        #parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="DrellYanControlNoMT2Cut",
                                                  help="selection which to apply.")
        parser.add_argument("-r", "--runRange", dest="runRanges", action="append", default=[],
                                                  help="name of run range.")
        parser.add_argument("-c", "--combine", dest="combine", action="store_true", default=False,
                                                  help="combined runRanges or not")
        parser.add_argument("-x", "--private", action="store_true", dest="private", default=False,
                                                  help="plot is private work.")         
        parser.add_argument("-w", "--write", action="store_true", dest="write", default=False,
                                                  help="write results to central repository")   
                                        
        args = parser.parse_args()      
        
        if not args.verbose:
                ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)  
                ROOT.RooMsgService.instance().setSilentMode(ROOT.kTRUE)
                

        cmsExtra = ""
        if args.private:
                cmsExtra = "Private Work"
                if args.mc:
                        cmsExtra = "#splitline{Private Work}{Simulation}"
        elif args.mc:
                cmsExtra = "Simulation" 
        else:
                #~ cmsExtra = "Preliminary"
                cmsExtra = "Supplementary"



        useExistingDataset = args.useExisting
        lumi = 0

        runRangeName = "_".join(args.runRanges)
        lumis = []
        for runRange in args.runRanges:
                lumis.append(getRunRange(runRange).printval)
        #lumi = "+".join(lumis)
        lumi = "137"
        from edgeConfig import edgeConfig
        theConfig = edgeConfig(region=args.selection,runNames=args.runRanges,useMC=args.mc)
        
        if args.private:
                theConfig.ownWork = True
        

        # init ROOT
        # uncomment this if you want a segmentation violation
        #gROOT.Reset()
        gROOT.SetStyle("Plain")
        setTDRStyle()
        ROOT.gROOT.SetStyle("tdrStyle") 
        

        
        # get data
        theDataInterface = dataInterface.DataInterface(theConfig.runRanges)
        treeOFOS = None
        treeEE = None
        treeMM = None
        
        #print ROOT.gDirectory.GetList()
   
        if not useExistingDataset:
                w = ROOT.RooWorkspace("w", ROOT.kTRUE)
                inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
                getattr(w,'import')(inv, ROOT.RooCmdArg())
                w.factory("weight[1.,0.,10.]")  
                vars = ROOT.RooArgSet(inv, w.var('weight'))             
                if (theConfig.useMC):
                        
                        log.logHighlighted("Using MC instead of data.")
                        datasets = theConfig.mcdatasets # ["TTJets", "ZJets", "DibosonMadgraph", "SingleTop"]
                        (treeEM, treeEE, treeMM) = tools.getTrees(theConfig, datasets)
                        
                else:
                        treeMMraw = theDataInterface.getTreeFromDataset("MergedData", "MuMu", cut=theConfig.selection.cut)
                        treeEMraw = theDataInterface.getTreeFromDataset("MergedData", "EMu", cut=theConfig.selection.cut)
                        treeEEraw = theDataInterface.getTreeFromDataset("MergedData", "EE", cut=theConfig.selection.cut)
                        

                        # convert trees
                        treeEM = dataInterface.DataInterface.convertDileptonTree(treeEMraw)
                        treeEE = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
                        treeMM = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
                
                print "EM", treeEM.GetEntries()
                print "EE", treeEE.GetEntries()
                print "MM", treeMM.GetEntries()
                
                
                histEM = createFitHistoFromTree(treeEM,"inv","weight",int((theConfig.maxInv - theConfig.minInv) / 2),theConfig.minInv,theConfig.maxInv)
                histEE = createFitHistoFromTree(treeEE,"inv","weight",int((theConfig.maxInv - theConfig.minInv) / 2),theConfig.minInv,theConfig.maxInv)
                histMM = createFitHistoFromTree(treeMM,"inv","weight",int((theConfig.maxInv - theConfig.minInv) / 2),theConfig.minInv,theConfig.maxInv)
                
                dataHistEE = ROOT.RooDataHist("dataHistEE", "dataHistEE", ROOT.RooArgList(w.var('inv')), histEE)
                dataHistMM = ROOT.RooDataHist("dataHistMM", "dataHistMM", ROOT.RooArgList(w.var('inv')), histMM)
                
                getattr(w, 'import')(dataHistEE, ROOT.RooCmdArg())
                getattr(w, 'import')(dataHistMM, ROOT.RooCmdArg())
                if theConfig.useMC:
                        w.writeToFile("workspaces/dyControl_%s_MC.root"%(runRangeName))
                else:
                        w.writeToFile("workspaces/dyControl_%s_Data.root"%(runRangeName))

        else:
                if theConfig.useMC:
                        f = ROOT.TFile("workspaces/dyControl_%s_MC.root"%(runRangeName))
                else:
                        f = ROOT.TFile("workspaces/dyControl_%s_Data.root"%(runRangeName))
                w =  f.Get("w")         
                #~ vars = ROOT.RooArgSet(w.var("inv"), w.var('weight'), w.var('genWeight'))
                vars = ROOT.RooArgSet(w.var("inv"), w.var('weight'))

        
        ### For some reason we never switched from the hard coded maximum. 
        ### Might want to change this in the future
        yMaximum = 5*10000                    ### 2016+2017+2018 data with MT2 cut
        yMinimum = 0.1                                  ### 2016+2017+2018 data with MT2 cut
        #yMaximum = histEE.GetMaximum()*1e10
        #yMinimum = 10
        
        global nBinsDY
        nBinsDY = 240 
        
        #
        global histoytitle
        histoytitle = 'Events / %.1f GeV' % ((theConfig.maxInv - theConfig.minInv) / float(nBinsDY))
        #histoytitle = 'Events / 4 GeV'
        ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
        ROOT.gSystem.Load("libFFTW.so")         
        ## 2 GeV binning for DY compared to 5 GeV in main fit
        


        w.var('inv').setBins(nBinsDY)
        #~ w.var('inv').setBins(140)

        
        
        # We know the z mass
        # z mass and width
        # mass resolution in electron and muon channels
        #w.factory("zmean[91.1876, 90.1876, 92.1876]")
        w.factory("zmean[91.1876]")
        #w.factory("zmean[91.1876,89,93]")

        w.factory("cbmeanMM[3.0,-5,5]")
        w.factory("cbmeanEE[3.0,-5,5]")
        w.factory("zwidthMM[2.4952]")
        w.factory("zwidthEE[2.4952]")
        w.factory("sMM[1.6.,0.,20.]")
        w.factory("BreitWigner::zShapeMM(inv,zmean,zwidthMM)")
        w.factory("sEE[1.61321382563436089e+00,0,20.]")
        w.factory("BreitWigner::zShapeEE(inv,zmean,zwidthEE)")
        w.factory("nMML[3.,0.,10]")
        w.factory("alphaMML[1.15,0,10]")
        w.factory("nMMR[1.,0,10]")
        w.factory("alphaMMR[2.5,0,10]")
        
        w.factory("DoubleCB::cbShapeMM(inv,cbmeanMM,sMM,alphaMML,nMML,alphaMMR,nMMR)")
        

        w.factory("nEEL[2.903,0.,10]")
        w.factory("alphaEEL[1.1598,0,5]")
        w.factory("nEER[1.0,0,10]")
        w.factory("alphaEER[2.508,0,5]")
        
        w.factory("DoubleCB::cbShapeEE(inv,cbmeanEE,sEE,alphaEEL,nEEL,alphaEER,nEER)")

        Abkg=ROOT.RooRealVar("Abkg","Abkg",1,0.01,10)
        getattr(w, 'import')(Abkg, ROOT.RooCmdArg())
        
        #~ w.var("inv").setBins(250,"cache")
        w.factory("cContinuumEE[%f,%f,%f]" % (-0.02,-0.1,0))
        
        w.factory("nZEE[100000.,500.,%s]" % (2000000))
        #~ w.factory("nZEE[100000.,300.,%s]" % (2000000))


        w.factory("Exponential::offShellEE(inv,cContinuumEE)")

        convEE = ROOT.RooFFTConvPdf("peakModelEE","zShapeEE (x) cbShapeEE",w.var("inv"),w.pdf("zShapeEE"),w.pdf("cbShapeEE"))
        getattr(w, 'import')(convEE, ROOT.RooCmdArg())
        w.pdf("peakModelEE").setBufferFraction(5.0)
        w.factory("zFractionEE[0.9,0,1]")
        expFractionEE = ROOT.RooFormulaVar('expFractionEE', '1-@0', ROOT.RooArgList(w.var('zFractionEE')))
        getattr(w, 'import')(expFractionEE, ROOT.RooCmdArg())   
        w.factory("SUM::modelEE1(zFractionEE*peakModelEE,expFractionEE*offShellEE)")
        w.factory("SUM::modelEE(nZEE*modelEE1)")


        w.factory("cContinuumMM[%f,%f,%f]" % (-0.02,-0.1,0))
        w.factory("Exponential::offShellMM(inv,cContinuumMM)")
        
        w.factory("nZMM[100000.,500.,%s]" % (2000000))
        w.factory("nOffShellMM[100000.,500.,%s]" % (2000000))
        #~ w.factory("nZMM[100000.,300.,%s]" % (2000000))
        #~ w.factory("nOffShellMM[100000.,300.,%s]" % (2000000))

        
        
        convMM = ROOT.RooFFTConvPdf("peakModelMM","zShapeMM (x) cbShapeMM",w.var("inv"),w.pdf("zShapeMM"),w.pdf("cbShapeMM"))
        getattr(w, 'import')(convMM, ROOT.RooCmdArg())
        w.pdf("peakModelMM").setBufferFraction(5.0)
        w.factory("zFractionMM[0.9,0,1]")
        expFractionMM = ROOT.RooFormulaVar('expFractionMM', '1-@0', ROOT.RooArgList(w.var('zFractionMM')))
        getattr(w, 'import')(expFractionMM, ROOT.RooCmdArg())           
        w.factory("SUM::modelMM1(zFractionMM*peakModelMM,expFractionMM*offShellMM)")
        w.factory("SUM::modelMM(nZMM*modelMM1)")
        
        print "3"

        fitEE = w.pdf('modelEE').fitTo(w.data('dataHistEE'),
                                                                                #ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(2.0))
                                                                                ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kFALSE), ROOT.RooFit.Extended(ROOT.kTRUE))
                                                                      
        parametersToSave["nParEE"] = fitEE.floatParsFinal().getSize()                                                                   
        
        print "3.1"
                
        fitMM = w.pdf('modelMM').fitTo(w.data('dataHistMM'),
                                                                                #ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(2.0))
                                                                                ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE), ROOT.RooFit.Minos(ROOT.kTRUE), ROOT.RooFit.Extended(ROOT.kTRUE))
                                                                                
        parametersToSave["nParMM"] = fitMM.floatParsFinal().getSize()                                                                           

        print "3.2"
        w.var("inv").setRange("zPeak",81,101)
        w.var("inv").setRange("fullRange",20,500)
        #~ w.var("inv").setRange("fullRange",20,300)
        w.var("inv").setRange("lowMass",20,70)
        argSet = ROOT.RooArgSet(w.var("inv"))

        peakIntEE = w.pdf("modelEE").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak")) 
        peakEE = peakIntEE.getVal()
        
        lowMassIntEE = w.pdf("modelEE").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass")) 
        lowMassEE = lowMassIntEE.getVal()
        
        peakIntMM = w.pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak"))
        peakMM = peakIntMM.getVal()
        
        lowMassIntMM = w.pdf("modelMM").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
        lowMassMM = lowMassIntMM.getVal()

        log.logHighlighted( "Peak: %.3f LowMass: %.3f (ee)"%(peakEE,lowMassEE))
        log.logHighlighted( "Peak: %.3f LowMass: %.3f (mm)"%(peakMM,lowMassMM))
        log.logHighlighted( "R(out,in): %.3f (ee) %.3f (mm)"%(lowMassEE/peakEE,lowMassMM/peakMM))
        
        
        frameEE = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
        
        frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
        frameEE.GetYaxis().SetTitle("Events / 2.5 GeV")
        #ROOT.RooAbsData.plotOn(w.data('dataHistEE'), frameEE, ROOT.RooFit.Binning(120))
        ROOT.RooAbsData.plotOn(w.data('dataHistEE'), frameEE)
        w.pdf('modelEE').plotOn(frameEE)                
        sizeCanvas = 800
        
        #~ parametersToSave["chi2EE"] = 1.1*frameEE.chiSquare(int(parametersToSave["nParEE"]))
        parametersToSave["chi2EE"] = frameEE.chiSquare(int(parametersToSave["nParEE"]))
        parametersToSave["chi2ProbEE"] = TMath.Prob(parametersToSave["chi2EE"]*(nBinsDY-int(parametersToSave["nParEE"])),nBinsDY-int(parametersToSave["nParEE"]))
        log.logHighlighted("Floating parameters EE: %f" % parametersToSave["nParEE"])
        log.logHighlighted("Chi2 EE: %f" % parametersToSave["chi2EE"])
        log.logHighlighted("Chi2 probability EE: %f" % parametersToSave["chi2ProbEE"])
        

        cEE = ROOT.TCanvas("ee distribtution", "ee distribution", sizeCanvas, int(1.25 * sizeCanvas))
        cEE.cd()
        pads = formatAndDrawFrame(w,theConfig,frameEE, title="EE", pdf=w.pdf("modelEE"), yMin = 0, yMax=0.05*yMaximum)
        
        dLeg = ROOT.TH1F()
        dLeg.SetMarkerStyle(ROOT.kFullCircle)
        dLeg.SetMarkerColor(ROOT.kBlack)
        dLeg.SetLineWidth(2)
        
        fullModelLeg = dLeg.Clone()
        fullModelLeg.SetLineColor(ROOT.kBlue)
        
        expLeg = dLeg.Clone()
        expLeg.SetLineColor(ROOT.kGreen+2)
        
        peakLeg = dLeg.Clone()
        peakLeg.SetLineColor(ROOT.kRed)
        
        nLegendEntries = 4
        leg = tools.myLegend(0.35, 0.89 - 0.07 * nLegendEntries, 0.92, 0.91, borderSize=0)
        leg.SetTextAlign(22)
        if (theConfig.useMC):
                leg.AddEntry(dLeg, 'Simulation', "pe")
        else:
                leg.AddEntry(dLeg, 'Data', "pe")
        leg.AddEntry(fullModelLeg, 'Full Z/#gamma* model', "l")
        leg.AddEntry(expLeg, 'Exponential component', "l")
        leg.AddEntry(peakLeg, 'DSCB #otimes BW component', "l")

        leg.Draw("same")
        
        goodnessOfFitEE = '#chi^{2}-prob. = %.3f' % parametersToSave["chi2ProbEE"]
        annotationsTitle = [
                                        (0.92, 0.47, "%s" % (theConfig.selection.latex)),
                                        #~ (0.92, 0.52, "%s" % (theConfig.selection.latex)),
                                        (0.92, 0.44, "%s" % goodnessOfFitEE),
                                        ]
        tools.makeCMSAnnotation(0.18, 0.88, lumi, mcOnly=theConfig.useMC, preliminary=theConfig.isPreliminary, year=theConfig.year,ownWork=theConfig.ownWork)
        tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
                
        tools.storeParameter("expofit", "dyExponent_EE" , "expo", w.var('cContinuumEE').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "cbMean", w.var('cbmeanEE').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "nL", w.var('nEEL').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "nR", w.var('nEER').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "alphaL", w.var('alphaEEL').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "alphaR", w.var('alphaEER').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "nZ", w.var('nZEE').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "zFraction", w.var('zFractionEE').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "s", w.var('sEE').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "sErr", w.var('sEE').getError(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "chi2", parametersToSave["chi2EE"],basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_EE" , "chi2Prob", parametersToSave["chi2ProbEE"],basePath="dyShelves/"+runRangeName+"/")
        eeName = "fig/expoFitEE_%s"%(runRangeName)
        if theConfig.useMC:
                eeName = "fig/expoFitEE_%s_MC"%(runRangeName)  
        cEE.Print(eeName+".pdf")
        cEE.Print(eeName+".root")       
        for pad in pads:
                pad.Close()     
        pads = formatAndDrawFrame(w,theConfig,frameEE, title="EE", pdf=w.pdf("modelEE"), yMin=yMinimum, yMax=yMaximum)
        
        leg.Draw("same")
        
        tools.makeCMSAnnotation(0.18, 0.88, lumi, mcOnly=theConfig.useMC, preliminary=theConfig.isPreliminary, year=theConfig.year,ownWork=theConfig.ownWork)
        tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
                        
                
        pads[0].SetLogy(1)
        eeName = "fig/expoFitEE_Log_%s"%(runRangeName)
        if theConfig.useMC:
                eeName = "fig/expoFitEE_Log_%s_MC"%(runRangeName)      
        cEE.Print(eeName+".pdf")
        cEE.Print(eeName+".root")       
        for pad in pads:
                pad.Close()


        frameMM = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of #mu#mu lepton pairs'))
        frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
        frameMM.GetYaxis().SetTitle("Events / 2.5 GeV")
        ROOT.RooAbsData.plotOn(w.data("dataHistMM"), frameMM)
        #ROOT.RooAbsData.plotOn(w.data("dataHistMM"), frameMM, ROOT.RooFit.Binning(120))
        w.pdf('modelMM').plotOn(frameMM)                
        sizeCanvas = 800
        
        #~ parametersToSave["chi2MM"] = 1.1*frameMM.chiSquare(int(parametersToSave["nParMM"]))
        parametersToSave["chi2MM"] = frameMM.chiSquare(int(parametersToSave["nParMM"]))
        parametersToSave["chi2ProbMM"] = TMath.Prob(parametersToSave["chi2MM"]*(nBinsDY-int(parametersToSave["nParMM"])),nBinsDY-int(parametersToSave["nParMM"]))
        log.logHighlighted("Chi2 MM: %f" % parametersToSave["chi2MM"])
        log.logHighlighted("Chi2 probability MM: %f" % parametersToSave["chi2ProbMM"])
        
        goodnessOfFitMM = '#chi^{2}-prob. = %.3f' % parametersToSave["chi2ProbMM"]
        annotationsTitle = [
                                        (0.92, 0.47, "%s" % (theConfig.selection.latex)),
                                        #~ (0.92, 0.52, "%s" % (theConfig.selection.latex)),
                                        (0.92, 0.44, "%s" % goodnessOfFitMM),
                                        ]
        
        residualMode = "pull"
        cMM = ROOT.TCanvas("#mu#mu distribtution", "#mu#mu distribution", sizeCanvas, int(1.25 * sizeCanvas))
        cMM.cd()
        pads = formatAndDrawFrame(w,theConfig,frameMM, title="MM", pdf=w.pdf("modelMM"), yMin = 0, yMax=0.05*yMaximum)

        
        
        leg.Draw("same")
        
        tools.makeCMSAnnotation(0.18, 0.88, lumi, mcOnly=theConfig.useMC, preliminary=theConfig.isPreliminary, year=theConfig.year,ownWork=theConfig.ownWork)
        tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
                

        tools.storeParameter("expofit", "dyExponent_MM", "expo", w.var('cContinuumMM').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "cbMean", w.var('cbmeanMM').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "cbMeanErr", w.var('cbmeanMM').getError(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "nL", w.var('nMML').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "nR", w.var('nMMR').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "alphaL", w.var('alphaMML').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "alphaR", w.var('alphaMMR').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "nZ", w.var('nZMM').getVal(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "zFraction", w.var('zFractionMM').getVal(),basePath="dyShelves/"+runRangeName+"/")              
        tools.storeParameter("expofit", "dyExponent_MM", "s", w.var('sMM').getVal(),basePath="dyShelves/"+runRangeName+"/")              
        tools.storeParameter("expofit", "dyExponent_MM", "sErr", w.var('sMM').getError(),basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "chi2", parametersToSave["chi2MM"],basePath="dyShelves/"+runRangeName+"/")
        tools.storeParameter("expofit", "dyExponent_MM", "chi2Prob", parametersToSave["chi2ProbMM"],basePath="dyShelves/"+runRangeName+"/")              
        mmName = "fig/expoFitMM_%s"%(runRangeName)
        if theConfig.useMC:
                mmName = "fig/expoFitMM_%s_MC"%(runRangeName)
        cMM.Print(mmName+".pdf")
        cMM.Print(mmName+".root")
        
        for pad in pads:
                pad.Close()     
                
        pads = formatAndDrawFrame(w,theConfig,frameMM, title="MM", pdf=w.pdf("modelMM"), yMin = yMinimum, yMax=yMaximum)
        legend = ROOT.TLegend(0.5, 0.6, 0.95, 0.94)
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



        leg.Draw("same")
        
        tools.makeCMSAnnotation(0.18, 0.88, lumi, mcOnly=theConfig.useMC, preliminary=theConfig.isPreliminary, year=theConfig.year,ownWork=theConfig.ownWork)
        tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
                
        
        pads[0].SetLogy(1)
        mmName = "fig/expoFitMM_Log_%s"%(runRangeName)
        if theConfig.useMC:
                mmName = "fig/expoFitMM_Log_%s_MC"%(runRangeName)
        
        cMM.Print(mmName+".pdf")
        cMM.Print(mmName+".root")       
        for pad in pads:
                pad.Close()


        if theConfig.useMC:
                w.writeToFile("dyWorkspace_MC.root")
        else:
                w.writeToFile("dyWorkspace.root")
        return w


main()
