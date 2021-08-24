class flow_info:
    def __init__(self, src=None, dst=None, period=None, size=None, bandwidth=None, deadline=None, allocated_path=None) -> None:
        self.src = src
        self.dst = dst
        self.period = period
        self.size = size
        self.bandwidth = bandwidth
        self.allocated_path = allocated_path