regions = [
#"SignalInclusiveHighMT2",
#"SignalInclusiveHighMT2NLL21",
#"SignalInclusiveNLL26",
#"SignalInclusiveNLL25",
#"SignalInclusiveNLL21",
#"SignalInclusiveHighMT2OneB",
#"SignalInclusiveHighMT2_85",
#"SignalInclusiveHighMT2_85_Met200",
"SignalInclusiveHighMT2_MT2_80_MET_250",
#"SignalInclusiveHighMT2_MT2_80_MET_300",
#"SignalInclusiveHighMT2_MT2_90_MET_300",
#"SignalInclusiveHighMT2_MT2_100_MET_300",
#"SignalInclusiveHighMT2_MT2_100_MET_250",
#"SignalInclusiveHighMT2_MT2_120_MET_250",
#"SignalInclusiveHighMT2_90", 
#"SignalInclusiveHighMT2_100", 
#"SignalInclusiveHighMT2Met200",
#"SignalInclusiveHighMT2Met220",
#"SignalInclusiveHighMT2Met230",
#"SignalInclusiveHighMT2Met240",
#"SignalInclusiveHighMT2Met250",
#"SignalInclusiveMet300",
#"SignalInclusiveMet350",
#"SignalInclusiveMet400",
#"SignalInclusiveHighMT270Met300",
#"SignalInclusiveHighMT270Met250",
#"SignalInclusiveHighMT270Met270",
#"SignalInclusiveHighMT260Met300",
]

signals = [
"slepton_1200_150",
#"slepton_1200_400",
]

#command = "python edgeFitter.py -m -r Run2016_140fb -s {region} -a {signal}"
command = "python edgeFitter.py -m -r Run2016_140fb -s {region}"

import subprocess
import multiprocessing as mp

def start_fit(arg):
    subprocess.call(arg, shell=True)

commands = []
for region in regions:
    for signal in signals: 
        #commands.append(command.format(region=region, signal=signal))
        commands.append(command.format(region=region))

pool = mp.Pool(6)
pool.map_async(start_fit, commands)
pool.close()
pool.join()
