import time

from supervisor_simple.states import OverallState


def report_writer(state: OverallState):
    time.sleep(3)
    print("report_writer node activated!!")
    pass
