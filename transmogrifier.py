import argparse, subprocess, json, time, random
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--poolcutoff", type=int, default=2, help="Don't send new transactions if there are already at least this many in the mempool")
parser.add_argument("-c", "--count", type=int, default=3, help="The number of wallets to create and use")
parser.add_argument("-r", "--rate", type=int, default=6, help="The number of transactions to send per hour")
parser.add_argument("-x", "--max", type=int, default=10, help="The maximum size of transactions to send")
parser.add_argument("-m", "--min", type=int, default=1, help="The minimum size of transactions to send")
parser.add_argument("-v", "--verbose", help="Verbose mode", action="store_true")
args = parser.parse_args()

# ISO 8601-ish
def timestr():
  return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# pick a random transaction size (uniform distribution)
def gettxnsize(acctmax):
  return random.randrange(round(args.min * 1000), round(min(acctmax, args.max) * 1000)) / 1000.0

# Send a transaction
def sendtxn(acctname, tgtaddr, size):
  print(json.dumps(["transfer", timestr(), acctname, tgtaddr, size]))
  subprocess.check_output(['ducatuscoin-cli', 'sendfrom', acctname, tgtaddr, str(size)])
  #ducatuscoin-cli sendfrom "" "Lj36yRsnQAPPsHtqJyS1UCPxCf4hTYqkn9" 10

if args.verbose:
  print(json.dumps(["infom", timestr(), "Adding nodes to daemon."]))

# Preconfigure network
for i in range(0,5):
  try:
    subprocess.check_output(['ducatuscoin-cli','addnode','snode-%d.ducatus.io' % i,'add'])
  except:
    pass #these may already be added. No prob.

#load up initial account totals
accttotals = json.loads(subprocess.check_output(['ducatuscoin-cli','listaccounts']))
if args.verbose:
  print(json.dumps(["totals", timestr(), accttotals]))

#load up addresses
addrs = {}
for acctname in accttotals:
  acctaddrs = json.loads(subprocess.check_output(['ducatuscoin-cli', 'getaddressesbyaccount', acctname]))
  addrs[acctname] = acctaddrs[0]

#verify you have enough accounts
for i in range(0, args.count):
  acctname = "account%d" % i
  if acctname not in accttotals and len(accttotals) < args.count:
    print(json.dumps(["create", timestr(), acctname, "Creating account"]))
    addrs[acctname] = subprocess.check_output(['ducatuscoin-cli','getnewaddress',acctname])
    print(json.dumps(["addr", timestr(), addrs[acctname], "New address"]))
    accttotals[acctname] = 0

#Run transaction scheduler loop
while True:
  delay = random.expovariate(1) * 3600.0 / args.rate
  if args.verbose:
    print(json.dumps(["infod", timestr(), delay, "delay"]))
  time.sleep(delay) #delay
  if args.verbose:
    print(json.dumps(["infog", timestr(), "Generating transaction (target average: %d per hour)" % args.rate]))
  #Reload account values in case anything's changed
  accttotals = json.loads(subprocess.check_output(['ducatuscoin-cli','listaccounts']))
  if args.verbose:
    print(json.dumps(["totals", timestr(), accttotals]))
  for acctname in accttotals:
    if acctname not in addrs:
      addrs[acctname] = json.loads(subprocess.check_output(['ducatuscoin-cli', 'getaddressesbyaccount', acctname]))[0]
  #Get accounts with less than min xfer amount and consolidate
  #sort by size
  acctssorted = sorted(accttotals.iteritems(), key=lambda (k,v): (v,k))
  senttxn = False
  numtoskip = 0 # accts with too little in them
  for i in range(0, len(acctssorted) - 1):
    acctname = acctssorted[i][0]
    acctval = acctssorted[i][1]
    if acctval <= 0: #skip this account
      if args.verbose:
        print(json.dumps(["infos", timestr(), acctname, "skipping acct with 0 balance"]))
      continue
    if acctval < args.min: #consolidate
      print(json.dumps(["infoc", timestr(), acctname, "Consolidating account with less than min txn size"]))
      tgtaddr = addrs[acctssorted[i + 1][0]]
      senttxn = True
      sendtxn(acctname, tgtaddr, acctval)
      break
    numtoskip = i
  if senttxn: #we did it
    continue
  #Can we do a transaction?
  if numtoskip == len(acctssorted):
    print(json.dumps(["errorf", timestr(), "No accounts found with sufficient funds. Please transfer more in."]))
    continue
  #Now randomly fill out a transaction
  sendacct = random.choice(acctssorted[numtoskip:])[0]
  possibleaddrs = addrs.values()
  possibleaddrs.remove(addrs[sendacct]) #pick a destination that isn't us
  destacct = random.choice(possibleaddrs)
  sendtxn(sendacct, destacct, gettxnsize(acctval)) #send it
