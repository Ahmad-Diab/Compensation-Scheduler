# Compensation-System Installation Guide

In order to get the project up and running we need to install swi-prolog & django framework which uses Python3 along with some additional packages

## Install SWI-PROLOG
> - Install **SWI-PROLOG** version **7.6.4** you can find it here [SWI-Prolog downloads](https://www.swi-prolog.org/download/stable?show=all)


## Install Python3
> - Install **Python3** version **3.8.0** you can find it here [Download Python \| Python.org](https://www.python.org/downloads/)
> - Then make sure that the python package installer ``pip`` is installed 
  > > - **macOS :** Open a new terminal window       and run the following command ``pip3 -V`` 
  > > - **Windows :** In the command line and run this command ``pip --version``

## Install Django Framework
> - **macOS :** Open a new terminal window and run this command ``pip3 install django``
> - **Windows :** In the command line and run this command ``pip install django``

## Install PySwip
> - **macOS :** Open a new terminal window and run this command ``pip3 install pyswip`` followed by these commands ``export PATH=$PATH:/Applications/SWI-Prolog.app/Contents/swipl/bin/x86_64-darwin15.6.0 
`` and ``export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/swipl/lib/x86_64-darwin15.6.0``
> - **Windows :** In the command line and run this command ``pip install pyswip``
