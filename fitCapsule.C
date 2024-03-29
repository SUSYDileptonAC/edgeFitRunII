#include <iostream>
#include "assert.h"
#include "TSystem.h"
#include "TFile.h"
#include "TColor.h"
#include "TCanvas.h"
#include "TAxis.h"

#include <RooRealVar.h>
#include <RooArgSet.h>
#include "RooWorkspace.h"
#include "RooCmdArg.h"
#include "RooWorkspace.h"
#include "RooAbsPdf.h"
#include "RooAddPdf.h"
#include "RooSimultaneous.h"
#include "RooGaussian.h"
#include "RooDataSet.h"
#include "RooPlot.h"
#include "RooAbsData.h"
#include "RooCategory.h"
#include "RooNLLVar.h"
#include "RooFitResult.h"


using namespace std;
using namespace RooFit;

// The routine is currently only used to make the profile plots of the log Likelhood vs mll
// Rest is older and might partially be removed. I never did so since I spotted this
// feature in Jans code quite recently and only used it to quickly produce some plots

// Use with options PROFILE and SIGNAL to make profile plots
// (so ./fitCapsule workspaces/*WORKSPACE_OF_INTEREST.root 1 1 OUTPUTNAME)

// The workspace has to be created before by the main fit (edgeFitter.py)

// Once this profile screwed up above 250 GeV of mll. Not sure what caused
// it, but when I changed the starting edge position in the config things were fine

// The output plot style is not too nice. Since it takes a bit to do the plots
// I fetch the second graph from the produced .C file and put it into the 
// (corresponding) fitProfileScanXX.py routine.
// If you use it more frequently you might want either to improve the output
// of this plot or store only the graph and not the full canvas. Since
// several things happen at once in the RooFit plotOn routine I am not sure how
// easy this is and never tried

int main(int argc, char** argv) {
    
    cout << "FitCapsule has been called. This capsule takes a file, extracts all the necessary information and carries out a fit (and a profile, if requested). " << endl;
    cout << "Note that the result is written back to the file " << endl;
    
    bool IllustrateResult=false;
    bool CreateProfile=true;
    bool fitSignal = false;
    bool UseMinos=true; // only deactivate this if you're debugging!
    bool useSumW2 = false;
    
    float ProfilePrecision=0.05;
    //~ float ProfilePrecision=1e0;
    
    cout << "Loading Libraries" << endl;
    //~ gSystem->Load("libRIO");
    gSystem->Load("shapes/RooSUSYTPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYX4Pdf_cxx.so");
    gSystem->Load("shapes/RooSUSYXM4Pdf_cxx.so");
    gSystem->Load("shapes/RooSUSYBkgPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYBkgBHPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYOldBkgPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYBkgMoreParamsPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYBkgMAPdf_cxx.so");
    gSystem->Load("shapes/RooSUSYBkgGaussiansPdf_cxx.so");
    gSystem->Load("shapes/RooTopPairProductionSpline_cxx.so");
    gSystem->Load("shapes/RooDoubleCB_cxx.so");
    //gSystem->Load("libFFTW.so");

    if(argc<5||argc>5) {
        cerr << " You need to provide three arguments: [FILE] [PROFILE] [SIGNAL] [NAME]" << endl;
        cerr << " FILE: The file where everything is stored (and the result will be written back to)" << endl;
        cerr << " PROFILE: 0 or 1, if you provide '1' a profile is generated and stored " << endl;
        cerr << " SIGNAL: 0 or 1, if you provide '1' a fit including the signal model is performed " << endl;
        cerr << " NAME: Name of the fit needed to save profiles" << endl;
    
        return -1;
    }
    string filename=argv[1];
    CreateProfile=atoi(argv[2]);
    fitSignal=atoi(argv[3]);
    string fitName = argv[4];
   
    cout << "Have been provided with argument " << filename << endl;
    
    
    TFile *fin = new TFile(filename.c_str());
    RooWorkspace *wa = (RooWorkspace*)fin->Get("transferSpace");
    if(!wa) wa = (RooWorkspace*)fin->Get("w");
    if(!wa) wa = (RooWorkspace*)fin->Get("wa");
    if(!wa) {
    cout << "Could not load w, wa, or transferSpace from file. Will print content and terminate" << endl;
    fin->ls();
    return -1;
    }

//    wa->Print();
//     wa->Print();
    //RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL);
    cout << "Loading variables " << filename << endl;
    RooRealVar *mll = (RooRealVar*)wa->var("mll");
    RooRealVar *mlledge = (RooRealVar*)wa->var("m0");
    RooRealVar *NsignalSignal = (RooRealVar*)wa->var("nSig");
    RooDataSet *combData = (RooDataSet*)wa->data("data_obs");
    RooSimultaneous *simPdf = (RooSimultaneous*)wa->pdf("combModel");    
     if (fitSignal) simPdf = (RooSimultaneous*)wa->pdf("combModel");
     else simPdf = (RooSimultaneous*)wa->pdf("combModelBgOnly");
    RooRealVar *R_SF_OF = (RooRealVar*)wa->var("rSFOF");
    
    
    RooCategory *sample = (RooCategory*)wa->cat("cat");

    RooGaussian *constrainingR_SF_OF = (RooGaussian*)wa->pdf("constraintRSFOF");
   
    RooFitResult *result;
    int nattempts=0;
    bool HasConverged=false;
    vector<int> CovStatus;
cout << "Current status (addresses : ) " << endl;
cout << "simPdf : " << simPdf << endl;
cout << "combData : " << combData << endl;
cout << "constraint (RSFOF): " << constrainingR_SF_OF << endl;
cout << "N(events) in dataset, unweighted : " << combData->numEntries() << endl;


    while(nattempts<5 && !HasConverged) {
         result = simPdf->fitTo(*combData,"1s",RooFit::Save(),RooFit::Extended(),RooFit::Minos(UseMinos),RooFit::ExternalConstraints(RooArgSet(*constrainingR_SF_OF)),RooFit::NumCPU(1));
//          result = simPdf->fitTo(*combData,"1s",RooFit::Save(),RooFit::Extended(),RooFit::Minos(UseMinos),RooFit::NumCPU(1),RooFit::SumW2Error(useSumW2));

        if(result->covQual()==3) HasConverged=true;
        else cout << "Unsuccesful, will try again" << endl;
    nattempts+=1;
        CovStatus.push_back(result->covQual());
    }
    
    result->Print("v");    
    wa->import(*result);


    if (fitSignal) {
        RooRealVar minNllH1("minNllH1", "-log L of fit with signal model", result->minNll(), result->minNll() , result->minNll());
        wa->import(minNllH1);
        RooRealVar nParH1("nParSFOSH1", "number of free parameters", result->floatParsFinal().getSize(), result->floatParsFinal().getSize() , result->floatParsFinal().getSize());
        wa->import(nParH1);
        RooRealVar fitQuality("fitQualityH1", "Quality of fit", result->covQual(), result->covQual() , result->covQual());
        wa->import(fitQuality); 
    }
    else {
        RooRealVar minNllH0("minNllH0", "-log L of fit without signal model", result->minNll(), result->minNll() , result->minNll());
        wa->import(minNllH0); 
        RooRealVar nParH0("nParSFOSH0", "number of free parameters", result->floatParsFinal().getSize(), result->floatParsFinal().getSize() , result->floatParsFinal().getSize());
        wa->import(nParH0);
        RooRealVar fitQuality("fitQualityH0", "Quality of fit", result->covQual(), result->covQual() , result->covQual());
        wa->import(fitQuality);             
            
    }
//     RooRealVar minNllH1("minNllH1", "-log L of fit with signal model", result->minNll(), result->minNll() , result->minNll());
    
//     wa->import(minNllH1);
    cout << "Result has been stored, printing it here for completeness' sake" << endl;
    result->Print("v");
    
    
    cout <<"Note that it took " << nattempts << " attempts to reach a result with decent error matrix" << endl;
    for(unsigned int i=0;i<CovStatus.size();i++) cout << "   Attempt " << i << " : " << CovStatus[i] << endl;
    
    
    if(IllustrateResult) {
        TCanvas *can = new TCanvas("can","can");
        can->Divide(2,2);
        can->cd(3);
        RooPlot *p1 = mll->frame();
        combData->plotOn(p1,RooFit::Name("OFdata"),RooFit::Cut("sample==sample::OF"));
        simPdf->plotOn(p1,RooFit::Slice(*sample,"OF"));
        simPdf->plotOn(p1,RooFit::Slice(*sample,"OF"),RooFit::ProjWData(*sample,*combData), RooFit::LineColor(kBlue));
        p1->Draw();
        
        can->cd(1);
        RooPlot *p2 = mll->frame();
        combData->plotOn(p2,RooFit::Name("eedata"),RooFit::Cut("sample==sample::ee"));
        simPdf->plotOn(p2,RooFit::Slice(*sample,"ee"));
        simPdf->plotOn(p2,RooFit::Slice(*sample,"ee"),RooFit::ProjWData(*sample,*combData), RooFit::LineColor(kBlue));
        p2->Draw();
        
        can->cd(2);
        RooPlot *p3 = mll->frame();
        combData->plotOn(p3,RooFit::Name("mmdata"),RooFit::Cut("sample==sample::mm"));
        simPdf->plotOn(p3,RooFit::Slice(*sample,"mm"));
        simPdf->plotOn(p3,RooFit::Slice(*sample,"mm"),RooFit::ProjWData(*sample,*combData), RooFit::LineColor(kBlue));
        p3->Draw();
        
        can->SaveAs("FitCapsuleResultIllustration.png");
    
        can->cd(4);
    RooNLLVar *NewNll = (RooNLLVar*) simPdf->createNLL(*combData,RooFit::ExternalConstraints(RooArgSet(*constrainingR_SF_OF)),RooFit::NumCPU(4));
    NewNll->SetName("NewNll");
    NewNll->SetTitle("NewNll");
    
    RooFormulaVar nllWithPenalty("nllWithPenalty","2*NewNll",RooArgList(*NewNll)) ;
    
    RooPlot* frameN = R_SF_OF->frame(RooFit::Range(1.08-2*0.05,1.08+2*0.05),RooFit::Title("-log(L) scan vs R(SF/OF)")) ;
    nllWithPenalty.plotOn(frameN,RooFit::PrintEvalErrors(-1),RooFit::ShiftToZero(),RooFit::Precision(1e-7)) ;
//  frameN->GetYaxis()->SetRangeUser(0,1);
    frameN->GetXaxis()->SetTitle("R(SF/OF)");
    frameN->GetXaxis()->CenterTitle();
    frameN->GetYaxis()->SetTitle("-2#Delta log(L)");
    frameN->GetYaxis()->CenterTitle();
    frameN->Draw();
    can->SaveAs("FitCapsuleResult_RSFOF.png");
    

    
    }
    
    
    if(CreateProfile && !(mlledge->isConstant()) ) { // pointless if mlledge is constant
        RooNLLVar *NewNll = (RooNLLVar*) simPdf->createNLL(*combData,RooFit::ExternalConstraints(RooArgSet(*constrainingR_SF_OF)),RooFit::NumCPU(4),RooFit::Extended());
        NewNll->SetName("NewNll");
        NewNll->SetTitle("NewNll");
        
        RooPlot *frameNOne = mlledge->frame(RooFit::Range(35,200),RooFit::Precision(ProfilePrecision));
    NewNll->plotOn(frameNOne,RooFit::LineColor(kRed),RooFit::NumCPU(4));
        RooFormulaVar nllWithPenalty("nllWithPenalty","2*NewNll",RooArgList(*NewNll)) ;
        
        RooAbsReal* pll_mlledge    = NewNll->createProfile(*mlledge);
        pll_mlledge->addOwnedComponents(*NewNll);
        
        
        RooPlot* frameNE = mlledge->frame(RooFit::Range(35,300),RooFit::Precision(ProfilePrecision),RooFit::Title("-log(L) scan vs m_{ll}^{max}"));
        pll_mlledge->plotOn(frameNE,RooFit::EvalErrorValue(-1),RooFit::Precision(ProfilePrecision),RooFit::Name("Profile"),RooFit::NumCPU(4));
        
//        wa->import(*pll_mlledge);
        wa->import(*frameNE);
        wa->import(*NewNll);
TCanvas *can = new TCanvas(); can->Divide(2,1);can->cd(1);frameNOne->Draw();can->cd(2);frameNE->Draw();can->SaveAs(("likelihoodScans/"+fitName+"_ProfileLikelihood.pdf").c_str());can->SaveAs(("likelihoodScans/"+fitName+"_ProfileLikelihood.C").c_str());delete can;
    } else {
        cout << "Profile creation not requested. " << endl;
    cout << "    ( create profile is " << CreateProfile << " and mlledge is set constant ? " << mlledge->isConstant() << endl;
    }
    wa->writeToFile((filename+"_result").c_str());
    
    if(!UseMinos) {
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!                                                                                                                   !!!!!" << endl;
      cout << "!!!!!                                            Note that you're not using MINOS                                       !!!!!" << endl;
      cout << "!!!!!                                            if you're doing that deliberately                                      !!!!!" << endl;
      cout << "!!!!!                                            then that's ok, otherwise you                                          !!!!!" << endl;
      cout << "!!!!!                                            need to change UseMinos in the                                         !!!!!" << endl;
      cout << "!!!!!                                            FitCapsule file (+recompile)                                           !!!!!" << endl;
      cout << "!!!!!                                                                                                                   !!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
      cout << "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" << endl;
    }
    
    return 0;
}


