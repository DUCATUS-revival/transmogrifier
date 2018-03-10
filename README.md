Transmogrifier
--------------

Automated transaction bot for Ducatus.

    usage: transmogrifier.py [-h] [-c COUNT] [-r RATE] [-x MAX] [-m MIN] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -c COUNT, --count COUNT
                            The number of wallets to create and use
      -r RATE, --rate RATE  The number of transactions to send per hour
      -x MAX, --max MAX     The maximum size of transactions to send
      -m MIN, --min MIN     The minimum size of transactions to send
      -v, --verbose         Verbose mode

Output is in JSON, each line is an array following the general syntax [ type, time, args... ]
for example, ["transfer", "2018-03-10T04:54:35Z", "account1", "LuzZiSBcv6n7eQKGEtd1ZgLwXi1eLrmCem", 0.513354]

Before running, ensure you have started ducatuscoind. Run in verbose mode for more info.

Transaction intervals are exponentially distributed with a mean rate specified.
Transaction amounts are uniformly distributed between minimum and either account/address totals or maximum.
Destination addresses are randomly selected.

Fees spent are left at default (variable, apparently going rate)

