import os
import re
import csv
import time
import shutil
import datetime
import requests
import plotly.graph_objects as go

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
    driver = webdriver.Firefox(firefox_profile=profile, firefox_options=firefox_options)
    driverversion = driver.capabilities['moz:geckodriverVersion']
    browserversion = driver.capabilities['browserVersion']
    print("[LOG]geckodriverVersion: " + driverversion, "\n[LOG]browserVersion: " + browserversion)
    print("[LOG]Carregando página...")
    driver.get(url=url)
    print("[LOG]Página carregada.")
    try:
        print("[LOG]Aguardando elementos da página serem carregados...")
        WebDriverWait(driver, 120).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[2]/div[2]/b'),
                "2020")
        )
        print("[LOG]Elementos carregados.")
        print("[LOG]Webdriver temporário sendo executado.")
        miningDriver = webdriver.Firefox(firefox_profile=profile, firefox_options=firefox_options)
        headerRequestID = None
        print("[LOG]Procurando header ID para GET request.")
        try:
            # A partir daqui, o algoritmo procura todas as tag <script> do html da pagina e
            # procura pela string "X-Parse-Application-Id".
            # Depois de encontrar, é utilizado REGEX para encontar alguns padrões e, a partir
            # deles, procuro pela string "X-Parse-Application-Id" e dou um parse simples.
            # Essa string que é encontrada é utilizada como request header em um GET request em uma parte do código
            header = driver.find_element_by_tag_name("head")
            scriptsFromHead = header.find_elements_by_tag_name("script")
            for script in scriptsFromHead:
                if script.get_attribute("src") and "https://covid.saude.gov.br" in script.get_attribute("src"):
                    scriptUrl = script.get_attribute("src")
                    miningDriver.get(scriptUrl)
                    if "X-Parse-Application-Id" in miningDriver.page_source:
                        html = miningDriver.page_source
                        p = re.compile('\(\"(.*?)\"\)')
                        for match in p.findall(html):
                            if "X-Parse-Application-Id" in match:
                                headerRequestID = str(match.split('","')[1]).strip()
                                # print(headerRequestID)
                                print("[LOG]Header ID para GET request encontrado.")
                                break
                        break

        finally:
            miningDriver.close()
            print("[LOG]Webdriver temporário encerrado.")

        # Captura dados gerais da página
        print("[LOG]Capturando dados gerais.")
        casos = dict()
        casos["Confirmados"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[2]/div[1]/div/div[1]').text
        casos["Obitos"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[2]/div[2]/div/div[1]').text
        casos["Letalidade(%)"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[2]/div[3]/div/div[1]').text[:-1].replace(",", ".")

        dateStr = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[2]/div[2]/b').text
        dateStr = dateStr.split(" ")
        hora = int(dateStr[0].split(":")[0])
        minuto = int((dateStr[0].split(":")[1])[0:1])
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
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[1]')
        driver.execute_script("arguments[0].scrollIntoView()", scrollRegioes)
        WebDriverWait(driver, 120).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[5]'),
                "Sul")
        )
        modeloRegiao = "Nome: {}, Casos confirmados: {}({}%)"
        for i in range(1, 6):
            scrollRegioes = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[' + str(i) + ']')
            driver.execute_script("arguments[0].scrollIntoView()", scrollRegioes)
            dado = dict()
            dado['Nome'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[' + str(
                    i) + ']/div[1]/div[2]').text
            dado['Casos'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[' + str(
                    i) + ']/div[2]/div[1]').text
            dado['PorcentagemDeCasosRelacional'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[' + str(
                    i) + ']/div[2]/div[2]').text[:-1]
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
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]')
        driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
        for i in range(2, 29):
            scrollEstados = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(i) + ']')
            driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
            dado = dict()
            dado['Nome'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(i) + ']/div[1]').text
            dado['Casos'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(i) + ']/div[2]/div[1]/b').text
            dado['PorcentagemDeCasosRelacional'] = float((int(dado['Casos']) / int(casos["Confirmados"].replace(".", ""))) * 100.0)
            dado['Obitos'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div['+str(i)+']/div[2]/div[2]/b').text
            dado['Letalidade'] = driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div['+str(i)+']/div[2]/div[3]/b').text
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
            with open("./dados/" + date.strftime("%d-%m-%Y--%H-%M") + ".csv", "w", newline="",
                      encoding="utf-8") as file:
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
                           headers={"X-Parse-Application-Id": headerRequestID})
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

        brasilcsv = str(os.path.join(pastaAtual, "dados/COVID19_"+date.strftime("%Y%m%d")+".csv"))
        entrada = input("Deseja ver as estatísticas de casos por estado?(sim/nao) ")
        casosEstaduais = dict()
        if entrada != "nao":
            print("[LOG]Baixando arquivo dos casos detalhados dos estados")
            #arquivo nao existe e baixa o mesmo
            if not os.path.exists(brasilcsv):
                driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[6]/div[1]').click()
                while not os.path.exists(brasilcsv):
                    time.sleep(1)
            #arquivo ja existe, apaga e cria outro
            else:
                os.remove(brasilcsv)
                driver.find_element_by_xpath('/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[6]/div[1]').click()
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

            with open(brasilcsv, newline='') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    if row['estado'] not in casosEstaduais:
                        casosEstaduais[row['estado']] = []
                        casosEstaduais[row['estado']].append([row['data']])
                        casosEstaduais[row['estado']].append([row['casosNovos']])
                        casosEstaduais[row['estado']].append([row['casosAcumulados']])
                        casosEstaduais[row['estado']].append([row['obitosNovos']])
                        casosEstaduais[row['estado']].append([row['obitosAcumulados']])
                        casosEstaduais[row['estado']].append(row['regiao'])

                    else:
                        casosEstaduais[row['estado']][0].append(row['data'])
                        casosEstaduais[row['estado']][1].append(row['casosNovos'])
                        casosEstaduais[row['estado']][2].append(row['casosAcumulados'])
                        casosEstaduais[row['estado']][3].append(row['obitosNovos'])
                        casosEstaduais[row['estado']][4].append(row['obitosAcumulados'])

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

    # except Exception as exc:
    #     print("[ERROR]{0}".format(exc))

    finally:
        print("[LOG]Encerrando script.")
        driver.quit()
        print("[LOG]Script encerrado.")
        print("Todos os dados foram extraídos de: " + url + ".")


if __name__ == '__main__':
    main()
