import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import ROOT
from ROOT import gROOT, gStyle
from setTDRStyle import setTDRStyle

from messageLogger import messageLogger as log
import dataInterface




def prepareDatasets(inv,weight,trees,addTrees,maxInv,minInv,typeName,nBinsMinv,rSFOF,rSFOFErr,addDataset,theConfig):


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
		log.logHighlighted("Preparing to dice %d Toys"%Holder.nToys)
		rand = ROOT.TRandom3()
		rand.SetSeed(0)
		
		wToys = ROOT.RooWorkspace("w", ROOT.kTRUE)
		wToys.factory("inv[%s,%s,%s]" % ((maxInv - minInv) / 2, minInv, maxInv))
		wToys.var('inv').setBins(nBinsMinv)
		wToys.factory("weight[1.,0.,10.]")
		inv = ROOT.RooRealVar("inv","inv",(maxInv - minInv) / 2,minInv,maxInv)
		#~ inv.setRange("Low",minInv,70)
		#~ inv.setRange("High",100,maxInv)
		#~ rangeString_ = "Low,High"
		vars = ROOT.RooArgSet(inv, wToys.var('weight'))
		Holder.vars = vars
		
		selectShapes(wToys,Holder.histSubtraction,Holder.shape,ratioMuE,nBinsMinv)	

		getattr(wToys, 'import')(dataEE)
		getattr(wToys, 'import')(dataMM)
		getattr(wToys, 'import')(dataSFOS)
		getattr(wToys, 'import')(dataOFOS)	
		
		if Holder.histSubtraction:
				log.logHighlighted("HistSubtraction activated!")

				if (Holder.histSmoothing):
					log.logHighlighted("Smoothing HistSubtraction shape")
					nameDataOFOS = "%sOFOS" % (typeName)
					wToys.factory("RooKeysPdf::ofosShape1(inv, %s, MirrorBoth)" % (nameDataOFOS))
				else:
					wToys.var('inv').setBins(Holder.histBinning)
					tempDataHist = ROOT.RooDataHist("dataHistOFOS", "dataHistOFOS", ROOT.RooArgSet(wToys.var('inv')), dataOFOS)
					wToys.var('inv').setBins(nBinsMinv)
					getattr(wToys, 'import')(tempDataHist)
					Abkg=ROOT.RooRealVar("Abkg","Abkg",1,0.01,10)
					wToys.factory("RooHistPdf::ofosShape1(inv, dataHistOFOS)")
					getattr(wToys, 'import')(Abkg)
					
		wToys.factory("SUM::ofosShape(nB[100,0,100000]*ofosShape1)")
		fitOFOS = wToys.pdf('ofosShape').fitTo(dataOFOS, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(ROOT.kFALSE))
		numOFOS = tmpOFOS.sumEntries()
		
		
		#~ tmpNumOFOS = float(rand.Poisson(numOFOS*Holder.scaleFactor))
		#~ tmpNumOFOS2 = float(rand.Poisson(numOFOS*Holder.scaleFactor))
		tmpNumOFOS = float(numOFOS*Holder.scaleFactor)
		tmpNumOFOS2 = float(numOFOS*Holder.scaleFactor)
		print "Signal OFOS %d"%tmpNumOFOS2
		print "Signal SFOS %d"%tmpNumOFOS
		frac1 = tmpNumOFOS/(tmpNumOFOS+predictions.zPrediction*Holder.scaleFactor+Holder.toySignalN*Holder.scaleFactor + predictions.offShellPrediction*Holder.scalefactor)
		frac2 = predictions.zPrediction*Holder.scaleFactor/(tmpNumOFOS+predictions.zPrediction*Holder.scaleFactor+Holder.toySignalN*Holder.scaleFactor + predictions.offShellPrediction*Holder.scalefactor)
		frac3 = predictions.offShellPrediction*Holder.scaleFactor/(tmpNumOFOS+predictions.zPrediction*Holder.scaleFactor+Holder.toySignalN*Holder.scaleFactor + predictions.offShellPrediction*Holder.scalefactor)
		signalFrac = Holder.toySignalN*Holder.scaleFactor * 1./(tmpNumOFOS+predictions.zPrediction*Holder.scaleFactor+Holder.toySignalN*Holder.scaleFactor + predictions.offShellPrediction*Holder.scalefactor)
		print frac1, frac2, frac3, signalFrac
		
		wToys.factory("frac1[%s,%s,%s]"%(frac1,frac1,frac1))
		wToys.var('frac1').setConstant(ROOT.kTRUE)		
		wToys.factory("frac2[%s,%s,%s]"%(frac2,frac2,frac2))
		wToys.var('frac2').setConstant(ROOT.kTRUE)	
		wToys.factory("frac3[%s,%s,%s]"%(frac3,frac3,frac3))
		wToys.var('frac3').setConstant(ROOT.kTRUE)	
		if Holder.toySignalN > 0:
			log.logHighlighted("Dicing %d Signal Events at %.1f GeV edge position"%(Holder.toySignalN,Holder.toySignalM0))
			wToys.factory("signalFrac[%(signalFrac)s,%(signalFrac)s,%(signalFrac)s]"%{"signalFrac":signalFrac})
			print wToys.var("signalFrac").getVal()
			wToys.var('signalFrac').setConstant(ROOT.kTRUE)
			wToys.var('m0').setVal(Holder.toySignalM0)
			if Holder.signalShape == "Concave":
				log.logHighlighted("Dicing concave signal shape")
				wToys.factory("SUSYX4Pdf::sfosShapeConcave(inv,const,s,m0)")
				wToys.factory("SUM::backtoymodelEE(frac1*ofosShape, frac2*zEEShape, frac3*offShell, signalFrac*sfosShapeConcave)")
				wToys.factory("SUM::backtoymodelMM(frac1*ofosShape, frac2*zMMShape, frac3*offShell,  signalFrac*sfosShapeConcave)")				
			elif Holder.signalShape == "Convex":
				log.logHighlighted("Dicing convex signal shape")
				wToys.factory("SUSYXM4Pdf::sfosShapeConvex(inv,const,s,m0)")				
				wToys.factory("SUM::backtoymodelEE(frac1*ofosShape, frac2*zEEShape, frac3*offShell, signalFrac*sfosShapeConvex)")
				wToys.factory("SUM::backtoymodelMM(frac1*ofosShape, frac2*zMMShape, frac3*offShell,  signalFrac*sfosShapeConvex)")				
			else:
				wToys.factory("SUM::backtoymodelEE(frac1*ofosShape, frac2*zEEShape, frac3*offShell, signalFrac*sfosShape)")
				wToys.factory("SUM::backtoymodelMM(frac1*ofosShape, frac2*zMMShape, frac3*offShell,  signalFrac*sfosShape)")
		else:
			wToys.factory("SUM::backtoymodelEE(frac1*ofosShape, frac3*offShell, frac2*zEEShape)")
			wToys.factory("SUM::backtoymodelMM(frac1*ofosShape, frac3*offShell, frac2*zMMShape)")						
			
		#~ wToys.factory("SIMUL::combModel(cat[EE=0,MM=1,OFOS=2], EE=backtoymodelEE, MM=backtoymodelMM, OFOS=ofosShape)")

		print wToys.factory('backtoymodel')

		if Holder.systShift == "Up":
			tmpRatioMuE = ratioMuE + ratioMuE*ratioMuEError
			tmpCorrection = 0.5*(tmpRatioMuE+1./tmpRatioMuE)*(ratioSFOFTrig+ratioSFOFTrigErr)
		elif Holder.systShift == "Down":
			tmpRatioMuE = ratioMuE - ratioMuE*ratioMuEError
			tmpCorrection = 0.5*(tmpRatioMuE+1./tmpRatioMuE)*(ratioSFOFTrig-ratioSFOFTrigErr)
		else:
			tmpRatioMuE = ratioMuE
			tmpCorrection = 0.5*(tmpRatioMuE+1./tmpRatioMuE)*(ratioSFOFTrig)
			
			

		eeFraction = 1./(1+tmpRatioMuE**2)
		mmFraction = tmpRatioMuE**2/(1+tmpRatioMuE**2)
		print "Signal eeFraction: %f"%(eeFraction)
		print "Signal mmFraction: %f"%(mmFraction)		
		genNumEE =  int(float(tmpNumOFOS*Holder.scaleFactor*tmpCorrection + Holder.toySignalN*Holder.scaleFactor)*eeFraction + predictions.zPrediction*Holder.scaleFactor*eeFraction)
		genNumMM = int(float(tmpNumOFOS*Holder.scaleFactor*tmpCorrection + Holder.toySignalN*Holder.scaleFactor)*mmFraction + predictions.zPrediction*Holder.scaleFactor*mmFraction)
		
		result = genToys2013(wToys,Holder.nToys,genNumEE,genNumMM,int(tmpNumOFOS))
		
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
	ws.factory("zmean[91.1876,89,95]")
	ws.var('zmean').setConstant(ROOT.kTRUE)
	ws.factory("zwidth[2.4952]")
	ws.factory("s[1.65,0.5,3.]")
	ws.var('s').setConstant(ROOT.kTRUE)
	ws.factory("sE[%f,%f,%f]" % (resElectron, resElectronMin, resElectronMax))
	ws.var('sE').setConstant(ROOT.kTRUE)
	ws.factory("sM[%f,%f,%f]" % (resMuon, resMuonMin, resMuonMax))
	ws.var('sM').setConstant(ROOT.kTRUE)


	cContinuumEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "expo")
	cContinuumMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "expo")
	cbMeanEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "cbMean")
	cbMeanMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "cbMean")
	nZEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nZ")
	nZMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nZ")
	zFractionEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "zFraction")
	zFractionMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "zFraction")
	nLEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nL")
	nLMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nL")
	nREECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "nR")
	nRMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "nR")
	alphaLEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "alphaL")
	alphaLMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "alphaL")
	alphaREECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "alphaR")
	alphaRMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "alphaR")
	sEECentral = tools.loadParameter("expofit", "dyExponent_Central_EE", "s")
	sMMCentral = tools.loadParameter("expofit", "dyExponent_Central_MM", "s")

	cContinuumEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "expo")
	cContinuumMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "expo")
	cbMeanEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "cbMean")
	cbMeanMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "cbMean")
	nZEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nZ")
	nZMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nZ")
	zFractionEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "zFraction")
	zFractionMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "zFraction")		
	nLEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nL")
	nLMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nL")
	nREEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "nR")
	nRMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "nR")
	alphaLEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "alphaL")
	alphaLMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "alphaL")
	alphaREEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "alphaR")
	alphaRMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "alphaR")
	sEEForward = tools.loadParameter("expofit", "dyExponent_Forward_EE", "s")
	sMMForward = tools.loadParameter("expofit", "dyExponent_Forward_MM", "s")
			
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


	
	
	#ws.var("inv").setBins(140,"cache")	




	ws.factory("m0[55., 20., 300.]")
	ws.var('m0').setAttribute("StoreAsymError")
	ws.factory("m0Show[45., 0., 300.]")
	#ws.factory("m0[75., 75., 75.]")
	ws.factory("const[45,20,100]")	

	if backgroundShape == 'L':
		log.logHighlighted("Using Landau")
		ws.factory("Landau::ofosShape1Central(inv,a1Central[30,0,100],b1Central[20,0,100])")
		ws.factory("Landau::ofosShape1Forward(inv,a1Forward[30,0,100],b1Forward[20,0,100])")
		
	elif backgroundShape == 'G':
		log.logHighlighted("Using old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.6.,0.,8.],a2Central[0.1,-1.,1.],b1Central[0.028,0.001,1.],b2Central[1.],c1Central[0.],c2Central[1.])") #trying to get rid of paramteres
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.6.,0.,8.],a2Forward[0.1,-1.,1.],b1Forward[0.028,0.001,1.],b2Forward[1.],c1Forward[0.],c2Forward[1.])") #trying to get rid of paramteres

	elif backgroundShape == 'O':
		log.logHighlighted("Using old old shape")
		ws.factory("SUSYBkgPdf::ofosShape1Central(inv,a1Central[1.0,0.,400.],a2Central[1.],b1Central[1,0.00001,100.],b2Central[1.])")
		ws.factory("SUSYBkgPdf::ofosShape1Forward(inv,a1Forward[1.0,0.0,400.],a2Forward[1.],b1Forward[1,0.00001,100.],b2Forward[1.])")	

	elif backgroundShape == 'MA':
		log.logHighlighted("Using Marco-Andreas shape")				
		ws.factory("SUSYBkgMAPdf::ofosShape1Central(inv,b1Central[-2000,-8000,8000],b2Central[120.,-800,800],b3Central[-1.,-5,5.],b4Central[0.01,0.0001,0.1], m1Central[50,30,80],m2Central[120,100,160])") #
		ws.factory("SUSYBkgMAPdf::ofosShape1Forward(inv,b1Forward[-3300,-5000,5000],b2Forward[120.,-800,800],b3Forward[-1.,-5,5.],b4Forward[0.01,0.0001,0.1], m1Forward[50,30,80],m2Forward[120,100,160])") #

	elif backgroundShape == 'Q':
		log.logHighlighted("Using Marco-Andreas shape for real")
		ws.factory("TopPairProductionSpline::ofosShape1Central(inv,b1Central[-1800,-8000,8000],b2Central[120.,-800,800],b4Central[0.01,0.0001,0.1], m1Central[50,30,80],m2Central[120,100,160])") #
		ws.factory("TopPairProductionSpline::ofosShape1Forward(inv,b1Forward[-1800,-5000,5000],b2Forward[120.,-400,400],b4Forward[0.01,0.0001,0.1], m1Forward[50,30,80],m2Forward[120,100,160])") #
			
	elif backgroundShape == 'P':
		log.logHighlighted("Gaussians activated!")
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Central(inv,a1Central[30.,0.,60.],a2Central[60.,20.,105.],a3Central[-100.,-150.,100.],b1Central[15,10.,80.],b2Central[20.,10.,80.],b3Central[200.,100.,300.])") #High MET
		ws.factory("SUSYBkgGaussiansPdf::ofosShape1Forward(inv,a1Forward[30.,0.,60.],a2Forward[60.,20.,105.],a3Forward[-100.,-150.,100.],b1Forward[15,10.,80.],b2Forward[20.,10.,80.],b3Forward[200.,100.,300.])") #High MET



	if signalShape == "Triangle":
		ws.factory("SUSYTPdf::sfosShape(inv,const,s,m0)")
		ws.factory("SUSYTPdf::sfosShapeShow(inv,const,s,m0Show)")
		ws.factory("SUSYTPdf::eeShape(inv,const,sE,m0)")
		ws.factory("SUSYTPdf::mmShape(inv,const,sM,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)
	elif signalShape == 'V' :
		ws.factory("Voigtian::sfosShape(inv,m0,zwidth,s)")
		ws.factory("Voigtian::eeShape(inv,m0,zwidth,sE)")
		ws.factory("Voigtian::mmShape(inv,m0,zwidth,sM)")
	elif signalShape == 'X4':
		ws.factory("SUSYX4Pdf::sfosShape(inv,const,s,m0)")
		ws.factory("SUSYX4Pdf::eeShape(inv,const,sE,m0)")
		ws.factory("SUSYX4Pdf::mmShape(inv,const,sM,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)
	elif signalShape == 'XM4' in Holder.shape:
		ws.factory("SUSYXM4Pdf::sfosShape(inv,const,s,m0)")
		ws.factory("SUSYXM4Pdf::eeShape(inv,const,sE,m0)")
		ws.factory("SUSYXM4Pdf::mmShape(inv,const,sM,m0)")
		ws.var('const').setConstant(ROOT.kTRUE)





def main():
	from sys import argv
	
	region = argv[1]
	backgroundShape = argv[2]
	signalShape = argv[3]
	runName = argv[4]
	
	from edgeConfig import edgeConfig
	theConfig = edgeConfig(region,backgroundShape,signalShape,runName)
	
	
	# init ROOT
	gROOT.Reset()
	gROOT.SetStyle("Plain")
	setTDRStyle()
	ROOT.gROOT.SetStyle("tdrStyle")	
	
	#set random random seed for RooFit, for toy generation
	ROOT.RooRandom.randomGenerator().SetSeed(0)
	


	# get data
	theDataInterface = dataInterface.DataInterface(theConfig.dataSetPath,theConfig.dataVersion)
	treeOFOS = None
	treeEE = None
	treeMM = None

	treePathOFOS = "/EMuDileptonTree"
	treePathEE = "/EEDileptonTree"
	treePathMM = "/MuMuDileptonTree"


	if (theConfig.useMC):
		log.logHighlighted("Using MC instead of data.")
		datasets = theConfig.mcdatasets # ["TTJets", "ZJets", "DibosonMadgraph", "SingleTop"]
		(treeOFOSCentral, treeEECentral, treeMMCentral) = getTrees(theConfig.flag, theConfig.task, datasets, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=True)
		(treeOFOSForward, treeEEForward, treeMMForward) = getTrees(theConfig.flag, theConfig.task, datasets, dataVersion=theConfig.dataVersion, cut=theConfig.selection.cut,central=False)
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

	log.logDebug("Starting edge fit")
	ROOT.gSystem.Load("shapes/RooSUSYTPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYX4Pdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYXM4Pdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYOldBkgPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgMAPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooSUSYBkgGaussiansPdf_cxx.so")
	ROOT.gSystem.Load("shapes/RooTopPairProductionSpline_cxx.so")
	ROOT.gSystem.Load("shapes/RooDoubleCB_cxx.so")
	ROOT.gSystem.Load("libFFTW.so") 		


	weight = ROOT.RooRealVar("weight","weight",1.,-100.,10.)
	inv = ROOT.RooRealVar("inv","inv",(theConfig.maxInv - theConfig.minInv) / 2,theConfig.minInv,theConfig.maxInv)
	
	
	typeName = "dataCentral"
	dataSetsCentral = prepareDatasets(inv,weight,treesCentral,addTreesCentral,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.central.value,theConfig.rSFOF.central.err,theConfig.addDataset,theConfig)
	typeName = "dataForward"
	dataSetsForward = prepareDatasets(inv,weight,treesForward,addTreesForward,theConfig.maxInv,theConfig.minInv,typeName,theConfig.nBinsMinv,theConfig.rSFOF.forward.value,theConfig.rSFOF.forward.err,theConfig.addDataset,theConfig)


	# silences all the info messages
	# 1 does not silence info messages, so 2 probably just suppresses these, but keeps the warnings
	#ROOT.RooMsgService.instance().Print()
	ROOT.RooMsgService.instance().setGlobalKillBelow(10)
	
	
	title = theConfig.selection.name+"_"+theConfig.runRange.name+"_"+theConfig.backgroundShape+theConfig.signalShape
	

	if theConfig.toyConfig["nToys"] > 0:
		title = "%s_Scale%sMo%sSignalN%s"%(title, theConfig.toyConfig["scale"], theConfig.toyConfig["m0"], theConfig.toyConfig["nSig"])

	if theConfig.fixEdge:
		title = title+"_FixedEdge_%.1f"%Holder.edgeHypothesis
	if theConfig.useMC:
		title = title+"_MC"
 	if theConfig.isSignal:
		title = title+"_SignalInjected"   	
	print Holder.title					
	titleSave = title				
	for index, dataSet in enumerate(dataSetsCentral):
		
		if theConfig.toyConfig["nToys"] > 0:
			x = "%x"%(random.random()*1e9)
			theConfig.figPath = "figToys/"
			title = titleSave 
			if theConfig.toyConfig["systShift"] == "Up" or theConfig.toyConfig["systShift"] == "Down":
				title = title + "_" + theConfig.toyConfig["systShift"]
			if theConfig.signalShape != "T":
				title = title + "_" + signalShape
			title = title + "_" + x
				
		else:
			x = None		

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
				
		# shape configuration
		selectShapes(w,Holder.histSubtraction,Holder.shape,ratioMuE,nBinsMinv)


		# Fit OFOS background
		if Holder.histSubtraction:
			log.logHighlighted("HistSubtraction activated!")

			if (Holder.histSmoothing):
				log.logHighlighted("Smoothing HistSubtraction shape")
				nameDataOFOSCentral = "dataOFOSCentral" 
				nameDataOFOSForward = "dataOFOSForward" 
				w.factory("RooKeysPdf::ofosShape1Central(inv, %s, MirrorBoth)" % (nameDataOFOSCentral))
				w.factory("RooKeysPdf::ofosShape1Forward(inv, %s, MirrorBoth)" % (nameDataOFOSForward))
			else:
				w.var('inv').setBins(theConfig.nBinsMinv)
				tempDataHistCentral = ROOT.RooDataHist("dataHistOFOSCentral", "dataHistOFOSCentral", ROOT.RooArgSet(w.var('inv')), dataOFOSCentral)
				getattr(w, 'import')(tempDataHistCentral)
				tempDataHistForward = ROOT.RooDataHist("dataHistOFOSForward", "dataHistOFOSForward", ROOT.RooArgSet(w.var('inv')), dataOFOSForward)
				getattr(w, 'import')(tempDataHistForward)
				w.factory("RooHistPdf::ofosShape1Central(inv, dataHistOFOSCentral)")
				w.factory("RooHistPdf::ofosShape1Forward(inv, dataHistOFOSForward)")
		print "Before the fit"


	

main()
