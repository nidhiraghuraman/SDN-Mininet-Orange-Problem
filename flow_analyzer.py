from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
from pox.lib.recoco import Timer
import logging

logging.getLogger("packet").setLevel(logging.CRITICAL)

log = core.getLogger()

switches = {}

# Switch Connection
def _handle_ConnectionUp(event):
    dpid = dpidToStr(event.dpid)
    switches[event.dpid] = event.connection
    log.info("Switch %s connected", dpid)

# Packet-In Handler 
def _handle_PacketIn(event):
    try:
        packet = event.parsed

        # Ignore invalid packets
        if packet is None:
            return

        # Ignore IPv6 (removes DNS + noise issues)
        if packet.type == 0x86dd:
            return

        src = packet.src.toStr()

        #  BLOCK ONLY h1
        if src == "00:00:00:00:00:01":
            log.info("Blocked traffic from %s", src)
            return

        #  ALLOW all other traffic
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)

        # Forward (Flood) 
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))

        event.connection.send(msg)

    except Exception as e:
        log.error("Packet error handled: %s", e)

# Request Flow Stats
def request_stats():
    for conn in switches.values():
        req = of.ofp_stats_request(body=of.ofp_flow_stats_request())
        conn.send(req)

# Flow Stats Handler
def _handle_FlowStatsReceived(event):
    dpid = dpidToStr(event.connection.dpid)

    active = 0
    unused = 0

    for stat in event.stats:

        # Skip empty flows
        if stat.packet_count == 0 and stat.byte_count == 0:
            continue

        if stat.packet_count > 0:
            active += 1
        else:
            unused += 1

    print(f"Switch {dpid} → Active: {active}, Unused: {unused}")

# Launch Controller
def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    core.openflow.addListenerByName("FlowStatsReceived", _handle_FlowStatsReceived)

    Timer(20, request_stats, recurring=True)

    log.info("....Flow Analyzer Controller Started....")
