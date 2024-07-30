# Projeto de Mitigação de Ataques DoS e DDoS usando SDN

Este projeto implementa uma topologia SDN usando Mininet e modifica um controlador POX para mitigar ataques de negação de serviço (DoS) e negação de serviço distribuído (DDoS).

## Requisitos

- Mininet
- POX

## Topologia da rede equivalente (Cisco Packet Tracer)

![Topologia da Rede](./images/topologia.png)

## Instruções

### 1. Configurar e Iniciar o Controlador POX

.Inserir o script controlador_pox na pasta /pox/ext
.Ir até a pasta onde o controlador POX está instalado e execute o controlador modificado:

```bash
cd ~/pox
./pox.py controlador_pox
