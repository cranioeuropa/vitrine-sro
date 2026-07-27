# Linha de Continuidade da Jornada do Aluno

## Propósito

Registrar a história operacional real de cada aluno sem inventar fatos, julgar comportamentos ou reduzir a pessoa a números isolados.

A linha oficial é:

```text
entrada
→ intenção declarada
→ prática
→ ritmo
→ interrupção
→ retomada
→ conquista
→ próxima fase
```

## Princípios

1. A máquina registra fatos; não fabrica evolução.
2. O aluno continua sendo protagonista da jornada.
3. Interrupção não é fracasso: é um estado que pode pedir contexto, espera ou retomada.
4. O sistema comunica saúde, progresso, atenção e risco — não apenas problemas.
5. Toda narrativa deve poder apontar para evidências registradas.
6. O próximo movimento deve ser pequeno, compreensível e executável.

## Modelo no Airtable

Base: `Academia Roteiro_Vivo`

### Tabela `Jornadas_Aluno`

Representa o estado atual consolidado da jornada.

Campos principais:

- `Jornada_ID`
- `Pessoa_ID`
- `Objetivo_Declarado`
- `Fase_Atual`
- `Estado_Jornada`
- `Data_Inicio`
- `Ultimo_Movimento`
- `Ritmo_Esperado_Semanal`
- `Ritmo_Atual_Semanal`
- `Resumo_Continuidade`
- `Proximo_Movimento`
- `Precisa_Atencao`

### Tabela `Eventos_Jornada`

Representa os fatos que constroem a história.

Tipos iniciais:

- entrada;
- presença;
- ausência;
- meta declarada;
- marco físico;
- marco comportamental;
- interrupção;
- retomada;
- conquista;
- mudança de fase;
- observação;
- próximo movimento.

## Papel da Sofia

A Sofia não cria a história. Ela transforma eventos confirmados em uma leitura compreensível, por exemplo:

> Há seis meses você começou buscando mais disposição. Nas últimas quatro semanas manteve duas presenças semanais. Nesta semana houve uma interrupção, mas sua jornada continua ativa. O próximo movimento possível é retomar com uma presença curta.

## Primeiras capacidades do MCP

- criar uma jornada;
- registrar um evento;
- consultar a linha do tempo de uma pessoa;
- resumir continuidade;
- sugerir próximo movimento com base em fatos;
- produzir narrativa visível para o aluno;
- separar observação, interpretação e recomendação.
