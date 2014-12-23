 /***************************************************************************** 
  * Project: RooFit                                                           * 
  *                                                                           * 
  * This code was autogenerated by RooClassFactory                            * 
  *****************************************************************************/ 

 // Your description goes here... 

 #include "Riostream.h" 

 #include "RooSUSYBkg2GaussiansPdf.h" 
 #include "RooAbsReal.h" 
 #include "RooAbsCategory.h"
 #include "TMath.h"

 ClassImp(RooSUSYBkg2GaussiansPdf) 

 RooSUSYBkg2GaussiansPdf::RooSUSYBkg2GaussiansPdf(const char *name, const char *title, 
                        RooAbsReal& _inv,
                        RooAbsReal& _a1,
                        RooAbsReal& _a2,
                        RooAbsReal& _b1,
                        RooAbsReal& _b2) :
   RooAbsPdf(name,title), 
   inv("inv","inv",this,_inv),
   a1("a1","a1",this,_a1),
   a2("a2","a2",this,_a2),
   b1("b1","b1",this,_b1),
   b2("b2","b2",this,_b2)
 { 
 } 


 RooSUSYBkg2GaussiansPdf::RooSUSYBkg2GaussiansPdf(const RooSUSYBkg2GaussiansPdf& other, const char* name) :  
   RooAbsPdf(other,name), 
   inv("inv",this,other.inv),
   a1("a1",this,other.a1),
   a2("a2",this,other.a2),
   b1("b1",this,other.b1),
   b2("b2",this,other.b2)
 { 
 } 



 Double_t RooSUSYBkg2GaussiansPdf::evaluate() const 
 { 
   // ENTER EXPRESSION IN TERMS OF VARIABLE ARGUMENTS HERE 
   //~ return TMath::Power(inv,a1)*TMath::Exp(-b1*inv);//+TMath::Power(inv,a2)*TMath::Exp(-b2*inv);
   Double_t peak1 = TMath::Gaus((inv - a1), a1, b1);
   Double_t peak2 = TMath::Gaus((inv - a2), a2, b2);

   return  peak1 + peak2;
 } 



