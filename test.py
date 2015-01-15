from client import OEISClient
import time


c = OEISClient()
print 'boopdeboop'
start = time.time()
l = c.lookup_by_author('sloane', max_seqs=50)
print time.time() - start
