import numpy as np
import scipy
import argparse
import glob
from pathlib import Path
from pathlib import PurePath
import subprocess
import re
from numpy import dtype
import os
import time
import json
import sys
import concurrent.futures
import pandas as pd
import argparse
import logging
import psutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from natsort import natsorted, ns

exp_timeout = None
logging.basicConfig(
    format="%(threadName)s - %(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def getBLOGPrograms(programList):
    pfile = open(programList, "r")
    analyzed_programs = pfile.readlines()
    pfile.close()

    analyzed_programsName = [
        p.strip().split("[")[0].strip().lower() for p in analyzed_programs
    ]

    programs = []
    allprograms = glob.glob("../**/programs/BLOG/**/*.blog", recursive=True)
    for p in allprograms:
        if Path(p.strip()).name.split(".")[0].strip().lower() in analyzed_programsName:
            programs.append(Path(p.strip()))

    return programs


def getMatches(matches):
    res = []
    for matchNum, match in enumerate(matches, start=1):
        # print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            # print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
            res += match.group(groupNum)
    return "".join(res)


def runSOGA(program, tvars, parallel=None):
    logger.info(f"Solving {program} with SOGA")
    rt = None
    value = None
    c = None
    d = None
    try:
        if parallel is None:
            out = subprocess.check_output(
                ["python3", "../src/SOGA.py", "-f", program],
                text=True,
                timeout=exp_timeout,
            )
        else:
            out = subprocess.check_output(
                ["python3", "../src/SOGA.py", "-f", program, "-p", f"{parallel}"],
                text=True,
                timeout=exp_timeout,
            )

        rt_reg = r"\s*Runtime:\s*(\d+\.\d+)"
        c_reg = r"\s*c:\s*(\d+)"
        d_reg = r"\s*d:\s*(\d+)"

        value_reg = None
        value = ""
        if tvars is not None:
            value_reg = r"E\[%s\]: ([\+\-]?\d+.\d+)" % (
                re.escape(tvars[1].replace('"', "").strip())
            )
            value = getMatches(
                re.finditer(value_reg, str(out).strip(), re.MULTILINE | re.IGNORECASE)
            )

        rt = getMatches(
            re.finditer(rt_reg, str(out).strip(), re.IGNORECASE | re.MULTILINE)
        )
        c = getMatches(
            re.finditer(c_reg, str(out).strip(), re.IGNORECASE | re.MULTILINE)
        )
        d = getMatches(
            re.finditer(d_reg, str(out).strip(), re.IGNORECASE | re.MULTILINE)
        )

    except subprocess.CalledProcessError as meme:
        value = "err"
    except subprocess.TimeoutExpired as toe:
        value = "to"

    return [rt, value, c, d]


def runAQUA(program, tvars, mean=False):
    logger.info(f"Solving {program} with AQUA")
    stormfiles = glob.glob("%s/**/*.template" % (str(program.parent)), recursive=True)
    rt = -1
    mem = False
    to = False
    value = None
    if len(stormfiles) == 0:
        try:
            st = time.time()
            subprocess.check_call(
                [
                    "java",
                    "-cp",
                    "target/aqua-1.0.jar:lib/storm-1.0.jar",
                    "aqua.analyses.AnalysisRunner",
                    "../%s" % (program.parent),
                ],
                cwd="../tools/AQUA",
                timeout=exp_timeout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            rt = time.time() - st
        except subprocess.CalledProcessError as meme:
            mem = True
        except subprocess.TimeoutExpired as toe:
            to = True
    else:
        try:
            st = time.time()
            subprocess.check_call(
                [
                    "java",
                    "-cp",
                    "target/aqua-1.0.jar:lib/storm-1.0.jar",
                    "aqua.analyses.AnalysisRunner",
                    "../%s" % (stormfiles[0]),
                ],
                cwd="../tools/AQUA",
                timeout=exp_timeout,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            rt = time.time() - st
        except subprocess.CalledProcessError as meme:
            mem = True
        except subprocess.TimeoutExpired as toe:
            to = True

    if mem == False and to == False:
        value = None
        if not mean:
            analisys = json.load(
                open(
                    "%s/analysis_%s.txt"
                    % (str(program.parent), tvars[1].replace('"', "").strip()),
                    "r",
                )
            )
            data = np.array(analisys["data"])
            value = np.dot(data[0, :], data[1, :])
        else:
            outFiles = sorted(glob.glob("%s/analysis_*.txt" % (str(program.parent))))
            mu = []
            for res in outFiles:
                analisys = json.load(open(res, "r"))
                data = np.array(analisys["data"])
                mu += [np.dot(data[0, :], data[1, :])]
            value = mu[0] * mu[1] + mu[2]

    return [rt, value, mem, to]


def runBLOG(program, tvars):
    logger.info(f"Solving {program} with BLOG")
    rt = -1
    mem = False
    to = False
    value = None
    try:
        st = time.time()
        subprocess.check_call(
            ["./blog", "../../%s" % (program)],
            cwd="../tools/blog-0.10/bin",
            timeout=exp_timeout,
            stdout=subprocess.DEVNULL,
        )
        rt = time.time() - st
    except subprocess.CalledProcessError as meme:
        mem = True
    except subprocess.TimeoutExpired as toe:
        to = True

    return [rt, value, mem, to]


def runPSI(program, tvars):
    logger.info(f"Solving {program} with PSI")
    rt = None
    mem = False
    to = False
    value = None

    ppath = "../%s" % (program)

    try:
        st = time.time()
        cwd = "../tools/psi"
        psiFormula = subprocess.check_output(
            ["./psi", ppath, "--expectation", "--raw", "--mathematica"],
            timeout=exp_timeout,
            cwd=cwd,
            text=True,
        )
        psiFormula = "Print[N[%s]]" % (psiFormula)
        logger.info(f"Formula Computed {psiFormula}")

        f = open("results/psi_formula/%s.txt" % (program.name.split(".")[0]), "w+")
        f.write(psiFormula)
        f.close()

        logger.info("Running mathics")
        value = subprocess.check_output(
            [
                "mathics",
                "-q",
                "-script",
                "./results/psi_formula/%s.txt" % (program.name.split(".")[0]),
            ],
            timeout=exp_timeout,
            text=True,
        )
        value = str(value).strip()

        if "Syntax::" in value:
            mem = True
            to = True

        rt = time.time() - st
    except subprocess.CalledProcessError as meme:
        mem = True
    except subprocess.TimeoutExpired as toe:
        to = True
    except concurrent.futures._base.TimeoutError as toe2:
        to = True

    return [rt, value, mem, to]


def runPYMC3(program, tvars):
    logger.info(f"Solving {program} with PyMC3")
    ppath = f"{program.parent.absolute()}/{program.name}"
    outpath = f"{program.parent.absolute()}/{program.stem}.csv"

    rt = None
    mem = False
    to = False
    value = None

    cwd = str(Path(program).parent.absolute())
    try:
        st = time.time()
        subprocess.check_call(
            ["python3", ppath, "-o", outpath],
            timeout=exp_timeout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        rt = time.time() - st
    except subprocess.CalledProcessError as meme:
        mem = True
    except subprocess.TimeoutExpired as toe:
        to = True

    if not to and not mem:
        if not Path(outpath).is_file():
            raise valueError(f"{outpath} not found")

        data = pd.read_csv(outpath, comment="#")
        value = data["value"].iloc[0]
        rt = data["time"].iloc[0]

        os.remove(outpath)

    return [rt, value, mem, to]


def runSTAN(program, tvars, runs=1000, datFile=None):
    ppath = "../%s/%s" % (program.parent, program.name.split(".")[0])
    print(program)
    rt = None
    mem = False
    to = False
    value = None

    print(f"Data {datFile}")

    cwd = "../tools/cmdstan-2.34.0"
    subprocess.check_call(
        ["make", ppath], cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    )
    while True:
        if (
            Path("%s/%s.data.R" % (str(program.parent), program.name.split(".")[0]))
        ).is_file() or Path(datFile).is_file():
            try:
                st = time.time()
                if datFile is None:
                    subprocess.check_call(
                        [
                            "%s/%s" % (str(program.parent), program.name.split(".")[0]),
                            "sample",
                            "num_samples=%s" % (runs),
                            "data",
                            "file=%s/%s.data.R"
                            % (str(program.parent), program.name.split(".")[0]),
                            "output",
                            "file=%s.csv" % (program.name.split(".")[0]),
                        ],
                        timeout=exp_timeout,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )
                else:
                    subprocess.check_call(
                        [
                            "%s/%s" % (str(program.parent), program.name.split(".")[0]),
                            "sample",
                            "num_samples=%s" % (runs),
                            "random",
                            "seed=0",
                            "data",
                            f"file={datFile}",
                            "output",
                            f"file={program.parent.absolute()}/%s.csv"
                            % (program.name.split(".")[0]),
                        ],
                        timeout=exp_timeout,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )

                rt = time.time() - st
            except subprocess.CalledProcessError as meme:
                mem = True
            except subprocess.TimeoutExpired as toe:
                to = True
        else:
            try:
                st = time.time()
                subprocess.check_call(
                    [
                        "%s/%s" % (str(program.parent), program.name.split(".")[0]),
                        "sample",
                        "num_samples=%s" % (runs),
                        "output",
                        "file=%s.csv" % (program.name.split(".")[0]),
                    ],
                    timeout=exp_timeout,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.STDOUT,
                )
                rt = time.time() - st
            except subprocess.CalledProcessError as meme:
                mem = True
            except subprocess.TimeoutExpired as toe:
                to = True

        if not to and not mem:
            if Path(
                f"{program.parent.absolute()}/%s_out.csv" % (program.name.split(".")[0])
            ).is_file():
                os.remove(
                    f"{program.parent.absolute()}/%s_out.csv"
                    % (program.name.split(".")[0])
                )

            subprocess.check_call(
                [
                    "../tools/cmdstan-2.34.0/bin/stansummary",
                    f"{program.parent.absolute()}/%s.csv"
                    % (program.name.split(".")[0]),
                    "-c",
                    f"{program.parent.absolute()}/%s_out.csv"
                    % (program.name.split(".")[0]),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

            data = pd.read_csv(
                f"{program.parent.absolute()}/%s_out.csv"
                % (program.name.split(".")[0]),
                comment="#",
            )
            e = []
            value = None
            for v in tvars:
                value = data[data["name"] == v.strip().lower()]["Mean"].iloc[0]
                stdDev = data[data["name"] == v.strip().lower()]["StdDev"].iloc[0]
                MCSE = data[data["name"] == v.strip().lower()]["MCSE"].iloc[0]
                ci = 1.96 * stdDev / np.sqrt(runs)
                rhat = data[data["name"] == v.strip().lower()]["R_hat"].iloc[0]
                # e+=[abs(ci*2)*100/value]
                e += [MCSE]
                # print(v,value)

            os.remove(
                f"{program.parent.absolute()}/%s.csv" % (program.name.split(".")[0])
            )
            if max(e) <= 0.1:
                print("converged")
                break
            else:
                print(max(e), runs, rt)
                runs += 1e04
        else:
            print("Timeedout")
            break

    return [rt, value, mem, to]


def saveRes(programs=None, tools=None, outPath=None, tableres=None):
    resFile = open(str(PurePath(outPath)), "w+")
    resFile.write("model,tool,time,value,#c,#d\n")
    fileline = ""
    for key, val in enumerate(tableres):
        # assumo che la struttura del nome sia tool_model
        exppname = val.replace("Prune", "").lower()
        tool = exppname.split("_")[0].strip().lower()
        prog = exppname.split("_")[1].strip().lower()
        fileline += f'"{prog}","{tool}"'
        if tool != "soga":
            if val in tableres:
                if tableres[val][2] == True:
                    fileline += ',"mem","mem","",""'
                elif tableres[val][3] == True:
                    fileline += ',"to","to","",""'
                else:
                    fileline += f',"{tableres[val][0]}","{tableres[val][1]}","",""'
            else:
                fileline += ",-,-"
        else:
            if val in tableres:
                if tableres[val][1] == "err":
                    fileline += ',"err","err","",""'
                elif tableres[val][1] == "to":
                    fileline += ',"to","to","",""'
                else:
                    fileline += f',"{tableres[val][0]}","{tableres[val][1]}","{tableres[val][2]}","{tableres[val][3]}"'
            else:
                fileline += ",-,-,-,-"
        fileline += "\n"

    resFile.write(fileline)

    resFile.flush()
    resFile.close()


def sensPruningExp():
    logger.info("Computing sensisitvity to pruning")
    programs = glob.glob(
        "../**/programs/SOGA/SensitivityExp/Pruning/**/*.soga", recursive=True
    )
    tvars = np.loadtxt(
        "../programs/SOGA/SensitivityExp/Pruning/observerdVariables.txt",
        dtype=str,
        delimiter=",",
    )

    tableres = {}
    for p in programs:
        p = Path(p)
        for idx, var in enumerate(tvars[:, 0]):
            if var.lower() == p.name.split(".")[0].lower():
                break
        pname = p.name.split(".")[0].replace("Prune", "").lower()
        expname = f"soga_{pname}@{p.parent.name}"
        tableres[expname] = runSOGA(p, tvars=tvars[idx, :])

    saveRes(
        programs=programs,
        tools=["SOGA"],
        outPath="./results/pruneSensitivity.csv",
        tableres=tableres,
    )


def sensBranchesExp():
    logger.info("Computing sensisitvity to #baranches")
    programs = glob.glob(
        "../**/programs/SOGA/SensitivityExp/#branches/**/*.soga", recursive=True
    )
    psiPrograms = glob.glob(
        "../**/programs/PSI/SensitivityExp/#branches/**/*.psi", recursive=True
    )
    dfvars = pd.read_csv(
        "../programs/SOGA/SensitivityExp/#branches/observedVariables.csv",
        names=["model", "var"],
    )

    tableres = {}
    logger.info("####################running SOGA#####################")
    for p in programs:
        p = Path(p)
        pname = p.name.split(".")[0].replace("Prune", "").lower()
        expname = f"soga_{p.stem}${p.parent.parent.name}"
        tvars = (
            dfvars[dfvars["model"].str.lower() == re.sub(r"\d+", "", pname)]["var"]
            .iloc[0]
            .strip()
        )
        tableres[expname] = runSOGA(p, tvars=["", tvars])
    logger.info("####################running PSI#####################")
    for p in psiPrograms:
        p = Path(p)
        pname = p.name.split(".")[0].lower()
        expname = f"psi_{p.stem}${p.parent.parent.name}"
        tvars = dfvars[dfvars["model"].str.lower() == re.sub(r"\d+", "", pname)][
            "var"
        ].iloc[0]
        tableres[expname] = runPSI(p, tvars=["", tvars])

    saveRes(
        programs=programs,
        tools=["SOGA", "PSI"],
        outPath="./results/branchSensitivity.csv",
        tableres=tableres,
    )


def sensVarExp():
    logger.info("Computing sensisitvity to variables experiements")
    programs = glob.glob(
        "../**/programs/SOGA/SensitivityExp/#variables/timeseries/*.soga",
        recursive=True,
    )
    PYMC3Programs = glob.glob("../**/programs/PYMC/timeseries*.py", recursive=True)

    tableres = {}
    logger.info("####################running PyMC3#####################")
    for p in PYMC3Programs:
        p = Path(p)
        nvar = int(re.findall(r"(\d+)\.", p.name)[0])-4
        tvars = ["alpha", "beta"]
        tvars += [f"y{v}" for v in range(1, nvar + 1)]
        dname = p.name.replace(f"{nvar}", "").split(".")[0]
        tableres["pymc_%s" % (p.stem.lower())] = runPYMC3(p, tvars)
    logger.info("####################running SOGA#####################")
    for p in programs:
        p = Path(p)
        nvar = int(re.findall(r"(\d+)\.", p.name)[0])-4
        tvars = ["", f"y{nvar}"]
        tableres[
            "soga_%s" % (p.name.split(".")[0].replace("Prune", "").lower())
        ] = runSOGA(p, tvars=tvars)

    resFile = open(str(PurePath("./results/varSensitivity.csv")), "w+")
    tools = ["SOGA", "PYMC"]

    saveRes(
        programs=programs,
        tools=tools,
        outPath="./results/varSensitivity.csv",
        tableres=tableres,
    )


def sensCmpExp():
    logger.info("Computing sensisitvity component experiements")
    programs = glob.glob(
        "../**/programs/SOGA/SensitivityExp/#components/*.soga", recursive=True
    )
    psiPrograms = glob.glob(
        "../**/programs/PSI/SensitivityExp/#components/**/*.psi", recursive=True
    )
    tvars = pd.read_csv("target_vars_T3.txt", header=None)
    tvars.iloc[:, 0] = tvars.iloc[:, 0].apply(lambda x: x.lower())

    tableres = {}

    logger.info("####################running SOGA#####################")
    for p in programs:
        p = Path(p)
        pname = p.name.split(".")[0].replace("Prune", "").lower()
        t = tvars[
            tvars.iloc[:, 0] == pname.replace(re.findall(r"(\d+)", pname)[0], "")
        ].iloc[0, 1]
        tableres["soga_%s" % (pname)] = runSOGA(p, tvars=["", t])

    saveRes(
        programs=programs,
        tools=["SOGA"],
        outPath="./results/cmpSensitivity.csv",
        tableres=tableres,
    )


def sensParExp():
    logger.info("Evaluating Pralellization Experiements")
    programs = glob.glob(
        "../**/programs/SOGA/SensitivityExp/#proc/continuous/**/*.soga", recursive=True
    )

    parLevels = [1]+[par - 2 for par in range(4, 24, 2)]

    tableres = {}
    logger.info("####################running SOGA#####################")
    tvars = ["", "x"]
    for p in programs:
        for pl in parLevels:
            logger.info(f"Analyzing {p} with concurrency level {pl}")
            p = Path(p)
            nvar = int(re.findall(r"(\d+)\.", p.name)[0])
            tableres[
                f"soga_%s_{pl}" % (p.name.split(".")[0].replace("Prune", "").lower())
            ] = runSOGA(p, tvars=tvars, parallel=pl)

    resFile = open(str(PurePath("./results/parSensitivity.csv")), "w+")
    tools = ["SOGA"]
    resFile.write("model,#proc,time,value,#c,#d\n")
    for p in programs:
        for pl in parLevels:
            fileline = ""
            p = Path(p)
            pname = p.name.split(".")[0].replace("Prune", "").lower()
            fileline += f"{pname},{pl}"
            for t in tools:
                k = "%s_%s_%s" % (t.lower(), pname, pl)
                if t.lower() != "soga":
                    if k in tableres:
                        if tableres[k][2] == True:
                            fileline += ",'mem','mem','',''"
                        elif tableres[k][3] == True:
                            fileline += ",'to','to','',''"
                        else:
                            fileline += ",%s,%s" % (
                                str(tableres[k][0]),
                                str(tableres[k][1]),
                            )
                    else:
                        fileline += ",--"
                else:
                    if k in tableres:
                        if tableres[k][1] == "err":
                            fileline += ',"err","err","",""'
                        elif tableres[k][1] == "to":
                            fileline += ',"to","to","",""'
                        else:
                            fileline += f",{tableres[k][0]},{tableres[k][1]},{tableres[k][2]},{tableres[k][3]}"
                    else:
                        fileline += ",-,-,-,-"

            resFile.write(fileline + "\n")

    resFile.flush()
    resFile.close()


def monitor_process_and_children(process_id, interval=None):
    """Monitors CPU and memory utilization of the given process and its children."""
    try:
        parent_process = psutil.Process(process_id)
        process_name = parent_process.name()

        # Get CPU utilization (average across cores)
        cpu_percent = parent_process.cpu_percent(interval=interval)

        # Calculate total CPU and memory usage of child processes
        children_cpu = 0
        for child in parent_process.children(recursive=True):
            children_cpu += child.cpu_percent(interval=interval)

        return process_name, cpu_percent, children_cpu

    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"Error monitoring process {process_id}: {e}")
        return None


def round_to_n_digit(num,n):
    try:
        rounded_num = round(float(num), n)
    except:
        return num
    return f'{{:.{n}f}}'.format(rounded_num)

def renderTable2Tex(respath="./results/varSensitivity.csv",outpath="./results/latexResult/"):
    varSensitivityRes=[]
    exp_path=Path(respath)
    if(not exp_path.is_file()):
        raise ValueError(f"Experiements {exp_path} does not Exist!")
    #Model time value time value %e
    vardf=pd.read_csv(exp_path)
    models=natsorted(list(set(vardf["model"])), alg=ns.IGNORECASE)
    for m in models:
        trow=[]
        sogares=vardf[(vardf["model"]==m) & (vardf["tool"]=="soga")].iloc[0]
        pymcres=vardf[(vardf["model"]==m) & (vardf["tool"]=="pymc")].iloc[0]

        err="-"
        sogatime,sogavalue,sogac,sogad,pymctime,pymcvalue=extractvalue(pymcres,sogares)

        if(pymctime!="to" and pymctime!="mem"):
            pymctime=round_to_n_digit(pymctime,3)
            pymcvalue=round_to_n_digit(pymcvalue,3)

        if(sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
            sogatime=round_to_n_digit(sogatime,3)
            sogavalue=round_to_n_digit(sogavalue,3)
            sogac=sogac
            sogad=sogad

        if(pymctime!="to" and pymctime!="mem" and sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
            err=round_to_n_digit(abs(float(pymcvalue)-float(sogavalue))*100/float(pymcvalue),3)

        trow+=[re.sub(r"\d+","",m),sogatime,sogavalue,pymctime,pymcvalue,err,sogad]

        varSensitivityRes+=[trow]

    outpath=Path(outpath).absolute()
    outpath.mkdir(parents=True, exist_ok=True)
    outpath=outpath/Path("Table2.tex")

    env = Environment(
            loader=FileSystemLoader('../jinjaTemplate/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False,
            comment_start_string='%!', 
            comment_end_string='!%')

    mat_tmpl = env.get_template('resTmpT2.tex')
    texFile = mat_tmpl.render(varSensitivityRes=varSensitivityRes)
    outFile=open(outpath.absolute(),"w+")
    outFile.write(texFile)
    outFile.close()

    try:
        subprocess.run(['pdflatex', outpath.absolute()],cwd=outpath.parent.absolute())
    except FileNotFoundError:
        print("pdflatex is not installed or not found in your PATH.")


def extractvalue(pymcres,sogares):
    pymctime=pymcres["time"]
    pymcvalue=pymcres["value"]
    sogatime=sogares["time"]
    sogavalue=sogares["value"]
    sogac="-"
    sogad="-"
    err="-"

    if(pymctime!="to" and pymctime!="mem"):
        pymctime=round_to_n_digit(pymctime,3)
        pymcvalue=round_to_n_digit(pymcvalue,3)

    if(sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
        sogatime=round_to_n_digit(sogatime,3)
        sogavalue=round_to_n_digit(sogavalue,3)
        sogac=int(sogares["#c"])
        sogad=int(sogares["#d"])

    return sogatime,sogavalue,sogac,sogad,pymctime,pymcvalue


def renderTable3Tex(respath="./results/branchSensitivity.csv",outpath="./results/latexResult/"):
    branchSensitivityRes={}
    exp_path=Path(respath)
    if(not exp_path.is_file()):
        raise ValueError(f"Experiements {exp_path} does not Exist!")

    branchdf=pd.read_csv(exp_path)
    models=[r"randomwalk\d+\$discrete",r"randomwalk\d+\$continuous",r"Bernoulli",r"ClinicalTrial",r"CoinBias",r"SurveyUnbias"]
    for m in models:
        sogares=branchdf[(branchdf["tool"]=="soga")&(branchdf['model'].str.contains(m, regex=True,case=False))].sort_values(by="#c")
        psires=branchdf[(branchdf["tool"]=="psi")&(branchdf['model'].str.contains(m, regex=True,case=False))].sort_values(by="#c")  

        for prg in sogares["model"]:
            it=int(re.findall(r"\d+",prg)[0])
            path=2**it
            if(str(it) not in branchSensitivityRes):
                branchSensitivityRes[str(it)]=[it,path]

            err="-"
            sogatime,sogavalue,sogac,sogad,psitime,psivalue=extractvalue(psires[psires["model"]==prg].iloc[0],sogares[sogares["model"]==prg].iloc[0])

            if(psitime!="to" and psitime!="mem"):
                psitime=round_to_n_digit(psitime,2)
                psivalue=round_to_n_digit(psivalue,2)

            if(sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
                sogatime=round_to_n_digit(sogatime,2)
                sogavalue=round_to_n_digit(sogavalue,2)
                sogac=sogac
                sogad=sogad

            if(psitime!="to" and psitime!="mem" and sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
                if(float(psivalue)==0):
                    err=0
                else:
                    err=round_to_n_digit(abs(float(psivalue)-float(sogavalue))*100/float(psivalue),2)

            branchSensitivityRes[str(it)]+=[sogac,sogatime,err]

    outpath=Path(outpath).absolute()
    outpath.mkdir(parents=True, exist_ok=True)
    outpath=outpath/Path("Table3.tex")

    env = Environment(
            loader=FileSystemLoader('../jinjaTemplate/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False,
            comment_start_string='%!', 
            comment_end_string='!%')

    mat_tmpl = env.get_template('resTmpT3.tex')
    texFile = mat_tmpl.render(branchSensitivityRes=branchSensitivityRes)
    outFile=open(outpath.absolute(),"w+")
    outFile.write(texFile)
    outFile.close()

    try:
        subprocess.run(['pdflatex', outpath.absolute()],cwd=outpath.parent.absolute())
    except FileNotFoundError:
        print("pdflatex is not installed or not found in your PATH.")

def renderTable4Tex(respath="./results/cmpSensitivity.csv",outpath="./results/latexResult/"):
    cmpSensitivityRes={}
    exp_path=Path(respath)
    if(not exp_path.is_file()):
        raise ValueError(f"Experiements {exp_path} does not Exist!")

    #model,tool,time,value,#c,#d
    cmpdf=pd.read_csv(exp_path)
    cmptrue=pd.read_csv("./results/cmpSensitivity_true.csv")
    models=[r"Coinbias\d*",r"SurveyUnbias\d*"]
    for m in models:
        sogares=cmpdf[(cmpdf["tool"]=="soga")&(cmpdf['model'].str.contains(m, regex=True,case=False))].sort_values(by="#c")
        psires=cmptrue[(cmptrue['model'].str.contains(m, regex=True,case=False))]

        for prg in sogares["model"]:
            it=int(re.findall(r"\d+",prg)[0])
            path=2**it
            if(str(it) not in cmpSensitivityRes):
                cmpSensitivityRes[str(it)]=[it]


            err="-"
            sogatime,sogavalue,sogac,sogad,psitime,psivalue=extractvalue(psires[psires["model"]==re.sub(r"\d+","",prg)].iloc[0],sogares[sogares["model"]==prg].iloc[0])

            if(psitime!="to" and psitime!="mem"):
                psitime=round_to_n_digit(psitime,2)
                psivalue=round_to_n_digit(psivalue,2)

            if(sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
                sogatime=round_to_n_digit(sogatime,2)
                sogavalue=round_to_n_digit(sogavalue,2)
                sogac=int(sogac)
                sogad=int(sogad)

            if(psitime!="to" and psitime!="mem" and sogavalue!="to" and sogavalue!="mem" and sogavalue!="err"):
                if(float(psivalue)==0):
                    err=0
                else:
                    err=round_to_n_digit(abs(float(psivalue)-float(sogavalue))*100/float(psivalue),2)

            cmpSensitivityRes[str(it)]+=[sogatime,err,sogac]

    outpath=Path(outpath).absolute()
    outpath.mkdir(parents=True, exist_ok=True)
    outpath=outpath/Path("Table4.tex")

    env = Environment(
            loader=FileSystemLoader('../jinjaTemplate/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False,
            comment_start_string='%!', 
            comment_end_string='!%')

    mat_tmpl = env.get_template('resTmpT4.tex')
    texFile = mat_tmpl.render(cmpSensitivityRes=cmpSensitivityRes)
    outFile=open(outpath.absolute(),"w+")
    outFile.write(texFile)
    outFile.close()

    try:
        subprocess.run(['pdflatex', outpath.absolute()],cwd=outpath.parent.absolute())
    except FileNotFoundError:
        print("pdflatex is not installed or not found in your PATH.")

def renderTable5Tex(respath="./results/parSensitivity.csv",outpath="./results/latexResult/"):
    parSensitivityRes={}
    exp_path=Path(respath)
    if(not exp_path.is_file()):
        raise ValueError(f"Experiements {exp_path} does not Exist!")

    pardf=pd.read_csv(exp_path)
    models=list(set(pardf["model"]))
    for m in models:
        sogares=pardf[(pardf['model'].str.contains(m, regex=True,case=False))].sort_values(by="#proc")
        mname=re.sub("\d+","",m).lower()
        parlevels=[1,2,4,6,8,10,12,20]
        parSensitivityRes[mname]=[ round_to_n_digit(sogares[sogares["#proc"]==p]["time"].iloc[0],2) for p in parlevels]

    outpath=Path(outpath).absolute()
    outpath.mkdir(parents=True, exist_ok=True)
    outpath=outpath/Path("Table5.tex")

    env = Environment(
            loader=FileSystemLoader('../jinjaTemplate/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False,
            comment_start_string='%!', 
            comment_end_string='!%')

    mat_tmpl = env.get_template('resTmpT5.tex')
    texFile = mat_tmpl.render(parSensitivityRes=parSensitivityRes)
    outFile=open(outpath.absolute(),"w+")
    outFile.write(texFile)
    outFile.close()

    try:
        subprocess.run(['pdflatex', outpath.absolute()],cwd=outpath.parent.absolute())
    except FileNotFoundError:
        print("pdflatex is not installed or not found in your PATH.")

def renderTable6Tex(respath="./results/pruneSensitivity.csv",outpath="./results/latexResult/"):
    pruneSensitivityRes={}
    exp_path=Path(respath)
    if(not exp_path.is_file()):
        raise ValueError(f"Experiements {exp_path} does not Exist!")

    #model,tool,time,value,#c,#d
    prunedf=pd.read_csv(exp_path)
    prunetruedf=pd.read_csv("./results/PruneTrue.csv")
    models=list(set(prunedf["model"]))
    models=list(set([m.split("@")[0] for m in models]))

    for m in models:
        sogares=prunedf[(prunedf['model'].str.contains(m, regex=True,case=False))].sort_values(by=["model"],ascending=False)
        pruneSensitivityRes[m]=[]
        gtruth=float(prunetruedf[prunetruedf["model"]==m]["value"])
        for i in range(sogares.shape[0]):
            e=None
            if(sogares["value"].iloc[i]!="" and not sogares["value"].iloc[i]=="to"):
                e=round_to_n_digit(abs(float(sogares["value"].iloc[i])-gtruth)*100/gtruth,2)

            mtime="to"
            if(sogares["time"].iloc[i] is not None and sogares["value"].iloc[i]!="to"):
                mtime=round_to_n_digit(sogares["time"].iloc[i],2)

            pruneSensitivityRes[m]+=[mtime,e]

    outpath=Path(outpath).absolute()
    outpath.mkdir(parents=True, exist_ok=True)
    outpath=outpath/Path("Table6.tex")

    env = Environment(
            loader=FileSystemLoader('../jinjaTemplate/'),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=False,
            lstrip_blocks=False,
            comment_start_string='%!', 
            comment_end_string='!%')

    mat_tmpl = env.get_template('resTmpT6.tex')
    texFile = mat_tmpl.render(pruneSensitivityRes=pruneSensitivityRes)
    outFile=open(outpath.absolute(),"w+")
    outFile.write(texFile)
    outFile.close()

    try:
        subprocess.run(['pdflatex', outpath.absolute()],cwd=outpath.parent.absolute())
    except FileNotFoundError:
        print("pdflatex is not installed or not found in your PATH.")

def main():
    global exp_timeout
    parser = argparse.ArgumentParser(description="SOGA Replication Scripts")

    parser.add_argument(
        "--exp",
        required=True,
        type=str,
        choices=["prune", "branch", "var", "cmp", "par"],
        help="Select the experiement to perform",
    )

    parser.add_argument('--smoke', '-s', action='store_true', help='Enable the smoke test', default=False)


    args = parser.parse_args()
    # Accessing the value of the string parameter
    exp = args.exp

    if(not args.smoke):
        exp_timeout=600
    else:
        exp_timeout=2

    if exp == "prune":
        sensPruningExp()
        renderTable6Tex()
    elif exp == "branch":
        sensBranchesExp()
        renderTable3Tex()
    elif exp == "var":
        sensVarExp()
        renderTable2Tex()
    elif exp == "cmp":
        sensCmpExp()
        renderTable4Tex()
    elif exp == "par":
        sensParExp()
        renderTable5Tex()


if __name__ == "__main__":
    main()
