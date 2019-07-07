# Bank terms comparer
Deobfuscate tons of lawspeek! Automatically!

## How to
Just use script within your archive folder.
It will show you whole terms (when run the first time) or just diff between the last terms in archive and the most recent terms (downloaded from site).

You can make an alias for that, like so:
```shell
alias compare-bank-terms='( [ -d $HOME/bank-terms-archive ] || mkdir -p $HOME/bank-terms-archive ) && cd $HOME/bank-terms-archive && python3 <script-path>/compare_bank_terms.py && cd - >/dev/null'
```