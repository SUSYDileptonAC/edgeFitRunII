import ROOT

def main():
	### default shape (CB)
	deltaLogL = -2*(1626.6951880923839-1629.6947384578953)
	### control region
	#~ deltaLogL = -2*(-1741.0049267357363+1738.3612358373866)
	### 8 TeV shape
	#~ deltaLogL = -2*(1631.4890368509305-1634.5698408383646)
	### KDE
	#~ deltaLogL = -2*(1626.5402114148835-1629.5325478974889)
	pvalue = ROOT.TMath.Prob(deltaLogL, 1);
	sigma = ROOT.TMath.NormQuantile(1.0-pvalue/2);	

	print pvalue, sigma
main()
