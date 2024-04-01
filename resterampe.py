class nodes:

    def __init__(self, cores, maxcore, freq):
        self.cores = cores
        self.maxcore = maxcore
        self.prio = int(freq/100)

    def something(self):
        return self.prio



node14 = nodes(14, 12000, 2200)