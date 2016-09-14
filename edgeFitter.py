#!/usr/bin/env python

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)
print sys.path
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import gROOT, gStyle, TFile, TH2F, TH2D
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import dataInterface
import tools
import math
import argparse	
import random

parametersToSave  = {}
rootContainer = []



### Routine to prepare the dataset. If only data/background MC is present
### the trees are simply returned as a RooDataSet. Signal MC can be added here
### If toys are produced datasets are returned for each set of toys

def prepareDatasets(inv,weight,trees,addTrees,maxInv,minInv,typeName,nBinsMinv,rSFOF,rSFOFErr,addDataset,theConfig,region="Central"):


	vars = ROOT.RooArgSet(inv, weight)
	

	# data or MC background
	
	tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(trees["EE"]), ROOT.RooFit.WeightVar("weight"))
	tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpOFOS = ROOT.RooDataSet("tmpOFOS", "tmpOFOS", vars, ROOT.RooFit.Import(trees["OFOS"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS = ROOT.RooDataSet("tmpSFOS", "tmpSFOS", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS.append(tmpEE)

	# add MC signal
	tmpAddEE = None
	tmpAddMM = None
	tmpAddOFOS = None
	if (addDataset != None and len(addTrees) > 0):
		tmpAddEE = ROOT.RooDataSet("tmpAddEE", "tmpAddEE", vars, ROOT.RooFit.Import(addTrees["EE"]), ROOT.RooFit.WeightVar("weight"))
		tmpAddMM = ROOT.RooDataSet("tmpAddMM", "tmpAddMM", vars, ROOT.RooFit.Import(addTrees["MM"]), ROOT.RooFit.WeightVar("weight"))
		tmpAddOFOS = ROOT.RooDataSet("tmpAddOFOS", "tmpAddOFOS", vars, ROOT.RooFit.Import(addTrees["OFOS"]), ROOT.RooFit.WeightVar("weight"))
		print "Checking the add"
		print trees["OFOS"].GetEntries()
		print tmpOFOS.sumEntries()
		print addTrees["OFOS"].GetEntries()
		print tmpAddOFOS.sumEntries()
		tmpEE.append(tmpAddEE)
		tmpMM.append(tmpAddMM)
		tmpSFOS.append(tmpAddEE)
		tmpSFOS.append(tmpAddMM)
		tmpOFOS.append(tmpAddOFOS)
		print tmpOFOS.sumEntries()

	
	dataEE = ROOT.RooDataSet("%sEE" % (typeName), "Dataset with invariant mass of di-electron pairs",
							 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
	dataMM = ROOT.RooDataSet("%sMM" % (typeName), "Dataset with invariant mass of di-muon pairs",
							 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
	dataSFOS = ROOT.RooDataSet("%sSFOS" % (typeName), "Dataset with invariant mass of SFOS lepton pairs",
							   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
	dataOFOS = ROOT.RooDataSet("%sOFOS" % (typeName), "Dataset with invariant mass of OFOS lepton pairs",
							   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))

	### Toys
	
	if theConfig.toyConfig["nToys"] > 0:
		log.logHighlighted("Preparing to dice %d Toys"%theConfig.toyConfig["nToys"])
		rand = ROOT.TRandom3()
		rand.SetSeed(0)
		
		wToys = {}
		
		### Add a temporary workspace for the toys
		wToys[region] = ROOT.RooWorkspace("wToys%s"%region, ROOT.kTRUE)
		wToys[region].factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
		wToys[region].factory("weight[1.,0.,10.]")
		vars = ROOT.RooArgSet(inv, wToys[region].var('weight'))
		
		### fetch the shapes
		selectShapes(wToys[region],theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)
		
		### get the trees from data/MC + optional signal MC into toy workspace
		dataEE = ROOT.RooDataSet("%sEE%s" % (typeName,region), "Dataset with invariant mass of di-electron pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
		dataMM = ROOT.RooDataSet("%sMM%s" % (typeName,region), "Dataset with invariant mass of di-muon pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
		dataSFOS = ROOT.RooDataSet("%sSFOS%s" % (typeName,region), "Dataset with invariant mass of SFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
		dataOFOS = ROOT.RooDataSet("%sOFOS%s" % (typeName,region), "Dataset with invariant mass of OFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))		
		
		getattr(wToys[region], 'import')(dataEE, ROOT.RooCmdArg())
		getattr(wToys[region], 'import')(dataMM, ROOT.RooCmdArg())
		getattr(wToys[region], 'import')(dataSFOS, ROOT.RooCmdArg())
		getattr(wToys[region], 'import')(dataOFOS, ROOT.RooCmdArg())	
		

					
		wToys[region].factory("SUM::ofosShape%s(nB[100,0,100000]*ofosShape1%s)"%(region,region))
		fitOFOS = wToys[region].pdf('ofosShape%s'%region).fitTo(wToys[region].data('%sOFOS%s'%(typeName,region)), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
		numOFOS = tmpOFOS.sumEntries()
		
		
		scale = theConfig.toyConfig["scale"]
		
		tmpNumOFOS = float(numOFOS*scale)
		tmpNumOFOS2 = float(numOFOS*scale)
		print "Signal OFOS %d"%tmpNumOFOS2
		print "Signal SFOS %d"%tmpNumOFOS
			
			
		### get the Z prediction from the central config
		zPrediction = getattr(theConfig.zPredictions.default.SF,region.lower()).val
		print zPrediction, theConfig.toyConfig["nSig"], tmpNumOFOS
		
		### get the different fractions
		fsFrac = tmpNumOFOS/(tmpNumOFOS+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
		zFrac = zPrediction*scale/(tmpNumOFOS+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
		sigFrac = theConfig.toyConfig["nSig"]*scale/(tmpNumOFOS+zPrediction+theConfig.toyConfig["nSig"]*scale)
		
		print fsFrac, zFrac, sigFrac
		
		wToys[region].factory("fsFrac[%s,%s,%s]"%(fsFrac,fsFrac,fsFrac))
		wToys[region].var('fsFrac').setConstant(ROOT.kTRUE)		
		wToys[region].factory("zFrac[%s,%s,%s]"%(zFrac,zFrac,zFrac))
		wToys[region].var('zFrac').setConstant(ROOT.kTRUE)	
		wToys[region].factory("sigFrac[%s,%s,%s]"%(sigFrac,sigFrac,sigFrac))
		wToys[region].var('sigFrac').setConstant(ROOT.kTRUE)
			
		if theConfig.toyConfig["nSig"] > 0:
			### generate toy signal events, if chosen in config
			log.logHighlighted("Dicing %d Signal Events at %.1f GeV edge position"%(theConfig.toyConfig["nSig"],theConfig.toyConfig["m0"]))
			
			wToys[region].var('m0').setVal(theConfig.toyConfig["m0"])
			if theConfig.toyConfig["sShape"] == "Concave":
				log.logHighlighted("Dicing concave signal shape")
				wToys[region].factory("SUSYX4Pdf::eeShape%sForToys(inv,constant,sEE%s,m0)"%(region,region))
				wToys[region].factory("SUSYX4Pdf::mmShape%sForToys(inv,constant,sMM%s,m0)"%(region,region))	
				wToys[region].factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s, sigFrac*eeShape%sForToys)"%(region,region,region))
				wToys[region].factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s, sigFrac*mmShape%sForToys)"%(region,region,region))
								
			elif theConfig.toyConfig["sShape"] == "Convex":
				log.logHighlighted("Dicing convex signal shape")
				wToys[region].factory("SUSYXM4Pdf::eeShape%sForToys(inv,constant,sEE%s,m0)"%(region,region))
				wToys[region].factory("SUSYXM4Pdf::mmShape%sForToys(inv,constant,sMM%s,m0)"%(region,region))		
				wToys[region].factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s, sigFrac*eeShape%sForToys)"%(region,region,region))
				wToys[region].factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s, sigFrac*mmShape%sForToys)"%(region,region,region))
							
			else:
				log.logHighlighted("Dicing triangular signal shape")	
				wToys[region].factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s, sigFrac*eeShape%s)"%(region,region,region))
				wToys[region].factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s, sigFrac*mmShape%s)"%(region,region,region))
		else:
			wToys[region].factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s)"%(region,region))
			wToys[region].factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s)"%(region,region))						
			

		### Shift R_SF/OF (R_ee/OF, R_mm/OF) up/down if systematic studies are to be performed
		if theConfig.toyConfig["systShift"] == "Up":
			tmpREEOF = getattr(theConfig.rEEOF,region.lower()).val + getattr(theConfig.rEEOF,region.lower()).err
			tmpRMMOF = getattr(theConfig.rMMOF,region.lower()).val + getattr(theConfig.rMMOF,region.lower()).err
			tmpRSFOF = getattr(theConfig.rSFOF,region.lower()).val + getattr(theConfig.rSFOF,region.lower()).err
		elif theConfig.toyConfig["systShift"] == "Down":
			tmpREEOF = getattr(theConfig.rEEOF,region.lower()).val - getattr(theConfig.rEEOF,region.lower()).err
			tmpRMMOF = getattr(theConfig.rMMOF,region.lower()).val - getattr(theConfig.rMMOF,region.lower()).err
			tmpRSFOF = getattr(theConfig.rSFOF,region.lower()).val - getattr(theConfig.rSFOF,region.lower()).err
		else:
			tmpREEOF = getattr(theConfig.rEEOF,region.lower()).val
			tmpRMMOF = getattr(theConfig.rMMOF,region.lower()).val
			tmpRSFOF = getattr(theConfig.rSFOF,region.lower()).val
			
				
		eeFraction = tmpREEOF/tmpRSFOF		
		mmFraction = tmpRMMOF/tmpRSFOF		
		
		### Get the number of generated EE and MuMu Events, assume 25% of the signal to be in forward and 75% central		
		genNumEE =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*eeFraction)
		genNumMM =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*mmFraction)
		if region == "Forward":		
			genNumEE =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale*0.33 + zPrediction*scale)*eeFraction)
			genNumMM =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale*0.33 + zPrediction*scale)*mmFraction)
		
		### generate the toys and get the corresponding datasets as a result
		result = genToys(wToys[region],theConfig.toyConfig["nToys"],genNumEE,genNumMM,int(tmpNumOFOS),region)
		wToys[region].Delete()
		
	else:
		result = [{"EE":dataEE,"MM":dataMM,"SFOS":dataSFOS,"OFOS":dataOFOS}]		
		
	return result	

### Actual dicing of toys, after a workspace is defined and the number of 
### events to be generated is determined
def genToys(ws, nToys=10,genEE=0,genMM=0,genOFOS=0,region="Central"):
	theToys = []

	mcEE = ROOT.RooMCStudy(ws.pdf('backtoymodelEE'), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcEE.generate(nToys, genEE, ROOT.kTRUE)
	mcMM = ROOT.RooMCStudy(ws.pdf("backtoymodelMM"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcMM.generate(nToys, genMM, ROOT.kTRUE)
	mcOFOS = ROOT.RooMCStudy(ws.pdf("ofosShape%s"%region), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcOFOS.generate(nToys, genOFOS, ROOT.kTRUE)
	
	vars = ROOT.RooArgSet(ws.var('inv'), ws.var('weight'))

	
	for i in range(nToys):
		toyEE = mcEE.genData(i)
		toyMM = mcMM.genData(i)
		toyOFOS = mcOFOS.genData(i)
		toySFOS = toyEE.Clone()
		toySFOS.append(toyMM.Clone())
		toyDataEE = ROOT.RooDataSet("theToyEE_%s" % (i), "toyEE_%s" % (i), vars,ROOT.RooFit.Import(toyEE))
		toyDataMM = ROOT.RooDataSet("theToyMM_%s" % (i), "toyMM_%s" % (i), vars,ROOT.RooFit.Import(toyMM))
		toyDataOFOS = ROOT.RooDataSet("theToyOFOS_%s" % (i), "toyOFOS_%s" % (i), vars,ROOT.RooFit.Import(toyOFOS))
		toyDataSFOS = ROOT.RooDataSet("theToySFOS_%s" % (i), "toySFOS_%s" % (i), vars,ROOT.RooFit.Import(toySFOS))
		theToys.append({"EE":toyDataEE,"MM":toyDataMM,"OFOS":toyDataOFOS,"SFOS":toyDataSFOS})

	return theToys


### routine to get the Z, the flavor-symmetric background and the signal shape
def selectShapes(ws,backgroundShape,signalShape,nBinsMinv):

	### Z-shape

	### Resolutions of dimuon and dielectron events
	### can be constant or within a range
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


	### fetch the parameters for the Z contribution
	
	### central 
	
	### continuum
	cContinuumEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "expo",basePath="dyShelves/")
	cContinuumMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "expo",basePath="dyShelves/")
	### Double sided crystal-ball
	cbMeanEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "cbMean",basePath="dyShelves/")
	cbMeanMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "cbMean",basePath="dyShelves/")
	nZEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nZ",basePath="dyShelves/")
	nZMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nZ",basePath="dyShelves/")
	nLEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nL",basePath="dyShelves/")
	nLMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nL",basePath="dyShelves/")
	nREECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nR",basePath="dyShelves/")
	nRMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nR",basePath="dyShelves/")
	alphaLEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "alphaL",basePath="dyShelves/")
	alphaLMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "alphaL",basePath="dyShelves/")
	alphaREECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "alphaR",basePath="dyShelves/")
	alphaRMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "alphaR",basePath="dyShelves/")
	sEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "s",basePath="dyShelves/")
	sMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "s",basePath="dyShelves/")
	### relative fraction of events in peak (peak/(peak+continuum))
	zFractionEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "zFraction",basePath="dyShelves/")
	zFractionMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "zFraction",basePath="dyShelves/")

	### forward
	
	### continuum
	cContinuumEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "expo",basePath="dyShelves/")
	cContinuumMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "expo",basePath="dyShelves/")
	### Double sided crystal-ball
	cbMeanEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "cbMean",basePath="dyShelves/")
	cbMeanMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "cbMean",basePath="dyShelves/")
	nZEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nZ",basePath="dyShelves/")
	nZMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nZ",basePath="dyShelves/")		
	nLEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nL",basePath="dyShelves/")
	nLMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nL",basePath="dyShelves/")
	nREEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nR",basePath="dyShelves/")
	nRMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nR",basePath="dyShelves/")
	alphaLEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "alphaL",basePath="dyShelves/")
	alphaLMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "alphaL",basePath="dyShelves/")
	alphaREEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "alphaR",basePath="dyShelves/")
	alphaRMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "alphaR",basePath="dyShelves/")
	sEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "s",basePath="dyShelves/")
	sMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "s",basePath="dyShelves/")
	### relative fraction of events in peak (peak/(peak+continuum))
	zFractionEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "zFraction",basePath="dyShelves/")
	zFractionMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "zFraction",basePath="dyShelves/")
	
	### Import the parameters to the workspace
	
	### continuum		
	cContinuum = -0.017
	ws.factory("cContinuumCentral[%f]" % (cContinuum))
	ws.factory("cContinuumEECentral[%f]" % (cContinuumEECentral))
	ws.factory("cContinuumMMCentral[%f]" % (cContinuumMMCentral))
	ws.factory("cContinuumForward[%f]" % (cContinuum))
	ws.factory("cContinuumEEForward[%f]" % (cContinuumEEForward))
	ws.factory("cContinuumMMForward[%f]" % (cContinuumMMForward))


	ws.factory("Exponential::offShellEECentral(inv,cContinuumEECentral)")				
	ws.factory("Exponential::offShellMMCentral(inv,cContinuumMMCentral)")				
	ws.factory("Exponential::offShellCentral(inv,cContinuumCentral)")	

	ws.factory("Exponential::offShellEEForward(inv,cContinuumEEForward)")				
	ws.factory("Exponential::offShellMMForward(inv,cContinuumMMForward)")				
	ws.factory("Exponential::offShellForward(inv,cContinuumForward)")	
				
	### Double-sided crystal-ball							
	ws.factory("zFractionMMCentral[%f]"%zFractionMMCentral)
	ws.factory("cbmeanMMCentral[%f]"%cbMeanMMCentral)				
	ws.factory("sMMCentral[%f]"%sMMCentral)													
	ws.factory("nMMLCentral[%f]"%nLMMCentral)
	ws.factory("alphaMMLCentral[%f]"%alphaLMMCentral)
	ws.factory("nMMRCentral[%f]"%nRMMCentral)
	ws.factory("alphaMMRCentral[%f]"%alphaRMMCentral)		
	
	ws.factory("DoubleCB::cbShapeMMCentral(inv,cbmeanMMCentral,sMMCentral,alphaMMLCentral,nMMLCentral,alphaMMRCentral,nMMRCentral)")	
					
	ws.factory("zFractionMMForward[%f]"%zFractionMMForward)
	ws.factory("cbmeanMMForward[%f]"%cbMeanMMForward)				
	ws.factory("sMMForward[%f]"%sMMForward)													
	ws.factory("nMMLForward[%f]"%nLMMForward)
	ws.factory("alphaMMLForward[%f]"%alphaLMMForward)
	ws.factory("nMMRForward[%f]"%nRMMForward)
	ws.factory("alphaMMRForward[%f]"%alphaRMMForward)		
	
	ws.factory("DoubleCB::cbShapeMMForward(inv,cbmeanMMForward,sMMForward,alphaMMLForward,nMMLForward,alphaMMRForward,nMMRForward)")	


	ws.factory("cbmeanEECentral[%f]"%cbMeanEECentral)
	ws.factory("zFractionEECentral[%f]"%zFractionEECentral)
	ws.factory("sEECentral[%f]"%sEECentral)				
	ws.factory("nEELCentral[%f]"%nLEECentral)
	ws.factory("alphaEELCentral[%f]"%alphaLEECentral)
	ws.factory("nEERCentral[%f]"%nREECentral)
	ws.factory("alphaEERCentral[%f]"%alphaREECentral)
	
	ws.factory("DoubleCB::cbShapeEECentral(inv,cbmeanEECentral,sEECentral,alphaEELCentral,nEELCentral,alphaEERCentral,nEERCentral)")	

	ws.factory("cbmeanEEForward[%f]"%cbMeanEEForward)
	ws.factory("zFractionEEForward[%f]"%zFractionEEForward)
	ws.factory("sEEForward[%f]"%sEEForward)				
	ws.factory("nEELForward[%f]"%nLEEForward)
	ws.factory("alphaEELForward[%f]"%alphaLEEForward)
	ws.factory("nEERForward[%f]"%nREEForward)
	ws.factory("alphaEERForward[%f]"%alphaREEForward)
	
	ws.factory("DoubleCB::cbShapeEEForward(inv,cbmeanEEForward,sEEForward,alphaEELForward,nEELForward,alphaEERForward,nEERForward)")	

	### Breit-Wigner with SM Z mean and width
	ws.factory("BreitWigner::bwShape(inv,zmean,zwidth)")
	
	### convolve the crystal-ball and the BreitWigner
	convEECentral = ROOT.RooFFTConvPdf("peakModelEECentral","zShapeEE Central (x) cbShapeEE Central",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeEECentral"))
	getattr(ws, 'import')(convEECentral, ROOT.RooCmdArg())
	ws.pdf("peakModelEECentral").setBufferFraction(5.0)
	
	convEEForward = ROOT.RooFFTConvPdf("peakModelEEForward","zShapeEE Forward (x) cbShapeEE Forward",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeEEForward"))
	getattr(ws, 'import')(convEEForward, ROOT.RooCmdArg())
	ws.pdf("peakModelEEForward").setBufferFraction(5.0)
	
	convMMCentral = ROOT.RooFFTConvPdf("peakModelMMCentral","zShapeMM Central (x) cbShapeMM Central",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeMMCentral"))
	getattr(ws, 'import')(convMMCentral, ROOT.RooCmdArg())
	ws.pdf("peakModelMMCentral").setBufferFraction(5.0)
	
	convMMForward = ROOT.RooFFTConvPdf("peakModelMMForward","zShapeMM Forward (x) cbShapeMM Forward",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeMMForward"))
	getattr(ws, 'import')(convMMForward, ROOT.RooCmdArg())
	ws.pdf("peakModelMMForward").setBufferFraction(5.0)
	

	### Exponential for the continuum
	ws.factory("expFractionMMCentral[%f]"%(1-zFractionMMCentral))		
	ws.factory("SUM::zMMShapeCentral(zFractionMMCentral*peakModelMMCentral,expFractionMMCentral*offShellMMCentral)")

	ws.factory("expFractionMMForward[%f]"%(1-zFractionMMForward))		
	ws.factory("SUM::zMMShapeForward(zFractionMMForward*peakModelMMForward,expFractionMMForward*offShellMMForward)")
	

	ws.factory("expFractionEECentral[%f]"%(1-zFractionEECentral))
	ws.factory("SUM::zEEShapeCentral(zFractionEECentral*peakModelEECentral,expFractionEECentral*offShellEECentral)")

	ws.factory("expFractionEEForward[%f]"%(1-zFractionEEForward))
	ws.factory("SUM::zEEShapeForward(zFractionEEForward*peakModelEEForward,expFractionEEForward*offShellEEForward)")


	
	### IMPORTANT! If the bin size for the cache is not set to the same used in the the drell-yan fit, things get really fucked up! 
	ws.var("inv").setBins(140,"cache")	
	

	### Parameters for the flavor-symmetric background shapes
	### A lot of shapes have been tried and can be choosen via option -b
	### Some work well some don't. The Crystal-Ball shape (CB) is the default one
	
	
	### Some more or less standard shapes
	if backgroundShape == 'L':
		log.logHighlighted("Using Landau")
		ws.factory("Landau::ofosShape1Central(inv,a1Central[30,0,100],b1Central[20,0,100])")
		ws.factory("Landau::ofosShape1Forward(inv,a1Forward[30,0,100],b1Forward[20,0,100])")
	elif backgroundShape == 'CH':
		log.logHighlighted("Using Chebychev")
		ws.factory("Chebychev::ofosShape1Central(inv,{a1Central[0,-2,2],b1Central[0,-2,2],c1Central[0,-1,1],d1Central[0,-1,1],e1Central[0,-1,1],f1Central[0,-1,1]})")
		ws.factory("Chebychev::ofosShape1Forward(inv,{a1Forward[0,-2,2],b1Forward[0,-2,2],c1Forward[0,-1,1],d1Forward[0,-1,1],e1Forward[0,-1,1],f1Forward[0,-1,1]})")
	elif backgroundShape == 'B':
		log.logHighlighted("Using BH shape")
		ws.factory("SUSYBkgBHPdf::ofosShape1Central(inv,a1Central[1.],a2Central[100,0,250],a3Central[1,0,100],a4Central[0.1,0,2])")
		ws.factory("SUSYBkgBHPdf::ofosShape1Forward(inv,a1Forward[1.],a2Forward[100,0,250],a3Forward[1,0,100],a4Forward[0.1,0,2])")
	
	### Some tries from 8 or even 7 TeV. Some had too many parameters, others did not fit so well	
	elif backgroundShape == 'G':
		log.logHighlighted("Using old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.6.,0.,8.],a2Central[0.1,-1.,1.],b1Central[0.028,0.001,1.],b2Central[1.],c1Central[0.],c2Central[1.])") #trying to get rid of paramteres
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.6.,0.,8.],a2Forward[0.1,-1.,1.],b1Forward[0.028,0.001,1.],b2Forward[1.],c1Forward[0.],c2Forward[1.])") #trying to get rid of paramteres
	elif backgroundShape == 'O':
		log.logHighlighted("Using old old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.0,0.,400.],a2Central[1.],b1Central[0.01,0.00001,100.],b2Central[1.])")
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.0,0.0,400.],a2Forward[1.],b1Forward[0.01,0.00001,100.],b2Forward[1.])")	
	elif backgroundShape == 'F':
		log.logHighlighted("Using new old shape")
		ws.factory("SUSYBkgMoreParamsPdf::ofosShape1Central(inv,a1Central[1.0,0.,400.],b1Central[1,0.00001,100.],c1Central[0.,-20.,30.])")
		ws.factory("SUSYBkgMoreParamsPdf::ofosShape1Forward(inv,a1Forward[1.0,0.0,400.],b1Forward[1,0.00001,100.],c1Forward[0.,-20.,30.])")	
	
	### the one finally used at 8 TeV. Describes the shape nicely but sometimes has a problem to converge and takes much time. Overall still too many parameters
	elif backgroundShape == '8TeV':
		log.logHighlighted("Using 8 TeV shape for real")
		ws.factory("TopPairProductionSpline::ofosShape1Central(inv,b1Central[-1800,-5000,5000],b2Central[120.,-400,400],b4Central[0.0025,0.0001,0.01], m1Central[50,20,80],m2Central[120,100,160])") 
		ws.factory("TopPairProductionSpline::ofosShape1Forward(inv,b1Forward[-1800,-5000,5000],b2Forward[120.,-400,400],b4Forward[0.0025,0.0001,0.01], m1Forward[50,20,80],m2Forward[120,100,160])")
		
	### Crystal-Ball shape used at 13 TeV. The description is as well as with the 8 TeV shape but requires less parameters. Thus it is faster and converges nearly all the time
	### The n-parameter was found to have basically no impact and tends to the upper limit. Thus it is most times fixed
	elif backgroundShape == 'CB':
			log.logHighlighted("Using Crystal-Ball shape")
			#~ ws.factory("CBShape::ofosShape1Central(inv,cbMeanCentral[50.,0.,200.],cbSigmaCentral[20.,0.,100.],alphaCentral[-1,-10.,0.],nCentral[1.,0.,100.])")
			#~ ws.factory("CBShape::ofosShape1Forward(inv,cbMeanForward[50.,0.,200.],cbSigmaForward[20.,0.,100.],alphaForward[-1,-10.,0.],nForward[1.,0.,100.])")
			ws.factory("CBShape::ofosShape1Central(inv,cbMeanCentral[50.,0.,200.],cbSigmaCentral[20.,0.,100.],alphaCentral[-1,-10.,0.],nCentral[100.])")
			ws.factory("CBShape::ofosShape1Forward(inv,cbMeanForward[50.,0.,200.],cbSigmaForward[20.,0.,100.],alphaForward[-1,-10.,0.],nForward[100.])")	
	elif backgroundShape == 'P':
		log.logHighlighted("Gaussians activated!")
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Central(inv,a1Central[30.,0.,70.],a2Central[60.,20.,105.],a3Central[100.,-1000.,1000.],b1Central[15,10.,80.],b2Central[20.,10.,80.],b3Central[200.,10.,3000.])") #High MET
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Forward(inv,a1Forward[30.,0.,70.],a2Forward[60.,20.,105.],a3Forward[100.,-1000.,1000.],b1Forward[15,10.,80.],b2Forward[20.,10.,80.],b3Forward[200.,10.,3000.])") #High MET

	elif backgroundShape == "K":
		log.logHighlighted("Kernel Density Estimation activated")
		nameDataOFOSCentral = "dataOFOSCentral" 
		nameDataOFOSForward = "dataOFOSForward" 
		ws.factory("RooKeysPdf::ofosShape1Central(inv, %s, MirrorBoth)" % (nameDataOFOSCentral))
		ws.factory("RooKeysPdf::ofosShape1Forward(inv, %s, MirrorBoth)" % (nameDataOFOSForward))
	elif backgroundShape == "Hist":
		log.logHighlighted("HistSubtraction activated!")
		ws.var('inv').setBins(nBinsMinv)
		tempDataHistCentral = ROOT.RooDataHist("dataHistOFOSCentral", "dataHistOFOSCentral", ROOT.RooArgSet(ws.var('inv')), ws.data("dataOFOSCentral"))
		getattr(ws, 'import')(tempDataHistCentral, ROOT.RooCmdArg())
		tempDataHistForward = ROOT.RooDataHist("dataHistOFOSForward", "dataHistOFOSForward", ROOT.RooArgSet(ws.var('inv')), ws.data("dataOFOSForward"))
		getattr(ws, 'import')(tempDataHistForward, ROOT.RooCmdArg())
		ws.factory("RooHistPdf::ofosShape1Central(inv, dataHistOFOSCentral)")
		ws.factory("RooHistPdf::ofosShape1Forward(inv, dataHistOFOSForward)")
	else:
		log.logHighlighted("No valid background shape selected, exiting")
		sys.exit()

	### set range and starting value to search for an edge
	ws.factory("m0[55., 30., 300.]")
	ws.var('m0').setAttribute("StoreAsymError")
	ws.factory("m0Show[45., 0., 300.]")
	ws.factory("constant[45,20,100]")

	### Signal shape. The triangle is the default one, while X4 and XM4 are more convex/concave
	if signalShape == "Triangle":
		ws.factory("SUSYTPdf::sfosShapeCentral(inv,constant,s,m0)")
		ws.factory("SUSYTPdf::sfosShapeCentralShow(inv,constant,s,m0Show)")
		ws.factory("SUSYTPdf::eeShapeCentral(inv,constant,sEECentral,m0)")
		ws.factory("SUSYTPdf::mmShapeCentral(inv,constant,sMMCentral,m0)")
		ws.factory("SUSYTPdf::sfosShapeForward(inv,constant,s,m0)")
		ws.factory("SUSYTPdf::sfosShapeShowForward(inv,constant,s,m0Show)")
		ws.factory("SUSYTPdf::eeShapeForward(inv,constant,sEEForward,m0)")
		ws.factory("SUSYTPdf::mmShapeForward(inv,constant,sMMForward,m0)")
		ws.var('constant').setConstant(ROOT.kTRUE)
	elif signalShape == 'Concave':
		ws.factory("SUSYX4Pdf::sfosShapeCentral(inv,constant,s,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeCentralShow(inv,constant,s,m0Show)")
		ws.factory("SUSYX4Pdf::eeShapeCentral(inv,constant,sEECentral,m0)")
		ws.factory("SUSYX4Pdf::mmShapeCentral(inv,constant,sMMCentral,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeForward(inv,constant,s,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeShowForward(inv,constant,s,m0Show)")
		ws.factory("SUSYX4Pdf::eeShapeForward(inv,constant,sEEForward,m0)")
		ws.factory("SUSYX4Pdf::mmShapeForward(inv,constant,sMMForward,m0)")
		ws.var('constant').setConstant(ROOT.kTRUE)
	elif signalShape == 'Convex':
		ws.factory("SUSYXM4Pdf::sfosShapeCentral(inv,constant,s,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeCentralShow(inv,constant,s,m0Show)")
		ws.factory("SUSYXM4Pdf::eeShapeCentral(inv,constant,sEECentral,m0)")
		ws.factory("SUSYXM4Pdf::mmShapeCentral(inv,constant,sMMCentral,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeForward(inv,constant,s,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeShowForward(inv,constant,s,m0Show)")
		ws.factory("SUSYXM4Pdf::eeShapeForward(inv,constant,sEEForward,m0)")
		ws.factory("SUSYXM4Pdf::mmShapeForward(inv,constant,sMMForward,m0)")
		ws.var('constant').setConstant(ROOT.kTRUE)
	else:
		log.logHighlighted("No valid background shape selected, exiting")
		sys.exit()	

### Routine to create a frame containing for certain fit results. Slices and cuts can be used to only 
### show the OF, ee or mumu results. H0 can be chosen if no signal is to be plotted
def plotModel(w, data, fitOFOS, theConfig, pdf="model", tag="", frame=None,
			  slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), cut=ROOT.RooCmdArg.none(),
			  overrideShapeNames={},region="Central",H0=False):
	if (frame == None):
		frame = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
	frame.GetXaxis().SetTitle('m_{ll} [GeV]')
	#frame.GetYaxis().SetTitle(histoytitle)
	ROOT.RooAbsData.plotOn(data, frame, cut)
	w.pdf(pdf).plotOn(frame, slice, projWData)

	shapeNames = {
				  'Z': "zShape%s"%region,
				  #~ 'offShell': "offShell",
				  'Background': "ofosShape%s"%region,
				  'Signal': "sfosShape%s"%region,
				  }
	shapeNames.update(overrideShapeNames)
	nameBGShape = "displayedBackgroundShape"
	nameBGZShape = "displayedBackgroundShapeZ"

	# get pdfs
	plotZ = ROOT.RooArgSet(w.pdf(shapeNames['Z']))
	plotOFOS = ROOT.RooArgSet(w.pdf(shapeNames['Background']))
	print shapeNames['Signal']
	plotSignal = ROOT.RooArgSet(w.pdf(shapeNames['Signal']))
	
	w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotOFOS), ROOT.RooFit.Name(nameBGShape),
					  slice, projWData,
					  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack))
	if theConfig.plotErrorBands:
		w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotOFOS),
						  slice, projWData,
						  ROOT.RooFit.VisualizeError(fitOFOS, 1),
						  ROOT.RooFit.FillColor(ROOT.kGreen + 2),
						  ROOT.RooFit.FillStyle(3009),
						  ROOT.RooFit.LineWidth(2))
	w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotZ),
						  slice, projWData,
						  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kViolet))

	# plot edge signal component
	if not H0:
		w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotSignal),
							  slice, projWData,
							  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
	
	return frame

### save the results in .pkl files
### For toys, the reults of toys run with the same configuration are stored in the same file
### each toy gets a random number x assigned which is used as an index to identify it
def saveFitResults(ws,theConfig,x = None,region="Central"):
	 
	if x == None:
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nS", ws.var('nSig%s'%region).getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nZ", ws.var('nZ%s'%region).getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nB", ws.var('nB%s'%region).getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "rSFOF", ws.var('rSFOF%s'%region).getVal(),basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0", ws.var('m0').getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sOFOS%s" %(theConfig.title,region), "chi2", parametersToSave["chi2OFOS%s"%region],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sOFOS%s" %(theConfig.title,region), "nPar", parametersToSave["nParOFOS%s"%region],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "chi2",parametersToSave["chi2SFOS%s"%region],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nPar", parametersToSave["nParH1"],basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "minNllH0", parametersToSave["minNllH0"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "minNllH1", parametersToSave["minNllH1"],basePath=theConfig.shelvePath)											
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "minNllOFOS", parametersToSave["minNllOFOS%s"%region],basePath=theConfig.shelvePath)											
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "initialM0", parametersToSave["initialM0"],basePath=theConfig.shelvePath)				

		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerror", ws.var('nSig%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerrorHi", ws.var("nSig%s"%region).getAsymErrorHi(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerrorLo", ws.var("nSig%s"%region).getAsymErrorLo(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nZerror", ws.var('nZ%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nBerror", ws.var('nB%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "rSFOFerror", ws.var('rSFOF%s'%region).getError(),basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0error", ws.var('m0').getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0errorHi", ws.var('m0').getAsymErrorHi(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0errorLo", ws.var('m0').getAsymErrorLo(),basePath=theConfig.shelvePath)
		
		
		ws.var("inv").setRange("fullRange",20,300)
		ws.var("inv").setRange("lowMass",20,70)
		argSet = ROOT.RooArgSet(ws.var("inv"))
		
		fittedZInt = ws.pdf("zShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak"))
		fittedZ = fittedZInt.getVal()*ws.var("nZ%s"%region).getVal()
		
		fittedLowMassZInt = ws.pdf("zShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassZ = fittedLowMassZInt.getVal()*ws.var("nZ%s"%region).getVal()
		
		fittedLowMassSInt = ws.pdf("sfosShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassS = fittedLowMassSInt.getVal()*ws.var("nSig%s"%region).getVal()
		
		fittedLowMassBInt = ws.pdf("ofosShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassB = fittedLowMassBInt.getVal()*ws.var("nB%s"%region).getVal()*ws.var("rSFOF%s"%region).getVal()

		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "onZZYield",fittedZ,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassZYield",fittedLowMassZ,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassSYield",fittedLowMassS,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassBYield",fittedLowMassB,basePath=theConfig.shelvePath)				

		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "onZZYielderror",fittedZInt.getVal()*ws.var("nZ%s"%region).getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassZYielderror",fittedLowMassZInt.getVal()*ws.var("nZ%s"%region).getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassSYielderror",fittedLowMassSInt.getVal()*ws.var("nSig%s"%region).getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "lowMassBYielderror",fittedLowMassBInt.getVal()*ws.var("nB%s"%region).getError(),basePath=theConfig.shelvePath)				
				
	else:
		title = theConfig.title.split("_%s"%x)[0]
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nS", ws.var('nSig%s'%region).getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nZ", ws.var('nZ%s'%region).getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nB", ws.var('nB%s'%region).getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "rSFOF", ws.var('rSFOF%s'%region).getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "m0", ws.var('m0').getVal(), index = x)
		tools.updateParameter("edgefit", "%sOFOS%s" %(title,region), "chi2",parametersToSave["chi2OFOS%s"%region], index = x)
		tools.updateParameter("edgefit", "%sOFOS%s" %(title,region), "nPar",parametersToSave["nParOFOS%s"%region], index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "chi2",parametersToSave["chi2SFOS%s"%region], index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nPar",parametersToSave["nParH1"], index = x)		
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "minNllH0", parametersToSave["minNllH0"], index = x)				
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "minNllH1", parametersToSave["minNllH1"], index = x)				
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "minNllOFOS", parametersToSave["minNllOFOS%s"%region], index = x)				
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "initialM0", parametersToSave["initialM0"], index = x)	
				
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nSerror", ws.var('nSig%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nZerror", ws.var('nZ%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nBerror", ws.var('nB%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "rSFOFerror", ws.var('rSFOF%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "m0error", ws.var('m0').getError(), index = x)
											
							
### routine to plot all the results of a fit
def plotFitResults(ws,theConfig,frameSFOS,frameOFOS,data_obs,fitOFOS,region="Central",H0=False):

	sizeCanvas = 800
	
	### fetch stuff from the config
	shape = theConfig.backgroundShape+theConfig.signalShape
	useMC = theConfig.useMC
	runMinos = theConfig.runMinos
	edgeHypothesis = theConfig.edgePosition
	residualMode = theConfig.residualMode
	luminosity = theConfig.runRange.lumi
	isPreliminary = theConfig.isPreliminary
	year = theConfig.year
	showText = theConfig.showText
	fixEdge = theConfig.fixEdge
	title = theConfig.title
	histoytitle = theConfig.histoytitle
	print year
	
	### make histograms for the legends
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
	if theConfig.plotErrorBands:
		uLeg = dLeg.Clone()
		uLeg.SetLineColor(ROOT.kGreen + 2)
		uLeg.SetFillColor(ROOT.kGreen + 2)
		uLeg.SetFillStyle(3009)
	lmLeg = dLeg.Clone()
	lmLeg.SetLineColor(ROOT.kViolet)
	lmLeg.SetLineStyle(ROOT.kDotted)
	### the number of entries changes if error bands are plotted and if signal is not used for background only plots
	if theConfig.plotErrorBands:
		if not H0:
			nLegendEntries = 6
		else:
			nLegendEntries = 5
	else:	
		if not H0:	
			nLegendEntries = 5
		else:	
			nLegendEntries = 4


	### Legend for the main plot
	### change the legend size according to the number of entries
	sl = tools.myLegend(0.59, 0.89 - 0.06 * nLegendEntries, 0.92, 0.91, borderSize=0)
	sl.SetTextAlign(22)
	if (useMC):
		sl.AddEntry(dLeg, 'Simulation', "pe")
	else:
		sl.AddEntry(dLeg, 'Data', "pe")
	sl.AddEntry(fitLeg, 'Fit', "l")

	if not H0:
		sl.AddEntry(sLeg, 'signal', "l")
	zLeg.SetLineColor(ROOT.kViolet)
	sl.AddEntry(zLeg, 'Drell-Yan background', "l")
	sl.AddEntry(bLeg, 'FS background', "l")
	if theConfig.plotErrorBands:
		sl.AddEntry(uLeg, 'OF uncertainty', "f")
		
	### legend for the OF plot	
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


	### get values for the signal fit to write them into plots
	nSignal = ws.var('nSig%s'%region).getVal()
	nSignalError = ws.var('nSig%s'%region).getError()
		
	annotEdge = 'N_{Signal} = %.1f #pm %.1f' % (nSignal, nSignalError)
	### Minos produces asymmetric uncertainties
	if theConfig.runMinos:
		nSignalError = max(ws.var('nSig%s'%region).getError(),max(abs(ws.var('nSig%s'%region).getAsymErrorHi()),abs(ws.var('nSig%s'%region).getAsymErrorLo())))
		annotEdge = 'fitted N_{S}^{edge} = %.1f #pm %.1f' % (nSignal, nSignalError)

	if theConfig.plotAsymErrs:
		note2 = "m^{edge}_{ll} = %.1f^{+%.1f}_{%.1f} GeV"
		note2 = note2%(ws.var("m0").getVal(),ws.var("m0").getAsymErrorHi(),ws.var("m0").getAsymErrorLo())
	else:
		note2 = "m^{edge}_{ll} = %.1f #pm %.1f GeV"
		note2 = note2%(ws.var("m0").getVal(),ws.var("m0").getError())
	

	sfosName = '%s/fit_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	ofosName = '%s/fit_OFOS_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	eeName = '%s/fit_EE_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	mmName = '%s/fit_MM_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	if H0:
		sfosName = '%s/fit_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		ofosName = '%s/fit_OFOS_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		eeName = '%s/fit_EE_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		mmName = '%s/fit_MM_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)	

	# determine y axis range or set to default values
	#~ yMaximum = 1.2 * max(frameOFOS.GetMaximum(), frameSFOS.GetMaximum())
	yMaximum = 220
	if (theConfig.plotYMax > 0.0):
		yMaximum = theConfig.plotYMax


	# make OFOS plot
	#---------------
	print "before OFOS plot"
	projWData = ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs)
	#if not Holder.nToys > 0:
	slice = ROOT.RooFit.Slice(ws.cat("cat"), "OFOS%s"%region)
	
	frameOFOS = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of e#mu lepton pairs'))
	frameOFOS = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sOFOS" % title, frame=frameOFOS,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::OFOS%s"%region),region=region,H0=H0)
	frameOFOS.GetYaxis().SetTitle(histoytitle)
	cOFOS = ROOT.TCanvas("OFOS distribtution", "OFOS distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cOFOS.cd()
	pads = formatAndDrawFrame(frameOFOS, theConfig, title="OFOS%s"%region, pdf=ws.pdf("combModel"), yMax=yMaximum,
							slice=ROOT.RooFit.Slice(ws.cat("cat"), "OFOS%s"%region),
							projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							residualMode =residualMode)
	annotationsTitle = [
					(0.92, 0.57, "%s" % (theConfig.selection.latex)),
					]
	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)
	bl.Draw()
	if theConfig.useToys == False or (theConfig.useToys == True and theConfig.toyConfig["plotToys"] == True):
		cOFOS.Print(ofosName)	
	for pad in pads:
		pad.Close()


	# make ee plot
	#------------
	
	shapeNames = {}

	shapeNames['Z'] = "zEEShape%s"%region
	shapeNames['offShell'] = "offShell%s"%region
	shapeNames['Signal'] = "eeShape%s"%region

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "EE%s"%region)

	frameEE = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
	frameEE = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sEE" % title, frame=frameEE,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::EE%s"%region),
						overrideShapeNames=shapeNames,region=region,H0=H0)

	cEE = ROOT.TCanvas("EE distribtution", "EE distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cEE.cd()
	pads = formatAndDrawFrame(frameEE, theConfig, title="EE%s"%region, pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "EE%s"%region),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode =residualMode)

	annotationsTitle = [
					   (0.92, 0.53, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.47, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)

	frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
	frameEE.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cEE.Update()
	if theConfig.useToys == False or (theConfig.useToys == True and theConfig.toyConfig["plotToys"] == True):
		cEE.Print(eeName)
	for pad in pads:
		pad.Close()


	# make mm plot
	#------------
	shapeNames['Z'] = "zMMShape%s"%region
	shapeNames['Signal'] = "mmShape%s"%region
	shapeNames['offShell'] = "offShell%s"%region

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "MM%s"%region)

	frameMM = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of mumu lepton pairs'))
	frameMM = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sMM" % title, frame=frameMM,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::MM%s"%region),
						overrideShapeNames=shapeNames,region=region,H0=H0)

	cMM = ROOT.TCanvas("MM distribtution", "MM distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cMM.cd()
	pads = formatAndDrawFrame(frameMM, theConfig, title="MM%s"%region, pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "MM%s"%region),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode=residualMode)

	annotationsTitle = [
					   (0.92, 0.53, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.47, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)

	frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
	frameMM.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cMM.Update()
	if theConfig.useToys == False or (theConfig.useToys == True and theConfig.toyConfig["plotToys"] == True):
		cMM.Print(mmName)
	for pad in pads:
		pad.Close()


	# make SFOS plot
	#---------------
	cSFOS = ROOT.TCanvas("SFOS distribtution", "SFOS distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cSFOS.cd()
	pads = formatAndDrawFrame(frameSFOS, theConfig, title="SFOS%s"%region, pdf=ws.pdf("model%s"%region), yMax=yMaximum, residualMode=residualMode)

	if (not fixEdge):
		edgeHypothesis = ws.var('m0').getVal()

	if not H0:
		annotationsTitle = [
						   (0.92, 0.53, "%s" % (theConfig.selection.latex)),
						   (0.92, 0.47, "%s" % (note2)),
						   ]
	else:
		annotationsTitle = [
							(0.92, 0.53, "%s" % (theConfig.selection.latex)),
							]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)
	annotationsFit = [
					   (0.92, 0.41, annotEdge),
					   ]
	if (showText):
		if not H0:
			tools.makeAnnotations(annotationsFit, color=ROOT.kBlue, textSize=0.04, align=31)
	sl.Draw()
	if theConfig.useToys == False or (theConfig.useToys == True and theConfig.toyConfig["plotToys"] == True):
		cSFOS.Print(sfosName)
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
	parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="SignalInclusive",
						  help="selection which to apply.")
	parser.add_argument("-r", "--runRange", dest="runRange", action="store", default="Run2015_25ns",
						  help="name of run range.")
	parser.add_argument("-b", "--backgroundShape", dest="backgroundShape", action="store", default="CB",
						  help="background shape, default CB")
	parser.add_argument("-e", "--edgeShape", dest="edgeShape", action="store", default="Triangle",
						  help="edge shape, default Triangle")
	parser.add_argument("-c", "--configuration", dest="config", action="store", default="Combined",
						  help="dataset configuration, default Combined")
	parser.add_argument("-t", "--toys", dest="toys", action="store", default=0,
						  help="generate and fit x toys")
	parser.add_argument("-a", "--addSignal", action="store", dest="addSignal", default="",
						  help="add signal MC.")		
	parser.add_argument("-x", "--private", action="store_true", dest="private", default=False,
						  help="plot is private work.")		
	parser.add_argument("-p", "--paper", action="store_true", dest="paper", default=False,
						  help="plot for paper without preliminary label.")		
					
	args = parser.parse_args()	


	region = args.selection
	backgroundShape = args.backgroundShape
	signalShape = args.edgeShape
	runName =args.runRange
	dataSetConfiguration = args.config
	
	### We can perform the fit either in central or forward or both combined
	if not args.config == "Central" and not args.config == "Forward" and not args.config == "Combined":
		log.logError("Dataset %s not not known, exiting" % dataSet)
		sys.exit()
	useExistingDataset = args.useExisting
		
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region,backgroundShape,signalShape,runName,args.config,args.mc,args.toys,args.addSignal)
	
	if args.paper:
		theConfig.isPreliminary = False
	if args.private:
		theConfig.ownWork = True
	
	# init ROOT
	gROOT.Reset()
	gROOT.SetStyle("Plain")
	setTDRStyle()
	ROOT.gROOT.SetStyle("tdrStyle")	
	
	#set random random seed for RooFit, for toy generation
	ROOT.RooRandom.randomGenerator().SetSeed(0)
	
	### get the additional shapes
	ROOT.gSystem.Load("shapes/RooSUSYTPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYX4Pdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYXM4Pdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgMoreParamsPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgBHPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYOldBkgPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgMAPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgGaussiansPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooTopPairProductionSpline_cxx.so")
	ROOT.gSystem.Load("libFFTW.so") 

	# get data
	theDataInterface = dataInterface.DataInterface(theConfig.dataSetPath,theConfig.dataVersion)
	treeOFOS = None
	treeEE = None
	treeMM = None

	treePathOFOS = "/EMuDileptonTree"
	treePathEE = "/EEDileptonTree"
	treePathMM = "/MuMuDileptonTree"

	
	
	if not useExistingDataset:
		### get the datasets if not existing ones are used
		if (theConfig.useMC):
			log.logHighlighted("Using MC instead of data.")
			datasets = theConfig.mcdatasets 
			(treeOFOSCentral, treeEECentral, treeMMCentral) = tools.getTrees(theConfig, datasets,etaRegion="Central")
			(treeOFOSForward, treeEEForward, treeMMForward) = tools.getTrees(theConfig, datasets,etaRegion="Forward")
		else:
			treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")
			treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")
			treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")

			# convert trees to a simpler and smaller format
			treeOFOSCentral = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
			treeEECentral = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
			treeMMCentral = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
			
			treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")
			treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")
			treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")

			# convert trees
			treeOFOSForward = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
			treeEEForward = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
			treeMMForward = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
		
		if (theConfig.addDataset != None):
			### Add signal dataset			
			denominatorFile = TFile("../SignalScan/T6bbllsleptonDenominatorHisto.root")
			denominatorHisto = TH2F(denominatorFile.Get("massScan"))
			
			denominator = denominatorHisto.GetBinContent(denominatorHisto.GetXaxis().FindBin(int(theConfig.addDataset.split("_")[1])),denominatorHisto.GetYaxis().FindBin(int(theConfig.addDataset.split("_")[2])))


			# cross section scaling
			jobs = dataInterface.InfoHolder.theDataSamples[theConfig.dataVersion][theConfig.addDataset]
			if (len(jobs) > 1):
				log.logError("Scaling of added MC samples not implemented. MC yield is wrong!")
			for job in jobs:
				dynNTotal = theDataInterface.getEventCount(job, theConfig.flag, theConfig.task)
				dynXsection = theDataInterface.getCrossSection(job)
				dynScale = dynXsection * theConfig.runRange.lumi / denominator
				print dynXsection
				print denominator
				scale = dynScale


			log.logHighlighted("Scaling added dataset (%s) with %f (dynamic)" % (theConfig.addDataset, scale))
			
			### get the trees
			treeAddOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")
			treeAddEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")
			treeAddMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Central")

			### convert them to smaller format
			treeAddOFOSCentral = dataInterface.DataInterface.convertDileptonTree(treeAddOFOSraw, weight=scale)
			treeAddEECentral = dataInterface.DataInterface.convertDileptonTree(treeAddEEraw, weight=scale)
			treeAddMMCentral = dataInterface.DataInterface.convertDileptonTree(treeAddMMraw, weight=scale)
			
			treeAddOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")
			treeAddEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")
			treeAddMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,etaRegion="Forward")

			treeAddOFOSForward = dataInterface.DataInterface.convertDileptonTree(treeAddOFOSraw, weight=scale)
			treeAddEEForward = dataInterface.DataInterface.convertDileptonTree(treeAddEEraw, weight=scale)
			treeAddMMForward = dataInterface.DataInterface.convertDileptonTree(treeAddMMraw, weight=scale)


		treesCentral = {"EE":treeEECentral,"MM":treeMMCentral,"OFOS":treeOFOSCentral}
		addTreesCentral = {}
		treesForward = {"EE":treeEEForward,"MM":treeMMForward,"OFOS":treeOFOSForward}
		addTreesForward = {}
		if theConfig.addDataset != None:
			addTreesCentral = {"EE":treeAddEECentral,"MM":treeAddMMCentral,"OFOS":treeAddOFOSCentral}
			addTreesForward = {"EE":treeAddEEForward,"MM":treeAddMMForward,"OFOS":treeAddOFOSForward}

		### set variables to be used, inv=mll, weight for PU weight
		weight = ROOT.RooRealVar("weight","weight",1.,0.,10.)
		inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		
		### get the RooDataSets
		typeName = "dataCentral"
		dataSetsCentral = prepareDatasets(inv,weight,treesCentral,addTreesCentral,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.central.val,theConfig.rSFOF.central.err,theConfig.addDataset,theConfig,region="Central")
		typeName = "dataForward"
		dataSetsForward = prepareDatasets(inv,weight,treesForward,addTreesForward,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.forward.val,theConfig.rSFOF.forward.err,theConfig.addDataset,theConfig,region="Forward")

	else:
		dataSetsCentral = ["dummy"]
		dataSetsForward = ["dummy"]
	log.logDebug("Starting edge fit")
		

	



	# silences all the info messages
	# 1 does not silence info messages, so 2 probably just suppresses these, but keeps the warnings
	#ROOT.RooMsgService.instance().Print()
	ROOT.RooMsgService.instance().setGlobalKillBelow(10)
	
	### Adapt the title depending on the config
	if theConfig.toyConfig["nToys"] > 0:
		theConfig.title = "%s_Scale%sMo%sSignalN%s"%(theConfig.title, theConfig.toyConfig["scale"], theConfig.toyConfig["m0"], theConfig.toyConfig["nSig"])

	if theConfig.fixEdge:
		theConfig.title = theConfig.title+"_FixedEdge_%.1f"%theConfig.edgePosition
	if theConfig.useMC:
		theConfig.title = theConfig.title+"_MC"
 	if theConfig.isSignal:
		theConfig.title = theConfig.title+"_SignalInjected_"+theConfig.signalDataSets[0]   	
					
	titleSave = theConfig.title	
	

	### Loop over all the datasets. For the normal fit is is only one iteration
	### but for toys one does this for each toy dataset
	
	### Since Root 6 there one gets error messages when reusing a workspace
	### or importing an already existing variable or shape
	### This is only a problem for toys
	### Thus create a workspace for each iteration
	
	w = {}	
				
	for index, dataSet in enumerate(dataSetsCentral):
		
		if theConfig.toyConfig["nToys"] > 0:
			### toys get a random index to identify them and adapt the title according to the configuration
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
			### Setup the workspace and import the datasets
			w[index] = ROOT.RooWorkspace("w%s"%index, ROOT.kTRUE)
			w[index].factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
			w[index].factory("weight[1.,0.,10.]")
			vars = ROOT.RooArgSet(inv, w[index].var('weight'))
			
			
			dataEECentral = dataSetsCentral[index]["EE"].Clone("dataEECentral")
			dataMMCentral = dataSetsCentral[index]["MM"].Clone("dataMMCentral")
			dataOFOSCentral = dataSetsCentral[index]["OFOS"].Clone("dataOFOSCentral")
			dataSFOSCentral = dataSetsCentral[index]["SFOS"].Clone("dataSFOSCentral")
			
			
			dataEEForward = dataSetsForward[index]["EE"].Clone("dataEEForward")
			dataMMForward = dataSetsForward[index]["MM"].Clone("dataMMForward")
			dataOFOSForward = dataSetsForward[index]["OFOS"].Clone("dataOFOSForward")
			dataSFOSForward = dataSetsForward[index]["SFOS"].Clone("dataSFOSForward")
			
			## this is kind of stupid, but since ROOT 6 getattr(w,'import')(inv) does not work any more
			## and RooFit needs another dummy entry to perform correctly e.g. getattr(w,'import')(dataset, ROOT.RooCmdArg())

			getattr(w[index], 'import')(dataEECentral, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataMMCentral, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataOFOSCentral, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataSFOSCentral, ROOT.RooCmdArg())		
			
			getattr(w[index], 'import')(dataEEForward, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataMMForward, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataOFOSForward, ROOT.RooCmdArg())
			getattr(w[index], 'import')(dataSFOSForward, ROOT.RooCmdArg())
		
			if x == None:
				if theConfig.useMC:
					w[index].writeToFile("workspaces/saveDataSet_%s_MC.root"%theConfig.selection.name)		
				else:
					w[index].writeToFile("workspaces/saveDataSet_%s_Data.root"%theConfig.selection.name)		
		
		else:
			### Import an existing dataset
			if theConfig.useMC:
				f = ROOT.TFile("workspaces/saveDataSet_%s_MC.root"%theConfig.selection.name)
			else:
				f = ROOT.TFile("workspaces/saveDataSet_%s_Data.root"%theConfig.selection.name)
			w = f.Get("w%s"%index)
			w[index].Print()			
			
			### Get the additional signal datasets
			if len(theConfig.signalDataSets) > 0:
				(treeOFOSCentralSignal, treeEECentralSignal, treeMMCentralSignal) = tools.getTrees(theConfig, theConfig.signalDataSets,etaRegion="Central")
				(treeOFOSForwardSignal, treeEEForwardSignal, treeMMForwardSignal) = tools.getTrees(theConfig, theConfig.signalDataSets,etaRegion="Forward")
			
				signalTreesCentral = {"EE":treeEECentralSignal,"MM":treeMMCentralSignal,"OFOS":treeOFOSCentralSignal}
				addSignalTreesCentral = {}
				signalTreesForward = {"EE":treeEEForwardSignal,"MM":treeMMForwardSignal,"OFOS":treeOFOSForwardSignal}
				addSignalTreesForward = {}				
										
				typeName = "signalCentral"
				dataSetsCentral = prepareDatasets(w[index].var("inv"),w[index].var('weight'),signalTreesCentral,addSignalTreesCentral,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.central.val,theConfig.rSFOF.central.err,False,theConfig,region="Central")
				typeName = "signalForward"
				dataSetsForward = prepareDatasets(w[index].var("inv"),w[index].var('weight'),signalTreesForward,addSignalTreesForward,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.forward.val,theConfig.rSFOF.forward.err,False,theConfig,region="Forward")
				
				w[index].data("dataEECentral").append(dataSetsCentral[index]["EE"].Clone("signalEECentral"))
				w[index].data("dataMMCentral").append(dataSetsCentral[index]["MM"].Clone("signalMMCentral"))
				w[index].data("dataOFOSCentral").append(dataSetsCentral[index]["OFOS"].Clone("signalOFOSCentral"))
				w[index].data("dataSFOSCentral").append(dataSetsCentral[index]["SFOS"].Clone("signalSFOSCentral"))
				
				w[index].data("dataEEForward").append(dataSetsForward[index]["EE"].Clone("signalEEForward"))
				w[index].data("dataMMForward").append(dataSetsForward[index]["MM"].Clone("signalMMForward"))
				w[index].data("dataOFOSForward").append(dataSetsForward[index]["OFOS"].Clone("signalOFOSForward"))
				w[index].data("dataSFOSForward").append(dataSetsForward[index]["SFOS"].Clone("signalSFOSForward"))

		
		### get the variables and shapes
		vars = ROOT.RooArgSet(w[index].var('inv'), w[index].var('weight'))
		selectShapes(w[index],theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)


		print w[index].data("dataSFOSCentral").sumEntries(), w[index].data("dataOFOSCentral").sumEntries()

	
		# deduce proper values for yield parameters from datasets and create yield parameters
		### Assume 20% of the events to be signal for the range to be tried
		predictedSignalYieldCentral = 0.2*w[index].data("dataSFOSCentral").sumEntries()
		predictedSignalYieldForward = 0.2*w[index].data("dataSFOSForward").sumEntries()
		if theConfig.allowNegSignal:
			w[index].factory("nSigCentral[%f,%f,%f]" % (0.,-2*predictedSignalYieldCentral, 2*predictedSignalYieldCentral))
			w[index].factory("nSigForward[%f,%f,%f]" % (0.,-4*predictedSignalYieldForward, 4*predictedSignalYieldForward))
		else:
			w[index].factory("nSigCentral[%f,%f,%f]" % (0.,0, 2*predictedSignalYieldCentral))
			w[index].factory("nSigForward[%f,%f,%f]" % (0.,0, 2*predictedSignalYieldForward))		
		w[index].var('nSigCentral').setAttribute("StoreAsymError")
		w[index].var('nSigForward').setAttribute("StoreAsymError")
		


		### Upper limit for Z contribution = 100% of the events on the Z peak
		maxZCentral = w[index].data("dataSFOSCentral").sumEntries("abs(inv-91.2) < 20")	
		maxZForward = w[index].data("dataSFOSForward").sumEntries("abs(inv-91.2) < 20")
		
		w[index].factory("nZCentral[%f,0.,%f]" % (theConfig.zPredictions.default.SF.central.val,maxZCentral))
		w[index].factory("nZForward[%f,0.,%f]" % (theConfig.zPredictions.default.SF.forward.val,maxZForward))
		
		
		### Range and starting values for the number of flavor symmetric background events
		nBMinCentral = w[index].data("dataOFOSCentral").sumEntries()*0
		nBMaxCentral= w[index].data("dataSFOSCentral").sumEntries()*2
		nBStartCentral = w[index].data("dataOFOSCentral").sumEntries()*0.7
		nBMinForward = w[index].data("dataOFOSForward").sumEntries()*0
		nBMaxForward= w[index].data("dataSFOSForward").sumEntries()*2
		nBStartForward = w[index].data("dataOFOSForward").sumEntries()*0.7		
		
		w[index].factory("nBCentral[%f,%f,%f]" % (nBStartCentral,nBMinCentral,nBMaxCentral))	
		w[index].factory("nBForward[%f,%f,%f]" % (nBStartForward,nBMinForward,nBMaxForward))	
		w[index].var('nBCentral').setAttribute("StoreAsymError")
		w[index].var('nBForward').setAttribute("StoreAsymError")

		#create background only shapes
			
		w[index].factory("SUM::ofosShapeCentral(nBCentral*ofosShape1Central)")
		w[index].factory("SUM::ofosShapeForward(nBForward*ofosShape1Forward)")
		
		# fit background only shapes to OFOS dataset
		w[index].Print()
		fitOFOSCentral = w[index].pdf('ofosShapeCentral').fitTo(w[index].data("dataOFOSCentral"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
		
		fitOFOSCentral.Print()
		
		fitOFOSForward = w[index].pdf('ofosShapeForward').fitTo(w[index].data("dataOFOSForward"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
		
		fitOFOSForward.Print()
		
		
		log.logWarning("Central OFOS Fit Convergence Quality: %d"%fitOFOSCentral.covQual())
		log.logWarning("Forward OFOS Fit Convergence Quality: %d"%fitOFOSForward.covQual())
		
		### Save parameters
		parametersToSave["minNllOFOSCentral"] = fitOFOSCentral.minNll()
		parametersToSave["minNllOFOSForward"] = fitOFOSCentral.minNll()

		parametersToSave["nParOFOSCentral"] = fitOFOSCentral.floatParsFinal().getSize()
		parametersToSave["nParOFOSForward"] = fitOFOSCentral.floatParsFinal().getSize()


		frameOFOSCentral = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		frameOFOSCentral.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		frameOFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
		frameOFOSForward = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		frameOFOSForward.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		frameOFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

		parametersToSave["chi2OFOSCentral"] = frameOFOSCentral.chiSquare(parametersToSave["nParOFOSCentral"])
		log.logDebug("Chi2 OFOS: %f" % parametersToSave["chi2OFOSCentral"])
		parametersToSave["chi2OFOSForward"] = frameOFOSForward.chiSquare(parametersToSave["nParOFOSForward"])
		log.logDebug("Chi2 OFOS: %f" % parametersToSave["chi2OFOSForward"])

		
		### plot the fit results
		ROOT.RooAbsData.plotOn(w[index].data("dataOFOSCentral"), frameOFOSCentral)
		w[index].pdf('ofosShapeCentral').plotOn(frameOFOSCentral)
		ROOT.RooAbsData.plotOn(w[index].data("dataOFOSForward"), frameOFOSForward)
		w[index].pdf('ofosShapeForward').plotOn(frameOFOSForward)


		w[index].pdf('ofosShapeCentral').plotOn(frameOFOSCentral,
								  ROOT.RooFit.LineWidth(2))
		w[index].pdf('ofosShapeCentral').plotOn(frameOFOSCentral)
		ROOT.RooAbsData.plotOn(w[index].data("dataOFOSCentral"), frameOFOSCentral)

		w[index].pdf('ofosShapeForward').plotOn(frameOFOSForward,
								  ROOT.RooFit.LineWidth(2))
		w[index].pdf('ofosShapeForward').plotOn(frameOFOSForward)
		ROOT.RooAbsData.plotOn(w[index].data("dataOFOSForward"), frameOFOSForward)


		# Fit SFOS distribution
		w[index].factory("rSFOFCentral[%f,%f,%f]" % (theConfig.rSFOF.central.val, theConfig.rSFOF.central.val - 4*theConfig.rSFOF.central.err, theConfig.rSFOF.central.val + 4*theConfig.rSFOF.central.err))
		w[index].factory("rSFOFMeasuredCentral[%f]" % (theConfig.rSFOF.central.val))
		w[index].factory("rSFOFMeasuredCentralErr[%f]" % (theConfig.rSFOF.central.err))
		w[index].factory("rSFOFForward[%f,%f,%f]" % (theConfig.rSFOF.forward.val, theConfig.rSFOF.forward.val - 4*theConfig.rSFOF.forward.err, theConfig.rSFOF.forward.val + 4*theConfig.rSFOF.forward.err))
		w[index].factory("rSFOFMeasuredForward[%f]" % (theConfig.rSFOF.forward.val))
		w[index].factory("rSFOFMeasuredForwardErr[%f]" % (theConfig.rSFOF.forward.err))
		
		w[index].factory("feeCentral[0.5,0.,1.]")
		w[index].factory("feeForward[0.5,0.,1.]")
		w[index].factory("Gaussian::constraintRSFOFForward(rSFOFForward,rSFOFMeasuredForward,rSFOFMeasuredForwardErr)")
		w[index].factory("Gaussian::constraintRSFOFCentral(rSFOFCentral,rSFOFMeasuredCentral,rSFOFMeasuredCentralErr)")

		### import formulars for the different yields (signal, flavor symmetric background, Z, for ee and mumu), which depend on the dilepton fraction
		### RSFOF (For flavor-symmetric background) and the total numbers for these backgrounds
		nSigEECentral = ROOT.RooFormulaVar('nSigEECentral', '@0*@1', ROOT.RooArgList(w[index].var('feeCentral'), w[index].var('nSigCentral')))
		getattr(w[index], 'import')(nSigEECentral, ROOT.RooCmdArg())
		nSigMMCentral = ROOT.RooFormulaVar('nSigMMCentral', '(1-@0)*@1', ROOT.RooArgList(w[index].var('feeCentral'), w[index].var('nSigCentral')))
		getattr(w[index], 'import')(nSigMMCentral, ROOT.RooCmdArg())			
		nZEECentral = ROOT.RooFormulaVar('nZEECentral', '@0*@1', ROOT.RooArgList(w[index].var('feeCentral'), w[index].var('nZCentral')))
		getattr(w[index], 'import')(nZEECentral, ROOT.RooCmdArg())
		nZMMCentral = ROOT.RooFormulaVar('nZMMCentral', '(1-@0)*@1', ROOT.RooArgList(w[index].var('feeCentral'), w[index].var('nZCentral')))
		getattr(w[index], 'import')(nZMMCentral, ROOT.RooCmdArg())
		nBEECentral = ROOT.RooFormulaVar('nBEECentral', '@0*@1*@2', ROOT.RooArgList(w[index].var('feeCentral'),w[index].var('rSFOFCentral'), w[index].var('nBCentral')))
		getattr(w[index], 'import')(nBEECentral, ROOT.RooCmdArg())
		nBMMCentral = ROOT.RooFormulaVar('nBMMCentral', '(1-@0)*@1*@2', ROOT.RooArgList(w[index].var('feeCentral'),w[index].var('rSFOFCentral'), w[index].var('nBCentral')))
		getattr(w[index], 'import')(nBMMCentral, ROOT.RooCmdArg())								
		nSigEEForward = ROOT.RooFormulaVar('nSigEEForward', '@0*@1', ROOT.RooArgList(w[index].var('feeForward'), w[index].var('nSigForward')))
		getattr(w[index], 'import')(nSigEEForward, ROOT.RooCmdArg())
		nSigMMForward = ROOT.RooFormulaVar('nSigMMForward', '(1-@0)*@1', ROOT.RooArgList(w[index].var('feeForward'), w[index].var('nSigForward')))
		getattr(w[index], 'import')(nSigMMForward, ROOT.RooCmdArg())			
		nZEEForward = ROOT.RooFormulaVar('nZEEForward', '@0*@1', ROOT.RooArgList(w[index].var('feeForward'), w[index].var('nZForward')))
		getattr(w[index], 'import')(nZEEForward, ROOT.RooCmdArg())
		nZMMForward = ROOT.RooFormulaVar('nZMMForward', '(1-@0)*@1', ROOT.RooArgList(w[index].var('feeForward'), w[index].var('nZForward')))
		getattr(w[index], 'import')(nZMMForward, ROOT.RooCmdArg())
		nBEEForward = ROOT.RooFormulaVar('nBEEForward', '@0*@1*@2', ROOT.RooArgList(w[index].var('feeForward'),w[index].var('rSFOFForward'), w[index].var('nBForward')))
		getattr(w[index], 'import')(nBEEForward, ROOT.RooCmdArg())
		nBMMForward = ROOT.RooFormulaVar('nBMMForward', '(1-@0)*@1*@2', ROOT.RooArgList(w[index].var('feeForward'),w[index].var('rSFOFForward'), w[index].var('nBForward')))
		getattr(w[index], 'import')(nBMMForward, ROOT.RooCmdArg())
		### constraints in RSFOF							
		constraints = ROOT.RooArgSet(w[index].pdf("constraintRSFOFCentral"),w[index].pdf("constraintRSFOFForward"))			
		
		### combine the diffent contributions
		w[index].factory("SUM::zShapeCentral(nZEECentral*zEEShapeCentral,nZMMCentral*zMMShapeCentral)")	
		w[index].factory("SUM::zShapeForward(nZEEForward*zEEShapeForward,nZMMForward*zMMShapeForward)")	
		w[index].factory("Voigtian::zShapeSeparately(inv,zmean,zwidth,s)")		


		### All 3 components
		w[index].factory("SUM::modelCentral(nSigCentral*sfosShapeCentral, nBCentral*ofosShapeCentral, nZCentral*zShapeCentral)")
		w[index].factory("SUM::mEECentral(nSigEECentral*eeShapeCentral, nBEECentral*ofosShapeCentral, nZEECentral*zEEShapeCentral)")
		w[index].factory("SUM::mMMCentral(nSigMMCentral*mmShapeCentral, nBMMCentral*ofosShapeCentral, nZMMCentral*zMMShapeCentral)")
		
		### constraints
		w[index].factory("PROD::constraintMEECentral(mEECentral, constraintRSFOFCentral)")
		w[index].factory("PROD::constraintMMMCentral(mMMCentral, constraintRSFOFCentral)")
		
		### background only
		w[index].factory("SUM::modelBgOnlyCentral( nBCentral*ofosShapeCentral, nZCentral*zShapeCentral)")
		w[index].factory("SUM::mEEBgOnlyCentral( nBEECentral*ofosShapeCentral, nZEECentral*zEEShapeCentral)")
		w[index].factory("SUM::mMMBgOnlyCentral( nBMMCentral*ofosShapeCentral, nZMMCentral*zMMShapeCentral)")
		
		### constraints
		w[index].factory("PROD::constraintMEEBgOnlyCentral( mEEBgOnlyCentral, constraintRSFOFCentral)")
		w[index].factory("PROD::constraintMMMBgOnlyCentral( mMMBgOnlyCentral, constraintRSFOFCentral)")
		
		
		### same for forward
		w[index].factory("SUM::modelForward(nSigForward*sfosShapeForward, nBForward*ofosShapeForward, nZForward*zShapeForward)")
		w[index].factory("SUM::mEEForward(nSigEEForward*eeShapeForward, nBEEForward*ofosShapeForward, nZEEForward*zEEShapeForward)")
		w[index].factory("SUM::mMMForward(nSigMMForward*mmShapeForward, nBMMForward*ofosShapeForward, nZMMForward*zMMShapeForward)")
				
		w[index].factory("PROD::constraintMEEForward(mEEForward,constraintRSFOFForward)")
		w[index].factory("PROD::constraintMMMForward(mMMForward,constraintRSFOFForward)")
				
		w[index].factory("SUM::modelBgOnlyForward( nBForward*ofosShapeForward, nZForward*zShapeForward)")
		w[index].factory("SUM::mEEBgOnlyForward( nBEEForward*ofosShapeForward, nZEEForward*zEEShapeForward)")
		w[index].factory("SUM::mMMBgOnlyForward( nBMMForward*ofosShapeForward, nZMMForward*zMMShapeForward)")
				
		
		w[index].factory("PROD::constraintMEEBgOnlyForward( mEEBgOnlyForward,constraintRSFOFForward)")
		w[index].factory("PROD::constraintMMMBgOnlyForward( mMMBgOnlyForward,constraintRSFOFForward)")
		
		### get the fit model for the chosen fit configuration (combined, central or forward) and import it	
		if dataSetConfiguration == "Combined":
			
			### background only
			w[index].factory("SIMUL::combModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=mEEBgOnlyCentral, MMCentral=mMMBgOnlyCentral, OFOSCentral=ofosShapeCentral, EEForward=mEEBgOnlyForward, MMForward=mMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			
			### full model
			w[index].factory("SIMUL::combModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=mEECentral, MMCentral=mMMCentral, OFOSCentral=ofosShapeCentral, EEForward=mEEForward, MMForward=mMMForward, OFOSForward=ofosShapeForward)")
					
			### all inout datasets	
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w[index].cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSCentral', w[index].data("dataOFOSCentral")),
									   ROOT.RooFit.Import('EECentral', w[index].data("dataEECentral")),
									   ROOT.RooFit.Import('MMCentral', w[index].data("dataMMCentral")),
									   ROOT.RooFit.Import('OFOSForward', w[index].data("dataOFOSForward")),
									   ROOT.RooFit.Import('EEForward', w[index].data("dataEEForward")),
									   ROOT.RooFit.Import('MMForward', w[index].data("dataMMForward")))
			getattr(w[index], 'import')(data_obs, ROOT.RooCmdArg())
			
		elif dataSetConfiguration == "Central":			
			w[index].factory("SIMUL::combModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=mEEBgOnlyCentral, MMCentral=mMMBgOnlyCentral, OFOSCentral=ofosShapeCentral)")
			# real model
			
			w[index].factory("SIMUL::combModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=mEECentral, MMCentral=mMMCentral, OFOSCentral=ofosShapeCentral)")		
				
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w[index].cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSCentral', w[index].data("dataOFOSCentral")),
									   ROOT.RooFit.Import('EECentral', w[index].data("dataEECentral")),
									   ROOT.RooFit.Import('MMCentral', w[index].data("dataMMCentral")))
			getattr(w[index], 'import')(data_obs, ROOT.RooCmdArg())
			w[index].var("rSFOFForward").setConstant()

		elif dataSetConfiguration == "Forward":
			w[index].factory("SIMUL::combModelBgOnly(cat[EEForward=0,MMForward=1,OFOSForward=2], EEForward=mEEBgOnlyForward, MMForward=mMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			# real model
			
			w[index].factory("SIMUL::combModel(cat[EEForward=0,MMForward=1,OFOSForward=2],  EEForward=mEEForward, MMForward=mMMForward, OFOSForward=ofosShapeForward)")
					
				
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w[index].cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSForward', w[index].data("dataOFOSForward")),
									   ROOT.RooFit.Import('EEForward', w[index].data("dataEEForward")),
									   ROOT.RooFit.Import('MMForward', w[index].data("dataMMForward")))
			getattr(w[index], 'import')(data_obs, ROOT.RooCmdArg())

			w[index].var("rSFOFCentral").setConstant()

						
		log.logWarning("Attempting background only Fit!")
		### background only fit	(H0)
		bgOnlyFit = w[index].pdf('combModelBgOnly').fitTo(w[index].data('data_obs'),
											ROOT.RooFit.Save(),
											ROOT.RooFit.SumW2Error(ROOT.kFALSE),
											ROOT.RooFit.Minos(theConfig.runMinos),
											ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet(w[index].pdf("constraintRSFOFCentral"),
																							w[index].pdf("constraintRSFOFForward"))),
											ROOT.RooFit.Extended(ROOT.kTRUE),
											ROOT.RooFit.Strategy(1))
											
		fitResult = bgOnlyFit.covQual()
		parametersToSave["minNllH0"] = bgOnlyFit.minNll()
		parametersToSave["nParH0"] = bgOnlyFit.floatParsFinal().getSize()
		log.logHighlighted("Background Only Fit Convergence Quality: %d"%fitResult)

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")
		

		w[index].var('inv').setBins(theConfig.nBinsMinv)

		### plot the results		
		if dataSetConfiguration == "Combined":
			frameSFOSCentral = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w[index], w[index].data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, region="Central",H0=True)
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w[index],theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central",H0=True)	
			
			frameSFOSForward = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w[index], w[index].data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, region="Forward",H0=True)
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

			plotFitResults(w[index],theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward",H0=True)	

		elif dataSetConfiguration == "Central":		
			frameSFOSCentral = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w[index], w[index].data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, region="Central",H0=True)
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w[index],theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central",H0=True)	
							
		if dataSetConfiguration == "Forward":		
			frameSFOSForward = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w[index], w[index].data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, region="Forward",H0=True)
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

			plotFitResults(w[index],theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward",H0=True)	



					   
		w[index].var("rSFOFCentral").setVal(theConfig.rSFOF.central.val)
		w[index].var("rSFOFForward").setVal(theConfig.rSFOF.forward.val)
		if (theConfig.edgePosition > 0):
			w[index].var('m0').setVal(float(theConfig.edgePosition))
			if theConfig.randomStartPoint:

				randomm0 = random.random()*300
				if randomm0 < 35:
					randomm0 = 35
				log.logWarning("Warning! Randomized initial value of m0 = %.1f"%randomm0)

				w[index].var('m0').setVal(float(randomm0))	
			
			
			if not x == None:
				w[index].var('m0').setVal(float(theConfig.toyConfig["m0"]))
				if theConfig.toyConfig["rand"]:

					randomm0 = random.random()*300
					if randomm0 < 35:
						randomm0 = 35
					log.logWarning("Warning! Randomized initial value of m0 = %.1f"%randomm0)

					w[index].var('m0').setVal(float(randomm0))					
			if (theConfig.fixEdge):
				w[index].var('m0').setConstant(ROOT.kTRUE)
			else:
				log.logWarning("Edge endpoint floating!")


		### Full fit
						
		hasConverged = False
		log.logWarning("Attempting combined Fit!")		
		
		signalFit = w[index].pdf('combModel').fitTo(w[index].data('data_obs'),
											ROOT.RooFit.Save(),
											ROOT.RooFit.SumW2Error(ROOT.kFALSE),
											ROOT.RooFit.Minos(theConfig.runMinos),
											ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet(w[index].pdf("constraintRSFOFCentral"),
																							w[index].pdf("constraintRSFOFForward"))),
											ROOT.RooFit.Extended(ROOT.kTRUE),
											ROOT.RooFit.Strategy(1))
											
		fitResult = signalFit.covQual()
		parametersToSave["minNllH1"] = signalFit.minNll()
		parametersToSave["nParH1"] = signalFit.floatParsFinal().getSize()
		parametersToSave["initialM0"] = theConfig.edgePosition
		if theConfig.toyConfig["rand"]:
			parametersToSave["initialM0"] = randomm0
		log.logHighlighted("Main Fit Convergence Quality: %d"%fitResult)

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")

		sizeCanvas = 800
		
		### plot the results and save the parameters
		if dataSetConfiguration == "Combined":
			frameSFOSCentral = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w[index], w[index].data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w[index],theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central")	
			
			frameSFOSForward = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w[index], w[index].data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)
			
			
			parametersToSave["chi2SFOSCentral"] = frameSFOSCentral.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSCentral"])
			parametersToSave["chi2SFOSForward"] = frameSFOSForward.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSForward"])


			plotFitResults(w[index],theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward")	

			saveFitResults(w[index],theConfig,x,region="Central")		
			saveFitResults(w[index],theConfig,x,region="Forward")	
		elif dataSetConfiguration == "Central":		
			frameSFOSCentral = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w[index], w[index].data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w[index],theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central")	
					
			parametersToSave["chi2SFOSCentral"] = frameSFOSCentral.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSCentral"])

			saveFitResults(w[index],theConfig,x,region="Central")		
		elif dataSetConfiguration == "Forward":		
			frameSFOSForward = w[index].var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w[index], w[index].data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

			parametersToSave["chi2SFOSForward"] = frameSFOSForward.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSForward"])

			plotFitResults(w[index],theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward")	
		
			saveFitResults(w[index],theConfig,x,region="Forward")	
		
	

main()
