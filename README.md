# Firewall — Projeto JAG

## 1) Política de Segurança

1. Permitir somente o tráfego necessário para as aplicações corporativas: HTTP (80), HTTPS (443), DNS (53), ICMP (ping) a partir das redes internas para a Internet.
2. Permitir tráfego SIP (UDP 5060 e 5061) e RTP (UDP 10000–11000) somente entre os sites (Matriz ↔ Filial) e entre hosts VoIP autorizados, conforme arquitetura de telefonia IP.
3. Permitir serviços internos (ERP/HTTP, VoIP, DNS) apenas através de NAT estático para os IPs públicos designados; bloquear acesso direto a servidores internos sem NAT.
4. Permitir acesso de gerenciamento (SSH/Telnet/HTTPS) a dispositivos de rede somente a partir da sub-rede de administração (VLAN Admin) da Matriz.
5. Negar todo o restante por padrão (policy: **deny-by-default**). Registrar/logar tentativas bloqueadas críticas.
6. Manter regras simples e auditáveis (ACLs legíveis); documentar cada regra com justificativa e proprietário.

## 2) Tabela de Regras

| ID | Origem                               | Destino                                        | Protocolo | Portas / Faixa    |                            Ação                            |    Direção (relativa ao FW)    | Justificativa / Observações                                      |
| -: | ------------------------------------ | ---------------------------------------------- | --------- | ----------------- | :--------------------------------------------------------: | :----------------------------: | ---------------------------------------------------------------- |
| 10 | LAN_Matriz (todas VLANs de usuários) | Internet (qualquer)                            | TCP       | 80 (HTTP)         |                           PERMIT                           |        inside → outside        | Navegação web dos usuários                                       |
| 11 | LAN_Matriz                           | Internet                                       | TCP       | 443 (HTTPS)       |                           PERMIT                           |        inside → outside        | Navegação segura                                                 |
| 12 | LAN_Matriz                           | DNS_Resolver (ISP / externa)                   | UDP       | 53                |                           PERMIT                           |        inside → outside        | Resolução de nomes                                               |
| 13 | LAN_Matriz                           | Internet                                       | ICMP      | any               |                           PERMIT                           |        inside → outside        | Diagnóstico (ping) controlado                                    |
| 14 | LAN_Filial (todas VLANs de usuários) | Internet                                       | TCP       | 80                |                           PERMIT                           |        inside → outside        | Navegação web da filial                                          |
| 15 | LAN_Filial                           | Internet                                       | TCP       | 443               |                           PERMIT                           |        inside → outside        | Navegação segura da filial                                       |
| 16 | LAN_Filial                           | DNS_Resolver                                   | UDP       | 53                |                           PERMIT                           |        inside → outside        | Resolução de nomes                                               |
| 17 | Matriz ↔ Filial (sub-redes internas) | Matriz ↔ Filial                                | UDP / TCP | 5060,5061 (SIP)   |                           PERMIT                           | both directions (site-to-site) | Telefonia SIP entre sites                                        |
| 18 | Matriz ↔ Filial                      | Matriz ↔ Filial                                | UDP       | 10000–11000 (RTP) |                           PERMIT                           |         both directions        | Fluxo de mídia RTP (VoIP)                                        |
| 19 | Rede Admin (Matriz)                  | Equipamentos de Rede                           | TCP       | 22 (SSH), 443     |                           PERMIT                           |         inside → device        | Gerenciamento seguro somente pela VLAN Admin                     |
| 20 | Internet (origem qualquer)           | FW_Public_IP(s) (NAT estático para servidores) | TCP       | 80 (HTTP)         |                 PERMIT (para IP público A)                 |   outside → inside (via NAT)   | Publicação ERP/WWW (NAT estático)                                |
| 21 | Internet                             | FW_Public_IP(s)                                | TCP       | 443 (HTTPS)       |                 PERMIT (para IP público B)                 |   outside → inside (via NAT)   | Publicação segura de serviços                                    |
| 22 | Internet                             | FW_Public_IP(s)                                | UDP       | 5060,5061         | DENY (ou permitir somente se houver necessidade/operadora) |        outside → inside        | Bloquear SIP público por padrão; só abrir se for serviço público |
| 30 | Qualquer                             | Qualquer                                       | IP        | any               |                            DENY                            |        (aplicação final)       | Política padrão: negar todo o resto e logar entradas relevantes  |

**Notas:**

* As regras 10–16 são aplicadas para permitir saída (usuários iniciando conexões). O retorno das conexões geralmente é gerenciado por NAT/NAPT no router/firewall; com ACLs sem estado, a posição e a direção de aplicação do ACL devem ser planejadas (ver seção de exemplo de ACL abaixo).
* Para SIP/RTP entre sites, o ideal é deixar esse tráfego atravessar a VPN/site-to-site; como no Packet Tracer não se configura a VPN, o tráfego será permitido pela VPN e que as ACLs entre os roteadores do backbone permitirão essas portas.

## 3) Exemplo de Access-Lists Cisco

> **Premissas de exemplo:**
>
> * Rede interna Matriz: 172.16.10.0/24 (VLAN usuários Matriz)
> * Rede interna Filial: 172.16.20.0/24 (VLAN usuários Filial)
> * Rede Admin Matriz: 172.16.99.0/24
> * IP público (exemplo) para NAT: 104.109.10.0/29
> * IP público destinado ao servidor Web (ERP) da Matriz: 104.109.10.2

### ACL para permitir saída dos usuários (aplicar na interface interna, ou como apropriado)

ip access-list extended ACL_INSIDE_OUT
 remark Permitir HTTP/HTTPS/DNS/ICMP da Matriz para Internet
 permit tcp 172.16.10.0 0.0.0.255 any eq 80
 permit tcp 172.16.10.0 0.0.0.255 any eq 443
 permit udp 172.16.10.0 0.0.0.255 any eq 53
 permit icmp 172.16.10.0 0.0.0.255 any
 remark Permitir HTTP/HTTPS/DNS/ICMP da Filial para Internet
 permit tcp 172.16.20.0 0.0.0.255 any eq 80
 permit tcp 172.16.20.0 0.0.0.255 any eq 443
 permit udp 172.16.20.0 0.0.0.255 any eq 53
 permit icmp 172.16.20.0 0.0.0.255 any
 remark Permitir SIP/RTP entre Matriz e Filial (somente entre redes internas)
 permit udp 172.16.10.0 0.0.0.255 172.16.20.0 0.0.0.255 eq 5060
 permit udp 172.16.10.0 0.0.0.255 172.16.20.0 0.0.0.255 eq 5061
 permit udp 172.16.10.0 0.0.0.255 172.16.20.0 0.0.0.255 range 10000 11000
 remark Gerenciamento (SSH/HTTPS) apenas da Rede Admin
 permit tcp 172.16.99.0 0.0.0.255 any eq 22
 permit tcp 172.16.99.0 0.0.0.255 any eq 443
 remark Por fim negar todo o resto (opcional - se deseja explicitar)
 deny ip any any
```

**Aplicação de exemplo na interface:**

```
interface GigabitEthernet0/0   ! interface voltada para a Internet (exterior)
 ip access-group ACL_INSIDE_OUT out
!
interface GigabitEthernet0/1   ! interface voltada para a LAN (interna)
 ip access-group ACL_INSIDE_OUT in
```

### ACL para permitir acesso público somente aos IPs NATeados (ex.: Web/ERP)

```
ip access-list extended ACL_OUTSIDE_IN
 remark Permitir acesso HTTP/HTTPS aos servidores NATeados
 permit tcp any host 104.109.10.2 eq 80
 permit tcp any host 104.109.10.2 eq 443
 remark Bloquear SIP público
 deny udp any any eq 5060
 deny udp any any eq 5061
 remark Negar todo o resto e logar
 deny ip any any
```

**Aplicar na interface externa (Internet) inbound:**

```
interface GigabitEthernet0/0
 ip access-group ACL_OUTSIDE_IN in
```

---

## 4) Observações sobre NAT e relação com ACLs

* Para serviços publicados (ERP/WWW/DNS público), implemente NAT estático (`ip nat inside source static tcp <server_internal_ip> 80 <public_ip> 80`) e deixe a ACL `ACL_OUTSIDE_IN` permitir somente as portas publicadas.
* Para navegação dos usuários (NAT overload/NAPT), implemente `ip nat inside source list <acl> interface <if_public> overload`. Neste caso, as ACLs que definem o que pode sair (lista de origem) também servem para o NAT.
* Lembre-se de adicionar rotas apropriadas nos roteadores ISP (conforme instruções do enunciado) para que os IPs públicos escolhidos sejam encaminhados ao seu firewall/roteador.
