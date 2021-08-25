import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import gROOT, gStyle
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import dataInterface
import tools
import math
import argparse 
import random

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



def prepareDatasets(inv,weight,trees,maxInv,minInv,typeName,nBinsMinv,rSFOF,rSFOFErr,theConfig, runRangeName):


        vars = ROOT.RooArgSet(inv, weight)
        

        # data
        
        tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(trees["EE"]), ROOT.RooFit.WeightVar("weight"))
        tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
        tmpEM = ROOT.RooDataSet("tmpEM", "tmpEM", vars, ROOT.RooFit.Import(trees["EM"]), ROOT.RooFit.WeightVar("weight"))
        tmpSFOS = ROOT.RooDataSet("tmpSFOS", "tmpSFOS", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
        tmpSFOS.append(tmpEE)

        
        dataEE = ROOT.RooDataSet("%sEE" % (typeName), "Dataset with invariant mass of di-electron pairs",
                                                         vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
        dataMM = ROOT.RooDataSet("%sMM" % (typeName), "Dataset with invariant mass of di-muon pairs",
                                                         vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
        dataSFOS = ROOT.RooDataSet("%sSFOS" % (typeName), "Dataset with invariant mass of SFOS lepton pairs",
                                                           vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
        dataEM = ROOT.RooDataSet("%sEM" % (typeName), "Dataset with invariant mass of EM lepton pairs",
                                                           vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEM))

        
        #~ histEM = createHistoFromTree(trees["EM"],"inv","weight*genWeight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
        #~ histEE = createHistoFromTree(trees["EE"],"inv","weight*genWeight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
        #~ histMM = createHistoFromTree(trees["MM"],"inv","weight*genWeight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
        #~ 
        histEM = createHistoFromTree(trees["EM"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 10,theConfig.minInv,theConfig.maxInv)
        histEE = createHistoFromTree(trees["EE"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 10,theConfig.minInv,theConfig.maxInv)
        histMM = createHistoFromTree(trees["MM"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 10,theConfig.minInv,theConfig.maxInv)
        
        histSFOS = histEE.Clone()
        histSFOS.Add(histMM)

        


        
        if theConfig.toyConfig["nToys"] > 0:
                log.logHighlighted("Preparing to dice %d Toys"%theConfig.toyConfig["nToys"])
                rand = ROOT.TRandom3()
                rand.SetSeed(0)
                
                wToys = ROOT.RooWorkspace("wToys", ROOT.kTRUE)
                wToys.factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
                wToys.factory("weight[1.,0.,10.]")
                vars = ROOT.RooArgSet(inv, wToys.var('weight'))
                
                selectShapes(wToys,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv, runRangeName)
                
                
                dataEE = ROOT.RooDataSet("%sEE" % (typeName), "Dataset with invariant mass of di-electron pairs",
                                                                 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
                dataMM = ROOT.RooDataSet("%sMM" % (typeName), "Dataset with invariant mass of di-muon pairs",
                                                                 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
                dataSFOS = ROOT.RooDataSet("%sSFOS" % (typeName), "Dataset with invariant mass of SFOS lepton pairs",
                                                                   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
                dataEM = ROOT.RooDataSet("%sEM" % (typeName), "Dataset with invariant mass of EM lepton pairs",
                                                                   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEM))          
                
                
                
                getattr(wToys, 'import')(dataEE, ROOT.RooCmdArg())
                getattr(wToys, 'import')(dataMM, ROOT.RooCmdArg())
                getattr(wToys, 'import')(dataSFOS, ROOT.RooCmdArg())
                getattr(wToys, 'import')(dataEM, ROOT.RooCmdArg())    
                

                                        
                wToys.factory("SUM::ofosShape(nB[100,0,100000]*ofosShape1)")
                fitEM = wToys.pdf('ofosShape').fitTo(wToys.data('%sEM'%(typeName)), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
                numEM = tmpEM.sumEntries()
                
                
                scale = theConfig.toyConfig["scale"]
                
                tmpNumEM = float(numEM*scale)
                tmpNumEM2 = float(numEM*scale)
                print "Signal EM %d"%tmpNumEM2
                print "Signal SFOS %d"%tmpNumEM
                
                #~ if theConfig.toyConfig["nSig"] > 0:
                        
                        
                
                zPrediction = theConfig.zPredictions.SF.MT2.inclusive.val
                print zPrediction, theConfig.toyConfig["nSig"], tmpNumEM
                fsFrac = tmpNumEM/(tmpNumEM+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
                zFrac = zPrediction*scale/(tmpNumEM+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
                sigFrac = theConfig.toyConfig["nSig"]*scale/(tmpNumEM+zPrediction+theConfig.toyConfig["nSig"]*scale)
                
                print fsFrac, zFrac, sigFrac
                
                wToys.factory("fsFrac[%s,%s,%s]"%(fsFrac,fsFrac,fsFrac))
                wToys.var('fsFrac').setConstant(ROOT.kTRUE)             
                wToys.factory("zFrac[%s,%s,%s]"%(zFrac,zFrac,zFrac))
                wToys.var('zFrac').setConstant(ROOT.kTRUE)      
                wToys.factory("sigFrac[%s,%s,%s]"%(sigFrac,sigFrac,sigFrac))
                wToys.var('sigFrac').setConstant(ROOT.kTRUE)    
                if theConfig.toyConfig["nSig"] > 0:
                        log.logHighlighted("Dicing %d Signal Events at %.1f GeV edge position"%(theConfig.toyConfig["nSig"],theConfig.toyConfig["m0"]))


                        
                        wToys.var('m0').setVal(theConfig.toyConfig["m0"])
                        if theConfig.toyConfig["sShape"] == "Concave":
                                log.logHighlighted("Dicing concave signal shape")
                                wToys.factory("SUSYX4Pdf::eeShapeForToys(inv,const,sEEl,m0)")
                                wToys.factory("SUSYX4Pdf::mmShapeForToys(inv,const,sMM,m0)")            
                                wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape, zFrac*zEEShape, sigFrac*eeShapeForToys)")
                                wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape, zFrac*zMMShape, sigFrac*mmShapeForToys)")
                                                                
                        elif theConfig.toyConfig["sShape"] == "Convex":
                                log.logHighlighted("Dicing convex signal shape")
                                wToys.factory("SUSYXM4Pdf::eeShapeForToys(inv,const,sEE,m0)")
                                wToys.factory("SUSYXM4Pdf::mmShapeForToys(inv,const,sMM,m0)")           
                                wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape, zFrac*zEEShape, sigFrac*eeShapeForToys)")
                                wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape, zFrac*zMMShape, sigFrac*mmShapeForToys)")
                                                        
                        else:
                                log.logHighlighted("Dicing triangular signal shape")    
                                wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape, zFrac*zEEShape, sigFrac*eeShape)")
                                wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape, zFrac*zMMShape, sigFrac*mmShape)")
                else:
                        wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape, zFrac*zEEShape)")
                        wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape, zFrac*zMMShape)")                                          
                        

                if theConfig.toyConfig["systShift"] == "Up":
                        tmpREEOF = theConfig.rEEOF.inclusive.val + theConfig.rEEOF.inclusive.val.err
                        tmpRMMOF = theConfig.rMMOF.inclusive.val + theConfig.rMMOF.inclusive.err
                        tmpRSFOF = theConfig.rSFOF.inclusive.val + theConfig.rSFOF.inclusive.err
                elif theConfig.toyConfig["systShift"] == "Down":
                        tmpREEOF = theConfig.rEEOF.inclusive.val - theConfig.rEEOF.inclusive.err
                        tmpRMMOF = theConfig.rMMOF.inclusive.val - theConfig.rMMOF.inclusive.err
                        tmpRSFOF = theConfig.rSFOF.inclusive.val - theConfig.rSFOF.inclusive.err
                else:
                        tmpREEOF = theConfig.rEEOF.inclusive.val
                        tmpRMMOF = theConfig.rMMOF.inclusive.val
                        tmpRSFOF = theConfig.rSFOF.inclusive.val
                        
                                
                eeFraction = tmpREEOF/tmpRSFOF          
                mmFraction = tmpRMMOF/tmpRSFOF          
                                
                genNumEE =  int((tmpNumEM*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*eeFraction)
                genNumMM =  int((tmpNumEM*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*mmFraction)
                
                result = genToys2013(wToys,theConfig.toyConfig["nToys"],genNumEE,genNumMM,int(tmpNumEM))
                
        else:
                result = [{"EE":dataEE,"MM":dataMM,"SFOS":dataSFOS,"EM":dataEM,"EEHist":histEE,"MMHist":histMM,"SFOSHist":histSFOS,"EMHist":histEM}]            
                
        return result   



def selectShapes(ws,backgroundShape,signalShape,nBinsMinv, runRangeName):


        resMuon = 1.0
        resElectron = 2.0
        # not used right now, resolutions are constant
        resMuonMin = 0.5
        resMuonMax = 2.0
        resElectronMin = 1.0
        resElectronMax = 3.0    
        # We know the z mass
        # z mass and width
        # mass resolution in electron and muon channels
        ws.factory("zmean[91.1876,89,93]")
        ws.var('zmean').setConstant(ROOT.kTRUE)
        ws.factory("zwidth[2.4952]")
        ws.factory("s[1.65,0.5,3.]")
        ws.var('s').setConstant(ROOT.kTRUE)
        ws.factory("sE[%f,%f,%f]" % (resElectron, resElectronMin, resElectronMax))
        ws.var('sE').setConstant(ROOT.kTRUE)
        ws.factory("sM[%f,%f,%f]" % (resMuon, resMuonMin, resMuonMax))
        ws.var('sM').setConstant(ROOT.kTRUE)
        
        ### IMPORTANT! If the bin size for the cache is not set to the same used in the the drell-yan fit, things get really fucked up! 
        ws.var("inv").setBins(240,"cache")      


        ws.factory("m0[55., 30., 500.]")
        ws.var('m0').setAttribute("StoreAsymError")
        ws.factory("m0Show[45., 0., 500.]")
        #ws.factory("m0[75., 75., 75.]")
        ws.factory("constant[45,20,100]")       
        
        cContinuumEE = tools.loadParameter("expofit", "dyExponent_EE", "expo",basePath="dyShelves/"+runRangeName+"/")
        cContinuumMM = tools.loadParameter("expofit", "dyExponent_MM", "expo",basePath="dyShelves/"+runRangeName+"/")
        cbMeanEE = tools.loadParameter("expofit", "dyExponent_EE", "cbMean",basePath="dyShelves/"+runRangeName+"/")
        cbMeanMM = tools.loadParameter("expofit", "dyExponent_MM", "cbMean",basePath="dyShelves/"+runRangeName+"/")
        nZEE = tools.loadParameter("expofit", "dyExponent_EE", "nZ",basePath="dyShelves/"+runRangeName+"/")
        nZMM = tools.loadParameter("expofit", "dyExponent_MM", "nZ",basePath="dyShelves/"+runRangeName+"/")
        zFractionEE = tools.loadParameter("expofit", "dyExponent_EE", "zFraction",basePath="dyShelves/"+runRangeName+"/")
        zFractionMM = tools.loadParameter("expofit", "dyExponent_MM", "zFraction",basePath="dyShelves/"+runRangeName+"/")
        nLEE = tools.loadParameter("expofit", "dyExponent_EE", "nL",basePath="dyShelves/"+runRangeName+"/")
        nLMM = tools.loadParameter("expofit", "dyExponent_MM", "nL",basePath="dyShelves/"+runRangeName+"/")
        nREE = tools.loadParameter("expofit", "dyExponent_EE", "nR",basePath="dyShelves/"+runRangeName+"/")
        nRMM = tools.loadParameter("expofit", "dyExponent_MM", "nR",basePath="dyShelves/"+runRangeName+"/")
        alphaLEE = tools.loadParameter("expofit", "dyExponent_EE", "alphaL",basePath="dyShelves/"+runRangeName+"/")
        alphaLMM = tools.loadParameter("expofit", "dyExponent_MM", "alphaL",basePath="dyShelves/"+runRangeName+"/")
        alphaREE = tools.loadParameter("expofit", "dyExponent_EE", "alphaR",basePath="dyShelves/"+runRangeName+"/")
        alphaRMM = tools.loadParameter("expofit", "dyExponent_MM", "alphaR",basePath="dyShelves/"+runRangeName+"/")
        sEE = tools.loadParameter("expofit", "dyExponent_EE", "s",basePath="dyShelves/"+runRangeName+"/")
        sMM = tools.loadParameter("expofit", "dyExponent_MM", "s",basePath="dyShelves/"+runRangeName+"/")
                        
        cContinuum = -0.017
        ws.factory("cContinuum[%f]" % (cContinuum))
        ws.factory("cContinuumEE[%f]" % (cContinuumEE))
        ws.factory("cContinuumMM[%f]" % (cContinuumMM))

        ws.factory("Exponential::offShellEE(inv,cContinuumEE)")                         
        ws.factory("Exponential::offShellMM(inv,cContinuumMM)")                         
        ws.factory("Exponential::offShell(inv,cContinuum)")     
                                


                                        
        ws.factory("zFractionMM[%f]"%zFractionMM)
        ws.factory("cbmeanMM[%f]"%cbMeanMM)                             
        ws.factory("sMM[%f]"%sMM)                                                                                                       
        ws.factory("nMML[%f]"%nLMM)
        ws.factory("alphaMML[%f]"%alphaLMM)
        ws.factory("nMMR[%f]"%nRMM)
        ws.factory("alphaMMR[%f]"%alphaRMM)             
        
        ws.factory("DoubleCB::cbShapeMM(inv,cbmeanMM,sMM,alphaMML,nMML,alphaMMR,nMMR)")


        ws.factory("cbmeanEE[%f]"%cbMeanEE)
        ws.factory("zFractionEE[%f]"%zFractionEE)
        ws.factory("sEE[%f]"%sEE)                               
        ws.factory("nEEL[%f]"%nLEE)
        ws.factory("alphaEEL[%f]"%alphaLEE)
        ws.factory("nEER[%f]"%nREE)
        ws.factory("alphaEER[%f]"%alphaREE)
        
        ws.factory("DoubleCB::cbShapeEE(inv,cbmeanEE,sEE,alphaEEL,nEEL,alphaEER,nEER)") 

        ws.factory("BreitWigner::bwShape(inv,zmean,zwidth)")
        
        convEE = ROOT.RooFFTConvPdf("peakModelEE","zShapeEE  (x) cbShapeEE ",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeEE"))
        getattr(ws, 'import')(convEE, ROOT.RooCmdArg())
        ws.pdf("peakModelEE").setBufferFraction(5.0)
        
        convMM = ROOT.RooFFTConvPdf("peakModelMM","zShapeMM  (x) cbShapeMM ",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeMM"))
        getattr(ws, 'import')(convMM, ROOT.RooCmdArg())
        ws.pdf("peakModelMM").setBufferFraction(5.0)
        

        ws.factory("expFractionMM[%f]"%(1-zFractionMM))         
        ws.factory("SUM::zMMShape(zFractionMM*peakModelMM,expFractionMM*offShellMM)")
        

        ws.factory("expFractionEE[%f]"%(1-zFractionEE))
        ws.factory("SUM::zEEShape(zFractionEE*peakModelEE,expFractionEE*offShellEE)")


        if backgroundShape == 'L':
                log.logHighlighted("Using Landau")
                ws.factory("Landau::ofosShape1(inv,a1[30,0,100],b1[20,0,100])")
        elif backgroundShape == 'CH':
                log.logHighlighted("Using Chebychev")
                ws.factory("Chebychev::ofosShape1(inv,{a1[0,-2,2],b1[0,-2,2],c1[0,-1,1],d1[0,-1,1]})")
                
                ws.Print()
                
        elif backgroundShape == 'CB':
                log.logHighlighted("Using crystall ball shape")
                ws.factory("CBShape::ofosShape1(inv,cbMean[50.,0.,200.],cbSigma[20.,0.,100.],alpha[-1,-10.,0.],n[100.])")
                                        
        elif backgroundShape == 'DSCB':
                log.logHighlighted("Using double sided crystall ball shape")
                ws.factory("DoubleCB::ofosShape1(inv,cbMean[50.,0.,200.],cbSigma[20.,0.,100.],alphaL[5.],nL[1.],alphaR[1.,0.,10.],nR[1.,0.,100.])")
                                        
                
        elif backgroundShape == 'B':
                log.logHighlighted("Using BH shape")
                ws.factory("SUSYBkgBHPdf::ofosShape1(inv,a1[1.],a2[1,0,400],a3[1,0,100],a4[0.1,-2,2])")
                                
        elif backgroundShape == 'B2':
                log.logHighlighted("Using BH2 shape")
                ws.factory("SUSYBkgBH2Pdf::ofosShape1(inv,a1[1.],a2[1,0,400],a3[1,0,100],a4[0.1,0,2])")
                
        elif backgroundShape == 'MD':
                log.logHighlighted("Using old shape")
                ws.factory("EXPR::ofosShape1('TMath::Power(inv,a1)*TMath::Exp(-b1*inv-b2*TMath::Power(inv,2))',inv,a1[1.0,0.,100.],b1[0.001,0.00001,100.],b2[0.001,0.000001,100.])") 
                
        elif backgroundShape == 'G':
                log.logHighlighted("Using old shape")
                ws.factory("SUSYBkgPdf::ofosShape1(inv,a1[1.6.,0.,8.],a2[0.1,-1.,1.],b1[0.028,0.001,1.],b2[1.],c1[0.],c2[1.])") #trying to get rid of paramteres
                
        elif backgroundShape == 'O':
                log.logHighlighted("Using old old shape")
                ws.factory("SUSYBkgPdf::ofosShape1(inv,a1[1.0,0.,400.],a2[1.],b1[0.01,0.00001,100.],b2[1.])")
                        
        elif backgroundShape == 'F':
                log.logHighlighted("Using new old shape")
                ws.factory("SUSYBkgMoreParamsPdf::ofosShape1(inv,a1[1.0,0.,400.],b1[1,0.00001,100.],c1[0.,-20.,30.])")
                
        elif backgroundShape == 'MA':
                log.logHighlighted("Using Marco-Andreas shape")                         
                ws.factory("SUSYBkgMAPdf::ofosShape1(inv,b1[-2000,-8000,8000],b2[120.,-800,800],b3[-1.,-5,5.],b4[0.01,-0.1,0.1], m1[50,20,100],m2[120,100,160])") #
                
        elif backgroundShape == 'ETH':
                log.logHighlighted("Using Marco-Andreas shape for real")
                ####### final -  never touch again!
                ws.factory("TopPairProductionSpline::ofosShape1(inv,b1[-1800,-5000,5000],b2[120.,-400,400],b4[0.0025,0.0001,0.01], m1[60.],m2[110.])") #
                ############    
                
        elif backgroundShape == 'P':
                log.logHighlighted("Gaussians activated!")
                ws.factory("SUSYBkgGaussiansPdf::ofosShape1(inv,a1[30.,0.,70.],a2[60.,20.,105.],a3[100.,-1000.,1000.],b1[15,10.,80.],b2[20.,10.,80.],b3[200.,10.,3000.])") #High MET
        
        elif backgroundShape == 'PT':
                log.logHighlighted("Gaussians plus exp activated!")
                ws.factory("RooSUSYBkgGaussiansPlusExpPdf::ofosShape1(inv,a1[30.,0.,700.],a2[60.,20.,1050.],a3[10,0,1000],b1[15,0.,80.],b2[20.,10.,80.],b3[-0.001,-1.,0.])") #High MET
                
        elif backgroundShape == "K":
                log.logHighlighted("Kernel Density Estimation activated")
                nameDataEM = "dataEM" 
                ws.factory("RooKeysPdf::ofosShape1(inv, %s, MirrorBoth)" % (nameDataEM))
                
        elif backgroundShape == "Hist":
                log.logHighlighted("HistSubtraction activated!")
                ws.var('inv').setBins(nBinsMinv)
                tempDataHist = ROOT.RooDataHist("dataHistEM", "dataHistEM", ROOT.RooArgSet(ws.var('inv')), ws.data("dataEM"))
                getattr(ws, 'import')(tempDataHist, ROOT.RooCmdArg())
                ws.factory("RooHistPdf::ofosShape1(inv, dataHistEM)")
                
        else:
                log.logHighlighted("No valid background shape selected, exiting")
                sys.exit()
                

        if signalShape == "Triangle":
                ws.factory("SUSYTPdf::sfosShape(inv,constant,s,m0)")
                ws.factory("SUSYTPdf::sfosShapeShow(inv,constant,s,m0Show)")
                ws.factory("SUSYTPdf::eeShape(inv,constant,sEE,m0)")
                ws.factory("SUSYTPdf::mmShape(inv,constant,sMM,m0)")
                ws.var('constant').setConstant(ROOT.kTRUE)
        elif signalShape == 'V' :
                ws.factory("Voigtian::sfosShape(inv,m0,zwidth,s)")
                ws.factory("Voigtian::eeShape(inv,m0,zwidth,sE)")
                ws.factory("Voigtian::mmShape(inv,m0,zwidth,sM)")
        elif signalShape == 'X4':
                ws.factory("SUSYX4Pdf::sfosShape(inv,constant,s,m0)")
                ws.factory("SUSYX4Pdf::sfosShapeShow(inv,constant,s,m0Show)")
                ws.factory("SUSYX4Pdf::eeShape(inv,constant,sEE,m0)")
                ws.factory("SUSYX4Pdf::mmShape(inv,constant,sMM,m0)")
                ws.var('constant').setConstant(ROOT.kTRUE)
        elif signalShape == 'XM4' in Holder.shape:
                ws.factory("SUSYXM4Pdf::sfosShape(inv,constant,s,m0)")
                ws.factory("SUSYXM4Pdf::sfosShapeShow(inv,constant,s,m0Show)")
                ws.factory("SUSYXM4Pdf::eeShape(inv,constant,sEE,m0)")
                ws.factory("SUSYXM4Pdf::mmShape(inv,constant,sMM,m0)")
                ws.var('constant').setConstant(ROOT.kTRUE)
        else:
                log.logHighlighted("No valid background shape selected, exiting")
                sys.exit()


def genToys2013(ws, nToys=10,genEE=0,genMM=0,genEM=0):
        theToys = []

        mcEE = ROOT.RooMCStudy(ws.pdf('backtoymodelEE'), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
        mcEE.generate(nToys, genEE, ROOT.kTRUE)
        mcMM = ROOT.RooMCStudy(ws.pdf("backtoymodelMM"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
        mcMM.generate(nToys, genMM, ROOT.kTRUE)
        mcEM = ROOT.RooMCStudy(ws.pdf("ofosShape"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
        mcEM.generate(nToys, genEM, ROOT.kTRUE)
        
        vars = ROOT.RooArgSet(ws.var('inv'), ws.var('weight'))

        
        for i in range(nToys):
                #toyEE = ws.pdf("mEE").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataEE').numEntries())
                #toyMM = ws.pdf("mMM").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataMM').numEntries())
                #toyEM = ws.pdf("backmodel").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataEM').numEntries())
                toyEE = mcEE.genData(i)
                toyMM = mcMM.genData(i)
                toyEM = mcEM.genData(i)
                toySFOS = toyEE.Clone()
                toySFOS.append(toyMM.Clone())
                #~ toyData = ROOT.RooDataSet("theToy_%s" % (i), "toy_%s" % (i), Holder.vars, ROOT.RooFit.Index(ws.cat('cat')),
                        #~ ROOT.RooFit.Import('EM', toyEM),
                        #~ ROOT.RooFit.Import('EE', toyEE),
                        #~ ROOT.RooFit.Import('MM', toyMM))
                toyDataEE = ROOT.RooDataSet("theToyEE_%s" % (i), "toyEE_%s" % (i), vars,ROOT.RooFit.Import(toyEE))
                toyDataMM = ROOT.RooDataSet("theToyMM_%s" % (i), "toyMM_%s" % (i), vars,ROOT.RooFit.Import(toyMM))
                toyDataEM = ROOT.RooDataSet("theToyEM_%s" % (i), "toyEM_%s" % (i), vars,ROOT.RooFit.Import(toyEM))
                toyDataSFOS = ROOT.RooDataSet("theToySFOS_%s" % (i), "toySFOS_%s" % (i), vars,ROOT.RooFit.Import(toySFOS))
                #toyData = mcTData.genData(i)
                #ws.var("nSig").setConstant(ROOT.kFALSE)
                #self.plotToy(ws,toyData)
                #ws.var("nSig").setConstant(ROOT.kTRUE)
                theToys.append({"EE":toyDataEE,"MM":toyDataMM,"EM":toyDataEM,"SFOS":toyDataSFOS})

        return theToys


def plotModel(w, data, fitEM, theConfig, pdf="model", tag="", frame=None, zPrediction= -1.0,
                          slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), cut=ROOT.RooCmdArg.none(),
                          overrideShapeNames={}):
        if (frame == None):
                frame = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
        frame.GetXaxis().SetTitle('m_{ll} [GeV]')
        #frame.GetYaxis().SetTitle(histoytitle)
        ROOT.RooAbsData.plotOn(data, frame, cut)
        w.pdf(pdf).plotOn(frame, slice, projWData)

        shapeNames = {
                                  'Z': "zShape",
                                  #~ 'offShell': "offShell",
                                  'Background': "ofosShape",
                                  'Signal': "sfosShape",
                                  }
        shapeNames.update(overrideShapeNames)
        nameBGShape = "displayedBackgroundShape"
        nameBGZShape = "displayedBackgroundShapeZ"
        #~ nameBGOffShellShape = "displayedBackgroundShapeOffShell"

        # get pdfs
        plotZ = ROOT.RooArgSet(w.pdf(shapeNames['Z']))
        #~ plotOffShell = ROOT.RooArgSet(w.pdf(shapeNames['offShell']))
        plotEM = ROOT.RooArgSet(w.pdf(shapeNames['Background']))
        plotSignal = ROOT.RooArgSet(w.pdf(shapeNames['Signal']))
        # different draw modes with and without z prediction
        zPrediction = 0.
        if (zPrediction > 0.0):
                fittedZ = w.var('nZ').getVal()
                zSignal = fittedZ - zPrediction
                log.logHighlighted("Z signal of %f = %f - %f (pred.)" % (zSignal, fittedZ, zPrediction))
                relScale = zSignal / fittedZ
                log.logDebug("Relative scale for Z signal: %f" % (relScale))
                w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotZ), ROOT.RooFit.Normalization(relScale, ROOT.RooAbsReal.Relative),
                                                          ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kViolet))
                # add Z prediction to ofos background
                relScale = zPrediction / fittedZ
                log.logDebug("Relative scale for Z prediction: %f" % (relScale))
                w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotZ), ROOT.RooFit.Normalization(relScale, ROOT.RooAbsReal.Relative), ROOT.RooFit.Name(nameBGZShape),
                                                          slice, projWData,
                                                          ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack), ROOT.RooFit.Invisible())
                #~ w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotOffShell), ROOT.RooFit.Name(nameBGOffShellShape),
                                                          #~ slice, projWData,
                                                          #~ ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kOrange+1))
                w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotEM), ROOT.RooFit.AddTo(nameBGZShape, 1.0, 1.0),
                                                  slice, projWData,
                                                  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack))
                if theConfig.plotErrorBands:                              
                        w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotEM), ROOT.RooFit.AddTo(nameBGZShape, 1.0, 1.0),
                                                          slice, projWData,
                                                          ROOT.RooFit.VisualizeError(fitEM, 1),
                                                          ROOT.RooFit.FillColor(ROOT.kGreen + 2),
                                                          ROOT.RooFit.FillStyle(3009),
                                                          ROOT.RooFit.LineWidth(2))
        else:
                # default draw mode, no z prediction
                w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotEM), ROOT.RooFit.Name(nameBGShape),
                                                  slice, projWData,
                                                  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack))
                if theConfig.plotErrorBands:
                        w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotEM),
                                                          slice, projWData,
                                                          ROOT.RooFit.VisualizeError(fitEM, 1),
                                                          ROOT.RooFit.FillColor(ROOT.kGreen + 2),
                                                          ROOT.RooFit.FillStyle(3009),
                                                          ROOT.RooFit.LineWidth(2))
                w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotZ),
                                                          slice, projWData,
                                                          ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kViolet))

        # plot edge signal component
        w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotSignal),
                                                  slice, projWData,
                                                  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
        
        return frame


def saveFitResults(ws,theConfig,x = None):
         
        if x == None:
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nS", ws.var('nSig').getVal(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nZ", ws.var('nZ').getVal(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nB", ws.var('nB').getVal(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "rSFOF", ws.var('rSFOF').getVal(),basePath=theConfig.shelvePath)           
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "m0", ws.var('m0').getVal(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sEM" %(theConfig.title), "chi2", parametersToSave["chi2EM"],basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sEM" %(theConfig.title), "nPar", parametersToSave["nParEM"],basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "chi2",parametersToSave["chi2SFOS"],basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nPar", parametersToSave["nParH1"],basePath=theConfig.shelvePath)          
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllH0", parametersToSave["minNllH0"],basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllH1", parametersToSave["minNllH1"],basePath=theConfig.shelvePath)                                                                                    
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllEM", parametersToSave["minNllEM"],basePath=theConfig.shelvePath)                                                                                        
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "initialM0", parametersToSave["initialM0"],basePath=theConfig.shelvePath)                          
                                                                  
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nSerror", ws.var('nSig').getError(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nSerrorHi", ws.var("nSig").getAsymErrorHi(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nSerrorLo", ws.var("nSig").getAsymErrorLo(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nZerror", ws.var('nZ').getError(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nBerror", ws.var('nB').getError(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "rSFOFerror", ws.var('rSFOF').getError(),basePath=theConfig.shelvePath)            
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "m0error", ws.var('m0').getError(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "m0errorHi", ws.var('m0').getAsymErrorHi(),basePath=theConfig.shelvePath)
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "m0errorLo", ws.var('m0').getAsymErrorLo(),basePath=theConfig.shelvePath)
                
                
                ws.var("inv").setRange("fullRange",20,300)
                ws.var("inv").setRange("lowMass",20,70)
                argSet = ROOT.RooArgSet(ws.var("inv"))
                
                fittedZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak"))
                fittedZ = fittedZInt.getVal()*ws.var("nZ").getVal()
                
                fittedLowMassZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
                fittedLowMassZ = fittedLowMassZInt.getVal()*ws.var("nZ").getVal()
                
                fittedLowMassSInt = ws.pdf("sfosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
                fittedLowMassS = fittedLowMassSInt.getVal()*ws.var("nSig").getVal()
                
                fittedLowMassBInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
                fittedLowMassB = fittedLowMassBInt.getVal()*ws.var("nB").getVal()*ws.var("rSFOF").getVal()

                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "onZZYield",fittedZ,basePath=theConfig.shelvePath)                         
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassZYield",fittedLowMassZ,basePath=theConfig.shelvePath)                              
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassSYield",fittedLowMassS,basePath=theConfig.shelvePath)                              
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassBYield",fittedLowMassB,basePath=theConfig.shelvePath)                              
                                                                  
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "onZZYielderror",fittedZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)                                
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassZYielderror",fittedLowMassZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)                             
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassSYielderror",fittedLowMassSInt.getVal()*ws.var("nSig").getError(),basePath=theConfig.shelvePath)                           
                tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassBYielderror",fittedLowMassBInt.getVal()*ws.var("nB").getError(),basePath=theConfig.shelvePath)                             
                                
        else:
                title = theConfig.title.split("_%s"%x)[0]
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nS", ws.var('nSig').getVal(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nZ", ws.var('nZ').getVal(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nB", ws.var('nB').getVal(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "rSFOF", ws.var('rSFOF').getVal(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "m0", ws.var('m0').getVal(), index = x)
                tools.updateParameter("edgefit", "%sEM" %(title), "chi2",parametersToSave["chi2EM"], index = x)
                tools.updateParameter("edgefit", "%sEM" %(title), "nPar",parametersToSave["nParEM"], index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "chi2",parametersToSave["chi2SFOS"], index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nPar",parametersToSave["nParH1"], index = x)               
                tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllH0", parametersToSave["minNllH0"], index = x)                                
                tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllH1", parametersToSave["minNllH1"], index = x)                                
                tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllEM", parametersToSave["minNllEM"], index = x)                            
                tools.updateParameter("edgefit", "%sSFOS" %(title), "initialM0", parametersToSave["initialM0"], index = x)      
                                                                         
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nSerror", ws.var('nSig').getError(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nZerror", ws.var('nZ').getError(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "nBerror", ws.var('nB').getError(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "rSFOFerror", ws.var('rSFOF').getError(), index = x)
                tools.updateParameter("edgefit", "%sSFOS" %(title), "m0error", ws.var('m0').getError(), index = x)
                                                                                        
                                                                

def prepareLegend(useMC,zPrediction,):
        # prepare legend
        dLeg = ROOT.TH1F()
        dLeg.SetMarkerStyle(ROOT.kFullCircle)
        dLeg.SetMarkerColor(ROOT.kBlack)
        dLeg.SetLineWidth(2)
        fitLeg = dLeg.Clone()
        fitLeg.SetLineColor(ROOT.kBlue)
        zLeg = dLeg.Clone()
        zLeg.SetLineStyle(2)
        zLeg.SetLineColor(ROOT.kGreen)
        sLeg = dLeg.Clone()
        sLeg.SetLineStyle(2)
        sLeg.SetLineColor(ROOT.kRed)
        bLeg = dLeg.Clone()
        bLeg.SetLineStyle(2)
        bLeg.SetLineColor(ROOT.kBlack)
        #~ oLeg = dLeg.Clone()
        #~ oLeg.SetLineStyle(2)
        #~ oLeg.SetLineColor(ROOT.kOrange + 2)
        #~ uLeg = dLeg.Clone()
        #~ uLeg.SetLineColor(ROOT.kGreen + 2)
        #~ uLeg.SetFillColor(ROOT.kGreen + 2)
        #~ uLeg.SetFillStyle(3009)
        lmLeg = dLeg.Clone()
        lmLeg.SetLineColor(ROOT.kViolet)
        lmLeg.SetLineStyle(ROOT.kDotted)

        nLegendEntries = 4

        sl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
        sl.SetTextAlign(22)
        if (useMC):
                sl.AddEntry(dLeg, 'Simulation', "pl")
        else:
                sl.AddEntry(dLeg, 'Data', "pl")
        sl.AddEntry(fitLeg, 'Fit', "l")

        if (zPrediction > 0.0):
                sl.AddEntry(sLeg, 'Edge signal', "l")
                zLeg.SetLineColor(ROOT.kViolet)
                sl.AddEntry(zLeg, 'Z signal', "l")
                sl.AddEntry(bLeg, 'FS Background', "l")
                #~ ol.AddEntry(bLeg, 'Off-Shell Drell-Yan', "l")
                #~ sl.AddEntry(uLeg, 'OF uncertainty', "f")
        else:
                sl.AddEntry(sLeg, 'Signal', "l")
                sl.AddEntry(zLeg, 'DY', "l")
                #sl.AddEntry(zLeg, 'Z^{0}/#gamma', "l")
                sl.AddEntry(bLeg, 'FS background', "l")
                #~ sl.AddEntry(uLeg, 'Uncertainty', "f")
                #sl.AddEntry(lmLeg, 'LM1 x 0.2', "l")
                
                
        nLegendEntries = 2
        bl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
        bl.SetTextAlign(22)
        
        if (useMC):
                bl.AddEntry(dLeg, 'Simulation', "pe")
        else:
                bl.AddEntry(dLeg, 'Data', "pe")
        bl.AddEntry(fitLeg, 'FS background', "l")
        #~ bl.AddEntry(uLeg, 'Uncertainty', "f")                
                        
        return [sl,bl]

def plotFitResults(ws,theConfig, lumi, frameEM,data,fitEM,H0=False):

        sizeCanvas = 800
        shape = theConfig.backgroundShape
        useMC = theConfig.useMC
        residualMode = theConfig.residualMode
        luminosity = lumi
        isPreliminary = theConfig.isPreliminary
        year = theConfig.year
        showText = theConfig.showText
        title = theConfig.title
        histoytitle = theConfig.histoytitle
        print year
        
        dLeg = ROOT.TH1F()
        dLeg.SetMarkerStyle(ROOT.kFullCircle)
        dLeg.SetMarkerColor(ROOT.kBlack)
        dLeg.SetLineWidth(2)
        fitLeg = dLeg.Clone()
        fitLeg.SetLineColor(ROOT.kBlue)
        bLeg = dLeg.Clone()
        bLeg.SetLineStyle(2)
        bLeg.SetLineColor(ROOT.kBlack)

                
                
        nLegendEntries = 2
        if theConfig.plotErrorBands:
                nLegendEntries =3
        bl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
        bl.SetTextAlign(22)
        
        if (useMC):
                bl.AddEntry(dLeg, 'Simulation', "pl")
        else:
                bl.AddEntry(dLeg, 'Data', "pl")
        bl.AddEntry(fitLeg, 'FS background', "l")
        if theConfig.plotErrorBands:
                bl.AddEntry(uLeg, 'Uncertainty', "f")
        

        ofosName = '%s/OFFit_%s_%s_%s.pdf' % (theConfig.figPath, shape, title)
        
        # determine y axis range
        #~ yMaximum = 1.2 * max(frameEM.GetMaximum(), frameSFOS.GetMaximum())
        yMaximum = 220
        if (theConfig.plotYMax > 0.0):
                yMaximum = theConfig.plotYMax


        # make EM plot
        #---------------
        print "before EM plot"
        
        frameEM = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of e#mu lepton pairs'))
        frameEM = plotModel(ws, data, fitEM, theConfig, pdf="combModel", tag="%sEM" % title, frame=frameEM, zPrediction=0.0,
                                                slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::EM"))
        frameEM.GetYaxis().SetTitle(histoytitle)
        cEM = ROOT.TCanvas("EM distribtution", "EM distribution", sizeCanvas, int(1.25 * sizeCanvas))
        cEM.cd()
        pads = formatAndDrawFrame(frameEM, theConfig, title="EM", pdf=ws.pdf("combModel"), yMax=yMaximum,
                                                        slice=ROOT.RooFit.Slice(ws.cat("cat"), "EM"),
                                                        projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
                                                        residualMode =residualMode)
        annotationsTitle = [
                                        (0.92, 0.57, "%s" % (theConfig.selection.latex)),
                                        ]
        tools.makeCMSAnnotation(0.18, 0.88, lumi, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
        #~ if (showText):
                #~ tools.makeAnnotations(annotationsTitle, color=tools.myColors['Grey'], textSize=0.03, align=31)
                
        if (showText):
                tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
        
        #~ dileptonAnnotation = [
                                                #~ (0.92, 0.27, "%s" % ("OCDF")),
                                                #~ ]
        #~ tools.makeAnnotations(dileptonAnnotation, color=ROOT.kBlack, textSize=0.04, align=31)
                
        bl.Draw()
        cEM.Print(ofosName)   
        for pad in pads:
                pad.Close()



def formatAndDrawFrame(frame, theConfig, title, pdf, yMax=0.0, slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), residualMode = "diff"):
        # This routine formats the frame and adds the residual plot.
        # Residuals are determined with respect to the given pdf.
        # For simultaneous models, the slice and projection option can be set.

        if (yMax > 0.0):
                frame.SetMaximum(yMax)
        frame.GetXaxis().SetRangeUser(theConfig.plotMinInv, theConfig.plotMaxInv)
        pad = ROOT.TPad("main%s" % (title), "main%s" % (title), 0.01, 0.25, 0.99, 0.99)
        ROOT.SetOwnership(pad, False)
        pad.SetNumber(1)
        pad.Draw()
        resPad = ROOT.TPad("residual%s" % (title), "residual%s" % (title), 0.01, 0.01, 0.99, 0.25)
        ROOT.SetOwnership(resPad, False)
        resPad.SetNumber(2)
        resPad.Draw()
        pad.cd()
        #~ pad.DrawFrame(Holder.plotMinInv,1,Holder.plotMaxInv,yMax,";m_{ll} [GeV];Events / 5 GeV")     
        frame.Draw()
        resPad.cd()
        residualMaxY = 20.
        residualTitle = "data - fit"
        if residualMode == "pull":
                residualMaxY = 3.
                residualTitle = "#frac{(data - fit)}{#sigma_{data}}"
        hAxis = resPad.DrawFrame(theConfig.plotMinInv, -residualMaxY, theConfig.plotMaxInv, residualMaxY, ";;%s"%residualTitle)
        resPad.SetGridx()
        resPad.SetGridy()
        pdf.plotOn(frame, slice, projWData)

        zeroLine = ROOT.TLine(theConfig.plotMinInv, 0.0, theConfig.plotMaxInv, 0.0)
        zeroLine.SetLineColor(ROOT.kBlue)
        zeroLine.SetLineWidth(2)
        zeroLine.Draw()
        residuals = None
        if residualMode == "pull":
                residuals = frame.pullHist()
        else:
                residuals = frame.residHist()
        residuals.Draw("P")
        hAxis.GetYaxis().SetNdivisions(4, 2, 5)
        hAxis.SetTitleOffset(0.36, "Y")
        hAxis.SetTitleSize(0.18, "Y")
        hAxis.GetXaxis().SetLabelSize(0.1) 
        hAxis.GetYaxis().SetLabelSize(0.12)
        resPad.Update()
        pad.cd()
        rootContainer.append([zeroLine])
        return [pad, resPad]


def main():

        parser = argparse.ArgumentParser(description='edge fitter reloaded.')
        
        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
                                                  help="Verbose mode.")
        parser.add_argument("-m", "--mc", action="store_true", dest="mc", default=False,
                                                  help="use MC, default is to use data.")
        parser.add_argument("-u", "--use", action="store_true", dest="useExisting", default=False,
                                                  help="use existing datasets from pickle, default is false.")
        parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="SignalHighMT2DeltaPhiJetMetFit",
                                                  help="selection which to apply.")
        parser.add_argument("-r", "--runRange", dest="runRanges", action="append", default=[],
                                                  help="name of run range.")
        parser.add_argument("-b", "--backgroundShape", dest="backgroundShape", action="store", default="CB",
                                                  help="background shape, default CB")
        parser.add_argument("-e", "--edgeShape", dest="edgeShape", action="store", default="Triangle",
                                                  help="edge shape, default Triangle")
        parser.add_argument("-t", "--toys", dest="toys", action="store", default=0,
                                                  help="generate and fit x toys")
        parser.add_argument("-a", "--addSignal", action="store", dest="addSignal", default="",
                                                  help="add signal MC.")                
        parser.add_argument("-x", "--private", action="store_true", dest="private", default=False,
                                                  help="plot is private work.")         
        parser.add_argument("-p", "--paper", action="store_true", dest="paper", default=False,
                                                  help="plot for paper without preliminary label.")             
        parser.add_argument("-l", "--likelihoodScan", action="store_true", dest="likelihoodScan", default=False,
                                                  help="produce likelihood scan vs edge position.")             
        parser.add_argument("-w", "--write", action="store_true", dest="write", default=False,
                                                  help="write results to central repository")   
                                        
        args = parser.parse_args()      
        
        region = args.selection
        backgroundShape = args.backgroundShape
        signalShape = args.edgeShape
        runRangeName = "_".join(args.runRanges)
        lumis = []
        from defs import getRunRange
        for runRange in args.runRanges:
                lumis.append(getRunRange(runRange).printval)
        lumi = "+".join(lumis)
        
        produceScan = args.likelihoodScan
        useExistingDataset = args.useExisting
                
        from edgeConfig import edgeConfig
        theConfig = edgeConfig(region,backgroundShape,signalShape,args.runRanges,args.mc,args.toys,args.addSignal)
        if args.paper:
                theConfig.isPreliminary = False
        if args.private:
                theConfig.ownWork = True
        
        theConfig.selection.cut = theConfig.selection.cut.replace("metFilterSummary > 0 &&", "")
        theConfig.selection.cut = theConfig.selection.cut.replace("&& metFilterSummary > 0", "")
        
        # init ROOT
        #gROOT.Reset()
        gROOT.SetStyle("Plain")
        setTDRStyle()
        ROOT.gROOT.SetStyle("tdrStyle") 
        
        #set random random seed for RooFit, for toy generation
        ROOT.RooRandom.randomGenerator().SetSeed(0)
        
        ROOT.gSystem.Load("shapes/RooSUSYTPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYX4Pdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYXM4Pdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgMoreParamsPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgBHPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgBH2Pdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYOldBkgPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgMAPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgGaussiansPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooSUSYBkgGaussiansPlusExpPdf_cxx.so")
        ROOT.gSystem.Load("shapes/RooTopPairProductionSpline_cxx.so")
        ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
        ROOT.gSystem.Load("libFFTW.so") 
        
        
        
        # get data
        theDataInterface = dataInterface.DataInterface(theConfig.runRanges)
        treeEM = None
        treeEE = None
        treeMM = None

        if not useExistingDataset:
                if (theConfig.useMC):
                        
                        log.logHighlighted("Using MC instead of data.")
                        datasets = theConfig.mcdatasets # ["TTJets", "ZJets", "DibosonMadgraph", "SingleTop"]
                        (treeEM, treeEE, treeMM) = tools.getTrees(theConfig, datasets, useNLL=True)
                        
                else:
                        treeMMraw = theDataInterface.getTreeFromDataset("MergedData", "MuMu", cut=theConfig.selection.cut, useNLL=True)
                        treeEMraw = theDataInterface.getTreeFromDataset("MergedData", "EMu", cut=theConfig.selection.cut, useNLL=True)
                        treeEEraw = theDataInterface.getTreeFromDataset("MergedData", "EE", cut=theConfig.selection.cut, useNLL=True)
                        

                        # convert trees
                        treeEM = dataInterface.DataInterface.convertDileptonTree(treeEMraw)
                        treeEE = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
                        treeMM = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
                                

                weight = ROOT.RooRealVar("weight","weight",1.,-100.,10.)
                inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
                
                trees ={}
                trees["EE"] = treeEE
                trees["EM"] = treeEM
                trees["MM"] = treeMM
                
                typeName = "data"
                dataSets = prepareDatasets(inv,weight,trees,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.inclusive.val,theConfig.rSFOF.inclusive.err,theConfig, runRangeName)
                
        else:
                dataSets = ["dummy"]
        log.logDebug("Starting edge fit")
                        
        
        

        
        



        # silences all the info messages
        # 1 does not silence info messages, so 2 probably just suppresses these, but keeps the warnings
        #ROOT.RooMsgService.instance().Print()
        ROOT.RooMsgService.instance().setGlobalKillBelow(10)
        
        
        if theConfig.toyConfig["nToys"] > 0:
                theConfig.title = "%s_Scale%sMo%sSignalN%s"%(theConfig.title, theConfig.toyConfig["scale"], theConfig.toyConfig["m0"], theConfig.toyConfig["nSig"])

        if theConfig.fixEdge:
                theConfig.title = theConfig.title+"_FixedEdge_%.1f"%theConfig.edgePosition
        if theConfig.useMC:
                theConfig.title = theConfig.title+"_MC"
        if theConfig.isSignal:
                theConfig.title = theConfig.title+"_SignalInjected_"+theConfig.signalDataSets[0]        
                                        
        titleSave = theConfig.title
                        
        for index, dataSet in enumerate(dataSets):
                
                if theConfig.toyConfig["nToys"] > 0:
                        x = "%x"%(random.random()*1e9)
                        theConfig.figPath = "figToys/"
                        theConfig.title = titleSave 
                        if theConfig.toyConfig["systShift"] == "Up" or theConfig.toyConfig["systShift"] == "Down":
                                theConfig.title = theConfig.title + "_" + theConfig.toyConfig["systShift"]
                        if theConfig.signalShape != "T":
                                theConfig.title = theConfig.title + "_" + signalShape
                        if theConfig.toyConfig["sShape"] != "Triangular":
                                theConfig.title = theConfig.title + "_" + theConfig.toyConfig["sShape"]
                        if theConfig.allowNegSignal:
                                theConfig.title = theConfig.title + "_" + "allowNegSignal"      
                        if theConfig.toyConfig["rand"]:
                                theConfig.title = theConfig.title + "_" + "randM0"                              
                        theConfig.title = theConfig.title + "_" + x
                        
                                
                else:
                        x = None
                
                if not useExistingDataset:
                
                        w = ROOT.RooWorkspace("w", ROOT.kTRUE)
                        w.factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
                        w.factory("weight[1.,0.,10.]")
                        vars = ROOT.RooArgSet(inv, w.var('weight'))
                        
                        
                        dataEE = dataSets[index]["EE"].Clone("dataEE")
                        dataMM = dataSets[index]["MM"].Clone("dataMM")
                        dataEM = dataSets[index]["EM"].Clone("dataEM")
                        dataSFOS = dataSets[index]["SFOS"].Clone("dataSFOS")                            


                        getattr(w, 'import')(dataEE, ROOT.RooCmdArg())
                        getattr(w, 'import')(dataMM, ROOT.RooCmdArg())
                        getattr(w, 'import')(dataEM, ROOT.RooCmdArg())
                        getattr(w, 'import')(dataSFOS, ROOT.RooCmdArg())                
                        
                        if x == None:
                                if theConfig.useMC:
                                        w.writeToFile("workspaces/saveDataSet_%s_MC.root"%theConfig.selection.name)             
                                else:
                                        w.writeToFile("workspaces/saveDataSet_%s_Data.root"%theConfig.selection.name)           
                # shape configuration
                
                else:
                        if theConfig.useMC:
                                f = ROOT.TFile("workspaces/saveDataSet_%s_MC.root"%theConfig.selection.name)
                        else:
                                f = ROOT.TFile("workspaces/saveDataSet_%s_Data.root"%theConfig.selection.name)
                        w = f.Get("w")
                        w.Print()                       
                        

                title = "bla"
                        
                vars = ROOT.RooArgSet(w.var('inv'), w.var('weight'))
                selectShapes(w,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv, runRangeName)


                print w.data("dataSFOS").sumEntries(), w.data("dataEM").sumEntries()

        
                # deduce proper values for yield parameters from datasets and create yield parameters
                
                predictedSignalYield = w.data("dataSFOS").sumEntries() - 0.8*w.data("dataSFOS").sumEntries()
                if theConfig.allowNegSignal:
                        w.factory("nSig[%f,%f,%f]" % (0.,-2*predictedSignalYield, 2*predictedSignalYield))
                else:
                        w.factory("nSig[%f,%f,%f]" % (0.,0, 2*predictedSignalYield))
                w.var('nSig').setAttribute("StoreAsymError")


                maxZ = w.data("dataSFOS").sumEntries("abs(inv-91.2) < 20")
                
                #~ w.factory("nZ[%f,0.,%f]" % (theConfig.zPredictions.SF..val,maxZ))
                w.factory("nZ[%f,0.,%f]" % (0.01,maxZ))
                w.var('nZ').setAttribute("StoreAsymError")
                w.var('nZ').setConstant()
                
                
                nBMin = w.data("dataEM").sumEntries()*0
                nBMax= w.data("dataSFOS").sumEntries()*2
                nBStart = w.data("dataEM").sumEntries()*0.7   
                
                w.factory("nB[%f,%f,%f]" % (nBStart,nBMin,nBMax))       
                w.var('nB').setAttribute("StoreAsymError")

                #create background only shapes
                
                #~ w.factory("Gaussian::gx(inv,mean[90,0,100],sigma[3,0,10])")
                #~ conv = ROOT.RooFFTConvPdf("bgModel","bla",w.var("inv"),w.pdf("gx"),w.pdf("ofosShape1"))
                #~ getattr(w, 'import')(conv, ROOT.RooCmdArg())
                #~ w.pdf("bgModel").setBufferFraction(5.0)

                
                        
                w.factory("SUM::ofosShape(nB*ofosShape1)")
                
                # fit background only shapes to EM dataset
                w.Print()
                fitEM = w.pdf('ofosShape').fitTo(w.data("dataEM"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
                
                fitEM.Print()
                
                log.logWarning(" EM Fit Convergence Quality: %d"%fitEM.covQual())
                
                
                parametersToSave["minNllEM"] = fitEM.minNll()

                parametersToSave["nParEM"] = fitEM.floatParsFinal().getSize()

                frameEM = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of EM lepton pairs'))
                frameEM.GetXaxis().SetTitle('m_{e#mu} [GeV]')
                frameEM.GetYaxis().SetTitle(theConfig.histoytitle)

                

                sizeCanvas = 800
                c1 = ROOT.TCanvas("c1","c1",sizeCanvas,int(1.25 * sizeCanvas))


                ROOT.RooAbsData.plotOn(w.data("dataEM"), frameEM)
                w.pdf('ofosShape').plotOn(frameEM)    


                w.pdf('ofosShape').plotOn(frameEM,
                                                                  #~ ROOT.RooFit.VisualizeError(fitEM, 1),
                                                                  #~ ROOT.RooFit.FillColor(ROOT.kGreen + 2),
                                                                  #~ ROOT.RooFit.FillStyle(3009),
                                                                  ROOT.RooFit.LineWidth(2))
                w.pdf('ofosShape').plotOn(frameEM)
                ROOT.RooAbsData.plotOn(w.data("dataEM"), frameEM)
                
                parametersToSave["chi2EM"] = frameEM.chiSquare(parametersToSave["nParEM"])
                log.logDebug("Chi2 EM: %f" % parametersToSave["chi2EM"])

                
                useMC = theConfig.useMC
                luminosity = lumi
                isPreliminary = theConfig.isPreliminary
                year = theConfig.year
                showText = theConfig.showText
                title = theConfig.title
                histoytitle = theConfig.histoytitle
                print year
                
                dLeg = ROOT.TH1F()
                dLeg.SetMarkerStyle(ROOT.kFullCircle)
                dLeg.SetMarkerColor(ROOT.kBlack)
                dLeg.SetLineWidth(2)
                fitLeg = dLeg.Clone()
                fitLeg.SetLineColor(ROOT.kBlue)
                bLeg = dLeg.Clone()
                bLeg.SetLineStyle(2)
                bLeg.SetLineColor(ROOT.kBlack)
        
                        
                        
                nLegendEntries = 2
                if theConfig.plotErrorBands:
                        nLegendEntries =3
                bl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
                bl.SetTextAlign(22)
                
                if (useMC):
                        bl.AddEntry(dLeg, 'Simulation', "pl")
                else:
                        bl.AddEntry(dLeg, 'Data', "pl")
                bl.AddEntry(fitLeg, 'FS background', "l")
                if theConfig.plotErrorBands:
                        bl.AddEntry(uLeg, 'Uncertainty', "f")
                
                                                                #~ residualMode =residualMode)
                annotationsTitle = [
                                                (0.92, 0.57, "#splitline{%s}{DF only fit}" % (theConfig.selection.latex)),
                                                ]
                
                

                frameEM.GetXaxis().SetRangeUser(theConfig.plotMinInv, theConfig.plotMaxInv)
                frameEM.SetMaximum(theConfig.plotYMax)
                pad = ROOT.TPad("main%s" % (title), "main%s" % (title), 0.01, 0.25, 0.99, 0.99)
                ROOT.SetOwnership(pad, False)
                pad.SetNumber(1)
                pad.Draw()
                resPad = ROOT.TPad("residual%s" % (title), "residual%s" % (title), 0.01, 0.01, 0.99, 0.25)
                ROOT.SetOwnership(resPad, False)
                resPad.SetNumber(2)
                resPad.Draw()
                pad.cd()
                ##~ pad.DrawFrame(Holder.plotMinInv,1,Holder.plotMaxInv,yMax,";m_{ll} [GeV];Events / 5 GeV")    
                frameEM.Draw()
                tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
                if (showText):
                        #~ tools.makeAnnotations(annotationsTitle, color=tools.myColors['Grey'], textSize=0.03, align=31)
                        tools.makeAnnotations(annotationsTitle, color=ROOT.kBlack, textSize=0.03, align=31)
                bl.Draw()
                resPad.cd()
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
                residuals = frameEM.pullHist()

                residuals.Draw("P")
                hAxis.GetYaxis().SetNdivisions(4, 2, 5)
                hAxis.SetTitleOffset(0.36, "Y")
                hAxis.SetTitleSize(0.18, "Y")
                hAxis.GetXaxis().SetLabelSize(0.1) 
                hAxis.GetYaxis().SetLabelSize(0.12)
                resPad.Update()
                pad.cd()

                if theConfig.useMC:
                        c1.Print("fig/OF_%s_MC.pdf"%theConfig.title)
                else:
                        c1.Print("fig/OF_%s.pdf"%theConfig.title)
                
        

main()
