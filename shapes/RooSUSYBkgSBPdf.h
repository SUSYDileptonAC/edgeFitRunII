/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef RooSUSYBkgSBPdf
#define RooSUSYBkgSBPdf

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooSUSYBkgSBPdf : public RooAbsPdf {
public:
  RooSUSYBkgSBPdf() {} ; 
  RooSUSYBkgSBPdf(const char *name, const char *title,
	      RooAbsReal& _inv,
	      RooAbsReal& _a1,
	      RooAbsReal& _a2,
	      RooAbsReal& _a3,
	      RooAbsReal& _b1,
	      RooAbsReal& _b2,
	      RooAbsReal& _b3);
  RooSUSYBkgSBPdf(const RooSUSYBkgSBPdf& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooSUSYBkgSBPdf(*this,newname); }
  inline virtual ~RooSUSYBkgSBPdf() { }

protected:

  RooRealProxy inv ;
  RooRealProxy a1 ;
  RooRealProxy a2 ;
  RooRealProxy a3 ;
  RooRealProxy b1 ;
  RooRealProxy b2 ;
  RooRealProxy b3 ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooSUSYBkgSBPdf,1) // Your description goes here...
};
 
#endif