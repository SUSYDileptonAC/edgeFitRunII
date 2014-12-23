#ifndef ROOTOPPAIRPRODUCTIONSPLINE
#define ROOTOPPAIRPRODUCTIONSPLINE

#include "RooAbsPdf.h"
#include "RooRealProxy.h"
#include "RooCategoryProxy.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
 
class RooTopPairProductionSpline : public RooAbsPdf {
public:
  RooTopPairProductionSpline() {} ;
  RooTopPairProductionSpline(const char *name, const char *title,
RooAbsReal& _x,
RooAbsReal& _c,
RooAbsReal& _d,
RooAbsReal& _f,
RooAbsReal& _x1,
RooAbsReal& _x2);
  RooTopPairProductionSpline(const RooTopPairProductionSpline& other, const char* name=0) ;
  void WriteOutParameters() const;
  virtual TObject* clone(const char* newname) const { return new RooTopPairProductionSpline(*this,newname); }
  inline virtual ~RooTopPairProductionSpline() { }

protected:

  RooRealProxy x ;
  RooRealProxy c ;
  RooRealProxy d ;
  RooRealProxy f ;
  RooRealProxy x1 ;
  RooRealProxy x2 ;
  
  Double_t evaluate() const ;

private:

  ClassDef(RooTopPairProductionSpline,1) // Your description goes here...
};
#endif

