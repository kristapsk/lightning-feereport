#!/usr/bin/env python3
"""This plugin for c-lightning emulates `lncli feereport` command of LND.

Allows the caller to obtain a report detailing the current fee schedule
enforced by the node globally for each channel.

Active the plugin with:
`lightningd --plugin=PATH_TO_PLUGIN/feereport.py`

Call the plugin with:
`lightning-cli feereport`

Author: Kristaps Kaupe (https://github.com/kristapsk)
"""

from datetime import datetime, timedelta
from lightning import LightningRpc, Plugin
from os.path import join

rpc = None
plugin = Plugin(autopatch=True)
our_nodeid = None


@plugin.method("feereport")
def feereport(plugin=None):
    """Returns the current fee policies of all active channels."""

    channels = rpc.listfunds()["channels"]
    channel_fees = []
    for channel in channels:
        # pending channels will not have short_channel_id, ignore them
        if "short_channel_id" in channel:
            channel_detail = rpc.listchannels(
                channel["short_channel_id"])["channels"]
            for detail in channel_detail:
                if detail["source"] == our_nodeid:

                    if "funding_output" in channel:
                        funding_output = str(channel["funding_output"])
                    else:
                        # funding_output isn't returned in v0.7.1, but we can
                        # get it from short_channel_id too
                        short_channel_id_parts = (
                            channel["short_channel_id"].split("x"))
                        funding_output = short_channel_id_parts[2]

                    channel_fees.append({
                        "chan_point": (
                            channel["funding_txid"] + ":" + funding_output),
                        "base_fee_msat": str(detail["base_fee_millisatoshi"]),
                        "fee_per_mil": str(detail["fee_per_millionth"]),
                        "fee_rate": "%.8f" % float(
                            detail["fee_per_millionth"] / 1000000)
                    })

                    break

    fee_data = ((fwd["fee"], fwd["resolved_time"])
                for fwd in rpc.listforwards()["forwards"]
                if fwd["status"] == "settled" and "resolved_time" in fwd)
    now = datetime.now()
    day_ago = (now - timedelta(hours=24)).timestamp()
    week_ago = (now - timedelta(days=7)).timestamp()
    month_ago = (now - timedelta(days=30)).timestamp()
    day_fee_sum = 0
    week_fee_sum = 0
    month_fee_sum = 0
    for fwd in fee_data:
        fee_msat = fwd[0]
        resolved_time = fwd[1]
        if resolved_time > month_ago:
            month_fee_sum += fee_msat
            if resolved_time > week_ago:
                week_fee_sum += fee_msat
                if resolved_time > day_ago:
                    day_fee_sum += fee_msat

    return {
        "channel_fees": channel_fees,
        "day_fee_sum": str(int(day_fee_sum / 1000)),
        "week_fee_sum": str(int(week_fee_sum / 1000)),
        "month_fee_sum": str(int(month_fee_sum / 1000)),
    }


@plugin.init()
def init(options, configuration, plugin):
    global rpc, our_nodeid
    plugin.log("feereport init")
    path = join(configuration["lightning-dir"], configuration["rpc-file"])
    rpc = LightningRpc(path)
    info = rpc.getinfo()
    our_nodeid = info["id"]


plugin.run()
