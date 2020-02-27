# signal-cli-wrapper

_A `bash` script for easier use of [signal-cli](https://github.com/AsamK/signal-cli)_

Usage: 

 * `sg snd <name> "message"` : Send to a name not a number
 * `sg gsnd <group-name> "message"` : Send to a group-name not an id
 * `sg rcv` : Get messages, which are written to a log file
 * `sg ids` : Check the phone numbers you have keys for
 * `sg log` : Read the logs more easily (to see receipts and read-receipts)
 * `sg cnv <name>` : Display a conversation:
 * `sg gcnv <group-name>` : Display a group conversation:
 
<img src="img/cnv.png" width="50%"/>

Also included: `checksg` a script to execute `sg rcv` and notify you via
`send-notify`; run it as a `cron` job.

## Installation

 1. Make the scripts executable (`chmod u+x sg`)
 2. Scripts and `signal-cli` must be in the shell’s `$PATH`
 3. Assign names to your numbers by editing the config. section of `sg` 
 4. (Optional) Add the full path to `sg` in `checksg` and add `checksg`
    to your `crontab`. E.g.: 

```    
0,10,20,30,40,50 * * * *   /home/foo/bin/checksg
```
