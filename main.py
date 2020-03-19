import os
import csv
import time
import json
import datetime
import requests
import plotly.graph_objects as go

from lxml import html
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def obterNomeEstadoPorUF(uf):
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if state["UF"].lower() == uf.lower():
                return state["Codigo"]


def obterNomeEstadoPorCodigo(codigo):
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if state["Codigo"].lower() == str(codigo).lower():
                return state["Unidade_Federativa"]


def obterCodigoEstadoPorNome(estado):
    with open("./recursos/estados.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for state in reader:
            if state["Unidade_Federativa"].lower() == estado.strip().lower():
                return state["Codigo"]


def abrirGraficoDoPaisPorNome(nomeDoPais, stats):
    re = requests.get("https://restcountries.eu/rest/v2/name/" + nomeDoPais)
    if "status" in re.text:
        return
    codigoDoPais = re.json()[0]["alpha2Code"]
    i = 0
    for key in stats:
        if str(codigoDoPais).lower() in str(key).lower():
            # https://restcountries.eu/
            req = requests.get("https://restcountries.eu/rest/v2/alpha?codes=" + key)
            # print(req.json())
            countryName = req.json()[0]["translations"]["br"]
            # print(key, stats[key])
            i += 1
            fig = go.Figure()
            fig.add_trace(go.Bar(y=stats[key][1], x=stats[key][0], name="Casos Confirmados", text=stats[key][5]))
            fig.add_trace(go.Bar(y=stats[key][2], x=stats[key][0], name="Novos Casos Confirmados"))
            fig.add_trace(go.Bar(y=stats[key][3], x=stats[key][0], name="Mortes"))
            fig.add_trace(go.Bar(y=stats[key][4], x=stats[key][0], name="Novas Mortes"))
            fig.update_layout(title='Estatística de casos do COVID-19 em ' + countryName,
                              xaxis_title='Data',
                              yaxis_title='Casos',
                              template="plotly")
            fig.show()


def abrirGraficoDoEstadoPorNome(nomeDoEstado, stats):
    codigoEstado = obterCodigoEstadoPorNome(nomeDoEstado)
    for key in stats:
        if codigoEstado.lower() == str(key).lower():
            fig = go.Figure()
            fig.add_trace(go.Bar(y=stats[key][1], x=stats[key][0], name="Casos Suspeitos", text=stats[key][5]))
            fig.add_trace(go.Bar(y=stats[key][3], x=stats[key][0], name="Casos Confirmados"))
            fig.add_trace(go.Bar(y=stats[key][4], x=stats[key][0], name="Mortes"))
            fig.add_trace(go.Bar(y=stats[key][2], x=stats[key][0], name="Casos Descartados"))
            fig.update_layout(title='Estatística de casos do COVID-19 em ' + nomeDoEstado,
                              xaxis_title='Data',
                              yaxis_title='Casos',
                              template="plotly")
            fig.show()


def compararCasosSuspeitos(nomeDoEstado1, nomeDoEstado2, stats):
    codigoEstado1 = obterCodigoEstadoPorNome(nomeDoEstado1)
    codigoEstado2 = obterCodigoEstadoPorNome(nomeDoEstado2)
    fig = go.Figure()
    for key in stats:
        if codigoEstado1.lower() == str(key).lower():
            fig.add_trace(go.Bar(y=stats[key][1], x=stats[key][0], name="Casos Suspeitos(" + nomeDoEstado1 + ")"))
            fig.add_trace(go.Bar(y=stats[key][3], x=stats[key][0], name="Casos Confirmados(" + nomeDoEstado1 + ")"))
        elif codigoEstado2.lower() == str(key).lower():
            fig.add_trace(go.Bar(y=stats[key][1], x=stats[key][0], name="Casos Suspeitos(" + nomeDoEstado2 + ")"))
            fig.add_trace(go.Bar(y=stats[key][3], x=stats[key][0], name="Casos Confirmados(" + nomeDoEstado2 + ")"))

    fig.update_layout(
        title='Estatística de casos do COVID-19 entre os estados do 🇧🇷🇧🇷🇧🇷Brasil: ' + nomeDoEstado1 + " e " + nomeDoEstado2,
        xaxis_title='Data',
        yaxis_title='Casos',
        template="plotly")
    fig.show()


def main():
    url = "http://plataforma.saude.gov.br/novocoronavirus/"
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', str(os.path.join(Path.home(), "Downloads")))
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    firefox_options = Options()
    profile.update_preferences()
    firefox_options.headless = True
    driver = webdriver.Firefox(firefox_profile=profile, firefox_options=firefox_options)
    # driver.minimize_window()
    print("[LOG]Carregando página...")
    driver.get(url=url)
    brasilcsv = str(os.path.join(Path.home(), "Downloads/brasil.csv"))
    worldcsv = str(os.path.join(Path.home(), "Downloads/mundo.csv"))
    print("[LOG]Página carregada.")
    try:
        print("[LOG]Aguardando elementos da página serem carregados...")
        WebDriverWait(driver, 120).until(
            EC.text_to_be_present_in_element((By.XPATH, '//*[@id="BRCardSuspects"]'), "%")
        )
        WebDriverWait(driver, 120).until(
            EC.text_to_be_present_in_element((By.XPATH, '/html/body/div[2]/div[3]/h4/small'), "atualizados")
        )
        print("[LOG]Elementos carregados.")
        casos = dict()
        casos["Suspeitos"] = driver.find_element_by_xpath('//*[@id="BRCardSuspects"]').text
        casos["Confirmados"] = driver.find_element_by_xpath('//*[@id="BRCardCases"]').text
        casos["Descartados"] = driver.find_element_by_xpath('//*[@id="BRCardRefuses"]').text
        casos["Óbitos"] = driver.find_element_by_xpath('//*[@id="BRCardDeaths"]').text

        dateStr = driver.find_element_by_xpath('/html/body/div[2]/div[2]/h4/small').text
        dateStr = dateStr.split(" ")
        # Houve um erro de formatação na página que motivou essa correção "desnecessária".
        # Estava "Dados atualizados em 17/03/2020 às 22:250" e consequentemente recebia o erro : "ValueError: minute must be in 0..59"
        dia = int(dateStr[3].split("/")[0])
        mes = int(dateStr[3].split("/")[1])
        ano = int(dateStr[3].split("/")[2])
        hora = int(dateStr[5].split(":")[0])
        minuto = int((dateStr[5].split(":")[1])[0:1])
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("Dados das Unidades da Federação atualizados em " + date.strftime(
            "%d/%m/%y, %H:%M") + ". Fonte: http://plataforma.saude.gov.br/novocoronavirus/")
        if input("Deseja ver as estatísticas gerais do Brasil?(sim/nao) ") != "nao":
            for key in casos.keys():
                print(key + ": " + casos[key])
            # print(cases)
        print("[LOG]Baixando arquivo de estatística do Brasil...")
        driver.find_element_by_xpath('//*[@id="BRcsvByData"]').click()
        print("[LOG]Arquivo baixado.")
        regioes = []
        estados = []

        while not os.path.exists(brasilcsv):
            time.sleep(1)

        with open(brasilcsv, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if "Região" in ''.join(row["Abrangência"]):
                    regiao = dict()
                    for key in row.keys():
                        # print region stats
                        # print(key + ": " + row[key])
                        regiao[key] = row[key]
                    regioes.append(regiao)
                else:
                    estado = dict()
                    for key in row.keys():
                        # print states stats
                        # print(key + ": " + row[key])
                        estado[key] = row[key]
                    estados.append(estado)

        template = "Nome: {}, Casos suspeitos: {}({}%), Casos confirmados: {}({}%), Casos descartados: {}({}%), Óbitos: {}({}%)"
        templateCountry = "Nome: {}, Casos confirmados: {}({}%), Taxa de letalidade {}%, Óbitos: {})"
        if input("Deseja ver as estatísticas por região?(sim/nao) ") != "nao":
            for regiao in regioes:
                print(template.format(regiao["Nome"],
                                      regiao["Casos suspeitos"], regiao["% Casos suspeitos"],
                                      regiao["Casos confirmados"], regiao["% Casos confirmados"],
                                      regiao["Casos descartados"], regiao["% Casos descartados"],
                                      regiao["Óbitos"], regiao["% Óbitos"]))

        print("[LOG]Carregando estatísticas gerais")
        r = requests.get("http://plataforma.saude.gov.br/novocoronavirus/resources/scripts/database.js")
        print("[LOG]Estatísticas carregadas")
        body = html.fromstring(r.content).text_content()

        jsonBody = json.loads(body[13:])

        stats = dict()
        brazilStats = dict()

        for key in jsonBody:
            if key == "world":
                for value in jsonBody[key]:
                    for country in value['values']:

                        if stats.get(country["uid"]):

                            stats[country["uid"]][0].append(value["date"] + " , " + value["time"])

                            if country.get("cases"):
                                stats[country["uid"]][1].append(country["cases"])

                            if country.get("casesNew"):
                                stats[country["uid"]][2].append(country['casesNew'])
                            else:
                                stats[country["uid"]][2].append(0)

                            if country.get('deaths'):
                                stats[country["uid"]][3].append(country['deaths'])
                            else:
                                stats[country["uid"]][3].append(0)

                            if country.get('deathsNew'):
                                stats[country["uid"]][4].append(country['deathsNew'])
                            else:
                                stats[country["uid"]][4].append(0)

                            if country.get('comments'):
                                if len(stats[country["uid"]]) == 5:
                                    stats[country["uid"]].append([country['comments']])
                                else:
                                    # ver se está certo
                                    stats[country["uid"]][5].append([country['comments']])
                            else:
                                if len(stats[country["uid"]]) == 5:
                                    stats[country["uid"]].append([""])
                                else:
                                    stats[country["uid"]][5].append("")

                        else:
                            stats[country["uid"]] = []

                            stats[country["uid"]].append([value["date"] + " , " + value["time"]])

                            if country.get("cases"):
                                stats[country["uid"]].append([country.get("cases")])

                            if country.get("casesNew"):
                                stats[country["uid"]].append([country['casesNew']])
                            else:
                                stats[country["uid"]].append(["0"])

                            if country.get('deaths'):
                                stats[country["uid"]].append([country['deaths']])
                            else:
                                stats[country["uid"]].append([0])

                            if country.get('deathsNew'):
                                stats[country["uid"]].append([country['deathsNew']])
                            else:
                                stats[country["uid"]].append([0])

                            if country.get('comments'):
                                stats[country["uid"]].append([country['comments']])
                            else:
                                stats[country["uid"]].append([""])
            else:
                for value in jsonBody[key]:
                    for state in value["values"]:
                        if brazilStats.get(state["uid"]):
                            brazilStats[state["uid"]][0].append(value["date"] + " , " + value["time"])
                            # if value["date"] == "17/03/2020" or value["date"] == "18/03/2020":
                            #     print("state", state)
                            #     print("value", value)
                            if state.get("suspects"):
                                brazilStats[state["uid"]][1].append(state['suspects'])
                            else:
                                brazilStats[state["uid"]][1].append(0)

                            if state.get("refuses"):
                                brazilStats[state["uid"]][2].append(state['refuses'])
                            else:
                                brazilStats[state["uid"]][2].append(0)

                            if state.get('confirmado'):
                                brazilStats[state["uid"]][3].append(state['confirmado'])
                            else:
                                brazilStats[state["uid"]][3].append(0)

                            if state.get('deads'):
                                brazilStats[state["uid"]][4].append(state['deads'])
                            else:
                                brazilStats[state["uid"]][4].append(0)

                            if state.get('comments'):
                                if len(brazilStats[state["uid"]]) == 5:
                                    brazilStats[state["uid"]].append([state['comments']])
                                else:
                                    brazilStats[state["uid"]][5].append(state['comments'])
                            else:
                                if len(brazilStats[state["uid"]]) == 5:
                                    brazilStats[state["uid"]].append([""])
                                else:
                                    brazilStats[state["uid"]][5].append("")

                        else:
                            brazilStats[state["uid"]] = []

                            brazilStats[state["uid"]].append([value["date"] + " , " + value["time"]])

                            if state.get("suspects"):
                                brazilStats[state["uid"]].append([state.get("suspects")])
                            else:
                                brazilStats[state["uid"]].append([0])

                            if state.get("refuses"):
                                brazilStats[state["uid"]].append([state['refuses']])
                            else:
                                brazilStats[state["uid"]].append([0])

                            if state.get('confirmado'):
                                brazilStats[state["uid"]].append([state['confirmado']])
                            else:
                                brazilStats[state["uid"]].append([0])

                            if state.get('deads'):
                                brazilStats[state["uid"]].append([state['deads']])
                            else:
                                brazilStats[state["uid"]].append([0])

                            if state.get('comments'):
                                brazilStats[state["uid"]].append([state['comments']])
                            else:
                                brazilStats[state["uid"]].append([""])

        option = input("Você deseja verificar as estatísticas de estados?(sim/nao/todos) ")
        while True:
            if option.lower() == "nao":
                break

            elif option.lower() == "todos":
                for estado in estados:
                    if estado["Nome"] is not None and estado["Óbitos"] is not None:
                        print(template.format(estado["Nome"].replace("*", ""),
                                              estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                              estado["Casos confirmados"], estado["% Casos confirmados"],
                                              estado["Casos descartados"], estado["% Casos descartados"],
                                              estado["Óbitos"], estado["% Óbitos"]))
                break

            else:
                name = input("Digite a sigla do estado ou o nome: ")
                try:
                    for estado in estados:
                        if len(name) <= 2:
                            if estado["Nome"] is not None and "(" + name.lower() + ")" in estado["Nome"].lower() and \
                                    estado["Óbitos"] is not None:
                                print(template.format(estado["Nome"].replace("*", ""),
                                                      estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                                      estado["Casos confirmados"], estado["% Casos confirmados"],
                                                      estado["Casos descartados"], estado["% Casos descartados"],
                                                      estado["Óbitos"], estado["% Óbitos"]))
                                if "*" in estado["Nome"]:
                                    abrirGraficoDoEstadoPorNome(estado["Nome"].replace("*", "")[:-4], brazilStats)
                                else:
                                    abrirGraficoDoEstadoPorNome(estado["Nome"][:-4], brazilStats)
                                break

                        else:
                            if estado["Nome"] is not None and name.lower() in estado["Nome"].lower() and estado[
                                "Óbitos"] is not None:
                                print(template.format(estado["Nome"].replace("*", ""),
                                                      estado["Casos suspeitos"], estado["% Casos suspeitos"],
                                                      estado["Casos confirmados"], estado["% Casos confirmados"],
                                                      estado["Casos descartados"], estado["% Casos descartados"],
                                                      estado["Óbitos"], estado["% Óbitos"]))
                                if "*" in estado["Nome"]:
                                    abrirGraficoDoEstadoPorNome(estado["Nome"].replace("*", "")[:-4], brazilStats)
                                else:
                                    abrirGraficoDoEstadoPorNome(estado["Nome"][:-4], brazilStats)
                finally:
                    option = input("Deseja continuar(sim/nao)? ")

        print("[LOG]Baixando arquivo de estatística do mundo...")
        driver.find_element_by_xpath('//*[@id="WRcsvByMap"]').click()
        print("[LOG]Arquivo baixado.")
        paises = []

        while not os.path.exists(worldcsv):
            time.sleep(1)

        with open(worldcsv, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                # print(row)
                pais = dict()
                for key in row.keys():
                    pais[key] = row[key]
                paises.append(pais)

        # print(countries)
        option = input("Deseja verificar estatística de algum país?(sim/nao/todos) ")
        dateStr = driver.find_element_by_xpath('/html/body/div[2]/div[3]/h4/small').text
        dateStr = dateStr.split(" ")
        # Houve um erro de formatação na página que motivou essa correção "desnecessária".
        # Estava "Dados atualizados em 17/03/2020 às 22:250" e consequentemente recebia o erro : "ValueError: minute must be in 0..59"
        dia = int(dateStr[3].split("/")[0])
        mes = int(dateStr[3].split("/")[1])
        ano = int(dateStr[3].split("/")[2])
        hora = int(dateStr[5].split(":")[0])
        minuto = int((dateStr[5].split(":")[1])[0:1])
        date = datetime.datetime(ano, mes, dia, hora, minuto)
        print("Países com com casos confirmados atualizados em " + date.strftime(
            "%d/%m/%y, %H:%M") + " segundo a OMS. Fonte: http://plataforma.saude.gov.br/novocoronavirus/")

        while True:
            if option.lower() == "nao":
                break

            elif option.lower() == "todos":
                # option = input("Você tem certeza que deseja abrir o gráfico de todos os países com casos do COVID-19? São, no total, " + str(len(paises)) + " (sim/nao) ")
                # if option == "sim":
                for pais in paises:
                    if pais["País"] is not None and pais["Óbitos"] is not None:
                        print(templateCountry.format(pais["País"].replace("*", ""),
                                                     pais["Casos confirmados"], pais["% Casos confirmados"],
                                                     pais["Taxa de letalidade******"], pais["Óbitos"]))
                        # abrirGraficoDoPaisPorNome(pais["País"], stats)
                # elif option == "nao":
                #     print("")

                break

            else:
                name = input("Digite o nome do país:  ")

                try:
                    for pais in paises:
                        # print(country)
                        if pais["País"] is not None and name.lower() in pais["País"].lower() and pais[
                            "Óbitos"] is not None:
                            print(templateCountry.format(pais["País"].replace("*", ""),
                                                         pais["Casos confirmados"], pais["% Casos confirmados"],
                                                         pais["Taxa de letalidade******"], pais["Óbitos"]))
                            abrirGraficoDoPaisPorNome(pais["País"].replace("*", ""), stats)

                finally:
                    option = input("Deseja continuar(sim/nao)? ")

    finally:
        driver.quit()
        try:
            os.remove(brasilcsv)
            os.remove(worldcsv)
        except Exception:
            print("error deleting files")


if __name__ == '__main__':
    main()
