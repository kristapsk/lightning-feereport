# lightning-feereport

[![tippin.me](https://badgen.net/badge/%E2%9A%A1%EF%B8%8Ftippin.me/@kristapsk/F0918E)](https://tippin.me/@kristapsk)

feereport plugin for c-lightning

This plugin for c-lightning emulates `lncli feereport` command of LND.

Allows the caller to obtain a report detailing the current fee schedule
enforced by the node globally for each channel.

Active the plugin with:
`lightningd --plugin=PATH_TO_PLUGIN/feereport.py`

Call the plugin with:
`lightning-cli feereport`

For full functionality needs c-lightning v0.7.1 or newer.
