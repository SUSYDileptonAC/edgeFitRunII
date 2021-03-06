/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef ROOSUSYBKGERRPDF
#define ROOSUSYBKGERRPDF

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooSUSYBkgErrPdf : public RooAbsPdf {
public:
  RooSUSYBkgErrPdf() {} ; 
  RooSUSYBkgErrPdf(const char *name, const char *title,
	      RooAbsReal& _inv,
	      RooAbsReal& _a1,
	      RooAbsReal& _a2,
	      RooAbsReal& _b1,
	      RooAbsReal& _b2,
	      RooAbsReal& _c1,
	      RooAbsReal& _c2);
  RooSUSYBkgErrPdf(const RooSUSYBkgErrPdf& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooSUSYBkgErrPdf(*this,newname); }
  inline virtual ~RooSUSYBkgErrPdf() { }

protected:

  RooRealProxy inv ;
  RooRealProxy a1 ;
  RooRealProxy a2 ;
  RooRealProxy b1 ;
  RooRealProxy b2 ;
  RooRealProxy c1 ;
  RooRealProxy c2 ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooSUSYBkgErrPdf,1) // Your description goes here...
};
 
#endif
