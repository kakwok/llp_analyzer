import glob
import sys, commands, os, fnmatch
from optparse import OptionParser,OptionGroup

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def write_condor(njobs, exe='runjob', files = [], dryRun=True):
    fname = '%s.jdl' % exe
    out = """universe = vanilla
Executable = {exe}.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT_OR_EVICT
Transfer_Input_Files = {exe}.sh,{files}
Output = {exe}.$(Process).$(Cluster).stdout
Error  = {exe}.$(Process).$(Cluster).stdout
Log    = {exe}.$(Process).$(Cluster).log
Arguments = $(Process) {njobs}
Queue {njobs}
    """.format(exe=exe, files=','.join(files), njobs=njobs)
    with open(fname, 'w') as f:
        f.write(out)
    if not dryRun:
        os.system("condor_submit %s" % fname)

def tarInput(taroutput,paths,dryRun=False):
    print("Tarring local input files ... ")
    flatFlist= []
    flist = []
    for p in paths:
        flist += glob.glob(p)

    for f in flist:
        exec_me("cp %s ."%f)
        flatFlist.append(os.path.split(f)[1]) ## file name of the path

    tarcmd = "tar -czvf %s "% taroutput +" ".join(flatFlist)
    exec_me(tarcmd,dryRun)
    print("cleaning up")
    exec_me("rm %s"%" ".join(flatFlist),dryRun)


def write_bash(temp = 'runjob.sh',  command = '',CMSSW="" ):
    out = '#!/bin/bash\n'
    out += 'date\n'
    out += 'MAINDIR=`pwd`\n'
    out += 'ls\n'
    #out += 'voms-proxy-info --all\n'
    out += '#CMSSW from scratch (only need for root)\n'
    out += 'export CWD=${PWD}\n'
    out += 'export PATH=${PATH}:/cvmfs/cms.cern.ch/common\n'
    out += 'export SCRAM_ARCH=slc7_amd64_gcc700\n'
    out += 'scramv1 project CMSSW %s\n'%CMSSW
    out += 'mv %s %s/src\n'%(command.split()[0],CMSSW) ## move executable to folder
    out += 'mv corrections.tar.gz %s/src\n'%CMSSW                            ## move tar to folder
    out += 'mv JEC.tar.gz %s/src\n'%CMSSW                            ## move tar to folder
    out += 'cd %s/src\n'%CMSSW
    out += 'eval `scramv1 runtime -sh` # cmsenv\n'
    out += 'echo "Untar : tar -vxzf corrections.tar.gz"\n'
    out += 'tar -vxzf corrections.tar.gz\n'
    out += 'echo "Untar JEC:" \n'
    out += 'tar -vxzf JEC.tar.gz\n'
    out += 'echo "After Untar: "\n'
    out += 'ls\n'
    out += command + '\n'
    out += 'echo "Inside $MAINDIR:"\n'
    out += 'ls\n'
    out += 'echo "DELETING..."\n'
    out += 'rm -rf %s\n'%CMSSW
    out += 'rm -rf *.pdf *.C core*\n'
    out += 'ls\n'
    out += 'date\n'
    with open(temp, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--clean', dest='clean', action='store_true',default = False, help='clean submission files', metavar='clean')
    parser.add_option('--dryRun', dest='dryRun', action='store_true',default = False, help='write submission files only', metavar='dryRUn')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')
    parser.add_option('-i', '--inputList', dest='inputList', default='./lists/test.txt', help='txt file for list of input', metavar='inputList')
    parser.add_option( '--njobs', dest='njobs', default=500, type="int", help='Number of jobs to split into', metavar='njobs')

    script_group  = OptionGroup(parser, "script options")
    script_group.add_option("-d","--isData", dest="isData", default="no",  help="MC = yes data = yes", metavar="isData")
    #script_group.add_option("-f"           , dest="outputFile", default="HeavyNeutralLepton_Tree.root", help="outputFile name", metavar="outputFile")
    script_group.add_option("-l"           , dest="optionLabel", default="Razor2018_17SeptEarlyReReco", help="optionLabel for JEC", metavar="optionLabel")
    script_group.add_option("--optionNumber", dest="optionNumber", default="01", help="optionNumber", metavar="optionNumber")
    parser.add_option_group(script_group)

    (options, args) = parser.parse_args()
    dryRun= options.dryRun 

    maxJobs = options.njobs 

    outpath= options.odir


    ##input files needed by analyzer:
    tarList = [
          "./data/ScaleFactors/2017/Muon*",
          "./data/ScaleFactors/METTriggers_SF.root",
          "./data/PileupWeights/PileupReweight_MC_Fall17_ZToMuMu_NNPDF31_13TeV-powheg_M_50_120.root",
          "./data/PileupWeights/PileupReweight_MC_Fall17_ggH_HToSSTobbbb_MH-125_TuneCP5_13TeV-powheg-pythia8.root",
          "./data/PileupWeights/PileupReweight_MC_Fall18_ggH_HToSSTobbbb_MH-125_TuneCP5_13TeV-powheg-pythia8.root",
          "./data/PileupWeights/PileupReweight_MC_Summer16_ggH_HToSSTobbbb_MH-125_TuneCUETP8M1_13TeV-powheg-pythia8.root",
          "./data/PileupWeights/PileupReweight_source18_target17.root",
          "./data/PileupWeights/PileupReweight_source18_target16.root",   
          "./data/HiggsPtWeights/ggH_HiggsPtReweight_NNLOPS.root",
    ]
    tarInput("corrections.tar.gz",tarList,options.dryRun)


    ##Small files used by the exe
    transfer_files = [
        os.getcwd()+"/Runllp_hnl_analyzer",
        os.getcwd()+"/data/JEC.tar.gz",
        os.getcwd()+"/corrections.tar.gz",
    ]
    fileName = 'HeavyNeutralLepton_Tree'
    subFileName = fileName.replace(".root","_*.root")

    ##split input txt list
    allinputs = []
    with open(options.inputList,'r') as f:
        allinputs = [line for line in f]
        nFilesPerJob = len(allinputs)/ maxJobs
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        os.chdir(outpath)
        print "submitting jobs from : ",os.getcwd()
    
        for i in range( maxJobs ):
            tmp_inputs =  allinputs[i*nFilesPerJob : (i+1)*nFilesPerJob]
            transfer_files.append("tmp_input_list_%i.txt"%i)
            with open("tmp_input_list_%i.txt"%i,'w') as fout:
                for line in tmp_inputs: fout.write(line)


    command      = './Runllp_hnl_analyzer ${MAINDIR}/tmp_input_list_$1.txt -f=${MAINDIR}/%s_$1.root '%fileName
    #Add script options to job command
    for opts in script_group.option_list:
            command  += " --%s=%s "%(opts.dest,getattr(options, opts.dest))

    print "command to run: ", command

    exe = "runjob"
    write_bash(exe+".sh",  command, "CMSSW_10_6_20" )
    write_condor(maxJobs, exe,  transfer_files, dryRun)