#!/usr/bin/env python

#=======================================================
# Project: LocalAnalysis
#                         SUSY Same Sign Dilepton Analysis
#
# File: dataInterface.py
#
# Author: Daniel Sprenger
#                daniel.sprenger@cern.ch
#=======================================================


from messageLogger import messageLogger as log

import ROOT
from ROOT import TFile, TH1F

import os, ConfigParser
from math import sqrt
import datetime

from locations import locations
from helpers import *


ROOT.gROOT.ProcessLine(\
                                           "struct MyDileptonTreeFormat{\
                                                 Double_t inv;\
                                                 Double_t chargeProduct;\
                                                 Int_t nJets;\
                                                 Double_t ht;\
                                                 Double_t met;\
                                                 Double_t MT2;\
                                                 Double_t pt1;\
                                                 Double_t pt2;\
                                                 Double_t weight;\
                                                };")
from ROOT import MyDileptonTreeFormat


class InfoHolder(object):
        class DataTypes(object):
                Unknown = -1
                Data = 1
                DataFake = 2
                MC = 10
                MCSignal = 11
                MCBackground = 12
                MCFake = 13
                EMuBackground = 20

        theHistograms = {
                'chargeProduct': "",
                'ht': "MET/HT",
                'met': "MET/MET",
                'MHT': "MET/MHT",

                'MET vs HT': "MET/MET - HT",
                'MET vs MHT': "MET/MET - MHT",

                'nJets': "Multiplicity/JetMultiplicity",
                'nBJets': "",

                'nVertices': "nVErtices",

                #'Trigger': "Trigger paths",

                # for trees
                'p4.M()': "p4.M()",
                'lumiSec': "lumiSec",
}

        theStandardColors = {
                'LM0': "Red",
                #'LM1': "Red",
                'LM1': "DarkGreen",
                'LM2': "Red",
                #'LM3': "Red",
                'LM3': "DarkGreen",
                'LM4': "Red",
                'LM5': "Red",
                #'LM6': "Red",
                'LM6': "DarkGreen",
                'LM7': "Red",
                'LM8': "Red",
                'LM9': "Red",
                'LM13': "DarkRed",
                'T3lh': "DarkGreen",
                'QCD': "Magenta",
                'QCD100': "Magenta",
                'QCD250': "Magenta",
                'QCD500': "Magenta",
                'QCD1000': "Magenta",
                #'WJets': "Orange",
                'WJets': "W11WJets",
                #'ZJets': "MyBlue",
                'ZJets': "W11ZLightJets",
                'AStar': "DarkOrange",
                #'Diboson': "DarkOrange",
                'Diboson': "W11Diboson",
                'DibosonMadgraph': "W11Diboson",
                #'TTJets': "MyGreen",
                'TTJets': "W11ttbar",
                'SingleTop': "W11singlet",
                'JetMETTau': "Black",
                'EG': "Black",
                'ElectronHad': "Black",
                'DoubleEle': "Black",
                'Mu': "Black",
                'MuHad': "Black",
                'DoubleMu': "Black",
                'Data': "Black",
                'DataMET': "Black",
                'DataSS': "Black",
                'DataFake': "Black",
                'DataFakeUpper': "Black",
                'DataFakeLower': "Black",
                'MCFake': "Brown",
        }


        theSampleDescriptions = {
                'ZJets': "Z+jets",
                'TTJets': "t#bar{t}+jets",
                'SingleTop': "t / #bar{t}+jets",
                'DibosonMadgraph': "WW, WZ, ZZ",
                'DataFake': "Fake leptons",
                'Rare': "Rare SM",
        }

        theXSectionUncertainty = {
                'ZJets': 0.0433,
                'TTJets': 0.1511,
                'SingleTop': 0.0604, # maximum relative uncertainty of all t processes
                'DibosonMadgraph': 0.0385, # uncertainty of WZ process
                'Rare': 0.5, # Conservative  uncertainty on ttV, VVV, etc...
                                                          }


class DataInterface(object):
        def __init__(self,runRanges):
                
                self.runRanges = runRanges
                import ConfigParser
                self.cfg = ConfigParser.ConfigParser()
                

        # static methods
        #==========
        def getTasksFromRootfile(filePath):
                file = TFile(filePath, 'READ')
                keys = file.GetListOfKeys()
                keyNames = [key.GetName() for key in keys]
                #log.logDebug("%s" % keyNames)
                file.Close()

                return keyNames

        getTasksFromRootfile = staticmethod(getTasksFromRootfile)


        def convertDileptonTree(tree, nMax= -1, weight=1.0, selection="", weightString=""):
                # TODO: make selection more efficient
                log.logDebug("Converting DileptonTree")

                data = MyDileptonTreeFormat()
                newTree = ROOT.TTree("treeInvM", "Dilepton Tree")
                newTree.SetDirectory(0)
                newTree.Branch("inv", ROOT.AddressOf(data, "inv"), "inv/D")
                newTree.Branch("chargeProduct", ROOT.AddressOf(data, "chargeProduct"), "chargeProduct/D")
                newTree.Branch("nJets", ROOT.AddressOf(data, "nJets"), "nJets/I")
                newTree.Branch("ht", ROOT.AddressOf(data, "ht"), "ht/D")
                newTree.Branch("met", ROOT.AddressOf(data, "met"), "met/D")
                newTree.Branch("MT2", ROOT.AddressOf(data, "MT2"), "MT2/D")
                newTree.Branch("pt1", ROOT.AddressOf(data, "pt1"), "pt1/D")
                newTree.Branch("pt2", ROOT.AddressOf(data, "pt2"), "pt2/D")
                newTree.Branch("weight", ROOT.AddressOf(data, "weight"), "weight/D")
                
                
                # only part of tree?
                iMax = tree.GetEntries()
                if (nMax != -1):
                        iMax = min(nMax, iMax)
                
                # Fill tree
                for i in xrange(iMax):
                        if (tree.GetEntry(i) > 0):
                                ### depending on the sample we have to switch between p4.M() and mll
                                #~ data.inv = tree.p4.M()
                                data.inv = tree.mll
                                data.chargeProduct = tree.chargeProduct
                                data.nJets = tree.nJets
                                data.ht = tree.ht
                                data.met = tree.met
                                data.MT2 = tree.MT2
                                data.pt1 = tree.pt1
                                data.pt2 = tree.pt2
                                if (weightString != ""):
                                        eventWeight = eval(weightString)
                                        data.weight = eventWeight
                                else:
                                        data.weight = weight
                                newTree.Fill()
                

                #return newTree
                return newTree.CopyTree(selection)

        convertDileptonTree = staticmethod(convertDileptonTree)

        def convertTree(tree, nMax= -1):
                ROOT.gROOT.ProcessLine(\
                                                           "struct MyDataFormat{\
                                                                 Double_t invM;\
                                                                 Int_t chargeProduct;\
                                                                };")
                from ROOT import MyDataFormat
                data = MyDataFormat()
                newTree = ROOT.TTree("treeInvM", "Invariant Mass Tree")
                newTree.Branch("invM", ROOT.AddressOf(data, "invM"), "invM/D")
                newTree.Branch("chargeProduct", ROOT.AddressOf(data, "chargeProduct"), "chargeProduct/I")

                # only part of tree?
                iMax = tree.GetEntries()
                if (nMax != -1):
                        iMax = min(nMax, iMax)

                # Fill tree
                for i in xrange(iMax):
                        if (tree.GetEntry(i) > 0):
                                #~ data.invM = tree.p4.M()
                                data.invM = tree.mll
                                data.chargeProduct = tree.chargeProduct
                                newTree.Fill()

                newTree.SetDirectory(0)
                return newTree

        convertTree = staticmethod(convertTree)


        def isHistogramInFile(self, fileName, path):
                log.logDebug("Checking path '%s'\n  in file %s" % (path, fileName))

                file = TFile(fileName, 'READ')
                path = file.Get(path)

                return (path != None)


        def getHistogramFromFile(self, fileName, histoPath):
                log.logDebug("Getting histogram '%s'\n  from file %s" % (histoPath, fileName))

                file = TFile(fileName, 'READ')
                histogram = file.Get(histoPath)

                if (histogram == None):
                        log.logError("Could not get histogram '%s'\n  from file %s" % (histoPath, fileName))
                        file.Close()
                        return None
                else:
                        histogram.SetDirectory(0)
                        histogram.Sumw2()
                        file.Close()
                        return histogram


        def getTreeFromDataset(self, dataset, dilepton, cut="", useNLL=False):
                tree = ROOT.TChain()
                baseCut = cut
                for runRange in self.runRanges:
                        if useNLL:
                                path = locations[runRange.era].dataSetPathNLL
                        else:
                                path = locations[runRange.era].dataSetPath
                        log.logDebug("Adding %s tree from %s"%(dataset, path))
                        ROOT.TH1.AddDirectory(False)
                        tmpTree = readTrees(path, dilepton)[dataset]
                        ROOT.TH1.AddDirectory(True)
                        tree.Add(tmpTree)
   
                runCuts = []
                runCut = ""
                for runRange in self.runRanges:
                        runCuts.append(runRange.runCut[3:])
                
                if useNLL:
                        runCuts.append("vetoHEM == 1")
                runCut = "&& (%s)"%(" || ".join(runCuts))
                
                cut = cut + runCut
                
                print tree.GetEntries()
                
                if (cut != ""):
                        log.logDebug("Cutting tree down to: %s" % cut)
                        #tree = tree.CopyTree(cut, "", 1000)
                        tree = tree.CopyTree(cut)
                        #log.logError("Tree size: %d entries" % (tree.GetEntries()))

                if (tree != None):
                        tree.SetDirectory(0)
                else:
                        log.logError("Tree invalid")
                return tree


        def getTreeFromJob(self, job, dilepton, cut="", useNLL=False):
                if len(self.runRanges) > 1:
                        log.logError("Should only have one runRange when calling getTreeFromJob")
                
                runRange = self.runRanges[0]
                
                if useNLL:
                        path = locations[runRange.era].dataSetPathNLL
                else:
                        path = locations[runRange.era].dataSetPath
                tree = ROOT.TChain()
                tree.Add(readTrees(path, dilepton)[job])
                
                cut = cut + runRange.runCut
                if useNLL:
                        cut = cut + " && vetoHEM == 1"
                
                if (cut != ""):
                        log.logDebug("Cutting tree down to: %s" % cut)
                        if tree.GetEntries() > 0:
                                tree = tree.CopyTree(cut)
                        log.logError("Tree size: %d entries" % (tree.GetEntries()))
                
                if (tree != None):
                        tree.SetDirectory(0)
                
                return tree
                
        
        def getSignalTreeFromJob(self, job, dilepton, cut="", useNLL=False):
                if len(self.runRanges) > 1:
                        log.logError("Should only have one runRange when calling getTreeFromJob")
                
                runRange = self.runRanges[0]
                
                signalType = job.split("_")[0]
                
                append = {}
                append["2016"] = "_Summer16"
                append["2017"] = "_Fall17"
                append["2018"] = "_Autumn18"
                
                if useNLL:
                        path = locations[runRange.era]["dataSetPathSignalNLL%s"%signalType]
                else:
                        path = locations[runRange.era]["dataSetPathSignal%s"%signalType]
                tree = ROOT.TChain()
                tree.Add(readTrees(path, dilepton)[job+append[runRange.era]])
                
                if (cut != ""):
                        log.logDebug("Cutting tree down to: %s" % cut)
                        if tree.GetEntries() > 0:
                                tree = tree.CopyTree(cut)
                        log.logError("Tree size: %d entries" % (tree.GetEntries()))
                
                if (tree != None):
                        tree.SetDirectory(0)
                
                return tree
                
        


        def logMemoryContent(self):
                directory = ROOT.gDirectory
                list = directory.GetList()
                keyNames = [key.GetName() for key in list]
                log.logDebug("Memory content:%s" % keyNames)



class Result:
        # for integral calculation
        xMax = 10000
        # formatting string for result to string conversion
        formatString = "%.3f \pm %.3f"

        def __init__(self, histogram):
                if (histogram == None):
                        log.logWarning("Creating a result from an empty histogram.")


                # default configuration
                self.dataName = "None"
                self.dataVersion = "None"
                self.taskName = "None"
                self.flagName = "None"
                self.dataType = InfoHolder.DataTypes.Unknown
                self.is2DHistogram = False
                self.scaled = False

                self.histogram = histogram
                #self.histogram.Sumw2()
                self.unscaledIntegral = -1
                self.scalingFactor = -1
                self.luminosity = -1
                self.xSection = -1
                self.kFactor = -1
                self.nEvents = -1
                self.__scaledAndAdded = False
                self.currentIntegralError = -1

                self.title = None

                #log.logDebug("%s" % type(histogram))
                self.is2DHistogram = False
                if (type(histogram) == ROOT.TH2F):
                        log.logDebug("2D histogram found: %s" % type(histogram))
                        self.is2DHistogram = True

        def clone(self):
                if (self.is2DHistogram):
                        log.logError("Cloning of 2d histograms not supported!")
                        return None

                cloneHistogram = ROOT.TH1F(self.histogram)
                clone = Result(cloneHistogram)
                clone.dataName = self.dataName
                clone.dataVersion = self.dataVersion
                clone.taskName = self.taskName
                clone.flagName = self.flagName
                clone.dataType = self.dataType
                clone.scaled = self.scaled

                clone.unscaledIntegral = self.unscaledIntegral
                clone.scalingFactor = self.scalingFactor
                clone.luminosity = self.luminosity
                clone.xSection = self.xSection
                clone.kFactor = self.kFactor
                clone.nEvents = self.nEvents
                clone.__scaledAndAdded = self.__scaledAndAdded
                clone.currentIntegralError = self.currentIntegralError

                clone.title = self.title

                # not supported
                self.is2DHistogram = False
                return clone

        def setXSection(self, xSection):
                if (xSection <= 0.0):
                        log.logError("Cannot set result cross section to zero or less (%f)" % xSection)
                else:
                        self.xSection = xSection

        def integral(self):
                #log.logDebug("bin1: %f" % self.histogram.GetBinContent(1))

                #a = self.histogram.GetBinContent(1)
                #if (a == ):
                #       log.logError("NAN!")

                try:
                        min = 0
                        binMin = self.histogram.FindBin(min)
                        binMax = self.histogram.FindBin(Result.xMax)
                        return self.histogram.Integral(binMin, binMax)
                except:
                        log.logError("Cannot get histogram integral")
                        return - 1

        def integralError(self):
                if (self.currentIntegralError >= 0.0):
                        return self.currentIntegralError
                if (self.is2DHistogram):
                        log.logError("Integral error not implemented for 2D histograms.")
                        return - 1

                if (self.scaled):
                        # have differently scaled histograms been added? (cannot calculate error the usual way)
                        if (self.__scaledAndAdded):
                                log.logError("Result scaled and added, but integral error value not set.")
                                return - 1
                        # usual way
                        if (self.unscaledIntegral < 0 or self.scalingFactor < 0):
                                log.logWarning("Could not determine integral error: unscaled integral or scaling factor not set!")
                                return - 1

                        #log.logDebug("Scaled Error: sqrt(%f) * %f = %f" % (self.unscaledIntegral, self.scalingFactor, sqrt(self.unscaledIntegral) * self.scalingFactor))
                        return sqrt(self.unscaledIntegral) * self.scalingFactor
                else:
                        return sqrt(self.integral())

        def scale(self, factor):
                if (self.histogram == None):
                        log.logError("Trying to scale empty result")
                        return
                if (self.is2DHistogram):
                        log.logError("Scaling not implemented for 2D histograms.")
                        return

                self.histogram.Scale(factor)
                #log.logDebug("Result: Scaling factor = %f" % (self.scalingFactor))
                if (self.scalingFactor < 0):
                        self.scalingFactor = factor
                else:
                        self.scalingFactor *= factor

                if (self.currentIntegralError > 0.0):
                        self.currentIntegralError *= factor

                #log.logDebug("Result: Scaling factor afterwards = %f" % (self.scalingFactor))
                self.scaled = True

        def addResult(self, result):
                if (self.histogram == None):
                        log.logWarning("Adding to empty result!")
                        if (result.histogram == None): log.logWarning("... also adding empty result!")
                        return result
                if (result.histogram == None):
                        log.logWarning("Adding empty result!")
                        return self

                if (not self.scaled == result.scaled):
                        log.logError("Cannot add scaled and unscaled results")
                        return None

                if (self.dataType != result.dataType):
                        log.logError("Cannot add results of different data types (%d, %d)" % (self.dataType, results.dataType))
                        return None

                # lumi info
                if (self.luminosity > 0 and result.luminosity > 0):
                        if (self.dataType == InfoHolder.DataTypes.Data):
                                self.luminosity += result.luminosity # for data
                        else:
                                pass # for MC and Unknown
                else:
                        log.logWarning("Adding results without complete luminosity information (%f, %f)" % (self.luminosity, result.luminosity))
                        self.luminosity = -1

                # xSection info
                if (self.xSection > 0 and result.xSection > 0):
                        self.xSection += result.xSection
                else:
                        if (self.dataType != InfoHolder.DataTypes.Data):
                                log.logWarning("Adding results without complete xSection information (%f, %f)" % (self.xSection, result.xSection))
                        self.xSection = -1

                # xSection info
                if (self.kFactor > 0 and result.kFactor > 0):
                        if (self.kFactor != result.kFactor):
                                log.logHighlighted("Adding results with different kFactors (%f, %f). Will not be able to track this any more." % (self.kFactor, result.kFactor))
                                self.kFactor = -1
                else:
                        log.logInfo("Adding results without complete kFactor information (%f, %f)" % (self.kFactor, result.kFactor))
                        self.kFactor = -1

                if (not self.scaled):
                        self.histogram.Add(result.histogram)
                        return self
                if (self.scalingFactor == result.scalingFactor):
                        self.unscaledIntegral += result.unscaledIntegral
                        self.histogram.Add(result.histogram)
                        return self

                log.logDebug("Combining results: %s, %s" % (str(self), str(result)))
                # first calculate new error
                self.currentIntegralError = sqrt(self.integralError() * self.integralError() + result.integralError() * result.integralError())
                # then change histogram
                self.histogram.Add(result.histogram)
                self.unscaledIntegral += result.unscaledIntegral
                self.scalingFactor = -1
                # finally mark result as scaled and added
                self.__scaledAndAdded = True
                log.logDebug("... to: %s" % (str(self)))
                return self

        def divideByResult(self, result):
                #if (self.dataType != InfoHolder.DataTypes.Data or result.dataType != InfoHolder.DataTypes.Data):
                #       log.logError("Result division only implemented for data results!")
                #       return None
                if (self.luminosity != result.luminosity):
                        log.logWarning("Dividing results with unlike luminosity!")

                #self.histogram.Divide(result.histogram)
                self.histogram.Divide(self.histogram, result.histogram, 1, 1, "B")

                return self


        def __str__(self):
                return Result.formatString % (self.integral(), self.integralError())


# entry point
if (__name__ == "__main__"):
        log.outputLevel = 5
        theDataInterface = dataInterface()
        histogram = theDataInterface.getHistogram("test", "cutsV2None", "LM0", InfoHolder.theHistograms['electron pt'])


