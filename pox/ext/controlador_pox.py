from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
from collections import defaultdict

log = core.getLogger()

# Limite de pacotes por segundo
THRESHOLD = 5

class ControladorMitigacaoEControle(object):
    """
    Este controlador POX trata de prover segurança à rede,
    mitigando ataques de negação de serviço e políticas de acesso, simulando VLANs.

    Funcionalidades:
    1. Mitigação de Dos e DDoS:
        - Observa o fluxo ICMP dos hosts.
        - Bloqueia hosts que enviarem mais de 5 pacotes ICMP por segundo.
    
    2. Controle de Acesso:
        - Simula comportamento de VLANs ao bloquear comunicação de hosts específicos.
        - Impede a comunicação de 'h1' e 'h2' com 'h3' e 'h4'.
    """
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
        dst_mac = str(packet.dst)

        # Controle de acesso para simular VLAN
        vlan_block = [
            ('00:00:00:00:00:01', '00:00:00:00:00:03'), # Impede h1 -> h3
            ('00:00:00:00:00:01', '00:00:00:00:00:04'), # Impede h1 -> h4
            ('00:00:00:00:00:02', '00:00:00:00:00:03'), # Impede h2 -> h3
            ('00:00:00:00:00:02', '00:00:00:00:00:04'), # Impede h2 -> h4
            ('00:00:00:00:00:03', '00:00:00:00:00:01'), # Impede h3 -> h1
            ('00:00:00:00:00:03', '00:00:00:00:00:02'), # Impede h3 -> h2
            ('00:00:00:00:00:04', '00:00:00:00:00:01'), # Impede h4 -> h1
            ('00:00:00:00:00:04', '00:00:00:00:00:02')  # Impede h4 -> h2
        ]

        for src, dst in vlan_block:
            if src_mac == src and dst_mac == dst:
                log.info('Bloqueando comunicação entre %s e %s', src, dst)
                return

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
    core.registerNew(ControladorMitigacaoEControle)
