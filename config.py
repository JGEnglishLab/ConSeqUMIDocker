from typing import List

LAST_TRAIN_PATH = {"ltp":"/app/promethion.mat"}
lamassembleCommandLine = f"lamassemble mat_path_filled_in_programmatically --end -g60 -m 40"

LCOMMAND: List[str] = lamassembleCommandLine.split()

medakaCommandLine = "medaka_consensus -f -m r941_min_high_g303"
MCOMMAND = medakaCommandLine.split()

#This config.py is made for the docker image.
#It will replace ConSeqUMI/src/ConSeqUMI/consensus/config.py from the git repo https://github.com/JGEnglishLab/ConSeqUMI that is cloned into the dockerfile
#We do this so the docker image defaults to use the "last train" file from here https://gitlab.com/mcfrith/lamassemble/-/blob/master/train/promethion.mat
#If the user wishes to use a different "last train" file they may do so using the "Input Last Train Path For Lamassemble" option
#If they wish to use the default "last train" they should leave the "Input Last Train Path For Lamassemble" option blank