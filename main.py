import os
import csv
import shutil
import requests
import datetime
import dateutil
import traceback
import plotly.graph_objects as go


def obterUFEstadoPorNome(estado):
    """
    Retorna o codigo UF do estado a partir do nome do estado
    :param estado: Nome do estado
    :return codigoDoEstado: Código UF do estado
    """
    try:
        with open("./recursos/estados.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for state in reader:
                if state["Unidade_Federativa"].lower() == estado.strip().lower():
                    return state["UF"]
    except Exception as exc:
        print("[ERROR]{0}".format(exc))


def obterNomeEstadoPorUF(uf):
    """
    Retorna o nome do estado a partir da sigla do estado
    :param uf: Código UF do estado
    :return nomeDoEstado: Nome do estado
    """
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if state["UF"].lower() == uf.lower():
                return state["Unidade_Federativa"]


def obterPrimeiroNomeEstadoPorEntrada(entrada):
    """
    Retorna o nome do estado a partir da sigla do estado
    :param uf: Código UF do estado
    :return nomeDoEstado: Nome do estado
    """
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if entrada.lower() in state["Unidade_Federativa"].lower():
                return state["Unidade_Federativa"]


def exibirGraficoCasosAcumulados(dados):
    """
    Exibe gráfico dos casos acumulados com casos confirmados e óbitos
    :param dados: Variável com dados estatísticos dos casos acumulados
    """
    data = []

    obitos = []
    novosObitos = []
    numeroObitosAnterior = None

    confirmados = []
    novosCasos = []
    numeroDeCasosAnterior = None
    for dado in dados:
        data.append(dado["Data"])
        if numeroDeCasosAnterior == None:
            numeroDeCasosAnterior = dado["Confirmados"]
            novosCasos.append(0)
        else:
            novosCasos.append(int(dado["Confirmados"]) - int(numeroDeCasosAnterior))
            numeroDeCasosAnterior = dado["Confirmados"]

        if numeroObitosAnterior == None:
            numeroObitosAnterior = dado["Obitos"]
            novosObitos.append(0)
        else:
            novosObitos.append(int(dado["Obitos"]) - int(numeroObitosAnterior))
            numeroObitosAnterior = dado["Obitos"]
        confirmados.append(dado["Confirmados"])
        obitos.append(dado["Obitos"])
    fig = go.Figure()
    fig.add_trace(go.Bar(y=novosObitos, x=data, name="Novos Óbitos"))
    fig.add_trace(go.Scatter(mode='lines+markers', y=obitos, x=data, name="Óbitos"))
    fig.add_trace(go.Bar(y=novosCasos, x=data, name="Novos Confirmados"))
    fig.add_trace(go.Scatter(mode='lines+markers', y=confirmados, x=data, name="Casos Confirmados"))

    fig.update_layout(
        title='Estatística de casos do COVID-19 no Brasil',
        xaxis_title='Data',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def exibirGraficoCasosAcumuladosPorUltimosRegistros(dados, ultimosRegistros):
    """
    Exibe gráfico dos casos acumulados com casos confirmados e óbitos
    :param dados: Variável com dados estatísticos dos casos acumulados
    :param ultimosRegistros: Variável com o número de quantos registros devem ser exibidos
    """
    dados = dados[-ultimosRegistros:]
    data = []

    obitos = []
    novosObitos = []
    numeroObitosAnterior = None

    confirmados = []
    novosCasos = []
    numeroDeCasosAnterior = None
    for dado in dados:
        data.append(dado["Data"])
        if numeroDeCasosAnterior == None:
            numeroDeCasosAnterior = dado["Confirmados"]
            novosCasos.append(0)
        else:
            novosCasos.append(int(dado["Confirmados"]) - int(numeroDeCasosAnterior))
            numeroDeCasosAnterior = dado["Confirmados"]

        if numeroObitosAnterior == None:
            numeroObitosAnterior = dado["Obitos"]
            novosObitos.append(0)
        else:
            novosObitos.append(int(dado["Obitos"]) - int(numeroObitosAnterior))
            numeroObitosAnterior = dado["Obitos"]
        confirmados.append(dado["Confirmados"])
        obitos.append(dado["Obitos"])
    fig = go.Figure()
    fig.add_trace(go.Bar(y=novosObitos, x=data, name="Novos Óbitos"))
    fig.add_trace(go.Scatter(mode='lines+markers', y=obitos, x=data, name="Óbitos"))
    fig.add_trace(go.Bar(y=novosCasos, x=data, name="Novos Confirmados"))
    fig.add_trace(go.Scatter(mode='lines+markers', y=confirmados, x=data, name="Casos Confirmados"))

    fig.update_layout(
        title='Estatística de casos do COVID-19 no Brasil',
        xaxis_title='Data',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def exibirGraficoCasosEstados(estados):
    """
    Exibe gráfico dos casos acumulados com casos dos estados
    :param estados: Variável com dados estatísticos dos estados
    """
    nomeEstados = []
    casosEstados = []
    for estado in sorted(estados, key=lambda est: int(est["Casos"])):
        nomeEstados.append(estado["Nome"])
        casosEstados.append(estado["Casos"])

    fig = go.Figure()
    fig.add_trace(go.Bar(y=casosEstados, x=nomeEstados))

    fig.update_layout(
        title='Estatística de casos do COVID-19 no Brasil entre estados',
        xaxis_title='Estados',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def exibirGraficoDetalhadoCasosEstado(casosEstados, ufEstado, nomeEstado):
    """
    Exibe gráfico dos casos detalhados de cada estado
    :param estados: Variável com dados estatísticos dos estados
    """

    fig = go.Figure()
    for key in casosEstados:
        if key == ufEstado:
            fig.add_trace(go.Bar(y=casosEstados[key][1], x=casosEstados[key][0], name='Casos Novos'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][2], x=casosEstados[key][0], name='Casos Acumulados'))
            fig.add_trace(go.Bar(y=casosEstados[key][3], x=casosEstados[key][0], name='Obitos Novos'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][4], x=casosEstados[key][0], name='Obitos Acumulados'))

    fig.update_layout(
        title='Estatística detalhados dos casos do COVID-19 no Brasil no estado ' + nomeEstado + '('+ufEstado+')',
        xaxis_title='Data',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def exibirGraficoDetalhadoCasosEntreEstados(casosEstados, ufEstado1, nomeEstado1, ufEstado2, nomeEstado2):
    """
    Exibe gráfico dos casos detalhados de cada estado
    :param estados: Variável com dados estatísticos dos estados
    """

    fig = go.Figure()
    for key in casosEstados:
        if key == ufEstado1:
            fig.add_trace(go.Bar(y=casosEstados[key][1], x=casosEstados[key][0], name='Casos Novos('+nomeEstado1+')'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][2], x=casosEstados[key][0], name='Casos Acumulados('+nomeEstado1+')'))
            fig.add_trace(go.Bar(y=casosEstados[key][3], x=casosEstados[key][0], name='Obitos Novos('+nomeEstado1+')'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][4], x=casosEstados[key][0], name='Obitos Acumulados('+nomeEstado1+')'))

        elif key == ufEstado2:
            fig.add_trace(go.Bar(y=casosEstados[key][1], x=casosEstados[key][0], name='Casos Novos('+nomeEstado2+')'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][2], x=casosEstados[key][0], name='Casos Acumulados('+nomeEstado2+')'))
            fig.add_trace(go.Bar(y=casosEstados[key][3], x=casosEstados[key][0], name='Obitos Novos('+nomeEstado2+')'))
            fig.add_trace(go.Scatter(mode='lines+markers', y=casosEstados[key][4], x=casosEstados[key][0], name='Obitos Acumulados('+nomeEstado2+')'))

    fig.update_layout(
        title='Estatística detalhados dos casos do COVID-19 no Brasil nos estados ' + nomeEstado1 + '('+ufEstado1+') e ' + nomeEstado2 + '('+ufEstado2+')' ,
        xaxis_title='Data',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def main():
    url = "https://covid.saude.gov.br/"
    pastaAtual = os.getcwd()
    try:
        application_id_request = 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm'

        # Captura dados gerais da página
        print("[LOG]Capturando dados gerais.")
        dados_gerais = requests.get('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalSintese',
                                    headers={"X-Parse-Application-Id": application_id_request}).json()
        casos = dict()
        casos["Confirmados"] = int(dados_gerais[0]['casosAcumuladoN'])
        casos["Obitos"] = int(dados_gerais[0]['obitosAcumuladoN'])
        casos["Letalidade(%)"] = float((casos["Obitos"] * 100) / casos["Confirmados"])
        # Pega hora em UTC e converte
        utc_zone = dateutil.tz.tzutc()
        local_zone = dateutil.tz.tzlocal()
        utc = datetime.datetime.strptime(dados_gerais[0]['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
        utc = utc.replace(tzinfo=utc_zone)
        # Converte para zona local
        hora_local_obj = utc.astimezone(local_zone)
        hora = hora_local_obj.hour
        minuto = hora_local_obj.minute
        dia = hora_local_obj.day
        mes = hora_local_obj.month
        ano = hora_local_obj.year
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("[LOG]Dados gerais extraídos.")
        print("Dados atualizados " + date.strftime("%d/%m/%Y %H:%M") + ". Fonte: " + url)
        if input("Deseja ver as estatísticas gerais do Brasil?(sim/nao) ") != "nao":
            for key in casos.keys():
                print('{:s}: {:.2f}'.format(key, casos[key]))

        regioes = []
        print("[LOG]Dados das regiões sendo extraídos.")
        dados_regioes = dados_gerais
        modeloRegiao = "Nome: {}, Casos confirmados: {}({:.2f}%)"
        for i in range(1, 6):
            dado = dict()
            dado['Nome'] = dados_regioes[i]['_id']
            dado['Casos'] = int(dados_regioes[i]['casosAcumulado'])
            dado['PorcentagemDeCasosRelacional'] = (dado['Casos'] / casos["Confirmados"]) * 100
            regioes.append(dado)
        print("[LOG]Dados das regiões extraídos.")
        if input("Deseja ver as estatísticas por região?(sim/nao) ") != "nao":
            for regiao in regioes:
                print(modeloRegiao.format(regiao['Nome'],
                                          regiao['Casos'],
                                          regiao['PorcentagemDeCasosRelacional']))

        estados = []
        # Captura dados dos estados
        print("[LOG]Dados dos estados sendo extraídos.")
        # dados_estados = dados_regioes
        for regiao in dados_regioes[1:6]:
            for estado in regiao['listaMunicipios']:
                dado = dict()
                dado['Nome'] = obterNomeEstadoPorUF(estado['_id'])
                dado['Casos'] = int(estado['casosAcumulado'])
                dado['PorcentagemDeCasosRelacional'] = float((dado['Casos'] / casos["Confirmados"]) * 100.0)
                dado['Obitos'] = int(estado['obitosAcumulado'])
                dado['Letalidade'] = float((dado['Obitos'] * 100) / dado['Casos'])
                estados.append(dado)
        print("[LOG]Dados dos estados extraídos.")
        entrada = input("Deseja ver as estatísticas por estados?(sim/nao/todos) ")
        while entrada != "nao":
            modeloEstado = "Nome: {}, Casos confirmados: {}(~{:.5f}%)"

            if entrada == "todos":
                for estado in estados:
                    print(modeloEstado.format(estado['Nome'], estado['Casos'], estado['PorcentagemDeCasosRelacional']))
                break

            if entrada != "nao":
                estadoNome = input("Qual o nome do estado? ")
                for estado in estados:
                    if estadoNome.lower() in str(estado['Nome']).lower():
                        print(modeloEstado.format(estado['Nome'], estado['Casos'], estado['PorcentagemDeCasosRelacional']))
                entrada = input("Deseja continuar(sim/nao)? ")

        entrada = input("Deseja passar todas a informações disponíveis para um arquivo no formato .csv?(sim/nao) ")
        if entrada != "nao":
            with open("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "w", newline="",
                      encoding="utf-8") as file:
                field_names = ["Nome", "Casos", "PorcentagemDeCasosRelacional", "Obitos", "Letalidade", "Atualizado"]
                writer = csv.DictWriter(file,
                                        fieldnames=field_names,
                                        delimiter=";",
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for regiao in regioes:
                    writer.writerow({"Nome": regiao["Nome"],
                                     "Casos": regiao["Casos"],
                                     "PorcentagemDeCasosRelacional": regiao["PorcentagemDeCasosRelacional"],
                                     "Obitos": "",
                                     "Letalidade": "",
                                     "Atualizado": ""
                                     })
                for estado in estados:
                    nome = estado["Nome"] + "(" + obterUFEstadoPorNome(estado["Nome"]) + ")"
                    writer.writerow({"Nome": nome,
                                     "Casos": estado["Casos"],
                                     "PorcentagemDeCasosRelacional": "{:.5f}".format(
                                         estado["PorcentagemDeCasosRelacional"]),
                                     "Obitos": estado["Obitos"],
                                     "Letalidade": estado["Letalidade"],
                                     "Atualizado": ""
                                     })
                # writer.writerows(estados)
                writer.writerow({"Nome": "Total",
                                 "Casos": str(casos["Confirmados"]).replace(".", ""),
                                 "PorcentagemDeCasosRelacional": "100",
                                 "Obitos": casos["Obitos"],
                                 "Letalidade": casos["Letalidade(%)"],
                                 "Atualizado": date.strftime("%d-%m-%Y--%H-%M")
                                 })

            shutil.copyfile("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "dados/maisRecente.csv")

            print(
                date.strftime("%d-%m-%Y--%H-%M") + ".csv criado na pasta dados, que se encontra na pasta desse script.")
            print("maisRecente.csv foi atualizado.")

        dados_acumulados = []

        req = requests.get("https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalCasos")
        req_json = req.json()
        for dado in req_json['dias']:
            dados_acumulados.append({"Data": dado["_id"],
                                    "Confirmados": dado["casosAcumulado"],
                                    "Obitos": dado["obitosAcumulado"]
                                    })

        entrada = input("Deseja passar o histórico de casos para um arquivo no formato .csv?(sim/nao) ")
        if entrada != "nao":
            with open("dados/casosAcumulados.csv", "w", newline="", encoding="utf-8") as file:
                field_names = ["Data", "Confirmados", "Novos Confirmados", "Obitos", "Novos Obitos"]
                writer = csv.DictWriter(file,
                                        fieldnames=field_names,
                                        delimiter=";",
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC
                                        )
                writer.writeheader()
                numero_obitos_anterior = None
                numero_de_casos_anterior = None
                for dado in dados_acumulados:
                    if numero_de_casos_anterior == None and numero_obitos_anterior == None:
                        numero_de_casos_anterior = dado["Confirmados"]
                        numero_obitos_anterior = dado["Obitos"]
                        writer.writerow({"Data": dado["Data"],
                                         "Confirmados": dado["Confirmados"],
                                         "Novos Confirmados": "0",
                                         "Obitos": dado["Obitos"],
                                         "Novos Obitos": "0"
                                         })
                    else:
                        writer.writerow({"Data": dado["Data"],
                                         "Confirmados": dado["Confirmados"],
                                         "Novos Confirmados": int(dado["Confirmados"]) - int(numero_de_casos_anterior),
                                         "Obitos": dado["Obitos"],
                                         "Novos Obitos": int(dado["Obitos"]) - int(numero_obitos_anterior)
                                         })
                        numero_de_casos_anterior = dado["Confirmados"]
                        numero_obitos_anterior = dado["Obitos"]

        entrada = input("Deseja exibir o gráfico do histórico de casos?(sim/ultimos/nao) ")
        if entrada != "nao":
            if entrada != "ultimos":
                # entrada = "sim"
                print("[LOG]Abrindo gráfico no navegador padrão.")
                exibirGraficoCasosAcumulados(dados_acumulados)
            else:
                registrosDisponiveis = len(dados_acumulados)
                ultimosRegistros = int(
                    input("Quantos registros devem ser exibidos?({} disponíveis) ".format(registrosDisponiveis)))
                if ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis:
                    print("[LOG]Abrindo gráfico no navegador padrão.")
                    exibirGraficoCasosAcumuladosPorUltimosRegistros(dados_acumulados, ultimosRegistros)
                while not (ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis):
                    ultimosRegistros = int(
                        input("Quantos registros devem ser exibidos?({} disponíveis)".format(registrosDisponiveis)))
                    if ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis:
                        print("[LOG]Abrindo gráfico no navegador padrão.")
                        exibirGraficoCasosAcumuladosPorUltimosRegistros(dados_acumulados, ultimosRegistros)
                        break

        entrada = input("Deseja exibir o gráfico de casos de estados?(sim/nao) ")
        if entrada != "nao":
            print("[LOG]Abrindo gráfico no navegador padrão.")
            exibirGraficoCasosEstados(estados)

        entrada = input("Deseja ver as estatísticas de casos detalhados por estado?(sim/nao) ")
        casos_estaduais = dict()
        print("[LOG]Obtendo casos detalhados dos estados")

        # DICIONARIO DE ESTADOS
        # CADA ESTADO TEM UMA LISTA
        # CADA LISTA POSSUI OUTRAS 5 LISTAS:
        # data
        # casosNovos
        # casosAcumulados
        # obitosNovos
        # obitosAcumulado

        casos_detalhados_estados = requests.get(
            'https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalRegiaoUf').json()

        for regiao in regioes:
            nome_regiao = regiao['Nome']
            for estado in casos_detalhados_estados[nome_regiao]:
                dia_anterior = dict()
                for dia in casos_detalhados_estados[nome_regiao][estado]['dias']:
                    if estado not in casos_estaduais:
                        casos_estaduais[estado] = []
                        casos_estaduais[estado].append([dia['_id']])
                        casos_estaduais[estado].append([dia['casosAcumulado']])  # casos novos
                        casos_estaduais[estado].append([dia['casosAcumulado']])  # casos acumulados
                        casos_estaduais[estado].append([dia['obitosAcumulado']])  # obitos novos
                        casos_estaduais[estado].append([dia['obitosAcumulado']])  # obitos acumulados
                        casos_estaduais[estado].append(regiao)  # obitos acumulados
                        dia_anterior['casos'] = dia['casosAcumulado']
                        dia_anterior['obitos'] = dia['obitosAcumulado']
                    else:
                        casos_estaduais[estado][0].append(dia['_id'])
                        casos_estaduais[estado][1].append(dia['casosAcumulado'] - dia_anterior['casos'])  # casos novos
                        casos_estaduais[estado][2].append(dia['casosAcumulado'])  # casos acumulados
                        casos_estaduais[estado][3].append(
                            dia['obitosAcumulado'] - dia_anterior['obitos'])  # obitos novos
                        casos_estaduais[estado][4].append(dia['obitosAcumulado'])  # obitos acumulados
                        dia_anterior['casos'] = dia['casosAcumulado']
                        dia_anterior['obitos'] = dia['obitosAcumulado']

        while entrada != "nao":
                entrada2 = input("Deseja ver um estado individualmente ou comparar com outro?(individual/comparar) ")
                if entrada2 == "comparar":
                    estado1 = input("Nome do primeiro estado a ser comparado: ")
                    estado2 = input("Nome do segundo estado a ser comparado: ")
                    nomeEstado1 = obterPrimeiroNomeEstadoPorEntrada(estado1)
                    ufEstado1 = obterUFEstadoPorNome(nomeEstado1)
                    nomeEstado2 = obterPrimeiroNomeEstadoPorEntrada(estado2)
                    ufEstado2 = obterUFEstadoPorNome(nomeEstado2)
                    exibirGraficoDetalhadoCasosEntreEstados(casos_estaduais, ufEstado1, nomeEstado1, ufEstado2, nomeEstado2)
                    entrada = input("Deseja continuar(sim/nao)? ")

                else:
                    estado = input("Nome do estado: ")
                    nomeEstado = obterPrimeiroNomeEstadoPorEntrada(estado)
                    ufEstado = obterUFEstadoPorNome(nomeEstado)
                    exibirGraficoDetalhadoCasosEstado(casos_estaduais, ufEstado, nomeEstado)
                    entrada = input("Deseja continuar(sim/nao)? ")




    # except Exception as exc:
    #     print("[ERROR]{0}".format(exc))

    finally:
        print("[LOG]Encerrando script.")
        print("[LOG]Script encerrado.")
        print("Todos os dados foram extraídos de: " + url + ".")


if __name__ == '__main__':
    main()
