# -*- coding: utf-8 -*-

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
from collections import defaultdict

log = core.getLogger()

# Limite de pacotes por segundo
THRESHOLD = 10

class MitigacaoSimplesDDoS(object):
    def __init__(self):
        self.packet_counts = defaultdict(int)
        self.blocked_hosts = set()
        core.openflow.addListeners(self)
        Timer(1, self._reset_counts, recurring=True)
        log.info('Controlador DDoS Mitigation inicializado')

    def _reset_counts(self):
        self.packet_counts.clear()

    def _handle_PacketIn(self, event):
        packet = event.parsed
        in_port = event.port
        src_mac = str(packet.src)

        # Descarta pacote para host bloqueado
        if src_mac in self.blocked_hosts:
            log.info('Bloqueando pacote de %s', src_mac)
            return

        # Verificar se o pacote é ICMP
        if packet.find("icmp"):
            self.packet_counts[src_mac] += 1
            if self.packet_counts[src_mac] > THRESHOLD:
                log.info('Bloqueando host %s', src_mac)
                self.blocked_hosts.add(src_mac)
                # Insere regra para bloquear o host
                msg = of.ofp_flow_mod()
                msg.match.dl_src = packet.src
                msg.actions = []
                msg.priority = 65535
                event.connection.send(msg)
                return

        # Instala fluxo para tráfego
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, in_port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)
        log.info('Permitindo tráfego de %s', src_mac)

def launch():
    core.registerNew(MitigacaoSimplesDDoS)
