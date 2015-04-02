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




def prepareDatasets(inv,weight,trees,addTrees,maxInv,minInv,typeName,nBinsMinv,rSFOF,rSFOFErr,addDataset,theConfig,region="Central"):


	vars = ROOT.RooArgSet(inv, weight)
	

	# data
	
	tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(trees["EE"]), ROOT.RooFit.WeightVar("weight"))
	tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpOFOS = ROOT.RooDataSet("tmpOFOS", "tmpOFOS", vars, ROOT.RooFit.Import(trees["OFOS"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS = ROOT.RooDataSet("tmpSFOS", "tmpSFOS", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS.append(tmpEE)

	# add MC signal
	tmpAddEE = None
	tmpAddMM = None
	tmpAddOFOS = None
	if (addDataset != None and addTrees != None):
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

	


	
	if theConfig.toyConfig["nToys"] > 0:
		log.logHighlighted("Preparing to dice %d Toys"%theConfig.toyConfig["nToys"])
		rand = ROOT.TRandom3()
		rand.SetSeed(0)
		
		wToys = ROOT.RooWorkspace("wToys", ROOT.kTRUE)
		wToys.factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
		wToys.factory("weight[1.,0.,10.]")
		vars = ROOT.RooArgSet(inv, wToys.var('weight'))
		
		selectShapes(wToys,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)
		
		
		dataEE = ROOT.RooDataSet("%sEE%s" % (typeName,region), "Dataset with invariant mass of di-electron pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
		dataMM = ROOT.RooDataSet("%sMM%s" % (typeName,region), "Dataset with invariant mass of di-muon pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
		dataSFOS = ROOT.RooDataSet("%sSFOS%s" % (typeName,region), "Dataset with invariant mass of SFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
		dataOFOS = ROOT.RooDataSet("%sOFOS%s" % (typeName,region), "Dataset with invariant mass of OFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))		
		
		
		
		getattr(wToys, 'import')(dataEE)
		getattr(wToys, 'import')(dataMM)
		getattr(wToys, 'import')(dataSFOS)
		getattr(wToys, 'import')(dataOFOS)	
		

					
		wToys.factory("SUM::ofosShape%s(nB[100,0,100000]*ofosShape1%s)"%(region,region))
		fitOFOS = wToys.pdf('ofosShape%s'%region).fitTo(wToys.data('%sOFOS%s'%(typeName,region)), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
		numOFOS = tmpOFOS.sumEntries()
		
		
		scale = theConfig.toyConfig["scale"]
		
		tmpNumOFOS = float(numOFOS*scale)
		tmpNumOFOS2 = float(numOFOS*scale)
		print "Signal OFOS %d"%tmpNumOFOS2
		print "Signal SFOS %d"%tmpNumOFOS
		
		#~ if theConfig.toyConfig["nSig"] > 0:
			
			
		
		zPrediction = getattr(theConfig.zPredictions.SF,region.lower()).val
		print zPrediction, theConfig.toyConfig["nSig"], tmpNumOFOS
		fsFrac = tmpNumOFOS/(tmpNumOFOS+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
		zFrac = zPrediction*scale/(tmpNumOFOS+zPrediction*scale+theConfig.toyConfig["nSig"]*scale)
		sigFrac = theConfig.toyConfig["nSig"]*scale/(tmpNumOFOS+zPrediction+theConfig.toyConfig["nSig"]*scale)
		
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
			if theConfig.signalShape == "Concave":
				log.logHighlighted("Dicing concave signal shape")				
			elif theConfig.signalShape == "Convex":
				log.logHighlighted("Dicing convex signal shape")			
			else:
				log.logHighlighted("Dicing triangular signal shape")	
			wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s, sigFrac*eeShape%s)"%(region,region,region))
			wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s, sigFrac*mmShape%s)"%(region,region,region))
		else:
			wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape%s, zFrac*zEEShape%s)"%(region,region))
			wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape%s, zFrac*zMMShape%s)"%(region,region))						
			

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
				
		genNumEE =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*eeFraction)
		genNumMM =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*mmFraction)
		if region == "Forward":		
			genNumEE =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale*0.33 + zPrediction*scale)*eeFraction)
			genNumMM =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale*0.33 + zPrediction*scale)*mmFraction)
		
		result = genToys2013(wToys,theConfig.toyConfig["nToys"],genNumEE,genNumMM,int(tmpNumOFOS),region)
		
	else:
		result = [{"EE":dataEE,"MM":dataMM,"SFOS":dataSFOS,"OFOS":dataOFOS}]		
		
	return result	



def selectShapes(ws,backgroundShape,signalShape,nBinsMinv):


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


	cContinuumEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "expo",basePath="dyShelves/")
	cContinuumMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "expo",basePath="dyShelves/")
	cbMeanEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "cbMean",basePath="dyShelves/")
	cbMeanMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "cbMean",basePath="dyShelves/")
	nZEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nZ",basePath="dyShelves/")
	nZMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nZ",basePath="dyShelves/")
	zFractionEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "zFraction",basePath="dyShelves/")
	zFractionMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "zFraction",basePath="dyShelves/")
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

	cContinuumEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "expo",basePath="dyShelves/")
	cContinuumMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "expo",basePath="dyShelves/")
	cbMeanEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "cbMean",basePath="dyShelves/")
	cbMeanMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "cbMean",basePath="dyShelves/")
	nZEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nZ",basePath="dyShelves/")
	nZMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nZ",basePath="dyShelves/")
	zFractionEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "zFraction",basePath="dyShelves/")
	zFractionMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "zFraction",basePath="dyShelves/")		
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

	ws.factory("BreitWigner::bwShape(inv,zmean,zwidth)")
	
	convEECentral = ROOT.RooFFTConvPdf("peakModelEECentral","zShapeEE Central (x) cbShapeEE Central",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeEECentral"))
	getattr(ws, 'import')(convEECentral)
	ws.pdf("peakModelEECentral").setBufferFraction(5.0)
	
	convEEForward = ROOT.RooFFTConvPdf("peakModelEEForward","zShapeEE Forward (x) cbShapeEE Forward",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeEEForward"))
	getattr(ws, 'import')(convEEForward)
	ws.pdf("peakModelEEForward").setBufferFraction(5.0)
	
	convMMCentral = ROOT.RooFFTConvPdf("peakModelMMCentral","zShapeMM Central (x) cbShapeMM Central",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeMMCentral"))
	getattr(ws, 'import')(convMMCentral)
	ws.pdf("peakModelMMCentral").setBufferFraction(5.0)
	
	convMMForward = ROOT.RooFFTConvPdf("peakModelMMForward","zShapeMM Forward (x) cbShapeMM Forward",ws.var("inv"),ws.pdf("bwShape"),ws.pdf("cbShapeMMForward"))
	getattr(ws, 'import')(convMMForward)
	ws.pdf("peakModelMMForward").setBufferFraction(5.0)
	

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




	ws.factory("m0[55., 30., 300.]")
	ws.var('m0').setAttribute("StoreAsymError")
	ws.factory("m0Show[45., 0., 300.]")
	#ws.factory("m0[75., 75., 75.]")
	ws.factory("const[45,20,100]")	

	if backgroundShape == 'L':
		log.logHighlighted("Using Landau")
		ws.factory("Landau::ofosShape1Central(inv,a1Central[30,0,100],b1Central[20,0,100])")
		ws.factory("Landau::ofosShape1Forward(inv,a1Forward[30,0,100],b1Forward[20,0,100])")
	elif backgroundShape == 'CH':
		log.logHighlighted("Using Chebychev")
		#~ ws.factory("Chebychev::ofosShape1Central(inv,{a1Central[0,-2,2],b1Central[0,-100,100],c1Central[0,-100,100],d1Central[0,-100,100],e1Central[0,-100,100],f1Central[0,-100,100],g1Central[0,-100,100]})")
		#~ ws.factory("Chebychev::ofosShape1Forward(inv,{a1Forward[0,-2,2],b1Forward[0,-100,100],c1Forward[0,-100,100],d1Forward[0,-100,100],e1Forward[0,-100,100],f1Forward[0,-100,100],g1Forward[0,-100,100]})")
		#~ 
		#works!
		ws.factory("Chebychev::ofosShape1Central(inv,{a1Central[0,-2,2],b1Central[0,-1,1],c1Central[0,-1,1],d1Central[0,-1,1],e1Central[0,-1,1],f1Central[0,-1,1]})")
		ws.factory("Chebychev::ofosShape1Forward(inv,{a1Forward[0,-2,2],b1Forward[0,-1,1],c1Forward[0,-1,1],d1Forward[0,-1,1],e1Forward[0,-1,1],f1Forward[0,-1,1]})")
		#~ ws.factory("Chebychev::ofosShape1Central(inv,{a1Central[0,-2,2],b1Central[0,-1,1],c1Central[0,-1,1],d1Central[0,-1,1]})")
		#~ ws.factory("Chebychev::ofosShape1Forward(inv,{a1Forward[0,-2,2],b1Forward[0,-1,1],c1Forward[0,-1,1],d1Forward[0,-1,1]})")
		
	elif backgroundShape == 'B':
		log.logHighlighted("Using BH shape")
		ws.factory("SUSYBkgBHPdf::ofosShape1Central(inv,a1Central[1.],a2Central[100,0,250],a3Central[1,0,100],a4Central[0.1,0,2])")
		ws.factory("SUSYBkgBHPdf::ofosShape1Forward(inv,a1Forward[1.],a2Forward[100,0,250],a3Forward[1,0,100],a4Forward[0.1,0,2])")
		
	elif backgroundShape == 'G':
		log.logHighlighted("Using old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.6.,0.,8.],a2Central[0.1,-1.,1.],b1Central[0.028,0.001,1.],b2Central[1.],c1Central[0.],c2Central[1.])") #trying to get rid of paramteres
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.6.,0.,8.],a2Forward[0.1,-1.,1.],b1Forward[0.028,0.001,1.],b2Forward[1.],c1Forward[0.],c2Forward[1.])") #trying to get rid of paramteres

	elif backgroundShape == 'O':
		log.logHighlighted("Using old old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.0,0.,400.],a2Central[1.],b1Central[1,0.00001,100.],b2Central[1.])")
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.0,0.0,400.],a2Forward[1.],b1Forward[1,0.00001,100.],b2Forward[1.])")	
	elif backgroundShape == 'F':
		log.logHighlighted("Using new old shape")
		ws.factory("SUSYBkgMoreParamsPdf::ofosShape1Central(inv,a1Central[1.0,0.,400.],b1Central[1,0.00001,100.],c1Central[0.,-20.,30.])")
		ws.factory("SUSYBkgMoreParamsPdf::ofosShape1Forward(inv,a1Forward[1.0,0.0,400.],b1Forward[1,0.00001,100.],c1Forward[0.,-20.,30.])")	

	elif backgroundShape == 'MA':
		log.logHighlighted("Using Marco-Andreas shape")				
		#~ ws.factory("SUSYBkgMAPdf::ofosShape1Central(inv,b1Central[-2000,-8000,8000],b2Central[120.,-800,800],b3Central[-1.,-5,5.],b4Central[0.01,0.0001,0.1], m1Central[50,30,80],m2Central[120,100,160])") #
		#~ ws.factory("SUSYBkgMAPdf::ofosShape1Forward(inv,b1Forward[-3300,-5000,5000],b2Forward[120.,-800,800],b3Forward[-1.,-5,5.],b4Forward[0.01,0.0001,0.1], m1Forward[50,30,80],m2Forward[120,100,160])") #
		ws.factory("SUSYBkgMAPdf::ofosShape1Central(inv,b1Central[-2000,-8000,8000],b2Central[120.,-800,800],b3Central[-1.,-5,5.],b4Central[0.01,-0.1,0.1], m1Central[50,20,100],m2Central[120,100,160])") #
		ws.factory("SUSYBkgMAPdf::ofosShape1Forward(inv,b1Forward[-3300,-5000,5000],b2Forward[120.,-800,800],b3Forward[-1.,-5,5.],b4Forward[0.01,-0.1,0.1], m1Forward[50,20,100],m2Forward[120,100,160])") #
		
	elif backgroundShape == 'ETH':
		log.logHighlighted("Using Marco-Andreas shape for real")
		####### final -  never touch again!
		ws.factory("TopPairProductionSpline::ofosShape1Central(inv,b1Central[-1800,-5000,5000],b2Central[120.,-400,400],b4Central[0.0025,0.0001,0.01], m1Central[50,20,80],m2Central[120,100,160])") #
		ws.factory("TopPairProductionSpline::ofosShape1Forward(inv,b1Forward[-1800,-5000,5000],b2Forward[120.,-400,400],b4Forward[0.0025,0.0001,0.01], m1Forward[50,20,80],m2Forward[120,100,160])") #
		############
		#~ ws.factory("TopPairProductionSpline::ofosShape1Central(inv,b1Central[-1800,-5000,5000],b2Central[120.,-800,800],b4Central[0.01,0.0001,0.1], m1Central[60,35,90],m2Central[120,100,160])") #
		#~ ws.factory("TopPairProductionSpline::ofosShape1Forward(inv,b1Forward[-1800,-5000,5000],b2Forward[120.,-400,400],b4Forward[0.01,0.0001,0.1], m1Forward[60,35,90],m2Forward[120,100,160])") #
		#~ ws.var("m1Central").setConstant()	
	elif backgroundShape == 'P':
		log.logHighlighted("Gaussians activated!")
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Central(inv,a1Central[30.,0.,60.],a2Central[60.,20.,105.],a3Central[100.,0.,1000.],b1Central[15,10.,80.],b2Central[20.,10.,80.],b3Central[200.,10.,3000.])") #High MET
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Forward(inv,a1Forward[30.,0.,60.],a2Forward[60.,20.,105.],a3Forward[100.,0.,1000.],b1Forward[15,10.,80.],b2Forward[20.,10.,80.],b3Forward[200.,10.,3000.])") #High MET

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
		getattr(ws, 'import')(tempDataHistCentral)
		tempDataHistForward = ROOT.RooDataHist("dataHistOFOSForward", "dataHistOFOSForward", ROOT.RooArgSet(ws.var('inv')), ws.data("dataOFOSForward"))
		getattr(ws, 'import')(tempDataHistForward)
		ws.factory("RooHistPdf::ofosShape1Central(inv, dataHistOFOSCentral)")
		ws.factory("RooHistPdf::ofosShape1Forward(inv, dataHistOFOSForward)")
	else:
		log.logHighlighted("No valid background shape selected, exiting")
		sys.exit()
		

	if signalShape == "Triangle":
		ws.factory("SUSYTPdf::sfosShapeCentral(inv,const,s,m0)")
		ws.factory("SUSYTPdf::sfosShapeCentralShow(inv,const,s,m0Show)")
		ws.factory("SUSYTPdf::eeShapeCentral(inv,const,sEECentral,m0)")
		ws.factory("SUSYTPdf::mmShapeCentral(inv,const,sMMCentral,m0)")
		ws.factory("SUSYTPdf::sfosShapeForward(inv,const,s,m0)")
		ws.factory("SUSYTPdf::sfosShapeShowForward(inv,const,s,m0Show)")
		ws.factory("SUSYTPdf::eeShapeForward(inv,const,sEEForward,m0)")
		ws.factory("SUSYTPdf::mmShapeForward(inv,const,sMMForward,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)
	elif signalShape == 'V' :
		ws.factory("Voigtian::sfosShape(inv,m0,zwidth,s)")
		ws.factory("Voigtian::eeShape(inv,m0,zwidth,sE)")
		ws.factory("Voigtian::mmShape(inv,m0,zwidth,sM)")
	elif signalShape == 'X4':
		ws.factory("SUSYX4Pdf::sfosShapeCentral(inv,const,s,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeCentralShow(inv,const,s,m0Show)")
		ws.factory("SUSYX4Pdf::eeShapeCentral(inv,const,sEECentral,m0)")
		ws.factory("SUSYX4Pdf::mmShapeCentral(inv,const,sMMCentral,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeForward(inv,const,s,m0)")
		ws.factory("SUSYX4Pdf::sfosShapeShowForward(inv,const,s,m0Show)")
		ws.factory("SUSYX4Pdf::eeShapeForward(inv,const,sEEForward,m0)")
		ws.factory("SUSYX4Pdf::mmShapeForward(inv,const,sMMForward,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)
	elif signalShape == 'XM4' in Holder.shape:
		ws.factory("SUSYXM4Pdf::sfosShapeCentral(inv,const,s,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeCentralShow(inv,const,s,m0Show)")
		ws.factory("SUSYXM4Pdf::eeShapeCentral(inv,const,sEECentral,m0)")
		ws.factory("SUSYXM4Pdf::mmShapeCentral(inv,const,sMMCentral,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeForward(inv,const,s,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeShowForward(inv,const,s,m0Show)")
		ws.factory("SUSYXM4Pdf::eeShapeForward(inv,const,sEEForward,m0)")
		ws.factory("SUSYXM4Pdf::mmShapeForward(inv,const,sMMForward,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)
	else:
		log.logHighlighted("No valid background shape selected, exiting")
		sys.exit()

def genToys2013(ws, nToys=10,genEE=0,genMM=0,genOFOS=0,region="Central"):
	theToys = []

	mcEE = ROOT.RooMCStudy(ws.pdf('backtoymodelEE'), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcEE.generate(nToys, genEE, ROOT.kTRUE)
	mcMM = ROOT.RooMCStudy(ws.pdf("backtoymodelMM"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcMM.generate(nToys, genMM, ROOT.kTRUE)
	mcOFOS = ROOT.RooMCStudy(ws.pdf("ofosShape%s"%region), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcOFOS.generate(nToys, genOFOS, ROOT.kTRUE)
	
	vars = ROOT.RooArgSet(ws.var('inv'), ws.var('weight'))

	
	for i in range(nToys):
		#toyEE = ws.pdf("mEE").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataEE').numEntries())
		#toyMM = ws.pdf("mMM").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataMM').numEntries())
		#toyOFOS = ws.pdf("backmodel").generate(ROOT.RooArgSet(ws.var('inv')),ws.data('dataOFOS').numEntries())
		toyEE = mcEE.genData(i)
		toyMM = mcMM.genData(i)
		toyOFOS = mcOFOS.genData(i)
		toySFOS = toyEE.Clone()
		toySFOS.append(toyMM.Clone())
		#~ toyData = ROOT.RooDataSet("theToy_%s" % (i), "toy_%s" % (i), Holder.vars, ROOT.RooFit.Index(ws.cat('cat')),
			#~ ROOT.RooFit.Import('OFOS', toyOFOS),
			#~ ROOT.RooFit.Import('EE', toyEE),
			#~ ROOT.RooFit.Import('MM', toyMM))
		toyDataEE = ROOT.RooDataSet("theToyEE_%s" % (i), "toyEE_%s" % (i), vars,ROOT.RooFit.Import(toyEE))
		toyDataMM = ROOT.RooDataSet("theToyMM_%s" % (i), "toyMM_%s" % (i), vars,ROOT.RooFit.Import(toyMM))
		toyDataOFOS = ROOT.RooDataSet("theToyOFOS_%s" % (i), "toyOFOS_%s" % (i), vars,ROOT.RooFit.Import(toyOFOS))
		toyDataSFOS = ROOT.RooDataSet("theToySFOS_%s" % (i), "toySFOS_%s" % (i), vars,ROOT.RooFit.Import(toySFOS))
		#toyData = mcTData.genData(i)
		#ws.var("nSig").setConstant(ROOT.kFALSE)
		#self.plotToy(ws,toyData)
		#ws.var("nSig").setConstant(ROOT.kTRUE)
		theToys.append({"EE":toyDataEE,"MM":toyDataMM,"OFOS":toyDataOFOS,"SFOS":toyDataSFOS})

	return theToys


def plotModel(w, data, fitOFOS, theConfig, pdf="model", tag="", frame=None, zPrediction= -1.0,
			  slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), cut=ROOT.RooCmdArg.none(),
			  overrideShapeNames={},region="Central"):
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
	#~ nameBGOffShellShape = "displayedBackgroundShapeOffShell"

	# get pdfs
	plotZ = ROOT.RooArgSet(w.pdf(shapeNames['Z']))
	#~ plotOffShell = ROOT.RooArgSet(w.pdf(shapeNames['offShell']))
	plotOFOS = ROOT.RooArgSet(w.pdf(shapeNames['Background']))
	plotSignal = ROOT.RooArgSet(w.pdf(shapeNames['Signal']))
	# different draw modes with and without z prediction
	zPrediction = 0.
	if (zPrediction > 0.0):
		fittedZ = w.var('nZ%s'%region).getVal()
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
		w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotOFOS), ROOT.RooFit.AddTo(nameBGZShape, 1.0, 1.0),
						  slice, projWData,
						  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack))
		if theConfig.plotErrorBands:				  
			w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotOFOS), ROOT.RooFit.AddTo(nameBGZShape, 1.0, 1.0),
							  slice, projWData,
							  ROOT.RooFit.VisualizeError(fitOFOS, 1),
							  ROOT.RooFit.FillColor(ROOT.kGreen + 2),
							  ROOT.RooFit.FillStyle(3009),
							  ROOT.RooFit.LineWidth(2))
	else:
		# default draw mode, no z prediction
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
	w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotSignal),
						  slice, projWData,
						  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kRed))
	
	return frame


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
				

		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerror", ws.var('nSig%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerrorHi", ws.var("nSig%s"%region).getAsymErrorHi(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nSerrorLo", ws.var("nSig%s"%region).getAsymErrorLo(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nZerror", ws.var('nZ%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "nBerror", ws.var('nB%s'%region).getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "rSFOFerror", ws.var('rSFOF%s'%region).getError(),basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0error", ws.var('m0').getError(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0errorHi", ws.var('m0').getAsymErrorHi(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS%s" %(theConfig.title,region), "m0errorLo", ws.var('m0').getAsymErrorLo(),basePath=theConfig.shelvePath)
				
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
				
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nSerror", ws.var('nSig%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nZerror", ws.var('nZ%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "nBerror", ws.var('nB%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "rSFOFerror", ws.var('rSFOF%s'%region).getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS%s" %(title,region), "m0error", ws.var('m0').getError(), index = x)
											
								

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
		sl.AddEntry(bLeg, 'e#mu-shape', "l")
		#~ sl.AddEntry(uLeg, 'Uncertainty', "f")
		#sl.AddEntry(lmLeg, 'LM1 x 0.2', "l")
		
		
	nLegendEntries = 2
	bl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
	bl.SetTextAlign(22)
	
	if (useMC):
		bl.AddEntry(dLeg, 'Simulation', "pl")
	else:
		bl.AddEntry(dLeg, 'Data', "pl")
	bl.AddEntry(fitLeg, 'e#mu-shape', "l")
	#~ bl.AddEntry(uLeg, 'Uncertainty', "f")		
			
	return [sl,bl]

def plotFitResults(ws,theConfig,frameSFOS,frameOFOS,data_obs,fitOFOS,region="Central",H0=False):

	sizeCanvas = 800
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
	if theConfig.plotErrorBands:
		uLeg = dLeg.Clone()
		uLeg.SetLineColor(ROOT.kGreen + 2)
		uLeg.SetFillColor(ROOT.kGreen + 2)
		uLeg.SetFillStyle(3009)
	lmLeg = dLeg.Clone()
	lmLeg.SetLineColor(ROOT.kViolet)
	lmLeg.SetLineStyle(ROOT.kDotted)
	if theConfig.plotErrorBands:
		
		nLegendEntries = 6
	else:	
		nLegendEntries = 5

	sl = tools.myLegend(0.59, 0.92 - 0.06 * nLegendEntries, 0.92, 0.93, borderSize=0)
	sl.SetTextAlign(22)
	if (useMC):
		sl.AddEntry(dLeg, 'Simulation', "pl")
	else:
		sl.AddEntry(dLeg, 'Data', "pe")
	sl.AddEntry(fitLeg, 'Fit', "l")

	if (getattr(theConfig.zPredictions.SF,region.lower()).val > 0.0):
		sl.AddEntry(sLeg, 'signal', "l")
		zLeg.SetLineColor(ROOT.kViolet)
		sl.AddEntry(zLeg, 'Z background', "l")
		sl.AddEntry(bLeg, 'FS background', "l")
		#~ sl.AddEntry(oLeg, 'Off-Shell Drell-Yan', "l")
		if theConfig.plotErrorBands:
			sl.AddEntry(uLeg, 'OF uncertainty', "f")
	else:
		sl.AddEntry(sLeg, 'Signal', "l")
		sl.AddEntry(zLeg, 'DY', "l")
		#sl.AddEntry(zLeg, 'Z^{0}/#gamma', "l")
		sl.AddEntry(bLeg, 'e#mu-shape', "l")
		if theConfig.plotErrorBands:
			sl.AddEntry(uLeg, 'Uncertainty', "f")
		#sl.AddEntry(lmLeg, 'LM1 x 0.2', "l")
		
		
	nLegendEntries = 2
	if theConfig.plotErrorBands:
		nLegendEntries =3
	bl = tools.myLegend(0.69, 0.92 - 0.05 * nLegendEntries, 0.92, 0.93, borderSize=0)
	bl.SetTextAlign(22)
	
	if (useMC):
		bl.AddEntry(dLeg, 'Simulation', "pl")
	else:
		bl.AddEntry(dLeg, 'Data', "pl")
	bl.AddEntry(fitLeg, 'e#mu-shape', "l")
	if theConfig.plotErrorBands:
		bl.AddEntry(uLeg, 'Uncertainty', "f")		


	nSignal = ws.var('nSig%s'%region).getVal()
	nSignalError = ws.var('nSig%s'%region).getError()
	annotEdge = 'fitted N_{S} = %.1f #pm %.1f' % (nSignal, nSignalError)

	if (theConfig.runMinos):
		# why is asymmetric error always zero?
		# --> Have to run MINOS during fit to get asym errors
		# --> MINOS does not take boundaries into account
		annotEdge = 'N_{S} = %.2f  + %.2f %.2f (%.2f)' % (ws.var('nSig%s'%region).getVal(), ws.var('nSig%s'%region).getAsymErrorHi(), ws.var('nSig%s'%region).getAsymErrorLo(), ws.var('nSig%s'%region).getError())

	#annotZ = 'n_{Z} = %.1f  + %.1f %.1f (%.1f)' % (ws.var('nZ').getVal(), ws.var('nZ').getAsymErrorHi(), ws.var('nZ').getAsymErrorLo(), ws.var('nZ').getError())
	ws.var("inv").setRange("zPeak",81,101)
	ws.var("inv").setRange("fullRange",20,300)
	ws.var("inv").setRange("lowMass",20,70)
	argSet = ROOT.RooArgSet(ws.var("inv"))
	
	fittedZInt = ws.pdf("zShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZ = fittedZInt.getVal()
	
	fittedZIntEE = ws.pdf("zEEShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZEE = fittedZIntEE.getVal()
	
	fittedZIntMM = ws.pdf("zMMShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZMM = fittedZIntMM.getVal()
	

	fittedFullZInt = ws.pdf("zShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("fullRange"))
	fittedFullZ = fittedFullZInt.getVal()
	
	fittedLowMassZInt = ws.pdf("zShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("lowMass"))
	fittedLowMassZ = fittedLowMassZInt.getVal()
	
	
	print fittedLowMassZ, fittedZ, fittedFullZ
	
	correctedZ = fittedZ/fittedFullZ*ws.var("nZ%s"%region).getVal()
	correctedLowMassZ = fittedLowMassZ/fittedFullZ*ws.var("nZ%s"%region).getVal()
	
	fittedZErr = max(ws.var("nZ%s"%region).getError(),max(abs(ws.var("nZ%s"%region).getAsymErrorLo()),abs(ws.var("nZ%s"%region).getAsymErrorHi())))*(fittedZ/fittedFullZ)
	fittedLowMassZErr = max(ws.var("nZ%s"%region).getError(),max(abs(ws.var("nZ%s"%region).getAsymErrorLo()),abs(ws.var("nZ%s"%region).getAsymErrorHi())))*(fittedLowMassZ/fittedFullZ)
	
	fittedBackgroundLowMassInt = ws.pdf("ofosShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("lowMass"))
	bgLowMass = fittedBackgroundLowMassInt.getVal()
	
	fittedBackgroundFullRangeInt = ws.pdf("ofosShape%s"%region).createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("FullRange"))
	bgLowMass = ws.var("nB%s"%region).getVal() * (fittedBackgroundLowMassInt.getVal() / fittedBackgroundFullRangeInt.getVal() ) * ws.var("rSFOF%s"%region).getVal()
	bgLowMassErr = max(ws.var("nB%s"%region).getError(),max(abs(ws.var("nB%s"%region).getAsymErrorLo()),abs(ws.var("nB%s"%region).getAsymErrorHi()))) * (fittedBackgroundLowMassInt.getVal() / fittedBackgroundFullRangeInt.getVal() ) * ws.var("rSFOF%s"%region).getVal()
	
	annotZ = 'N_{Z} = %.1f #pm %.1f' % (correctedZ, fittedZErr)
	annotLowMassZ = "N_{Z} = %.1f #pm %.1f" % (correctedLowMassZ, fittedLowMassZErr)	

		
	varBack = ws.var('nB%s'%region).getVal()
	varBackErr = ws.var('nB%s'%region).getError()

	annotBG = 'N_{B}^{OF} = %.1f #pm %.1f (%.1f #pm %.1f)' % (bgLowMass, bgLowMassErr,varBack, varBackErr)
	annotNSStar = ""
	annotZpred = ""
	if (getattr(theConfig.zPredictions.SF,region.lower()).val > 0.0):
		annotEdge = 'N_{Signal} = %.1f #pm %.1f' % (nSignal, nSignalError)
		if theConfig.runMinos:
			nSignalError = max(ws.var('nSig%s'%region).getError(),max(abs(ws.var('nSig%s'%region).getAsymErrorHi()),abs(ws.var('nSig%s'%region).getAsymErrorLo())))
			annotEdge = 'fitted N_{S}^{edge} = %.1f #pm %.1f' % (nSignal, nSignalError)
			
			#~ annotEdge = 'N_{S} = %.2f  + %.2f %.2f (%.2f)' % (ws.var('nSig').getVal(), ws.var('nSig').getAsymErrorHi(), ws.var('nSig').getAsymErrorLo(), ws.var('nSig').getError())

		nSStar = 0
		nSStarError = 0
		annotNSStar = 'corrected N_{S}^{edge} = %.1f #pm %.1f' % (nSStar,nSStarError)
		nsZ = fittedZ - getattr(theConfig.zPredictions.SF,region.lower()).val 
		nsZError = math.sqrt(fittedZErr**2 + getattr(theConfig.zPredictions.SF,region.lower()).err ** 2)
		#~ annotZ = "N_{S}^{Z} = %.1f #pm %.1f" % (nsZ, nsZError)
		annotZpred = "N_{pred}^{Z} = %.1f #pm %.1f" % (getattr(theConfig.zPredictions.SF,region.lower()).val , getattr(theConfig.zPredictions.SF,region.lower()).err)


	note2 = "m^{edge}_{ll} = %.1f^{+%.1f}_{%.1f} GeV"
	note2 = note2%(ws.var("m0").getVal(),ws.var("m0").getAsymErrorHi(),ws.var("m0").getAsymErrorLo())
	

	sfosName = '%s/fit2012_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	ofosName = '%s/fit2012OFOS_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	eeName = '%s/fit2012EE_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	mmName = '%s/fit2012MM_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
	if H0:
		sfosName = '%s/fit2012_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		ofosName = '%s/fit2012OFOS_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		eeName = '%s/fit2012EE_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)
		mmName = '%s/fit2012MM_H0_%s_%s_%s.pdf' % (theConfig.figPath, shape, title,region)	

	# determine y axis range
	#~ yMaximum = 1.2 * max(frameOFOS.GetMaximum(), frameSFOS.GetMaximum())
	yMaximum = 220
	if (theConfig.plotYMax > 0.0):
		yMaximum = theConfig.plotYMax


	# make OFOS plot
	#---------------
	print "before OFOS plot"
	projWData = ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs)
	#~ cOFOS = ROOT.TCanvas("OFOS distribution", "OFOS distribution", sizeCanvas, int(sizeCanvas * 1.25))
	#~ cOFOS.cd()
	#~ pads = formatAndDrawFrame(frameOFOS, title="OFOS", pdf=ws.pdf("ofosShape"), yMax=yMaximum,residualMode = residualMode)
	#if not Holder.nToys > 0:
	slice = ROOT.RooFit.Slice(ws.cat("cat"), "OFOS%s"%region)
	
	frameOFOS = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of e#mu lepton pairs'))
	frameOFOS = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sOFOS" % title, frame=frameOFOS, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::OFOS%s"%region),region=region)
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
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['Grey'], textSize=0.03, align=31)
	bl.Draw()
	cOFOS.Print(ofosName)	
	for pad in pads:
		pad.Close()


	# make ee plot
	#------------
	
	shapeNames = {}

	shapeNames['Z'] = "zEEShape%s"%region
	shapeNames['offShell'] = "offShell%s"%region
	shapeNames['Signal'] = "eeShape"

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "EE%s"%region)

	frameEE = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
	frameEE = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sEE" % title, frame=frameEE, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::EE%s"%region),
						overrideShapeNames=shapeNames,region=region)

	cEE = ROOT.TCanvas("EE distribtution", "EE distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cEE.cd()
	pads = formatAndDrawFrame(frameEE, theConfig, title="EE%s"%region, pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "EE%s"%region),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode =residualMode)

	annotationsTitle = [
					   (0.92, 0.57, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.53, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['Grey'], textSize=0.03, align=31)

	frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
	frameEE.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cEE.Update()
	cEE.Print(eeName)
	for pad in pads:
		pad.Close()


	# make mm plot
	#------------
	shapeNames['Z'] = "zMMShape%s"%region
	shapeNames['Signal'] = "mmShape"
	shapeNames['offShell'] = "offShell%s"%region

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "MM%s"%region)

	frameMM = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of mumu lepton pairs'))
	frameMM = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sMM" % title, frame=frameMM, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::MM%s"%region),
						overrideShapeNames=shapeNames)

	cMM = ROOT.TCanvas("MM distribtution", "MM distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cMM.cd()
	pads = formatAndDrawFrame(frameMM, theConfig, title="MM%s"%region, pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "MM%s"%region),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode=residualMode)

	annotationsTitle = [
					   (0.92, 0.51, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.47, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['Grey'], textSize=0.03, align=31)

	frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
	frameMM.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cMM.Update()
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

	annotationsTitle = [
					   (0.92, 0.53, "%s" % (region)),
					   (0.92, 0.47, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
	annotRangeLow = "Low Mass (20 < m_{ll} < 70):"
	annotRangeZ = "Z Peak (81 < m_{ll} < 101):"
	annotationsFitHeader = [
					   (0.92, 0.55, annotRangeLow),
					   ]
	annotationsFit = [
					   (0.92, 0.41, annotEdge),
					   #~ (0.92, 0.47, annotLowMassZ),
					   #~ (0.92, 0.47, annotBG),
					   ]
	annotationsFitZHeader = [
					   (0.92, 0.37, annotRangeZ),
					   ]
	annotationsFitZ = [
					   (0.92, 0.32, annotZ),
					   ]
	annotationsFitZPred = [
					   (0.92, 0.27, annotZpred),
					   ]
	#~ annotationsFit = [
#~ 
					   #~ ]
	#~ annotationsFitZPred = [
#~ 
					   #~ ]
	if (showText):
		#~ tools.makeAnnotations(annotationsFitHeader, color=tools.myColors['Black'], textSize=0.03, align=31)
		tools.makeAnnotations(annotationsFit, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
		#~ tools.makeAnnotations(annotationsFitZHeader, color=tools.myColors['Black'], textSize=0.03, align=31)
		#~ tools.makeAnnotations(annotationsFitZ, color=tools.myColors['AnnBlue'], textSize=0.03, align=31)
		#~ tools.makeAnnotations(annotationsFitZPred, color=tools.myColors['Grey'], textSize=0.03, align=31)
	#~ pads[0].SetLogy()
	sl.Draw()
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
	parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="SignalInclusive",
						  help="selection which to apply.")
	parser.add_argument("-r", "--runRange", dest="runRange", action="store", default="Full2012",
						  help="name of run range.")
	parser.add_argument("-b", "--backgroundShape", dest="backgroundShape", action="store", default="ETH",
						  help="background shape, default ETH")
	parser.add_argument("-e", "--edgeShape", dest="edgeShape", action="store", default="Triangle",
						  help="edge shape, default Triangle")
	parser.add_argument("-c", "--configuration", dest="config", action="store", default="Combined",
						  help="dataset configuration, default Combined")
	parser.add_argument("-t", "--toys", dest="toys", action="store", default=0,
						  help="generate and fit x toys")
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
	runName =args.runRange
	dataSetConfiguration = args.config
	produceScan = args.likelihoodScan
	if not args.config == "Inclusive" and not args.config == "Central" and not args.config == "Forward" and not args.config == "Combined":
		log.logError("Dataset %s not not known, exiting" % dataSet)
		sys.exit()
	useExistingDataset = args.useExisting
		
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region,backgroundShape,signalShape,runName,args.config,args.mc,args.toys)
	
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
	ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
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
		if (theConfig.useMC):
			log.logHighlighted("Using MC instead of data.")
			datasets = theConfig.mcdatasets # ["TTJets", "ZJets", "DibosonMadgraph", "SingleTop"]
			(treeOFOSCentral, treeEECentral, treeMMCentral) = tools.getTrees(theConfig, datasets,central=True)
			(treeOFOSForward, treeEEForward, treeMMForward) = tools.getTrees(theConfig, datasets,central=False)
		else:
			treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)
			treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)
			treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)

			# convert trees
			treeOFOSCentral = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
			treeEECentral = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
			treeMMCentral = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
			
			treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)
			treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)
			treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)

			# convert trees
			treeOFOSForward = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
			treeEEForward = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
			treeMMForward = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
		if (theConfig.addDataset != None):
			treeAddOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeAddEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeAddMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
		

			xsection = 0.0
			nTotal = 1.0
			scale = xsection * theConfig.luminosity / nTotal


			# dynamic scaling
			jobs = dataInterface.InfotheConfig.theDataSamples[theConfig.dataVersion][theConfig.addDataset]
			if (len(jobs) > 1):
				log.logError("Scaling of added MC samples not implemented. MC yield is wrong!")
			for job in jobs:
				dynNTotal = theDataInterface.getEventCount(job, theConfig.flag, theConfig.task)
				dynXsection = theDataInterface.getCrossSection(job)
				dynScale = dynXsection * theConfig.luminosity / dynNTotal
				scale = dynScale


			log.logHighlighted("Scaling added dataset (%s) with %f (dynamic)" % (theConfig.addDataset, scale))

			# convert trees
			treeAddOFOS = dataInterface.dataInterface.convertDileptonTree(treeAddOFOSraw, weight=scale)
			treeAddEE = dataInterface.dataInterface.convertDileptonTree(treeAddEEraw, weight=scale)
			treeAddMM = dataInterface.dataInterface.convertDileptonTree(treeAddMMraw, weight=scale)



		treesCentral = {"EE":treeEECentral,"MM":treeMMCentral,"OFOS":treeOFOSCentral}
		addTreesCentral = {}
		treesForward = {"EE":treeEEForward,"MM":treeMMForward,"OFOS":treeOFOSForward}
		addTreesForward = {}
		if theConfig.addDataset != None:
			addTreesCentral = {"EE":treeAddEECentral,"MM":treeAddMMCentral,"OFOS":treeAddOFOSCentral}
			addTreesForward = {"EE":treeAddEEForward,"MM":treeAddMMForward,"OFOS":treeAddOFOSForward}

		weight = ROOT.RooRealVar("weight","weight",1.,-100.,10.)
		inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		
		
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
	
	
	if theConfig.toyConfig["nToys"] > 0:
		theConfig.title = "%s_Scale%sMo%sSignalN%s"%(theConfig.title, theConfig.toyConfig["scale"], theConfig.toyConfig["m0"], theConfig.toyConfig["nSig"])

	if theConfig.fixEdge:
		theConfig.title = theConfig.title+"_FixedEdge_%.1f"%theConfig.edgePosition
	if theConfig.useMC:
		theConfig.title = theConfig.title+"_MC"
 	if theConfig.isSignal:
		theConfig.title = theConfig.title+"_SignalInjected"   	
					
	titleSave = theConfig.title	
	

		
				
	for index, dataSet in enumerate(dataSetsCentral):
		
		if theConfig.toyConfig["nToys"] > 0:
			x = "%x"%(random.random()*1e9)
			theConfig.figPath = "figToys/"
			theConfig.title = titleSave 
			if theConfig.toyConfig["systShift"] == "Up" or theConfig.toyConfig["systShift"] == "Down":
				theConfig.title = theConfig.title + "_" + theConfig.toyConfig["systShift"]
			if theConfig.signalShape != "T":
				theConfig.title = theConfig.title + "_" + signalShape
			if theConfig.allowNegSignal:
				theConfig.title = theConfig.title + "_" + "allowNegSignal"	
			theConfig.title = theConfig.title + "_" + x
				
		else:
			x = None		
		
		if not useExistingDataset:
		
			w = ROOT.RooWorkspace("w", ROOT.kTRUE)
			w.factory("inv[%s,%s,%s]" % ((theConfig.maxInv - theConfig.minInv) / 2, theConfig.minInv, theConfig.maxInv))
			w.factory("weight[1.,0.,10.]")
			vars = ROOT.RooArgSet(inv, w.var('weight'))
			
			
			dataEECentral = dataSetsCentral[index]["EE"].Clone("dataEECentral")
			dataMMCentral = dataSetsCentral[index]["MM"].Clone("dataMMCentral")
			dataOFOSCentral = dataSetsCentral[index]["OFOS"].Clone("dataOFOSCentral")
			dataSFOSCentral = dataSetsCentral[index]["SFOS"].Clone("dataSFOSCentral")
			
			
			dataEEForward = dataSetsForward[index]["EE"].Clone("dataEEForward")
			dataMMForward = dataSetsForward[index]["MM"].Clone("dataMMForward")
			dataOFOSForward = dataSetsForward[index]["OFOS"].Clone("dataOFOSForward")
			dataSFOSForward = dataSetsForward[index]["SFOS"].Clone("dataSFOSForward")

			getattr(w, 'import')(dataEECentral)
			getattr(w, 'import')(dataMMCentral)
			getattr(w, 'import')(dataOFOSCentral)
			getattr(w, 'import')(dataSFOSCentral)		
			
			getattr(w, 'import')(dataEEForward)
			getattr(w, 'import')(dataMMForward)
			getattr(w, 'import')(dataOFOSForward)
			getattr(w, 'import')(dataSFOSForward)
		
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
			w =  f.Get("w")			
			
		vars = ROOT.RooArgSet(w.var('inv'), w.var('weight'))
		selectShapes(w,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)


		

	
		# deduce proper values for yield parameters from datasets and create yield parameters
		
		predictedSignalYieldCentral = w.data("dataSFOSCentral").sumEntries() - 0.8*w.data("dataSFOSCentral").sumEntries()
		predictedSignalYieldForward = w.data("dataSFOSForward").sumEntries() - 0.8*w.data("dataSFOSForward").sumEntries()
		if theConfig.allowNegSignal:
			w.factory("nSigCentral[%f,%f,%f]" % (0.,-2*predictedSignalYieldCentral, 2*predictedSignalYieldCentral))
			w.factory("nSigForward[%f,%f,%f]" % (0.,-4*predictedSignalYieldForward, 4*predictedSignalYieldForward))
		else:
			w.factory("nSigCentral[%f,%f,%f]" % (0.,0, 2*predictedSignalYieldCentral))
			w.factory("nSigForward[%f,%f,%f]" % (0.,0, 2*predictedSignalYieldForward))		
		w.var('nSigCentral').setAttribute("StoreAsymError")
		w.var('nSigForward').setAttribute("StoreAsymError")


		maxZCentral = w.data("dataSFOSCentral").sumEntries("abs(inv-91.2) < 20")	
		maxZForward = w.data("dataSFOSForward").sumEntries("abs(inv-91.2) < 20")
		
		w.factory("nZCentral[%f,0.,%f]" % (theConfig.zPredictions.SF.central.val,maxZCentral))
		w.factory("nZForward[%f,0.,%f]" % (theConfig.zPredictions.SF.forward.val,maxZForward))
		w.var('nZCentral').setAttribute("StoreAsymError")
		w.var('nZForward').setAttribute("StoreAsymError")
		
		nBMinCentral = w.data("dataOFOSCentral").sumEntries()*0
		nBMaxCentral= w.data("dataSFOSCentral").sumEntries()*2
		nBStartCentral = w.data("dataOFOSCentral").sumEntries()*0.7
		nBMinForward = w.data("dataOFOSForward").sumEntries()*0
		nBMaxForward= w.data("dataSFOSForward").sumEntries()*2
		nBStartForward = w.data("dataOFOSForward").sumEntries()*0.7		
		
		w.factory("nBCentral[%f,%f,%f]" % (nBStartCentral,nBMinCentral,nBMaxCentral))	
		w.factory("nBForward[%f,%f,%f]" % (nBStartForward,nBMinForward,nBMaxForward))	
		w.var('nBCentral').setAttribute("StoreAsymError")
		w.var('nBForward').setAttribute("StoreAsymError")

		#create background only shapes
			
		w.factory("SUM::ofosShapeCentral(nBCentral*ofosShape1Central)")
		w.factory("SUM::ofosShapeForward(nBForward*ofosShape1Forward)")
		
		# fit background only shapes to OFOS dataset
		w.Print()
		fitOFOSCentral = w.pdf('ofosShapeCentral').fitTo(w.data("dataOFOSCentral"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
		
		fitOFOSCentral.Print()
		
		fitOFOSForward = w.pdf('ofosShapeForward').fitTo(w.data("dataOFOSForward"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
		
		fitOFOSForward.Print()
		
		
		log.logWarning("Central OFOS Fit Convergence Quality: %d"%fitOFOSCentral.covQual())
		log.logWarning("Forward OFOS Fit Convergence Quality: %d"%fitOFOSForward.covQual())
		
		
		parametersToSave["minNllOFOSCentral"] = fitOFOSCentral.minNll()
		parametersToSave["minNllOFOSForward"] = fitOFOSCentral.minNll()

		parametersToSave["nParOFOSCentral"] = fitOFOSCentral.floatParsFinal().getSize()
		parametersToSave["nParOFOSForward"] = fitOFOSCentral.floatParsFinal().getSize()


		frameOFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		frameOFOSCentral.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		frameOFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
		frameOFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		frameOFOSForward.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		frameOFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

		parametersToSave["chi2OFOSCentral"] = frameOFOSCentral.chiSquare(parametersToSave["nParOFOSCentral"])
		log.logDebug("Chi2 OFOS: %f" % parametersToSave["chi2OFOSCentral"])
		parametersToSave["chi2OFOSForward"] = frameOFOSForward.chiSquare(parametersToSave["nParOFOSForward"])
		log.logDebug("Chi2 OFOS: %f" % parametersToSave["chi2OFOSForward"])

		
		ROOT.RooAbsData.plotOn(w.data("dataOFOSCentral"), frameOFOSCentral)
		w.pdf('ofosShapeCentral').plotOn(frameOFOSCentral)
		ROOT.RooAbsData.plotOn(w.data("dataOFOSForward"), frameOFOSForward)
		w.pdf('ofosShapeForward').plotOn(frameOFOSForward)



		w.pdf('ofosShapeCentral').plotOn(frameOFOSCentral,
								  #~ ROOT.RooFit.VisualizeError(fitOFOS, 1),
								  #~ ROOT.RooFit.FillColor(ROOT.kGreen + 2),
								  #~ ROOT.RooFit.FillStyle(3009),
								  ROOT.RooFit.LineWidth(2))
		w.pdf('ofosShapeCentral').plotOn(frameOFOSCentral)
		ROOT.RooAbsData.plotOn(w.data("dataOFOSCentral"), frameOFOSCentral)

		w.pdf('ofosShapeForward').plotOn(frameOFOSForward,
								  #~ ROOT.RooFit.VisualizeError(fitOFOS, 1),
								  #~ ROOT.RooFit.FillColor(ROOT.kGreen + 2),
								  #~ ROOT.RooFit.FillStyle(3009),
								  ROOT.RooFit.LineWidth(2))
		w.pdf('ofosShapeForward').plotOn(frameOFOSForward)
		ROOT.RooAbsData.plotOn(w.data("dataOFOSForward"), frameOFOSForward)


		# Fit SFOS distribution

		
		w.factory("rSFOFCentral[%f,%f,%f]" % (theConfig.rSFOF.central.val, theConfig.rSFOF.central.val - 4*theConfig.rSFOF.central.err, theConfig.rSFOF.central.val + 4*theConfig.rSFOF.central.err))
		w.factory("rSFOFMeasuredCentral[%f]" % (theConfig.rSFOF.central.val))
		w.factory("rSFOFMeasuredCentralErr[%f]" % (theConfig.rSFOF.central.err))
		w.factory("rSFOFForward[%f,%f,%f]" % (theConfig.rSFOF.forward.val, theConfig.rSFOF.forward.val - 4*theConfig.rSFOF.forward.err, theConfig.rSFOF.forward.val + 4*theConfig.rSFOF.forward.err))
		w.factory("rSFOFMeasuredForward[%f]" % (theConfig.rSFOF.forward.val))
		w.factory("rSFOFMeasuredForwardErr[%f]" % (theConfig.rSFOF.forward.err))
		
		w.factory("feeCentral[0.5,0.,1.]")
		w.factory("feeForward[0.5,0.,1.]")
		w.factory("Gaussian::constraintRSFOFForward(rSFOFForward,rSFOFMeasuredForward,rSFOFMeasuredForwardErr)")
		w.factory("Gaussian::constraintRSFOFCentral(rSFOFCentral,rSFOFMeasuredCentral,rSFOFMeasuredCentralErr)")

		nSigEECentral = ROOT.RooFormulaVar('nSigEECentral', '@0*@1', ROOT.RooArgList(w.var('feeCentral'), w.var('nSigCentral')))
		getattr(w, 'import')(nSigEECentral)
		nSigMMCentral = ROOT.RooFormulaVar('nSigMMCentral', '(1-@0)*@1', ROOT.RooArgList(w.var('feeCentral'), w.var('nSigCentral')))
		getattr(w, 'import')(nSigMMCentral)			
		nZEECentral = ROOT.RooFormulaVar('nZEECentral', '@0*@1', ROOT.RooArgList(w.var('feeCentral'), w.var('nZCentral')))
		getattr(w, 'import')(nZEECentral)
		nZMMCentral = ROOT.RooFormulaVar('nZMMCentral', '(1-@0)*@1', ROOT.RooArgList(w.var('feeCentral'), w.var('nZCentral')))
		getattr(w, 'import')(nZMMCentral)
		nBEECentral = ROOT.RooFormulaVar('nBEECentral', '@0*@1*@2', ROOT.RooArgList(w.var('feeCentral'),w.var('rSFOFCentral'), w.var('nBCentral')))
		getattr(w, 'import')(nBEECentral)
		nBMMCentral = ROOT.RooFormulaVar('nBMMCentral', '(1-@0)*@1*@2', ROOT.RooArgList(w.var('feeCentral'),w.var('rSFOFCentral'), w.var('nBCentral')))
		getattr(w, 'import')(nBMMCentral)								
		nSigEEForward = ROOT.RooFormulaVar('nSigEEForward', '@0*@1', ROOT.RooArgList(w.var('feeForward'), w.var('nSigForward')))
		getattr(w, 'import')(nSigEEForward)
		nSigMMForward = ROOT.RooFormulaVar('nSigMMForward', '(1-@0)*@1', ROOT.RooArgList(w.var('feeForward'), w.var('nSigForward')))
		getattr(w, 'import')(nSigMMForward)			
		nZEEForward = ROOT.RooFormulaVar('nZEEForward', '@0*@1', ROOT.RooArgList(w.var('feeForward'), w.var('nZForward')))
		getattr(w, 'import')(nZEEForward)
		nZMMForward = ROOT.RooFormulaVar('nZMMForward', '(1-@0)*@1', ROOT.RooArgList(w.var('feeForward'), w.var('nZForward')))
		getattr(w, 'import')(nZMMForward)
		nBEEForward = ROOT.RooFormulaVar('nBEEForward', '@0*@1*@2', ROOT.RooArgList(w.var('feeForward'),w.var('rSFOFForward'), w.var('nBForward')))
		getattr(w, 'import')(nBEEForward)
		nBMMForward = ROOT.RooFormulaVar('nBMMForward', '(1-@0)*@1*@2', ROOT.RooArgList(w.var('feeForward'),w.var('rSFOFForward'), w.var('nBForward')))
		getattr(w, 'import')(nBMMForward)							
		constraints = ROOT.RooArgSet(w.pdf("constraintRSFOFCentral"),w.pdf("constraintRSFOFForward"))			
		
		w.factory("SUM::zShapeCentral(nZEECentral*zEEShapeCentral,nZMMCentral*zMMShapeCentral)")	
		w.factory("SUM::zShapeForward(nZEEForward*zEEShapeForward,nZMMForward*zMMShapeForward)")	
		w.factory("Voigtian::zShapeSeparately(inv,zmean,zwidth,s)")		


		w.factory("SUM::modelCentral(nSigCentral*sfosShapeCentral, nBCentral*ofosShapeCentral, nZCentral*zShapeCentral)")
		w.factory("SUM::mEECentral(nSigEECentral*eeShapeCentral, nBEECentral*ofosShapeCentral, nZEECentral*zEEShapeCentral)")
		w.factory("SUM::mMMCentral(nSigMMCentral*mmShapeCentral, nBMMCentral*ofosShapeCentral, nZMMCentral*zMMShapeCentral)")
		
		
		w.factory("PROD::constraintMEECentral(mEECentral, constraintRSFOFCentral)")
		w.factory("PROD::constraintMMMCentral(mMMCentral, constraintRSFOFCentral)")
		
		w.factory("SUM::modelBgOnlyCentral( nBCentral*ofosShapeCentral, nZCentral*zShapeCentral)")
		w.factory("SUM::mEEBgOnlyCentral( nBEECentral*ofosShapeCentral, nZEECentral*zEEShapeCentral)")
		w.factory("SUM::mMMBgOnlyCentral( nBMMCentral*ofosShapeCentral, nZMMCentral*zMMShapeCentral)")
		
		
		w.factory("PROD::constraintMEEBgOnlyCentral( mEEBgOnlyCentral, constraintRSFOFCentral)")
		w.factory("PROD::constraintMMMBgOnlyCentral( mMMBgOnlyCentral, constraintRSFOFCentral)")
		
		w.factory("SUM::modelForward(nSigForward*sfosShapeForward, nBForward*ofosShapeForward, nZForward*zShapeForward)")
		w.factory("SUM::mEEForward(nSigEEForward*eeShapeForward, nBEEForward*ofosShapeForward, nZEEForward*zEEShapeForward)")
		w.factory("SUM::mMMForward(nSigMMForward*mmShapeForward, nBMMForward*ofosShapeForward, nZMMForward*zMMShapeForward)")
		
		
		w.factory("PROD::constraintMEEForward(mEEForward,constraintRSFOFForward)")
		w.factory("PROD::constraintMMMForward(mMMForward,constraintRSFOFForward)")
		
		
		w.factory("SUM::modelBgOnlyForward( nBForward*ofosShapeForward, nZForward*zShapeForward)")
		w.factory("SUM::mEEBgOnlyForward( nBEEForward*ofosShapeForward, nZEEForward*zEEShapeForward)")
		w.factory("SUM::mMMBgOnlyForward( nBMMForward*ofosShapeForward, nZMMForward*zMMShapeForward)")
		
		
		
		w.factory("PROD::constraintMEEBgOnlyForward( mEEBgOnlyForward,constraintRSFOFForward)")
		w.factory("PROD::constraintMMMBgOnlyForward( mMMBgOnlyForward,constraintRSFOFForward)")
			
		if dataSetConfiguration == "Combined":
			w.factory("SIMUL::combModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=mEEBgOnlyCentral, MMCentral=mMMBgOnlyCentral, OFOSCentral=ofosShapeCentral, EEForward=mEEBgOnlyForward, MMForward=mMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			# real model
			
			w.factory("SIMUL::combModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=mEECentral, MMCentral=mMMCentral, OFOSCentral=ofosShapeCentral, EEForward=mEEForward, MMForward=mMMForward, OFOSForward=ofosShapeForward)")
			
			w.factory("SIMUL::constraintCombModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=constraintMEEBgOnlyCentral, MMCentral=constraintMMMBgOnlyCentral, OFOSCentral=ofosShapeCentral, EEForward=constraintMEEBgOnlyForward, MMForward=constraintMMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			# real model
			
			w.factory("SIMUL::constraintCombModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2,EEForward=3,MMForward=4,OFOSForward=5], EECentral=mEECentral, MMCentral=constraintMMMCentral, OFOSCentral=ofosShapeCentral, EEForward=mEEForward, MMForward=constraintMMMForward, OFOSForward=ofosShapeForward)")		
					
				
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w.cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSCentral', w.data("dataOFOSCentral")),
									   ROOT.RooFit.Import('EECentral', w.data("dataEECentral")),
									   ROOT.RooFit.Import('MMCentral', w.data("dataMMCentral")),
									   ROOT.RooFit.Import('OFOSForward', w.data("dataOFOSForward")),
									   ROOT.RooFit.Import('EEForward', w.data("dataEEForward")),
									   ROOT.RooFit.Import('MMForward', w.data("dataMMForward")))
			getattr(w, 'import')(data_obs)
		elif dataSetConfiguration == "Central":			
			w.factory("SIMUL::combModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=mEEBgOnlyCentral, MMCentral=mMMBgOnlyCentral, OFOSCentral=ofosShapeCentral)")
			# real model
			
			w.factory("SIMUL::combModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=mEECentral, MMCentral=mMMCentral, OFOSCentral=ofosShapeCentral)")
			
			w.factory("SIMUL::constraintCombModelBgOnly(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=constraintMEEBgOnlyCentral, MMCentral=constraintMMMBgOnlyCentral, OFOSCentral=ofosShapeCentral)")
			# real model
			
			w.factory("SIMUL::constraintCombModel(cat[EECentral=0,MMCentral=1,OFOSCentral=2], EECentral=mEECentral, MMCentral=constraintMMMCentral, OFOSCentral=ofosShapeCentral)")		
					
				
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w.cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSCentral', w.data("dataOFOSCentral")),
									   ROOT.RooFit.Import('EECentral', w.data("dataEECentral")),
									   ROOT.RooFit.Import('MMCentral', w.data("dataMMCentral")))
			getattr(w, 'import')(data_obs)
			w.var("rSFOFForward").setConstant()

		elif dataSetConfiguration == "Forward":
			w.factory("SIMUL::combModelBgOnly(cat[EEForward=0,MMForward=1,OFOSForward=2], EEForward=mEEBgOnlyForward, MMForward=mMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			# real model
			
			w.factory("SIMUL::combModel(cat[EEForward=0,MMForward=1,OFOSForward=2],  EEForward=mEEForward, MMForward=mMMForward, OFOSForward=ofosShapeForward)")
			
			w.factory("SIMUL::constraintCombModelBgOnly(cat[EEForward=0,MMForward=1,OFOSForward=2], EEForward=constraintMEEBgOnlyForward, MMForward=constraintMMMBgOnlyForward, OFOSForward=ofosShapeForward)")
			# real model
			
			w.factory("SIMUL::constraintCombModel(cat[EEForward=0,MMForward=1,OFOSForward=2], EEForward=mEEForward, MMForward=constraintMMMForward, OFOSForward=ofosShapeForward)")		
					
				
			data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w.cat('cat')),
									   ROOT.RooFit.WeightVar('weight'),
									   ROOT.RooFit.Import('OFOSForward', w.data("dataOFOSForward")),
									   ROOT.RooFit.Import('EEForward', w.data("dataEEForward")),
									   ROOT.RooFit.Import('MMForward', w.data("dataMMForward")))
			getattr(w, 'import')(data_obs)

			w.var("rSFOFCentral").setConstant()

						
		log.logWarning("Attempting background only Fit!")

		log.logHighlighted("Using capsuled fit to avoid memory problems!")
		w.writeToFile("workspaces/workSpaceTemp_%s.root"%theConfig.title)
		bashCommand = "./fitCapsule workspaces/workSpaceTemp_%s.root 0 0 %s"%(theConfig.title,theConfig.title)
		import subprocess
		process = subprocess.Popen(bashCommand.split())
		output = process.communicate()[0]
		log.logHighlighted("back in main routine")
		f = ROOT.TFile("workspaces/workSpaceTemp_%s.root_result"%theConfig.title)
		w =  f.Get("w")
		fitResult = w.var("fitQualityH0")
		parametersToSave["minNllH0"] = w.var("minNllH0").getVal()
		parametersToSave["nParH0"] = w.var("nParSFOSH0").getVal()
		log.logHighlighted("Background Only Fit Convergence Quality: %d"%fitResult.getVal())

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")		
		

		w.var('inv').setBins(theConfig.nBinsMinv)

		if dataSetConfiguration == "Combined":
			frameSFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w, w.data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, zPrediction=theConfig.zPredictions.SF.central.val,region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w,theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central",H0=True)	
			
			frameSFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w, w.data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, zPrediction=theConfig.zPredictions.SF.forward.val,region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)


			plotFitResults(w,theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward",H0=True)	

		elif dataSetConfiguration == "Central":		
			frameSFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w, w.data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, zPrediction=theConfig.zPredictions.SF.central.val,region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w,theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central",H0=True)	
							
		if dataSetConfiguration == "Forward":		
			frameSFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w, w.data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, zPrediction=theConfig.zPredictions.SF.forward.val,region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

			plotFitResults(w,theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward",H0=True)	








					   
		w.var("rSFOFCentral").setVal(theConfig.rSFOF.central.val)
		#~ w.var("nSigCentral").setVal(100)
		w.var("rSFOFForward").setVal(theConfig.rSFOF.forward.val)
		w.var("nZCentral").setVal(theConfig.zPredictions.SF.central.val)
		w.var("nZForward").setVal(theConfig.zPredictions.SF.forward.val)
		#~ w.var("rSFOFCentral").setConstant()
		#~ w.var("rSFOFForward").setConstant()
		if (theConfig.edgePosition > 0):
			w.var('m0').setVal(float(theConfig.edgePosition))
			if not x == None:
				w.var('m0').setVal(float(theConfig.toyConfig["m0"]))
				
			if (theConfig.fixEdge):
				w.var('m0').setConstant(ROOT.kTRUE)
			else:
				log.logWarning("Edge endpoint floating!")



						
		hasConverged = False
		log.logWarning("Attempting combined Fit!")
		log.logHighlighted("Using capsuled fit to avoid memory problems!")
		w.writeToFile("workspaces/workSpaceTemp_%s.root"%theConfig.title)
		if produceScan:
			bashCommand = "./fitCapsule workspaces/workSpaceTemp_%s.root 1 1 %s"%(theConfig.title,theConfig.title)
		else:
			bashCommand = "./fitCapsule workspaces/workSpaceTemp_%s.root 0 1 %s"%(theConfig.title,theConfig.title)			
		process = subprocess.Popen(bashCommand.split())
		output = process.communicate()[0]
		log.logHighlighted("back in main routine")
		f = ROOT.TFile("workspaces/workSpaceTemp_%s.root_result"%theConfig.title)
		w =  f.Get("w")
		fitResult = w.var("fitQualityH1")
		parametersToSave["minNllH1"] = w.var("minNllH1").getVal()
		parametersToSave["nParH1"] = w.var("nParSFOSH1").getVal()
		log.logHighlighted("Main Fit Convergence Quality: %d"%fitResult.getVal())

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")

		sizeCanvas = 800
		
		
		
		

		


		#~ frameOFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		#~ frameOFOSCentral.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		#~ frameOFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
		#~ frameOFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		#~ frameOFOSForward.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		#~ frameOFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)



		if dataSetConfiguration == "Combined":
			frameSFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w, w.data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, zPrediction=theConfig.zPredictions.SF.central.val,region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w,theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central")	
			
			frameSFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w, w.data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, zPrediction=theConfig.zPredictions.SF.forward.val,region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)
			
			
			parametersToSave["chi2SFOSCentral"] = frameSFOSCentral.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSCentral"])
			parametersToSave["chi2SFOSForward"] = frameSFOSForward.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSForward"])


			plotFitResults(w,theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward")	

			saveFitResults(w,theConfig,x,region="Central")		
			saveFitResults(w,theConfig,x,region="Forward")	
		elif dataSetConfiguration == "Central":		
			frameSFOSCentral = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSCentral = plotModel(w, w.data("dataSFOSCentral"), fitOFOSCentral, theConfig, pdf="modelCentral", tag="%sSFOSCentral" % theConfig.title, frame=frameSFOSCentral, zPrediction=theConfig.zPredictions.SF.central.val,region="Central")
			frameSFOSCentral.GetYaxis().SetTitle(theConfig.histoytitle)
			
			plotFitResults(w,theConfig, frameSFOSCentral,frameOFOSCentral,data_obs,fitOFOSCentral,region="Central")	
					
			parametersToSave["chi2SFOSCentral"] = frameSFOSCentral.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSCentral"])

			saveFitResults(w,theConfig,x,region="Central")		
		if dataSetConfiguration == "Forward":		
			frameSFOSForward = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
			frameSFOSForward = plotModel(w, w.data("dataSFOSForward"), fitOFOSForward, theConfig, pdf="modelForward", tag="%sSFOSForward" % theConfig.title, frame=frameSFOSForward, zPrediction=theConfig.zPredictions.SF.forward.val,region="Forward")
			frameSFOSForward.GetYaxis().SetTitle(theConfig.histoytitle)

			parametersToSave["chi2SFOSForward"] = frameSFOSForward.chiSquare(int(parametersToSave["nParH1"]))
			log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOSForward"])

			plotFitResults(w,theConfig, frameSFOSForward,frameOFOSForward,data_obs,fitOFOSForward,region="Forward")	
		
			saveFitResults(w,theConfig,x,region="Forward")	
		
	

main()
