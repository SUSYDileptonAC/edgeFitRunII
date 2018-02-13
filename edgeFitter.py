import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)
print sys.path
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import gROOT, gStyle, TFile, TH2F, TH2D, TF1,TMath, TH1F
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


def prepareDatasets(inv,weight,trees,addTrees,maxInv,minInv,typeName,nBinsMinv,rSFOF,rSFOFErr,addDataset,theConfig):


	vars = ROOT.RooArgSet(inv, weight)
	

	# data
	
	tmpEE = ROOT.RooDataSet("tmpEE", "tmpEE", vars, ROOT.RooFit.Import(trees["EE"]), ROOT.RooFit.WeightVar("weight"))
	tmpMM = ROOT.RooDataSet("tmpMM", "tmpMM", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpOFOS = ROOT.RooDataSet("tmpOFOS", "tmpOFOS", vars, ROOT.RooFit.Import(trees["OFOS"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS = ROOT.RooDataSet("tmpSFOS", "tmpSFOS", vars, ROOT.RooFit.Import(trees["MM"]), ROOT.RooFit.WeightVar("weight"))
	tmpSFOS.append(tmpEE)
	print tmpOFOS.sumEntries()
	print tmpSFOS.sumEntries()

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
		print tmpSFOS.sumEntries()
		print addTrees["OFOS"].GetEntries()
		print tmpAddOFOS.sumEntries()
		tmpEE.append(tmpAddEE)
		tmpMM.append(tmpAddMM)
		tmpSFOS.append(tmpAddEE)
		tmpSFOS.append(tmpAddMM)
		tmpOFOS.append(tmpAddOFOS)
		print tmpOFOS.sumEntries()
		print tmpSFOS.sumEntries()

	
	dataEE = ROOT.RooDataSet("%sEE" % (typeName), "Dataset with invariant mass of di-electron pairs",
							 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
	dataMM = ROOT.RooDataSet("%sMM" % (typeName), "Dataset with invariant mass of di-muon pairs",
							 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
	dataSFOS = ROOT.RooDataSet("%sSFOS" % (typeName), "Dataset with invariant mass of SFOS lepton pairs",
							   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
	dataOFOS = ROOT.RooDataSet("%sOFOS" % (typeName), "Dataset with invariant mass of OFOS lepton pairs",
							   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))

	histOFOS = createHistoFromTree(trees["OFOS"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
	histEE = createHistoFromTree(trees["EE"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
	histMM = createHistoFromTree(trees["MM"],"inv","weight",(theConfig.maxInv - theConfig.minInv) / 5,theConfig.minInv,theConfig.maxInv)
	
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
		
		selectShapes(wToys,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)
		
		
		dataEE = ROOT.RooDataSet("%sEE" % (typeName), "Dataset with invariant mass of di-electron pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpEE))
		dataMM = ROOT.RooDataSet("%sMM" % (typeName), "Dataset with invariant mass of di-muon pairs",
								 vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpMM))
		dataSFOS = ROOT.RooDataSet("%sSFOS" % (typeName), "Dataset with invariant mass of SFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpSFOS))
		dataOFOS = ROOT.RooDataSet("%sOFOS" % (typeName), "Dataset with invariant mass of OFOS lepton pairs",
								   vars, ROOT.RooFit.WeightVar('weight'), ROOT.RooFit.Import(tmpOFOS))		
		
		
		
		getattr(wToys, 'import')(dataEE, ROOT.RooCmdArg())
		getattr(wToys, 'import')(dataMM, ROOT.RooCmdArg())
		getattr(wToys, 'import')(dataSFOS, ROOT.RooCmdArg())
		getattr(wToys, 'import')(dataOFOS, ROOT.RooCmdArg())	
		

					
		wToys.factory("SUM::ofosShape(nB[100,0,100000]*ofosShape1)")
		wToys.Print()
		fitOFOS = wToys.pdf('ofosShape').fitTo(wToys.data('%sOFOS'%(typeName)), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
		numOFOS = tmpOFOS.sumEntries()
		
		
		scale = theConfig.toyConfig["scale"]
		
		tmpNumOFOS = float(numOFOS*scale)
		tmpNumOFOS2 = float(numOFOS*scale)
		print "Signal OFOS %d"%tmpNumOFOS2
		print "Signal SFOS %d"%tmpNumOFOS
		
		#~ if theConfig.toyConfig["nSig"] > 0:
			
			
		
		zPrediction = theConfig.zPredictions.MT2.SF.inclusive.val
		#~ zPrediction = 125.
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
			if theConfig.toyConfig["sShape"] == "Concave":
				log.logHighlighted("Dicing concave signal shape")
				wToys.factory("SUSYX4Pdf::eeShapeForToys(inv,const,sEE,m0)")
				wToys.factory("SUSYX4Pdf::mmShapeForToys(inv,const,sMM,m0)")		
				wToys.factory("SUM::backtoymodelEE(fsFrac*ofosShape, zFrac*zEEShape, sigFrac*eeShapeForToys)")
				wToys.factory("SUM::backtoymodelMM(fsFrac*ofosShape, zFrac*zMMShape, sigFrac*mmShapeForToys)")
								
			elif theConfig.toyConfig["sShape"] == "Convex":
				log.logHighlighted("Dicing convex signal shape")
				wToys.factory("SUSYXM4Pdf::eeShape%sForToys(inv,const,sEE,m0)")
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
			tmpREEOF = theConfig.rEEOF.inclusive.val + theConfig.rEEOF.inclusive.err
			tmpRMMOF = theConfig.rMMOF.inclusive.val + theConfig.rMMOF.inclusive.err
			tmpRSFOF = theConfig.rSFOF.inclusive.val + theConfig.rSFOF.inclusive.err
		elif theConfig.toyConfig["systShift"] == "Down":
			tmpREEOF = theConfig.rEEOF.inclusive.val - theConfig.rEEOF.inclusive.err
			tmpRMMOF = theConfig.rMMOF.inclusive.val - theConfig.rMMOF.inclusive.err
			tmpRSFOF = theConfig.rSFOF.inclusive.val - theConfig.inclusive.err
		else:
			tmpREEOF = theConfig.rEEOF.inclusive.val
			tmpRMMOF = theConfig.rMMOF.inclusive.val
			tmpRSFOF = theConfig.rSFOF.inclusive.val
			
				
		eeFraction = tmpREEOF/tmpRSFOF		
		mmFraction = tmpRMMOF/tmpRSFOF		
				
		genNumEE =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*eeFraction)
		genNumMM =  int((tmpNumOFOS*scale*tmpRSFOF + theConfig.toyConfig["nSig"]*scale + zPrediction*scale)*mmFraction)
		
		result = genToys(wToys,theConfig.toyConfig["nToys"],genNumEE,genNumMM,int(tmpNumOFOS))
		
	else:
		result = [{"EE":dataEE,"MM":dataMM,"SFOS":dataSFOS,"OFOS":dataOFOS,"EEHist":histEE,"MMHist":histMM,"SFOSHist":histSFOS,"OFOSHist":histOFOS}]			
		
	return result	



def selectShapes(ws,backgroundShape,signalShape,nBinsMinv):


	resMuon = 1.6
	resElectron = 1.6
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
	
	cContinuum = -0.017
	
	### IMPORTANT! If the bin size for the cache is not set to the same used in the the drell-yan fit, things get really fucked up! 
	ws.var("inv").setBins(240,"cache")	
	#~ ws.var("inv").setBins(140,"cache")	

	ws.factory("m0[55., 30., 500.]")
	#~ ws.factory("m0[55., 30., 300.]")
	ws.var('m0').setAttribute("StoreAsymError")
	ws.factory("m0Show[45., 0., 500.]")
	#~ ws.factory("m0Show[45., 0., 300.]")
	#ws.factory("m0[75., 75., 75.]")
	ws.factory("constant[45,20,100]")

	cContinuumEE = tools.loadParameter("expofit", "dyExponent_EE", "expo",basePath="dyShelves/")
	cContinuumMM = tools.loadParameter("expofit", "dyExponent_MM", "expo",basePath="dyShelves/")
	cbMeanEE = tools.loadParameter("expofit", "dyExponent_EE", "cbMean",basePath="dyShelves/")
	cbMeanMM = tools.loadParameter("expofit", "dyExponent_MM", "cbMean",basePath="dyShelves/")
	nZEE = tools.loadParameter("expofit", "dyExponent_EE", "nZ",basePath="dyShelves/")
	nZMM = tools.loadParameter("expofit", "dyExponent_MM", "nZ",basePath="dyShelves/")
	zFractionEE = tools.loadParameter("expofit", "dyExponent_EE", "zFraction",basePath="dyShelves/")
	zFractionMM = tools.loadParameter("expofit", "dyExponent_MM", "zFraction",basePath="dyShelves/")
	nLEE = tools.loadParameter("expofit", "dyExponent_EE", "nL",basePath="dyShelves/")
	nLMM = tools.loadParameter("expofit", "dyExponent_MM", "nL",basePath="dyShelves/")
	nREE = tools.loadParameter("expofit", "dyExponent_EE", "nR",basePath="dyShelves/")
	nRMM = tools.loadParameter("expofit", "dyExponent_MM", "nR",basePath="dyShelves/")
	alphaLEE = tools.loadParameter("expofit", "dyExponent_EE", "alphaL",basePath="dyShelves/")
	alphaLMM = tools.loadParameter("expofit", "dyExponent_MM", "alphaL",basePath="dyShelves/")
	alphaREE = tools.loadParameter("expofit", "dyExponent_EE", "alphaR",basePath="dyShelves/")
	alphaRMM = tools.loadParameter("expofit", "dyExponent_MM", "alphaR",basePath="dyShelves/")
	sEE = tools.loadParameter("expofit", "dyExponent_EE", "s",basePath="dyShelves/")
	sMM = tools.loadParameter("expofit", "dyExponent_MM", "s",basePath="dyShelves/")
	
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
		#works!
		ws.factory("Chebychev::ofosShape1(inv,{a1[0,-2,2],b1[0,-2,2],c1[0,-1,1],d1[0,-1,1],e1[0,-1,1],f1[0,-1,1]})")
		
	elif backgroundShape == 'CB':
		log.logHighlighted("Using crystall ball shape")
		ws.factory("CBShape::ofosShape1(inv,cbMean[50.,0.,200.],cbSigma[20.,0.,100.],alpha[-1,-10.,0.],n[1.,0.,100.])")
		#~ ws.factory("CBShape::ofosShape1(inv,cbMean[50.,0.,200.],cbSigma[20.,0.,100.],alpha[-1,-10.,0.],n[100.])")
		
	elif backgroundShape == 'B':
		log.logHighlighted("Using BH shape")
		ws.factory("SUSYBkgBHPdf::ofosShape1(inv,a1[1.],a2[100,0,250],a3[1,0,100],a4[0.1,0,2])")
		
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
		ws.factory("SUSYBkgMAPdf::ofosShape1(inv,b1[-2000,-8000,8000],b2[120.,-800,800],b3[-1.,-5,5.],b4[0.01,-0.1,0.1], m1[50,20,100],m2[120,100,160])") 
		
	elif backgroundShape == 'ETH':
		log.logHighlighted("Using Marco-Andreas shape for real")
		####### final -  never touch again!
		ws.factory("TopPairProductionSpline::ofosShape1(inv,b1[-1800,-5000,5000],b2[120.,-400,400],b4[0.0025,0.0001,0.01], m1[60.],m2[110.])") #
		############
	elif backgroundShape == 'P':
		log.logHighlighted("Gaussians activated!")
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1(inv,a1[30.,0.,70.],a2[60.,20.,105.],a3[100.,-1000.,1000.],b1[15,10.,80.],b2[20.,10.,80.],b3[200.,10.,3000.])") #High MET

	elif backgroundShape == "K":
		log.logHighlighted("Kernel Density Estimation activated")
		nameDataOFOS = "dataOFOS" 
		ws.factory("RooKeysPdf::ofosShape1(inv, %s, MirrorBoth)" % (nameDataOFOS))
	elif backgroundShape == "Hist":
		log.logHighlighted("HistSubtraction activated!")
		ws.var('inv').setBins(nBinsMinv)
		tempDataHist = ROOT.RooDataHist("dataHistOFOS", "dataHistOFOS", ROOT.RooArgSet(ws.var('inv')), ws.data("dataOFOS"))
		getattr(ws, 'import')(tempDataHist, ROOT.RooCmdArg())
		ws.factory("RooHistPdf::ofosShape1(inv, dataHistOFOS)")
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
	#~ elif signalShape == 'XM4' in Holder.shape:
	elif signalShape == 'XM4':
		ws.factory("SUSYXM4Pdf::sfosShape(inv,constant,s,m0)")
		ws.factory("SUSYXM4Pdf::sfosShapeShow(inv,constant,s,m0Show)")
		ws.factory("SUSYXM4Pdf::eeShape(inv,constant,sEE,m0)")
		ws.factory("SUSYXM4Pdf::mmShape(inv,constant,sMM,m0)")
		ws.var('constant').setConstant(ROOT.kTRUE)
	else:
		log.logHighlighted("No valid background shape selected, exiting")
		sys.exit()


def genToys(ws, nToys=10,genEE=0,genMM=0,genOFOS=0):
	theToys = []

	mcEE = ROOT.RooMCStudy(ws.pdf('backtoymodelEE'), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcEE.generate(nToys, genEE, ROOT.kTRUE)
	mcMM = ROOT.RooMCStudy(ws.pdf("backtoymodelMM"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
	mcMM.generate(nToys, genMM, ROOT.kTRUE)
	mcOFOS = ROOT.RooMCStudy(ws.pdf("ofosShape"), ROOT.RooArgSet(ws.var('inv')),ROOT.RooFit.Extended(ROOT.kTRUE))
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


def plotModel(w, data, fitOFOS, theConfig, pdf="model", tag="", frame=None, zPrediction= -1.0,
			  slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), cut=ROOT.RooCmdArg.none(),
			  overrideShapeNames={},H0=False):
	if (frame == None):
		frame = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
	frame.GetXaxis().SetTitle('m_{ll} [GeV]')
	#~ frame.SetMinimum(-20.)
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
	
	# get pdfs
	plotZ = ROOT.RooArgSet(w.pdf(shapeNames['Z']))
	plotOFOS = ROOT.RooArgSet(w.pdf(shapeNames['Background']))
	print shapeNames['Signal']
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
							  ROOT.RooFit.LineStyle(3), ROOT.RooFit.LineColor(ROOT.kRed))
		# add Z prediction to ofos background
		relScale = zPrediction / fittedZ
		log.logDebug("Relative scale for Z prediction: %f" % (relScale))
		w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotZ), ROOT.RooFit.Normalization(relScale, ROOT.RooAbsReal.Relative), ROOT.RooFit.Name(nameBGZShape),
							  slice, projWData,
							  ROOT.RooFit.LineStyle(ROOT.kDashed), ROOT.RooFit.LineColor(ROOT.kBlack), ROOT.RooFit.Invisible())
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
							  ROOT.RooFit.LineStyle(3), ROOT.RooFit.LineColor(ROOT.kRed))


	############
	### plot edge signal component
	
	### If the fitted signal is negative, for some reason ROOFit plots it at 0.
	### Comment this part out and comment in the part in plotFitResults to do it anyway.
	### Remember to set minimum of y-axis to appropriate negative value in formatAndDrawFrame
	if not H0:
		w.pdf(pdf).plotOn(frame, ROOT.RooFit.Components(plotSignal),
							  slice, projWData,
							  ROOT.RooFit.LineStyle(4), ROOT.RooFit.LineColor(ROOT.kViolet))
	############
	
	return frame


def saveFitResults(ws,theConfig,x = None):
	 
	if x == None:
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nS", ws.var('nSig').getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nZ", ws.var('nZ').getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nB", ws.var('nB').getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "rSFOF", ws.var('rSFOF').getVal(),basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "m0", ws.var('m0').getVal(),basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sOFOS" %(theConfig.title), "chi2", parametersToSave["chi2OFOS"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sOFOS" %(theConfig.title), "chi2Prob", parametersToSave["chi2ProbOFOS"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sOFOS" %(theConfig.title), "nPar", parametersToSave["nParOFOS"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "chi2H1",parametersToSave["chi2SFOS"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "chi2H0",parametersToSave["chi2SFOSH0"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "chi2ProbH1",parametersToSave["chi2ProbSFOS"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "chi2ProbH0",parametersToSave["chi2ProbSFOSH0"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "nPar", parametersToSave["nParH1"],basePath=theConfig.shelvePath)		
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllH0", parametersToSave["minNllH0"],basePath=theConfig.shelvePath)
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllH1", parametersToSave["minNllH1"],basePath=theConfig.shelvePath)											
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "minNllOFOS", parametersToSave["minNllOFOS"],basePath=theConfig.shelvePath)											
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
		
		
		ws.var("inv").setRange("fullRange",20,500)
		ws.var("inv").setRange("lowMass",20,70)
		ws.var("inv").setRange("mass20To60",20,60)
		ws.var("inv").setRange("mass60To86",60,86)
		ws.var("inv").setRange("mass96To150",96,150)
		argSet = ROOT.RooArgSet(ws.var("inv"))
		
		fittedZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("zPeak"))
		fittedZ = fittedZInt.getVal()*ws.var("nZ").getVal()
		
		fittedLowMassZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassZ = fittedLowMassZInt.getVal()*ws.var("nZ").getVal()
		
		fittedLowMassSInt = ws.pdf("sfosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassS = fittedLowMassSInt.getVal()*ws.var("nSig").getVal()
		
		fittedLowMassBInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("lowMass"))
		fittedLowMassB = fittedLowMassBInt.getVal()*ws.var("nB").getVal()*ws.var("rSFOF").getVal()

		
		fittedMass20To60ZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass20To60"))
		fittedMass20To60Z = fittedMass20To60ZInt.getVal()*ws.var("nZ").getVal()
		
		fittedMass20To60SInt = ws.pdf("sfosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass20To60"))
		fittedMass20To60S = fittedMass20To60SInt.getVal()*ws.var("nSig").getVal()
		
		fittedMass20To60BInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass20To60"))
		fittedMass20To60B = fittedMass20To60BInt.getVal()*ws.var("nB").getVal()
		fittedMass20To60BPred = fittedMass20To60BInt.getVal()*ws.var("nB").getVal()*ws.var("rSFOF").getVal()
		
		fittedMass60To86ZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass60To86"))
		fittedMass60To86Z = fittedMass60To86ZInt.getVal()*ws.var("nZ").getVal()
		
		fittedMass60To86SInt = ws.pdf("sfosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass60To86"))
		fittedMass60To86S = fittedMass60To86SInt.getVal()*ws.var("nSig").getVal()
		
		fittedMass60To86BInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass60To86"))
		fittedMass60To86B = fittedMass60To86BInt.getVal()*ws.var("nB").getVal()
		fittedMass60To86BPred = fittedMass60To86BInt.getVal()*ws.var("nB").getVal()*ws.var("rSFOF").getVal()
		
		fittedMass96To150ZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass96To150"))
		fittedMass96To150Z = fittedMass96To150ZInt.getVal()*ws.var("nZ").getVal()
		
		fittedMass96To150SInt = ws.pdf("sfosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass96To150"))
		fittedMass96To150S = fittedMass96To150SInt.getVal()*ws.var("nSig").getVal()
		
		fittedMass96To150BInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(argSet), ROOT.RooFit.Range("mass96To150"))
		fittedMass96To150B = fittedMass96To150BInt.getVal()*ws.var("nB").getVal()
		fittedMass96To150BPred = fittedMass96To150BInt.getVal()*ws.var("nB").getVal()*ws.var("rSFOF").getVal()

		
		
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "onZZYield",fittedZ,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassZYield",fittedLowMassZ,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassSYield",fittedLowMassS,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassBYield",fittedLowMassB,basePath=theConfig.shelvePath)				
                                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60ZYield",fittedMass20To60Z,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60SYield",fittedMass20To60S,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60BYield",fittedMass20To60B,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60BPred",fittedMass20To60BPred,basePath=theConfig.shelvePath)				
                                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86ZYield",fittedMass60To86Z,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86SYield",fittedMass60To86S,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86BYield",fittedMass60To86B,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86BPred",fittedMass60To86BPred,basePath=theConfig.shelvePath)				
                                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150ZYield",fittedMass96To150Z,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150SYield",fittedMass96To150S,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150BYield",fittedMass96To150B,basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150BPred",fittedMass96To150BPred,basePath=theConfig.shelvePath)				
                                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "onZZYielderror",fittedZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassZYielderror",fittedLowMassZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassSYielderror",fittedLowMassSInt.getVal()*ws.var("nSig").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "lowMassBYielderror",fittedLowMassBInt.getVal()*ws.var("nB").getError(),basePath=theConfig.shelvePath)					
				                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60ZYielderror",fittedMass20To60ZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60SYielderror",fittedMass20To60SInt.getVal()*ws.var("nSig").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass20To60BYielderror",fittedMass20To60BInt.getVal()*ws.var("nB").getError(),basePath=theConfig.shelvePath)				
				                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86ZYielderror",fittedMass60To86ZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86SYielderror",fittedMass60To86SInt.getVal()*ws.var("nSig").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass60To86BYielderror",fittedMass60To86BInt.getVal()*ws.var("nB").getError(),basePath=theConfig.shelvePath)				
				                                                  
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150ZYielderror",fittedMass96To150ZInt.getVal()*ws.var("nZ").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150SYielderror",fittedMass96To150SInt.getVal()*ws.var("nSig").getError(),basePath=theConfig.shelvePath)				
		tools.storeParameter("edgefit", "%sSFOS" %(theConfig.title), "mass96To150BYielderror",fittedMass96To150BInt.getVal()*ws.var("nB").getError(),basePath=theConfig.shelvePath)				
				
	else:
		title = theConfig.title.split("_%s"%x)[0]
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nS", ws.var('nSig').getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nZ", ws.var('nZ').getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nB", ws.var('nB').getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "rSFOF", ws.var('rSFOF').getVal(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "m0", ws.var('m0').getVal(), index = x)
		tools.updateParameter("edgefit", "%sOFOS" %(title), "chi2",parametersToSave["chi2OFOS"], index = x)
		tools.updateParameter("edgefit", "%sOFOS" %(title), "chi2Prob",parametersToSave["chi2ProbOFOS"], index = x)
		tools.updateParameter("edgefit", "%sOFOS" %(title), "nPar",parametersToSave["nParOFOS"], index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "chi2H1",parametersToSave["chi2SFOS"], index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "chi2H0",parametersToSave["chi2SFOSH0"], index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "chi2ProbH1",parametersToSave["chi2ProbSFOS"], index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "chi2ProbH0",parametersToSave["chi2ProbSFOSH0"], index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nPar",parametersToSave["nParH1"], index = x)		
		tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllH0", parametersToSave["minNllH0"], index = x)				
		tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllH1", parametersToSave["minNllH1"], index = x)				
		tools.updateParameter("edgefit", "%sSFOS" %(title), "minNllOFOS", parametersToSave["minNllOFOS"], index = x)				
		tools.updateParameter("edgefit", "%sSFOS" %(title), "initialM0", parametersToSave["initialM0"], index = x)	
				                                         
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nSerror", ws.var('nSig').getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nZerror", ws.var('nZ').getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "nBerror", ws.var('nB').getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "rSFOFerror", ws.var('rSFOF').getError(), index = x)
		tools.updateParameter("edgefit", "%sSFOS" %(title), "m0error", ws.var('m0').getError(), index = x)
		
		
											
								

def plotFitResults(ws,theConfig,frameSFOS,frameOFOS,data_obs,fitOFOS,H0=False):

	frameSFOS.SetMinimum(0.)
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
	zLeg.SetLineStyle(3)
	zLeg.SetLineColor(ROOT.kRed)
	if not H0:
		sLeg = dLeg.Clone()
		sLeg.SetLineStyle(4)
		sLeg.SetLineColor(ROOT.kViolet)
	bLeg = dLeg.Clone()
	bLeg.SetLineStyle(2)
	bLeg.SetLineColor(ROOT.kBlack)
	if theConfig.plotErrorBands:
		uLeg = dLeg.Clone()
		uLeg.SetLineColor(ROOT.kGreen + 2)
		uLeg.SetFillColor(ROOT.kGreen + 2)
		uLeg.SetFillStyle(3009)
	lmLeg = dLeg.Clone()
	lmLeg.SetLineColor(ROOT.kRed)
	lmLeg.SetLineStyle(ROOT.kDotted)
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

	sl = tools.myLegend(0.45, 0.89 - 0.07 * nLegendEntries, 0.92, 0.91, borderSize=0)
	sl.SetTextAlign(22)
	if (useMC):
		sl.AddEntry(dLeg, 'Simulation', "pe")
	else:
		sl.AddEntry(dLeg, 'Data', "pe")
	sl.AddEntry(fitLeg, 'Fit', "l")

	if not H0:
		sl.AddEntry(sLeg, 'Signal', "l")
	zLeg.SetLineColor(ROOT.kRed)
	sl.AddEntry(zLeg, 'Z/#gamma* background', "l")
	sl.AddEntry(bLeg, 'FS background', "l")
	if theConfig.plotErrorBands:
		sl.AddEntry(uLeg, 'OF uncertainty', "f")
		
		
	nLegendEntries = 2
	if theConfig.plotErrorBands:
		nLegendEntries =3
	bl = tools.myLegend(0.55, 0.89 - 0.07 * nLegendEntries, 0.92, 0.91, borderSize=0)
	bl.SetTextAlign(22)
	
	if (useMC):
		bl.AddEntry(dLeg, 'Simulation', "pl")
	else:
		bl.AddEntry(dLeg, 'Data', "pe")
	bl.AddEntry(fitLeg, 'FS background', "l")
	if theConfig.plotErrorBands:
		bl.AddEntry(uLeg, 'Uncertainty', "f")		


	nSignal = ws.var('nSig').getVal()
	nSignalError = ws.var('nSig').getError()
	annotEdge = 'fitted N_{S}^{edge} = %.0f #pm %.0f' % (nSignal, nSignalError)

	if theConfig.runMinos:
		nSignalError = max(ws.var('nSig').getError(),max(abs(ws.var('nSig').getAsymErrorHi()),abs(ws.var('nSig').getAsymErrorLo())))
		annotEdge = 'fitted N_{S}^{edge} = %.0f #pm %.0f' % (nSignal, nSignalError)
		
	ws.var("inv").setRange("zPeak",81,101)
	ws.var("inv").setRange("fullRange",20,500)
	ws.var("inv").setRange("lowMass",20,70)
	argSet = ROOT.RooArgSet(ws.var("inv"))
	
	fittedZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZ = fittedZInt.getVal()
	
	fittedZIntEE = ws.pdf("zEEShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZEE = fittedZIntEE.getVal()
	
	fittedZIntMM = ws.pdf("zMMShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("zPeak"))
	fittedZMM = fittedZIntMM.getVal()
	

	fittedFullZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("fullRange"))
	fittedFullZ = fittedFullZInt.getVal()
	
	fittedLowMassZInt = ws.pdf("zShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("lowMass"))
	fittedLowMassZ = fittedLowMassZInt.getVal()
	
	
	print fittedLowMassZ, fittedZ, fittedFullZ
	
	correctedZ = fittedZ/fittedFullZ*ws.var("nZ").getVal()
	correctedLowMassZ = fittedLowMassZ/fittedFullZ*ws.var("nZ").getVal()
	
	fittedZErr = max(ws.var("nZ").getError(),max(abs(ws.var("nZ").getAsymErrorLo()),abs(ws.var("nZ").getAsymErrorHi())))*(fittedZ/fittedFullZ)
	fittedLowMassZErr = max(ws.var("nZ").getError(),max(abs(ws.var("nZ").getAsymErrorLo()),abs(ws.var("nZ").getAsymErrorHi())))*(fittedLowMassZ/fittedFullZ)
	
	fittedBackgroundLowMassInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("lowMass"))
	bgLowMass = fittedBackgroundLowMassInt.getVal()
	
	fittedBackgroundFullRangeInt = ws.pdf("ofosShape").createIntegral(argSet,ROOT.RooFit.NormSet(ROOT.RooArgSet(ws.var("inv"))), ROOT.RooFit.Range("FullRange"))
	bgLowMass = ws.var("nB").getVal() * (fittedBackgroundLowMassInt.getVal() / fittedBackgroundFullRangeInt.getVal() ) * ws.var("rSFOF").getVal()
	bgLowMassErr = max(ws.var("nB").getError(),max(abs(ws.var("nB").getAsymErrorLo()),abs(ws.var("nB").getAsymErrorHi()))) * (fittedBackgroundLowMassInt.getVal() / fittedBackgroundFullRangeInt.getVal() ) * ws.var("rSFOF").getVal()
	
	annotZ = 'N_{Z} = %.1f #pm %.1f' % (correctedZ, fittedZErr)
	annotLowMassZ = "N_{Z} = %.1f #pm %.1f" % (correctedLowMassZ, fittedLowMassZErr)	

		
	varBack = ws.var('nB').getVal()
	varBackErr = ws.var('nB').getError()

	annotBG = 'N_{B}^{OF} = %.1f #pm %.1f (%.1f #pm %.1f)' % (bgLowMass, bgLowMassErr,varBack, varBackErr)
	annotNSStar = ""
	annotZpred = ""
	
	if theConfig.plotAsymErrs:
		note2 = "m^{edge}_{ll} = %.1f^{+%.1f}_{-%.1f} GeV"
		note2 = note2%(ws.var("m0").getVal(),ws.var("m0").getAsymErrorHi(),abs(ws.var("m0").getAsymErrorLo()))
	else:
		note2 = "m^{edge}_{ll} = %.1f #pm %.1f GeV"
		note2 = note2%(ws.var("m0").getVal(),ws.var("m0").getError())
	

	sfosName = '%s/fit_%s_%s.pdf' % (theConfig.figPath, shape, title)
	ofosName = '%s/fit_OFOS_%s_%s.pdf' % (theConfig.figPath, shape, title)
	eeName = '%s/fit_EE_%s_%s.pdf' % (theConfig.figPath, shape, title)
	mmName = '%s/fit_MM_%s_%s.pdf' % (theConfig.figPath, shape, title)
	if H0:
		sfosName = '%s/fit_H0_%s_%s.pdf' % (theConfig.figPath, shape, title)
		ofosName = '%s/fit_OFOS_H0_%s_%s.pdf' % (theConfig.figPath,  shape, title)
		eeName = '%s/fit_EE_H0_%s_%s.pdf' % (theConfig.figPath, shape, title)
		mmName = '%s/fit_MM_H0_%s_%s.pdf' % (theConfig.figPath, shape, title)	

	# determine y axis range
	#~ yMaximum = 1.2 * max(frameOFOS.GetMaximum(), frameSFOS.GetMaximum())
	yMaximum = 250
	if (theConfig.plotYMax > 0.0):
		yMaximum = theConfig.plotYMax
		
	if theConfig.logPlot:
		yMaximum = 100* yMaximum 


	# make OFOS plot
	#---------------
	print "before OFOS plot"
	projWData = ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs)

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "OFOS")
	
	frameOFOS = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of e#mu lepton pairs'))
	frameOFOS = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sOFOS" % title, frame=frameOFOS, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::OFOS"),H0=H0)
	frameOFOS.GetYaxis().SetTitle(histoytitle)
	cOFOS = ROOT.TCanvas("OFOS distribtution", "OFOS distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cOFOS.cd()
	pads = formatAndDrawFrame(frameOFOS, theConfig, title="OFOS", pdf=ws.pdf("combModel"), yMax=yMaximum,
							slice=ROOT.RooFit.Slice(ws.cat("cat"), "OFOS"),
							projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							residualMode =residualMode,
							histName = "h_data_obs_Cut[cat==cat::OFOS]",
							curveName = "ofosShape_Norm[inv]")
							
	bl.Draw()
	
	annotationsTitle = [
					(0.92, 0.48, "%s" % (theConfig.selection.latex)),
					]
	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
	
	dileptonAnnotation = [
						#~ (0.92, 0.27, "%s" % ("OCDF")),
						(0.92, 0.22, "%s" % ("OCDF")),
						]
	tools.makeAnnotations(dileptonAnnotation, color=ROOT.kBlack, textSize=0.04, align=31)	
		
	
	if not theConfig.useToys:
		cOFOS.Print(ofosName)	
	for pad in pads:
		pad.Close()


	# make ee plot
	#------------
	
	shapeNames = {}

	shapeNames['Z'] = "zEEShape"
	shapeNames['offShell'] = "offShell"
	shapeNames['Signal'] = "eeShape"

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "EE")

	frameEE = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of ee lepton pairs'))
	frameEE = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sEE" % title, frame=frameEE, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::EE"),
						overrideShapeNames=shapeNames,H0=H0)						

	cEE = ROOT.TCanvas("EE distribtution", "EE distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cEE.cd()
	pads = formatAndDrawFrame(frameEE, theConfig, title="EE", pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "EE"),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode =residualMode,
							  histName = "h_data_obs_Cut[cat==cat::EE]",
							  curveName = "mEE_Norm[inv]")

	annotationsTitle = [
					   (0.92, 0.48, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.42, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)

	frameEE.GetXaxis().SetTitle('m_{ee} [GeV]')
	frameEE.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cEE.Update()
	if not theConfig.useToys:
		cEE.Print(eeName)
	for pad in pads:
		pad.Close()


	# make mm plot
	#------------
	shapeNames['Z'] = "zMMShape"
	shapeNames['Signal'] = "mmShape"
	shapeNames['offShell'] = "offShell"

	slice = ROOT.RooFit.Slice(ws.cat("cat"), "MM")

	frameMM = ws.var('inv').frame(ROOT.RooFit.Title('Invariant mass of mumu lepton pairs'))
	frameMM = plotModel(ws, data_obs, fitOFOS, theConfig, pdf="combModel", tag="%sMM" % title, frame=frameMM, zPrediction=0.0,
						slice=slice, projWData=projWData, cut=ROOT.RooFit.Cut("cat==cat::MM"),
						overrideShapeNames=shapeNames,H0=H0)

	cMM = ROOT.TCanvas("MM distribtution", "MM distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cMM.cd()
	pads = formatAndDrawFrame(frameMM, theConfig, title="MM", pdf=ws.pdf("combModel"), yMax=yMaximum,
							  slice=ROOT.RooFit.Slice(ws.cat("cat"), "MM"),
							  projWData=ROOT.RooFit.ProjWData(ROOT.RooArgSet(ws.cat("cat")), data_obs),
							  residualMode=residualMode,
							  histName = "h_data_obs_Cut[cat==cat::MM]",
							  curveName = "mMM_Norm[inv]")

	annotationsTitle = [
					   (0.92, 0.48, "%s" % (theConfig.selection.latex)),
					   (0.92, 0.42, "%s" % (note2)),
					   ]

	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=ROOT.kBlue, textSize=0.04, align=31)

	frameMM.GetXaxis().SetTitle('m_{#mu#mu} [GeV]')
	frameMM.GetYaxis().SetTitle(histoytitle)

	sl.Draw()
	cMM.Update()
	if not theConfig.useToys:
		cMM.Print(mmName)
	for pad in pads:
		pad.Close()


	# make SFOS plot
	#---------------
	cSFOS = ROOT.TCanvas("SFOS distribtution", "SFOS distribution", sizeCanvas, int(1.25 * sizeCanvas))
	cSFOS.cd()
	
	pads = formatAndDrawFrame(frameSFOS, theConfig, title="SFOS", 
								pdf=ws.pdf("model"), yMax=yMaximum, residualMode=residualMode,
								histName = "h_dataSFOS",
								curveName = "model_Norm[inv]")

	if (not fixEdge):
		edgeHypothesis = ws.var('m0').getVal()
		
	### The Histograms with MC have a large content in the overflow bin, which screws up the default chi2 calculation
	### Therefore we calculate it ourself when the pull plots are created
	
	if not H0:
		if theConfig.useMC:
			parametersToSave["chi2SFOS"] = parametersToSave["chi2SFOSTemp"]/(theConfig.nBinsMinv-int(parametersToSave["nParH1"]))
		else:
			parametersToSave["chi2SFOS"] = frameSFOS.chiSquare(int(parametersToSave["nParH1"]))
		parametersToSave["chi2ProbSFOS"] = TMath.Prob(parametersToSave["chi2SFOS"]*(theConfig.nBinsMinv-int(parametersToSave["nParH1"])),theConfig.nBinsMinv-int(parametersToSave["nParH1"]))
		log.logDebug("Fit Chi2 SFOS: %f" % parametersToSave["chi2SFOS"])
		
		log.logDebug("Fit Free parameters SFOS: %f" % (int(theConfig.nBinsMinv)-int(parametersToSave["nParH1"])))	
		
		log.logDebug("FitChi2 Probability SFOS: %f" %parametersToSave["chi2ProbSFOS"])	
		
		goodnessOfFit = '#chi^{2}-prob. = %.3f' % parametersToSave["chi2ProbSFOS"]
		annotationsTitle = [
						   (0.92, 0.49, "%s" % (theConfig.selection.latex)),
						   (0.92, 0.42, "%s" % (goodnessOfFit)),
						   (0.92, 0.35, "%s" % (note2)),
						   (0.92, 0.28, annotEdge),
						   ]
		
	else:
		if theConfig.useMC:
			parametersToSave["chi2SFOSH0"] = parametersToSave["chi2SFOSTemp"]/(theConfig.nBinsMinv-int(parametersToSave["nParH0"]))
		else:
			parametersToSave["chi2SFOSH0"] = frameSFOS.chiSquare(int(parametersToSave["nParH0"]))
		parametersToSave["chi2ProbSFOSH0"] = TMath.Prob(parametersToSave["chi2SFOSH0"]*(theConfig.nBinsMinv-int(parametersToSave["nParH0"])),theConfig.nBinsMinv-int(parametersToSave["nParH0"]))
		log.logDebug("Background only Fit Chi2 SFOS: %f" % parametersToSave["chi2SFOSH0"])
		
		log.logDebug("Background only Fit Free parameters SFOS: %f" % (int(theConfig.nBinsMinv)-int(parametersToSave["nParH0"])))	
		
		log.logDebug("Background only FitChi2 Probability SFOS: %f" %parametersToSave["chi2ProbSFOSH0"])	

		if parametersToSave["chi2ProbSFOSH0"] < 0.001:
			goodnessOfFit = '#chi^{2}-prob. < 0.001'
		else:
			goodnessOfFit = '#chi^{2}-prob. = %.3f' % parametersToSave["chi2ProbSFOSH0"]
		annotationsTitle = [
							(0.92, 0.48, "%s" % (theConfig.selection.latex)),
						   (0.92, 0.42, "%s" % (goodnessOfFit)),
							]
							
	tools.makeCMSAnnotation(0.18, 0.88, luminosity, mcOnly=useMC, preliminary=isPreliminary, year=year,ownWork=theConfig.ownWork)
	if (showText):
		tools.makeAnnotations(annotationsTitle, color=tools.myColors['AnnBlue'], textSize=0.04, align=31)
	annotRangeLow = "Low Mass (20 < m_{ll} < 70):"
	annotRangeZ = "Z Peak (81 < m_{ll} < 101):"
	annotationsFitHeader = [
					   (0.92, 0.55, annotRangeLow),
					   ]
	
	dileptonAnnotation = [
						#~ (0.92, 0.27, "%s" % ("OCSF")),
						(0.92, 0.22, "%s" % ("OCSF")),
						]
	tools.makeAnnotations(dileptonAnnotation, color=ROOT.kBlack, textSize=0.04, align=31)
	
	############
	
	### If the fitted signal is negative, for some reason ROOFit plots it at 0.
	### Use this part and comment out usual plotting of signal in plotModel to plot it anyway.
	### Remember to set minimum of y-axis to appropriate negative value in formatAndDrawFrame

	#~ if not H0:
		#~ m0=ws.var("m0").getVal()
		#~ res = 1.6
		#~ 
		#~ nbins = int((theConfig.plotMaxInv-theConfig.plotMinInv)) 
		#~ signalHisto = ROOT.TH1F("signalHist","signalHistogram",nbins,theConfig.plotMinInv,theConfig.plotMaxInv)
		#~ 
		#~ for i in range(0,nbins):
			#~ xval = i+theConfig.plotMinInv
			#~ signalHisto.SetBinContent(i,(TMath.Sqrt(2)*res*(TMath.Exp(-xval*xval/(2*res*res))-TMath.Exp(-(m0-xval)*(m0-xval)/(2*res*res)))+xval*TMath.Sqrt(TMath.Pi())*(TMath.Erf(xval/(TMath.Sqrt(2)*res))+TMath.Erf((m0-xval)/(TMath.Sqrt(2)*res)))))
				#~ 
		#~ signalHisto.Scale(5*nSignal/signalHisto.Integral())	
		#~ signalHisto.SetLineStyle(4)
		#~ signalHisto.SetLineWidth(4)
		#~ signalHisto.SetLineColor(ROOT.kViolet)
		#~ signalHisto.Draw("same l")
	
	############
        
	if theConfig.logPlot:
		pads[0].SetLogy(1)
	sl.Draw("same")
	cSFOS.Update()
	if not theConfig.useToys:
		cSFOS.Print(sfosName)
	for pad in pads:
		pad.Close()



def formatAndDrawFrame(frame, theConfig, title, pdf, yMax=0.0, slice=ROOT.RooCmdArg.none(), projWData=ROOT.RooCmdArg.none(), residualMode = "diff",histName = "", curveName = ""):
	# This routine formats the frame and adds the residual plot.
	# Residuals are determined with respect to the given pdf.
	# For simultaneous models, the slice and projection option can be set.
	
	if (yMax > 0.0):
		frame.SetMaximum(yMax)
	frame.GetXaxis().SetRangeUser(theConfig.plotMinInv, theConfig.plotMaxInv)
	if theConfig.logPlot:
		yMin = 0.1
		frame.SetMinimum(0.01)
		frame.GetYaxis().SetRangeUser(0.01, yMax)
	else:
		### Set minimum depending if signal contribution is negative
		### Since RooFit for some reason does not plot a negative 
		### component, remember to change the parts in plotFitResults
		### and plotModel as well
		#~ yMin = -25.
		#~ yMin = -12.
		yMin = 0.
	
	
	pad = ROOT.TPad("main%s" % (title), "main%s" % (title), 0.01, 0.25, 0.99, 0.99)
	pad.SetNumber(1)
	pad.Draw()
	
	resPad = ROOT.TPad("residual%s" % (title), "residual%s" % (title), 0.01, 0.01, 0.99, 0.25)
	resPad.SetNumber(2)
	resPad.Draw()
	
	pad.cd()	
	pad.DrawFrame(theConfig.plotMinInv,yMin,theConfig.plotMaxInv,yMax,";m_{ll} [GeV];Events / 5 GeV")
	
	
	pdf.plotOn(frame, slice, projWData)	
	frame.Draw("same")
	frame.Print()
	
	resPad.cd()
	residualMaxY = 20.
	residualTitle = "data - fit"
	if residualMode == "pull":
		residualMaxY = 3.
		residualTitle = "#frac{data - fit}{#sqrt{fit}}"
	hAxis = resPad.DrawFrame(theConfig.plotMinInv, -residualMaxY, theConfig.plotMaxInv, residualMaxY, ";;%s"%residualTitle)
	resPad.SetGridx()
	resPad.SetGridy()
	

	zeroLine = ROOT.TLine(theConfig.plotMinInv, 0.0, theConfig.plotMaxInv, 0.0)
	zeroLine.SetLineColor(ROOT.kBlue)
	zeroLine.SetLineWidth(2)
	zeroLine.Draw()
	if residualMode == "pull":
		### For pulls divided by data uncertainty (default in RooFit pulls)
		
		#~ residuals = frame.pullHist()
		
		###########
		
		### For pulls with division by prediction uncertainty
		curve = frame.findObject(curveName,ROOT.RooCurve.Class())
		if curve == None:
			print "Curve not found"		
		
		datahist = frame.findObject(histName,ROOT.RooHist.Class())
  		
  		### Somehow the histogram is not plotted if I use a TGraphAsymmError or new RooHist
  		### But it works if I fetch the default pull histogram and update the values
  		### No clue why this is the case
		residuals = frame.pullHist()
		
		xstart,xstop,y = ROOT.Double(0.),ROOT.Double(0.),ROOT.Double(0.)
		curve.GetPoint(0,xstart,y)
		curve.GetPoint(curve.GetN()-1,xstop,y)
		
		chiSquare = 0.
		for i in range(0,datahist.GetN()-1):
			x,point = ROOT.Double(0.),ROOT.Double(0.)
			datahist.GetPoint(i,x,point)
			if x<xstart or x>xstop:
				continue
				
			yy = ROOT.Double(0.)
			yy = point - curve.interpolate(x)
			norm = math.sqrt(curve.interpolate(x))			
			errLow = datahist.GetErrorYlow(i)
			errHigh = datahist.GetErrorYhigh(i)
			
			if errLow > 0:
				if yy/errLow > -3.5:  ### Exclude a few bins with weird (downward) fluctuations that yield values of yy/err up to -8
					chiSquare = chiSquare + (yy/errLow)**2
					#~ print x
					#~ print yy/errLow
			
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
			
		parametersToSave["chi2SFOSTemp"] = chiSquare
		print chiSquare
		
		###########
		
	else:
		residuals = frame.residHist()

	residuals.Draw("P")
	#~ residuals.Print()
	hAxis.GetYaxis().SetNdivisions(4, 2, 5)
	hAxis.GetYaxis().CenterTitle()
	hAxis.SetTitleOffset(0.32, "Y")
	hAxis.SetTitleSize(0.17, "Y")
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
	parser.add_argument("-s", "--selection", dest = "selection" , action="store", default="SignalHighMT2DeltaPhiJetMet",
						  help="selection which to apply.")
	parser.add_argument("-r", "--runRange", dest="runRange", action="store", default="Run2016_36fb",
						  help="name of run range.")
	parser.add_argument("-b", "--backgroundShape", dest="backgroundShape", action="store", default="CB",
						  help="background shape, default CB")
	parser.add_argument("-e", "--edgeShape", dest="edgeShape", action="store", default="Triangle",
						  help="edge shape, default Triangle")
	### Removed the possibility to split in central and forward to reduce
	### the amount of code. Has not been used for ages anyway
	#~ parser.add_argument("-c", "--configuration", dest="config", action="store", default="Inclusive",
						  #~ help="dataset configuration, default Inclusive")
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
	runName =args.runRange
	produceScan = args.likelihoodScan
	useExistingDataset = args.useExisting
		
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region,backgroundShape,signalShape,runName,args.mc,args.toys,args.addSignal)
	
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
	
	if not args.verbose:
		ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)  
		ROOT.RooMsgService.instance().setSilentMode(ROOT.kTRUE)


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
			(treeOFOS, treeEE, treeMM) = tools.getTrees(theConfig, datasets)
		else:
			treeOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.dataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)

			# convert trees
			treeOFOS = dataInterface.DataInterface.convertDileptonTree(treeOFOSraw)
			treeEE = dataInterface.DataInterface.convertDileptonTree(treeEEraw)
			treeMM = dataInterface.DataInterface.convertDileptonTree(treeMMraw)
			
		if (theConfig.addDataset != None):
			xsection = 0.0
			nTotal = 1.0
			scale = xsection * theConfig.runRange.lumi / nTotal
			
			denominatorFile = TFile("../SignalScan/T6bbllsleptonDenominatorHisto7.root")
			denominatorHisto = TH2F(denominatorFile.Get("massScan"))
			
			
			denominator = denominatorHisto.GetBinContent(denominatorHisto.GetXaxis().FindBin(int(theConfig.addDataset.split("_")[1])),denominatorHisto.GetYaxis().FindBin(int(theConfig.addDataset.split("_")[2])))


			# dynamic scaling
			jobs = dataInterface.InfoHolder.theDataSamples[theConfig.dataVersion][theConfig.addDataset]
			if (len(jobs) > 1):
				log.logError("Scaling of added MC samples not implemented. MC yield is wrong!")
			for job in jobs:
				dynNTotal = theDataInterface.getEventCount(job, theConfig.flag, theConfig.task)
				dynXsection = theDataInterface.getCrossSection(job)
				#~ dynScale = dynXsection * theConfig.runRange.lumi / dynNTotal
				dynScale = dynXsection * theConfig.runRange.lumi / denominator
				print dynXsection
				print dynNTotal
				scale = dynScale


			log.logHighlighted("Scaling added dataset (%s) with %f (dynamic)" % (theConfig.addDataset, scale))
			
			treeAddOFOSraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathOFOS, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeAddEEraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathEE, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)
			treeAddMMraw = theDataInterface.getTreeFromDataset(theConfig.flag, theConfig.task, theConfig.addDataset, treePathMM, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut)

			# convert trees
			treeAddOFOS = dataInterface.DataInterface.convertDileptonTree(treeAddOFOSraw, weight=scale)
			treeAddEE = dataInterface.DataInterface.convertDileptonTree(treeAddEEraw, weight=scale)
			treeAddMM = dataInterface.DataInterface.convertDileptonTree(treeAddMMraw, weight=scale)
	

		trees = {"EE":treeEE,"MM":treeMM,"OFOS":treeOFOS}
		addTrees = {}
		
		if theConfig.addDataset != None:
			addTrees = {"EE":treeAddEE,"MM":treeAddMM,"OFOS":treeAddOFOS}
		
		weight = ROOT.RooRealVar("weight","weight",1.,-100.,10.)
		inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
		
		typeName = "data"
		dataSets = prepareDatasets(inv,weight,trees,addTrees,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.inclusive.val,theConfig.rSFOF.inclusive.err,theConfig.addDataset,theConfig)
		
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
			dataOFOS = dataSets[index]["OFOS"].Clone("dataOFOS")
			dataSFOS = dataSets[index]["SFOS"].Clone("dataSFOS")
			
			getattr(w, 'import')(dataEE, ROOT.RooCmdArg())
			getattr(w, 'import')(dataMM, ROOT.RooCmdArg())
			getattr(w, 'import')(dataOFOS, ROOT.RooCmdArg())
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
			#~ w.Print()			
			
			if len(theConfig.signalDataSets) > 0:
				(treeOFOSSignal, treeEESignal, treeMMSignal) = tools.getTrees(theConfig, theConfig.signalDataSets)
				
				signalTrees = {"EE":treeEESignal,"MM":treeMMSignal,"OFOS":treeOFOSSignal}
				addSignalTrees = {}
										
				typeName = "signal"
				dataSets = prepareDatasets(w.var("inv"),w.var('weight'),signalTrees,addSignalTrees,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.inclusive.val,theConfig.rSFOF.inclusive.err,False,theConfig)
				
				w.data("dataEE").append(dataSets[index]["EE"].Clone("signalEE"))
				w.data("dataMM").append(dataSets[index]["MM"].Clone("signalMM"))
				w.data("dataOFOS").append(dataSets[index]["OFOS"].Clone("signalOFOS"))
				w.data("dataSFOS").append(dataSets[index]["SFOS"].Clone("signalSFOS"))
					
		vars = ROOT.RooArgSet(w.var('inv'), w.var('weight'))
		selectShapes(w,theConfig.backgroundShape,theConfig.signalShape,theConfig.nBinsMinv)
		


		#~ print w.data("dataSFOS").sumEntries(), w.data("dataOFOS").sumEntries()
	
		# deduce proper values for yield parameters from datasets and create yield parameters
		
		predictedSignalYield = w.data("dataSFOS").sumEntries() - 0.8*w.data("dataSFOS").sumEntries()
		if theConfig.allowNegSignal:
			w.factory("nSig[%f,%f,%f]" % (0.,-2*predictedSignalYield, 2*predictedSignalYield))
		else:
			w.factory("nSig[%f,%f,%f]" % (0.,0, 2*predictedSignalYield))	
		w.var('nSig').setAttribute("StoreAsymError")


		maxZ = w.data("dataSFOS").sumEntries("abs(inv-91.2) < 20")
				
		#~ w.factory("nZ[%f,0.,%f]" % (theConfig.zPredictions.MT2.SF.inclusive.val,maxZ))
		w.factory("nZ[%f,0.,%f]" % (0.2*maxZ,maxZ))
		
		nBMin = w.data("dataOFOS").sumEntries()*0
		nBMax= w.data("dataSFOS").sumEntries()*2
		nBStart = w.data("dataOFOS").sumEntries()*0.7	
		
		w.factory("nB[%f,%f,%f]" % (nBStart,nBMin,nBMax))
		w.var('nB').setAttribute("StoreAsymError")

		#create background only shapes
			
		w.factory("SUM::ofosShape(nB*ofosShape1)")
		
		# fit background only shapes to OFOS dataset
		#~ w.Print()
		fitOFOS = w.pdf('ofosShape').fitTo(w.data("dataOFOS"), ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE),ROOT.RooFit.Minos(theConfig.runMinos),ROOT.RooFit.Extended(ROOT.kTRUE),ROOT.RooFit.Strategy(1))
		
		#~ fitOFOS.Print()
		
		log.logWarning("OFOS Fit Convergence Quality: %d"%fitOFOS.covQual())
		
		
		parametersToSave["minNllOFOS"] = fitOFOS.minNll()

		parametersToSave["nParOFOS"] = fitOFOS.floatParsFinal().getSize()	

		frameOFOS = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of OFOS lepton pairs'))
		frameOFOS.GetXaxis().SetTitle('m_{e#mu} [GeV]')
		frameOFOS.GetYaxis().SetTitle(theConfig.histoytitle)
		
		ROOT.RooAbsData.plotOn(w.data("dataOFOS"), frameOFOS)
		w.pdf('ofosShape').plotOn(frameOFOS)		

		w.pdf('ofosShape').plotOn(frameOFOS,ROOT.RooFit.LineWidth(2))
		w.pdf('ofosShape').plotOn(frameOFOS)
		ROOT.RooAbsData.plotOn(w.data("dataOFOS"), frameOFOS)

		parametersToSave["chi2OFOS"] = frameOFOS.chiSquare(parametersToSave["nParOFOS"])
		parametersToSave["chi2ProbOFOS"] = TMath.Prob(parametersToSave["chi2OFOS"]*(theConfig.nBinsMinv-parametersToSave["nParOFOS"]),(theConfig.nBinsMinv-parametersToSave["nParOFOS"]))
		#~ log.logDebug("Chi2 OFOS: %f" % parametersToSave["chi2OFOS"])	
		#~ log.logDebug("Free Parameters OFOS: %f" % (theConfig.nBinsMinv-parametersToSave["nParOFOS"]))	
		#~ log.logDebug("Chi2 Probability OFOS: %f" %parametersToSave["chi2ProbOFOS"])
		
		# Fit SFOS distribution

		if theConfig.useMC and theConfig.toyConfig["nToys"] == 0:
			w.factory("rSFOF[%f,%f,%f]" % (theConfig.rSFOF.inclusive.valMC, theConfig.rSFOF.inclusive.valMC - 4*theConfig.rSFOF.inclusive.errMC, theConfig.rSFOF.inclusive.valMC + 4*theConfig.rSFOF.inclusive.errMC))
			w.factory("rSFOFMeasured[%f]" % (theConfig.rSFOF.inclusive.valMC))
			w.factory("rSFOFMeasuredErr[%f]" % (theConfig.rSFOF.inclusive.errMC))
		else:
			w.factory("rSFOF[%f,%f,%f]" % (theConfig.rSFOF.inclusive.val, theConfig.rSFOF.inclusive.val - 4*theConfig.rSFOF.inclusive.err, theConfig.rSFOF.inclusive.val + 4*theConfig.rSFOF.inclusive.err))
			w.factory("rSFOFMeasured[%f]" % (theConfig.rSFOF.inclusive.val))
			w.factory("rSFOFMeasuredErr[%f]" % (theConfig.rSFOF.inclusive.err))
			
		w.factory("fee[0.5,0.,1.]")
		w.factory("Gaussian::constraintRSFOF(rSFOF,rSFOFMeasured,rSFOFMeasuredErr)")

		nSigEE = ROOT.RooFormulaVar('nSigEE', '@0*@1', ROOT.RooArgList(w.var('fee'), w.var('nSig')))
		getattr(w, 'import')(nSigEE, ROOT.RooCmdArg())
		nSigMM = ROOT.RooFormulaVar('nSigMM', '(1-@0)*@1', ROOT.RooArgList(w.var('fee'), w.var('nSig')))
		getattr(w, 'import')(nSigMM, ROOT.RooCmdArg())			
		nZEE = ROOT.RooFormulaVar('nZEE', '@0*@1', ROOT.RooArgList(w.var('fee'), w.var('nZ')))
		getattr(w, 'import')(nZEE, ROOT.RooCmdArg())
		nZMM = ROOT.RooFormulaVar('nZMM', '(1-@0)*@1', ROOT.RooArgList(w.var('fee'), w.var('nZ')))
		getattr(w, 'import')(nZMM, ROOT.RooCmdArg())
		nBEE = ROOT.RooFormulaVar('nBEE', '@0*@1*@2', ROOT.RooArgList(w.var('fee'),w.var('rSFOF'), w.var('nB')))
		getattr(w, 'import')(nBEE, ROOT.RooCmdArg())
		nBMM = ROOT.RooFormulaVar('nBMM', '(1-@0)*@1*@2', ROOT.RooArgList(w.var('fee'),w.var('rSFOF'), w.var('nB')))
		getattr(w, 'import')(nBMM, ROOT.RooCmdArg())	
		constraints = ROOT.RooArgSet(w.pdf("constraintRSFOF"))			
		
		w.factory("SUM::zShape(nZEE*zEEShape,nZMM*zMMShape)")	
		w.factory("Voigtian::zShapeSeparately(inv,zmean,zwidth,s)")			

		w.factory("SUM::model(nSig*sfosShape, nB*ofosShape, nZ*zShape)")
		w.factory("SUM::mEE(nSigEE*eeShape, nBEE*ofosShape, nZEE*zEEShape)")
		w.factory("SUM::mMM(nSigMM*mmShape, nBMM*ofosShape, nZMM*zMMShape)")
		
		
		w.factory("PROD::constraintMEE(mEE, constraintRSFOF)")
		w.factory("PROD::constraintMMM(mMM, constraintRSFOF)")
		
		w.factory("SUM::modelBgOnly( nB*ofosShape, nZ*zShape)")
		w.factory("SUM::mEEBgOnly( nBEE*ofosShape, nZEE*zEEShape)")
		w.factory("SUM::mMMBgOnly( nBMM*ofosShape, nZMM*zMMShape)")
		
		w.factory("PROD::constraintMEEBgOnly( mEEBgOnly, constraintRSFOF)")
		w.factory("PROD::constraintMMMBgOnly( mMMBgOnly, constraintRSFOF)")			
					
		w.factory("SIMUL::combModelBgOnly(cat[EE=0,MM=1,OFOS=2], EE=mEEBgOnly, MM=mMMBgOnly, OFOS=ofosShape)")
		# real model
		
		w.factory("SIMUL::combModel(cat[EE=0,MM=1,OFOS=2], EE=mEE, MM=mMM, OFOS=ofosShape)")
		
		w.factory("SIMUL::constraintCombModelBgOnly(cat[EE=0,MM=1,OFOS=2], EE=constraintMEEBgOnly, MM=constraintMMMBgOnly, OFOS=ofosShape)")
		# real model
		
		w.factory("SIMUL::constraintCombModel(cat[EE=0,MM=1,OFOS=2], EE=constraintMEE, MM=constraintMMM, OFOS=ofosShape)")		
				
			
		data_obs = ROOT.RooDataSet("data_obs", "combined data", vars, ROOT.RooFit.Index(w.cat('cat')),
								   ROOT.RooFit.WeightVar('weight'),
								   ROOT.RooFit.Import('OFOS', w.data("dataOFOS")),
								   ROOT.RooFit.Import('EE', w.data("dataEE")),
								   ROOT.RooFit.Import('MM', w.data("dataMM")))
		getattr(w, 'import')(data_obs, ROOT.RooCmdArg())
		
						
		log.logWarning("Attempting background only Fit!")
		
		bgOnlyFit = w.pdf('combModelBgOnly').fitTo(w.data('data_obs'),
											ROOT.RooFit.Save(),
											ROOT.RooFit.SumW2Error(ROOT.kFALSE),
											ROOT.RooFit.Minos(theConfig.runMinos),
											ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet(w.pdf("constraintRSFOF"))),
											ROOT.RooFit.Extended(ROOT.kTRUE),
											ROOT.RooFit.Strategy(1))
											
		fitResult = bgOnlyFit.covQual()
		#~ log.logHighlighted("NUMBER OF FS BG EVENTS")
		log.logHighlighted(str(w.var('nB').getVal()))
		log.logHighlighted(str(w.var('nB').getError()))
		log.logHighlighted(str(w.var('nZ').getVal()))
		log.logHighlighted(str(w.var('nZ').getError()))
		log.logHighlighted(str(w.var('rSFOF').getVal()))
		log.logHighlighted(str(w.var('rSFOF').getError()))
		parametersToSave["minNllH0"] = bgOnlyFit.minNll()
		parametersToSave["nParH0"] = bgOnlyFit.floatParsFinal().getSize()
		
		log.logHighlighted("Background Only Fit Convergence Quality: %d"%fitResult)

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")		
		

		w.var('inv').setBins(theConfig.nBinsMinv)
		
		frameSFOS = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
		#~ frameSFOS = plotModel(w, w.data("dataSFOS"), fitOFOS, theConfig, pdf="model", tag="%sSFOS" % theConfig.title, frame=frameSFOS, zPrediction=theConfig.zPredictions.MT2.SF.inclusive.val,H0=True)
		frameSFOS = plotModel(w, w.data("dataSFOS"), fitOFOS, theConfig, pdf="model", tag="%sSFOS" % theConfig.title, frame=frameSFOS, zPrediction=0.5*maxZ,H0=True)
		frameSFOS.GetYaxis().SetTitle(theConfig.histoytitle)
		
		plotFitResults(w,theConfig, frameSFOS,frameOFOS,data_obs,fitOFOS,H0=True)		

					   
		w.var("rSFOF").setVal(theConfig.rSFOF.inclusive.val)
		if (theConfig.edgePosition > 0):
			w.var('m0').setVal(float(theConfig.edgePosition))
			if not x == None:
				w.var('m0').setVal(float(theConfig.toyConfig["m0"]))
				if theConfig.toyConfig["rand"]:

					
					### Do not use too low initial values otherwise the fit might
					### get stuck in a local minimum of that is only a fluctuation
					### in a very small range
					randomm0 = 35+random.random()*465
					log.logWarning("Warning! Randomized initial value of m0 = %.1f"%randomm0)

					w.var('m0').setVal(float(randomm0))					
			if (theConfig.fixEdge):
				w.var('m0').setConstant(ROOT.kTRUE)
			else:
				log.logWarning("Edge endpoint floating!")	

						
		hasConverged = False
		log.logWarning("Attempting combined Fit!")
		
		if theConfig.useMC:
			w.writeToFile("workspaces/tempWorkSpace_%s_MC_%s.root"%(theConfig.selection.name,theConfig.backgroundShape))		
		else:
			w.writeToFile("workspaces/tempWorkSpace_%s_Data_%s.root"%(theConfig.selection.name,theConfig.backgroundShape))		
		
		signalFit = w.pdf('combModel').fitTo(w.data('data_obs'),
											ROOT.RooFit.Save(),
											ROOT.RooFit.SumW2Error(ROOT.kFALSE),
											ROOT.RooFit.Minos(theConfig.runMinos),
											ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet(w.pdf("constraintRSFOF"))),
											ROOT.RooFit.Extended(ROOT.kTRUE),
											ROOT.RooFit.Strategy(1))
											
		
		fitResult = signalFit.covQual()
		parametersToSave["minNllH1"] = signalFit.minNll()
		parametersToSave["nParH1"] = signalFit.floatParsFinal().getSize()
		parametersToSave["initialM0"] = theConfig.edgePosition
		if theConfig.toyConfig["nToys"] > 0 and theConfig.toyConfig["rand"]:
			parametersToSave["initialM0"] = randomm0
		log.logHighlighted("Main Fit Convergence Quality: %d"%fitResult)

		if fitResult == 3:
			hasConverged = True
			log.logHighlighted("Fit converged, congrats!")
		else:
				log.logError("Fit did not converge! Do not trust this result!")

		sizeCanvas = 800

		
		frameSFOS = w.var('inv').frame(ROOT.RooFit.Title('Invariant mass of SFOS lepton pairs'))
		#~ frameSFOS = plotModel(w, w.data("dataSFOS"), fitOFOS, theConfig, pdf="model", tag="%sSFOS" % theConfig.title, frame=frameSFOS, zPrediction=theConfig.zPredictions.MT2.SF.inclusive.val)
		frameSFOS = plotModel(w, w.data("dataSFOS"), fitOFOS, theConfig, pdf="model", tag="%sSFOS" % theConfig.title, frame=frameSFOS, zPrediction=0.5*maxZ)
		frameSFOS.GetYaxis().SetTitle(theConfig.histoytitle)
		
		### The Histograms with MC have a large content in the overflow bin, which screws up the default chi2 calculation
		### Therefore we calculate it ourself when the pull plots are created
		if theConfig.useMC:
			parametersToSave["chi2SFOS"] = parametersToSave["chi2SFOSTemp"]/(theConfig.nBinsMinv-int(parametersToSave["nParH1"]))
		else:	
			parametersToSave["chi2SFOS"] = frameSFOS.chiSquare(int(parametersToSave["nParH1"]))
		parametersToSave["chi2ProbSFOS"] = TMath.Prob(parametersToSave["chi2SFOS"]*(theConfig.nBinsMinv-int(parametersToSave["nParH1"])),theConfig.nBinsMinv-int(parametersToSave["nParH1"]))
		log.logDebug("Chi2 SFOS: %f" % parametersToSave["chi2SFOS"])
		
		log.logDebug("Free parameters SFOS: %f" % (theConfig.nBinsMinv-int(parametersToSave["nParH1"])))	
		
		log.logDebug("Chi2 Probability SFOS: %f" %parametersToSave["chi2ProbSFOS"])
		
		plotFitResults(w,theConfig, frameSFOS,frameOFOS,data_obs,fitOFOS)	
		

		saveFitResults(w,theConfig,x)	
		
		if theConfig.useMC:
			w.writeToFile("workspaces/outputWorkSpace_%s_MC.root"%theConfig.selection.name)		
		else:
			w.writeToFile("workspaces/outputWorkSpace_%s_Data.root"%theConfig.selection.name)		
		
			
			
	

main()
