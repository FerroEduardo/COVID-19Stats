import os
import re
import csv
import time
import shutil
import datetime
import requests
import traceback
import plotly.graph_objects as go

from selenium import common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', str(os.path.join(pastaAtual, "dados")))
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    profile.update_preferences()
    firefox_options = Options()
    firefox_options.headless = True
    driver = webdriver.Firefox(firefox_profile=profile, options=firefox_options)
    driverversion = driver.capabilities['moz:geckodriverVersion']
    browserversion = driver.capabilities['browserVersion']
    print("[LOG]geckodriverVersion: " + driverversion, "\n[LOG]browserVersion: " + browserversion)
    print("[LOG]Carregando página...")
    driver.get(url=url)
    print("[LOG]Página carregada.")
    try:
        print("[LOG]Aguardando elementos da página serem carregados...")
        WebDriverWait(driver, 120).until(
            # Verifica se página/data foi carregada
            EC.text_to_be_present_in_element(
                (By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[1]/div[3]/span'),
                "2020")
        )
        print("[LOG]Elementos carregados.")
        print("[LOG]Webdriver temporário sendo executado.")
        miningDriver = webdriver.Firefox(firefox_profile=profile, options=firefox_options)
        applicationIDRequest = None
        authorizationRequestInsumos = None
        print("[LOG]Procurando header ID para request.")
        try:
            # A partir daqui, o algoritmo procura todas as tag <script> do html da pagina e
            # procura pela string "X-Parse-Application-Id" e pela string "Authorization"
            # Depois de encontrar, é utilizado REGEX para encontar alguns padrões e, a partir
            # deles, procuro pelas strings "X-Parse-Application-Id" e "Authorization" e um parse simples.
            # Essa string que é encontrada é utilizada como request header em um GET request em uma parte do código
            header = driver.find_element_by_tag_name("head")
            scriptsFromHead = header.find_elements_by_tag_name("script")
            for script in scriptsFromHead:
                if script.get_attribute("src") and "https://covid.saude.gov.br" in script.get_attribute("src"):
                    scriptUrl = script.get_attribute("src")
                    miningDriver.get(scriptUrl)
                    p = re.compile('\(\"(.*?)\"\)')
                    if "X-Parse-Application-Id" in miningDriver.page_source and "Authorization" in miningDriver.page_source:
                        html = miningDriver.page_source
                        for match in p.findall(html):
                            if "X-Parse-Application-Id" in match:
                                applicationIDRequest = str(match.split('","')[1]).strip()
                                # print(headerRequestID)
                                print("[LOG]Header ID para request encontrado.")
                            elif "Authorization" in match:
                                authorizationRequestInsumos = str(match.split('","')[1]).strip()
                                # print(headerRequestInsumos)
                                print("[LOG]Header Authorization para request encontrado.")
                                break
                        break

        finally:
            miningDriver.close()
            print("[LOG]Webdriver temporário encerrado.")

        # Captura dados gerais da página
        print("[LOG]Capturando dados gerais.")
        casos = dict()
        casos["Confirmados"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/card-totalizadores-component/div[1]/div[1]/div/div[1]').text
        casos["Obitos"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/card-totalizadores-component/div[1]/div[2]/div/div[1]').text
        casos["Letalidade(%)"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/card-totalizadores-component/div[1]/div[3]/div/div[1]').text[:-1].replace(",", ".")

        dateStr = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[1]/div[3]/span').text
        dateStr = dateStr.split(" ")
        hora = int(dateStr[0].split(":")[0])
        minuto = int((dateStr[0].split(":")[1]))
        dia = int(dateStr[1].split("/")[0])
        mes = int(dateStr[1].split("/")[1])
        ano = int(dateStr[1].split("/")[2])
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("[LOG]Dados gerais extraídos.")
        print("Dados atualizados " + date.strftime("%d/%m/%Y %H:%M") + ". Fonte: " + url)
        if input("Deseja ver as estatísticas gerais do Brasil?(sim/nao) ") != "nao":
            for key in casos.keys():
                print(key + ": " + casos[key])

        regioes = []
        # Captura dados das regiões da página
        # Por algum motivo, o Selenium só reconheceu os textos quando eles estavam na tela
        print("[LOG]Dados das regiões sendo extraídos.")
        scrollRegioes = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/p')
        driver.execute_script("arguments[0].scrollIntoView()", scrollRegioes)
        # Aguarda regiões carregarem
        WebDriverWait(driver, 120).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/legendas-component/div/div[5]/div[1]/div[2]'),
                "Sul")
        )
        modeloRegiao = "Nome: {}, Casos confirmados: {}({}%)"
        for i in range(1, 6):
            scrollRegioes = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/legendas-component/div/div[' + str(i) + ']')
            driver.execute_script("arguments[0].scrollIntoView()", scrollRegioes)
            dado = dict()
            dado['Nome'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/legendas-component/div/div[' + str(i) + ']/div[1]/div[2]').text
            dado['Casos'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/legendas-component/div/div[' + str(i) + ']/div[2]/div[1]').text
            dado['PorcentagemDeCasosRelacional'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[1]/div[2]/div[1]/chart-pie-component/legendas-component/div/div[' + str(i) + ']/div[2]/div[2]').text[:-1].replace(',','.')

            regioes.append(dado)
        print("[LOG]Dados das regiões extraídos.")
        if input("Deseja ver as estatísticas por região?(sim/nao) ") != "nao":
            for regiao in regioes:
                print(modeloRegiao.format(regiao['Nome'],
                                          regiao['Casos'],
                                          regiao['PorcentagemDeCasosRelacional']))

        estados = []
        # Captura dados dos estados da página
        print("[LOG]Dados dos estados sendo extraídos.")
        scrollEstados = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/p/span')
        driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
        for i in range(1, 28):
            scrollEstados = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/div[2]/div[' + str(i) + ']')
            driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
            dado = dict()
            dado['Nome'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/div[2]/div[' + str(i) + ']/div[1]').text
            dado['Casos'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/div[2]/div[' + str(i) + ']/div[3]/div[1]/b').text
            dado['PorcentagemDeCasosRelacional'] = float((int(dado['Casos']) / int(casos["Confirmados"].replace(".", ""))) * 100.0)
            dado['Obitos'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/div[2]/div[' + str(i) + ']/div[3]/div[2]/b').text
            dado['Letalidade'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/painel-geral-component/div/div[2]/div[2]/div[1]/lista-itens-component/div[2]/div[' + str(i) + ']/div[3]/div[4]/b').text
            if "%" in dado['Letalidade']:
                dado['Letalidade'] = dado['Letalidade'][:-1].replace(",", ".")
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
            with open("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "w", newline="", encoding="utf-8") as file:
                fieldNames = ["Nome", "Casos", "PorcentagemDeCasosRelacional", "Obitos", "Letalidade", "Atualizado"]
                writer = csv.DictWriter(file,
                                        fieldnames=fieldNames,
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
                                     "PorcentagemDeCasosRelacional": "{:.5f}".format(estado["PorcentagemDeCasosRelacional"]),
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

        dadosAcumulados = []

        req = requests.get("https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalAcumulo",
                           headers={"X-Parse-Application-Id": applicationIDRequest})
        reqJson = req.json()
        for dado in reqJson['results']:
            dadosAcumulados.append({"Data": dado["label"],
                                    "Confirmados": dado["qtd_confirmado"],
                                    "Obitos": dado["qtd_obito"]
                                    })

        entrada = input("Deseja passar o histórico de casos para um arquivo no formato .csv?(sim/nao) ")
        if entrada != "nao":
            with open("dados/casosAcumulados.csv", "w", newline="", encoding="utf-8") as file:
                fieldNames = ["Data", "Confirmados", "Novos Confirmados", "Obitos", "Novos Obitos"]
                writer = csv.DictWriter(file,
                                        fieldnames=fieldNames,
                                        delimiter=";",
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC
                                        )
                writer.writeheader()
                numeroObitosAnterior = None
                numeroDeCasosAnterior = None
                for dado in dadosAcumulados:
                    if numeroDeCasosAnterior == None and numeroObitosAnterior == None:
                        numeroDeCasosAnterior = dado["Confirmados"]
                        numeroObitosAnterior = dado["Obitos"]
                        writer.writerow({"Data": dado["Data"],
                                         "Confirmados": dado["Confirmados"],
                                         "Novos Confirmados": "0",
                                         "Obitos": dado["Obitos"],
                                         "Novos Obitos": "0"
                                         })
                    else:
                        writer.writerow({"Data": dado["Data"],
                                         "Confirmados": dado["Confirmados"],
                                         "Novos Confirmados": int(dado["Confirmados"]) - int(numeroDeCasosAnterior),
                                         "Obitos": dado["Obitos"],
                                         "Novos Obitos": int(dado["Obitos"]) - int(numeroObitosAnterior)
                                         })
                        numeroDeCasosAnterior = dado["Confirmados"]
                        numeroObitosAnterior = dado["Obitos"]

        entrada = input("Deseja exibir o gráfico do histórico de casos?(sim/ultimos/nao) ")
        if entrada != "nao":
            if entrada != "ultimos":
                # entrada = "sim"
                print("[LOG]Abrindo gráfico no navegador padrão.")
                exibirGraficoCasosAcumulados(dadosAcumulados)
            else:
                registrosDisponiveis = len(dadosAcumulados)
                ultimosRegistros = int(
                    input("Quantos registros devem ser exibidos?({} disponíveis) ".format(registrosDisponiveis)))
                if ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis:
                    print("[LOG]Abrindo gráfico no navegador padrão.")
                    exibirGraficoCasosAcumuladosPorUltimosRegistros(dadosAcumulados, ultimosRegistros)
                while not (ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis):
                    ultimosRegistros = int(
                        input("Quantos registros devem ser exibidos?({} disponíveis)".format(registrosDisponiveis)))
                    if ultimosRegistros > 0 and ultimosRegistros <= registrosDisponiveis:
                        print("[LOG]Abrindo gráfico no navegador padrão.")
                        exibirGraficoCasosAcumuladosPorUltimosRegistros(dadosAcumulados, ultimosRegistros)
                        break

        entrada = input("Deseja exibir o gráfico de casos de estados?(sim/nao) ")
        if entrada != "nao":
            print("[LOG]Abrindo gráfico no navegador padrão.")
            exibirGraficoCasosEstados(estados)

        brasilcsv = None
        entrada = input("Deseja ver as estatísticas de casos por estado?(sim/nao) ")
        casosEstaduais = dict()
        if entrada != "nao":
            # Correção necessária, formato do nome foi alterado no site e alguns dados(nome,url) sobre o arquivo podem ser encontrados nesse JSON
            req = requests.get("https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalGeral",
                               headers={"X-Parse-Application-Id": applicationIDRequest})
            reqJson = req.json()
            fileName = reqJson['results'][0]['arquivo']['name']
            # brasilCsvUrl = reqJson['results'][0]['arquivo']['url']
            # brasilcsv = str(os.path.join(pastaAtual, "dados/"+fileName))
            brasilcsv = str(os.path.join(pastaAtual, "dados/arquivo_geral.csv"))
            # brasilcsv = None
            print("[LOG]Baixando arquivo dos casos detalhados dos estados")
            # arquivo nao existe e baixa o mesmo
            # se arquivo ja existe, apaga e cria outro
            if os.path.exists(brasilcsv):
                os.remove(brasilcsv)
            driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[2]/ion-button').click()
            time.sleep(1)
            driver.get('about:downloads')
            filename = driver.execute_script("return document.querySelector('description').getAttribute('value')")
            brasilcsv = str(os.path.join(pastaAtual, "dados/" + filename))
            try:
                getDownloadPercentage = driver.execute_script("return document.querySelector('progress').getAttribute('value')")
                while getDownloadPercentage != "100":
                    time.sleep(1)
                    getDownloadPercentage = driver.execute_script("return document.querySelector('progress').getAttribute('value')")

            except common.exceptions.JavascriptException:
                time.sleep(2)
                while not os.path.exists(brasilcsv):
                    time.sleep(1)
            # DICIONARIO DE ESTADOS
            # CADA ESTADO TEM UMA LISTA
            # CADA LISTA POSSUI OUTRAS 5 LISTAS:
            # data
            # casosNovos
            # casosAcumulados
            # obitosNovos
            # obitosAcumulado

            with open(brasilcsv, newline='', encoding='latin-1') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                try:
                    for row in reader:
                        keySiglaOuEstado = None
                        if 'estado' in row.keys():
                            keySiglaOuEstado = 'estado'
                        else:
                            keySiglaOuEstado = 'sigla'
                        if row[keySiglaOuEstado] not in casosEstaduais:
                            casosEstaduais[row[keySiglaOuEstado]] = []
                            casosEstaduais[row[keySiglaOuEstado]].append([row['data']])
                            casosEstaduais[row[keySiglaOuEstado]].append([row['casosNovos']])
                            casosEstaduais[row[keySiglaOuEstado]].append([row['casosAcumulados']])
                            casosEstaduais[row[keySiglaOuEstado]].append([row['obitosNovos']])
                            casosEstaduais[row[keySiglaOuEstado]].append([row['obitosAcumulados']])
                            if row['regiao']:
                                casosEstaduais[row[keySiglaOuEstado]].append(row['regiao'])
                            elif row['região']:
                                casosEstaduais[row[keySiglaOuEstado]].append(row['regiao'])

                        else:
                            casosEstaduais[row[keySiglaOuEstado]][0].append(row['data'])
                            casosEstaduais[row[keySiglaOuEstado]][1].append(row['casosNovos'])
                            casosEstaduais[row[keySiglaOuEstado]][2].append(row['casosAcumulados'])
                            casosEstaduais[row[keySiglaOuEstado]][3].append(row['obitosNovos'])
                            casosEstaduais[row[keySiglaOuEstado]][4].append(row['obitosAcumulados'])
                except KeyError:
                    print("[ERROR]Provavelmente a tabela no qual o download foi feito possui um erro no header, resultando nesse erro.\n"
                          "Ou o header da tabela foi alterado, necessitando de alteração no algoritmo.")
                    traceback.print_exc()
                    exit(-1)

            while entrada != "nao":
                entrada2 = input("Deseja ver um estado individualmente ou comparar com outro?(individual/comparar) ")
                if entrada2 == "comparar":
                    estado1 = input("Nome do primeiro estado a ser comparado: ")
                    estado2 = input("Nome do segundo estado a ser comparado: ")
                    nomeEstado1 = obterPrimeiroNomeEstadoPorEntrada(estado1)
                    ufEstado1 = obterUFEstadoPorNome(nomeEstado1)
                    nomeEstado2 = obterPrimeiroNomeEstadoPorEntrada(estado2)
                    ufEstado2 = obterUFEstadoPorNome(nomeEstado2)
                    exibirGraficoDetalhadoCasosEntreEstados(casosEstaduais, ufEstado1, nomeEstado1, ufEstado2, nomeEstado2)
                    entrada = input("Deseja continuar(sim/nao)? ")

                else:
                    estado = input("Nome do estado: ")
                    nomeEstado = obterPrimeiroNomeEstadoPorEntrada(estado)
                    ufEstado = obterUFEstadoPorNome(nomeEstado)
                    exibirGraficoDetalhadoCasosEstado(casosEstaduais, ufEstado, nomeEstado)
                    entrada = input("Deseja continuar(sim/nao)? ")


        if input("Deseja ver dados sobre os insumos distribuidos e passar todas a informações para um arquivo no formato .csv?(sim/nao) ") != 'nao':
            headerRequestInsumos = {"Authorization": authorizationRequestInsumos, "Content-Type": "application/json"}
            bodyRequestInsumos = '{"size":30,"sort":["no_uf"],"aggs":{"doses_distribuidas":{"sum":{"field":"doses_distribuidas"}},"luava_proc_n_cirurgico":{"sum":{"field":"luava_proc_n_cirurgico"}},"avental":{"sum":{"field":"avental"}},"leitos_alocados":{"sum":{"field":"leitos_alocados"}},"teste_rapido":{"sum":{"field":"teste_rapido"}},"alcool_etilico100":{"sum":{"field":"alcool_etilico_100ml"}},"alcool_etilico500":{"sum":{"field":"alcool_etilico_500ml"}},"touca_hosp":{"sum":{"field":"touca_hosp"}},"sapatilha":{"sum":{"field":"sapatilha"}},"mascara_3_camadas":{"sum":{"field":"mascara_3_camadas"}},"oculos_protecao":{"sum":{"field":"oculos_protecao"}},"uti_adulto":{"sum":{"field":"uti_adulto"}},"pop_2019":{"sum":{"field":"pop_2019"}},"doses_aplicadas":{"sum":{"field":"doses_aplicadas"}}}}'
            print('[LOG]Extraindo dados dos insumos.')
            req = requests.post('https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalInsumo', data=bodyRequestInsumos, headers=headerRequestInsumos)
            print('[LOG]Dados dos insumos extraídos.')
            insumos = dict()
            insumosPorEstado = dict()
            for insumo in req.json()['aggregations'].keys():
                insumos[insumo] = req.json()['aggregations'][insumo]['value']

            removerDoDict = ['@version', '@timestamp']
            for estado in req.json()['hits']['hits']:
                for tag in removerDoDict:
                    estado['_source'].pop(tag)
                insumosPorEstado[estado['_id']] = estado['_source']
            while True:
                entrada = input("Deseja ver dados dos insumos de todos os estados ou individualmente?(todos/invididualmente) ")
                if entrada == "todos":
                    for estado in insumosPorEstado:
                        print("Estado:", estado)
                        for insumo, quantidade in insumosPorEstado[estado].items():
                            print(insumo + ": " + str(quantidade), end=", ")
                        print()

                else:
                    estado = input("Qual o nome do estado? ")
                    nomeEstado = obterPrimeiroNomeEstadoPorEntrada(estado)
                    ufEstado = obterUFEstadoPorNome(nomeEstado)
                    print(nomeEstado)
                    for insumo, quantidade in insumosPorEstado[ufEstado].items():
                        print(insumo + ": " + str(quantidade), end=", ")
                    print()

                if input("Deseja continuar(sim/nao)? ") == "nao":
                    break
            print('[LOG]Salvando arquivo insumos.csv na pasta dados.')
            # Isso foi feito para colocar o codigo, sigla e nome do estado no inicio do .csv
            fieldNamesInsumosEstados = ["co_uf", "sg_uf", "no_uf", "doses_distribuidas", "luava_proc_n_cirurgico", "avental", "leitos_alocados", "teste_rapido", "alcool_etilico_100ml", "alcool_etilico_500ml", "touca_hosp", "sapatilha", "mascara_3_camadas", "oculos_protecao", "uti_adulto", "pop_2019", "doses_aplicadas", "atualizacao_insumos", "atualizacao_materiais"]
            with open('dados/insumos.csv', "w", newline="", encoding="utf-8") as csvfileInsumosEstado:
                writer = csv.DictWriter(csvfileInsumosEstado,
                                        fieldnames=fieldNamesInsumosEstados,
                                        delimiter=';',
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for estado in insumosPorEstado:
                    writer.writerow(insumosPorEstado[estado])

    # except Exception as exc:
    #     print("[ERROR]{0}".format(exc))

    finally:
        print("[LOG]Encerrando script.")
        driver.quit()
        print("[LOG]Script encerrado.")
        print("Todos os dados foram extraídos de: " + url + ".")


if __name__ == '__main__':
    main()
