import datetime

from backtrader.feeds import GenericCSVData

class GenericCSV_BaoShare(GenericCSVData):
    # Add a 'pe' line to the inherited ones from the base class
    lines = ('amount',)

    # openinterest in GenericCSVData has index 7 ... add 1
    # add the parameter to the parameters inherited from the base class
    params = (
        ('fromdate', datetime.datetime(2012, 1, 1)),
        ('todate', datetime.datetime(2022, 12, 30)),
        ('nullvalue', 0.0),
        ('dtformat', ('%Y-%m-%d')),
        ('datetime', 1),
        ('time', -1),
        ('high', 4),
        ('low', 5),
        ('open', 3),
        ('close', 6),
        ('volume', 8),
        ('amount', 9),
        ('reverse', False),
        ('openinterest', -1),
    )
    #params = (('code', 8), ('amount', 9))