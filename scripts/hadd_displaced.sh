#!/bin/sh



dir=/store/group/phys_exotica/delayedjets/displacedJetMuonAnalyzer/csc/V1p7/MC_Summer16/v11/v10/signals/wH/normalized/
eval `scram runtime -sh`

for sample in \
HToSSTobbbb_WToLNu_MH-125_MS-15_ctauS-100_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-40_ctauS-100_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-55_ctauS-100_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-15_ctauS-1000_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-55_ctauS-1000_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-15_ctauS-10000_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-40_ctauS-10000_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-55_ctauS-10000_TuneCUETP8M1_13TeV-powheg-pythia8 \
HToSSTobbbb_WToLNu_MH-125_MS-40_ctauS-1000_TuneCUETP8M1_13TeV-powheg-pythia8
do
eval `scram runtime -sh`
outputRoot=WH_${sample}_1pb_weighted.root
echo "${dir}"
hadd ${outputRoot} /mnt/hadoop/${dir}/WplusH_${sample}_1pb_weighted.root /mnt/hadoop/${dir}/WminusH_${sample}_1pb_weighted.root

if [ -f $outputRoot ]
then
        echo "hadd done"
fi

eval `scram unsetenv -sh`
LD_LIBRARY_PATH=/usr/lib64:$LD_LIBRARY_PATH

gfal-copy -f --checksum-mode=both $outputRoot gsiftp://transfer.ultralight.org/${dir}/$outputRoot

if [ -f /mnt/hadoop/${dir}/$outputRoot ]
then
	echo "copy succeed"
	rm ${outputRoot}
#	gfal-rm gsiftp://transfer.ultralight.org//$dir/WplusH_${sample}_1pb_weighted.root
#	gfal-rm gsiftp://transfer.ultralight.org//$dir/WminusH_${sample}_1pb_weighted.root
fi
done

