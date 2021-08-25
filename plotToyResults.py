#!/usr/bin/env python


import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.gROOT.SetBatch(True)

from tools import loadParameter


basePath = "shelves/dicts/"
# basePath = "shelvesScan/dicts/"
project = "edgefit"
selection = "SignalHighMT2DeltaPhiJetMetFit_Run2016_36fb_Run2017_42fb_Run2018_60fb_CBTriangle"
m0s = [40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]
# gens = [(50, 50), (150, 50), (150, 100), (250, 75), (300, 150), (300, 75)]
gens = []
for m0 in m0s:
        gens.append( (m0, 50))

#m0s = [40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]
region = "Signal"
nSigs = {"Signal":50}
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
        
        stops = [0.00, 0.34, 0.61, 0.84, 1.00]
        red = [0.00, 0.09, 0.18, 0.09, 0.00]
        green = [0.01, 0.02, 0.39, 0.68, 0.97]
        blue = [0.17, 0.39, 0.62, 0.79, 0.97]
        
        minStop =0.
        maxStop = 1.
        
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



def loadToysForScan(name):
        
        ### Might need to change the default title, depending on the toys that shall be fitted
        result = {}
        for  i in range(0,len(gens)):
                title = "Scale1Mo%dSignalN%d_MC_Triangle_allowNegSignalSFOS"%(m0s[i],nSigs[region])
                # title = "Scale1Mo%dSignalN%d_MC_Triangle_allowNegSignal_randM0SFOS"%(gens[i][0],gens[i][1])
                parameters = loadParameter(project, "%s_%s"%(selection,title), name, basePath = basePath)
                result[i]=([name,gens[i][0], parameters, project, "Signal", title, name])     
        
        
        return result
        

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
        parametersChi2.update(loadParameter(project, "%s_%s"%(selection,label), "chi2H0", basePath = basePath))
        parametersLogLH0.update(loadParameter(project, "%s_%s"%(selection,label), "minNllH0", basePath = basePath))
        parametersLogLH1.update(loadParameter(project, "%s_%s"%(selection,label), "minNllH1", basePath = basePath))
        parametersRSFOF.update(loadParameter(project, "%s_%s"%(selection,label), "rSFOF", basePath = basePath))
        if "randM0" in label:
                parametersRandM0.update(loadParameter(project, "%s_%s"%(selection,label), "initialM0", basePath = basePath))
                result=([label,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, parametersRSFOF,parametersNB,parametersNBErr,parametersRandM0, project, selection, label])       
        else:
                result=([label,0., parameters,parametersError,parametersMass,parametersChi2,parametersLogLH0,parametersLogLH1, parametersRSFOF,parametersNB,parametersNBErr, project, selection, label])        
                        
        return result




def loadToysAdditional(label, project="edgefit", selection="SignalHighMT2DeltaPhiJetMetFit_Run2016_36fb_Run2017_42fb_Run2018_60fb_CBTriangle", basePath="shelvesAdditional/dicts/"):

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
        parametersChi2.update(loadParameter(project, "%s_%s"%(selection,label), "chi2H0", basePath = basePath))
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
                        
                        
                        
                        gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",0,350,"fitted m_{ll}^{edge} [GeV]","m0","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False,intVal=40+index*10)
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
                        
                        
                        
                        gaussFits = plotToyPlot([hist],[ROOT.kBlack],"signalScan",-100,500,"fitted N_{S}","nS","%d_signalScan"%(m0s[index]),Fit=True,histStyle=False)
                        
                        fitResults["means"].append(hist.GetMean())
                        fitResults["widths"].append(hist.GetRMS())
                        fitResults["normMeans"].append(hist.GetMean()/m0s[index])
                        fitResults["normWidths"].append(hist.GetRMS()/m0s[index])       
                        fitResults["meansFit"].append(gaussFits[0].GetParameter(1))
                        fitResults["widthsFit"].append(gaussFits[0].GetParameter(2))
                        fitResults["normMeansFit"].append(gaussFits[0].GetParameter(1)/m0s[index])
                        fitResults["normWidthsFit"].append(gaussFits[0].GetParameter(2)/m0s[index])
                                
                        
                return fitResults       



def plotToyPlot(hists,color,labels,xMin,xMax,xLabel,varName,plotName,Fit=False,histStyle=True,flipLables=False,intVal=None,RMSForFloat=False):
        
        from ROOT import TCanvas, TPad, TH1F, TH2F, TH1I, THStack, TLegend, TF1, TGraphErrors, TTree
        from numpy import array
        import numpy as n
        
        from setTDRStyle import setTDRStyle
                        
                
        hCanvas = TCanvas("hCanvas", "Distribution", 1200,800)
        plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
        
        style=setTDRStyle()
        style.SetTitleYOffset(1.2)

        plotPad.UseCurrentStyle()
        plotPad.Draw()  
        plotPad.cd()            


        gaussFits = []
        means = []
        RMS = []
        yMax = 0
        if Fit:
                for index, hist in enumerate(hists):
                        if intVal==None:
                                gaussFits.append(ROOT.TF1("gaussFit%d"%index,"gaus"))
                                gaussFits[index].SetParameter(1,0)
                                gaussFits[index].SetParLimits(0,12,500)
                                gaussFits[index].SetParLimits(1,0.4*xMin,1.4*xMax)
                                gaussFits[index].SetParLimits(2,0.4*xMin,1.4*xMax)
                                hist.Fit("gaussFit%d"%index)    
                        else:   
                                gaussFits.append(ROOT.TF1("gaussFit%d"%index,"gaus",intVal-3,intVal+3)) 
                                hist.Fit("gaussFit%d"%index,"R")
                        gaussFits[index].SetLineColor(color[index])
                        
                        means.append(hist.GetMean())
                        RMS.append(hist.GetRMS())
                        
                        if hist.GetBinContent(hist.GetMaximumBin()) > yMax:
                                yMax = hist.GetBinContent(hist.GetMaximumBin())
        else:
                for index, hist in enumerate(hists):
                        if hist.GetBinContent(hist.GetMaximumBin()) > yMax:
                                yMax = hist.GetBinContent(hist.GetMaximumBin())                         
        hCanvas.DrawFrame(xMin,0,xMax,yMax*1.9,"; %s ; %s" %(xLabel,"N_{fit results}")) 
        
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
        
        latex.DrawLatex(0.95, 0.96, "137 fb^{-1} (13 TeV)")
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
        
        latexVal = ROOT.TLatex()
        latexVal.SetTextSize(0.04)
        latexVal.SetNDC(True)
        latexVal.SetTextAlign(31)
        
        nLegendEntries = len(hists)
        


        if "nominal" in labels[0]:
                legend = ROOT.TLegend(xLabelPos,0.7-nLegendEntries*0.08,xLegendMax+0.04,0.75, "Inserted R_{SF/DF}")
        else:
                legend = ROOT.TLegend(xLabelPos,0.75-nLegendEntries*0.08,xLegendMax,0.75)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0) 
        

        ### In case of a floating edge (RMSForFloat), there is often a double peak structure
        ### -> a Gaussian fit to determine mean and width does not really make sense
        ### -> Use mean and RMS of histogram instead
        
        ### Number of significant digits, units etc. vary depending on the variable
        ### Used therefore slightly different positions/labels
        ### Might want to write a seperate routine
        for index, hist in enumerate(hists):
                if Fit:
                        latex.SetTextColor(color[index])
                        latexVal.SetTextColor(color[index])
                        if varName == "rSFDF":
                                if RMSForFloat== True and index == 0:                   
                                        latex.DrawLatex(0.7, 0.85-index*0.1, "mean_{hist}:")                    
                                        latexVal.DrawLatex(0.85, 0.85-index*0.1, "%.3f"%(means[index]))                 
                                        latex.DrawLatex(0.7, 0.81-index*0.1, "#sigma_{hist}:")                  
                                        latexVal.DrawLatex(0.85, 0.81-index*0.1, "%.3f"%(RMS[index]))                                           
                                else:           
                                        latex.DrawLatex(0.7, 0.85-index*0.1, "mean:")                   
                                        latexVal.DrawLatex(0.85, 0.85-index*0.1, "%.3f"%(gaussFits[index].GetParameter(1)))                     
                                        latex.DrawLatex(0.7, 0.81-index*0.1, "#sigma:")                 
                                        latexVal.DrawLatex(0.85, 0.81-index*0.1, "%.3f"%(gaussFits[index].GetParameter(2)))                                             
                        else:
                                if RMSForFloat== True and index == 0:           
                                        latex.DrawLatex(0.7, 0.85-index*0.1, "mean_{hist}:")                    
                                        latexVal.DrawLatex(0.875, 0.85-index*0.1, "%.2f"%(means[index]))                        
                                        latex.DrawLatex(0.7, 0.81-index*0.1, "#sigma_{hist}:")                  
                                        latexVal.DrawLatex(0.875, 0.81-index*0.1, "%.2f"%(RMS[index]))
                                        if varName == "m0":
                                                latex.DrawLatex(0.885, 0.85-index*0.1, "GeV")   
                                                latex.DrawLatex(0.885, 0.81-index*0.1, "GeV")   
                                elif RMSForFloat== True and index > 0:          
                                        latex.DrawLatex(0.7, 0.85-index*0.1, "mean:")                   
                                        latexVal.DrawLatex(0.875, 0.85-index*0.1, "%.2f"%(gaussFits[index].GetParameter(1)))                    
                                        latex.DrawLatex(0.7, 0.81-index*0.1, "#sigma:")                 
                                        latexVal.DrawLatex(0.875, 0.81-index*0.1, "%.2f"%(gaussFits[index].GetParameter(2)))
                                        if varName == "m0":
                                                latex.DrawLatex(0.885, 0.85-index*0.1, "GeV")   
                                                latex.DrawLatex(0.885, 0.81-index*0.1, "GeV")                           
                                else:
                                        latex.DrawLatex(0.7, 0.85-index*0.1, "mean:")                   
                                        latexVal.DrawLatex(0.85, 0.85-index*0.1, "%.2f"%(gaussFits[index].GetParameter(1)))                     
                                        latex.DrawLatex(0.7, 0.81-index*0.1, "#sigma:")                 
                                        latexVal.DrawLatex(0.85, 0.81-index*0.1, "%.2f"%(gaussFits[index].GetParameter(2)))
                                        if varName == "m0":
                                                latex.DrawLatex(0.86, 0.85-index*0.1, "GeV")    
                                                latex.DrawLatex(0.86, 0.81-index*0.1, "GeV")                    
                
                if histStyle:           
                        hist.SetMarkerStyle(20)
                        hist.SetMarkerSize(0)
                        hist.SetLineWidth(2)
                        hist.SetLineStyle(index+1)
                        hist.SetMarkerColor(color[index])
                        hist.SetLineColor(color[index])
                        
                        legend.AddEntry(hist,labels[index],"l")
                        
                        hist.Draw("samehist")
                else:   
                        hist.SetMarkerStyle(20)
                        hist.SetMarkerColor(color[index])
                        hist.SetLineColor(color[index])
                        
                        legend.AddEntry(hist,labels[index],"pe")
                        
                        hist.Draw("samepe")
                        
        ROOT.gStyle.SetOptStat(0)
        
        if len(hists) > 1:
                legend.Draw("same")
        else:
                latex.DrawLatex(0.65, 0.77, labels[0])
                ### Often used toys with certain injected number of signal events, edge position etc.
                ### Put lines in to mark the positions
                if labels[0] == "Signal injected":
                        if varName == "nSPure":
                                insertedVal = ROOT.TLine(80,0,80,yMax*1.3)
                                insertedVal.SetLineColor(ROOT.kRed+1)
                                insertedVal.SetLineWidth(2)
                                insertedVal.SetLineStyle(ROOT.kDashed)
                                insertedVal.Draw("same")
                                latex.SetTextColor(ROOT.kRed+1)
                                latex.DrawLatex(0.65, 0.72, "Injected N_{S}: 80")
                        if varName == "m0":
                                insertedVal = ROOT.TLine(150,0,150,yMax*1.3)
                                insertedVal.SetLineColor(ROOT.kRed+1)
                                insertedVal.SetLineWidth(2)
                                insertedVal.SetLineStyle(ROOT.kDashed)
                                insertedVal.Draw("same")
                                latex.SetTextColor(ROOT.kRed+1)
                                latex.DrawLatex(0.65, 0.72, "Injected m_{ll}^{edge}: 150 GeV")
                        if varName == "rSFDF":
                                insertedVal = ROOT.TLine(1.06,0,1.06,yMax*1.3)
                                insertedVal.SetLineColor(ROOT.kRed+1)
                                insertedVal.SetLineWidth(2)
                                insertedVal.SetLineStyle(ROOT.kDashed)
                                insertedVal.Draw("same")
                                latex.SetTextColor(ROOT.kRed+1)
                                latex.DrawLatex(0.65, 0.72, "Injected R_{SF/DF}: 1.06")

        hCanvas.RedrawAxis()
        hCanvas.Update()
        hCanvas.Print("toyResults/%s_%s.pdf"%(varName,plotName))        
        
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
        
        latex.DrawLatex(0.95, 0.96, "137 fb^{-1} (13 TeV)")
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


def plotToyPlot2D(hist,xMin,xMax,yMin,yMax,xLabel,yLabel,varName1,varName2,plotName,showCorr=True,showDiagonal=False,mean=None,log=False,horizontal=False):
        
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
        
        ### Draw obtained correlations, diagonal/horizontal/vertical line 
        ### to mark points where fitted and generated values are the same
        if showCorr:
                latex.DrawLatex(0.5, 0.25, "Correlation: %.2f"%(hist.GetCorrelationFactor()))                   
        if showDiagonal:
                diagonal = ROOT.TLine(yMin,yMin,yMax,yMax)
                diagonal.SetLineColor(ROOT.kRed+1)
                diagonal.SetLineWidth(2)
                diagonal.SetLineStyle(ROOT.kDashed)
                diagonal.Draw("same")
        if not mean == None:
                if horizontal:
                        mean = ROOT.TLine(xMin,mean,xMax,mean)
                        mean.SetLineColor(ROOT.kRed+1)
                        mean.SetLineWidth(2)
                        mean.SetLineStyle(ROOT.kDashed)
                        mean.Draw("same")               
                else:
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
        
        latex.DrawLatex(0.8, 0.96, "137 fb^{-1} (13 TeV)")
        cmsExtra = "#splitline{Private Work}{Simulation}"

        latexCMS.DrawLatex(0.18,0.88,"CMS")
        if "Simulation" in cmsExtra:
                yLabelPos = 0.81        
        else:
                yLabelPos = 0.84        

        latexCMSExtra.DrawLatex(0.18,yLabelPos,"%s"%(cmsExtra))         
        
        plotPad.RedrawAxis()

        ROOT.gStyle.SetOptStat(0)
        #ROOT.gStyle.SetOptFit(0)
        hCanvas.Print("toyResults/%svs%s_%s.pdf"%(varName2,varName1,plotName))


def plotChiSquares(pklsSmooth,pklsStep,illustrate=True,observedValue=0.):
        from ROOT import TH1F, TCanvas, TLegend
        from setTDRStyle import setTDRStyle
        
        print observedValue
        
        ### Fill two histograms, one for fixed and one for floating
        ### edge position

        bckgOnlyHist = TH1F("bckgOnlyHist","bckgOnlyHist",50,0,5)
        bckgOnlyHistStep = TH1F("bckgOnlyHist","bckgOnlyHist",50,0,5)
        bckgOnlyHist.SetMarkerColor(ROOT.kRed)
        bckgOnlyHist.SetLineColor(ROOT.kRed)
        bckgOnlyHist.SetMarkerStyle(20)
        bckgOnlyHistStep.SetMarkerColor(ROOT.kBlack)
        bckgOnlyHistStep.SetLineColor(ROOT.kBlack)
        bckgOnlyHistStep.SetMarkerStyle(20)       
        

        
        ### for floating edge
        for index, value in pklsSmooth[2].iteritems():
                ### bkgOnly chi^2/ndf
                bckgOnlyHist.Fill(pklsSmooth[5][index])     

        ### fixed edge                                  
        for index, value in pklsStep[2].iteritems():
                ### bkgOnly chi^2/ndf
                bckgOnlyHistStep.Fill(pklsStep[5][index])      
                
                        
        hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
        plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
        
        style=setTDRStyle()


        plotPad.UseCurrentStyle()
        plotPad.Draw()  
        plotPad.cd()    
        
        
        
        hCanvas.DrawFrame(0,0,5,bckgOnlyHistStep.GetBinContent(bckgOnlyHistStep.GetMaximumBin())+280,"; %s ; %s" %("#chi^{2} / ndf","N_{fit results}"))     
              
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
        
        latex.DrawLatex(0.95, 0.96, "137.2 fb^{-1} (13 TeV)")
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
        
        
        observedLine = ROOT.TLine(observedValue,0,observedValue,bckgOnlyHistStep.GetBinContent(bckgOnlyHistStep.GetMaximumBin())+280)
        observedLine.SetLineColor(ROOT.kRed)
        observedLine.SetLineStyle(2)
        if observedValue > 0.:
                observedLine.Draw("same")
        bckgOnlyHist.Draw("samepe")
        bckgOnlyHistStep.SetMarkerColor(ROOT.kBlue)
        bckgOnlyHistStep.SetLineColor(ROOT.kBlue)
        bckgOnlyHistStep.Draw("samepe")
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        
        legend = ROOT.TLegend(0.475,0.65,0.925,0.9)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.SetTextFont(42)
        if observedValue > 0.:  
                legend.AddEntry(observedLine,"observed","l")
        if illustrate:
                legend.AddEntry(bckgOnlyHist,"Normal toys","l")
                legend.AddEntry(bckgOnlyHistStep,"Step function toys","l")

                
        hist = ROOT.TH1F()
        hist.SetLineColor(ROOT.kWhite)
        
        
        legend.Draw("same")
        hCanvas.Print("toyResults/chiSquareDistributions_BackgroundOnly.pdf")                        


def plotPValues(shelves,shelvesFixed,FitLabels=False,illustrate=False,observedValue=0.,observedValueFixed=0.):
        from ROOT import TH1F, TCanvas, TLegend
        from setTDRStyle import setTDRStyle
        
        print observedValue
        
        ### Fill two histograms, one for fixed and one for floating
        ### edge position

        bckgOnlyHist = TH1F("bckgOnlyHist","bckgOnlyHist",50,-1,22)
        bckgOnlyHistFixed = TH1F("bckgOnlyHist","bckgOnlyHist",50,-1,22)
        bckgOnlyHist.SetMarkerColor(ROOT.kRed)
        bckgOnlyHist.SetLineColor(ROOT.kRed)
        bckgOnlyHist.SetMarkerStyle(20)
        bckgOnlyHistFixed.SetMarkerColor(ROOT.kBlack)
        bckgOnlyHistFixed.SetLineColor(ROOT.kBlack)
        bckgOnlyHistFixed.SetMarkerStyle(20)       
        
        nominatorHist = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
        nominatorHistFull = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
        denominatorHist = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
        denominatorHistFull = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
                
        nominatorHistFixed = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
        nominatorHistFullFixed = ROOT.TH1F("nominatorHist","nominatorHist",1,0,1)
        denominatorHistFixed = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
        denominatorHistFullFixed = ROOT.TH1F("denominatorHist","denominatorHist",1,0,1)
        
        ### for floating edge
        for index, value in shelves[2].iteritems():
                ### difference of log likelihood between s+b and b-only hypothesis (2#Delta(log(L)))
                bckgOnlyHist.Fill(-2*(shelves[7][index]-shelves[6][index]))     
                ### Only consider positive signal yields, but take this into account
                ### by filling 0.5 instead of 1
                if shelves[4][index] > 0:
                        denominatorHistFull.Fill(0.5)
                        if -2*(shelves[7][index]-shelves[6][index]) >= observedValue:
                                nominatorHistFull.Fill(0.5)
                        ### If one only wants to consider a certain mass range (here below the Z)
                        if shelves[4][index] < 90 and shelves[4][index] > 0:    
                                denominatorHist.Fill(0.5)
                                if -2*(shelves[7][index]-shelves[6][index]) >= observedValue:
                                        nominatorHist.Fill(0.5)
        
        ### fixed edge                                  
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
        
        ### Chi2 shapes to visualize the applicability of Wilks theorem
        ### Parameter [0] *2 (not sure why this is necessary) = number of
        ### degrees of freedom.
        ### If you go back to central-forward or some other split, add 0.5 per
        ### additional signal region.
        ### Since the chi2 distribution does not fit for the case with the
        ### floating edge (as expected), only the function for the fixed edge
        ### is fitted instead. So you have to set the normalization for the
        ### floating edge by hand 
        chi1Shape = ROOT.TF1("chi1Shape","[1]*TMath::GammaDist(x,[0],0,2)",0,18)
        chi1Shape.SetParameters(0.5,500)
        chi1Shape.SetParLimits(0,0.5,0.5)               ### Fix number of degrees of freedom
        chi1Shape.SetLineColor(ROOT.kBlue)
        chi2Shape = ROOT.TF1("chi2Shape","[1]*TMath::GammaDist(x,[0],0,2)",0,18)
        chi2Shape.SetParameters(1,bckgOnlyHist.Integral()/2)

        
        
        bckgOnlyHistFixed.Fit("chi1Shape")
        
        frame = hCanvas.DrawFrame(0,0,14,bckgOnlyHistFixed.GetBinContent(bckgOnlyHistFixed.GetMaximumBin())+40,"; %s ; %s" %("-2#Delta(log L)","N_{fit results}"))     
        frame.GetYaxis().SetTitleOffset(1.4)
        if illustrate:
                chi1Shape.SetLineColor(ROOT.kBlue)
                chi2Shape.SetLineColor(ROOT.kBlack)
                chi1Shape.Draw("same")                  
                chi2Shape.Draw("same")                  
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
        
        latex.DrawLatex(0.95, 0.96, "137 fb^{-1} (13 TeV)")
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
        if FitLabels:
                latex.DrawLatex(0.5, 0.6, "#splitline{fit of #chi^{2} dist., NDF = %.2f}{#chi^{2}/N_{dof} %.2f}"%(chi1Shape.GetParameter(0)*2,chi1Shape.GetChisquare()/chi1Shape.GetNDF()))                     
        
        observedLine = ROOT.TLine(observedValue,0,observedValue,bckgOnlyHistFixed.GetBinContent(bckgOnlyHistFixed.GetMaximumBin())+40)
        observedLine.SetLineColor(ROOT.kRed)
        observedLine.SetLineStyle(2)
        if observedValue > 0.:
                observedLine.Draw("same")
        bckgOnlyHist.Draw("samepe")
        bckgOnlyHistFixed.SetMarkerColor(ROOT.kBlue)
        bckgOnlyHistFixed.SetLineColor(ROOT.kBlue)
        bckgOnlyHistFixed.Draw("samepe")
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)
        
        legend = ROOT.TLegend(0.475,0.65,0.925,0.9)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.SetTextFont(42)
        if observedValue > 0.:  
                legend.AddEntry(observedLine,"observed","l")
        if illustrate:
                legend.AddEntry(chi1Shape,"#chi^{2} dist. with 1 d.o.f.","l")
                legend.AddEntry(chi2Shape,"#chi^{2} dist. with 2 d.o.f.","l")
                
        hist = ROOT.TH1F()
        hist.SetLineColor(ROOT.kWhite)
        
        
        pValue = getEffciency(nominatorHist,denominatorHist)
        pValueFull = getEffciency(nominatorHistFull,denominatorHistFull)
        #~ pValueFixed = getEffciency(nominatorHistFixed,denominatorHistFixed)
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



def plotScanResults():

        from ROOT import TH1F, TH2F, TTree, TCanvas, TGraphErrors, TGraph
        
        import numpy as n               

        ### First load scan results. Might need to change default name in routine       
        m0pkl = loadToysForScan("m0")  
        nSpkl = loadToysForScan("nS")
        rSFOFpkl = loadToysForScan("rSFOF")
        massHists = []
        nSHists = []
        rSFOFHists = []
        
        plotName = "signalInjectedN50"
        nSMean = 50
        rSFOFMean = 1.06

        
        for i in range(0,len(gens)):
                massHists.append(TH1F("mass_hist_%d"%i,"mass_hist_%d"%i,306,0,306))     
                nSHists.append(TH1F("nS_hist_%d"%i,"nS_hist_%d"%i,50,-100,400)) 

        scanHist = TH2F("scanHist","scanHist; fitted m_{#kern[1.0]{ }ll}^{edge} [GeV]; generated m_{#kern[1.0]{ }ll}^{edge} [GeV]; N_{fit results}",int((m0s[-1]+55-25)/2.5),25,m0s[-1]+55,len(m0s),m0s[0]-5,m0s[-1]+5)
        for index, value in m0pkl.iteritems():
                
                m0 = m0s[index]
                
                for index2, value2 in value[2].iteritems():     
                                scanHist.Fill(value2,m0)
                                massHists[index].Fill(value2)
        
        plotToyPlot2D(scanHist,30,m0s[-1]+55,35,m0s[-1]+5,"fitted m_{#kern[1.0]{ }ll}^{edge} [GeV]","generated m_{#kern[1.0]{ }ll}^{edge} [GeV]","fittedM0","generatedM0",plotName,showCorr=False,showDiagonal=True,log=False)
        
        
        scanHistSignal = TH2F("scanHist","scanHist; fitted N_{S} [GeV]; generated m_{#kern[1.0]{ }ll}^{edge} [GeV]; N_{fit results}",50,-100,400,len(m0s),m0s[0]-5,m0s[-1]+5)
        for index, value in nSpkl.iteritems():
                
                m0 = gens[index][0]
                toycounter = 0
                
                for index2, value2 in value[2].iteritems():     
                                toycounter = toycounter + 1
                                if toycounter == 1000:
                                        break
                                scanHistSignal.Fill(value2,m0)
                                nSHists[index].Fill(value2)
                        
        plotToyPlot2D(scanHistSignal,-150,300,35,m0s[-1]+5,"fitted N_{S}","generated m_{#kern[1.0]{ }ll}^{edge} [GeV]","fittedNS","generatedM0",plotName,showCorr=False,mean=nSMean,log=False)
        
        
        scanHistRSFOF = TH2F("scanHist","scanHist; fitted R_{SF/DF}; generated m_{#kern[1.0]{ }ll}^{edge} [GeV]; N_{fit results}",90,0.95,1.25,len(m0s),m0s[0]-5,m0s[-1]+5)
        for index, value in rSFOFpkl.iteritems():
                
                m0 = gens[index][0]
                
                for index2, value2 in value[2].iteritems():     
                                scanHistRSFOF.Fill(value2,m0)
                        
        plotToyPlot2D(scanHistRSFOF,0.95,1.2,35,m0s[-1]+5,"fitted R_{SF/DF}","generated m_{ll}^{edge} [GeV]","fittedRSFOF","generatedM0",plotName,showCorr=False,mean=rSFOFMean,log=False)
        
        
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


        plotGraph([graph,graphFit],[ROOT.kBlack,ROOT.kBlue],["mean #pm RMS","gaussian mean #pm #sigma"],m0s[0]-10,m0s[-1]+10,m0s[0]-10,m0s[-1]+10,"generated m_{ll}^{edge} [GeV]","mean fitted m_{ll}^{edge} [GeV]","meanM0vsGenM0",plotName)
        plotGraph([normGraph],[ROOT.kBlack],["RMS"],m0s[0]-10,m0s[-1]+10,0.7,1.3,"generated m_{ll}^{edge} [GeV]","mean fitted / generated  m_{ll}^{edge}","fitvsGenM0Ratio",plotName)
        plotGraph([widthGraph,widthGraphFit],[ROOT.kBlack,ROOT.kBlue],["RMS","gaussian #sigma"],m0s[0]-10,m0s[-1]+10,0,20,"generated m_{ll}^{edge} [GeV]","width of m_{ll}^{edge} dist. [GeV]","WidthsvsGenM0Ratio",plotName)

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


        plotGraph([graphFit],[ROOT.kBlack],[],m0s[0]-10,m0s[-1]+10,0,300,"generated m_{ll}^{edge} [GeV]","mean fitted N_{S} ","meanNSvsGenM0",plotName)



def main():
        from sys import argv

        from ROOT import TH1F, TH2F
        
        #### Plot scan of toys with different injected mass positions but otherwise same quantities (e.g. same number of signal events, all fixed or floating edge ...)
        # plotScanResults()
        #exit()
        #
        #### List of additional toy samples, varying edge positions, number of signal events, randomized or fixed starting positions ....
        # listOfScans = [
        # "Scale1Mo50SignalN50_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo50SignalN50_FixedEdge_50.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo150SignalN50_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo150SignalN50_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo150SignalN100_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo150SignalN100_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo250SignalN75_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo250SignalN75_FixedEdge_250.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo300SignalN75_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo300SignalN75_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo300SignalN150_MC_Triangle_allowNegSignal_randM0SFOS","Scale1Mo300SignalN150_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS",
        
        # "Scale1Mo300SignalN0_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS","Scale1Mo300SignalN0_MC_Triangle_randM0SFOS","Scale1Mo150SignalN0_MC_Triangle_allowNegSignal_randM0SFOS",]
        
        #### define somewhat shorter names for the resulting plots
        # names = {
        # "Scale1Mo50SignalN50_FixedEdge_50.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m050nS50_FixedEdge_allowNeg",
        # "Scale1Mo50SignalN50_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m050S50_allowNeg_randM0",
        
        # "Scale1Mo150SignalN50_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m0150nS50_FixedEdge_allowNeg",
        # "Scale1Mo150SignalN50_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m0150S50_allowNeg_randM0",
        
        # "Scale1Mo150SignalN100_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m0150nS100_FixedEdge_allowNeg",
        # "Scale1Mo150SignalN100_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m0150S100_allowNeg_randM0",
        
        # "Scale1Mo250SignalN75_FixedEdge_250.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m0250nS75_FixedEdge_allowNeg",
        # "Scale1Mo250SignalN75_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m0250S75_allowNeg_randM0",
        
        # "Scale1Mo300SignalN75_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m0300nS75_FixedEdge_allowNeg",
        # "Scale1Mo300SignalN75_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m0300S75_allowNeg_randM0",
        
        # "Scale1Mo300SignalN150_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS":"signalInjected_m0300nS150_FixedEdge_allowNeg",
        # "Scale1Mo300SignalN150_MC_Triangle_allowNegSignal_randM0SFOS":"signalInjected_m0300S150_allowNeg_randM0",
        
        # "Scale1Mo300SignalN0_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS":"backgroundOnly_m0150_FixedEdge_allowNeg",
        # "Scale1Mo150SignalN0_MC_Triangle_allowNegSignal_randM0SFOS":"backgroundOnly_m0150_allowNeg_randM0",
        # "Scale1Mo300SignalN0_MC_Triangle_randM0SFOS":"backgroundOnly_m0300_randM0",}
        
        #hists = {}
        #label50_50 = "m_{ll} = 50 GeV, N_{S,true} = 50"    
        #label150_50 = "m_{ll} = 150 GeV, N_{S,true} = 50" 
        #label150_100 = "m_{ll} = 150 GeV, N_{S,true} = 100" 
        #label250_75 = "m_{ll} = 250 GeV, N_{S,true} = 75" 
        #label300_75 = "m_{ll} = 300 GeV, N_{S,true} = 75" 
        #label300_150 = "m_{ll} = 300 GeV, N_{S,true} = 150" 


        #pkls = loadToys("Scale1Mo50SignalN50_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["50_50_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["50_50_float"].Fill((value-50)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo50SignalN50_FixedEdge_50.0_MC_Triangle_allowNegSignalSFOS")
        #hists["50_50_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["50_50_fixed"].Fill((value-50)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo150SignalN50_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["150_50_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["150_50_float"].Fill((value-50)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo150SignalN50_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS")
        #hists["150_50_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["150_50_fixed"].Fill((value-50)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo150SignalN100_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["150_100_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["150_100_float"].Fill((value-100)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo150SignalN100_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS")
        #hists["150_100_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["150_100_fixed"].Fill((value-100)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo250SignalN75_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["250_75_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["250_75_float"].Fill((value-75)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo250SignalN75_FixedEdge_250.0_MC_Triangle_allowNegSignalSFOS")
        #hists["250_75_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["250_75_fixed"].Fill((value-75)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo300SignalN75_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["300_75_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["300_75_float"].Fill((value-75)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo300SignalN75_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS")
        #hists["300_75_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["300_75_fixed"].Fill((value-75)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo300SignalN150_MC_Triangle_allowNegSignal_randM0SFOS")
        #hists["300_150_float"] = TH1F("","",100,-10,8)
        #for index, value in pkls[2].iteritems():
                #hists["300_150_float"].Fill((value-150)/pkls[3][index])       
                
        #pkls = loadToys("Scale1Mo300SignalN150_FixedEdge_300.0_MC_Triangle_allowNegSignalSFOS")
        #hists["300_150_fixed"] = TH1F("","",100,-10,10)
        #for index, value in pkls[2].iteritems():
                #hists["300_150_fixed"].Fill((value-150)/pkls[3][index])       
                
           

        #plotToyPlot([hists["50_50_float"],hists["150_50_float"],hists["150_100_float"],hists["250_75_float"],hists["300_75_float"],hists["300_150_float"]],[ROOT.kBlack,ROOT.kBlue,ROOT.kRed,ROOT.kGreen+2,ROOT.kOrange+1,ROOT.kGray++1],[label50_50,label150_50,label150_100,label250_75,label300_75,label300_150],-10,8,"(fitted N_{S} - N_{S,true}) / #sigma_{N_{S}}","nS","signalInjected_floatComparison",Fit=True)
        
        #plotToyPlot([hists["50_50_fixed"],hists["150_50_fixed"],hists["150_100_fixed"],hists["250_75_fixed"],hists["300_75_fixed"],hists["300_150_fixed"]],[ROOT.kBlack,ROOT.kBlue,ROOT.kRed,ROOT.kGreen+2,ROOT.kOrange+1,ROOT.kGray+1],[label50_50,label150_50,label150_100,label250_75,label300_75,label300_150],-10,8,"(fitted N_{S} - N_{S,true}) / #sigma_{N_{S}}","nS","signalInjected_fixedComparison",Fit=True)
        
            
        listOfScans = ["Scale1Mo150SignalN80_MC_Triangle_allowNegSignalSFOS"]
        names = {"Scale1Mo150SignalN80_MC_Triangle_allowNegSignalSFOS" : "m150n80"}
        
        ##### make some default plots, not used for a while so take care
        # for name in listOfScans:
                # print name
                # label = names[name]                     
                # pkls = loadToysAdditional(name)
                
                ### Needs the same number of injected signal events
                # hist = TH1F("","",100,-10,10)
                # trueVal = 0
                # if "SignalN" in name:
                        # trueVal = float(name.split("_")[0].split("SignalN")[1])
                # for index, value in pkls[2].iteritems():
                        # hist.Fill((value-trueVal)/pkls[3][index])     
                
                # plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],-10,10,"(fitted N_{S} - N_{S,true}) / #sigma_{N_{S}}","nSvsNsTrue",label,Fit=True)
                
                # hist = TH1F("","",100,-10,10)
                # for index, value in pkls[2].iteritems():
                        # hist.Fill(value/pkls[3][index]) 
                # plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nSNonCorr",label,Fit=True)

                
                # hist = TH1F("","",80,-150,150)
                # for index, value in pkls[2].iteritems():
                        # hist.Fill(value)        
                # plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],-50,200,"fitted N_{S}","nSPure",label,Fit=True)
                
                
                # hist = TH1F("","",100,-10,10)
                # for index, value in pkls[6].iteritems():
                        # if "FixedEdge" in name:
                                # pvalue = ROOT.TMath.Prob(max(0,-2*(pkls[7][index]-value)), 1)
                        # else:
                                # pvalue = ROOT.TMath.Prob(max(0,-2*(pkls[7][index]-value)), 2)
                        # sigma = ROOT.TMath.NormQuantile(1.0-pvalue/2.0);                        
                        # hist.Fill(sigma)        
                # plotToyPlot([hist],[ROOT.kBlack],[label],-10,10,"#sigma from Likelihoods","signif",label,Fit=False)
                
                        
                # hist = TH1F("","",140,20,300)
                # for index, value in pkls[4].iteritems():
                        # hist.Fill(value)        
                # plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],30,300,"fitted m_{#kern[1.0]{ }ll}^{edge}","m0",label,Fit=True)
                                        
                
                # hist = TH1F("","",80,0.8,1.2)
                # for index, value in pkls[8].iteritems():
                        # hist.Fill(value)
                # plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],0.975,1.225,"fitted R_{SF/DF}","rSFDF",label,Fit=True)             
        
                                
                # hist = TH1F("","",100,2000,6000)
                # for index, value in pkls[9].iteritems():
                        # hist.Fill(value)
                # plotToyPlot([hist],[ROOT.kBlack],[label],2000,6000,"fitted N_{B}","nB",label,Fit=True)          
        
        
                # hist = TH2F("bckgOnlyHist","bckgOnlyHist",80,0.9,1.3,20,-5,15)
                # for index, value in pkls[2].iteritems():
                        # hist.Fill(pkls[8][index],value/pkls[3][index])
                # plotToyPlot2D(hist,0.9,1.3,-5,15,"fitted R_{SF/DF}","fitted N_{S}/#sigma_{N_{S}}","rSFDF","nS",label)
        
        
        #        
        #
        #
        #### Toys with injected RSFOF on nominal value or at +/- 1 sigma 
        # pkls = loadToysAdditional("Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOS")
        # pklsUp = loadToysAdditional("Scale1Mo150SignalN0_MC_Up_Triangle_allowNegSignalSFOS")
        # pklsDown = loadToysAdditional("Scale1Mo150SignalN0_MC_Down_Triangle_allowNegSignalSFOS")
        
        # hist = TH1F("","",50,-10,10)
        # histUp = TH1F("","",50,-10,10)
        # histDown = TH1F("","",50,-10,10)
        # for index, value in pkls[2].iteritems():
                # hist.Fill(value/pkls[3][index]) 
        # for index, value in pklsUp[2].iteritems():
                # histUp.Fill(value/pklsUp[3][index])     
        # for index, value in pklsDown[2].iteritems():
                # histDown.Fill(value/pklsDown[3][index]) 
        # plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["nominal","+1 #sigma","-1 #sigma"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS","systShift",Fit=False)
        
        # hist = TH1F("","",40,-200,200)
        # histUp = TH1F("","",40,-200,200)
        # histDown = TH1F("","",40,-200,200)
        # for index, value in pkls[2].iteritems():
                # hist.Fill(value)        
        # for index, value in pklsUp[2].iteritems():
                # histUp.Fill(value)      
        # for index, value in pklsDown[2].iteritems():
                # histDown.Fill(value)    
        # plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["nominal","+1 #sigma","-1 #sigma"],-200,200,"fitted N_{S}","nSPure","systShift",Fit=False)
        
        # hist = TH1F("","",140,20,300)
        # histUp = TH1F("","",140,20,300)
        # histDown = TH1F("","",140,20,300)
        # for index, value in pkls[4].iteritems():
                        # hist.Fill(value)
        # for index, value in pklsUp[4].iteritems():
                        # histUp.Fill(value)
        # for index, value in pklsDown[4].iteritems():
                        # histDown.Fill(value)                    
        # plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["nominal","+1 #sigma","-1 #sigma"],30,300,"fitted m_{ll}^{edge} [GeV]","m0","systShift",Fit=True)
                        
        # hist = TH1F("","",100,0.975,1.225)
        # histUp = TH1F("","",100,0.975,1.225)
        # histDown = TH1F("","",100,0.975,1.225)
        # for index, value in pkls[8].iteritems():
                        # hist.Fill(value)
        # for index, value in pklsUp[8].iteritems():
                        # histUp.Fill(value)
        # for index, value in pklsDown[8].iteritems():
                        # histDown.Fill(value)
        # plotToyPlot([hist,histUp,histDown],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["nominal","+1 #sigma","-1 #sigma"],0.955,1.225,"fitted R_{SF/DF}","rSFDF","systShift",Fit=True)


                        
        ### Fits for background only toys with and without floating edge position
        
        # pkls = loadToysAdditional("Scale1Mo150SignalN0_MC_Triangle_allowNegSignalSFOS")
        # pklsFixed = loadToysAdditional("Scale1Mo150SignalN0_FixedEdge_150.0_MC_Triangle_allowNegSignalSFOS")
        
        # hist = TH1F("","",100,-10,10)
        # histFixed = TH1F("","",100,-10,10)
        # for index, value in pkls[2].iteritems():
                # hist.Fill(value/pkls[3][index]) 
        # for index, value in pklsFixed[2].iteritems():
                # histFixed.Fill(value/pklsFixed[3][index])       
        # plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],-10,10,"fitted N_{S} / #sigma_{N_{S}}","nS","floatVsFixed",Fit=True,RMSForFloat=True)

        # hist = TH1F("","",100,-100,100)
        # histFixed = TH1F("","",100,-100,100)
        # for index, value in pkls[2].iteritems():
                # hist.Fill(value)
        # for index, value in pklsFixed[2].iteritems():
                # histFixed.Fill(value)           
        # plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],-150,150,"fitted N_{S}","nSPure","floatVsFixed",Fit=True,RMSForFloat=True)
        
        # hist = TH1F("","",140,20,300)
        # histFixed = TH1F("","",140,20,300)
        # for index, value in pkls[4].iteritems():
                       # hist.Fill(value)
        # for index, value in pklsFixed[4].iteritems():
                       # histFixed.Fill(value)                   
        # plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],30,300,"fitted m_{ll}^{edge} [GeV]","m0","floatVsFixed",Fit=True)
                                        
        # hist = TH1F("","",100,0.975,1.225)
        # histFixed = TH1F("","",100,0.975,1.225)
        # for index, value in pkls[8].iteritems():
                       # hist.Fill(value)
        # for index, value in pklsFixed[8].iteritems():
                       # histFixed.Fill(value)
        # plotToyPlot([hist,histFixed],[ROOT.kBlack,ROOT.kBlue],["floating edge","fixed edge"],0.975,1.225,"fitted R_{SF/DF}","rSFDF","floatVsFixed",Fit=True)

        
        ### Difference in log likelihood between s+b (H1) and b-only (H0) hypothesis
        ### taken from main fit. Could rewrite it to read the pickles directly
        ### but the nomenclature differs a bit from the one used in toys
        ### and we wanted to avoid double structures
        # observed_deltaNll = -2*(1708.7819094781976-1711.642020093571)  # allowing negative, edge at 34.4                        
        observed_deltaNll = -2*(1710.8428064756974-1711.6420200936084)  # for positive signal, edge at 294.3                      
        
        ### Using toys with randomized initial value makes more sense for BG only, 
        ### but the difference is usually small
        pkls = loadToys("Scale1Mo300SignalN0_MC_Triangle_allowNegSignal_randM0SFOS")
        pklsFixed = loadToys("Scale1Mo300SignalN0_FixedEdge_34.4_MC_Triangle_allowNegSignalSFOS")      
        plotPValues(pkls,pklsFixed,illustrate=True,FitLabels=False,observedValue=observed_deltaNll,observedValueFixed=observed_deltaNll)
        
        ### bkg only Chi^2/ndf plots for toys based on step function / fitted EM distribution
        
        # observed_chisquare = 0.7441906347649522
        # pklsSmooth = loadToysAdditional("Scale1Mo300SignalN0_Triangle_allowNegSignalSFOS")
        # pklsStep   = loadToysAdditional("Scale1Mo300SignalN0_Hist_Triangle_allowNegSignalSFOS")
        
        # plotChiSquares(pklsSmooth,pklsStep,illustrate=True,observedValue=observed_chisquare)

        ### Studies with injected signal
        #pkls = loadToys("Scale1Mo150SignalN70_MC_Triangle_allowNegSignalSFOS")
        #hist = TH1F("","",60,-4,8)
        #for index, value in pkls[2].iteritems():
                #hist.Fill(value/pkls[3][index])                 
        #plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],-3.5,9,"fitted N_{S} / #sigma_{N_{S}}","nS","signalInjected",Fit=True)

        #hist = TH1F("","",70,-100,250)
        #for index, value in pkls[2].iteritems():
                        #hist.Fill(value)
        #plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],-75,250,"fitted N_{S}","nSPure","signalInjected",Fit=True)
                
        #hist = TH1F("","",80,110,190)
        #for index, value in pkls[4].iteritems():
                        #hist.Fill(value)
        #plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],110,190,"fitted m_{ll}^{edge} [GeV]","m0","signalInjected",Fit=True)
                        
        #hist = TH1F("","",100,0.975,1.225)
        #for index, value in pkls[8].iteritems():
                        #hist.Fill(value)
        #plotToyPlot([hist],[ROOT.kBlack],["Signal injected"],0.975,1.225,"fitted R_{SF/DF}","rSFOF","signalInjected",Fit=True)


        ### Compare initial and fitted edge for BG only and S+B
        # pklsBgOnly = loadToysAdditional("Scale1Mo150SignalN0_MC_Triangle_allowNegSignal_randM0SFOS")
        # pklsSigInjected = loadToysAdditional("Scale1Mo150SignalN50_MC_Triangle_allowNegSignal_randM0SFOS")
        # hist = TH2F("initialVsFittedHist","initialVsFittedHist; initial value of m_{ll}^{edge}; final value of m_{ll}^{edge}; N_{fit results}",75,0,300,75,0,300)
        # histSig = TH2F("initialVsFittedHist","initialVsFittedHist; initial value of m_{ll}^{edge}; final value of m_{ll}^{edge}; N_{fit results}",75,0,300,75,0,300)
        
        # for index, value in pklsBgOnly[4].iteritems():
               # hist.Fill(pklsBgOnly[11][index],value)  
        # plotToyPlot2D(hist,35,300,35,300,"initial value of m_{#kern[1.2]{ }ll}^{edge}","final value of m_{#kern[1.2]{ }ll}^{edge}","initialM0","fittedM0","backgroundOnly_m0100_allowNeg_randM0")
        
        # for index, value in pklsSigInjected[4].iteritems():
               # histSig.Fill(pklsSigInjected[11][index],value)  
        # plotToyPlot2D(histSig,35,300,35,300,"initial value of m_{#kern[1.2]{ }ll}^{edge}","final value of m_{#kern[1.2]{ }ll}^{edge}","initialM0","fittedM0","signalInjectedM150N70_randM0",mean=150,horizontal=True)


        

        ### Toys with different shapes, not used since 2012 data
        
        #~ pkls = loadToys("Scale1Mo70SignalN125_MC_Triangle_allowNegSignalSFOSCentral")
        #~ pklsConcave = loadToys("Scale1Mo70SignalN125_MC_Triangle_Concave_allowNegSignalSFOSCentral")
        #~ pklsConvex = loadToys("Scale1Mo70SignalN125_MC_Triangle_Convex_allowNegSignalSFOSCentral")
        
        #~ hist = TH1F("","",50,-10,10)
        #~ histConcave = TH1F("","",50,-10,10)
        #~ histConvex = TH1F("","",50,-10,10)
        #~ for index, value in pkls[2].iteritems():
                        #~ hist.Fill(value/pkls[3][index])      
        #~ for index, value in pklsConcave[2].iteritems():
                        #~ histConcave.Fill(value/pklsConcave[3][index])        
        #~ for index, value in pklsConvex[2].iteritems():
                        #~ histConvex.Fill(value/pklsConvex[3][index])  
        #~ plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],-2,10,"fitted N_{S} / #sigma_{N_{S}}","nS","shapeBias",Fit=True)
#~  
        #~ hist = TH1F("","",40,-50,350)
        #~ histConcave = TH1F("","",40,-50,350)
        #~ histConvex = TH1F("","",40,-50,350)
        #~ for index, value in pkls[2].iteritems():
                        #~ hist.Fill(value)     
        #~ for index, value in pklsConcave[2].iteritems():
                        #~ histConcave.Fill(value)      
        #~ for index, value in pklsConvex[2].iteritems():
                        #~ histConvex.Fill(value)       
        #~ plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],-50,350,"fitted N_{S}","nSPure","shapeBias",Fit=True)

#~ 
        #~ hist = TH1F("","",140,20,300)
        #~ histConcave = TH1F("","",140,20,300)
        #~ histConvex = TH1F("","",140,20,300)
        #~ for index, value in pkls[4].iteritems():
                        #~ hist.Fill(value)
        #~ for index, value in pklsConcave[4].iteritems():
                        #~ histConcave.Fill(value)
        #~ for index, value in pklsConvex[4].iteritems():
                        #~ histConvex.Fill(value)
        #~ plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],30,100,"fitted m_{ll}^{max}","m0","shapeBias",Fit=True)
#~ 
        #~ hist = TH1F("","",80,0.8,1.2)
        #~ histConcave = TH1F("","",80,0.8,1.2)
        #~ histConvex = TH1F("","",80,0.8,1.2)
        #~ for index, value in pkls[8].iteritems():
                        #~ hist.Fill(value)
        #~ for index, value in pklsConcave[8].iteritems():
                        #~ histConcave.Fill(value)
        #~ for index, value in pklsConvex[8].iteritems():
                        #~ histConvex.Fill(value)
        #~ plotToyPlot([hist,histConcave,histConvex],[ROOT.kBlack,ROOT.kRed,ROOT.kBlue],["triangle","concave","convex"],0.8,1.2,"fitted R_{SF/OF}","rSFOF","shapeBias",Fit=True)
#~      
        

        
main()
