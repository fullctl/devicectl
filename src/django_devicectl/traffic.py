import os
import time

import fullctl.graph.mrtg.rrd as mrtg_rrd
from django.conf import settings

def start_time_and_duration(start_time: int, duration: int):
    """
    Helper function to return start_time and duration
    """

    if not start_time:
        start_time = int(time.time())
    else:
        start_time = int(start_time)

    if not duration:
        duration = 86400
    else:
        duration = int(duration)

    return start_time, duration


def get_traffic_for_obj(obj: object, start_time: int, duration: int):
    """
    Loads traffic data for object (device, physical port, virtual port etc.)
    """

    start_time, duration = start_time_and_duration(start_time, duration)

    if not getattr(obj, "meta", None) or "graph" not in obj.meta:
        return []

    graph_file = os.path.join(settings.GRAPHS_PATH, obj.meta.get("graph"))

    if not os.path.exists(graph_file):
        return {}

    traffic_data = mrtg_rrd.load_rrd_file(graph_file, start_time, duration)
    traffic_data = sorted(traffic_data, key=lambda x: -x["timestamp"])

    # set id on each data point
    for data_point in traffic_data:
        data_point["id"] = obj.id

    return traffic_data


def get_traffic_for_group(group_type: str, id: str, start_time: int, duration: int):
    """
    Loads traffic data for group of objects (device, physical port, virtual port etc.)
    """

    start_time, duration = start_time_and_duration(start_time, duration)

    if group_type not in ["ixctl-ix", "peers"]:
        raise ValueError(f"Unknown group type {group_type}")

    try:
        map(int, str(id).split("-"))
    except ValueError:
        raise ValueError(f"Invalid id(s) {id}")

    graph_file = os.path.join(settings.GRAPHS_PATH, f"{group_type}-{id}.rrd")

    if not os.path.exists(graph_file):
        return []

    traffic_data = mrtg_rrd.load_rrd_file(graph_file, start_time, duration)
    traffic_data = sorted(traffic_data, key=lambda x: -x["timestamp"])

    # set id on each data point
    for data_point in traffic_data:
        data_point["id"] = id

    return traffic_data



def update_peer_traffic(data: dict, virtual_ports: list):
    """
    Updates traffic data for two virtual ports (peers)

    Note: data["ids"] order needs to be the same as virtual_ports order

    There should be two virtual ports in the list

    The virtual port with the lowest id should be first in the list
    """


    ids = sorted(data["ids"])
    virtual_ports = sorted(virtual_ports, key=lambda x: x.id)

    bps_in = data["bps_in"]
    bps_out = data["bps_out"]
    timestamp = data["timestamp"]
    bps_in_max = data["bps_in_max"]
    bps_out_max = data["bps_out_max"]

    graph_path = os.path.join(settings.GRAPHS_PATH, f"peers-{ids[0]}-{ids[1]}.rrd")

    if not os.path.exists(graph_path):
        mrtg_rrd.create_rrd_file(graph_path, timestamp)

    last_update = mrtg_rrd.get_last_update_time(graph_path)

    key = f"graph-peer-{ids[1]}"
    if key not in virtual_ports[0].meta:
        virtual_ports[0].meta[key] = graph_path
        virtual_ports[0].save()
    
    key = f"graph-peer-{ids[0]}"
    if key not in virtual_ports[1].meta:
        virtual_ports[1].meta[key] = graph_path
        virtual_ports[1].save()

    mrtg_rrd.update_rrd(
        graph_path,
        f"{timestamp} {bps_in} {bps_out} {bps_in_max} {bps_out_max}",
        last_update,
    )