/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef ROOZEXTPDF
#define ROOZEXTPDF

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooZExtPdf : public RooAbsPdf {
public:
  RooZExtPdf() {} ;
	RooZExtPdf(const char *name, const char *title, 
						   RooAbsReal& _inv,
						   RooAbsReal& _cContinuum,
						   RooAbsReal& _prediction );
  RooZExtPdf(const RooZExtPdf& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooZExtPdf(*this,newname); }
  inline virtual ~RooZExtPdf() { }

protected:

  RooRealProxy inv ;
  RooRealProxy mZ ;
  RooRealProxy cContinuum ;
  RooRealProxy prediction ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooZExtPdf,1) // Your description goes here...
};
 
#endif
