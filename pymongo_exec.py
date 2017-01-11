import constants
import matlab.engine
eng = matlab.engine.start_matlab()
eng.cd(constants.MATLAB_DIR)

#ret = eng.triarea(1.0,5.0)

ret = eng.script_runme(nargout=0)

print(ret)