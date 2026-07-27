from runner import decidir


def test_melhora_comportamental_confirma_estado_saudavel() -> None:
    decisao = decidir("Responde positivamente", 4, "Melhorou")

    assert decisao.estado_final == "Saudável"
    assert decisao.acao_final == "Manter acompanhamento"
    assert decisao.resultado == "Eficaz"
    assert decisao.exige_humano is False
    assert decisao.interrompe_automacao is False


def test_fala_sem_comportamento_nao_prova_recuperacao() -> None:
    decisao = decidir("Responde positivamente", 0, "Manteve")

    assert decisao.estado_final == "Queda"
    assert decisao.acao_final == "Pergunta leve"
    assert decisao.resultado == "Ineficaz"


def test_pedido_de_silencio_interrompe_automacao() -> None:
    decisao = decidir("Pede silêncio", 3, "Melhorou")

    assert decisao.estado_final == "Silenciado"
    assert decisao.acao_final == "Silenciar contato"
    assert decisao.interrompe_automacao is True


def test_dificuldade_concreta_encaminha_para_humano() -> None:
    decisao = decidir("Revela dificuldade", 0, "Piorou")

    assert decisao.estado_final == "Humano"
    assert decisao.acao_final == "Encaminhar humano"
    assert decisao.exige_humano is True
    assert decisao.interrompe_automacao is True


def test_retorno_inicial_ainda_exige_observacao() -> None:
    decisao = decidir("Responde positivamente", 1, "Manteve")

    assert decisao.estado_final == "Atenção leve"
    assert decisao.acao_final == "Aguardar"
