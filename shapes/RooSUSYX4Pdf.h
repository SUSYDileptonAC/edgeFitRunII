/*****************************************************************************
 * Project: RooFit                                                           *
 *                                                                           *
  * This code was autogenerated by RooClassFactory                            * 
 *****************************************************************************/

#ifndef ROOSUSYX4PDF
#define ROOSUSYX4PDF

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooSUSYX4Pdf : public RooAbsPdf {
public:
  RooSUSYX4Pdf() {} ; 
  RooSUSYX4Pdf(const char *name, const char *title,
	      RooAbsReal& _inv,
	      RooAbsReal& _c,
	      RooAbsReal& _s,
	      RooAbsReal& _m0);
  RooSUSYX4Pdf(const RooSUSYX4Pdf& other, const char* name=0) ;
  virtual TObject* clone(const char* newname) const { return new RooSUSYX4Pdf(*this,newname); }
  inline virtual ~RooSUSYX4Pdf() { }

protected:

  RooRealProxy inv ;
  RooRealProxy c ;
  RooRealProxy s ;
  RooRealProxy m0 ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooSUSYX4Pdf,1) // Your description goes here...
};
 
#endif
