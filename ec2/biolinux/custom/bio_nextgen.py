"""Install next gen sequencing analysis tools not currently packaged.
"""
import os

from fabric.api import *
from fabric.contrib.files import *

from shared import (_if_not_installed, _make_tmp_dir,
                    _get_install, _get_install_local, _make_copy, _configure_make,
                    _symlinked_java_version_dir, _fetch_and_unpack)

@_if_not_installed("faToTwoBit")
def install_ucsc_tools(env):
    """Install useful executables from UCSC.

    todo: install from source to handle 32bit and get more programs
    http://hgdownload.cse.ucsc.edu/admin/jksrc.zip
    """
    tools = ["liftOver", "faToTwoBit", "bedToBigBed",
             "bigBedInfo", "bigBedSummary", "bigBedToBed",
             "bigWigInfo", "bigWigSummary", "bigWigToBedGraph", "bigWigToWig",
             "fetchChromSizes", "wigToBigWig"]
    url = "http://hgdownload.cse.ucsc.edu/admin/exe/linux.x86_64/"
    install_dir = os.path.join(env.system_install, "bin")
    for tool in tools:
        with cd(install_dir):
            if not exists(tool):
                sudo("wget %s%s" % (url, tool))
                sudo("chmod a+rwx %s" % tool)

# --- Alignment tools

@_if_not_installed("bowtie")
def install_bowtie(env):
    """Install the bowtie short read aligner.
    """
    version = "0.12.7"
    url = "http://downloads.sourceforge.net/project/bowtie-bio/bowtie/%s/" \
          "bowtie-%s-src.zip" % (version, version)
    _get_install(url, env, _make_copy("find -perm -100 -name 'bowtie*'"))

@_if_not_installed("bwa")
def install_bwa(env):
    version = "0.5.9rc1"
    url = "http://downloads.sourceforge.net/project/bio-bwa/bwa-%s.tar.bz2" % (
            version)
    def _fix_makefile():
        arch = run("uname -m")
        # if not 64bit, remove the appropriate flag
        if arch.find("x86_64") == -1:
            run("sed -i.bak -r -e 's/-O2 -m64/-O2/g' Makefile")
    _get_install(url, env, _make_copy("ls -1 bwa solid2fastq.pl qualfa2fq.pl",
                                        _fix_makefile))

@_if_not_installed("bfast")
def install_bfast(env):
    version = "0.6.4"
    vext = "e"
    url = "http://downloads.sourceforge.net/project/bfast/bfast/%s/bfast-%s%s.tar.gz"\
            % (version, version, vext)
    _get_install(url, env, _configure_make)

@_if_not_installed("perm")
def install_perm(env):
    version = "0.3.3"
    url = "http://perm.googlecode.com/files/PerM%sSource.zip" % version
    def gcc44_makefile_patch():
        gcc_cmd = "g++44"
        with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                      warn_only=True):
            result = run("%s -v" % gcc_cmd)
        print result.return_code
        if result.return_code == 0:
            sed("makefile", "g\+\+", gcc_cmd)
    _get_install(url, env, _make_copy("ls -1 perm", gcc44_makefile_patch))

@_if_not_installed("gmap")
def install_gmap(env):
    version = "2010-07-27"
    url = "http://research-pub.gene.com/gmap/src/gmap-gsnap-%s.tar.gz" % version
    _get_install(url, env, _configure_make)

def _wget_with_cookies(ref_url, dl_url):
    run("wget --cookies=on --keep-session-cookies --save-cookies=cookie.txt %s"
            % (ref_url))
    run("wget --referer=%s --cookies=on --load-cookies=cookie.txt "
        "--keep-session-cookies --save-cookies=cookie.txt %s" %
        (ref_url, dl_url))

@_if_not_installed("novoalign")
def install_novoalign(env):
    base_version = "V2.07.09"
    cs_version = "V1.01.09"
    _url = "http://www.novocraft.com/downloads/%s/" % base_version
    ref_url = "http://www.novocraft.com/main/downloadpage.php"
    base_url = "%s/novocraft%s.gcc.tar.gz" % (_url, base_version)
    cs_url = "%s/novoalignCS%s.gcc.tar.gz" % (_url, cs_version)
    install_dir = os.path.join(env.system_install, "bin")
    with _make_tmp_dir() as work_dir:
        with cd(work_dir):
            _wget_with_cookies(ref_url, base_url)
            run("tar -xzvpf novocraft%s.gcc.tar.gz" % base_version)
            with cd("novocraft"):
                for fname in ["isnovoindex", "novo2maq", "novo2paf",
                        "novo2sam.pl", "novoalign", "novobarcode",
                        "novoindex", "novope2bed.pl", "novorun.pl",
                        "novoutil"]:
                    sudo("mv %s %s" % (fname, install_dir))
    with _make_tmp_dir() as work_dir:
        with cd(work_dir):
            _wget_with_cookies(ref_url, cs_url)
            run("tar -xzvpf novoalignCS%s.gcc.tar.gz" % cs_version)
            with cd("novoalignCS"):
                for fname in ["novoalignCS"]:
                    sudo("mv %s %s" % (fname, install_dir))

@_if_not_installed("lastz")
def install_lastz(env):
    version = "1.02.00"
    url = "http://www.bx.psu.edu/miller_lab/dist/" \
          "lastz-%s.tar.gz" % version
    _get_install(url, env, _make_copy("find -perm -100 -name 'lastz'"))

# --- Analysis

@_if_not_installed("fastq_quality_boxplot_graph.sh")
def install_fastx_toolkit(env):
    version = "0.0.13"
    gtext_version = "0.6"
    url_base = "http://hannonlab.cshl.edu/fastx_toolkit/"
    fastx_url = "%sfastx_toolkit-%s.tar.bz2" % (url_base, version)
    gtext_url = "%slibgtextutils-%s.tar.bz2" % (url_base, gtext_version)
    _get_install(gtext_url, env, _configure_make)
    _get_install(fastx_url, env, _configure_make)

@_if_not_installed("SolexaQA.pl")
def install_solexaqa(env):
    version = "1.4"
    url = "http://downloads.sourceforge.net/project/solexaqa/src/" \
            "SolexaQA_v.%s.pl.zip" % version
    with _make_tmp_dir() as work_dir:
        with cd(work_dir):
            run("wget %s" % url)
            run("unzip %s" % os.path.basename(url))
            sudo("mv SolexaQA.pl %s" % os.path.join(env.system_install, "bin"))

def install_picard(env):
    version = "1.41"
    url = "http://downloads.sourceforge.net/project/picard/" \
          "picard-tools/%s/picard-tools-%s.zip" % (version, version)
    install_dir = _symlinked_java_version_dir("picard", version)
    if install_dir:
        with _make_tmp_dir() as work_dir:
            with cd(work_dir):
                run("wget %s" % (url))
                run("unzip %s" % os.path.basename(url))
                with cd(os.path.splitext(os.path.basename(url))[0]):
                    sudo("mv *.jar %s" % install_dir)

def install_gatk(env):
    version = "1.0.5506"
    ext = ".tar.bz2"
    url = "ftp://ftp.broadinstitute.org/pub/gsa/GenomeAnalysisTK/"\
          "GenomeAnalysisTK-%s%s" % (version, ext)
    install_dir = _symlinked_java_version_dir("gatk", version)
    if install_dir:
        with _make_tmp_dir() as work_dir:
            with cd(work_dir):
                run("wget %s" % (url))
                run("tar -xjvpf %s" % os.path.basename(url))
                with cd(os.path.basename(url).replace(ext, "")):
                    sudo("mv *.jar %s" % install_dir)

def install_snpeff(env):
    version = "1_9"
    genomes = ["hg37.61", "mm37.61"]
    url = "http://downloads.sourceforge.net/project/snpeff/" \
          "snpEff_v%s_core.zip" % version
    genome_url_base = "http://downloads.sourceforge.net/project/snpeff/"\
                      "databases/v%s/snpEff_v%s_%s.zip"
    install_dir = _symlinked_java_version_dir("snpeff", version)
    if install_dir:
        with _make_tmp_dir() as work_dir:
            with cd(work_dir):
                dir_name = _fetch_and_unpack(url)
                with cd(dir_name):
                    sudo("mv *.jar %s" % install_dir)
                    run("sed -i.bak -r -e 's/data_dir = \.\/data\//data_dir = %s\/data/' %s" %
                        (install_dir.replace("/", "\/"), "snpEff.config"))
                    sudo("mv *.config %s" % install_dir)
                    data_dir = os.path.join(install_dir, "data")
                    sudo("mkdir %s" % data_dir)
                    for org in genomes:
                        if not exists(os.path.join(data_dir, org)):
                            gurl = genome_url_base % (version, version, org)
                            _fetch_and_unpack(gurl, need_dir=False)
                            sudo("mv data/%s %s" % (org, data_dir))

@_if_not_installed("freebayes")
def install_freebayes(env):
    repository = "git clone git://github.com/ekg/freebayes.git"
    _get_install(repository, env, _make_copy("ls -1 bin/*"))

@_if_not_installed("intersectBed")
def install_bedtools(env):
    repository = "git clone git://github.com/arq5x/bedtools.git"
    _get_install(repository, env, _make_copy("ls -1 bin/*"))

def _install_samtools_libs(env):
    repository = "svn co --non-interactive " \
                 "https://samtools.svn.sourceforge.net/svnroot/samtools/trunk/samtools"
    def _samtools_lib_install(env):
        lib_dir = os.path.join(env.system_install, "lib")
        include_dir = os.path.join(env.system_install, "include", "bam")
        run("make")
        sudo("mv -f libbam* %s" % lib_dir)
        sudo("mkdir -p %s" % include_dir)
        sudo("mv -f *.h %s" % include_dir)
    check_dir = os.path.join(env.system_install, "include", "bam")
    if not exists(check_dir):
        _get_install(repository, env, _samtools_lib_install)

@_if_not_installed("tophat")
def install_tophat(env):
    _install_samtools_libs(env)
    version = "1.2.0"
    def _fixseqan_configure_make(env):
        """Upgrade local copy of SeqAn before compiling to fix errors.

        http://seqanswers.com/forums/showthread.php?t=9082
        """
        with cd("src/SeqAn-1.1"):
            run("wget http://www.seqan.de/uploads/media/Seqan_Release_1.2.zip")
            run("rm -rf seqan")
            run("unzip Seqan_Release_1.2.zip")
        _configure_make(env)
    url = "http://tophat.cbcb.umd.edu/downloads/tophat-%s.tar.gz" % version
    _get_install(url, env, _fixseqan_configure_make)

@_if_not_installed("cufflinks")
def install_cufflinks(env):
    # XXX problems on CentOS with older default version of boost libraries
    _install_samtools_libs(env)
    version = "0.9.3"
    url = "http://cufflinks.cbcb.umd.edu/downloads/cufflinks-%s.tar.gz" % version
    _get_install(url, env, _configure_make)

# --- Assembly

@_if_not_installed("ABYSS")
def install_abyss(env):
    # XXX check for no sparehash on non-ubuntu systems
    version = "1.2.6"
    url = "http://www.bcgsc.ca/downloads/abyss/abyss-%s.tar.gz" % version
    _get_install(url, env, _configure_make)

def install_transabyss(env):
    version = "1.2.0"
    url = "http://www.bcgsc.ca/platform/bioinfo/software/trans-abyss/" \
          "releases/%s/trans-ABySS-v%s.tar.gz" % (version, version)
    _get_install_local(url, env, _make_copy(do_make=False))

@_if_not_installed("velvetg")
def install_velvet(env):
    version = "1.0.13"
    url = "http://www.ebi.ac.uk/~zerbino/velvet/velvet_%s.tgz" % version
    _get_install(url, env, _make_copy("find -perm -100 -name 'velvet*'"))

def install_trinity(env):
    version = "03122011"
    url = "http://downloads.sourceforge.net/project/trinityrnaseq/" \
          "trinityrnaseq-%s.tgz" % version
    _get_install_local(url, env, _make_copy())
