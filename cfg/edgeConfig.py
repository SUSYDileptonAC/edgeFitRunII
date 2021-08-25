import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

from locations import locations

class rSFOF: # from (rMuE+1/rMuE)*RT evaluation of combined data sets in ttbar control region.
        class inclusive:
                val = 1.06
                err = 0.05
                valMC = 1.06
                errMC = 0.05
class rMMOF: # from (rMuE)*RT evaluation of combined data sets in ttbar control region.
        class inclusive:
                val = 0.64
                err = 0.08
                valMC = 0.64
                errMC = 0.08
class rEEOF: # from (1/rMuE)*RT evaluation of combined data sets in ttbar control region.
        class inclusive:
                val = 0.42
                err = 0.06
                valMC = 0.42
                errMC = 0.06


class edgeConfig:
                
                
                dataset = "MergedData"
                figPath = "fig/"
                # shelvePath = "shelvesAdditional/"
                # shelvePath = "shelvesScan/"
                shelvePath = "shelves/"
                                
                residualMode = "pull"
                plotErrorBands = False  
                
                # edgePosition = 34.4
                #edgePosition = 150
                edgePosition = 290
                # edgePosition = 294.3
                # edgePosition = 150
                toyConfig = {"nToys":1000,"m0":150,"nSig":0,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular","backgroundShape":"CB"}
                #edgePosition = 150
                #fixEdge = True
                fixEdge = False
                                
                title = "None"
                histoytitle = "None"
                
                useMC = True
                useToys = False
 
                #mcdatasets = ["TTJets_Madgraph","ZJets",'SingleTop','Diboson',"Rare"]
                #mcdatasets = ["TT_Powheg","DrellYan","DrellYanTauTau",'SingleTop','Diboson',"Rare"]
                mcdatasets = ["TTJets_Madgraph","DrellYan","DrellYanTauTau",'SingleTop','Diboson',"Rare"]
                #mcdatasets = ["TTJets_Madgraph","ZJets"]
                #mcdatasets = ["TT_Dilepton_Powheg","ZJets"]
                signalDataSets = []
                addDataset = None
                isSignal = False
                
                ### Minos produces asymmetric (and more correct) uncertainties but
                ### takes much longer -> Use for main fit but not for toys
                ### Can still decide to plot symmetric errors if desired
                
                # runMinos = False
                runMinos = True
                # plotAsymErrs = False
                plotAsymErrs = True # THIS IS ONLY VALID FOR THE run 2 paper results, need to change code back if new fit is made. 
                        
                isPreliminary = False
                # isPreliminary = True
                
                ### Can restrict fit to positive signal (which is what we expect)
                ### Note that this introduces a bias to positive signal contributions
                # allowNegSignal = True
                allowNegSignal = False
                ownWork = False
                year = 2016
                showText = True
                logPlot = True
                
                ### Set maximum of y-axis by hand to have the same in SF and OF
                ### Might consider a way to use the SF plot to set it for both
                plotYMax = 350
                #plotYMax = 400
                #plotYMax = 2500
                ### toy-related configuration
                
                # toyConfig = {"nToys":1000,"m0":150,"nSig":0,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular","backgroundShape":"CB"}
                # toyConfig = {"nToys":3000,"m0":300,"nSig":0,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular","backgroundShape":"Hist"}
                #toyConfig = {"nToys":1000,"nSig":70,"m0":300,"scale":1,"systShift":"None","rand":False,"sShape":"Triangular"}

                #dataSetPath = locations.dataSetPath
                
                ### Usually we fit up to 500 GeV (maxInv) but plot only up to 300 (plotMaxInv)
                ### due to insignificant statistics, nBinsMinv is usually (maxInv-minInv)/5
                ### Might be good to check once if there is anything above 300
                #~ maxInv = 700
                maxInv = 500
                #~ maxInv = 300
                minInv = 20
                plotMaxInvDY = 500
                plotMaxInv = 320
                plotMinInv = 20
                #~ nBinsMinv = 136
                #nBinsMinv = 96
                nBinsMinv = 96
                #nBinsMinv = 240
                #~ nBinsMinv = 56
                
                def __init__(self,region="SignalInclusive",backgroundShape="ETH",signalShape="T",runNames = ["Run2016_36fb",],useMC=False,toys=0,addSignal=""):
                        sys.path.append(pathes.basePath)
                        
                        ### Use smaller data sets produced for the likelihood for
                        ### fit in signal region to increase the speed
                        ### Due to MET cut this is not possible for DY fit ->
                        ### normal trees
                        #self.dataSetPath = locations.dataSetPathNLL
                        #self.dataSetPath = locations.dataSetPath
                        
                        self.useMC = useMC
                        
                        from defs import getRunRange
                        self.runRanges = []
                        for runName in runNames:
                                self.runRanges.append(getRunRange(runName))
                        
                        from defs import Regions
                        if not region in dir(Regions):
                                print "invalid region, exiting"
                                sys.exit()
                        else:   
                                self.selection = getattr(Regions,region)
                                self.region = region
                        from centralConfig import zPredictions
                        #from corrections import  rSFOF, rEEOF, rMMOF    
                        #self.rSFOF = rSFOF
                        #self.rEEOF = rEEOF
                        #self.rMMOF = rMMOF
                        
                        
                        
                        from corrections import corrections
                        self.rSFOF = rSFOF
                        self.rEEOF = rEEOF
                        self.rMMOF = rMMOF
                        
                        self.zPredictions = zPredictions
                        
                        self.backgroundShape = backgroundShape
                        self.signalShape = signalShape
                        
                        runRangeName = "_".join([r.label for r in self.runRanges])
                        
                        self.title = self.selection.name+"_"+runRangeName+"_"+self.backgroundShape+self.signalShape
                        self.histoytitle = 'Events / %.1f GeV' % ((self.maxInv - self.minInv) / self.nBinsMinv) 
                        
                        self.toyConfig["nToys"] = int(toys)
                        
                        if toys > 0:
                                # self.useMC = True
                                self.useToys = True
                                
                        if addSignal is not "":
                                self.signalDataSets.append(addSignal)
                                self.isSignal = True
                                self.addDataset = addSignal
