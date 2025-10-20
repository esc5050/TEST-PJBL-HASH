# Firewall — Projeto SIGLA (README)

**Arquivo:** `README.md` — seção do projeto que descreve toda a parte de Firewall a ser entregue junto com o relatório e o arquivo do Packet Tracer.

---

## 1. Visão Geral

Este documento descreve a política de segurança, as regras do firewall (em português), exemplos de Access-Lists Cisco (sem estado), configurações de NAT e recomendações de implementação usadas no projeto da rede da empresa **SIGLA** (Matriz — São Paulo; Filial — Curitiba).

> **Observação:** os comandos abaixo usam placeholders para endereços IP e interfaces. Substitua `<...>` pelos endereços e nomes reais do seu ambiente antes de colar no Packet Tracer.

---

## 2. Política de Segurança (resumida, em Português)

1. Permitir apenas o tráfego necessário para as aplicações corporativas: HTTP (80), HTTPS (443), DNS (53) e ICMP (ping) para navegação e diagnóstico.
2. Permitir SIP (UDP 5060/5061) e RTP (UDP 10000–11000) **somente** entre as redes internas da Matriz e da Filial (site-to-site), e entre endpoints VoIP autorizados.
3. Publicar serviços (ERP/WWW/DNS) somente via NAT estático para IPs públicos designados; bloquear acesso direto a IPs privados internos.
4. Permitir gerenciamento de dispositivos (SSH/HTTPS) apenas a partir da VLAN de administração (rede Admin) da Matriz.
5. Política padrão: **negue todo o resto** (deny-by-default). Registrar eventos bloqueados importantes.
6. Documentar cada regra com justificativa, responsável e data.

---

## 3. Tabela de Regras (para inserir no relatório)

| ID | Origem                         | Destino                     | Protocolo | Portas / Faixa |       Ação       | Direção (relativa ao FW) | Observações                                         |
| -: | ------------------------------ | --------------------------- | --------- | -------------- | :--------------: | :----------------------: | --------------------------------------------------- |
| 10 | LAN_Matriz (VLANs de usuários) | Internet                    | TCP       | 80             |      PERMIT      |     inside → outside     | Navegação HTTP                                      |
| 11 | LAN_Matriz                     | Internet                    | TCP       | 443            |      PERMIT      |     inside → outside     | Navegação HTTPS                                     |
| 12 | LAN_Matriz                     | Servidor DNS (ISP/externo)  | UDP       | 53             |      PERMIT      |     inside → outside     | Resolução de nomes                                  |
| 13 | LAN_Matriz                     | Internet                    | ICMP      | any            |      PERMIT      |     inside → outside     | Diagnóstico controlado                              |
| 14 | LAN_Filial (VLANs de usuários) | Internet                    | TCP       | 80             |      PERMIT      |     inside → outside     | Navegação HTTP filial                               |
| 15 | LAN_Filial                     | Internet                    | TCP       | 443            |      PERMIT      |     inside → outside     | Navegação HTTPS filial                              |
| 16 | LAN_Filial                     | DNS                         | UDP       | 53             |      PERMIT      |     inside → outside     | Resolução de nomes filial                           |
| 17 | Matriz ↔ Filial                | Matriz ↔ Filial             | UDP/TCP   | 5060, 5061     |      PERMIT      |           both           | SIP entre sites (voz sinalização)                   |
| 18 | Matriz ↔ Filial                | Matriz ↔ Filial             | UDP       | 10000–11000    |      PERMIT      |           both           | RTP (áudio) entre sites                             |
| 19 | Rede Admin (Matriz)            | Dispositivos de rede        | TCP       | 22, 443        |      PERMIT      |      inside → device     | Gerenciamento seguro                                |
| 20 | Internet (qualquer)            | IP_PÚBLICO_SERVIDORES (NAT) | TCP       | 80             | PERMIT (via NAT) |     outside → inside     | Publicação ERP/WWW via NAT estático                 |
| 21 | Internet                       | IP_PÚBLICO_SERVIDORES       | TCP       | 443            | PERMIT (via NAT) |     outside → inside     | Publicação segura via NAT                           |
| 22 | Internet                       | Interno                     | UDP       | 5060,5061      |       DENY       |     outside → inside     | Bloquear SIP público por padrão                     |
| 30 | any                            | any                         | IP        | any            |       DENY       |           both           | Regra final: negar tudo e logar entradas relevantes |

**Explicação:** As regras 10–16 permitem saída iniciada por usuários. Em ambiente com NAT, o retorno é tratado pela tradução; em ACLs sem estado, posicione as listas onde façam sentido (na interface interna `in` ou externa `out`).

---

## 4. Exemplo de ACLs Cisco (sem estado) — prontas para ajustar

> Exemplo de plano de endereçamento (substitua se for diferente):
>
> * Matriz (Usuários): `172.28.10.0/24`
> * Filial (Usuários): `172.28.20.0/24`
> * Admin (Matriz): `172.28.99.0/24`
> * IP público exemplo para servidores: `104.109.10.2` (substituir pelo bloco público do professor/ISP)

### ACL para tráfego interno → Internet e tráfego site-to-site

```cisco
ip access-list extended ACL_INSIDE_OUT
 remark Permitir HTTP/HTTPS/DNS/ICMP Matriz e Filial
 permit tcp 172.28.10.0 0.0.0.255 any eq 80
 permit tcp 172.28.10.0 0.0.0.255 any eq 443
 permit udp 172.28.10.0 0.0.0.255 any eq 53
 permit icmp 172.28.10.0 0.0.0.255 any
 permit tcp 172.28.20.0 0.0.0.255 any eq 80
 permit tcp 172.28.20.0 0.0.0.255 any eq 443
 permit udp 172.28.20.0 0.0.0.255 any eq 53
 permit icmp 172.28.20.0 0.0.0.255 any
 remark SIP/RTP entre Matriz e Filial (endpoints internos)
 permit udp 172.28.10.0 0.0.0.255 172.28.20.0 0.0.0.255 eq 5060
 permit udp 172.28.10.0 0.0.0.255 172.28.20.0 0.0.0.255 eq 5061
 permit udp 172.28.10.0 0.0.0.255 172.28.20.0 0.0.0.255 range 10000 11000
 remark Gerenciamento (SSH/HTTPS) apenas da Rede Admin
 permit tcp 172.28.99.0 0.0.0.255 any eq 22
 permit tcp 172.28.99.0 0.0.0.255 any eq 443
 deny ip any any
```

**Aplicação de exemplo (interface interna / interface externa):**

```cisco
interface GigabitEthernet0/1   ! interna (LAN)
 ip access-group ACL_INSIDE_OUT in

interface GigabitEthernet0/0   ! externa (Internet)
 ip access-group ACL_OUTSIDE_IN in
```

### ACL para tráfego externo → IPs públicos NATeados (entrada)

```cisco
ip access-list extended ACL_OUTSIDE_IN
 remark Permitir HTTP/HTTPS aos servidores NATeados
 permit tcp any host 104.109.10.2 eq 80
 permit tcp any host 104.109.10.2 eq 443
 remark Bloquear SIP público
 deny udp any any eq 5060
 deny udp any any eq 5061
 deny ip any any
```

---

## 5. NAT (exemplos)

### Marcar interfaces inside/outside

```cisco
interface GigabitEthernet0/1
 ip nat inside
!
interface GigabitEthernet0/0
 ip nat outside
```

### NAT estático (public IP -> servidor interno)

```cisco
ip nat inside source static tcp <IP_SERVIDOR_WEB_INT> 80 <IP_PUB_WEB> 80
ip nat inside source static tcp <IP_SERVIDOR_WEB_INT> 443 <IP_PUB_WEB> 443
```

### NAT Overload (NATP) — usuários saindo para Internet

```cisco
access-list 10 permit 172.28.10.0 0.0.0.255
access-list 10 permit 172.28.20.0 0.0.0.255
ip nat inside source list 10 interface <IF_PUBLICA> overload
```

**Observação:** Para NAT estático e IPs públicos, adicione a rota no(s) roteador(es) dos ISPs apontando o bloco público para o firewall/roteador do lado da matriz (conforme instruções do enunciado).

---

## 6. Rotas de Exemplo

* Rota default (usar ISP1 como principal, ISP2 como backup):

```cisco
ip route 0.0.0.0 0.0.0.0 <IP_ISP1>
ip route 0.0.0.0 0.0.0.0 <IP_ISP2> 10
```

* Rota para bloco público dos servidores (em ambos os ISPs, se necessário):

```cisco
ip route <BLOCO_PUB_SERVIDORES> <MASK> <IP_FW>
```

---

## 7. Logging e Auditoria

* Ative `logging buffered 4096` no router/firewall.
* Em regras `deny` críticas, adicione `log` para capturar origens maliciosas.
* Gere evidências de testes (ping, acesso HTTP/HTTPS, chamadas VoIP) e inclua os logs no relatório.

---

## 8. Checklist para Entrega (Colar no README do GitHub)

* [ ] Política de segurança (incluída).
* [ ] Tabela de regras (incluída).
* [ ] ACLs de exemplo (incluídas).
* [ ] Exemplos de NAT (incluídos).
* [ ] Instruções para substituição de placeholders (incluídas).
* [ ] Logs e evidências dos testes (anexar no repositório).

---

## 9. Como substituir os placeholders (passo-a-passo rápido)

1. Troque todas as redes `172.28.X.X` se você recebeu outra faixa do professor (ex.: `172.16.X.X`).
2. Substitua `<IP_PUB_WEB>`, `<IP_SERVIDOR_WEB_INT>`, `<IF_PUBLICA>`, `<IP_ISP1>`, `<IP_ISP2>` pelos valores reais do seu ambiente.
3. Ajuste os nomes das interfaces conforme os routers/switches do Packet Tracer (ex.: `GigabitEthernet0/0`).
4. Teste cada serviço (HTTP, HTTPS, DNS, ping) e valide as regras de ACLs.

---

## 10. Exemplo de Plano de Endereçamento (sugestão, já pronto para colar)

* Matriz Usuários (VLAN 10): `172.28.10.0/24` — gateway `172.28.10.1` (switch L3)
* Filial Usuários (VLAN 20): `172.28.20.0/24` — gateway `172.28.20.1`
* Rede Admin (VLAN 99): `172.28.99.0/24` — gateway `172.28.99.1`
* Link p2p Matriz ↔ ISP1: `172.28.30.0/30`
* Link p2p Filial ↔ ISP2: `172.28.30.4/30`
* IP público exemplo (NAT): `104.109.10.2` → servidor web interno `172.28.10.10`

---

Se quiser, eu já adapto este README com **os IPs finais que você escolher** (por exemplo, se preferir usar `172.16.*` em vez de `172.28.*`) e deixo tudo pronto para colar diretamente no seu `README.md`. Basta me enviar o plano de endereçamento final (sub-redes internas e IPs públicos escolhidos).
