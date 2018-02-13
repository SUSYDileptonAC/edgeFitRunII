#include <math.h>

#include "Riostream.h"
#include "RooTopPairProductionSpline.h"
#include "RooAbsReal.h"
#include "RooAbsCategory.h"
#include "TMath.h"

ClassImp(RooTopPairProductionSpline)

RooTopPairProductionSpline::RooTopPairProductionSpline(const char *name, const char *title,
                        RooAbsReal& _x,
                        RooAbsReal& _c,
                        RooAbsReal& _d,
                        RooAbsReal& _f,
                        RooAbsReal& _x1,
                        RooAbsReal& _x2) :
   RooAbsPdf(name,title),
   x("x","x",this,_x),
   c("c","c",this,_c),
   d("d","d",this,_d),
   f("f","f",this,_f),
   x1("x1","x1",this,_x1),
   x2("x2","x2",this,_x2)
{}

RooTopPairProductionSpline::RooTopPairProductionSpline(const RooTopPairProductionSpline& other, const char* name) :
   RooAbsPdf(other,name),
   x("x",this,other.x),
   c("c",this,other.c),
   d("d",this,other.d),
   f("f",this,other.f),
   x1("x1",this,other.x1),
   x2("x2",this,other.x2)
{}

Double_t RooTopPairProductionSpline::evaluate() const
{
       //there are three parts:
    // f_1(x) = a * x^b
    // f_2(x) = c + dx + ex^2 + fx^3
    // f_3(x) = g e^{-hx}
    // the resulting function must be continuous (f_1(x1)=f_2(x1), f_2(x2)=f_3(x2)) and smooth ((f'_1(x1)=f'_2(x1), f'_2(x2)=f'_3(x2))
    // we define the input parameters c,d,e,f (all parameters of f_2(x) ) and conclude on the parameters for f_1 and f_3. In this way the
    // central function also defines the outer ones (note that there 8 parameters and 4 constraints -> 4 free parameters)
  
    // note: since RooFit normalizes as it pleases, there is one too many free parameters - we've chosen to divide everything by "e", making e=-1 (in the old parametrization it was -1.3)
  
   bool debug=false;
    
    if(x1<30) {
        if(debug) cout << "x1 too small (" << x1 << ")" << endl;
        return 0;
    }
    if(x2<x1) {
        if(debug) cout << "x2 smaller than x1 " << endl;
        return 0;
    }
    if(x2<70) {
        if(debug) cout << "x2<70 ... " << endl;
        return 0;
    }
    
    float a=0;
    float b=0;
    float e=-1; // fixed for normalization !
    float g=0;
    float h=0;
    
    b=(d+2*e*x1+3*f*x1*x1)*x1 / (c+d*x1+e*x1*x1+f*x1*x1*x1);
    a=(c+d*x1+e*x1*x1+f*x1*x1*x1)/(pow((float)x1,b));
    
    h=(-1) * (d+2*e*x2+3*f*x2*x2)/(c+d*x2+e*x2*x2+f*x2*x2*x2);
    g=exp(h*x2)*(c+d*x2+e*x2*x2+f*x2*x2*x2);
    
    if(x<0) return 0;
    if(x<x1) return a*pow((float)x,b);
    if(x>=x1 && x<=x2) return c + d*x + e*x*x + f*x*x*x;
    if(x>x2) return g*exp(-h*x);
    return 0;
}

void RooTopPairProductionSpline::WriteOutParameters() const
{
  float a=0;
  float b=0;
  float e=-1; // fixed for normalization !
  float g=0;
  float h=0;
    
  b=(d+2*e*x1+3*f*x1*x1)*x1 / (c+d*x1+e*x1*x1+f*x1*x1*x1);
  a=(c+d*x1+e*x1*x1+f*x1*x1*x1)/(pow((float)x1,b));
    
  h=(-1) * (d+2*e*x2+3*f*x2*x2)/(c+d*x2+e*x2*x2+f*x2*x2*x2);
  g=exp(h*x2)*(c+d*x2+e*x2*x2+f*x2*x2*x2);
  
  
  cout <<" WriteOutParameters a=" << a << endl;
  cout <<" WriteOutParameters b=" << b << endl;
  cout <<" WriteOutParameters c=" << c << endl;
  cout <<" WriteOutParameters d=" << d << endl;
  cout <<" WriteOutParameters e=" << e << endl;
  cout <<" WriteOutParameters f=" << f << endl;
  cout <<" WriteOutParameters g=" << g << endl;
  cout <<" WriteOutParameters h=" << h << endl;
  cout <<" WriteOutParameters x1=" << x1 << endl;
  cout <<" WriteOutParameters x2=" << x2 << endl;
}
