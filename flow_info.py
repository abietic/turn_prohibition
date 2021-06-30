class flow_info:
    def __init__(self, src, dst, period, size, bandwidth) -> None:
        self.src = src
        self.dst = dst
        self.period = period
        self.size = size
        self.bandwidth = bandwidth