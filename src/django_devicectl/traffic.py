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



def update_peer_traffic(data: dict, virtual_ports: dict):
    """
    Updates traffic data for two virtual ports (peers)
    """

    from_port = data["from_port"]
    to_port = data["to_port"]

    bps_in = data["bps_in"]
    bps_out = data["bps_out"]
    timestamp = data["timestamp"]
    bps_in_max = data["bps_in_max"]
    bps_out_max = data["bps_out_max"]

    graph_path_from_port = os.path.join(settings.GRAPHS_PATH, f"peers-{from_port}-{to_port}.rrd")
    graph_path_to_port = os.path.join(settings.GRAPHS_PATH, f"peers-{to_port}-{from_port}.rrd")

    if not os.path.exists(graph_path_from_port):
        mrtg_rrd.create_rrd_file(graph_path_from_port, timestamp)

    if not os.path.exists(graph_path_to_port):
        mrtg_rrd.create_rrd_file(graph_path_to_port, timestamp)

    last_update_from = mrtg_rrd.get_last_update_time(graph_path_from_port)
    last_update_to = mrtg_rrd.get_last_update_time(graph_path_to_port)

    key = f"graph-peer-{to_port}"
    if key not in virtual_ports[from_port].meta:
        virtual_ports[from_port].meta[key] = graph_path_from_port
        virtual_ports[from_port].save()
    
    key = f"graph-peer-{from_port}"
    if key not in virtual_ports[to_port].meta:
        virtual_ports[to_port].meta[key] = graph_path_to_port
        virtual_ports[to_port].save()

    mrtg_rrd.update_rrd(
        graph_path_from_port,
        f"{timestamp} {bps_in} {bps_out} {bps_in_max} {bps_out_max}",
        last_update_from,
    )

    mrtg_rrd.update_rrd(
        graph_path_to_port,
        f"{timestamp} {bps_out} {bps_in} {bps_out_max} {bps_in_max}",
        last_update_to,
    )