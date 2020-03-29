import re
import csv
import shutil
import datetime

import requests
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


def main():
    url = "https://covid.saude.gov.br/"
    profile = webdriver.FirefoxProfile()
    profile.update_preferences()
    firefox_options = Options()
    firefox_options.headless = True
    driver = webdriver.Firefox(firefox_profile=profile, firefox_options=firefox_options)
    driverversion = driver.capabilities['moz:geckodriverVersion']
    browserversion = driver.capabilities['browserVersion']
    print("geckodriverVersion: " + driverversion, "browserVersion: " + browserversion)
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
        casos["Óbitos"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[2]/div[2]/div/div[1]').text
        casos["Letalidade(%)"] = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[2]/div[3]/div/div[1]').text[:-1]

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
        print("Dados atualizados " + date.strftime("%d/%m/%y %H:%M") + ". Fonte: " + url)

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
            dado['Porcentagem'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[3]/div[2]/div[' + str(
                    i) + ']/div[2]/div[2]').text[:-1]
            regioes.append(dado)
        print("[LOG]Dados das regiões extraídos.")

        estados = []
        # Captura dados dos estados da página
        print("[LOG]Dados dos estados sendo extraídos.")
        scrollEstados = driver.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]')
        driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
        for i in range(1, 28):
            scrollEstados = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(
                    i) + ']')
            driver.execute_script("arguments[0].scrollIntoView()", scrollEstados)
            dado = dict()
            dado['Nome'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(
                    i) + ']/div[1]').text
            dado['Casos'] = driver.find_element_by_xpath(
                '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[4]/div[2]/div/div[' + str(
                    i) + ']/div[2]/b').text
            dado['Porcentagem'] = float((int(dado['Casos']) / int(casos["Confirmados"].replace(".", ""))) * 100.0)
            estados.append(dado)
        print("[LOG]Dados dos estados extraídos.")

        with open("./dados/" + date.strftime("%d-%m-%y--%H-%M") + ".csv", "w", newline="",
                  encoding="utf-8") as file:
            fieldNames = ["Nome", "Casos", "Casos", "Porcentagem"]
            writer = csv.DictWriter(file,
                                    fieldnames=fieldNames,
                                    delimiter=";",
                                    quotechar='"',
                                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(regioes)
            for estado in estados:
                nome = estado["Nome"] + "(" + obterUFEstadoPorNome(estado["Nome"]) + ")"
                writer.writerow({"Nome": nome,
                                 "Casos": estado["Casos"],
                                 "Porcentagem": "{:.5f}".format(estado["Porcentagem"])})
            # writer.writerows(estados)
            writer.writerow({"Nome": "Total",
                             "Casos": str(casos["Confirmados"]).replace(".", ""),
                             "Porcentagem": "100"})

        shutil.copyfile("./dados/" + date.strftime("%d-%m-%y--%H-%M") + ".csv", "dados/maisRecente.csv")

        print(
            date.strftime("%d-%m-%y--%H-%M") + ".csv criado na pasta dados, que se encontra na pasta desse script.")
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

    finally:
        print("[LOG]Encerrando script.")
        driver.quit()
        print("[LOG]Script encerrado.")
        print("Todos os dados foram extraídos de: " + url + ".")


if __name__ == '__main__':
    main()
