import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)
print sys.path
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
import argparse 


def main():
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
    
    parser = argparse.ArgumentParser(description='edge fitter reloaded.')
        
    parser.add_argument("-i", "--input", action="store", dest="input", default="",
                                              help="Input workspace")
    
    parser.add_argument("-o", "--output", action="store", dest="output", default="",
                                              help="Output filename")
    
    
                                    
    args = parser.parse_args()     
    filename = args.input
    fitSignal = 1
    fitName = args.output
    CreateProfile = 1
    # UseMinos = True
    UseMinos = False
    ProfilePrecision=0.05
    print "Have been provided with argument "+ filename
    
    fin = ROOT.TFile(filename)
    wa = fin.Get("w")
    
    ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)
    ROOT.RooMsgService.instance().setSilentMode(ROOT.kTRUE)

    
    mll = wa.var("mll")
    mlledge = wa.var("m0")
    NsignalSignal = wa.var("nSig")
    combData = wa.data("data_obs")
    simPdf = wa.pdf("combModel")   
    if (fitSignal):
        simPdf = wa.pdf("combModel")
    else: 
        simPdf = wa.pdf("combModelBgOnly")
        
    R_SF_OF = wa.var("rSFOF")
    
    sample = wa.cat("cat")

    constrainingR_SF_OF = wa.pdf("constraintRSFOF")
   
    nattempts=0
    HasConverged=False
    #vector<int> CovStatus;
    print "Current status (addresses : ) " 
    print "simPdf : ", simPdf
    print "combData : ",combData 
    print "constraint (RSFOF): ", constrainingR_SF_OF 
    print "N(events) in dataset, unweighted : ",combData.numEntries()
    CovStatus = []
    while(nattempts<5 and  not HasConverged):
        constArgs = ROOT.RooArgSet(constrainingR_SF_OF)
        result = simPdf.fitTo(combData,ROOT.RooFit.Save(),ROOT.RooFit.Extended(),ROOT.RooFit.Minos(UseMinos),ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet(constArgs)),ROOT.RooFit.NumCPU(1))

        if(result.covQual()==3): 
            HasConverged=True;
        else: 
            print "Unsuccesful, will try again"
        nattempts+=1
        CovStatus.append(result.covQual())

    
    result.Print("v")    
    getattr(wa, 'import')(result)
    
    if (fitSignal):
        minNllH1 = ROOT.RooRealVar("minNllH1", "-log L of fit with signal model", result.minNll(), result.minNll() , result.minNll())
        getattr(wa, 'import')(minNllH1)
        nParH1 = ROOT.RooRealVar("nParSFOSH1", "number of free parameters", result.floatParsFinal().getSize(), result.floatParsFinal().getSize() , result.floatParsFinal().getSize())
        getattr(wa, 'import')(nParH1)
        fitQuality = ROOT.RooRealVar("fitQualityH1", "Quality of fit", result.covQual(), result.covQual() , result.covQual())
        getattr(wa, 'import')(fitQuality) 
    else:
        minNllH0 = ROOT.RooRealVar("minNllH0", "-log L of fit without signal model", result.minNll(), result.minNll() , result.minNll())
        getattr(wa, 'import')(minNllH0) 
        nParH0 = ROOT.RooRealVar("nParSFOSH0", "number of free parameters", result.floatParsFinal().getSize(), result.floatParsFinal().getSize() , result.floatParsFinal().getSize())
        getattr(wa, 'import')(nParH0)
        fitQuality = ROOT.RooRealVar("fitQualityH0", "Quality of fit", result.covQual(), result.covQual() , result.covQual())
        getattr(wa, 'import')(fitQuality)             
         
    print "Result has been stored, printing it here for completeness' sake"
    result.Print("v")
    
    print "Note that it took ", nattempts," attempts to reach a result with decent error matrix"
    for i, cov in enumerate(CovStatus):
        print "Attempt", i,":", cov
        
    if(CreateProfile and not (mlledge.isConstant()) ):
        constArgs = ROOT.RooArgSet(constrainingR_SF_OF)
        NewNll = simPdf.createNLL(combData,ROOT.RooFit.ExternalConstraints(constArgs),ROOT.RooFit.NumCPU(4),ROOT.RooFit.Extended())
        NewNll.SetName("NewNll")
        NewNll.SetTitle("NewNll")
        
        frameNOne = mlledge.frame(ROOT.RooFit.Range(30,320),ROOT.RooFit.Precision(ProfilePrecision))
        NewNll.plotOn(frameNOne,ROOT.RooFit.LineColor(ROOT.kRed),ROOT.RooFit.NumCPU(4))
        nllWithPenalty = ROOT.RooFormulaVar("nllWithPenalty","2*NewNll",ROOT.RooArgList(NewNll)) 
        
        mlledgearg = ROOT.RooArgSet(mlledge)
        nllarg = ROOT.RooArgSet(NewNll)
        pll_mlledge = NewNll.createProfile(mlledgearg)
        pll_mlledge.addOwnedComponents(nllarg)
        
        
        frameNE = mlledge.frame(ROOT.RooFit.Range(30,320),ROOT.RooFit.Precision(ProfilePrecision),ROOT.RooFit.Title("-log(L) scan vs m_{ll}^{max}"))
        pll_mlledge.plotOn(frameNE,ROOT.RooFit.EvalErrorValue(-1),ROOT.RooFit.Precision(ProfilePrecision),ROOT.RooFit.Name("Profile"),ROOT.RooFit.NumCPU(8))
        
        getattr(wa, 'import')(frameNE)
        getattr(wa, 'import')(NewNll)
        can = ROOT.TCanvas() 
        can.Divide(2,1)
        can.cd(1)
        frameNOne.Draw()
        can.cd(2)
        frameNE.Draw()
        
        # li = ROOT.TLine(100,0.5,320,0.5)
        # li.Draw("same")
        
        can.SaveAs(("likelihoodScans/"+fitName+"_ProfileLikelihood.pdf"))
        can.SaveAs(("likelihoodScans/"+fitName+"_ProfileLikelihood.C"))
        can.SaveAs(("likelihoodScans/"+fitName+"_ProfileLikelihood.root"))
            
    #wa.writeToFile(filename+"_result")
    
if __name__ == "__main__":
    main()
